import streamlit as st
from openai import OpenAI
import os
import uuid
from dotenv import load_dotenv

# --- .env 자동 로딩 ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="헤밍웨이 TRPG", page_icon="🎲")
st.title("🎲 헤밍웨이 스타일 TRPG")

# --- 세션 상태 초기화 ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

world_list = ["중세 판타지", "사이버펑크", "아포칼립스", "우주 탐험", "무협", "현대 스릴러"]
world = st.selectbox("세계관을 선택하세요", world_list)

# --- 1) 세계관 미리보기 ---
if st.button("🌍 세계관 미리보기"):
    prompt = f"""
    세계관: {world}
    헤밍웨이 스타일 초단문 3줄로 세계관을 묘사하세요.
    각 줄은 3~6단어, 감정을 함축하며 긴장감 있게.

    예시:
    안개가 성을 덮는다.
    성벽 위 까마귀 기다린다.
    어둠에 검이 번뜬다.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "헤밍웨이 스타일 TRPG 시나리오 작가"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    preview = response.choices[0].message.content.strip()
    st.write("### 🌍 세계관 미리보기")
    st.text(preview)

# --- 2) TRPG 시작 ---
if st.button("TRPG 시작"):
    prompt = f"""
    세계관: {world}
    헤밍웨이 스타일 초단문으로 TRPG의 첫 장면 5줄 작성.
    각 줄은 3~6단어, 간결하고 강렬하며 감정을 함축.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "헤밍웨이 스타일 TRPG 시나리오 작가"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )
    first_scene = response.choices[0].message.content.strip()
    st.session_state.messages = [("bot", first_scene)]

# --- 3) 기존 대화 출력 ---
if st.session_state.messages:
    st.subheader("💬 TRPG 대화")
    for sender, msg in st.session_state.messages:
        with st.chat_message("assistant" if sender == "bot" else "user"):
            st.markdown(msg)

# --- 4) 플레이어 행동 입력 ---
if st.session_state.messages:
    if user_input := st.chat_input("행동을 입력하세요 (헤밍웨이 스타일, 짧게)"):
        st.session_state.messages.append(("user", user_input))
        last_scene = st.session_state.messages[-2][1]

        prompt = f"""
        세계관: {world}
        지금까지의 이야기:
        {last_scene}

        플레이어 행동: {user_input}

        헤밍웨이 초단문 스타일로 3~5줄 시나리오를 이어 작성하세요.
        각 줄은 3~6단어. 간결하고 강렬하며 감정을 함축.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "헤밍웨이 스타일 TRPG 시나리오 작가"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        next_scene = response.choices[0].message.content.strip()
        st.session_state.messages.append(("bot", next_scene))
        st.rerun()