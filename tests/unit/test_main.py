"""
Unit tests for main FastAPI application.

Tests the health check endpoints and basic app configuration.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: FastAPI test client instance
    """
    return TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint (upload page)."""

    def test_root_returns_200(self, client: TestClient) -> None:
        """
        Test that GET / returns HTTP 200 status.

        Args:
            client: FastAPI test client
        """
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_html(self, client: TestClient) -> None:
        """
        Test that GET / returns HTML content (upload page).

        Args:
            client: FastAPI test client
        """
        response = client.get("/")
        assert response.headers["content-type"].startswith("text/html")
        assert "<!DOCTYPE html>" in response.text
        assert "Fill - 2D Table Data Auto-Filling" in response.text

    def test_root_contains_upload_form(self, client: TestClient) -> None:
        """
        Test that GET / contains upload form elements.

        Args:
            client: FastAPI test client
        """
        response = client.get("/")
        assert 'id="fileInput"' in response.text
        assert 'id="uploadBtn"' in response.text
        assert 'id="message"' in response.text


class TestAppConfiguration:
    """Tests for application configuration."""

    def test_app_title(self) -> None:
        """Test that app has correct title."""
        assert app.title == "Fill API"

    def test_app_version(self) -> None:
        """Test that app has version set."""
        assert app.version == "0.1.0"

    def test_docs_endpoint_configured(self) -> None:
        """Test that Swagger docs endpoint is configured."""
        assert app.docs_url == "/docs"

    def test_redoc_endpoint_configured(self) -> None:
        """Test that ReDoc endpoint is configured."""
        assert app.redoc_url == "/redoc"


class TestCORSMiddleware:
    """Tests for CORS middleware configuration."""

    def test_cors_middleware_present(self, client: TestClient) -> None:
        """
        Test that CORS middleware is configured.

        Args:
            client: FastAPI test client
        """
        # Make an OPTIONS request to trigger CORS preflight
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        # CORS middleware should add the necessary headers
        assert "access-control-allow-origin" in response.headers


class TestDocsEndpoints:
    """Tests for API documentation endpoints."""

    def test_swagger_docs_accessible(self, client: TestClient) -> None:
        """
        Test that Swagger UI is accessible at /docs.

        Args:
            client: FastAPI test client
        """
        response = client.get("/docs")
        # FastAPI returns HTML for Swagger UI
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_redoc_accessible(self, client: TestClient) -> None:
        """
        Test that ReDoc is accessible at /redoc.

        Args:
            client: FastAPI test client
        """
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_openapi_schema_accessible(self, client: TestClient) -> None:
        """
        Test that OpenAPI schema is accessible at /openapi.json.

        Args:
            client: FastAPI test client
        """
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "Fill API"
        assert schema["info"]["version"] == "0.1.0"
