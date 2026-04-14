from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class NodeSpec(BaseModel):
    cpu_cores: int = 0
    ram_mb: int = 0
    gpu_count: int = 0
    gpu_info: list[dict[str, Any]] | None = None
    os_info: str | None = None
    arch: str | None = None


class RegisterMessage(BaseModel):
    type: Literal["register"]
    owner_user_id: int | None = None
    node_name: str
    host: str | None = None
    machine_fingerprint_hash: str = Field(..., min_length=16, max_length=128)
    node_group: str | None = None
    spec: NodeSpec


class HeartbeatResource(BaseModel):
    cpu_usage: float | None = None
    ram_usage_mb: int | None = None
    gpu_usage: list[dict[str, Any]] | list[Any] = Field(default_factory=list)


class HeartbeatMessage(BaseModel):
    type: Literal["heartbeat"]
    timestamp: datetime
    resource: HeartbeatResource | None = None
