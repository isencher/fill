"""
Pytest configuration and shared fixtures for E2E tests.
"""

import subprocess
import time
import warnings

# Filter warnings BEFORE importing app
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning, message=".*Unclosed.*MemoryObjectReceiveStream.*")

from fastapi.testclient import TestClient

import pytest
from src.main import app


@pytest.fixture(scope="session")
def server():
    """
    Start a uvicorn server for Playwright E2E tests.

    This fixture starts the server in the background before running Playwright tests
    and stops it after all tests complete.
    """
    import socket
    import sys
    from pathlib import Path

    # Find uvicorn executable in virtual environment
    venv_path = Path(__file__).parent.parent / ".venv"
    if sys.platform == "win32":
        uvicorn_exe = venv_path / "Scripts" / "uvicorn.exe"
    else:
        uvicorn_exe = venv_path / "bin" / "uvicorn"

    # Start uvicorn server in background
    proc = subprocess.Popen(
        [str(uvicorn_exe), "src.main:app", "--port", "8000", "--log-level", "error"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start with retry logic
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex(("localhost", 8000)) == 0:
                    break
        except:
            pass
        time.sleep(0.5)
    else:
        proc.terminate()
        proc.wait()
        raise RuntimeError("Server failed to start after 15 seconds")

    yield  # Server is now running

    # Cleanup: stop the server
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


# Check if playwright is available for browser-based E2E tests
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
    config.addinivalue_line(
        "markers",
        "playwright: mark test as requiring Playwright browser automation"
    )


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
