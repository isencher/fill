"""
Fill API module.

This module provides a modular API structure using FastAPI's APIRouter.
The main application is created here with all routers registered.

Backward compatibility: This module exports the same symbols that were previously
available from src.main, allowing existing imports to continue working.
"""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.repositories.database import init_db
from src.api.dependencies import _file_storage, _template_store, _output_storage
from src.api.routers import (
    upload_router,
    templates_router,
    mappings_router,
    outputs_router,
    frontend_router,
)


# Initialize database on module load
init_db()

# Create FastAPI application instance
app = FastAPI(
    title="Fill API",
    description="2D Table Data Auto-Filling Web Application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware for development and production
# Use ALLOWED_ORIGINS env var for production (comma-separated list)
# Default: http://localhost:8000,http://localhost:3000 for development
_allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in _allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
