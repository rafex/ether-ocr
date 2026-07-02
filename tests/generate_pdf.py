#!/usr/bin/env python3
"""Genera un PDF valido con texto Unicode para pruebas de OCR."""

import io
import zlib
from pathlib import Path


def _p(s: str) -> bytes:
    """Encode a string as a PDF literal string with escaping."""
    escaped = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"({escaped})".encode("latin-1")


def build_pdf() -> bytes:
    text_content = (
        "Hola mundo.\n"
        "Este es un documento de prueba para OCR.\n"
        "Art\xedculo 1. Todo texto debe ser procesado correctamente.\n"
        "Art\xedculo 2. La validaci\xf3n debe confirmar UTF-8 limpio.\n"
        "Caracteres especiales: acentos, enies, signos.\n"
        "El servicio ether-ocr debe extraer este contenido sin errores.\n"
    )

    font_name = "/F1"
    font_size = 12

    stream_raw = f"BT {font_name} {font_size} Tf 72 700 Td {_p(text_content).decode('latin-1')} Tj ET"
    stream_bytes = stream_raw.encode("latin-1")

    compressed = zlib.compress(stream_bytes)

    buf = io.BytesIO()

    def obj(n: int) -> None:
        buf.write(f"{n} 0 obj\n".encode())

    def endobj() -> None:
        buf.write(b"endobj\n")

    buf.write(b"%PDF-1.4\n")

    obj(1)
    buf.write(b"<< /Type /Catalog /Pages 2 0 R >>\n")
    endobj()

    obj(2)
    buf.write(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n")
    endobj()

    obj(3)
    buf.write(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\n"
    )
    endobj()

    obj(4)
    buf.write(f"<< /Length {len(compressed)} /Filter /FlateDecode >>\n".encode())
    buf.write(b"stream\n")
    buf.write(compressed)
    buf.write(b"\nendstream\n")
    endobj()

    obj(5)
    buf.write(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\n")
    endobj()

    offsets: list[int] = []
    body = buf.getvalue()
    pos = 0
    for line in body.split(b"\n"):
        offsets.append(pos)
        pos += len(line) + 1

    xref_pos = pos
    buf.write(f"xref\n0 6\n0000000000 65535 f \n".encode())
    for off in offsets:
        buf.write(f"{off:010d} 00000 n \n".encode())

    buf.write(b"trailer\n<< /Size 6 /Root 1 0 R >>\n")
    buf.write(f"startxref\n{xref_pos}\n%%EOF\n".encode())

    return buf.getvalue()


def main() -> None:
    out = Path(__file__).parent / "sample.pdf"
    pdf = build_pdf()
    out.write_bytes(pdf)
    print(f"PDF generado: {out} ({len(pdf)} bytes)")


if __name__ == "__main__":
    main()
