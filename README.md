# Agent Resource Server

FastAPI + MySQL 기반의 최소 서버 뼈대입니다.

## 포함 기능
- 노드 CRUD API
- 태스크 CRUD 일부 API
- FastAPI WebSocket 기반 노드 register / heartbeat
- heartbeat timeout 시 offline 처리
- SQLAlchemy 모델
- Alembic 마이그레이션 초안

## 실행

```bash
python -m venv .venv
source .venv/bin/activate  # Windows는 .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

MySQL에 `agent_server` 데이터베이스를 먼저 생성한 뒤:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

## 주요 엔드포인트
- `GET /`
- `GET /api/nodes`
- `POST /api/nodes`
- `PATCH /api/nodes/{node_id}`
- `GET /api/tasks`
- `POST /api/tasks`
- `WS /ws/nodes/connect`

## WebSocket 메시지 예시

### register
```json
{
  "type": "register",
  "owner_user_id": 1,
  "node_name": "worker-01",
  "host": "192.168.0.10",
  "machine_fingerprint_hash": "0123456789abcdef0123456789abcdef",
  "node_group": "gpu-high",
  "spec": {
    "cpu_cores": 16,
    "ram_mb": 32768,
    "gpu_count": 1,
    "gpu_info": [{"name": "RTX 4080", "vram_mb": 16384}],
    "os_info": "ubuntu22.04",
    "arch": "x86_64"
  }
}
```

### heartbeat
```json
{
  "type": "heartbeat",
  "timestamp": "2026-04-11T14:10:00",
  "resource": {
    "cpu_usage": 12.5,
    "ram_usage_mb": 9000,
    "gpu_usage": [{"index": 0, "util": 40, "vram_used_mb": 2048}]
  }
}
```
