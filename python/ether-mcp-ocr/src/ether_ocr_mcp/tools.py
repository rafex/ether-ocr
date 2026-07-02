"""MCP tools — call the ether-ocr REST API via httpx."""

from __future__ import annotations

import base64
import json
import os
import tempfile
from pathlib import Path

import httpx

OCR_API_URL = os.getenv("OCR_API_URL", "http://localhost:8000")
OCR_API_KEY = os.getenv("OCR_API_KEY", "")
TIMEOUT = int(os.getenv("OCR_API_TIMEOUT", "60"))


def _headers() -> dict[str, str]:
    h: dict[str, str] = {}
    if OCR_API_KEY:
        h["X-API-Key"] = OCR_API_KEY
    return h


async def call_health_check() -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{OCR_API_URL}/api/v1/health", headers=_headers())
        r.raise_for_status()
        return json.dumps(r.json(), indent=2)


async def call_ocr_document(
    *,
    file_base64: str,
    filename: str,
    lang: str = "spa+eng",
    dpi: int = 300,
    validate: bool = True,
    force_image: bool = False,
) -> str:
    data = base64.b64decode(file_base64)
    suffix = Path(filename).suffix

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        content_type = "application/pdf" if suffix == ".pdf" else "application/octet-stream"
        files = {"file": (filename, open(tmp_path, "rb"), content_type)}
        form = {
            "lang": lang,
            "dpi": str(dpi),
            "validate": str(validate).lower(),
            "force_image": str(force_image).lower(),
        }
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(
                f"{OCR_API_URL}/api/v1/ocr",
                files=files,
                data=form,
                headers=_headers(),
            )
            r.raise_for_status()
            content_type_resp = r.headers.get("content-type", "")
            if "application/gzip" in content_type_resp:
                return f"Text too large — received tar.gz ({len(r.content)} bytes)"

            return json.dumps(r.json(), indent=2, ensure_ascii=False)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


async def call_batch_ocr(
    *,
    files: list[dict[str, str]],
    lang: str = "spa+eng",
    dpi: int = 300,
) -> str:
    multipart_files: list[tuple[str, tuple[str, bytes, str]]] = []
    for f in files:
        data = base64.b64decode(f["base64"])
        multipart_files.append(
            ("files", (f["filename"], data, "application/octet-stream"))
        )

    form = {"lang": lang, "dpi": str(dpi)}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(
            f"{OCR_API_URL}/api/v1/ocr/batch",
            files=multipart_files,
            data=form,
            headers=_headers(),
        )
        r.raise_for_status()
        return json.dumps(r.json(), indent=2, ensure_ascii=False)


async def call_validate_text(text: str) -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        files = {"file": ("validate.txt", text.encode("utf-8"), "text/plain")}
        r = await client.post(
            f"{OCR_API_URL}/api/v1/validate",
            files=files,
            headers=_headers(),
        )
        r.raise_for_status()
        return json.dumps(r.json(), indent=2, ensure_ascii=False)
