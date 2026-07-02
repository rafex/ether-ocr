"""Authentication module — API key and JWT validation."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from ether_ocr_api.config import get_settings

security = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    """Context passed to route handlers after successful authentication."""

    method: str
    key_id: str = ""


def _verify_jwt(token: str, secret: str) -> AuthContext | None:
    """Verify a JWT token using HS256. Returns AuthContext if valid."""
    if not secret:
        return None
    try:
        import jwt as pyjwt

        payload = pyjwt.decode(token, secret, algorithms=["HS256"])
        sub = payload.get("sub", "unknown")
        key_id = sub[:8] if isinstance(sub, str) else str(sub)[:8]
        return AuthContext(method="jwt", key_id=key_id)
    except Exception:
        return None


async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthContext:
    """FastAPI dependency that requires authentication."""
    cfg = get_settings()

    if not cfg.auth_enabled:
        return AuthContext(method="none")

    api_key = request.headers.get("X-API-Key")
    if api_key:
        if cfg.verify_api_key(api_key):
            return AuthContext(method="api_key", key_id=api_key[:8])
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if credentials and credentials.credentials:
        ctx = _verify_jwt(credentials.credentials, cfg.jwt_secret)
        if ctx:
            return ctx
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired JWT token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide X-API-Key header or Bearer token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
