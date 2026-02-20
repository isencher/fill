"""
Cleanup middleware for automatic file storage cleanup.

This middleware triggers cleanup of expired files after each request
with minimal overhead.
"""

from fastapi import Request

from src.api.dependencies import _file_storage


async def cleanup_middleware(request: Request, call_next):
    """
    Middleware that triggers cleanup of expired files.

    This runs after each request to clean up expired files from
    in-memory storage, preventing memory leaks.

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        The response from the next handler
    """
    response = await call_next(request)
    # Trigger cleanup after each request (low overhead)
    _file_storage.cleanup_expired()
    return response
