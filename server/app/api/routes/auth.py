from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.auth import (
    TokenCreateRequest,
    TokenCreateResponse,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
)
from app.services.api_token_service import ApiTokenService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(payload: UserCreateRequest, db: Session = Depends(get_db)):
    try:
        user = UserService.create_user(db, payload)
        return user
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/tokens",
    response_model=TokenCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_token(payload: TokenCreateRequest, db: Session = Depends(get_db)):
    try:
        token, plain_token = ApiTokenService.create_token(
            db,
            user_id=payload.user_id,
            token_name=payload.token_name,
            expires_at=payload.expires_at,
        )
        return TokenCreateResponse(
            token_id=token.id,
            token_name=token.token_name,
            plain_token=plain_token,
            created_at=token.created_at,
            expires_at=token.expires_at,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/users/{user_id}/tokens",
    response_model=list[TokenResponse],
)
def list_user_tokens(user_id: int, db: Session = Depends(get_db)):
    return ApiTokenService.list_tokens_by_user(db, user_id)


@router.post(
    "/tokens/{token_id}/revoke",
    response_model=TokenResponse,
)
def revoke_token(token_id: int, db: Session = Depends(get_db)):
    token = ApiTokenService.revoke_token(db, token_id)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="토큰을 찾을 수 없습니다.",
        )
    return token