"""High-level document preparation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ether_ocr_core.cleaner import clean_extracted_text, count_paragraphs
from ether_ocr_core.extractor import extract_pdf_text
from ether_ocr_core.validator import ValidationResult, validate_plain_text


@dataclass(frozen=True)
class PreparationResult:
    input_path: Path
    output_path: Path
    paragraphs: int
    size_bytes: int
    validation: ValidationResult


def prepare_document(
    input_path: Path,
    output_path: Path,
    *,
    validate: bool = True,
    pdftotext_bin: str = "pdftotext",
) -> PreparationResult:
    """Prepare a PDF or text file as clean UTF-8 text for RAG ingestion."""
    source = Path(input_path)
    target = Path(output_path)

    if source.suffix.lower() == ".pdf":
        raw_text = extract_pdf_text(source, pdftotext_bin=pdftotext_bin)
    else:
        raw_text = source.read_text(encoding="utf-8")

    cleaned = clean_extracted_text(raw_text)
    validation = validate_plain_text(cleaned) if validate else ValidationResult()
    if not validation.valid:
        raise ValueError(validation.error_message())

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(cleaned, encoding="utf-8")

    return PreparationResult(
        input_path=source,
        output_path=target,
        paragraphs=count_paragraphs(cleaned),
        size_bytes=len(cleaned.encode("utf-8")),
        validation=validation,
    )
