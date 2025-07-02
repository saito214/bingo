import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("📊 ビンゴ大会リアルタイム表示")

# セッション状態の初期化
if "called" not in st.session_state:
    st.session_state.called = set()

# 🎯 入力フォーム
with st.form("number_form"):
    num = st.text_input("数字を入力（Enterで追加または取消）", "")
    submitted = st.form_submit_button("送信")

# 🎯 数字の追加 or 取消処理
if submitted and num.isdigit():
    if num in st.session_state.called:
        st.session_state.called.remove(num)
    else:
        st.session_state.called.add(num)

# 🎯 ビンゴ判定関数
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
        row = df.iloc[i, :]
        col = df.iloc[:, i]
        for line in [row, col]:
            s = line_status(line)
            if s:
                states.append(s)

    diag1 = [df.iloc[i, i] for i in range(5)]
    diag2 = [df.iloc[i, 4 - i] for i in range(5)]
    for d in [diag1, diag2]:
        s = line_status(d)
        if s:
            states.append(s)

    if "BINGO" in states:
        return "BINGO"
    elif "REACH" in states:
        return "REACH"
    else:
        return None

# 🎯 カード情報読み込み＆ステータス判定（キャッシュ）
card_status = {}  # {idx: (df, status)}
for idx in range(1, 21):
    path = f"./csv/{idx}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path, header=None).fillna("FREE").astype(str)
        status = check_status(df, st.session_state.called)
        card_status[idx] = (df, status)

# 🎯 現在の数字表示
st.markdown("### 🔢 現在の入力数字")
st.write(", ".join(sorted(st.session_state.called, key=lambda x: int(x))))

# 🎯 リーチ・ビンゴ一覧表示
reach_cards = [f"{idx:02}" for idx, (_, s) in card_status.items() if s == "REACH"]
bingo_cards = [f"{idx:02}" for idx, (_, s) in card_status.items() if s == "BINGO"]

if reach_cards:
    st.markdown("### 🟡 リーチ中のカード")
    st.write("→", ", ".join(reach_cards))

if bingo_cards:
    st.markdown("### 🎉 BINGOしたカード")
    st.write("→", ", ".join(bingo_cards))

# 🎯 各カード表示（4列グリッド）
st.markdown("### 🧾 各カードの状態とビンゴ表")
cols = st.columns(4)
for idx, (df, status) in card_status.items():
    title = f"Card {idx:02}"
    if status == "BINGO":
        title += " 🎉 BINGO!"
    elif status == "REACH":
        title += " ⚠️ REACH!"
    with cols[(idx - 1) % 4]:
        st.markdown(f"#### {title}")
        st.dataframe(df.style.applymap(
            lambda v: 'background-color: yellow' if v in st.session_state.called else None
        ))
