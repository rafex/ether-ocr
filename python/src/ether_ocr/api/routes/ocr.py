"""OCR endpoint — POST /api/v1/ocr."""

from __future__ import annotations

import io
import tarfile
import tempfile
from pathlib import Path

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from starlette import status

from ether_ocr.api.auth import AuthContext, require_auth
from ether_ocr.api.schemas.ocr import (
    BatchFileResult,
    BatchOcrResponse,
    OcrMetadata,
    OcrResponse,
)
from ether_ocr.pipeline import ocr_document

router = APIRouter(tags=["ocr"])

# If text exceeds this size, return compressed tar.gz instead of inline
MAX_INLINE_BYTES = 100 * 1024  # 100 KB

# Allowed MIME types
ALLOWED_MIMES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/tiff",
    "text/plain",
}
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".txt"}


def _validate_file(upload: UploadFile) -> None:
    """Validate uploaded file type and extension."""
    if upload.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )
    ext = Path(upload.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file extension: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    if upload.content_type and upload.content_type not in ALLOWED_MIMES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported MIME type: {upload.content_type}",
        )


def _build_tar_gz(text: str, metadata: OcrMetadata, filename: str) -> io.BytesIO:
    """Create an in-memory tar.gz with text and metadata JSON."""
    import json

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        # Text file
        text_bytes = text.encode("utf-8")
        text_info = tarfile.TarInfo(name=f"{filename}.txt")
        text_info.size = len(text_bytes)
        tar.addfile(text_info, io.BytesIO(text_bytes))

        # Metadata JSON
        meta_bytes = json.dumps(metadata.model_dump(), indent=2).encode("utf-8")
        meta_info = tarfile.TarInfo(name=f"{filename}.metadata.json")
        meta_info.size = len(meta_bytes)
        tar.addfile(meta_info, io.BytesIO(meta_bytes))

    buf.seek(0)
    return buf


async def _process_single_file(
    file: UploadFile,
    lang: str,
    dpi: int,
    validate: bool,
    force_image: bool,
) -> OcrResponse:
    """Process a single file through the OCR pipeline."""
    _validate_file(file)

    suffix = Path(file.filename or "upload").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_input:
        content = await file.read()
        tmp_input.write(content)
        input_path = Path(tmp_input.name)

    try:
        result = ocr_document(
            input_path=input_path,
            output_path=input_path.with_suffix(".txt"),
            force_image=force_image,
            lang=lang,
            dpi=dpi,
            validate=validate,
        )

        metadata = OcrMetadata(
            pages=result.pages,
            paragraphs=result.paragraphs,
            size_bytes=result.size_bytes,
            ocr_used=result.used_ocr,
            method="tesseract" if result.used_ocr else "poppler",
            language=lang,
            dpi=dpi,
        )

        text = result.output_path.read_text(encoding="utf-8")
        result.output_path.unlink(missing_ok=True)

        return OcrResponse(status="ok", text=text, metadata=metadata)

    finally:
        input_path.unlink(missing_ok=True)


@router.post(
    "/ocr",
    summary="Extract text from a document using OCR or direct extraction",
    description=(
        "Upload a PDF (with or without text layer) or image file. "
        "Returns cleaned UTF-8 text with metadata. "
        "For texts larger than 100 KB, returns a tar.gz archive."
    ),
    responses={
        200: {"description": "Text extracted successfully (JSON or tar.gz)"},
        400: {"description": "Invalid request"},
        401: {"description": "Authentication required"},
        415: {"description": "Unsupported file format"},
        422: {"description": "Text failed RAG validation"},
    },
)
async def ocr_endpoint(
    file: UploadFile = File(..., description="PDF or image file to process"),
    lang: str = Form(default="spa+eng"),
    dpi: int = Form(default=300, ge=72, le=600),
    validate: bool = Form(default=True),
    force_image: bool = Form(default=False),
    auth: AuthContext = Depends(require_auth),
):
    """Process a single document through the OCR pipeline."""
    try:
        single = await _process_single_file(file, lang, dpi, validate, force_image)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    # ── Large text: return tar.gz ─────────────────────
    if single.metadata.size_bytes > MAX_INLINE_BYTES:
        stem = Path(file.filename or "output").stem
        tar_buf = _build_tar_gz(single.text, single.metadata, stem)
        return StreamingResponse(
            tar_buf,
            media_type="application/gzip",
            headers={"Content-Disposition": f'attachment; filename="{stem}.tar.gz"'},
        )

    return single


@router.post(
    "/ocr/batch",
    response_model=BatchOcrResponse,
    summary="Batch OCR — process multiple files at once",
    description="Upload multiple files and process them through the OCR pipeline.",
)
async def ocr_batch_endpoint(
    files: List[UploadFile] = File(..., description="Multiple files to process"),
    lang: str = Form(default="spa+eng"),
    dpi: int = Form(default=300, ge=72, le=600),
    validate: bool = Form(default=True),
    force_image: bool = Form(default=False),
    auth: AuthContext = Depends(require_auth),
) -> BatchOcrResponse:
    """Process multiple documents through the OCR pipeline."""
    results: list[BatchFileResult] = []
    successful = 0
    failed = 0

    for batch_file in files:
        try:
            single = await _process_single_file(batch_file, lang, dpi, validate, force_image)
            results.append(BatchFileResult(
                filename=batch_file.filename or "unknown",
                status="ok",
                text=single.text,
                metadata=single.metadata,
            ))
            successful += 1
        except HTTPException:
            raise
        except Exception as exc:
            results.append(BatchFileResult(
                filename=batch_file.filename or "unknown",
                status="error",
                error=str(exc),
            ))
            failed += 1

    return BatchOcrResponse(
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results,
    )
