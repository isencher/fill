"""
Shared dependencies for API routers.

This module provides FastAPI dependency functions for shared service instances.
All routers should use these dependencies to access services.
"""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.repositories.database import get_db
from src.services.file_storage import get_file_storage
from src.services.template_store import get_template_store
from src.services.output_storage import get_output_storage


# Initialize singleton service instances
_file_storage = get_file_storage()
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
]
