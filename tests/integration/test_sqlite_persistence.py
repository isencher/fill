"""
Integration tests for SQLite persistence layer.

Tests that data is properly persisted to SQLite database
and survives application restarts.
"""

import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from migrations import Base, File, Template, Mapping, Job
from src.repositories.database import DatabaseManager
from src.repositories.file_repository import FileRepository
from src.repositories.template_repository import TemplateRepository
from src.repositories.mapping_repository import MappingRepository


@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    # Create temp file in a temp directory that will be cleaned up automatically
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test.db")
    yield db_path
    # Cleanup - use a loop to handle Windows file locking
    import shutil
    import gc
    import time

    # Force garbage collection to close any remaining connections
    gc.collect()

    # Try multiple times with delays to handle Windows file locking
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
            break
        except PermissionError:
            if attempt < max_attempts - 1:
                # Wait longer on each attempt
                time.sleep(0.5 * (attempt + 1))
                gc.collect()
            else:
                # Final attempt - log but don't fail the test
                print(f"Warning: Could not cleanup temp directory {tmpdir}")
                pass


@pytest.fixture
def db_manager(temp_db_path):
    """Create a DatabaseManager with SQLite."""
    db_url = f"sqlite:///{temp_db_path}"
    manager = DatabaseManager(database_url=db_url)
    manager.init_db()
    return manager


@pytest.fixture
def db_session(db_manager) -> Session:
    """Create a database session."""
    with db_manager.get_session() as session:
        yield session


