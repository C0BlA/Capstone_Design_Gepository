import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.schemas.ws import HeartbeatMessage, RegisterMessage
from app.services.node_service import NodeService
from app.db.models.node import Node
from app.ws.ws_manager import monitor_manager

router = APIRouter(tags=["node-websocket"])

active_connections: dict[int, WebSocket] = {}


async def broadcast_nodes(db: Session) -> None:
    nodes = db.query(Node).order_by(Node.id.asc()).all()

    payload = {
        "type": "nodes_snapshot",
        "nodes": [
            {
                "id": node.id,
                "owner_user_id": node.owner_user_id,
                "node_name": node.node_name,
                "host": node.host,
                "status": node.status,
                "cpu_cores": node.cpu_cores,
                "ram_mb": node.ram_mb,
                "gpu_count": node.gpu_count,
                "node_group": node.node_group,
                "os_info": node.os_info,
                "arch": node.arch,
                "last_seen_at": node.last_seen_at.isoformat() if node.last_seen_at else None,
                "is_active": node.is_active,
            }
            for node in nodes
        ],
    }

    await monitor_manager.broadcast(payload)


@router.websocket("/ws/nodes/connect")
async def node_connect(websocket: WebSocket):
    await websocket.accept()
    current_node_id: int | None = None

    try:
        while True:
            raw_message = await websocket.receive_text()
            payload = json.loads(raw_message)
            message_type = payload.get("type")

            with SessionLocal() as db:
                if message_type == "register":
                    try:
                        message = RegisterMessage(**payload)
                        node = NodeService.upsert_from_register(db, message)
                    except ValueError as exc:
                        await websocket.send_json({
                            "type": "error",
                            "message": str(exc),
                        })
                        continue

                    current_node_id = node.id
                    active_connections[node.id] = websocket

                    await websocket.send_json({
                        "type": "register_ack",
                        "node_id": node.id,
                        "owner_user_id": node.owner_user_id,
                        "status": node.status,
                    })

                    await broadcast_nodes(db)

                elif message_type == "heartbeat":
                    if current_node_id is None:
                        await websocket.send_json({
                            "type": "error",
                            "message": "register 메시지 이후 heartbeat를 보내야 합니다.",
                        })
                        continue

                    HeartbeatMessage(**payload)
                    node = NodeService.get_node(db, current_node_id)
                    if node is None:
                        await websocket.send_json({
                            "type": "error",
                            "message": "등록된 노드를 찾을 수 없습니다.",
                        })
                        continue

                    NodeService.mark_heartbeat(db, node)

                    await websocket.send_json({
                        "type": "heartbeat_ack",
                        "node_id": current_node_id,
                        "server_time": datetime.utcnow().isoformat(),
                    })

                    await broadcast_nodes(db)

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"지원하지 않는 메시지 타입입니다: {message_type}",
                    })

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        if current_node_id is not None:
            active_connections.pop(current_node_id, None)
            with SessionLocal() as db:
                node = NodeService.get_node(db, current_node_id)
                if node is not None:
                    NodeService.mark_offline(db, node)
                    await broadcast_nodes(db)


async def offline_watcher() -> None:
    while True:
        cutoff = datetime.utcnow() - timedelta(seconds=settings.heartbeat_timeout_seconds)
        with SessionLocal() as db:
            changed = False
            nodes = NodeService.list_nodes(db)
            for node in nodes:
                if node.last_seen_at and node.last_seen_at < cutoff and node.status != "offline":
                    NodeService.mark_offline(db, node)
                    active_connections.pop(node.id, None)
                    changed = True

            if changed:
                await broadcast_nodes(db)

        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan_context() -> AsyncIterator[None]:
    task = asyncio.create_task(offline_watcher())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass