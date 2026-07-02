"""Prepare and validate endpoints."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from starlette import status

from ether_ocr_api.auth import AuthContext, require_auth
from ether_ocr_api.schemas.prepare import (
    PrepareMetadata,
    PrepareResponse,
    ValidateResponse,
    ValidationIssue,
)
from ether_ocr_core.preparer import prepare_document
from ether_ocr_core.validator import validate_plain_text

router = APIRouter(tags=["prepare"])

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def _validate_file(upload: UploadFile) -> None:
    if upload.filename is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Filename is required")
    ext = Path(upload.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported extension: {ext}. Allowed: .pdf, .txt",
        )


@router.post(
    "/prepare",
    response_model=PrepareResponse,
    summary="Prepare a document as clean UTF-8 text",
)
async def prepare_endpoint(
    file: UploadFile = File(..., description="PDF or UTF-8 text file"),
    skip_validation: bool = Form(default=False, alias="skip-validation"),
    pdftotext_bin: str = Form(default="pdftotext", alias="pdftotext-bin"),
    auth: AuthContext = Depends(require_auth),
) -> PrepareResponse:
    _validate_file(file)

    suffix = Path(file.filename or "upload").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_input:
        content = await file.read()
        tmp_input.write(content)
        input_path = Path(tmp_input.name)

    try:
        result = prepare_document(
            input_path=input_path,
            output_path=input_path.with_suffix(".txt"),
            validate=not skip_validation,
            pdftotext_bin=pdftotext_bin,
        )

        text = result.output_path.read_text(encoding="utf-8")
        result.output_path.unlink(missing_ok=True)

        return PrepareResponse(
            status="ok",
            text=text,
            metadata=PrepareMetadata(
                paragraphs=result.paragraphs,
                size_bytes=result.size_bytes,
                method="poppler" if input_path.suffix.lower() == ".pdf" else "passthrough",
            ),
        )

    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    finally:
        input_path.unlink(missing_ok=True)


@router.post(
    "/validate",
    response_model=ValidateResponse,
    summary="Validate text for RAG compatibility",
)
async def validate_endpoint(
    file: UploadFile = File(..., description="UTF-8 text file to validate"),
    auth: AuthContext = Depends(require_auth),
) -> ValidateResponse:
    if file.filename is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Filename is required")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File must be UTF-8 encoded")

    validation = validate_plain_text(text)

    return ValidateResponse(
        status="ok",
        valid=validation.valid,
        issues=[ValidationIssue(description=issue) for issue in validation.issues],
    )
