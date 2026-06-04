"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from ether_ocr.api.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns service health status and version.",
)
async def health_check() -> HealthResponse:
    """Verify the API is running and responsive."""
    return HealthResponse()
