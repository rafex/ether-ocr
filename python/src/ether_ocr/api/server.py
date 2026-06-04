"""FastAPI application factory and uvicorn entry point."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ether_ocr.api.routes.health import router as health_router

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Uses the app factory pattern so tests can create fresh instances
    without starting a real server.
    """
    app = FastAPI(
        title="ether-ocr",
        description="OCR engine and document preparation API for RAG ingestion.",
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ──────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────
    app.include_router(health_router, prefix=API_PREFIX)

    return app


def main() -> None:
    """Entry point for uvicorn server.

    Usage:
        python -m ether_ocr.api.server
        ether-ocr-api
        uvicorn ether_ocr.api.server:create_app --factory
    """
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "").lower() in ("1", "true", "yes")

    uvicorn.run(
        "ether_ocr.api.server:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


if __name__ == "__main__":
    main()
