"""Authentication module — API key and JWT validation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

security = HTTPBearer(auto_error=False)

# Load from environment with sensible defaults for development
API_KEYS: set[str] = set()
JWT_SECRET: str = ""


def _load_config() -> tuple[set[str], str, bool]:
    """Load auth configuration from environment at call time."""
    keys = {
        key.strip()
        for key in os.getenv("API_KEYS", "dev-key-ether-ocr").split(",")
        if key.strip()
    }
    secret = os.getenv("JWT_SECRET", "")
    enabled = os.getenv("AUTH_ENABLED", "1").lower() not in ("0", "false", "no")
    return keys, secret, enabled


@dataclass
class AuthContext:
    """Context passed to route handlers after successful authentication."""

    method: str  # "api_key" or "jwt"
    key_id: Optional[str] = None  # First 8 chars of key hash for API key


def _verify_api_key(api_key: str, valid_keys: set[str]) -> Optional[AuthContext]:
    """Verify an API key against the configured set."""
    if api_key in valid_keys:
        return AuthContext(method="api_key", key_id=api_key[:8])
    return None


def _verify_jwt(token: str, secret: str) -> Optional[AuthContext]:
    """Verify a JWT token. Returns AuthContext if valid, None otherwise.

    For the POC, we verify the JWT signature using HS256 and the configured secret.
    """
    if not secret:
        return None

    try:
        import jwt as pyjwt

        payload = pyjwt.decode(token, secret, algorithms=["HS256"])
        sub = payload.get("sub", "unknown")
        return AuthContext(method="jwt", key_id=sub[:8] if isinstance(sub, str) else str(sub)[:8])
    except Exception:
        return None


async def require_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = None,
) -> AuthContext:
    """FastAPI dependency that requires authentication.

    Checks in order:
    1. X-API-Key header
    2. Authorization: Bearer <token> (JWT)

    If AUTH_ENABLED is false, authentication is skipped (dev mode).
    """
    api_keys, jwt_secret, auth_enabled = _load_config()

    if not auth_enabled:
        return AuthContext(method="none")

    # Check API key header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        ctx = _verify_api_key(api_key, api_keys)
        if ctx:
            return ctx
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # Check JWT Bearer token
    if credentials and credentials.credentials:
        ctx = _verify_jwt(credentials.credentials, jwt_secret)
        if ctx:
            return ctx
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired JWT token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # No credentials provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide X-API-Key header or Bearer token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
