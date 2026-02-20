"""
Request logging middleware for the Fill API.

This middleware logs all incoming requests and their responses
for debugging and monitoring purposes.
"""

from fastapi import Request
import logging

logger = logging.getLogger(__name__)


async def request_logging_middleware(request: Request, call_next):
    """
    Middleware that logs all requests and responses.

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        The response from the next handler
    """
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response
