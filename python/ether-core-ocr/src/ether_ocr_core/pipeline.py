"""Document processing pipeline — routes inputs through extractor or OCR."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ether_ocr_core.cleaner import clean_extracted_text, count_paragraphs
from ether_ocr_core.extractor import PdfExtractionError, extract_pdf_text
from ether_ocr_core.ocr import has_text_layer, ocr_image, ocr_pdf_scanned
from ether_ocr_core.validator import ValidationResult, validate_plain_text

_IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}
)


@dataclass(frozen=True)
class OcrPipelineResult:
    """Result of the full OCR pipeline."""

    input_path: Path
    output_path: Path
    pages: int
    paragraphs: int
    size_bytes: int
    used_ocr: bool
    validation: ValidationResult


def _process_image(source: Path, lang: str) -> tuple[str, bool, int]:
    """Extract text from an image file using Tesseract OCR."""
    result = ocr_image(source, lang=lang)
    return result.text, True, 1


def _process_pdf(source: Path, lang: str, dpi: int) -> tuple[str, bool, int]:
    """Extract text from a PDF — Poppler first, OCR as fallback."""
    text = ""
    used_ocr = False
    pages = 0

    try:
        text = extract_pdf_text(source)
    except PdfExtractionError:
        text = ""

    if len(text.strip()) < 10:
        if has_text_layer(source):
            pages = 1
        else:
            result = ocr_pdf_scanned(source, lang=lang, dpi=dpi)
            text = result.text
            used_ocr = True
            pages = result.pages
    else:
        pages = 1

    return text, used_ocr, pages


def _process_text(source: Path) -> tuple[str, bool, int]:
    """Read a plain text file as-is."""
    return source.read_text(encoding="utf-8"), False, 0


def _validate_and_write(
    text: str,
    target: Path,
    *,
    validate: bool,
) -> tuple[str, ValidationResult]:
    cleaned = clean_extracted_text(text)
    validation = validate_plain_text(cleaned) if validate else ValidationResult()

    if not validation.valid:
        raise ValueError(validation.error_message())

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(cleaned, encoding="utf-8")
    return cleaned, validation


def ocr_document(
    input_path: Path,
    output_path: Path,
    *,
    force_image: bool = False,
    lang: str = "spa+eng",
    dpi: int = 300,
    validate: bool = True,
) -> OcrPipelineResult:
    """Process a PDF or image through the OCR pipeline."""
    source = Path(input_path)
    target = Path(output_path)

    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")

    suffix = source.suffix.lower()

    if force_image or suffix in _IMAGE_EXTENSIONS:
        text, used_ocr, pages = _process_image(source, lang)
    elif suffix == ".pdf":
        text, used_ocr, pages = _process_pdf(source, lang, dpi)
    else:
        text, used_ocr, pages = _process_text(source)

    cleaned, validation = _validate_and_write(text, target, validate=validate)

    return OcrPipelineResult(
        input_path=source,
        output_path=target,
        pages=pages,
        paragraphs=count_paragraphs(cleaned),
        size_bytes=len(cleaned.encode("utf-8")),
        used_ocr=used_ocr,
        validation=validation,
    )
