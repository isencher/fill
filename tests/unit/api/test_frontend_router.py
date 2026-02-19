"""
Unit tests for frontend router.

Tests HTML page serving endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_returns_html(self, client: TestClient) -> None:
        """Test that root endpoint returns HTML."""
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_root_contains_onboarding_or_index(self, client: TestClient) -> None:
        """Test that root returns onboarding or index page."""
        response = client.get("/")

        assert response.status_code == 200
        # Should contain HTML content
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text.lower()


class TestMappingPage:
    """Tests for GET /mapping endpoint."""

    def test_mapping_page_returns_html(self, client: TestClient) -> None:
        """Test that mapping page returns HTML."""
        response = client.get("/mapping")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_mapping_page_content(self, client: TestClient) -> None:
        """Test that mapping page has expected content."""
        response = client.get("/mapping")

        assert response.status_code == 200
        # Should contain HTML
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text.lower()


class TestTemplatesPage:
    """Tests for GET /templates.html endpoint."""

    def test_templates_page_returns_html(self, client: TestClient) -> None:
        """Test that templates.html returns HTML."""
        response = client.get("/templates.html")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_templates_page_content(self, client: TestClient) -> None:
        """Test that templates.html has expected content."""
        response = client.get("/templates.html")

        assert response.status_code == 200
        # Should contain HTML
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text.lower()


class TestMappingHtmlPage:
    """Tests for GET /mapping.html endpoint."""

    def test_mapping_html_page_returns_html(self, client: TestClient) -> None:
        """Test that mapping.html returns HTML."""
        response = client.get("/mapping.html")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_mapping_html_page_content(self, client: TestClient) -> None:
        """Test that mapping.html has expected content."""
        response = client.get("/mapping.html")

        assert response.status_code == 200
        # Should contain HTML
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text.lower()
