import streamlit as st
import pandas as pd
import os
import glob

st.set_page_config(layout="wide")
st.title("📊 ビンゴ大会リアルタイム表示")

# ユーザー名の入力
username = st.text_input("🧑 あなたのユーザー名を入力してください", "")
if not username:
    st.warning("ユーザー名を入力してください")
    st.stop()

else :


    user_dir = f"./{username}"
    if not os.path.isdir(user_dir):
        st.error(f"ユーザー「{username}」のカードフォルダが存在しません。")
        st.stop()

    # セッション初期化
    if "called" not in st.session_state:
        st.session_state.called = set()

    # 数字入力フォーム
    with st.form("number_form"):
        num = st.text_input("数字を入力（Enterで追加または取消）", "")
        submitted = st.form_submit_button("送信")

    if submitted and num.isdigit():
        if num in st.session_state.called:
            st.session_state.called.remove(num)
        else:
            st.session_state.called.add(num)

    # ビンゴ/リーチ判定
    def check_status(df, called):
        def line_status(cells):
            marked = [(str(c) in called or str(c).upper() == "FREE") for c in cells]
            if sum(marked) == 5:
                return "BINGO"
            elif sum(marked) == 4:
                return "REACH"
            return None

        states = []

        for i in range(5):
            for line in [df.iloc[i, :], df.iloc[:, i]]:
                s = line_status(line)
                if s:
                    states.append(s)

        for diag in [[df.iloc[i, i] for i in range(5)], [df.iloc[i, 4 - i] for i in range(5)]]:
            s = line_status(diag)
            if s:
                states.append(s)

        return "BINGO" if "BINGO" in states else ("REACH" if "REACH" in states else None)

    # CSVファイルを自動で読み込む
    csv_files = sorted(glob.glob(os.path.join(user_dir, "*.csv")))
    card_status = {}  # {ファイル名（インデックス）: (df, status)}

    for path in csv_files:
        try:
            df = pd.read_csv(path, header=None).fillna("FREE").astype(str)
            status = check_status(df, st.session_state.called)
            filename = os.path.basename(path)
            card_id = os.path.splitext(filename)[0]
            card_status[card_id] = (df, status)
        except Exception as e:
            st.error(f"{path} の読み込みに失敗しました: {e}")

    # 現在の数字
    st.markdown("### 🔢 現在の入力数字")
    st.write(", ".join(sorted(st.session_state.called, key=lambda x: int(x))))

    # リーチ・ビンゴの簡易表示
    reach_cards = [k for k, (_, s) in card_status.items() if s == "REACH"]
    bingo_cards = [k for k, (_, s) in card_status.items() if s == "BINGO"]

    if reach_cards:
        st.markdown("### 🟡 リーチ中のカード")
        st.write("→", ", ".join(reach_cards))

    if bingo_cards:
        st.markdown("### 🎉 BINGOしたカード")
        st.write("→", ", ".join(bingo_cards))

    # 各カードの表示（4列グリッド）
    st.markdown("### 🧾 各カードの状態とビンゴ表")
    cols = st.columns(4)

    for idx, card_id in enumerate(sorted(card_status.keys(), key=lambda x: int(x)), start=1):
        df, status = card_status[card_id]
        title = f"Card {card_id}"
        if status == "BINGO":
            title += " 🎉 BINGO!"
        elif status == "REACH":
            title += " ⚠️ REACH!"
        with cols[(idx - 1) % 4]:
            st.markdown(f"#### {title}")
            st.dataframe(df.style.applymap(
                lambda v: 'background-color: yellow' if v in st.session_state.called else None
            ))

