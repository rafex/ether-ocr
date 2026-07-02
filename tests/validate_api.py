#!/usr/bin/env python3
"""Validador de integracion para la API REST de ether-ocr.

Ejecuta pruebas end-to-end contra el servidor corriendo (local o remoto).
Usa variables de entorno para configuracion:

  OCR_API_URL     — URL base de la API (default: http://localhost:8000)
  OCR_API_KEY     — API key para auth (default: dev-key-ether-ocr)
  OCR_API_TIMEOUT — Timeout HTTP en segundos (default: 30)

Uso:
  python3 validate_api.py
  OCR_API_URL=http://192.168.1.100:8000 python3 validate_api.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

SAMPLE_PDF = Path(__file__).parent / "sample.pdf"

API_URL = os.getenv("OCR_API_URL", "http://localhost:8000")
API_KEY = os.getenv("OCR_API_KEY", "dev-key-ether-ocr")
TIMEOUT = int(os.getenv("OCR_API_TIMEOUT", "30"))

HEADERS = {"X-API-Key": API_KEY}

passed = 0
failed = 0


def _ok(name: str) -> None:
    global passed
    passed += 1
    print(f"  PASS  {name}")


def _fail(name: str, detail: str) -> None:
    global failed
    failed += 1
    print(f"  FAIL  {name}: {detail}")


def health_check() -> None:
    """GET /api/v1/health — debe responder 200 con status ok."""
    name = "GET /api/v1/health"
    try:
        r = httpx.get(f"{API_URL}/api/v1/health", timeout=TIMEOUT)
        if r.status_code != 200:
            return _fail(name, f"status={r.status_code}")
        body = r.json()
        if body.get("status") != "ok":
            return _fail(name, f"status field={body.get('status')}")
        _ok(name)
    except httpx.ConnectError:
        _fail(name, f"no se puede conectar a {API_URL}")
    except Exception as exc:
        _fail(name, str(exc))


def auth_required() -> None:
    """Sin API key debe devolver 401."""
    name = "auth: sin API key retorna 401"
    try:
        r = httpx.post(
            f"{API_URL}/api/v1/ocr",
            files={"file": ("test.txt", b"Hola", "text/plain")},
            timeout=TIMEOUT,
        )
        if r.status_code == 401:
            _ok(name)
        else:
            _fail(name, f"esperado 401, recibido {r.status_code}")
    except httpx.ConnectError:
        _fail(name, f"no se puede conectar a {API_URL}")
    except Exception as exc:
        _fail(name, str(exc))


def ocr_pdf_text_extraction() -> None:
    """POST /api/v1/ocr con PDF con capa de texto."""
    name = "POST /api/v1/ocr (PDF)"
    try:
        with open(SAMPLE_PDF, "rb") as f:
            files = {"file": ("sample.pdf", f, "application/pdf")}
            r = httpx.post(
                f"{API_URL}/api/v1/ocr",
                files=files,
                headers=HEADERS,
                data={"validate": "true"},
                timeout=TIMEOUT,
            )
        if r.status_code != 200:
            return _fail(name, f"status={r.status_code} body={r.text[:200]}")

        body = r.json()
        if body.get("status") != "ok":
            return _fail(name, f"campo status={body.get('status')}")

        text = body.get("text", "")
        if "Hola mundo" not in text and "Articulo" not in text and "Artículo" not in text:
            return _fail(name, f"texto extraido no contiene contenido esperado: {text[:100]}")

        meta = body.get("metadata", {})
        if meta.get("pages", 0) < 1:
            return _fail(name, f"metadata.pages={meta.get('pages')}")

        _ok(name)
    except FileNotFoundError:
        _fail(name, f"no se encontro {SAMPLE_PDF}. Ejecuta primero: python3 generate_pdf.py")
    except httpx.ConnectError:
        _fail(name, f"no se puede conectar a {API_URL}")
    except Exception as exc:
        _fail(name, str(exc))


def ocr_batch() -> None:
    """POST /api/v1/ocr/batch con multiples archivos."""
    name = "POST /api/v1/ocr/batch"
    try:
        txt_content = b"texto de prueba\npara batch\n"
        files = [
            ("files", ("doc1.txt", txt_content, "text/plain")),
            ("files", ("doc2.txt", txt_content, "text/plain")),
        ]
        r = httpx.post(
            f"{API_URL}/api/v1/ocr/batch",
            files=files,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            return _fail(name, f"status={r.status_code}")

        body = r.json()
        if body.get("total_files") != 2:
            return _fail(name, f"total_files={body.get('total_files')}")
        if body.get("successful") != 2:
            return _fail(name, f"successful={body.get('successful')}")

        results = body.get("results", [])
        if len(results) != 2:
            return _fail(name, f"results count={len(results)}")

        ok_count = sum(1 for r in results if r.get("status") == "ok")
        if ok_count != 2:
            return _fail(name, f"resultados OK={ok_count}/2")

        _ok(name)
    except httpx.ConnectError:
        _fail(name, f"no se puede conectar a {API_URL}")
    except Exception as exc:
        _fail(name, str(exc))


def prepare_pdf() -> None:
    """POST /api/v1/prepare con PDF."""
    name = "POST /api/v1/prepare"
    try:
        with open(SAMPLE_PDF, "rb") as f:
            files = {"file": ("sample.pdf", f, "application/pdf")}
            r = httpx.post(
                f"{API_URL}/api/v1/prepare",
                files=files,
                headers=HEADERS,
                timeout=TIMEOUT,
            )
        if r.status_code != 200:
            return _fail(name, f"status={r.status_code}")

        body = r.json()
        if body.get("status") != "ok":
            return _fail(name, f"campo status={body.get('status')}")

        _ok(name)
    except FileNotFoundError:
        _fail(name, f"no se encontro {SAMPLE_PDF}")
    except httpx.ConnectError:
        _fail(name, f"no se puede conectar a {API_URL}")
    except Exception as exc:
        _fail(name, str(exc))


def validate_text() -> None:
    """POST /api/v1/validate con texto valido."""
    name = "POST /api/v1/validate"
    try:
        txt = b"Texto UTF-8 limpio. Sin Markdown ni HTML.\nSolo texto plano.\n"
        files = {"file": ("valid.txt", txt, "text/plain")}
        r = httpx.post(
            f"{API_URL}/api/v1/validate",
            files=files,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            return _fail(name, f"status={r.status_code}")

        body = r.json()
        if body.get("valid") is not True:
            issues = body.get("issues", [])
            return _fail(name, f"valid=false, issues={issues}")

        _ok(name)
    except httpx.ConnectError:
        _fail(name, f"no se puede conectar a {API_URL}")
    except Exception as exc:
        _fail(name, str(exc))


def run_all() -> int:
    print(f"\nether-ocr API validator")
    print(f"  URL:  {API_URL}")
    print(f"  Key:  {API_KEY[:8]}...")
    print()

    if not SAMPLE_PDF.exists():
        print(f"  WARN  {SAMPLE_PDF} no existe. Ejecuta: python3 generate_pdf.py\n")

    health_check()
    auth_required()
    ocr_pdf_text_extraction()
    ocr_batch()
    prepare_pdf()
    validate_text()

    print(f"\n  Resultado: {passed} OK, {failed} FAIL")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all())
