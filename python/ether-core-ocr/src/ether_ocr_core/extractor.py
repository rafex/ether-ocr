"""PDF text extraction using the external Poppler pdftotext binary."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


class PdfExtractionError(RuntimeError):
    """Raised when a PDF cannot be converted to text."""


def extract_pdf_text(pdf_path: Path, *, pdftotext_bin: str = "pdftotext") -> str:
    """Extract text from a PDF with pdftotext -layout and return UTF-8 text."""
    if not pdf_path.exists():
        raise PdfExtractionError(f"Input file does not exist: {pdf_path}")
    if shutil.which(pdftotext_bin) is None:
        raise PdfExtractionError(
            f"'{pdftotext_bin}' was not found. Install Poppler first "
            "(macOS: brew install poppler; Debian/Ubuntu: sudo apt install poppler-utils)."
        )

    with tempfile.TemporaryDirectory(prefix="ether-ocr-") as tmpdir:
        output_path = Path(tmpdir) / "raw.txt"
        command = [pdftotext_bin, "-layout", str(pdf_path), str(output_path)]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or "pdftotext failed without stderr"
            raise PdfExtractionError(stderr)
        return output_path.read_text(encoding="utf-8")
