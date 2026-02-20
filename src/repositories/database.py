"""
Fill Application - Database Session Manager

Provides centralized database session management for the application.
Handles engine creation, session lifecycle, and initialization.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from migrations import Base
from src.config.settings import settings

# Database URL from settings
DATABASE_URL = settings.database_url

# Ensure data directory exists for SQLite
if DATABASE_URL.startswith("sqlite:///./"):
    db_path = DATABASE_URL.replace("sqlite:///./", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

# Create SQLAlchemy engine
# pool_pre_ping=True checks connection health before use
# echo=False disables SQL query logging (enable for debugging)
# check_same_thread=False required for SQLite in FastAPI (multiple threads)
engine_args = {
    "pool_pre_ping": True,
    "echo": False,
    "pool_size": settings.pool_size,
    "max_overflow": settings.max_overflow,
    "pool_timeout": settings.pool_timeout,
    "pool_recycle": settings.pool_recycle,
}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)

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
            database_url: Optional database URL. Uses settings if not provided.
        """
        self.database_url = database_url or DATABASE_URL

        # Create engine and session factory for this manager
        engine_args = {
            "pool_pre_ping": True,
            "echo": False,
            "pool_size": settings.pool_size,
            "max_overflow": settings.max_overflow,
            "pool_timeout": settings.pool_timeout,
            "pool_recycle": settings.pool_recycle,
        }
        if self.database_url.startswith("sqlite"):
            engine_args["connect_args"] = {"check_same_thread": False}

            # Ensure data directory exists for SQLite
            # Handle both relative (sqlite:///./path) and absolute (sqlite:///path) URLs
            db_path = self.database_url.replace("sqlite:///", "")
            if db_path and db_path != ":memory:":
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self._engine = create_engine(self.database_url, **engine_args)
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )

    def init_db(self) -> None:
        """
        Initialize the database schema.

        Creates all tables defined in the SQLAlchemy models.
        This is idempotent - safe to call multiple times.
        """
        Base.metadata.create_all(bind=self._engine)

    def drop_all(self) -> None:
        """
        Drop all database tables.

        WARNING: This deletes all data. Use only for testing or development.
        """
        Base.metadata.drop_all(bind=self._engine)

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
        session = self._session_factory()
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
    Automatically handles session commit/rollback and cleanup.

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
        session.commit()  # Auto-commit on successful request
    except Exception:
        session.rollback()  # Rollback on error
        raise
    finally:
        session.close()
