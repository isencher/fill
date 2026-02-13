"""pytest configuration and fixtures for fill application."""

import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "fixtures"
