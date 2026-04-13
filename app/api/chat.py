from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    user_id: int | None = None


@router.post("")
async def chat(payload: ChatRequest):
    """
    채팅 처리 흐름:
    1. 서버 GET /api/nodes 에서 status=="idle" 노드 탐색
    2. idle 노드 없으면 "online" 노드로 폴백
    3. 서버 POST /api/tasks 로 태스크 생성
    4. 현재는 LLM 연동 전이므로 태스크 생성 결과를 그대로 반환
    """
    async with httpx.AsyncClient() as client:
        nodes_resp = await client.get(f"{settings.server_url}/api/nodes")

    if nodes_resp.status_code != 200:
        raise HTTPException(status_code=502, detail="노드 목록 조회에 실패했습니다.")

    nodes = nodes_resp.json()

    # idle → online 순으로 사용 가능한 노드 탐색
    selected_node = next((n for n in nodes if n["status"] == "idle"), None)
    if selected_node is None:
        selected_node = next((n for n in nodes if n["status"] == "online"), None)

    task_payload = {
        "prompt": payload.message,
        "assignment_mode": "auto" if selected_node is None else "manual",
        "requester_user_id": payload.user_id,
        "selected_node_id": selected_node["id"] if selected_node else None,
    }

    async with httpx.AsyncClient() as client:
        task_resp = await client.post(
            f"{settings.server_url}/api/tasks",
            json=task_payload,
        )

    if task_resp.status_code != 201:
        detail = task_resp.json().get("detail", "태스크 생성에 실패했습니다.")
        raise HTTPException(status_code=task_resp.status_code, detail=detail)

    task = task_resp.json()
    return {
        "task": task,
        "node": selected_node,
        # LLM 연동 전 임시 응답
        "reply": f"[태스크 #{task['id']} 생성됨] 현재 LLM 연동 준비 중입니다. 잠시 후 결과가 전달될 예정입니다.",
    }
