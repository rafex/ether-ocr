"""Integration tests for the ether-ocr REST API."""

from __future__ import annotations

import io
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from ether_ocr_api.server import create_app
from ether_ocr_api.config import Settings, hash_api_key, override_settings
from ether_ocr_core.pipeline import OcrPipelineResult
from ether_ocr_core.validator import ValidationResult


def _no_auth() -> Settings:
    """Build a Settings with auth disabled for tests that don't test auth."""
    return Settings(auth_enabled=False, rate_limit_enabled=False)


def _with_keys(*keys: str) -> Settings:
    """Build a Settings with specific API keys (plain text, stored as hashes)."""
    return Settings(
        auth_enabled=True,
        api_key_hashes=frozenset(hash_api_key(k) for k in keys),
        rate_limit_enabled=False,
    )


class TestHealthEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        override_settings(_no_auth())
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
        override_settings(_no_auth())
        cls.app = create_app()
        cls.client = TestClient(cls.app)

    def test_ocr_without_file_returns_422(self):
        response = self.client.post("/api/v1/ocr")
        self.assertEqual(response.status_code, 422)

    def test_ocr_unsupported_extension_returns_415(self):
        response = self.client.post(
            "/api/v1/ocr",
            files={
                "file": (
                    "document.docx",
                    io.BytesIO(b"fake"),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
        self.assertEqual(response.status_code, 415)

    @patch("ether_ocr_api.routes.ocr.ocr_document")
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
            with patch.object(Path, "unlink"):
                response = self.client.post(
                    "/api/v1/ocr",
                    files={
                        "file": (
                            "test.txt",
                            io.BytesIO(b"Hello world\n\nTest text."),
                            "text/plain",
                        )
                    },
                    data={"lang": "spa", "validate": "false"},
                )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("text", data)
        self.assertEqual(data["metadata"]["ocr_used"], False)
        self.assertEqual(data["metadata"]["method"], "poppler")

    @patch("ether_ocr_api.routes.ocr.ocr_document")
    def test_ocr_with_validation_failure(self, mock_ocr):
        mock_ocr.side_effect = ValueError(
            "El texto no cumple con formato plano para RAG:\n- Detectados 2 header(s) Markdown"
        )

        response = self.client.post(
            "/api/v1/ocr",
            files={
                "file": ("bad.txt", io.BytesIO(b"# Title\n\n## Subtitle"), "text/plain")
            },
            data={"validate": "true"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Markdown", response.json()["detail"])

    def test_ocr_openapi_registered(self):
        response = self.client.get("/openapi.json")
        schema = response.json()
        self.assertIn("/api/v1/ocr", schema["paths"])
        self.assertIn("post", schema["paths"]["/api/v1/ocr"])

    @patch("ether_ocr_api.routes.ocr.ocr_document")
    def test_ocr_batch_multiple_files(self, mock_ocr):
        from pathlib import Path

        def make_result(*args, **kwargs):
            return OcrPipelineResult(
                input_path=Path("/tmp/t.txt"),
                output_path=Path("/tmp/t.txt"),
                pages=1,
                paragraphs=1,
                size_bytes=10,
                used_ocr=False,
                validation=ValidationResult(valid=True),
            )

        mock_ocr.side_effect = make_result

        with patch.object(Path, "read_text", return_value="batch ok"):
            with patch.object(Path, "unlink"):
                files = [
                    ("files", ("a.txt", io.BytesIO(b"a"), "text/plain")),
                    ("files", ("b.txt", io.BytesIO(b"b"), "text/plain")),
                ]
                response = self.client.post(
                    "/api/v1/ocr/batch",
                    files=files,
                    data={"validate": "false"},
                )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_files"], 2)
        self.assertEqual(data["successful"], 2)
        self.assertEqual(len(data["results"]), 2)

    @patch("ether_ocr_api.routes.ocr.ocr_document")
    def test_ocr_large_text_returns_tar_gz(self, mock_ocr):
        from pathlib import Path

        big_text = "x" * (101 * 1024)
        mock_ocr.return_value = OcrPipelineResult(
            input_path=Path("/tmp/t.txt"),
            output_path=Path("/tmp/t.txt"),
            pages=1,
            paragraphs=1,
            size_bytes=len(big_text.encode("utf-8")),
            used_ocr=False,
            validation=ValidationResult(valid=True),
        )

        with patch.object(Path, "read_text", return_value=big_text):
            with patch.object(Path, "unlink"):
                response = self.client.post(
                    "/api/v1/ocr",
                    files={
                        "file": ("big.txt", io.BytesIO(big_text.encode()), "text/plain")
                    },
                    data={"validate": "false"},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/gzip")
        self.assertIn("attachment", response.headers["content-disposition"])


class TestPrepareEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        override_settings(_no_auth())
        cls.app = create_app()
        cls.client = TestClient(cls.app)

    @patch("ether_ocr_api.routes.prepare.prepare_document")
    def test_prepare_text_success(self, mock_prepare):
        from pathlib import Path

        from ether_ocr_core.preparer import PreparationResult

        mock_prepare.return_value = PreparationResult(
            input_path=Path("/tmp/test.txt"),
            output_path=Path("/tmp/test.txt"),
            paragraphs=3,
            size_bytes=100,
            validation=ValidationResult(valid=True),
        )

        with patch.object(Path, "read_text", return_value="Clean text."):
            with patch.object(Path, "unlink"):
                response = self.client.post(
                    "/api/v1/prepare",
                    files={"file": ("test.txt", io.BytesIO(b"raw text"), "text/plain")},
                    data={"skip-validation": "true"},
                )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("text", data)
        self.assertEqual(data["metadata"]["paragraphs"], 3)

    def test_prepare_unsupported_extension(self):
        response = self.client.post(
            "/api/v1/prepare",
            files={
                "file": (
                    "doc.docx",
                    io.BytesIO(b"fake"),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
        self.assertEqual(response.status_code, 415)

    def test_prepare_openapi_registered(self):
        response = self.client.get("/openapi.json")
        schema = response.json()
        self.assertIn("/api/v1/prepare", schema["paths"])


class TestValidateEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        override_settings(_no_auth())
        cls.app = create_app()
        cls.client = TestClient(cls.app)

    def test_validate_valid_text(self):
        response = self.client.post(
            "/api/v1/validate",
            files={
                "file": (
                    "valid.txt",
                    io.BytesIO(b"Plain text.\n\nNo markdown here."),
                    "text/plain",
                )
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["valid"])
        self.assertEqual(data["issues"], [])

    def test_validate_markdown_rejected(self):
        response = self.client.post(
            "/api/v1/validate",
            files={
                "file": (
                    "bad.txt",
                    io.BytesIO(b"# Title\n\n## Subtitle\n\n[link](http://example.com)"),
                    "text/plain",
                )
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["valid"])
        self.assertGreater(len(data["issues"]), 0)

    def test_validate_non_utf8_rejected(self):
        response = self.client.post(
            "/api/v1/validate",
            files={
                "file": ("bad.bin", b"\xff\xfe\x00\x00", "application/octet-stream")
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("UTF-8", response.json()["detail"])

    def test_validate_openapi_registered(self):
        response = self.client.get("/openapi.json")
        schema = response.json()
        self.assertIn("/api/v1/validate", schema["paths"])


class TestAuth(unittest.TestCase):
    """Authentication tests — run with auth enabled."""

    @classmethod
    def setUpClass(cls):
        override_settings(_with_keys("test-key-123", "other-key-456"))
        cls.app = create_app()
        cls.client = TestClient(cls.app)

    def test_health_no_auth_required(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)

    def test_ocr_without_auth_returns_401(self):
        response = self.client.post(
            "/api/v1/ocr",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        self.assertEqual(response.status_code, 401)

    def test_ocr_with_valid_api_key(self):
        with patch("ether_ocr_api.routes.ocr.ocr_document") as mock_ocr:
            from pathlib import Path

            mock_ocr.return_value = OcrPipelineResult(
                input_path=Path("/tmp/t.txt"),
                output_path=Path("/tmp/t.txt"),
                pages=1,
                paragraphs=1,
                size_bytes=10,
                used_ocr=False,
                validation=ValidationResult(valid=True),
            )
            with patch.object(Path, "read_text", return_value="ok"):
                with patch.object(Path, "unlink"):
                    response = self.client.post(
                        "/api/v1/ocr",
                        files={
                            "file": ("test.txt", io.BytesIO(b"hello"), "text/plain")
                        },
                        headers={"X-API-Key": "test-key-123"},
                        data={"validate": "false"},
                    )
            self.assertEqual(response.status_code, 200)

    def test_ocr_with_invalid_api_key_returns_401(self):
        response = self.client.post(
            "/api/v1/ocr",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
            headers={"X-API-Key": "wrong-key"},
        )
        self.assertEqual(response.status_code, 401)

    def test_prepare_without_auth_returns_401(self):
        response = self.client.post(
            "/api/v1/prepare",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        self.assertEqual(response.status_code, 401)

    def test_validate_without_auth_returns_401(self):
        response = self.client.post(
            "/api/v1/validate",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
