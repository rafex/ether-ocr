"""Centralized configuration loaded from environment variables."""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass, field

_MAX_UPLOAD_BYTES = 50 * 1024 * 1024
_MAX_INLINE_TEXT_BYTES = 100 * 1024
_RATE_LIMIT_REQUESTS = 30
_RATE_LIMIT_WINDOW_SECONDS = 60


@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded from environment at startup."""

    auth_enabled: bool = True
    api_key_hashes: frozenset[str] = field(default_factory=frozenset)
    jwt_secret: str = ""

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:8000"])

    ocr_default_lang: str = "spa+eng"
    ocr_default_dpi: int = 300
    max_inline_text_bytes: int = _MAX_INLINE_TEXT_BYTES
    max_upload_bytes: int = _MAX_UPLOAD_BYTES

    rate_limit_enabled: bool = True
    rate_limit_requests: int = _RATE_LIMIT_REQUESTS
    rate_limit_window_seconds: int = _RATE_LIMIT_WINDOW_SECONDS

    def verify_api_key(self, key: str) -> bool:
        """Constant-time comparison of an API key against configured hashes."""
        if not self.api_key_hashes:
            return False
        key_hash = hash_api_key(key)
        return any(
            hmac.compare_digest(key_hash, stored) for stored in self.api_key_hashes
        )

    @staticmethod
    def from_env() -> Settings:
        """Build Settings from environment variables (loaded once at startup)."""
        return Settings(
            auth_enabled=_bool_env("AUTH_ENABLED", default=True),
            api_key_hashes=_load_api_key_hashes(),
            jwt_secret=os.getenv("JWT_SECRET", ""),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            reload=_bool_env("RELOAD", default=False),
            cors_origins=_load_cors_origins(),
            ocr_default_lang=os.getenv("OCR_DEFAULT_LANG", "spa+eng"),
            ocr_default_dpi=int(os.getenv("OCR_DEFAULT_DPI", "300")),
            max_inline_text_bytes=int(
                os.getenv("OCR_MAX_INLINE_BYTES", str(_MAX_INLINE_TEXT_BYTES))
            ),
            max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", str(_MAX_UPLOAD_BYTES))),
            rate_limit_enabled=_bool_env("RATE_LIMIT_ENABLED", default=True),
            rate_limit_requests=int(
                os.getenv("RATE_LIMIT_REQUESTS", str(_RATE_LIMIT_REQUESTS))
            ),
            rate_limit_window_seconds=int(
                os.getenv("RATE_LIMIT_WINDOW_SECONDS", str(_RATE_LIMIT_WINDOW_SECONDS))
            ),
        )


def hash_api_key(key: str) -> str:
    """Hash an API key with SHA-256 for secure storage/comparison."""
    return hashlib.sha256(key.encode()).hexdigest()


def _load_api_key_hashes() -> frozenset[str]:
    raw = os.getenv("API_KEYS", "")
    if not raw.strip():
        return frozenset()
    return frozenset(hash_api_key(k.strip()) for k in raw.split(",") if k.strip())


def _load_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:8000")
    if raw.strip() == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


def _bool_env(name: str, *, default: bool = False) -> bool:
    val = os.getenv(name, str(default).lower())
    return val.lower() not in ("0", "false", "no", "")


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the singleton Settings instance. Builds it on first call."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def override_settings(s: Settings) -> None:
    """Override the singleton (for tests)."""
    global _settings
    _settings = s
