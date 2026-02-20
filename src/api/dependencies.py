"""
Shared dependencies for API routers.

This module provides FastAPI dependency functions for shared service instances.
All routers should use these dependencies to access services.
"""

from datetime import timedelta
from typing import Generator

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.repositories.database import get_db
from src.services.file_storage import FileStorage, get_file_storage
from src.services.template_store import get_template_store
from src.services.output_storage import get_output_storage
from src.config.settings import settings


# Initialize singleton service instances with settings
_file_storage: FileStorage = get_file_storage()
# Re-initialize with settings-based TTL as timedelta
_file_storage._ttl = timedelta(hours=settings.upload_ttl_hours)

_template_store = get_template_store()
_output_storage = get_output_storage()


async def file_storage() -> Generator:
    """
    Dependency to get the shared file storage service.

    Yields:
        FileStorage: The singleton file storage instance
    """
    yield _file_storage


async def template_store() -> Generator:
    """
    Dependency to get the shared template store service.

    Yields:
        TemplateStore: The singleton template store instance
    """
    yield _template_store


async def output_storage() -> Generator:
    """
    Dependency to get the shared output storage service.

    Yields:
        OutputStorage: The singleton output storage instance
    """
    yield _output_storage


# Re-export database session dependency
def database() -> Generator:
    """
    Dependency to get a database session.

    Yields:
        Session: SQLAlchemy database session
    """
    db_gen = get_db()
    yield from db_gen


async def validate_uuid(id_str: str, field_name: str = "ID") -> UUID:
    """
    Validate and convert UUID string.

    Args:
        id_str: The UUID string to validate
        field_name: Name of the field for error messages

    Returns:
        The validated UUID object

    Raises:
        HTTPException: 404 if the UUID format is invalid
    """
    try:
        return UUID(id_str)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid {field_name} format"
        )


# Export service instances for backward compatibility
__all__ = [
    "file_storage",
    "template_store",
    "output_storage",
    "database",
    "get_db",
    "_file_storage",
    "_template_store",
    "_output_storage",
    "validate_uuid",
]
