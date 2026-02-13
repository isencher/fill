"""First failing test - skeleton test to verify main app import."""

import pytest


def test_main_app_exists():
    """Test that main app module can be imported.

    This is expected to fail initially because main.py doesn't exist yet.
    Following TDD: Red -> Green -> Refactor
    """
    from src.main import app

    assert app is not None
    assert hasattr(app, "routes")
