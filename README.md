# Gepository Backend

프론트엔드(UI/UX)와 서버(agent resource server) 사이를 중계하는 FastAPI 백엔드입니다.

---

## 구현 완료 항목

### 1. 백엔드 API (`Capstone_Design_Gepository-backend/`)

| 메서드 | 경로 | 상태 | 설명 |
|--------|------|------|------|
| GET  | `/health` | ✅ 완료 | 헬스 체크 |
| POST | `/api/auth/signup` | ✅ 완료 | 서버 `POST /api/auth/register` 중계 → 성공 시 API 토큰 자동 발급 |
| POST | `/api/auth/login` | ⚠️ 부분 완료 | username 존재 여부만 확인 (비밀번호 검증 미구현, 아래 한계 참고) |
| POST | `/api/chat` | ✅ 완료 | idle → online 노드 탐색 후 서버에 태스크 생성, 결과 반환 |

**채팅 흐름:**
```
POST /api/chat
  → GET  서버/api/nodes        (idle 노드 탐색, 없으면 online 폴백)
  → POST 서버/api/tasks        (프롬프트 + 노드 ID로 태스크 생성)
  → 태스크 생성 결과 반환      (LLM 연동 전 placeholder 메시지 포함)
```

### 2. 프론트엔드 연결 (`Capstone_Design_Gepository-main/`)

| 파일 | 변경 내용 |
|------|-----------|
| `login.html` | 입력 필드 id 추가, 로그인 버튼 → `handleLogin()` 연결 |
| `signup.html` | 입력 필드 id 추가, 가입 완료 버튼 → `handleSignup()` 연결 |
| `main.html` | 채팅 input/전송 버튼 id 추가, `sendMessage()` 연결 |
| `script.js` | 하드코딩 더미 데이터 제거, 백엔드 API 실제 호출로 교체 |

`script.js` 추가 함수:
- `handleLogin(event)` — `POST /api/auth/login`, 성공 시 `sessionStorage`에 user 저장 후 `main.html` 이동
- `handleSignup()` — `POST /api/auth/signup`, 비밀번호 확인 검증 포함
- `sendMessage()` — `POST /api/chat`, Enter 키 지원, 봇 응답 렌더링

---

## 미완료 / 한계 사항

| 항목 | 이유 | 해결 방법 |
|------|------|-----------|
| 로그인 비밀번호 검증 없음 | 서버에 `POST /api/auth/login` 엔드포인트 없음 | 서버 측에 login 엔드포인트 추가 후 `app/api/auth.py`의 `login()` 교체 |
| LLM 실제 응답 없음 | LLM 연동 전 단계 | `app/api/chat.py`의 `chat()` 함수에서 태스크 완료 후 결과를 polling하거나 WebSocket으로 수신하도록 확장 |
| MySQL 연결 (서버) | `Capstone_Design_Gepository-server/.env`의 DB 비밀번호 불일치 | 아래 DB 설정 참고 |

---

## 실행 방법

### 사전 조건
- Python 3.11+
- MySQL 실행 중 + `agent_server` DB 존재
- `Capstone_Design_Gepository-server`가 port 8000에서 실행 중

### 1. 가상환경 & 의존성 설치

```bash
cd Capstone_Design_Gepository-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 기본값 (필요 시 수정):
```
SERVER_URL=http://localhost:8000
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8001
```

### 3. 백엔드 실행

```bash
python main.py
# 또는
uvicorn main:app --reload --port 8001
```

### 4. 프론트엔드 열기

```bash
cd ../Capstone_Design_Gepository-main
python3 -m http.server 3000
# → http://localhost:3000/login.html
```

### 전체 실행 순서

```
1. MySQL 실행
2. agent_server DB 및 테이블 준비 (최초 1회)
   cd Capstone_Design_Gepository-server
   mysql -u root -p<비밀번호> -e "CREATE DATABASE IF NOT EXISTS agent_server;"
   .venv/bin/python -m alembic upgrade head
3. 서버 실행  (port 8000)
   cd Capstone_Design_Gepository-server && .venv/bin/python run.py
4. 백엔드 실행 (port 8001)  ← 이 프로젝트
   cd Capstone_Design_Gepository-backend && python main.py
5. 브라우저에서 http://localhost:3000/login.html 열기
```

---

## DB 설정 (서버 팀 확인 필요)

`Capstone_Design_Gepository-server/.env`의 DB 비밀번호가 실제 MySQL과 불일치합니다.  
서버 팀에서 올바른 비밀번호로 수정해야 합니다:

```
DATABASE_URL=mysql+pymysql://root:<실제 비밀번호>@localhost:3306/agent_server
```

또한 서버의 `requirements.txt`에 `cryptography` 패키지가 누락되어 있습니다 (MySQL 8.0 인증에 필요).  
서버 `requirements.txt`에 추가 필요:
```
cryptography
```

---

## 폴더 구조

```
Capstone_Design_Gepository-backend/
├── main.py              # FastAPI 앱 진입점, CORS 설정
├── requirements.txt
├── .env.example
└── app/
    ├── api/
    │   ├── auth.py      # POST /api/auth/signup, /api/auth/login
    │   └── chat.py      # POST /api/chat
    └── core/
        └── config.py    # 환경 변수 (SERVER_URL, 포트 등)
```

---

## LLM 연동 시 수정 위치

`app/api/chat.py` — `chat()` 함수 끝부분:

```python
# 현재 (임시 응답)
return {
    "task": task,
    "node": selected_node,
    "reply": f"[태스크 #{task['id']} 생성됨] 현재 LLM 연동 준비 중입니다.",
}

# LLM 연동 후 → task 완료 대기 또는 WebSocket 스트리밍으로 교체
```
