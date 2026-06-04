"""OCR engine using Tesseract for scanned PDFs and images."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OcrResult:
    """Result of an OCR operation."""

    input_path: Path
    text: str
    pages: int
    ocr_engine: str = "tesseract"


class OcrError(RuntimeError):
    """Raised when OCR processing fails."""


def _check_tesseract() -> None:
    """Verify tesseract is installed and accessible."""
    if shutil.which("tesseract") is None:
        raise OcrError(
            "Tesseract OCR not found. Install it first:\n"
            "  macOS:      brew install tesseract tesseract-lang\n"
            "  Debian:     sudo apt install tesseract-ocr tesseract-ocr-spa\n"
            "  Docker:     use the provided Dockerfile"
        )


def ocr_image(image_path: Path, *, lang: str = "spa+eng") -> OcrResult:
    """Run Tesseract OCR on a single image file.

    Args:
        image_path: Path to PNG, JPEG, or TIFF image.
        lang: Tesseract language(s), e.g. 'spa+eng'.

    Returns:
        OcrResult with extracted text.

    Raises:
        OcrError: If the file doesn't exist or OCR fails.
    """
    _check_tesseract()

    if not image_path.exists():
        raise OcrError(f"Image not found: {image_path}")

    with tempfile.TemporaryDirectory(prefix="ether-ocr-") as tmpdir:
        output_base = Path(tmpdir) / "ocr_output"
        command = [
            "tesseract",
            str(image_path),
            str(output_base),
            "-l", lang,
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)

        if completed.returncode != 0:
            stderr = completed.stderr.strip() or "tesseract failed without stderr"
            raise OcrError(f"OCR failed: {stderr}")

        output_file = Path(f"{output_base}.txt")
        if not output_file.exists():
            raise OcrError("OCR produced no output file")

        text = output_file.read_text(encoding="utf-8")

    return OcrResult(
        input_path=image_path,
        text=text,
        pages=1,
    )


def ocr_pdf_scanned(
    pdf_path: Path,
    *,
    lang: str = "spa+eng",
    dpi: int = 300,
) -> OcrResult:
    """Convert a scanned PDF to images and OCR each page.

    Uses pdf2image (requires Poppler) to convert PDF pages to images,
    then runs Tesseract OCR on each page image.

    Args:
        pdf_path: Path to the scanned PDF.
        lang: Tesseract language(s).
        dpi: Resolution for PDF-to-image conversion.

    Returns:
        OcrResult with concatenated text from all pages.
    """
    _check_tesseract()

    if not pdf_path.exists():
        raise OcrError(f"PDF not found: {pdf_path}")

    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise OcrError(
            "pdf2image is required for PDF OCR. Install it:\n"
            "  pip install pdf2image\n"
            "  Also requires Poppler (brew install poppler / apt install poppler-utils)"
        )

    with tempfile.TemporaryDirectory(prefix="ether-ocr-pages-") as tmpdir:
        try:
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                output_folder=tmpdir,
                fmt="png",
            )
        except Exception as exc:
            raise OcrError(f"Failed to convert PDF to images: {exc}") from exc

        if not images:
            return OcrResult(input_path=pdf_path, text="", pages=0)

        text_parts: list[str] = []
        for i, image in enumerate(images, start=1):
            page_img = Path(tmpdir) / f"page_{i:04d}.png"
            image.save(str(page_img), "PNG")

            try:
                page_result = ocr_image(page_img, lang=lang)
                text_parts.append(page_result.text)
            except OcrError as exc:
                text_parts.append(f"[OCR ERROR on page {i}: {exc}]")

    combined_text = "\n\n".join(text_parts)
    return OcrResult(
        input_path=pdf_path,
        text=combined_text,
        pages=len(images),
    )


def has_text_layer(pdf_path: Path, *, pdftotext_bin: str = "pdftotext") -> bool:
    """Quick check: does the PDF have an extractable text layer?

    Returns True if Poppler can extract meaningful text (>10 chars).
    """
    if shutil.which(pdftotext_bin) is None:
        return False

    with tempfile.TemporaryDirectory(prefix="ether-ocr-check-") as tmpdir:
        output = Path(tmpdir) / "check.txt"
        result = subprocess.run(
            [pdftotext_bin, "-l", "1", str(pdf_path), str(output)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return False
        text = output.read_text(encoding="utf-8").strip()
        return len(text) > 10
