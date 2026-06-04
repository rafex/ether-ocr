"""Integration tests for the ether-ocr REST API."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from ether_ocr.api.server import create_app


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


if __name__ == "__main__":
    unittest.main()