class TestSQLitePersistence:
    """Test data persistence with SQLite."""

    def test_database_file_created(self, temp_db_path, db_manager):
        """Test that database file is created on init."""
        assert os.path.exists(temp_db_path)
        assert os.path.getsize(temp_db_path) > 0

    def test_file_persistence(self, temp_db_path, db_manager):
        """Test that files are persisted to SQLite."""
        # Create a file
        with db_manager.get_session() as session:
            repo = FileRepository(session)
            file_record = repo.create_file(
                filename="test.csv",
                content_type="text/csv",
                size=1024,
                file_path="/uploads/test.csv",
                status="uploaded",
            )
            file_id = file_record.id

        # Verify file exists in new session
        with db_manager.get_session() as session:
            repo = FileRepository(session)
            retrieved = repo.get_file_by_id(file_id)
            assert retrieved is not None
            assert retrieved.filename == "test.csv"
            assert retrieved.content_type == "text/csv"
            assert retrieved.size == 1024

    def test_template_persistence(self, temp_db_path, db_manager):
        """Test that templates are persisted to SQLite."""
        # Create a template
        with db_manager.get_session() as session:
            repo = TemplateRepository(session)
            template = repo.create_template(
                name="Invoice Template",
                placeholders=["invoice_number", "date", "total"],
                file_path="/templates/invoice.docx",
                description="Standard invoice template",
            )
            template_id = template.id

        # Verify template exists in new session
        with db_manager.get_session() as session:
            repo = TemplateRepository(session)
            retrieved = repo.get_template_by_id(template_id)
            assert retrieved is not None
            assert retrieved.name == "Invoice Template"
            assert json.loads(retrieved.placeholders) == ["invoice_number", "date", "total"]

    def test_mapping_persistence(self, temp_db_path, db_manager):
        """Test that mappings are persisted to SQLite."""
        # Create related records
        with db_manager.get_session() as session:
            file_repo = FileRepository(session)
            template_repo = TemplateRepository(session)
            mapping_repo = MappingRepository(session)

            file_record = file_repo.create_file(
                filename="data.csv",
                content_type="text/csv",
                size=2048,
                file_path="/uploads/data.csv",
            )
            template = template_repo.create_template(
                name="Letter Template",
                placeholders=["name", "address"],
                file_path="/templates/letter.docx",
            )

            mapping = mapping_repo.create_mapping(
                file_id=file_record.id,
                template_id=template.id,
                column_mappings={"Customer Name": "name", "Customer Address": "address"},
            )
            mapping_id = mapping.id

        # Verify mapping exists in new session
        with db_manager.get_session() as session:
            mapping_repo = MappingRepository(session)
            retrieved = mapping_repo.get_mapping_by_id(mapping_id)
            assert retrieved is not None
            assert json.loads(retrieved.column_mappings) == {
                "Customer Name": "name",
                "Customer Address": "address",
            }

    def test_data_survives_session_close(self, temp_db_path):
        """Test that data survives after all sessions are closed (simulating restart)."""
        db_url = f"sqlite:///{temp_db_path}"
        
        # First "application run" - create data
        manager1 = DatabaseManager(database_url=db_url)
        manager1.init_db()
        
        with manager1.get_session() as session:
            repo = FileRepository(session)
            file_record = repo.create_file(
                filename="survivor.csv",
                content_type="text/csv",
                size=512,
                file_path="/uploads/survivor.csv",
            )
            file_id = file_record.id

        # Second "application run" - verify data still exists
        manager2 = DatabaseManager(database_url=db_url)
        # Don't init_db - just connect to existing database
        
        with manager2.get_session() as session:
            repo = FileRepository(session)
            retrieved = repo.get_file_by_id(file_id)
            assert retrieved is not None
            assert retrieved.filename == "survivor.csv"

    def test_multiple_records_persistence(self, temp_db_path, db_manager):
        """Test persisting multiple records of different types."""
        file_ids = []
        template_ids = []

        # Create multiple files
        with db_manager.get_session() as session:
            repo = FileRepository(session)
            for i in range(5):
                file_record = repo.create_file(
                    filename=f"file{i}.csv",
                    content_type="text/csv",
                    size=100 * i,
                    file_path=f"/uploads/file{i}.csv",
                )
                file_ids.append(file_record.id)

        # Create multiple templates
        with db_manager.get_session() as session:
            repo = TemplateRepository(session)
            for i in range(3):
                template = repo.create_template(
                    name=f"Template {i}",
                    placeholders=[f"field{i}_a", f"field{i}_b"],
                    file_path=f"/templates/template{i}.docx",
                )
                template_ids.append(template.id)

        # Verify all files persisted
        with db_manager.get_session() as session:
            repo = FileRepository(session)
            files = repo.list_files(limit=10)
            assert len(files) == 5

        # Verify all templates persisted
        with db_manager.get_session() as session:
            repo = TemplateRepository(session)
            templates = repo.list_templates()
            assert len(templates) == 3

    def test_update_operations_persisted(self, temp_db_path, db_manager):
        """Test that update operations are persisted."""
        # Create a file
        with db_manager.get_session() as session:
            repo = FileRepository(session)
            file_record = repo.create_file(
                filename="original.csv",
                content_type="text/csv",
                size=100,
                file_path="/uploads/original.csv",
                status="pending",
            )
            file_id = file_record.id

        # Update the file
        with db_manager.get_session() as session:
            repo = FileRepository(session)
            updated = repo.update_file_status(file_id, "completed")
            assert updated is not None
            assert updated.status == "completed"

        # Verify update persisted in new session
        with db_manager.get_session() as session:
            repo = FileRepository(session)
            retrieved = repo.get_file_by_id(file_id)
            assert retrieved.status == "completed"

    def test_delete_operations_persisted(self, temp_db_path, db_manager):
        """Test that delete operations are persisted."""
        # Create a file
        with db_manager.get_session() as session:
            repo = FileRepository(session)
            file_record = repo.create_file(
                filename="to_delete.csv",
                content_type="text/csv",
                size=100,
                file_path="/uploads/to_delete.csv",
            )
            file_id = file_record.id

        # Delete the file
        with db_manager.get_session() as session:
            repo = FileRepository(session)
            assert repo.delete_file(file_id) is True

        # Verify deletion persisted in new session
        with db_manager.get_session() as session:
            repo = FileRepository(session)
            retrieved = repo.get_file_by_id(file_id)
            assert retrieved is None


class TestSQLiteSpecificFeatures:
    """Test SQLite-specific behaviors."""

    def test_sqlite_connection_args(self, temp_db_path):
        """Test that SQLite connection uses correct arguments."""
        db_url = f"sqlite:///{temp_db_path}"

        # Should not raise error with check_same_thread=False
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False}
        )

        # Create tables first
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)

        # Should work from different threads (simulated by multiple sessions)
        session1 = Session()
        session2 = Session()

        # Both sessions should work
        result1 = session1.query(File).count()
        result2 = session2.query(File).count()

        session1.close()
        session2.close()

    def test_data_directory_creation(self):
        """Test that data directory is created automatically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "subdir" / "data" / "fill.db"
            db_url = f"sqlite:///./data/fill.db"

            # Directory should not exist yet
            assert not db_path.parent.exists()

            # Creating DatabaseManager with a relative path should create directory
            # Use absolute path for testing
            abs_db_path = Path(tmpdir) / "subdir" / "data" / "test.db"
            abs_db_url = f"sqlite:///{abs_db_path}"

            manager = DatabaseManager(database_url=abs_db_url)

            # Now directory should exist
            assert abs_db_path.parent.exists()
