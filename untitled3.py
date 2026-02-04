import streamlit as st
import pandas as pd

# --- 設定：単価 ---
RATES = {
    'BASE': 300,
    'SHIFT': 400,
    'SHOPPING': 500,
    'PREP': 400,
    'DEBT': 4500,
    'LEADER': 5000,
    'INSTA': 1000,
    'CHIEF': 1500,
    'ACCOUNTANT': 1500
}

ADMIN_PASSWORD = "Chijimi"

# 画面設定：スマホで見やすいようワイドモードをオフにし、タイトルを短く
st.set_page_config(page_title="配当金確認", layout="centered")

# カスタムCSS：スマホでの視認性向上（フォントサイズ調整など）
st.markdown("""
    <style>
    .main {
        padding-top: 10px;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# サイドバー認証
st.sidebar.title("認証")
auth_pass = st.sidebar.text_input("パスワード", type="password", placeholder="合言葉を入力")

if auth_pass != ADMIN_PASSWORD:
    if auth_pass:
        st.sidebar.error("パスワードが違います")
    st.title("工大祭 配当金確認")
    st.info("サイドバーにパスワードを入力して開始してください")
    st.stop()

# メインコンテンツ
st.title('💰 配当金確認')

@st.cache_data
def load_data():
    file_name = '工大祭分配金.xlsx'
    try:
        df = pd.read_excel(file_name, header=1)
        df = df.iloc[:, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
        df.columns = [
            'student_id', 'name', 'base','debt', 'shift', 'shopping', 'prep',
            'leader', 'insta', 'chief', 'accountant'
        ]
        df['student_id'] = df['student_id'].astype(str).str.split('.').str[0].str.strip()
        num_cols = ['base','debt', 'shift', 'shopping', 'prep', 'leader', 'insta', 'chief', 'accountant']
        df[num_cols] = df[num_cols].fillna(0)
        return df
    except Exception as e:
        st.error(f"ファイル読み込みエラー: {e}")
        return None

df = load_data()

if df is not None:
    # スマホで打ちやすいよう、大文字に自動変換する案内
    st.write('学籍番号を入力（例: 25B12345）')
    input_id = st.text_input('学籍番号', placeholder='ここをタップして入力').strip().upper()

    # 「確認」ボタンを大きく表示
    if st.button('配当金を計算する', use_container_width=True, type="primary"):
        if not input_id:
            st.warning("学籍番号を入れてください")
        else:
            user_data = df[df['student_id'] == input_id]

            if not user_data.empty:
                row = user_data.iloc[0]
                
                # 計算
                base_pay = row['base'] * RATES['BASE']
                shift_pay = row['shift'] * RATES['SHIFT']
                shop_pay = row['shopping'] * RATES['SHOPPING']
                prep_pay = row['prep'] * RATES['PREP']
                debt_pay = row['debt'] * RATES['DEBT']

                role_pay = 0
                role_details = []
                # 基本給は個別に表示するためrolesからは除外
                roles = [
                    ('leader', 'LEADER', "責任者"),
                    ('insta', 'INSTA', "インスタ"),
                    ('chief', 'CHIEF', "係長"),
                    ('accountant', 'ACCOUNTANT', "会計")
                ]

                for col, rate_key, label in roles:
                    if row[col] == 1:
                        role_pay += RATES[rate_key]
                        role_details.append(f"{label} (+¥{RATES[rate_key]:,})")

                total = base_pay + shift_pay + shop_pay + prep_pay + debt_pay + role_pay

                # 表示
                st.subheader(f'👤 {row["name"]} さん')
                st.metric(label="合計支給額", value=f"¥{int(total):,}")

                with st.expander("💸 明細を確認する", expanded=True):
                    if base_pay > 0:
                        st.write(f"**基本給:** ¥{int(base_pay):,}")
                    if shift_pay > 0:
                        st.write(f"**シフト:** {row['shift']}h → ¥{int(shift_pay):,}")
                    if prep_pay > 0:
                        st.write(f"**準備・片付:** {int(row['prep'])}回 → ¥{int(prep_pay):,}")
                    if shop_pay > 0:
                        st.write(f"**買い出し:** {int(row['shopping'])}回 → ¥{int(shop_pay):,}")
                    if debt_pay > 0:
                        st.write(f"**立替金返済:** ¥{int(debt_pay):,}")
                    
                    if role_details:
                        st.divider()
                        st.write("**役職手当:**")
                        for d in role_details:
                            st.write(f"✅ {d}")
            else:
                st.error('番号が見つからない...大文字・小文字を確認してね。')

    # フッター：スマホでスクロールした際に見やすく
    st.markdown("---")
    st.caption("© 寺田響希 分配金管理システム")
