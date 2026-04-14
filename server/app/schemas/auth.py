from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenCreateRequest(BaseModel):
    user_id: int
    token_name: str = Field(min_length=1, max_length=100)
    expires_at: datetime | None = None


class TokenCreateResponse(BaseModel):
    token_id: int
    token_name: str
    plain_token: str
    created_at: datetime
    expires_at: datetime | None = None


class TokenResponse(BaseModel):
    id: int
    user_id: int
    token_name: str
    is_revoked: bool
    created_at: datetime
    expires_at: datetime | None = None
    last_used_at: datetime | None = None

    class Config:
        from_attributes = True