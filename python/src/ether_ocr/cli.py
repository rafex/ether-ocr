"""Command line interface for ether_ocr."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ether_ocr.cleaner import clean_extracted_text, count_paragraphs
from ether_ocr.pipeline import ocr_document
from ether_ocr.preparer import prepare_document
from ether_ocr.validator import validate_plain_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ether-ocr",
        description="Prepare PDF or raw text files as plain UTF-8 text for RAG ingestion.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    prepare = subcommands.add_parser("prepare", help="Extract, clean and validate a document.")
    prepare.add_argument("input", type=Path, help="Input .pdf or UTF-8 text file.")
    prepare.add_argument("output", type=Path, help="Output .txt file.")
    prepare.add_argument("--pdftotext-bin", default="pdftotext", help="pdftotext executable name/path.")
    prepare.add_argument("--skip-validation", action="store_true", help="Write output even if RAG validation would fail.")

    clean = subcommands.add_parser("clean", help="Clean an already extracted UTF-8 text file.")
    clean.add_argument("input", type=Path, help="Raw UTF-8 text file.")
    clean.add_argument("output", type=Path, help="Output .txt file.")

    validate = subcommands.add_parser("validate", help="Validate a UTF-8 text file for RAG ingestion.")
    validate.add_argument("input", type=Path, help="UTF-8 text file to validate.")

    ocr = subcommands.add_parser("ocr", help="Run OCR on a scanned PDF or image file.")
    ocr.add_argument("input", type=Path, help="Input file (.pdf, .png, .jpg, .jpeg, .tiff).")
    ocr.add_argument("output", type=Path, help="Output .txt file.")
    ocr.add_argument("--image", action="store_true", help="Force image mode (skip PDF-to-image conversion).")
    ocr.add_argument("--lang", default="spa+eng", help="Tesseract language(s) (default: spa+eng).")
    ocr.add_argument("--dpi", type=int, default=300, help="DPI for PDF-to-image conversion (default: 300).")
    ocr.add_argument("--skip-validation", action="store_true", help="Write output even if RAG validation would fail.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "prepare":
            result = prepare_document(
                args.input,
                args.output,
                validate=not args.skip_validation,
                pdftotext_bin=args.pdftotext_bin,
            )
            print(_summary(result.paragraphs, result.size_bytes, result.output_path))
            return 0

        if args.command == "clean":
            raw = args.input.read_text(encoding="utf-8")
            cleaned = clean_extracted_text(raw)
            validation = validate_plain_text(cleaned)
            if not validation.valid:
                raise ValueError(validation.error_message())
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(cleaned, encoding="utf-8")
            print(_summary(count_paragraphs(cleaned), len(cleaned.encode("utf-8")), args.output))
            return 0

        if args.command == "validate":
            text = args.input.read_text(encoding="utf-8")
            validation = validate_plain_text(text)
            if not validation.valid:
                print(validation.error_message(), file=sys.stderr)
                return 1
            print("OK")
            return 0

        if args.command == "ocr":
            result = ocr_document(
                args.input,
                args.output,
                force_image=args.image,
                lang=args.lang,
                dpi=args.dpi,
                validate=not args.skip_validation,
            )
            print(f"Output: {result.output_path}")
            print(f"Pages: {result.pages}")
            print(f"Paragraphs: {result.paragraphs}")
            print(f"Size: {result.size_bytes / 1024:.1f} KB")
            print(f"OCR used: {'yes' if result.used_ocr else 'no'}")
            return 0

    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    parser.error(f"Unknown command: {args.command}")
    return 2


def _summary(paragraphs: int, size_bytes: int, output_path: Path) -> str:
    return (
        f"Output: {output_path}\n"
        f"Paragraphs: {paragraphs}\n"
        f"Size: {size_bytes / 1024:.1f} KB"
    )
