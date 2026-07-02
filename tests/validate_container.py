#!/usr/bin/env python3
"""Validador de integracion para el CLI OCR por contenedor.

Construye la imagen, ejecuta OCR sobre el PDF de prueba usando el script
docker-run.sh y verifica que el texto extraido contenga lo esperado.

Usa variables de entorno para configuracion:

  DOCKER_IMAGE — Nombre de la imagen (default: ether-ocr)
  DOCKER_TAG   — Tag de la imagen (default: latest)

Uso:
  python3 validate_container.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SAMPLE_PDF = Path(__file__).parent / "sample.pdf"
DOCKER_RUN = REPO_ROOT / "scripts" / "shellscript" / "docker-run.sh"

IMAGE_NAME = os.getenv("DOCKER_IMAGE", "ether-ocr")
IMAGE_TAG = os.getenv("DOCKER_TAG", "latest")

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


def _run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["DOCKER_IMAGE"] = IMAGE_NAME
    env["DOCKER_TAG"] = IMAGE_TAG
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
        **kwargs,  # type: ignore[arg-type]
    )


def check_docker_available() -> bool:
    """Verifica que docker/podman este disponible."""
    name = "docker disponible"
    try:
        r = subprocess.run(
            ["docker", "version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0:
            _ok(name)
            return True
        _fail(name, f"exit code={r.returncode}")
        return False
    except FileNotFoundError:
        _fail(name, "docker no encontrado en PATH")
        return False
    except Exception as exc:
        _fail(name, str(exc))
        return False


def check_dockerfile_exists() -> None:
    """Verifica que el Dockerfile exista."""
    name = "Dockerfile existe"
    dockerfile = REPO_ROOT / "containers" / "Dockerfile"
    if dockerfile.exists():
        _ok(name)
    else:
        _fail(name, f"no encontrado en {dockerfile}")


def build_image() -> bool:
    """Construye la imagen Docker."""
    name = "docker build"
    dockerfile = REPO_ROOT / "containers" / "Dockerfile"
    print(f"    Construyendo {IMAGE_NAME}:{IMAGE_TAG} ...")
    r = _run(
        ["docker", "build", "-t", f"{IMAGE_NAME}:{IMAGE_TAG}",
         "-f", str(dockerfile), str(REPO_ROOT)],
        timeout=300,
    )
    if r.returncode == 0:
        _ok(name)
        return True
    _fail(name, f"exit={r.returncode}\n    stderr: {r.stderr[-300:]}")
    return False


def check_sample_pdf() -> None:
    """Verifica que el PDF de prueba exista."""
    name = "sample.pdf existe"
    if SAMPLE_PDF.exists():
        _ok(name)
    else:
        _fail(name, f"no encontrado en {SAMPLE_PDF}. Ejecuta: python3 generate_pdf.py")


def run_ocr_on_sample() -> None:
    """Ejecuta OCR sobre el PDF de prueba dentro del contenedor."""
    name = "docker-run OCR sobre sample.pdf"
    output = "/tmp/ether-ocr-test-output.txt"

    r = _run(
        ["bash", str(DOCKER_RUN), str(SAMPLE_PDF), output],
        timeout=120,
    )
    if r.returncode != 0:
        return _fail(name, f"exit={r.returncode}\n    stderr: {r.stderr[-300:]}")

    try:
        text = Path(output).read_text(encoding="utf-8")
    except FileNotFoundError:
        return _fail(name, f"archivo de salida no encontrado: {output}")
    except Exception as exc:
        return _fail(name, str(exc))

    if not text.strip():
        return _fail(name, "texto extraido vacio")

    if "Hola mundo" not in text and "Articulo" not in text and "Artículo" not in text:
        return _fail(name, f"contenido no coincide: {text[:100]}")

    # Cleanup
    Path(output).unlink(missing_ok=True)
    _ok(name)


def run_all() -> int:
    print(f"\nether-ocr container validator")
    print(f"  Image: {IMAGE_NAME}:{IMAGE_TAG}")
    print()

    check_dockerfile_exists()
    check_sample_pdf()

    if not check_docker_available():
        print(f"\n  Resultado: {passed} OK, {failed} FAIL")
        return 1

    if not build_image():
        print(f"\n  Resultado: {passed} OK, {failed} FAIL")
        return 1

    run_ocr_on_sample()

    print(f"\n  Resultado: {passed} OK, {failed} FAIL")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all())
