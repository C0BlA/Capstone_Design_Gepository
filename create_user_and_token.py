from __future__ import annotations

from datetime import datetime

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.api_token import ApiToken
from app.services.token_service import TokenService


def main() -> None:
    db = SessionLocal()
    try:
        username = "admin"
        email = "admin@example.com"
        password_hash = "temporary-password-hash"

        user = db.query(User).filter(User.username == username).first()
        if user is None:
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                is_active=True,
                is_admin=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        plain_token, token_hash = TokenService.generate_token_pair()

        api_token = ApiToken(
            user_id=user.id,
            token_name="default-node-token",
            token_hash=token_hash,
            is_revoked=False,
            created_at=datetime.utcnow(),
        )
        db.add(api_token)
        db.commit()

        print("user_id:", user.id)
        print("token:", plain_token)
        print("이 토큰은 다시 DB에서 원문으로 볼 수 없습니다. 잘 저장하세요.")
    finally:
        db.close()


if __name__ == "__main__":
    main()