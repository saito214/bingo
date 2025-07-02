import streamlit as st
import pandas as pd
import os

# 初期化
if 'called' not in st.session_state:
    st.session_state.called = set()

# 数字入力欄
st.title("🎯 ビンゴ番号入力")
number = st.text_input("番号を入力（Enterで追加・削除）", key="number_input")

if number:
    try:
        n = int(number)
        if n in st.session_state.called:
            st.session_state.called.remove(n)
        else:
            st.session_state.called.add(n)
        # 入力欄を空にする
        st.session_state.number_input = ""
    except ValueError:
        st.warning("数字を入力してください")

# 現在の入力番号一覧
if st.session_state.called:
    st.markdown("### 📋 現在の数字")
    st.write(sorted(st.session_state.called))

# カードの読み込み
folder = "./csv"
cards = {}
for file in sorted(os.listdir(folder)):
    if file.endswith(".csv"):
        card_id = int(file.replace(".csv", ""))
        cards[card_id] = pd.read_csv(os.path.join(folder, file), header=None)

# 判定関数
def is_bingo(card, called):
    for i in range(5):
        if all(card.iloc[i, j] in called or card.iloc[i, j] == "FREE" for j in range(5)):
            return True
        if all(card.iloc[j, i] in called or card.iloc[j, i] == "FREE" for j in range(5)):
            return True
    if all(card.iloc[i, i] in called or card.iloc[i, i] == "FREE" for i in range(5)):
        return True
    if all(card.iloc[i, 4-i] in called or card.iloc[i, 4-i] == "FREE" for i in range(5)):
        return True
    return False

def is_reach(card, called):
    def count_hits(line):
        return sum(1 for v in line if v in called or v == "FREE")
    for i in range(5):
        if count_hits(card.iloc[i, :]) == 4:
            return True
        if count_hits(card.iloc[:, i]) == 4:
            return True
    if count_hits([card.iloc[i, i] for i in range(5)]) == 4:
        return True
    if count_hits([card.iloc[i, 4-i] for i in range(5)]) == 4:
        return True
    return False

# カード表示
st.markdown("---")
st.header("🃏 ビンゴカードの状態")
for i in sorted(cards):
    card = cards[i].copy()
    for r in range(5):
        for c in range(5):
            val = card.iat[r, c]
            if val != "FREE":
                try:
                    card.iat[r, c] = int(val)
                except:
                    pass

    bingo = is_bingo(card, st.session_state.called)
    reach = is_reach(card, st.session_state.called)

    if bingo:
        st.subheader(f"🎉 Card {i:02}: BINGO!")
    elif reach:
        st.markdown(f"🔔 Card {i:02}: リーチ！")

    st.dataframe(card.style.applymap(lambda v: 'background-color: yellow' if v in st.session_state.called else None))
