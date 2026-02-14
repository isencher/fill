"""
Fill Application - Database Session Manager

Provides centralized database session management for the application.
Handles engine creation, session lifecycle, and initialization.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from migrations import Base

# Default database URL (PostgreSQL in Docker)
# Can be overridden via DATABASE_URL environment variable
DEFAULT_DATABASE_URL = "postgresql://fill_user:fill_password@localhost:5432/fill_db"

# Database URL from environment or default
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Create SQLAlchemy engine
# pool_pre_ping=True checks connection health before use
# echo=False disables SQL query logging (enable for debugging)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseManager:
    """
    Database connection manager.

    Provides methods for initializing the database schema
    and managing database sessions.
    """

    def __init__(self, database_url: str | None = None) -> None:
        """
        Initialize the database manager.

        Args:
            database_url: Optional database URL. Uses DATABASE_URL env var or default if not provided.
        """
        self.database_url = database_url or DATABASE_URL

    def init_db(self) -> None:
        """
        Initialize the database schema.

        Creates all tables defined in the SQLAlchemy models.
        This is idempotent - safe to call multiple times.
        """
        Base.metadata.create_all(bind=engine)

    def drop_all(self) -> None:
        """
        Drop all database tables.

        WARNING: This deletes all data. Use only for testing or development.
        """
        Base.metadata.drop_all(bind=engine)

    def reset_db(self) -> None:
        """
        Reset the database schema.

        Drops all tables and recreates them.
        WARNING: This deletes all data.
        """
        self.drop_all()
        self.init_db()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session context manager.

        Automatically handles session cleanup (commit/rollback/close).

        Yields:
            Session: SQLAlchemy session object

        Example:
            with db_manager.get_session() as session:
                file = FileRepository(session).get_file_by_id(file_id)
        """
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database manager instance
_db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """
    Get the global database manager instance.

    Returns:
        DatabaseManager: The singleton database manager
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def init_db() -> None:
    """
    Initialize the database schema.

    Creates all tables defined in the SQLAlchemy models.
    Uses the global database manager.
    """
    get_db_manager().init_db()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session injection.

    Provides a database session to endpoint handlers.
    Automatically handles session cleanup.

    Yields:
        Session: SQLAlchemy session for the request

    Example:
        @app.get("/files/{file_id}")
        def get_file(file_id: str, db: Session = Depends(get_db)):
            file = FileRepository(db).get_file_by_id(file_id)
            return file
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
