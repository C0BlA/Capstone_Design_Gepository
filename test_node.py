import asyncio
import hashlib
import json
import platform
import socket
import uuid
from datetime import datetime, timezone

import websockets


SERVER_URL = "ws://211.229.208.209:8000/ws/nodes/connect"
NODE_NAME = "test-node-1"
NODE_GROUP = "default"
HEARTBEAT_INTERVAL_SECONDS = 5


def generate_machine_fingerprint_hash() -> str:
    raw = f"{uuid.getnode()}-{platform.node()}-{platform.machine()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_system_spec() -> dict:
    # 지금은 최소 버전으로 고정값/기본값 사용
    # 나중에 psutil 붙이면 cpu/ram 실제값 넣으면 됨
    return {
        "cpu_cores": 4,
        "ram_mb": 8192,
        "gpu_count": 0,
        "gpu_info": [],
        "os_info": platform.system(),
        "arch": platform.machine(),
    }


def build_register_message() -> dict:
    return {
        "type": "register",
        "node_name": NODE_NAME,
        "machine_fingerprint_hash": generate_machine_fingerprint_hash(),
        "host": socket.gethostname(),
        "node_group": NODE_GROUP,
        "spec": get_system_spec(),
    }


def build_heartbeat_message() -> dict:
    return {
        "type": "heartbeat",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "resource": {
            "cpu_usage": 10.0,
            "ram_usage_mb": 2048,
            "gpu_usage": [],
        },
    }


async def send_register(ws) -> int | None:
    message = build_register_message()
    await ws.send(json.dumps(message, ensure_ascii=False))
    print("[SEND] register")

    raw_response = await ws.recv()
    response = json.loads(raw_response)
    print("[RECV]", response)

    if response.get("type") == "register_ack":
        return response.get("node_id")

    if response.get("type") == "error":
        raise RuntimeError(response.get("message", "register failed"))

    raise RuntimeError(f"unexpected response after register: {response}")


async def send_heartbeat(ws) -> None:
    message = build_heartbeat_message()
    await ws.send(json.dumps(message, ensure_ascii=False))
    print("[SEND] heartbeat")

    raw_response = await ws.recv()
    response = json.loads(raw_response)
    print("[RECV]", response)

    if response.get("type") == "heartbeat_ack":
        return

    if response.get("type") == "error":
        raise RuntimeError(response.get("message", "heartbeat failed"))

    raise RuntimeError(f"unexpected response after heartbeat: {response}")


async def run_client() -> None:
    while True:
        try:
            print(f"[INFO] connecting to {SERVER_URL}")
            async with websockets.connect(SERVER_URL) as ws:
                node_id = await send_register(ws)
                print(f"[INFO] registered node_id={node_id}")

                while True:
                    await send_heartbeat(ws)
                    await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("[INFO] interrupted by user")
            raise
        except Exception as exc:
            print(f"[ERROR] {exc}")
            print("[INFO] reconnecting in 3 seconds...")
            await asyncio.sleep(3)
            
            
def build_register_message() -> dict:
    return {
        "type": "register",
        "token": "여기에_발급받은_원문토큰",
        "node_name": NODE_NAME,
        "machine_fingerprint_hash": generate_machine_fingerprint_hash(),
        "host": socket.gethostname(),
        "node_group": NODE_GROUP,
        "spec": get_system_spec(),
    }

if __name__ == "__main__":
    asyncio.run(run_client())