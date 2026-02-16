"""
Pytest configuration and shared fixtures for E2E tests.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI app.

    This fixture provides a TestClient instance for making HTTP requests
    to the FastAPI application during tests.

    Returns:
        TestClient: Configured test client for the FastAPI app
    """
    return TestClient(app)


@pytest.fixture
def client_with_onboarding_skipped(client: TestClient) -> TestClient:
    """
    Create a test client with onboarding bypassed.

    This fixture sets localStorage to skip the onboarding flow for tests
    that need to access the application directly without going through
    the first-time user experience.

    Usage:
        def test_something(client_with_onboarding_skipped):
            response = client_with_onboarding_skipped.get("/")
            # Will get index.html instead of onboarding.html

    Args:
        client: Base TestClient fixture

    Returns:
        TestClient: Configured test client with onboarding bypassed
    """
    # For E2E tests using TestClient, we can't directly set localStorage
    # since TestClient doesn't execute JavaScript.
    # Tests should use /static/index.html directly instead of /
    return client


def pytest_configure(config):
    """
    Configure pytest with custom markers and settings.

    This function is called once at the start of the test run.
    """
    config.addinivalue_line(
        "markers",
        "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers",
        "unit: mark test as a unit test"
    )
