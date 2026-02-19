"""
Fill Application - 2D Table Data Auto-Filling Web Application

Main FastAPI application entry point.

This file now serves as a thin wrapper around the modular API structure.
All route definitions have been moved to src/api/routers/ for better organization.

For backward compatibility, this file re-exports all symbols that were previously
defined here.
"""

# Import the application and all shared symbols from the new modular structure
from src.api import (
    app,
    _file_storage,
    _template_store,
    _output_storage,
)

# Re-export everything for backward compatibility
# This allows existing code like `from src.main import app` to continue working
__all__ = [
    "app",
    "_file_storage",
    "_template_store",
    "_output_storage",
]
