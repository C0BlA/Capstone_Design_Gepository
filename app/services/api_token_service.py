from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.api_token import ApiToken
from app.db.models.user import User
from app.services.token_service import TokenService


class ApiTokenService:
    @staticmethod
    def create_token(
        db: Session,
        *,
        user_id: int,
        token_name: str,
        expires_at: datetime | None = None,
    ) -> tuple[ApiToken, str]:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise ValueError("존재하지 않는 사용자입니다.")

        plain_token, token_hash = TokenService.generate_token_pair()

        api_token = ApiToken(
            user_id=user_id,
            token_name=token_name,
            token_hash=token_hash,
            is_revoked=False,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            expires_at=expires_at,
            last_used_at=None,
        )

        db.add(api_token)
        db.commit()
        db.refresh(api_token)

        return api_token, plain_token

    @staticmethod
    def list_tokens_by_user(db: Session, user_id: int) -> list[ApiToken]:
        return (
            db.query(ApiToken)
            .filter(ApiToken.user_id == user_id)
            .order_by(ApiToken.id.desc())
            .all()
        )

    @staticmethod
    def revoke_token(db: Session, token_id: int) -> ApiToken | None:
        token = db.query(ApiToken).filter(ApiToken.id == token_id).first()
        if token is None:
            return None

        token.is_revoked = True
        db.commit()
        db.refresh(token)
        return token