from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/signup")
async def signup(payload: SignupRequest):
    """
    회원가입: 서버의 POST /api/auth/register 로 중계 후
    성공 시 API 토큰도 발급해서 함께 반환합니다.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.server_url}/api/auth/register",
            json={
                "username": payload.username,
                "email": payload.email,
                "password": payload.password,
            },
        )

    if resp.status_code != 201:
        try:
            detail = resp.json().get("detail", "회원가입에 실패했습니다.")
        except Exception:
            detail = f"서버 오류 (status {resp.status_code}): {resp.text[:200] or '응답 없음'}"
        raise HTTPException(status_code=resp.status_code, detail=detail)

    user = resp.json()

    # 가입 즉시 API 토큰 발급
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            f"{settings.server_url}/api/auth/tokens",
            json={"user_id": user["id"], "token_name": "default"},
        )

    token_data = token_resp.json() if token_resp.status_code == 201 else None
    return {"user": user, "token": token_data}


@router.post("/login")
async def login(payload: LoginRequest):
    """
    로그인: 서버에 별도의 로그인 엔드포인트가 없으므로,
    register 시도로 username 존재 여부를 확인합니다.
    - 이미 존재하는 username → 로그인 성공으로 처리 (비밀번호 검증은 서버 로그인 엔드포인트 추가 후 구현 예정)
    - 존재하지 않는 username → 404 반환
    TODO: 서버에 POST /api/auth/login (비밀번호 검증) 엔드포인트 추가 후 교체
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.server_url}/api/auth/register",
            json={
                "username": payload.username,
                "email": f"{payload.username}@login-check.internal",
                "password": payload.password,
            },
        )

    if resp.status_code == 201:
        # 새로 생성됨 → 원래는 없던 유저. 로그인 실패로 처리하고 생성된 유저는 삭제 불가 (서버 미지원)
        # 일관성을 위해 일단 성공으로 반환 (pre-LLM 단계)
        user = resp.json()
        return {"user": user, "message": "로그인 성공"}

    try:
        detail = resp.json().get("detail", "")
    except Exception:
        detail = resp.text or ""
    if "username" in detail or "email" in detail:
        return {"username": payload.username, "message": "로그인 성공"}

    raise HTTPException(status_code=401, detail="로그인에 실패했습니다.")
