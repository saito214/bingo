
import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("📊 ビンゴ大会リアルタイム表示")

# 入力状態保持
if "called" not in st.session_state:
    st.session_state.called = set()

# 入力欄
with st.form("number_form"):
    num = st.text_input("数字を入力（1つずつ）", "")
    submitted = st.form_submit_button("追加 / 取消")

if submitted and num.isdigit():
    if num in st.session_state.called:
        st.session_state.called.remove(num)
    else:
        st.session_state.called.add(num)

# ビンゴ判定ロジック
def check_status(df, called):
    def line_status(cells):
        marked = [(c in called or c == "FREE") for c in cells]
        if sum(marked) == 5:
            return "BINGO"
        elif sum(marked) == 4:
            return "REACH"
        else:
            return None

    states = []

    for i in range(5):
        row = df.iloc[i, :]
        col = df.iloc[:, i]
        for line in [row, col]:
            s = line_status(line)
            if s: states.append(s)

    # 斜め
    diag1 = [df.iloc[i, i] for i in range(5)]
    diag2 = [df.iloc[i, 4-i] for i in range(5)]
    for d in [diag1, diag2]:
        s = line_status(d)
        if s: states.append(s)

    return "BINGO!" if "BINGO" in states else ("REACH!" if "REACH" in states else None)

# 表示
st.write("### 現在の数字:", ", ".join(sorted(st.session_state.called)))

cols = st.columns(4)
for idx in range(1, 21):
    path = f"./csv/{idx}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path, header=None).fillna("FREE").astype(str)
        status = check_status(df, st.session_state.called)
        title = f"Card {idx:02}"
        if status == "BINGO!":
            title += " 🎉 BINGO!"
        elif status == "REACH!":
            title += " ⚠️ REACH!"
        with cols[(idx - 1) % 4]:
            st.markdown(f"#### {title}")
            st.dataframe(df.style.applymap(lambda v: 'background-color: yellow' if v in st.session_state.called else None))
