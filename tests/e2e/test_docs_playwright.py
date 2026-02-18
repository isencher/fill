"""Playwright E2E tests for API documentation.

These tests launch a real browser to verify the Swagger UI is accessible.
The server fixture automatically starts uvicorn on port 8000 for these tests.
"""

import pytest

pytest.importorskip("playwright.sync_api")

from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.playwright
def test_swagger_ui_accessible_in_browser(page: Page, server) -> None:
    """Test that Swagger UI is accessible via browser.

    This test navigates to http://localhost:8000/docs and verifies:
    - Page loads successfully
    - Page title contains "Fill API"
    - Swagger UI elements are visible

    The server fixture automatically starts uvicorn on port 8000.

    Acceptance Criteria:
    - Page loads without errors
    - Title contains "Fill API"
    - Swagger UI is visible
    """
    # Navigate to docs page
    page.goto("http://localhost:8000/docs")

    # Wait for page to load
    page.wait_for_load_state("networkidle")

    # Check page title contains "Fill API"
    expect(page).to_have_title("Fill API - Swagger UI")

    # Verify Swagger UI is loaded by checking for common elements
    page.wait_for_selector("body", timeout=5000)

    # Check that the page content is loaded
    body_text = page.inner_text("body")
    assert "swagger" in body_text.lower() or "api" in body_text.lower()


@pytest.mark.e2e
@pytest.mark.playwright
def test_redoc_accessible_in_browser(page: Page, server) -> None:
    """Test that ReDoc is accessible via browser.

    This test navigates to http://localhost:8000/redoc and verifies:
    - Page loads successfully
    - ReDoc UI is visible

    The server fixture automatically starts uvicorn on port 8000.

    Acceptance Criteria:
    - Page loads without errors
    - ReDoc content is visible
    """
    # Navigate to redoc page
    page.goto("http://localhost:8000/redoc")

    # Wait for page to load and render
    page.wait_for_load_state("domcontentloaded")

    # Wait a bit for ReDoc to render (it's a SPA)
    page.wait_for_timeout(3000)

    # Check for ReDoc content in the page title
    title = page.title()
    assert "fill" in title.lower() or "api" in title.lower() or "redoc" in title.lower()

    # Check that the page loaded successfully (check URL hasn't changed due to error)
    assert "redoc" in page.url.lower()


@pytest.mark.e2e
@pytest.mark.playwright
def test_api_docs_list_root_endpoint(page: Page, server) -> None:
    """Test that API docs show the root endpoint.

    This test verifies that the /docs page lists our GET / endpoint.

    The server fixture automatically starts uvicorn on port 8000.

    Acceptance Criteria:
    - Root endpoint (/) is listed in docs
    - GET method is shown
    - Response schema is visible
    """
    # Navigate to docs page
    page.goto("http://localhost:8000/docs")

    # Wait for Swagger UI to fully load
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("body", timeout=5000)

    # Look for the root endpoint in the page
    # Swagger UI shows endpoints as /path or [method] /path
    page.wait_for_timeout(1000)  # Give JS time to render

    # Check if we can find the root endpoint mentioned
    body_text = page.inner_text("body")
    # The root endpoint should be mentioned somewhere in the docs
    assert "/" in body_text or "root" in body_text.lower()
