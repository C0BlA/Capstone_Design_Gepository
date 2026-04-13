from __future__ import annotations

import hashlib
import secrets


class TokenService:
    @staticmethod
    def generate_plain_token(prefix: str = "gepos") -> str:
        return f"{prefix}_{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_token_pair() -> tuple[str, str]:
        plain = TokenService.generate_plain_token()
        token_hash = TokenService.hash_token(plain)
        return plain, token_hash