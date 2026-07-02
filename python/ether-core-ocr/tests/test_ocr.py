"""Tests for ether_ocr_core.ocr module — unit tests without requiring Tesseract."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from ether_ocr_core.ocr import (
    OcrError,
    OcrResult,
    has_text_layer,
    ocr_image,
    ocr_pdf_scanned,
)

# Pre-register pdf2image as a mock module so @patch can resolve it
if "pdf2image" not in sys.modules:
    sys.modules["pdf2image"] = MagicMock()


class TestOcrImage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path("/tmp/ether-ocr-test")
        self.temp_dir.mkdir(exist_ok=True)

    def test_file_not_found_raises_error(self):
        with self.assertRaises(OcrError):
            ocr_image(Path("/nonexistent/image.png"))

    @patch("ether_ocr_core.ocr.shutil.which", return_value="/usr/bin/tesseract")
    @patch("ether_ocr_core.ocr.subprocess.run")
    @patch("ether_ocr_core.ocr.tempfile.TemporaryDirectory")
    def test_ocr_success(self, mock_tmpdir, mock_run, mock_which):
        # Setup mock temporary directory
        mock_context = MagicMock()
        mock_tmpdir.return_value = mock_context
        mock_context.__enter__.return_value = "/tmp/mock-tmp"

        # Mock subprocess to simulate successful OCR
        mock_run.return_value = MagicMock(returncode=0)

        # Mock the output file that tesseract creates
        with patch("pathlib.Path.exists", return_value=True):
            with patch.object(
                Path, "read_text", return_value="Texto extraído de prueba."
            ):
                result = ocr_image(Path("/tmp/test.png"), lang="spa")

        self.assertIsInstance(result, OcrResult)
        self.assertEqual(result.pages, 1)
        self.assertIn("Texto extraído", result.text)

    @patch("ether_ocr_core.ocr.shutil.which", return_value=None)
    def test_tesseract_not_found(self, mock_which):
        with self.assertRaises(OcrError) as ctx:
            ocr_image(Path("/tmp/test.png"))
        self.assertIn("Tesseract OCR not found", str(ctx.exception))


class TestOcrPdfScanned(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path("/tmp/ether-ocr-test")
        self.temp_dir.mkdir(exist_ok=True)

    def test_file_not_found_raises_error(self):
        with self.assertRaises(OcrError):
            ocr_pdf_scanned(Path("/nonexistent/doc.pdf"))

    @patch("ether_ocr_core.ocr.shutil.which", return_value="/usr/bin/tesseract")
    @patch("ether_ocr_core.ocr.tempfile.TemporaryDirectory")
    def test_ocr_pdf_with_images(self, mock_tmpdir, mock_which):
        mock_context = MagicMock()
        mock_tmpdir.return_value = mock_context
        mock_context.__enter__.return_value = "/tmp/mock-tmp"

        # Create dummy PDF file
        pdf = self.temp_dir / "test.pdf"
        pdf.write_text("dummy pdf content")

        # Create a dummy image mock
        mock_image = MagicMock()
        with patch("pdf2image.convert_from_path", return_value=[mock_image]):
            # Also mock ocr_image to return a controlled result
            with patch("ether_ocr_core.ocr.ocr_image") as mock_ocr_image:
                mock_ocr_image.return_value = OcrResult(
                    input_path=Path("/tmp/page.png"),
                    text="Página 1 de prueba.",
                    pages=1,
                )

                result = ocr_pdf_scanned(pdf)

        self.assertEqual(result.pages, 1)
        self.assertIn("Página 1", result.text)

    @patch("ether_ocr_core.ocr.shutil.which", return_value="/usr/bin/tesseract")
    @patch("pdf2image.convert_from_path", return_value=[])
    def test_empty_pdf(self, mock_convert, mock_which):
        pdf = self.temp_dir / "empty.pdf"
        pdf.write_text("dummy pdf content")
        result = ocr_pdf_scanned(pdf)
        self.assertEqual(result.pages, 0)
        self.assertEqual(result.text, "")


class TestHasTextLayer(unittest.TestCase):
    @patch("ether_ocr_core.ocr.shutil.which", return_value=None)
    def test_no_pdftotext_returns_false(self, mock_which):
        result = has_text_layer(Path("/tmp/test.pdf"))
        self.assertFalse(result)

    @patch("ether_ocr_core.ocr.shutil.which", return_value="/usr/bin/pdftotext")
    @patch("ether_ocr_core.ocr.subprocess.run")
    def test_empty_text_returns_false(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        with patch.object(Path, "read_text", return_value="  "):
            result = has_text_layer(Path("/tmp/test.pdf"))
            self.assertFalse(result)

    @patch("ether_ocr_core.ocr.shutil.which", return_value="/usr/bin/pdftotext")
    @patch("ether_ocr_core.ocr.subprocess.run")
    def test_meaningful_text_returns_true(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        with patch.object(
            Path,
            "read_text",
            return_value="Este es un texto largo con suficiente contenido.",
        ):
            result = has_text_layer(Path("/tmp/test.pdf"))
            self.assertTrue(result)
