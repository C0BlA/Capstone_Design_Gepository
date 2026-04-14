from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.api_token import ApiToken
from app.db.models.user import User


class AuthService:
    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def validate_api_token(db: Session, plain_token: str) -> ApiToken | None:
        token_hash = AuthService.hash_token(plain_token)

        api_token = (
            db.query(ApiToken)
            .filter(ApiToken.token_hash == token_hash)
            .filter(ApiToken.is_revoked.is_(False))
            .first()
        )

        if api_token is None:
            return None

        if api_token.expires_at is not None:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            if api_token.expires_at < now:
                return None

        user = db.query(User).filter(User.id == api_token.user_id).first()
        if user is None or not user.is_active:
            return None

        api_token.last_used_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
        db.refresh(api_token)

        return api_token

    @staticmethod
    def get_user_from_token(db: Session, plain_token: str) -> User | None:
        api_token = AuthService.validate_api_token(db, plain_token)
        if api_token is None:
            return None

        return db.query(User).filter(User.id == api_token.user_id).first()