"""
API router module exports.

This module exports all API routers for easy inclusion in the main application.
"""

from src.api.routers.upload import router as upload_router
from src.api.routers.templates import router as templates_router
from src.api.routers.mappings import router as mappings_router
from src.api.routers.outputs import router as outputs_router
from src.api.routers.frontend import router as frontend_router


__all__ = [
    "upload_router",
    "templates_router",
    "mappings_router",
    "outputs_router",
    "frontend_router",
]
