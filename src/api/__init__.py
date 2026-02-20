"""
Fill API module.

This module provides a modular API structure using FastAPI's APIRouter.
The main application is created here with all routers registered.

Backward compatibility: This module exports the same symbols that were previously
available from src.main, allowing existing imports to continue working.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException

from src.repositories.database import init_db
from src.api.dependencies import _file_storage, _template_store, _output_storage
from src.api.routers import (
    upload_router,
    templates_router,
    mappings_router,
    outputs_router,
    frontend_router,
)
from src.api.middleware import cleanup_middleware, request_logging_middleware
from src.api.errors import http_exception_handler, generic_exception_handler
from src.config.settings import settings
from src.config.logging import setup_logging


# Initialize logging
setup_logging()

# Initialize database on module load
init_db()

# Create FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    description="2D Table Data Auto-Filling Web Application",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Add middleware
app.middleware("http")(request_logging_middleware)
app.middleware("http")(cleanup_middleware)

# Configure CORS middleware for development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Register all routers
app.include_router(upload_router)
app.include_router(templates_router)
app.include_router(mappings_router)
app.include_router(outputs_router)
app.include_router(frontend_router)


# Export for backward compatibility
# These allow existing code that imports from src.main to continue working
__all__ = [
    "app",
    "_file_storage",
    "_template_store",
    "_output_storage",
]
