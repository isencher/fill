"""
Fill Application - Repository Layer

Database repository classes for persistent storage.
Replaces in-memory storage with PostgreSQL database persistence.
"""

from src.repositories.database import (
    DatabaseManager,
    get_db,
    get_db_manager,
    init_db,
    SessionLocal,
    engine,
)
from src.repositories.file_repository import FileRepository
from src.repositories.template_repository import TemplateRepository
from src.repositories.mapping_repository import MappingRepository
from src.repositories.job_repository import JobRepository, JobOutputRepository

__all__ = [
    # Database session management
    "DatabaseManager",
    "get_db",
    "get_db_manager",
    "init_db",
    "SessionLocal",
    "engine",
    # Repositories
    "FileRepository",
    "TemplateRepository",
    "MappingRepository",
    "JobRepository",
    "JobOutputRepository",
]
