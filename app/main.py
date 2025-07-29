from fastapi import FastAPI
from pydantic import BaseModel
import os
from openai import OpenAI
import uuid

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

WORLD_LIST = ["중세 판타지", "사이버펑크", "아포칼립스","우주탐험","무협","전통판타지","현대 스릴러","고대 신화"]
SESSION_STORE = {}

class WorldRequest(BaseModel):
    world: str

class ActionRequest(BaseModel):
    session_id: str
    action: str  # 플레이어 행동 (짧고 간결한 헤밍웨이 스타일)

@app.get("/")
def home():
    return {"message": "TRPG 서버 작동 중"}

@app.get("/worlds")
def get_worlds():
    """3개의 세계관에 대한 GPT 3줄 초단문 소개 (헤밍웨이 스타일)"""
    result = {}
    for world in WORLD_LIST:
        prompt = f"""
        세계관: {world}
        헤밍웨이 스타일 초단문 3줄로 세계관을 묘사하세요.
        각 줄은 3~6단어, 감정을 함축하며 긴장감 있게.
        예시:
            안개가 성을 덮는다.  
            성벽 위 까마귀 기다린다.  
            어둠에 검이 번뜬다.
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 헤밍웨이 스타일의 초단문 TRPG 시나리오 작가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            gpt_text = response.choices[0].message.content.strip()
            intro_lines = [line.strip() for line in gpt_text.split("\n") if line.strip()][:3]
            result[world] = intro_lines
        except Exception as e:
            result[world] = [f"Error: {str(e)}"]
    return {"worlds": result}

@app.post("/start_trpg")
def start_trpg(req: WorldRequest):
    """헤밍웨이 초단문 스타일 첫 장면 작성 & 세션 시작"""
    if req.world not in WORLD_LIST:
        return {"error": "존재하지 않는 세계관입니다."}

    session_id = str(uuid.uuid4())

    prompt = f"""
    세계관: {req.world}
    헤밍웨이 스타일 초단문으로 TRPG의 첫 장면 5줄 작성.
    각 줄은 3~6단어. 간결하고 강렬하며, 감정을 함축.
    예시:
    Night falls. Wolves howl.
    Blade cold. Breath fogs.
    Door creaks. Silence answers.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 헤밍웨이 스타일의 초단문 TRPG 시나리오 작가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        first_scene = response.choices[0].message.content.strip()

        # 세션 저장
        SESSION_STORE[session_id] = {
            "world": req.world,
            "history": [first_scene]
        }

        return {"session_id": session_id, "world": req.world, "scene": first_scene}
    except Exception as e:
        return {"error": str(e)}

@app.post("/next_turn")
def next_turn(req: ActionRequest):
    """플레이어 행동을 받아 초단문 헤밍웨이 스타일로 다음 장면 작성"""
    session = SESSION_STORE.get(req.session_id)
    if not session:
        return {"error": "세션이 존재하지 않습니다."}

    world = session["world"]
    last_scene = session["history"][-1]

    prompt = f"""
    세계관: {world}
    지금까지의 이야기:
    {last_scene}

    플레이어 행동: {req.action}

    헤밍웨이 초단문 스타일로 3~5줄 시나리오를 이어 작성하세요.
    각 줄 3~6단어. 간결, 강렬, 함축적.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 헤밍웨이 스타일의 초단문 TRPG 시나리오 작가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        next_scene = response.choices[0].message.content.strip()

        # 세션 업데이트
        session["history"].append(next_scene)

        return {"session_id": req.session_id, "scene": next_scene}
    except Exception as e:
        return {"error": str(e)}

# docker stop fastapi-container
# docker rm fastapi-container
# docker build -t fastapi-app .
# docker run -d -p 8000:8000 --name fastapi-container fastapi-app
# curl http://localhost:8000
# {"message": "Hello, FastAPI with Docker!"}

# 1. 기존 컨테이너 중지 및 삭제
# docker stop fastapi-container
# docker rm fastapi-container

# # 2. 이미지 재빌드
# docker build -t fastapi-app .

# # 3. 컨테이너 실행 (환경변수 주입)
# docker run -d -p 8000:8000 --env-file .env --name fastapi-container fastapi-app

# # 4. 로그 확인
# docker logs fastapi-container

# docker rm -f trpg-container
# docker build --no-cache -t fastapi-trpg .
# docker run -d -p 8000:8000 --name trpg-container \
#     -e OPENAI_API_KEY=your_api_key fastapi-trpg
