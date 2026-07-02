"""Tests for ether_ocr_core.pipeline module — unit tests without requiring OCR deps."""

import unittest
from pathlib import Path
from unittest.mock import patch

from ether_ocr_core.pipeline import ocr_document


class TestOcrPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path("/tmp/ether-ocr-test")
        self.temp_dir.mkdir(exist_ok=True)

    def test_input_not_found_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            ocr_document(Path("/nonexistent/doc.pdf"), Path("/tmp/output.txt"))

    @patch("ether_ocr_core.pipeline.ocr_image")
    def test_image_input_uses_ocr(self, mock_ocr_image):
        from ether_ocr_core.ocr import OcrResult

        mock_ocr_image.return_value = OcrResult(
            input_path=Path("/tmp/scan.png"),
            text="Texto escaneado de prueba.\n\nSegundo párrafo.",
            pages=1,
        )

        img = self.temp_dir / "scan.png"
        img.write_text("dummy png")

        output = self.temp_dir / "output.txt"
        result = ocr_document(img, output, lang="spa", validate=False)

        self.assertTrue(result.used_ocr)
        self.assertEqual(result.pages, 1)
        self.assertTrue(output.exists())
        content = output.read_text(encoding="utf-8")
        self.assertIn("Texto escaneado", content)

    @patch("ether_ocr_core.pipeline.extract_pdf_text")
    def test_pdf_with_text_layer_uses_extractor(self, mock_extract):
        mock_extract.return_value = "Texto extraído con pdftotext.\n\nSegundo párrafo."

        pdf = self.temp_dir / "doc.pdf"
        pdf.write_text("dummy pdf")

        output = self.temp_dir / "output.txt"
        result = ocr_document(pdf, output, validate=False)

        self.assertFalse(result.used_ocr)
        self.assertTrue(output.exists())
        content = output.read_text(encoding="utf-8")
        self.assertIn("Texto extraído", content)

    @patch("ether_ocr_core.pipeline.extract_pdf_text", return_value="")
    @patch("ether_ocr_core.pipeline.has_text_layer", return_value=False)
    @patch("ether_ocr_core.pipeline.ocr_pdf_scanned")
    def test_pdf_without_text_falls_back_to_ocr(
        self, mock_ocr, mock_has_text, mock_extract
    ):
        from ether_ocr_core.ocr import OcrResult

        mock_ocr.return_value = OcrResult(
            input_path=Path("/tmp/doc.pdf"),
            text="Texto obtenido por OCR.",
            pages=3,
        )

        pdf = self.temp_dir / "doc.pdf"
        pdf.write_text("dummy pdf")

        output = self.temp_dir / "output.txt"
        result = ocr_document(pdf, output, validate=False)

        self.assertTrue(result.used_ocr)
        self.assertEqual(result.pages, 3)
        self.assertTrue(output.exists())

    def test_validation_rejects_markdown(self):
        # Need at least 2 markdown headers to trigger the validator
        text_with_md = "# Título Uno\n\nTexto normal.\n\n## Título Dos\n\nMás texto."
        input_file = self.temp_dir / "text.md"
        input_file.write_text(text_with_md, encoding="utf-8")
        output = self.temp_dir / "output.txt"

        with self.assertRaises(ValueError) as ctx:
            ocr_document(input_file, output, validate=True)
        self.assertIn("Markdown", str(ctx.exception))

    def test_plain_text_passes(self):
        input_file = self.temp_dir / "plain.txt"
        input_file.write_text(
            "Texto completamente plano.\n\nSegundo párrafo.", encoding="utf-8"
        )
        output = self.temp_dir / "output.txt"

        result = ocr_document(input_file, output, validate=True)
        self.assertIsNotNone(result)
        self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
