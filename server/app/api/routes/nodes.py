import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.node import NodeCreate, NodeResponse, NodeUpdate
from app.services.node_service import NodeService

router = APIRouter(prefix="/nodes", tags=["nodes"])


def to_response(node) -> NodeResponse:
    return NodeResponse(
        id=node.id,
        owner_user_id=node.owner_user_id,
        node_name=node.node_name,
        host=node.host,
        machine_fingerprint_hash=node.machine_fingerprint_hash,
        node_group=node.node_group,
        status=node.status,
        cpu_cores=node.cpu_cores,
        ram_mb=node.ram_mb,
        gpu_count=node.gpu_count,
        gpu_info=json.loads(node.gpu_info_json or "[]"),
        os_info=node.os_info,
        arch=node.arch,
        is_active=node.is_active,
        last_seen_at=node.last_seen_at,
        created_at=node.created_at,
        updated_at=node.updated_at,
    )


@router.post("", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(payload: NodeCreate, db: Session = Depends(get_db)):
    existing = NodeService.get_by_fingerprint(db, payload.machine_fingerprint_hash)
    if existing is not None:
        raise HTTPException(status_code=409, detail="이미 등록된 machine_fingerprint_hash입니다.")
    node = NodeService.create_node(db, payload)
    return to_response(node)


@router.get("", response_model=list[NodeResponse])
def list_nodes(db: Session = Depends(get_db)):
    return [to_response(node) for node in NodeService.list_nodes(db)]


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(node_id: int, db: Session = Depends(get_db)):
    node = NodeService.get_node(db, node_id)
    if node is None:
        raise HTTPException(status_code=404, detail="노드를 찾을 수 없습니다.")
    return to_response(node)


@router.patch("/{node_id}", response_model=NodeResponse)
def update_node(node_id: int, payload: NodeUpdate, db: Session = Depends(get_db)):
    node = NodeService.get_node(db, node_id)
    if node is None:
        raise HTTPException(status_code=404, detail="노드를 찾을 수 없습니다.")
    node = NodeService.update_node(db, node, payload)
    return to_response(node)
