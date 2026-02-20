"""
Centralized error handlers for the Fill API.

This module provides custom exception handlers that properly
log errors without leaking sensitive information.
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTPExceptions with proper logging.

    Args:
        request: The incoming request
        exc: The HTTPException that was raised

    Returns:
        JSONResponse with error details
    """
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions without leaking details.

    Args:
        request: The incoming request
        exc: The exception that was raised

    Returns:
        JSONResponse with generic error message
    """
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
