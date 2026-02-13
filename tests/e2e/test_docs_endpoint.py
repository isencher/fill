"""E2E tests for API documentation endpoint.

This test module verifies that the Swagger UI documentation is accessible.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_docs_endpoint_returns_html() -> None:
    """Test that GET /docs endpoint returns HTML content.

    FastAPI auto-generates Swagger UI at /docs.
    This test verifies the endpoint is accessible and returns HTML.

    Acceptance Criteria:
    - Endpoint returns 200 status
    - Content-Type is HTML
    - Response contains Swagger UI indicators
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "").lower()
        # Verify it's the Swagger UI
        text = response.text
        assert "swagger" in text.lower() or "redoc" in text.lower()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_redoc_endpoint_returns_html() -> None:
    """Test that GET /redoc endpoint returns HTML content.

    FastAPI also provides ReDoc documentation at /redoc.
    This test verifies the endpoint is accessible.

    Acceptance Criteria:
    - Endpoint returns 200 status
    - Content-Type is HTML
    - Response contains ReDoc indicators
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/redoc")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "").lower()
        # Verify it's ReDoc
        text = response.text
        assert "redoc" in text.lower()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_openapi_json_endpoint() -> None:
    """Test that GET /openapi.json returns OpenAPI schema.

    FastAPI generates the OpenAPI schema at /openapi.json.
    This test verifies the schema is accessible and valid.

    Acceptance Criteria:
    - Endpoint returns 200 status
    - Content-Type is JSON
    - Response contains required OpenAPI fields
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")

        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

        schema = response.json()
        # Verify OpenAPI schema structure
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert schema["info"]["title"] == "fill"
        assert schema["info"]["version"] == "0.1.0"
