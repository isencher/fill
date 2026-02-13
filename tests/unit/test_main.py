"""Unit tests for main FastAPI application."""

from fastapi.testclient import TestClient

from src.main import app


def test_main_app_exists() -> None:
    """Test that main app module can be imported.

    This test was originally the failing skeleton test. Now it passes.
    Following TDD: Red -> Green -> Refactor
    """
    assert app is not None
    assert hasattr(app, "routes")


def test_get_root_returns_status_ok() -> None:
    """Test that GET / endpoint returns 200 status and correct response."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint_response_structure() -> None:
    """Test that root endpoint response has correct structure."""
    client = TestClient(app)
    response = client.get("/")
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert data["status"] == "ok"
