from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.user import User
from app.schemas.auth import UserCreateRequest


class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        # 지금은 최소 버전. 운영용으로는 bcrypt/passlib 권장
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def create_user(db: Session, payload: UserCreateRequest) -> User:
        existing_username = db.query(User).filter(User.username == payload.username).first()
        if existing_username is not None:
            raise ValueError("이미 존재하는 username입니다.")

        existing_email = db.query(User).filter(User.email == payload.email).first()
        if existing_email is not None:
            raise ValueError("이미 존재하는 email입니다.")

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        user = User(
            username=payload.username,
            email=payload.email,
            password_hash=UserService.hash_password(payload.password),
            is_active=True,
            is_admin=False,
            created_at=now,
            updated_at=now,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()