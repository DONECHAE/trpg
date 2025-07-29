import streamlit as st
from openai import OpenAI
import os
import uuid

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("🎲 헤밍웨이 스타일 TRPG")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

world = st.selectbox("세계관 선택", ["중세 판타지", "사이버펑크", "아포칼립스"])

if st.button("TRPG 시작"):
    prompt = f"""
    세계관: {world}
    헤밍웨이 스타일 초단문으로 TRPG의 첫 장면 5줄 작성.
    각 줄은 3~6단어, 간결하고 강렬하며 감정을 함축.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "헤밍웨이 스타일 TRPG 시나리오 작가"},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )
    first_scene = response.choices[0].message.content.strip()
    st.session_state.messages = [("bot", first_scene)]

# 기존 대화 출력
for sender, msg in st.session_state.messages:
    with st.chat_message("assistant" if sender == "bot" else "user"):
        st.markdown(msg)

# 플레이어 행동 입력
if user_input := st.chat_input("행동을 입력하세요 (헤밍웨이 스타일, 짧게)"):
    st.session_state.messages.append(("user", user_input))
    last_scene = st.session_state.messages[-2][1]

    prompt = f"""
    세계관: {world}
    지금까지의 이야기:
    {last_scene}

    플레이어 행동: {user_input}
    헤밍웨이 초단문 스타일로 3~5줄 시나리오를 이어 작성하세요.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "헤밍웨이 스타일 TRPG 시나리오 작가"},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )
    next_scene = response.choices[0].message.content.strip()
    st.session_state.messages.append(("bot", next_scene))
    st.rerun()