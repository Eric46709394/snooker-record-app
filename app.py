import streamlit as st
import pandas as pd
from collections import defaultdict

# 初始化狀態
if 'page' not in st.session_state:
    st.session_state.page = 'setup'

if 'players' not in st.session_state:
    st.session_state.players = []

if 'matches' not in st.session_state:
    st.session_state.matches = []

if 'match_counts' not in st.session_state:
    st.session_state.match_counts = defaultdict(int)

if 'match_index' not in st.session_state:
    st.session_state.match_index = 1

if 'total_matches' not in st.session_state:
    st.session_state.total_matches = 0

def restart_app():
    st.session_state.page = 'setup'
    st.session_state.players = []
    st.session_state.matches = []
    st.session_state.match_counts = defaultdict(int)
    st.session_state.match_index = 1
    st.session_state.total_matches = 0

def setup_page():
    st.title("🏓 桌球記分記錄")
    num_players = st.number_input("請輸入玩家人數（至少 2 位）", min_value=2, step=1)

    with st.form("player_form"):
        player_names = []
        for i in range(num_players):
            name = st.text_input(f"玩家 {i+1} 名稱", key=f"name_{i}")
            player_names.append(name)

        submitted = st.form_submit_button("開始比賽")
        if submitted:
            if "" in player_names:
                st.warning("所有玩家名稱都需要填寫")
            else:
                st.session_state.players = player_names
                n = len(player_names)
                st.session_state.total_matches = n * (n - 1)
                st.session_state.page = 'match'

def match_page():
    st.subheader(f"第 {st.session_state.match_index} 局 / 共 {st.session_state.total_matches} 局")
    players = st.session_state.players

    with st.form("match_form"):
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.selectbox("玩家 1", players, key=f"p1_{st.session_state.match_index}")
        with col2:
            p2 = st.selectbox("玩家 2", players, key=f"p2_{st.session_state.match_index}")

        s1 = st.number_input(f"{p1} 得分", min_value=0, step=1, key=f"s1_{st.session_state.match_index}")
        s2 = st.number_input(f"{p2} 得分", min_value=0, step=1, key=f"s2_{st.session_state.match_index}")

        break_player = st.selectbox("單桿最高分球員", [p1, p2], key=f"bp_{st.session_state.match_index}")
        break_score = st.number_input("單桿最高分", min_value=0, step=1, key=f"bs_{st.session_state.match_index}")

        submitted = st.form_submit_button("儲存並進入下一局")

        if submitted:
            if p1 == p2:
                st.error("請選擇兩位不同玩家")
                return

            pair = tuple(sorted([p1, p2]))
            if st.session_state.match_counts[pair] >= 2:
                st.error(f"{p1} 和 {p2} 已對戰兩次，請選其他對手")
                return

            match = {
                "player1": p1,
                "player2": p2,
                "scores": {p1: s1, p2: s2},
                "highest_break_player": break_player,
                "highest_break_score": break_score
            }

            st.session_state.matches.append(match)
            st.session_state.match_counts[pair] += 1
            st.session_state.match_index += 1

            if st.session_state.match_index > st.session_state.total_matches:
                st.session_state.page = 'stats'

def stats_page():
    st.header("📊 比賽統計結果")

    stats = {p: {"wins": 0, "max_score": 0} for p in st.session_state.players}
    highest_break = {"score": 0, "player": ""}
    highest_match = {"score": 0, "player": ""}

    for match in st.session_state.matches:
        p1, p2 = match["player1"], match["player2"]
        s1, s2 = match["scores"][p1], match["scores"][p2]
        bp, bs = match["highest_break_player"], match["highest_break_score"]

        if s1 > s2:
            stats[p1]["wins"] += 1
        elif s2 > s1:
            stats[p2]["wins"] += 1

        for player, score in match["scores"].items():
            if score > stats[player]["max_score"]:
                stats[player]["max_score"] = score
            if score > highest_match["score"]:
                highest_match = {"score": score, "player": player}

        if bs > highest_break["score"]:
            highest_break = {"score": bs, "player": bp}

    df = pd.DataFrame([
        {"玩家": p, "勝場": stats[p]["wins"], "單場最高得分": stats[p]["max_score"]}
        for p in st.session_state.players
    ])

    df = df.sort_values(by=["勝場", "單場最高得分"], ascending=[False, False])
    df["排名"] = range(1, len(df)+1)

    st.dataframe(df[["排名", "玩家", "勝場", "單場最高得分"]], use_container_width=True)

    st.markdown(f"🏆 **單場最高得分：** {highest_match['player']}（{highest_match['score']} 分）")
    st.markdown(f"🎯 **單桿最高分：** {highest_break['player']}（{highest_break['score']} 分）")

    st.button("🔁 重新開始", on_click=restart_app)

# 控制流程頁面切換
if st.session_state.page == 'setup':
    setup_page()
elif st.session_state.page == 'match':
    match_page()
elif st.session_state.page == 'stats':
    stats_page()