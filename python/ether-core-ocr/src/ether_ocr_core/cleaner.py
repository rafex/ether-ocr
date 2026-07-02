"""Text cleanup rules for PDF text extracted with pdftotext."""

from __future__ import annotations

import re

_PAGE_NUMBER_RE = re.compile(r"^\d{1,4}$")
_ARTICLE_RE = re.compile(r"\n(Art[i\u00ed]culo\s+\d+)", re.IGNORECASE)
_SECTION_RE = re.compile(
    r"\n(T[I\u00cd]TULO\s+|CAP[I\u00cd]TULO\s+|SECCI[O\u00d3]N\s+)",
    re.IGNORECASE,
)
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")
_MANY_NEWLINES_RE = re.compile(r"\n{3,}")


def clean_extracted_text(text: str) -> str:
    """Normalize layout artifacts while preserving paragraph boundaries."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines: list[str] = []

    for raw_line in normalized.splitlines():
        line = raw_line.strip()
        if _PAGE_NUMBER_RE.fullmatch(line):
            continue
        lines.append(line)

    cleaned = "\n".join(lines)
    cleaned = _MANY_NEWLINES_RE.sub("\n\n", cleaned)
    cleaned = _ARTICLE_RE.sub(r"\n\n\1", cleaned)
    cleaned = _SECTION_RE.sub(r"\n\n\1", cleaned)
    cleaned = _MULTI_SPACE_RE.sub(" ", cleaned)
    cleaned = _MANY_NEWLINES_RE.sub("\n\n", cleaned)
    return cleaned.strip()


def count_paragraphs(text: str) -> int:
    """Count non-empty paragraphs separated by blank lines."""
    return len([p for p in text.split("\n\n") if p.strip()])
