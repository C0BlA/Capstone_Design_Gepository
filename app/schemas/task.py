from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    requester_user_id: int | None = None
    prompt: str = Field(..., min_length=1)
    assignment_mode: str = Field(default="manual")
    selected_node_id: int | None = None


class TaskResponse(BaseModel):
    id: int
    requester_user_id: int | None
    prompt: str
    status: str
    assignment_mode: str
    selected_node_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
