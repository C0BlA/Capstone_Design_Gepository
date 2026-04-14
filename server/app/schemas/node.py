from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class NodeBase(BaseModel):
    owner_user_id: int | None = None
    node_name: str = Field(..., min_length=1, max_length=100)
    host: str | None = None
    machine_fingerprint_hash: str = Field(..., min_length=16, max_length=128) # 멕 주소 해시 값
    node_group: str | None = Field(default=None, max_length=50)
    cpu_cores: int = Field(default=0, ge=0)
    ram_mb: int = Field(default=0, ge=0)
    gpu_count: int = Field(default=0, ge=0)
    gpu_info: list[dict[str, Any]] | None = None
    os_info: str | None = None
    arch: str | None = None
    is_active: bool = True


class NodeCreate(NodeBase):
    pass


class NodeUpdate(BaseModel):
    node_name: str | None = Field(default=None, min_length=1, max_length=100)
    host: str | None = None
    node_group: str | None = Field(default=None, max_length=50)
    status: str | None = None
    cpu_cores: int | None = Field(default=None, ge=0)
    ram_mb: int | None = Field(default=None, ge=0)
    gpu_count: int | None = Field(default=None, ge=0)
    gpu_info: list[dict[str, Any]] | None = None
    os_info: str | None = None
    arch: str | None = None
    is_active: bool | None = None


class NodeResponse(BaseModel):
    id: int
    owner_user_id: int | None
    node_name: str
    host: str | None
    machine_fingerprint_hash: str
    node_group: str | None
    status: str
    cpu_cores: int
    ram_mb: int
    gpu_count: int
    gpu_info: list[dict[str, Any]] | None = None
    os_info: str | None
    arch: str | None
    is_active: bool
    last_seen_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
