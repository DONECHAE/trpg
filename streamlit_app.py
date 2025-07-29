import streamlit as st
import requests

FASTAPI_URL = "http://localhost:8000"

st.set_page_config(page_title="TRPG 시나리오", page_icon="🎲", layout="centered")
st.title("🎲 헤밍웨이 스타일 TRPG")

# --- 세션 상태 초기화 ---
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "worlds" not in st.session_state:
    st.session_state.worlds = None
if "selected_world" not in st.session_state:
    st.session_state.selected_world = None

# --- 1) 세계관 불러오기 ---
if st.session_state.worlds is None:
    res = requests.get(f"{FASTAPI_URL}/worlds")
    if res.status_code == 200:
        st.session_state.worlds = res.json().get("worlds", {})
    else:
        st.error("세계관을 불러오는 데 실패했습니다.")

# --- 2) 세계관 선택 ---
if st.session_state.session_id is None:
    st.subheader("세계관을 선택하세요")
    if st.session_state.worlds:
        worlds = list(st.session_state.worlds.keys())
        selected_world = st.radio("세계관 선택", worlds)
        st.write("### 선택한 세계관 미리보기")
        for line in st.session_state.worlds[selected_world]:
            st.write(f"- {line}")

        if st.button("TRPG 시작"):
            res = requests.post(f"{FASTAPI_URL}/start_trpg", json={"world": selected_world})
            if res.status_code == 200:
                data = res.json()
                st.session_state.session_id = data["session_id"]
                st.session_state.selected_world = selected_world
                st.session_state.messages.append(("system", f"🌍 {selected_world} TRPG 시작!"))
                st.session_state.messages.append(("bot", data["scene"]))
            else:
                st.error("TRPG 시작에 실패했습니다.")

# --- 3) 챗봇 스타일 시나리오 진행 ---
if st.session_state.session_id:
    st.subheader(f"세계관: {st.session_state.selected_world}")
    for sender, msg in st.session_state.messages:
        with st.chat_message("assistant" if sender == "bot" else "user"):
            st.markdown(msg)

    # 사용자 입력
    if user_input := st.chat_input("행동을 입력하세요 (헤밍웨이 스타일, 짧게)"):
        st.session_state.messages.append(("user", user_input))

        # 서버에 턴 요청
        res = requests.post(f"{FASTAPI_URL}/next_turn", json={
            "session_id": st.session_state.session_id,
            "action": user_input
        })
        if res.status_code == 200:
            data = res.json()
            next_scene = data["scene"]
            st.session_state.messages.append(("bot", next_scene))
            st.rerun()
        else:
            st.error("서버 오류로 진행할 수 없습니다.")