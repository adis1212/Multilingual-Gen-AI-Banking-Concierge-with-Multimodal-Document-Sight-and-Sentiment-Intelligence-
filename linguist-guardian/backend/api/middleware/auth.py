from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM  = "HS256"

security = HTTPBearer(auto_error=False)


async def verify_token(request: Request, call_next):
    """
    Simple JWT middleware.
    For hackathon — skips auth on /health and /api/session/create.
    """
    OPEN_PATHS = ["/health", "/docs", "/openapi.json", "/api/session/create"]

    if any(request.url.path.startswith(p) for p in OPEN_PATHS):
        return await call_next(request)

    # For hackathon demo, skip strict auth
    # In production: validate Bearer token here
    return await call_next(request)


def create_token(staff_id: str, branch_id: str) -> str:
    payload = {"sub": staff_id, "branch": branch_id}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Invalid token")