"""Document processing pipeline — routes inputs through extractor or OCR."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ether_ocr.cleaner import clean_extracted_text, count_paragraphs
from ether_ocr.extractor import PdfExtractionError, extract_pdf_text
from ether_ocr.ocr import has_text_layer, ocr_image, ocr_pdf_scanned
from ether_ocr.validator import ValidationResult, validate_plain_text


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


def ocr_document(
    input_path: Path,
    output_path: Path,
    *,
    force_image: bool = False,
    lang: str = "spa+eng",
    dpi: int = 300,
    validate: bool = True,
) -> OcrPipelineResult:
    """Process a PDF or image through the OCR pipeline.

    For PDFs: tries Poppler text extraction first; falls back to OCR
    if the text layer is empty or insufficient.
    For images: always uses OCR.

    Args:
        input_path: Input file (.pdf, .png, .jpg, .jpeg, .tiff).
        output_path: Output .txt file.
        force_image: Skip PDF logic and treat input as an image.
        lang: Tesseract language(s).
        dpi: DPI for PDF-to-image conversion.
        validate: Run RAG compatibility validation.

    Returns:
        OcrPipelineResult with output details.

    Raises:
        FileNotFoundError: If input doesn't exist.
        ValueError: If validation fails and validate=True.
    """
    source = Path(input_path)
    target = Path(output_path)

    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")

    suffix = source.suffix.lower()
    text: str = ""
    used_ocr = False
    pages = 0

    # ── Image handling ─────────────────────────────────
    if force_image or suffix in (".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"):
        result = ocr_image(source, lang=lang)
        text = result.text
        used_ocr = True
        pages = 1

    # ── PDF handling ───────────────────────────────────
    elif suffix == ".pdf":
        # First, try Poppler text extraction
        try:
            text = extract_pdf_text(source)
        except PdfExtractionError:
            text = ""

        # If text is insufficient, fall back to OCR
        if len(text.strip()) < 10:
            if has_text_layer(source):
                # Has text but it's short — use what we got
                pass
            else:
                result = ocr_pdf_scanned(source, lang=lang, dpi=dpi)
                text = result.text
                used_ocr = True
                pages = result.pages
        else:
            pages = 1  # Poppler extraction

    else:
        # Treat unknown extensions as text files
        text = source.read_text(encoding="utf-8")

    # ── Clean and validate ─────────────────────────────
    cleaned = clean_extracted_text(text)
    validation = validate_plain_text(cleaned) if validate else ValidationResult()

    if not validation.valid:
        raise ValueError(validation.error_message())

    # ── Write output ───────────────────────────────────
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(cleaned, encoding="utf-8")

    return OcrPipelineResult(
        input_path=source,
        output_path=target,
        pages=pages,
        paragraphs=count_paragraphs(cleaned),
        size_bytes=len(cleaned.encode("utf-8")),
        used_ocr=used_ocr,
        validation=validation,
    )
