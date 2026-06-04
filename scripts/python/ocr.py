#!/usr/bin/env python3
"""OCR script — runs OCR on a PDF or image file and outputs clean UTF-8 text."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _add_src_to_path() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    src_dir = repo_root / "python" / "src"
    sys.path.insert(0, str(src_dir))


def main(argv: list[str] | None = None) -> int:
    _add_src_to_path()

    parser = argparse.ArgumentParser(
        prog="ocr",
        description="Run OCR on a PDF or image file to extract clean UTF-8 text.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input file (.pdf, .png, .jpg, .jpeg, .tiff)",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Output .txt file",
    )
    parser.add_argument(
        "--image",
        action="store_true",
        help="Force image mode (skip PDF-to-image conversion)",
    )
    parser.add_argument(
        "--lang",
        default="spa+eng",
        help="Tesseract language(s) (default: spa+eng)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for PDF-to-image conversion (default: 300)",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Write output even if RAG validation would fail",
    )

    args = parser.parse_args(argv)

    try:
        from ether_ocr.pipeline import ocr_document

        result = ocr_document(
            input_path=args.input,
            output_path=args.output,
            force_image=args.image,
            lang=args.lang,
            dpi=args.dpi,
            validate=not args.skip_validation,
        )

        print(f"Output: {result.output_path}")
        print(f"Pages processed: {result.pages}")
        print(f"Paragraphs: {result.paragraphs}")
        print(f"Size: {result.size_bytes / 1024:.1f} KB")
        return 0

    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
