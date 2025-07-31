import streamlit as st
from openai import OpenAI
import os
import uuid
from dotenv import load_dotenv

# --- .env 자동 로딩 ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="텍스트 게임", page_icon="🎲")
st.title("🎲 텍스트 게임")

# --- 공통 시스템 프롬프트 ---
system_prompt = """
당신은 헤밍웨이 스타일의 초단문 TRPG 시나리오 작가입니다.
- 모든 출력은 **항상 3줄**, 각 줄 3~6단어
- 불필요한 접속사나 설명 제거, 단호하고 감정적인 묘사
- 플레이어 행동을 적극 반영하고 장면에 상호작용 포함
- 플레이어의 선택과 반응을 유도하며 자연스럽게 이어짐
- 스스로 이야기를 끝내지 말고, 결말은 플레이어의 행동으로 도달
- 플레이어가 죽거나 최종장에서 결말을 맞이하면 마지막 줄 끝에 [END]를 추가
"""

# --- 세션 상태 초기화 ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

world = st.text_input("세계관을 입력하세요", placeholder="예: 중세 판타지, 우주 전쟁, 좀비 아포칼립스 등")

# --- 1) 세계관 미리보기 ---
if st.button("🌍 세계관 미리보기"):
    prompt = f"""
    세계관: {world}
    이 세계관의 분위기와 시작 장면을 3줄로 묘사해 주세요.
    각 줄은 3~6단어, 감정과 긴장감을 함축.
    장면 전환은 부드럽게 하세요.
    스스로 이야기를 끝내지 마세요. 결말은 플레이어 행동으로 도달해야 합니다.
    [END]는 플레이어가 죽거나 최종장에 도달했을 때만 마지막 줄에 추가하세요.
    헤밍웨이 초단문 스타일로 항상 3줄 작성.

    예시:
    안개 낀 성문
    까마귀 울음 번진다
    검은 그림자 스친다
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt + "\n\n" + prompt}
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
    TRPG의 첫 장면을 3줄로 작성.
    각 줄 3~6단어, 간결하고 강렬하며 감정 함축.
    이야기는 자연스럽게 이어지고 플레이어의 행동에 따라 발전.
    스스로 이야기를 끝내지 마세요. 결말은 플레이어 행동으로 도달해야 합니다.
    [END]는 플레이어가 죽거나 최종장에 도달했을 때만 마지막 줄에 추가하세요.
    헤밍웨이 초단문 스타일로 항상 3줄 작성.

    예시:
    비 내린 골목
    등불 아래 그림자 멈춘다
    문 삐걱 열렸다
    """
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt + "\n\n" + prompt}
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
    if user_input := st.chat_input("행동을 입력하세요 (간단명료, 짧게)"):
        st.session_state.messages.append(("user", user_input))

        prompt = f"""
        세계관: {world}

        지금까지의 이야기:
        {''.join([msg for sender, msg in st.session_state.messages if sender=='bot'])}

        플레이어 행동: {user_input}

        플레이어 행동을 적극 반영하고, 그 결과를 최소 한 줄 이상 묘사하세요.
        헤밍웨이 초단문 스타일로 **항상 3줄만 작성**, 각 줄 3~6단어.
        세 줄은 서로 자연스럽게 이어져야 하며, 감정과 장면이 부드럽게 연결되어야 합니다.
        불필요한 설명 없이 플레이어의 행동 결과가 명확히 드러나야 합니다.
        스스로 결말을 내지 마세요. 결말은 플레이어가 죽거나 최종장에 도달했을 때만 마지막 줄 끝에 [END]를 추가하세요.

        예시:
        어둠 속 발자국
        바닥에 부서진 검
        멀리서 까마귀 울음
        """
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt + "\n\n" + prompt}
            ],
            max_tokens=200
        )
        next_scene = response.choices[0].message.content.strip()
        lines = [line.strip() for line in next_scene.splitlines() if line.strip()]

        # 항상 3줄 유지
        if len(lines) > 3:
            lines = lines[:3]
        elif len(lines) < 3:
            while len(lines) < 3:
                lines.append(lines[-1])

        next_scene = "\n".join(lines)
        formatted_scene = "```\n" + "\n".join(lines) + "\n```"
        st.session_state.messages.append(("bot", formatted_scene))

        # --- 종료 체크 ---
        if "[END]" in next_scene:
            st.subheader("🏁 게임 종료")
            st.stop()  # 이후 입력 차단

        st.rerun()