"""Main FastAPI application entry point for fill."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI application instance
app = FastAPI(
    title="fill",
    description="A web application for automatically filling 2D table data into template files",
    version="0.1.0",
)

# Configure CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    """Root health check endpoint.

    Returns:
        A dictionary with status indicator.
    """
    return {"status": "ok"}
