# Gepository — 통합 브랜치 (integrated)

분산 LLM 플랫폼 캡스톤 프로젝트입니다.  
이 브랜치는 **프론트엔드 · 백엔드 · 서버**를 하나의 레포에 통합한 버전입니다.

---

## 폴더 구조

```
Gepository/
├── frontend/           ← UI (HTML/CSS/JS)
│   ├── login.html
│   ├── signup.html
│   ├── main.html
│   ├── script.js
│   └── style.css
│
├── backend/            ← FastAPI 중계 서버 (port 8001)
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── api/
│       │   ├── auth.py     # POST /api/auth/signup, /api/auth/login
│       │   └── chat.py     # POST /api/chat
│       └── core/
│           └── config.py
│
└── server/             ← Agent Resource Server (port 8000)
    ├── run.py
    ├── requirements.txt
    ├── .env.example
    ├── alembic.ini
    ├── alembic/        ← DB 마이그레이션
    └── app/
        ├── api/routes/ # auth, nodes, tasks
        ├── db/         # SQLAlchemy 모델
        ├── schemas/
        ├── services/
        └── ws/         # WebSocket (노드 연결, 모니터)
```

---

## 전체 흐름

```
브라우저 (3000)
    ↕ HTTP
backend/ (8001)   ← 프론트 요청 중계, 노드 탐색 로직
    ↕ HTTP
server/ (8000)    ← REST API, WebSocket
    ↕
MySQL (3306)
```

---

## 실행 방법

### 최초 1회 — 환경 세팅

#### 1. MySQL 데이터베이스 생성
```bash
mysql -u root -p<비밀번호> -e "CREATE DATABASE IF NOT EXISTS agent_server;"
```

#### 2. server 의존성 설치 & DB 테이블 생성
```bash
cd server
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install cryptography email-validator   # 누락 패키지 추가 설치

# DB 비밀번호 설정
cp .env.example .env
# .env 파일에서 아래 줄 수정:
# DATABASE_URL=mysql+pymysql://root:<비밀번호>@localhost:3306/agent_server

python -m alembic upgrade head   # 테이블 생성
```

#### 3. backend 의존성 설치
```bash
cd ../backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 매번 실행 순서

터미널 3개를 열어 각각 실행합니다.

**터미널 1 — server (port 8000)**
```bash
cd server
source .venv/bin/activate
python run.py
# "Application startup complete" 확인
```

**터미널 2 — backend (port 8001)**
```bash
cd backend
source .venv/bin/activate
python main.py
# "Application startup complete" 확인
```

**터미널 3 — frontend (port 3000)**
```bash
cd frontend
python3 -m http.server 3000
```

**브라우저**
```
http://localhost:3000/login.html
```

---

## API 엔드포인트

### backend (port 8001)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET  | `/health` | 헬스 체크 |
| POST | `/api/auth/signup` | 회원가입 |
| POST | `/api/auth/login` | 로그인 |
| POST | `/api/chat` | 채팅 메시지 전송 |

### server (port 8000)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/auth/register` | 유저 생성 |
| POST | `/api/auth/tokens` | API 토큰 발급 |
| GET  | `/api/nodes` | 노드 목록 조회 |
| POST | `/api/tasks` | 태스크 생성 |
| GET  | `/api/tasks/{id}` | 태스크 조회 |
| WS   | `/ws/nodes/connect` | 노드 WebSocket 연결 |
| WS   | `/ws/monitor` | 모니터링 WebSocket |

---

## 현재 한계 (LLM 연동 전)

| 항목 | 상태 |
|------|------|
| 회원가입 | ✅ 동작 (MySQL 연결 필요) |
| 로그인 | ⚠️ 비밀번호 검증 없음 — 서버에 login 엔드포인트 추가 필요 |
| 채팅 | ⚠️ 태스크 생성까지만 동작, LLM 응답 없음 |
| 노드 연결 | ✅ WebSocket으로 노드 등록·하트비트 동작 |

---

## 브랜치 구성

| 브랜치 | 내용 |
|--------|------|
| `main` | 기본 브랜치 |
| `UI/UX` | 프론트엔드 원본 |
| `server` | 서버 원본 |
| `backend` | 백엔드 작업 브랜치 |
| `integrated` | **세 파트 통합 (현재 브랜치)** |