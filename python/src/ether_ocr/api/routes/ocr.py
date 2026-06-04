"""OCR endpoint — POST /api/v1/ocr."""

from __future__ import annotations

import io
import tarfile
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from starlette import status

from ether_ocr.api.auth import AuthContext, require_auth
from ether_ocr.api.schemas.ocr import OcrMetadata, OcrResponse
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


@router.post(
    "/ocr",
    response_model=OcrResponse,
    summary="Extract text from a document using OCR or direct extraction",
    description=(
        "Upload a PDF (with or without text layer) or image file. "
        "The service automatically detects whether to use Poppler (fast, for PDFs "
        "with text layer) or Tesseract OCR (for scanned PDFs and images). "
        "Returns cleaned UTF-8 text with metadata. "
        "For texts larger than 100 KB, returns a tar.gz file instead of inline text."
    ),
    responses={
        200: {"description": "Text extracted successfully"},
        400: {"description": "Invalid request (missing file, bad parameters)"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported file format"},
        422: {"description": "Text failed RAG validation"},
    },
)
async def ocr_endpoint(
    file: UploadFile = File(..., description="PDF or image file to process"),
    lang: str = Form(default="spa+eng", description="Tesseract language(s)"),
    dpi: int = Form(default=300, ge=72, le=600, description="DPI for PDF-to-image conversion"),
    validate: bool = Form(default=True, description="Run RAG compatibility validation"),
    force_image: bool = Form(default=False, description="Force image mode (skip PDF logic)"),
    auth: AuthContext = Depends(require_auth),
) -> OcrResponse:
    """Process an uploaded document through the OCR pipeline."""
    _validate_file(file)

    # Read uploaded file into a temporary location
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

        # Clean up output file (input file cleaned in finally)
        result.output_path.unlink(missing_ok=True)

        return OcrResponse(status="ok", text=text, metadata=metadata)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        # Clean up temporary input file
        input_path.unlink(missing_ok=True)
