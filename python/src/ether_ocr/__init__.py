"""OCR engine and utilities to prepare plain UTF-8 text for RAG ingestion."""

from ether_ocr.pipeline import OcrPipelineResult, ocr_document
from ether_ocr.preparer import PreparationResult, prepare_document
from ether_ocr.validator import ValidationResult, validate_plain_text

__all__ = [
    "OcrPipelineResult",
    "PreparationResult",
    "ValidationResult",
    "ocr_document",
    "prepare_document",
    "validate_plain_text",
]
