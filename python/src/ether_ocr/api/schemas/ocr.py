"""Schemas for OCR endpoint request/response."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OcrMetadata(BaseModel):
    """Metadata about the OCR/extraction process."""

    pages: int = Field(description="Number of pages processed")
    paragraphs: int = Field(description="Number of paragraphs in output")
    size_bytes: int = Field(description="Size of output text in bytes")
    ocr_used: bool = Field(description="Whether OCR was applied (vs direct text extraction)")
    method: str = Field(description="Method used: 'poppler', 'tesseract', or 'passthrough'")
    language: str = Field(default="spa+eng", description="Language(s) used for OCR")
    dpi: int = Field(default=300, description="DPI used for PDF-to-image conversion")


class OcrResponse(BaseModel):
    """Response for POST /api/v1/ocr."""

    status: str = Field(default="ok", description="Request status")
    text: str = Field(description="Extracted and cleaned UTF-8 text")
    metadata: OcrMetadata = Field(description="Processing metadata")

    model_config = {"json_schema_extra": {
        "example": {
            "status": "ok",
            "text": "Artículo 1. Todo individuo tiene derecho...",
            "metadata": {
                "pages": 3,
                "paragraphs": 42,
                "size_bytes": 12345,
                "ocr_used": True,
                "method": "tesseract",
                "language": "spa+eng",
                "dpi": 300,
            },
        },
    }}


class OcrLargeResponse(BaseModel):
    """Response when text exceeds inline size limit — returns a download URL."""

    status: str = Field(default="ok", description="Request status")
    text_size_bytes: int = Field(description="Total size of extracted text in bytes")
    download_url: str = Field(description="URL to download the compressed text")
    metadata: OcrMetadata = Field(description="Processing metadata")
