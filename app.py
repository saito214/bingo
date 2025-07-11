import streamlit as st
import pandas as pd
import os
import glob
import shutil
st.set_page_config(layout="wide")
st.title("📊 ビンゴ大会リアルタイム表示")

# パスワードの設定（ハードコーディング）
CORRECT_PASSWORD = "Sirouta0615"


# 管理者操作が必要なユーザー名
admin_keywords = ["alluser", "del","gore"]

username = st.text_input("ユーザー名を入力してください")

# 管理者モードに入る場合はパスワードを要求
if username.strip().lower() in admin_keywords:
    password = st.text_input("🔑 管理者パスワードを入力してください", type="password")
    if password != CORRECT_PASSWORD:
        st.error("パスワードが間違っています。")
        st.stop()


# alluser モード
if username.strip().lower() == "alluser":
    user_dirs = [
        name for name in os.listdir(".")
        if os.path.isdir(name) and not name.startswith(".") and name not in ["__pycache__", "csv", "gore", ".git"]
    ]
    st.markdown("### 👥 登録済みユーザー一覧")
    if user_dirs:
        st.write(", ".join(sorted(user_dirs)))
    else:
        st.write("（ユーザーはまだ登録されていません）")
    st.stop()

# del モード
if username.strip().lower() == "del":
    st.markdown("### ⚠️ ユーザー削除モード")
    user_to_delete = st.text_input("🗑 削除したいユーザー名を入力してください", "")
    if user_to_delete:
        user_folder = os.path.join(user_to_delete)
        if os.path.exists(user_folder):
            st.warning(f"ユーザー「{user_to_delete}」のフォルダを削除してもよいですか？この操作は元に戻せません。")
            if st.button("🚨 本当に削除する"):
                shutil.rmtree(user_folder)
                st.success(f"✅ ユーザー「{user_to_delete}」のデータを削除しました。")
        else:
            st.error(f"ユーザー「{user_to_delete}」のフォルダが見つかりません。")
    st.stop()
