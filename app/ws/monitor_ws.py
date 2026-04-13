from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ws.ws_manager import monitor_manager

router = APIRouter()


@router.websocket("/ws/monitor")
async def monitor_websocket(websocket: WebSocket):
    await monitor_manager.connect(websocket)

    try:
        while True:
            # 연결 유지용
            await websocket.receive_text()
    except WebSocketDisconnect:
        monitor_manager.disconnect(websocket)
    except Exception:
        monitor_manager.disconnect(websocket)