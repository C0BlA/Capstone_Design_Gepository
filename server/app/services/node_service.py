from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.node import Node
from app.schemas.ws import RegisterMessage
from app.services.auth_service import AuthService


class NodeService:
    @staticmethod
    def get_node(db: Session, node_id: int) -> Node | None:
        return db.query(Node).filter(Node.id == node_id).first()

    @staticmethod
    def list_nodes(db: Session) -> list[Node]:
        return db.query(Node).order_by(Node.id.asc()).all()

    @staticmethod
    def upsert_from_register(db: Session, message: RegisterMessage) -> Node:
        user = AuthService.get_user_from_token(db, message.token)
        if user is None:
            raise ValueError("유효하지 않은 토큰입니다.")

        node = (
            db.query(Node)
            .filter(Node.machine_fingerprint_hash == message.machine_fingerprint_hash)
            .first()
        )

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if node is None:
            node = Node(
                owner_user_id=user.id,
                node_name=message.node_name,
                host=message.host,
                machine_fingerprint_hash=message.machine_fingerprint_hash,
                node_group=message.node_group,
                status="online",
                cpu_cores=message.spec.cpu_cores,
                ram_mb=message.spec.ram_mb,
                gpu_count=message.spec.gpu_count,
                gpu_info_json=message.spec.gpu_info,
                os_info=message.spec.os_info,
                arch=message.spec.arch,
                last_seen_at=now,
                is_active=True,
            )
            db.add(node)
        else:
            node.owner_user_id = user.id
            node.node_name = message.node_name
            node.host = message.host
            node.node_group = message.node_group
            node.status = "online"
            node.cpu_cores = message.spec.cpu_cores
            node.ram_mb = message.spec.ram_mb
            node.gpu_count = message.spec.gpu_count
            node.gpu_info_json = message.spec.gpu_info
            node.os_info = message.spec.os_info
            node.arch = message.spec.arch
            node.last_seen_at = now
            node.is_active = True

        db.commit()
        db.refresh(node)
        return node

    @staticmethod
    def mark_heartbeat(db: Session, node: Node) -> Node:
        node.status = "online"
        node.last_seen_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
        db.refresh(node)
        return node

    @staticmethod
    def mark_offline(db: Session, node: Node) -> Node:
        node.status = "offline"
        node.last_seen_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
        db.refresh(node)
        return node