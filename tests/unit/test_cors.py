"""Integration tests for CORS middleware and server configuration."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


def test_cors_headers_present_on_root_request() -> None:
    """Test that CORS headers are present in API responses.

    Verifies the CORS middleware is properly configured.
    Following TDD: Red -> Green -> Refactor
    """
    client = TestClient(app)
    # Make a request with an allowed Origin header to trigger CORS
    # Using localhost:8000 which is in ALLOWED_ORIGINS
    response = client.get("/", headers={"Origin": "http://localhost:8000"})

    assert response.status_code == 200
    # Check for CORS headers
    assert "access-control-allow-origin" in response.headers
    assert "http://localhost:8000" in response.headers["access-control-allow-origin"]


def test_cors_preflight_request() -> None:
    """Test CORS preflight OPTIONS request.

    Verifies that preflight requests are handled correctly.
    """
    client = TestClient(app)
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "GET",
        },
    )

    # Preflight should succeed
    assert response.status_code == 200 or response.status_code == 204


def test_server_has_expected_routes() -> None:
    """Test that server is configured with expected routes.

    Verifies the application routing is properly set up.
    """
    # Get all route paths
    route_paths = [route.path for route in app.routes]

    # Verify root endpoint exists
    assert "/" in route_paths


def test_app_metadata_configured() -> None:
    """Test that FastAPI app has proper metadata.

    Verifies app title, description, and version are set.
    """
    assert app.title == "Fill API"
    assert app.version == "0.1.0"
    # Description mentions auto-filling functionality
    assert "filling" in app.description.lower() or "auto" in app.description.lower()
