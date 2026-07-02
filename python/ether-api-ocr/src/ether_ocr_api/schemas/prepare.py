"""Schemas for prepare and validate endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PrepareMetadata(BaseModel):
    """Metadata about the preparation process."""

    paragraphs: int = Field(description="Number of paragraphs in output")
    size_bytes: int = Field(description="Size of output text in bytes")
    method: str = Field(description="Method used: 'poppler' or 'passthrough'")


class PrepareResponse(BaseModel):
    """Response for POST /api/v1/prepare."""

    status: str = Field(default="ok")
    text: str = Field(description="Cleaned and validated UTF-8 text")
    metadata: PrepareMetadata


class ValidationIssue(BaseModel):
    """A single validation issue found in the text."""

    description: str = Field(description="Human-readable description of the issue")


class ValidateResponse(BaseModel):
    """Response for POST /api/v1/validate."""

    status: str = Field(default="ok")
    valid: bool = Field(description="Whether the text passes RAG validation")
    issues: list[ValidationIssue] = Field(
        default_factory=list,
        description="List of issues found (empty if valid=True)",
    )
