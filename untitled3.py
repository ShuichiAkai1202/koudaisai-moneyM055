import streamlit as st
import pandas as pd

# --- 設定：単価 (ファイル内の表に基づく) ---
RATES = {
    'BASE': 300,          # 基本給
    'SHIFT': 400,         # シフト手当 (時給)
    'SHOPPING': 600,      # 買い出し手当 (回)
    'PREP': 400,          # 準備・片付け手当 (回)
    'DEBT': 4500,         # 借りたお金 (立替金など)
    'LEADER': 5000,       # 責任者手当
    'INSTA': 1000,        # インスタ手当
    'CHIEF': 2000,        # 係長手当
    'ACCOUNTANT': 2000    # 会計手当
}

# 管理用パスワード（適宜変更してほしい）
ADMIN_PASSWORD = "Chijimi"

# ----------------------------------------

st.set_page_config(page_title="文化祭配当金確認システム", layout="centered")

# サイドバーで簡易ログイン
st.sidebar.title("認証")
auth_pass = st.sidebar.text_input("パスワードを入力", type="password")

if auth_pass != ADMIN_PASSWORD:
    if auth_pass:
        st.sidebar.error("パスワードが違う")
    st.title("文化祭配当金 確認システム")
    st.warning("閲覧するには正しいパスワードを左のメニューに入力してください")
    st.stop()

st.title('文化祭配当金 確認システム')

@st.cache_data
def load_data():
    file_name = '工大祭分配金.xlsx'
    try:
        # 2行目をヘッダーとして読み込む
        df = pd.read_excel(file_name, header=1)

        # 必要な列をインデックスで抽出
        df = df.iloc[:, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
        df.columns = [
            'student_id', 'name', 'base','debt', 'shift', 'shopping', 'prep',
            'leader', 'insta', 'chief', 'accountant'
        ]

        # 学籍番号のクリーニング：数値として読み込まれた際の ".0" を削除
        df['student_id'] = df['student_id'].astype(str).str.split('.').str[0].str.strip()
        
        # 数値項目の空欄を0で埋める
        num_cols = ['base','debt', 'shift', 'shopping', 'prep', 'leader', 'insta', 'chief', 'accountant']
        df[num_cols] = df[num_cols].fillna(0)
        
        return df

    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"エラーが発生した: {e}")
        return None

df = load_data()

if df is None:
    st.error('Excelファイル (工大祭分配金.xlsx) が見つからない、または読み込めない。')
    st.stop()

# 検索フォーム
st.write('学籍番号を入力して「確認する」を押してください')
input_id = st.text_input('学籍番号', placeholder='例: 25B12345').strip()

if st.button('確認する'):
    if not input_id:
        st.warning("学籍番号を入力してください")
    else:
        # 学籍番号で検索
        user_data = df[df['student_id'] == input_id]

        if not user_data.empty:
            row = user_data.iloc[0]
            name = row['name']

            # --- 計算ロジック ---
            base_pay = row['base']*RATES['BASE']
            shift_pay = row['shift'] * RATES['SHIFT']
            shop_pay = row['shopping'] * RATES['SHOPPING']
            prep_pay = row['prep'] * RATES['PREP']
            debt_pay = row['debt'] * RATES['DEBT'] 

            # 役職手当
            role_pay = 0
            role_details = []
            roles = [
                ('base','BASE',"基本給"),
                ('leader', 'LEADER', "責任者"),
                ('insta', 'INSTA', "インスタ"),
                ('chief', 'CHIEF', "係長"),
                ('accountant', 'ACCOUNTANT', "会計")
            ]

            for col, rate_key, label in roles:
                if row[col] == 1:
                    role_pay += RATES[rate_key]
                    role_details.append(f"{label} (+¥{RATES[rate_key]:,})")

            # 総額
            total = base_pay + shift_pay + shop_pay + prep_pay + debt_pay + role_pay

            # --- 結果表示 ---
            st.subheader(f'{name} さんの配当金')
            st.metric(label="支給総額", value=f"¥{int(total):,}")

            with st.expander("内訳を確認する", expanded=True):
                st.markdown(f"**基本給:** ¥{RATES['BASE']:,}")

                if shift_pay > 0:
                    st.markdown(f"**シフト:** {row['shift']}h × @{RATES['SHIFT']} = ¥{int(shift_pay):,}")

                if prep_pay > 0:
                    st.markdown(f"**準備・片付:** {int(row['prep'])}回 × @{RATES['PREP']} = ¥{int(prep_pay):,}")

                if shop_pay > 0:
                    st.markdown(f"**買い出し:** {int(row['shopping'])}回 × @{RATES['SHOPPING']} = ¥{int(shop_pay):,}")

                if debt_pay > 0:
                    st.markdown(f"**立替金返済など:** ¥{int(debt_pay):,}")

                if role_details:
                    st.markdown("**役職手当:**")
                    for d in role_details:
                        st.markdown(f"- {d}")
        else:
            st.error('その番号は見つからない。入力ミスか、リストに載っていない可能性がある。')
