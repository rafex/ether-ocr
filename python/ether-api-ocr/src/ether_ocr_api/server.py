"""FastAPI application factory and uvicorn entry point."""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from ether_ocr_api.routes.health import router as health_router
from ether_ocr_api.routes.ocr import router as ocr_router
from ether_ocr_api.routes.prepare import router as prepare_router
from ether_ocr_api.config import Settings, get_settings

API_PREFIX = "/api/v1"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory rate limiter per client IP."""

    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self._settings = settings
        self._clients: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        settings = self._settings
        if not settings.rate_limit_enabled:
            return await call_next(request)

        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window_start = now - settings.rate_limit_window_seconds
        self._clients[client_ip] = [
            t for t in self._clients[client_ip] if t > window_start
        ]
        self._clients[client_ip].append(now)

        if len(self._clients[client_ip]) > settings.rate_limit_requests:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        return await call_next(request)


class MaxUploadSizeMiddleware(BaseHTTPMiddleware):
    """Reject requests with body exceeding configured max upload size."""

    def __init__(self, app, max_bytes: int):
        super().__init__(app)
        self._max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self._max_bytes:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "detail": f"Upload too large. Maximum is {self._max_bytes // (1024 * 1024)} MB."
                },
            )
        return await call_next(request)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    cfg = settings or get_settings()

    app = FastAPI(
        title="ether-ocr",
        description="OCR engine and document preparation API for RAG ingestion.",
        version="0.3.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(MaxUploadSizeMiddleware, max_bytes=cfg.max_upload_bytes)
    app.add_middleware(RateLimitMiddleware, settings=cfg)

    app.include_router(health_router, prefix=API_PREFIX)
    app.include_router(ocr_router, prefix=API_PREFIX)
    app.include_router(prepare_router, prefix=API_PREFIX)

    return app


def main() -> None:
    """Entry point for uvicorn server."""
    import uvicorn

    cfg = get_settings()

    uvicorn.run(
        "ether_ocr_api.server:create_app",
        host=cfg.host,
        port=cfg.port,
        reload=cfg.reload,
        factory=True,
    )


if __name__ == "__main__":
    main()
