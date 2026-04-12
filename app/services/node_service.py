import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.node import Node
from app.schemas.node import NodeCreate, NodeUpdate
from app.schemas.ws import RegisterMessage


class NodeService:
    @staticmethod
    def list_nodes(db: Session) -> list[Node]:
        return list(db.scalars(select(Node).order_by(Node.id.desc())).all())

    @staticmethod
    def get_node(db: Session, node_id: int) -> Node | None:
        return db.get(Node, node_id)

    @staticmethod
    def get_by_fingerprint(db: Session, fingerprint_hash: str) -> Node | None:
        stmt = select(Node).where(Node.machine_fingerprint_hash == fingerprint_hash)
        return db.scalar(stmt)

    @staticmethod
    def create_node(db: Session, payload: NodeCreate) -> Node:
        node = Node(
            owner_user_id=payload.owner_user_id,
            node_name=payload.node_name,
            host=payload.host,
            machine_fingerprint_hash=payload.machine_fingerprint_hash,
            node_group=payload.node_group,
            cpu_cores=payload.cpu_cores,
            ram_mb=payload.ram_mb,
            gpu_count=payload.gpu_count,
            gpu_info_json=json.dumps(payload.gpu_info or []),
            os_info=payload.os_info,
            arch=payload.arch,
            is_active=payload.is_active,
            status="offline",
        )
        db.add(node)
        db.commit()
        db.refresh(node)
        return node

    @staticmethod
    def update_node(db: Session, node: Node, payload: NodeUpdate) -> Node:
        update_data = payload.model_dump(exclude_unset=True)
        if "gpu_info" in update_data:
            node.gpu_info_json = json.dumps(update_data.pop("gpu_info") or [])

        for key, value in update_data.items():
            setattr(node, key, value)

        db.commit()
        db.refresh(node)
        return node

    @staticmethod
    def upsert_from_register(db: Session, message: RegisterMessage) -> Node:
        node = NodeService.get_by_fingerprint(db, message.machine_fingerprint_hash)
        gpu_info_json = json.dumps(message.spec.gpu_info or [])

        if node is None:
            node = Node(
                owner_user_id=message.owner_user_id,
                node_name=message.node_name,
                host=message.host,
                machine_fingerprint_hash=message.machine_fingerprint_hash,
                node_group=message.node_group,
                status="online",
                cpu_cores=message.spec.cpu_cores,
                ram_mb=message.spec.ram_mb,
                gpu_count=message.spec.gpu_count,
                gpu_info_json=gpu_info_json,
                os_info=message.spec.os_info,
                arch=message.spec.arch,
                is_active=True,
                last_seen_at=datetime.utcnow(),
            )
            db.add(node)
        else:
            node.owner_user_id = message.owner_user_id
            node.node_name = message.node_name
            node.host = message.host
            node.node_group = message.node_group
            node.status = "online"
            node.cpu_cores = message.spec.cpu_cores
            node.ram_mb = message.spec.ram_mb
            node.gpu_count = message.spec.gpu_count
            node.gpu_info_json = gpu_info_json
            node.os_info = message.spec.os_info
            node.arch = message.spec.arch
            node.last_seen_at = datetime.utcnow()

        db.commit()
        db.refresh(node)
        return node

    @staticmethod
    def mark_heartbeat(db: Session, node: Node) -> Node:
        node.last_seen_at = datetime.utcnow()
        if node.status == "offline":
            node.status = "online"
        db.commit()
        db.refresh(node)
        return node

    @staticmethod
    def mark_offline(db: Session, node: Node) -> None:
        node.status = "offline"
        db.commit()