else :
    user_dir = f"./{username}"
    # if not os.path.isdir(user_dir):
    #     st.error(f"ユーザー「{username}」のカードフォルダが存在しません。")
    #     st.stop()

    if not os.path.exists(user_dir):
        st.warning("このユーザー名のビンゴカードが存在しません。新規作成してください。")

        # 新規作成モード
        st.markdown("### 🆕 ビンゴカードを手入力で追加")
        # カード入力欄の初期化フラグ
        if "clear_rows" not in st.session_state:
            st.session_state.clear_rows = False
        if "new_cards" not in st.session_state:
            st.session_state.new_cards = []

        if st.session_state.clear_rows:
            for i in range(5):
                st.session_state[f"row_{i}"] = ""

        new_card = []

        for i in range(5):
            key = f"row_{i}"
            default_value = "" if st.session_state.clear_rows else st.session_state.get(key, "")
            row_input = st.text_input(
                f"{i+1}行目の数字（カンマ区切り）",  # ← 表示も修正
                value=default_value,
                key=key
            )

            parts = [p.strip() for p in row_input.strip().split(",") if p.strip()]  # カンマ区切りで分割＆空白除去

            if i == 2:
                if len(parts) >= 2:
                    parts.insert(2, "FREE")
                else:
                    parts = parts + ["FREE"]

            row = parts[:5] + [""] * (5 - len(parts))
            new_card.append(row)


        # ➕ カード追加ボタン処理
        if st.button("➕ カードを追加"):
            valid = True
            error_msgs = []

            for i in range(5):
                for j in range(5):
                    if i == 2 and j == 2:
                        continue  # 中央FREEマス
                    value = new_card[i][j]
                    if value == "" or value is None:
                        error_msgs.append(f"{i+1}行{j+1}列が空白です")
                        valid = False
                    else:
                        try:
                            num = int(value)
                            if not (1 <= num <= 99):
                                error_msgs.append(f"{i+1}行{j+1}列は1〜99の整数である必要があります")
                                valid = False
                        except ValueError:
                            error_msgs.append(f"{i+1}行{j+1}列に無効な値が含まれています")
                            valid = False

            if valid:
                st.session_state.new_cards.append(new_card)
                st.session_state.clear_rows = True  # ✅ 次フレームで空にする
                st.rerun()  # 🔁 強制再描画（clear_rowsが効く）
            else:
                for msg in error_msgs:
                    st.error(msg)

        # ✅ 再描画後の初期化フラグ解除
        if st.session_state.get("clear_rows", False):
            st.session_state.clear_rows = False

        # ✅ 現在のカード一覧表示
        if st.session_state.new_cards:
            st.markdown("#### 現在追加されたカード一覧")
            for idx, card in enumerate(st.session_state.new_cards, start=1):
                st.write(f"🃏 Card {idx}")
                st.table(card)

            # ✅ 保存処理
            if st.button("💾 全て保存して次へ"):
                os.makedirs(user_dir, exist_ok=True)
                for idx, card in enumerate(st.session_state.new_cards, start=1):
                    df = pd.DataFrame(card)
                    df.iloc[2, 2] = "FREE"  # 念のためFREE再確認
                    df.to_csv(f"{user_dir}/{idx}.csv", index=False, header=False)
                st.success("✅ 全カードを保存しました。ページを再読み込みしてください。")
                st.stop()

    #既存ユーザーも追加できるように
    else:
        st.success(f"✅ ユーザー「{username}」が見つかりました。")
        choice = st.radio("次の操作を選んでください", ["🎴 ビンゴカードを追加(必ず再読み込みしてください)", "🎯 ビンゴ判定に進む", "✏️ ビンゴカードを修正"], index=1)

        # ========================
        # 🎴 ビンゴカードを追加
        # ========================
        # カード追加モードに入ったときの初期化フラグ
        if "card_add_initialized" not in st.session_state:
            st.session_state.card_add_initialized = False

        if choice == "🎴 ビンゴカードを追加(必ず再読み込みしてください)":
            # 初回だけ new_cards を明示的に初期化
            if not st.session_state.card_add_initialized:
                st.session_state.new_cards = []
                st.session_state.card_add_initialized = True
            st.markdown("### 🆕 ビンゴカードを手入力で追加")


            if "clear_rows" not in st.session_state:
                st.session_state.clear_rows = False
            if "new_cards" not in st.session_state:
                st.session_state.new_cards = []

            new_card = []

            for i in range(5):
                key = f"row_{i}"
                default_value = "" if st.session_state.clear_rows else st.session_state.get(key, "")
                row_input = st.text_input(
                    f"{i+1}行目の数字（カンマ区切り）",  # ← 表示も修正
                    value=default_value,
                    key=key
                )

                parts = [p.strip() for p in row_input.strip().split(",") if p.strip()]  # カンマ区切りで分割＆空白除去

                if i == 2:
                    if len(parts) >= 2:
                        parts.insert(2, "FREE")
                    else:
                        parts = parts + ["FREE"]

                row = parts[:5] + [""] * (5 - len(parts))
                new_card.append(row)


            if st.button("➕ カードを追加"):
                valid = True
                error_msgs = []
                for i in range(5):
                    for j in range(5):
                        if i == 2 and j == 2:
                            continue  # FREEマス
                        value = new_card[i][j]
                        if value == "" or value is None:
                            error_msgs.append(f"{i+1}行{j+1}列が空白です")
                            valid = False
                        else:
                            try:
                                num = int(value)
                                if not (1 <= num <= 99):
                                    error_msgs.append(f"{i+1}行{j+1}列は1〜99の整数である必要があります")
                                    valid = False
                            except ValueError:
                                error_msgs.append(f"{i+1}行{j+1}列に無効な値が含まれています")
                                valid = False

                if valid:
                    st.session_state.new_cards.append(new_card)
                    st.session_state.clear_rows = True
                    st.rerun()
                else:
                    for msg in error_msgs:
                        st.error(msg)

            if st.session_state.get("clear_rows", False):
                st.session_state.clear_rows = False

            if st.session_state.new_cards:
                st.markdown("#### 現在追加されたカード一覧")
                for idx, card in enumerate(st.session_state.new_cards, start=1):
                    st.write(f"🃏 Card {idx}")
                    st.table(card)

                if st.button("💾 全て保存して次へ"):
                    os.makedirs(user_dir, exist_ok=True)

                    # 現在あるCSVファイルの最大番号を取得
                    existing_files = [
                        int(os.path.splitext(f)[0])
                        for f in os.listdir(user_dir)
                        if f.endswith(".csv") and os.path.splitext(f)[0].isdigit()
                    ]
                    base_idx = max(existing_files) if existing_files else 0

                    # 追加されたカードだけ保存
                    for i, card in enumerate(st.session_state.new_cards):
                        df = pd.DataFrame(card)
                        df.iloc[2, 2] = "FREE"
                        save_path = os.path.join(user_dir, f"{base_idx + i + 1}.csv")
                        df.to_csv(save_path, index=False, header=False)

                    # 保存後に new_cards をリセット
                    st.session_state.new_cards = []
                    st.session_state.card_add_initialized = False  # ←追加

                    st.success("✅ 全カードを保存しました。ページを再読み込みしてください。")
                    st.stop()
        # ========================
        # 🎯 ビンゴ判定に進む
        # ========================

        elif choice == "🎯 ビンゴ判定に進む":
            # 初期化
            # セッション初期化
            if "called" not in st.session_state:
                st.session_state.called = set()
            if "input_key" not in st.session_state:
                st.session_state.input_key = 0

            # 入力欄（キーをインクリメントでリセット対応）
            # 入力欄（キーをインクリメントでリセット対応）
            num = st.text_input(
                "数字を入力（カンマ区切り・Enterで追加/取消）",
                key=f"number_input_{st.session_state.input_key}"
            )
            # フォーム（送信ボタン用）
            with st.form("number_form"):
                submitted = st.form_submit_button("送信")

            # どちらかで反応する
            if num and (submitted or not submitted):
                # カンマで区切って複数入力対応
                inputs = [n.strip() for n in num.strip().split(",") if n.strip()]
                for n in inputs:
                    if n.isdigit():
                        if n in st.session_state.called:
                            st.session_state.called.remove(n)
                        else:
                            st.session_state.called.add(n)
                    else:
                        st.warning(f"⚠️ 無効な入力: {n}")
                
                # 入力欄のキーを変更してリセット
                st.session_state.input_key += 1
                st.rerun()  # 入力欄を即リセット（再実行）


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
        elif choice == "✏️ ビンゴカードを修正":
            st.markdown("### ✏️ 既存のビンゴカードを修正")
            csv_files = sorted(glob.glob(os.path.join(user_dir, "*.csv")))

            if not csv_files:
                st.warning("修正できるカードが存在しません")
            else:
                selected_file = st.selectbox("修正するカードを選んでください", csv_files, format_func=lambda x: os.path.basename(x))
                df = pd.read_csv(selected_file, header=None).fillna("").astype(str)

                edited = []
                for i in range(5):
                    row_input = st.text_input(f"{i+1}行目（カンマ区切り）", value=",".join(df.iloc[i]), key=f"edit_row_{i}")
                    parts = [p.strip() for p in row_input.split(",")]
                    edited.append(parts[:5] + [""] * (5 - len(parts)))

                if st.button("💾 このカードを保存"):
                    df_new = pd.DataFrame(edited)
                    df_new.iloc[2, 2] = "FREE"  # FREE セル補完
                    df_new.to_csv(selected_file, index=False, header=False)
                    st.success("✅ 修正を保存しました！")