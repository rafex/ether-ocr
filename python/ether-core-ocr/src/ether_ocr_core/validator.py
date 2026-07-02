"""Plain-text validator for RAG ingestion compatibility."""

from __future__ import annotations

from dataclasses import dataclass, field
import re

_RE_MD_HEADER = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_RE_MD_BOLD_ITALIC = re.compile(r"(\*{1,2}|_{1,2})\w.+?\1")
_RE_MD_LINK = re.compile(r"(?<!!)\[.+?\]\(.+?\)")
_RE_MD_IMAGE = re.compile(r"!\[.*?\]\(.+?\)")
_RE_MD_CODE_FENCE = re.compile(r"^```", re.MULTILINE)
_RE_MD_CODE_INLINE = re.compile(r"`[^`\n]+`")
_RE_MD_TABLE_ROW = re.compile(r"^\|.+\|", re.MULTILINE)
_RE_MD_TABLE_SEP = re.compile(r"^\|[-:| ]+\|", re.MULTILINE)
_RE_HTML_TAG = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*(\s[^>]*)?>", re.IGNORECASE)
_RE_HTML_ENTITY = re.compile(r"&[a-zA-Z]{2,8};")
_RE_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


@dataclass
class ValidationResult:
    valid: bool = True
    issues: list[str] = field(default_factory=list)

    def add(self, issue: str) -> None:
        self.valid = False
        self.issues.append(issue)

    def error_message(self) -> str:
        if self.valid:
            return "OK"
        details = "\n".join(f"- {issue}" for issue in self.issues)
        return "El texto no cumple con formato plano para RAG:\n" + details


def validate_plain_text(text: str) -> ValidationResult:
    """Reject likely Markdown, HTML and non-text control characters."""
    result = ValidationResult()

    control_chars = _RE_CONTROL_CHARS.findall(text)
    if control_chars:
        result.add(
            f"Detectados {len(control_chars)} caracter(es) de control no permitidos."
        )

    headers = _RE_MD_HEADER.findall(text)
    if len(headers) >= 2:
        result.add(f"Detectados {len(headers)} header(s) Markdown con '#'.")

    images = _RE_MD_IMAGE.findall(text)
    if images:
        result.add(f"Detectadas {len(images)} imagen(es) Markdown.")

    links = _RE_MD_LINK.findall(text)
    if links:
        result.add(f"Detectados {len(links)} enlace(s) Markdown.")

    fences = _RE_MD_CODE_FENCE.findall(text)
    if fences:
        result.add("Detectado bloque de codigo Markdown con triple backtick.")

    emphasis = _RE_MD_BOLD_ITALIC.findall(text)
    if len(emphasis) >= 3:
        result.add(f"Detectadas {len(emphasis)} marca(s) Markdown de negrita/cursiva.")

    inline_code = _RE_MD_CODE_INLINE.findall(text)
    if len(inline_code) >= 5:
        result.add(f"Detectadas {len(inline_code)} marca(s) de codigo inline Markdown.")

    table_rows = _RE_MD_TABLE_ROW.findall(text)
    table_separators = _RE_MD_TABLE_SEP.findall(text)
    if len(table_rows) >= 2 or table_separators:
        result.add("Detectada tabla Markdown.")

    html_tags = _RE_HTML_TAG.findall(text)
    if len(html_tags) >= 2:
        result.add(f"Detectados {len(html_tags)} tag(s) HTML.")

    entities = _RE_HTML_ENTITY.findall(text)
    if len(entities) >= 3:
        result.add(f"Detectadas {len(entities)} entidad(es) HTML.")

    return result
