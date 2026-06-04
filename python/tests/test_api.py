"""Integration tests for the ether-ocr REST API."""

from __future__ import annotations

import io
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from ether_ocr.api.server import create_app
from ether_ocr.pipeline import OcrPipelineResult
from ether_ocr.validator import ValidationResult


class TestHealthEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)

    def test_health_returns_200(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)

    def test_health_response_schema(self):
        response = self.client.get("/api/v1/health")
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "ether-ocr")
        self.assertIn("version", data)

    def test_openapi_schema_generated(self):
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(schema["info"]["title"], "ether-ocr")
        self.assertIn("/api/v1/health", schema["paths"])

    def test_docs_accessible(self):
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)

    def test_redoc_accessible(self):
        response = self.client.get("/redoc")
        self.assertEqual(response.status_code, 200)

    def test_404_on_unknown_route(self):
        response = self.client.get("/api/v1/nonexistent")
        self.assertEqual(response.status_code, 404)


class TestOcrEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)

    def test_ocr_without_file_returns_422(self):
        response = self.client.post("/api/v1/ocr")
        self.assertEqual(response.status_code, 422)

    def test_ocr_unsupported_extension_returns_415(self):
        response = self.client.post(
            "/api/v1/ocr",
            files={"file": ("document.docx", io.BytesIO(b"fake"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        self.assertEqual(response.status_code, 415)

    @patch("ether_ocr.api.routes.ocr.ocr_document")
    def test_ocr_plain_text_success(self, mock_ocr):
        from pathlib import Path

        mock_ocr.return_value = OcrPipelineResult(
            input_path=Path("/tmp/test.txt"),
            output_path=Path("/tmp/test.txt"),
            pages=1,
            paragraphs=3,
            size_bytes=100,
            used_ocr=False,
            validation=ValidationResult(valid=True),
        )

        with patch.object(Path, "read_text", return_value="Hello world\n\nTest text."):
            with patch.object(Path, "unlink"):  # Cleanup tries to delete temp file
                response = self.client.post(
                    "/api/v1/ocr",
                    files={"file": ("test.txt", io.BytesIO(b"Hello world\n\nTest text."), "text/plain")},
                    data={"lang": "spa", "validate": "false"},
                )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("text", data)
        self.assertEqual(data["metadata"]["ocr_used"], False)
        self.assertEqual(data["metadata"]["method"], "poppler")

    @patch("ether_ocr.api.routes.ocr.ocr_document")
    def test_ocr_with_validation_failure(self, mock_ocr):
        mock_ocr.side_effect = ValueError("El texto no cumple con formato plano para RAG:\n- Detectados 2 header(s) Markdown")

        response = self.client.post(
            "/api/v1/ocr",
            files={"file": ("bad.txt", io.BytesIO(b"# Title\n\n## Subtitle"), "text/plain")},
            data={"validate": "true"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Markdown", response.json()["detail"])

    def test_ocr_openapi_registered(self):
        response = self.client.get("/openapi.json")
        schema = response.json()
        self.assertIn("/api/v1/ocr", schema["paths"])
        self.assertIn("post", schema["paths"]["/api/v1/ocr"])


if __name__ == "__main__":
    unittest.main()
