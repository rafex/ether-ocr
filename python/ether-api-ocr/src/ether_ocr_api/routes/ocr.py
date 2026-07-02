"""OCR endpoint — POST /api/v1/ocr."""

from __future__ import annotations

import io
import json
import tarfile
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from starlette import status

from ether_ocr_api.auth import AuthContext, require_auth
from ether_ocr_api.config import get_settings
from ether_ocr_api.schemas.ocr import (
    BatchFileResult,
    BatchOcrResponse,
    OcrMetadata,
    OcrResponse,
)
from ether_ocr_core.pipeline import ocr_document

router = APIRouter(tags=["ocr"])

_ALLOWED_EXTENSIONS: frozenset[str] = frozenset(
    {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".txt"}
)
_ALLOWED_MIMES: frozenset[str] = frozenset(
    {"application/pdf", "image/png", "image/jpeg", "image/tiff", "text/plain"}
)


def _validate_file(upload: UploadFile) -> None:
    if upload.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )
    ext = Path(upload.filename).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file extension: {ext}. "
                f"Allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}"
            ),
        )
    if upload.content_type and upload.content_type not in _ALLOWED_MIMES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported MIME type: {upload.content_type}",
        )


def _write_upload_to_temp(upload: UploadFile) -> Path:
    suffix = Path(upload.filename or "upload").suffix
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp.write(upload.file.read())
    tmp.close()
    return Path(tmp.name)


def _build_tar_gz(text: str, metadata: OcrMetadata, stem: str) -> io.BytesIO:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, content in [(f"{stem}.txt", text), (f"{stem}.metadata.json", json.dumps(metadata.model_dump(), indent=2))]:
            data = content.encode("utf-8")
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    buf.seek(0)
    return buf


def _run_ocr_pipeline(
    input_path: Path,
    *,
    lang: str,
    dpi: int,
    validate: bool,
    force_image: bool,
) -> OcrResponse:
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


async def _process_single_file(
    file: UploadFile,
    lang: str,
    dpi: int,
    validate: bool,
    force_image: bool,
) -> OcrResponse:
    _validate_file(file)
    input_path = _write_upload_to_temp(file)
    try:
        return _run_ocr_pipeline(
            input_path, lang=lang, dpi=dpi, validate=validate, force_image=force_image
        )
    finally:
        input_path.unlink(missing_ok=True)


def _maybe_stream_response(
    single: OcrResponse, filename: str | None
) -> OcrResponse | StreamingResponse:
    cfg = get_settings()
    if single.metadata.size_bytes <= cfg.max_inline_text_bytes:
        return single
    stem = Path(filename or "output").stem
    tar_buf = _build_tar_gz(single.text, single.metadata, stem)
    return StreamingResponse(
        tar_buf,
        media_type="application/gzip",
        headers={"Content-Disposition": f'attachment; filename="{stem}.tar.gz"'},
    )


@router.post(
    "/ocr",
    summary="Extract text from a document using OCR or direct extraction",
)
async def ocr_endpoint(
    file: UploadFile = File(..., description="PDF or image file to process"),
    lang: str = Form(default="spa+eng"),
    dpi: int = Form(default=300, ge=72, le=600),
    validate: bool = Form(default=True),
    force_image: bool = Form(default=False),
    auth: AuthContext = Depends(require_auth),
):
    try:
        single = await _process_single_file(file, lang, dpi, validate, force_image)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    return _maybe_stream_response(single, file.filename)


@router.post(
    "/ocr/batch",
    response_model=BatchOcrResponse,
    summary="Batch OCR — process multiple files at once",
)
async def ocr_batch_endpoint(
    files: list[UploadFile] = File(..., description="Multiple files to process"),
    lang: str = Form(default="spa+eng"),
    dpi: int = Form(default=300, ge=72, le=600),
    validate: bool = Form(default=True),
    force_image: bool = Form(default=False),
    auth: AuthContext = Depends(require_auth),
) -> BatchOcrResponse:
    results: list[BatchFileResult] = []
    successful = 0
    failed = 0

    for batch_file in files:
        try:
            single = await _process_single_file(
                batch_file, lang, dpi, validate, force_image
            )
            results.append(
                BatchFileResult(
                    filename=batch_file.filename or "unknown",
                    status="ok",
                    text=single.text,
                    metadata=single.metadata,
                )
            )
            successful += 1
        except HTTPException:
            raise
        except Exception as exc:
            results.append(
                BatchFileResult(
                    filename=batch_file.filename or "unknown",
                    status="error",
                    error=str(exc),
                )
            )
            failed += 1

    return BatchOcrResponse(
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results,
    )
