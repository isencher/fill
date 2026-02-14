"""
Integration Tests for Repository Layer

Tests all repository classes with an in-memory SQLite database
to ensure database operations work correctly.
"""

import json
from datetime import datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from migrations import Base, File, Template, Mapping, Job, JobOutput
from src.repositories.database import DatabaseManager
from src.repositories.file_repository import FileRepository
from src.repositories.template_repository import TemplateRepository
from src.repositories.mapping_repository import MappingRepository
from src.repositories.job_repository import JobRepository, JobOutputRepository


# Fixtures
@pytest.fixture
def in_memory_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return engine, TestingSessionLocal


@pytest.fixture
def db_session(in_memory_db):
    """Create a database session for testing."""
    engine, TestingSessionLocal = in_memory_db
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# FileRepository Tests
class TestFileRepository:
    """Test FileRepository CRUD operations."""

    def test_create_file(self, db_session: Session):
        """Test creating a file record."""
        repo = FileRepository(db_session)
        file_record = repo.create_file(
            filename="test.csv",
            content_type="text/csv",
            size=1024,
            file_path="/tmp/test.csv",
            status="pending",
        )

        assert file_record.id is not None
        assert file_record.filename == "test.csv"
        assert file_record.content_type == "text/csv"
        assert file_record.size == 1024
        assert file_record.file_path == "/tmp/test.csv"
        assert file_record.status == "pending"
        assert file_record.uploaded_at is not None

    def test_get_file_by_id(self, db_session: Session):
        """Test retrieving file by ID."""
        repo = FileRepository(db_session)
        created = repo.create_file(
            filename="test.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=2048,
            file_path="/tmp/test.xlsx",
        )

        retrieved = repo.get_file_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.filename == "test.xlsx"

    def test_get_file_by_id_not_found(self, db_session: Session):
        """Test retrieving non-existent file."""
        repo = FileRepository(db_session)
        retrieved = repo.get_file_by_id(uuid4())
        assert retrieved is None

    def test_list_files_empty(self, db_session: Session):
        """Test listing files when database is empty."""
        repo = FileRepository(db_session)
        files = repo.list_files()
        assert files == []

    def test_list_files_with_data(self, db_session: Session):
        """Test listing files with multiple records."""
        repo = FileRepository(db_session)
        repo.create_file("test1.csv", "text/csv", 100, "/tmp/test1.csv")
        repo.create_file("test2.xlsx", "application/vnd.ms-excel", 200, "/tmp/test2.csv")
        repo.create_file("test3.csv", "text/csv", 300, "/tmp/test3.csv")

        files = repo.list_files(limit=10)
        assert len(files) == 3
        # Should be sorted by uploaded_at descending
        assert files[0].filename == "test3.csv"

    def test_list_files_with_status_filter(self, db_session: Session):
        """Test listing files with status filter."""
        repo = FileRepository(db_session)
        repo.create_file("pending.csv", "text/csv", 100, "/tmp/pending.csv", "pending")
        repo.create_file("completed.csv", "text/csv", 200, "/tmp/completed.csv", "completed")
        repo.create_file("failed.csv", "text/csv", 300, "/tmp/failed.csv", "pending")

        files = repo.list_files(status="pending")
        assert len(files) == 2
        assert all(f.status == "pending" for f in files)

    def test_list_files_with_pagination(self, db_session: Session):
        """Test listing files with pagination."""
        repo = FileRepository(db_session)
        for i in range(5):
            repo.create_file(f"test{i}.csv", "text/csv", 100 * i, f"/tmp/test{i}.csv")

        files_page1 = repo.list_files(limit=2, offset=0)
        assert len(files_page1) == 2

        files_page2 = repo.list_files(limit=2, offset=2)
        assert len(files_page2) == 2

        files_page3 = repo.list_files(limit=2, offset=4)
        assert len(files_page3) == 1

    def test_count_files(self, db_session: Session):
        """Test counting files."""
        repo = FileRepository(db_session)
        assert repo.count_files() == 0

        repo.create_file("test1.csv", "text/csv", 100, "/tmp/test1.csv")
        repo.create_file("test2.csv", "text/csv", 200, "/tmp/test2.csv")
        assert repo.count_files() == 2

    def test_count_files_with_status(self, db_session: Session):
        """Test counting files with status filter."""
        repo = FileRepository(db_session)
        repo.create_file("test1.csv", "text/csv", 100, "/tmp/test1.csv", "pending")
        repo.create_file("test2.csv", "text/csv", 200, "/tmp/test2.csv", "completed")
        repo.create_file("test3.csv", "text/csv", 300, "/tmp/test3.csv", "pending")

        assert repo.count_files(status="pending") == 2
        assert repo.count_files(status="completed") == 1

    def test_update_file_status(self, db_session: Session):
        """Test updating file status."""
        repo = FileRepository(db_session)
        file_record = repo.create_file("test.csv", "text/csv", 100, "/tmp/test.csv", "pending")

        updated = repo.update_file_status(file_record.id, "completed")
        assert updated is not None
        assert updated.status == "completed"

    def test_update_file_status_not_found(self, db_session: Session):
        """Test updating status for non-existent file."""
        repo = FileRepository(db_session)
        updated = repo.update_file_status(uuid4(), "completed")
        assert updated is None

    def test_delete_file(self, db_session: Session):
        """Test deleting file."""
        repo = FileRepository(db_session)
        file_record = repo.create_file("test.csv", "text/csv", 100, "/tmp/test.csv")

        assert repo.delete_file(file_record.id) is True
        assert repo.get_file_by_id(file_record.id) is None

    def test_delete_file_not_found(self, db_session: Session):
        """Test deleting non-existent file."""
        repo = FileRepository(db_session)
        assert repo.delete_file(uuid4()) is False


# TemplateRepository Tests
class TestTemplateRepository:
    """Test TemplateRepository CRUD operations."""

    def test_create_template(self, db_session: Session):
        """Test creating a template record."""
        repo = TemplateRepository(db_session)
        template = repo.create_template(
            name="Invoice Template",
            placeholders=["invoice_number", "date", "total"],
            file_path="/templates/invoice.docx",
            description="Invoice generation template",
        )

        assert template.id is not None
        assert template.name == "Invoice Template"
        assert template.description == "Invoice generation template"
        assert json.loads(template.placeholders) == ["invoice_number", "date", "total"]
        assert template.file_path == "/templates/invoice.docx"
        assert template.created_at is not None

    def test_get_template_by_id(self, db_session: Session):
        """Test retrieving template by ID."""
        repo = TemplateRepository(db_session)
        created = repo.create_template(
            name="Test Template",
            placeholders=["field1"],
            file_path="/templates/test.docx",
        )

        retrieved = repo.get_template_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Template"

    def test_get_template_by_name(self, db_session: Session):
        """Test retrieving template by name."""
        repo = TemplateRepository(db_session)
        repo.create_template(
            name="Unique Template",
            placeholders=["field1"],
            file_path="/templates/unique.docx",
        )

        retrieved = repo.get_template_by_name("Unique Template")
        assert retrieved is not None
        assert retrieved.name == "Unique Template"

    def test_list_templates(self, db_session: Session):
        """Test listing templates."""
        repo = TemplateRepository(db_session)
        repo.create_template("Template A", ["field1"], "/templates/a.docx")
        repo.create_template("Template B", ["field2"], "/templates/b.docx")
        repo.create_template("Template C", ["field3"], "/templates/c.docx")

        templates = repo.list_templates()
        assert len(templates) == 3

    def test_list_templates_sorting(self, db_session: Session):
        """Test listing templates with sorting."""
        repo = TemplateRepository(db_session)
        repo.create_template("Zebra", ["field1"], "/templates/z.docx")
        repo.create_template("Alpha", ["field2"], "/templates/a.docx")
        repo.create_template("Beta", ["field3"], "/templates/b.docx")

        # Sort by name ascending
        templates_asc = repo.list_templates(sort_by="name", sort_order="asc")
        assert templates_asc[0].name == "Alpha"
        assert templates_asc[1].name == "Beta"
        assert templates_asc[2].name == "Zebra"

    def test_update_template(self, db_session: Session):
        """Test updating template."""
        repo = TemplateRepository(db_session)
        template = repo.create_template(
            name="Old Name",
            placeholders=["field1"],
            file_path="/templates/old.docx",
            description="Old description",
        )

        updated = repo.update_template(
            template.id,
            name="New Name",
            placeholders=["field1", "field2"],
            description="New description",
        )

        assert updated is not None
        assert updated.name == "New Name"
        assert updated.description == "New description"
        assert json.loads(updated.placeholders) == ["field1", "field2"]

    def test_delete_template(self, db_session: Session):
        """Test deleting template."""
        repo = TemplateRepository(db_session)
        template = repo.create_template(
            name="To Delete",
            placeholders=["field1"],
            file_path="/templates/delete.docx",
        )

        assert repo.delete_template(template.id) is True
        assert repo.get_template_by_id(template.id) is None


# MappingRepository Tests
class TestMappingRepository:
    """Test MappingRepository CRUD operations."""

    def test_create_mapping(self, db_session: Session):
        """Test creating a mapping record."""
        # Create related records
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1", "field2"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        db_session.add(file_rec)
        db_session.add(template_rec)
        db_session.flush()

        repo = MappingRepository(db_session)
        mapping = repo.create_mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings={"Column A": "field1", "Column B": "field2"},
        )

        assert mapping.id is not None
        assert mapping.file_id == file_rec.id
        assert mapping.template_id == template_rec.id
        assert json.loads(mapping.column_mappings) == {"Column A": "field1", "Column B": "field2"}

    def test_get_mapping_by_id(self, db_session: Session):
        """Test retrieving mapping by ID."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        db_session.add(file_rec)
        db_session.add(template_rec)
        db_session.flush()

        repo = MappingRepository(db_session)
        created = repo.create_mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings={"col": "field"},
        )

        retrieved = repo.get_mapping_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_mappings_by_file(self, db_session: Session):
        """Test retrieving mappings by file."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template1 = Template(
            name="Template 1",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/t1.docx",
            created_at=datetime.utcnow(),
        )
        template2 = Template(
            name="Template 2",
            placeholders=json.dumps(["field2"]),
            file_path="/templates/t2.docx",
            created_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template1, template2])
        db_session.flush()

        repo = MappingRepository(db_session)
        repo.create_mapping(file_rec.id, template1.id, {"col": "field1"})
        repo.create_mapping(file_rec.id, template2.id, {"col": "field2"})

        mappings = repo.get_mappings_by_file(file_rec.id)
        assert len(mappings) == 2

    def test_update_mapping(self, db_session: Session):
        """Test updating mapping."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        db_session.add(file_rec)
        db_session.add(template_rec)
        db_session.flush()

        repo = MappingRepository(db_session)
        mapping = repo.create_mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings={"old": "field"},
        )

        updated = repo.update_mapping(
            mapping.id,
            column_mappings={"new": "field"},
        )

        assert updated is not None
        assert json.loads(updated.column_mappings) == {"new": "field"}


# JobRepository Tests
class TestJobRepository:
    """Test JobRepository CRUD operations."""

    def test_create_job(self, db_session: Session):
        """Test creating a job record."""
        # Create related records
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()  # Flush to get IDs

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()  # Flush mapping to get its ID

        repo = JobRepository(db_session)
        job = repo.create_job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            total_rows=100,
            status="pending",
        )

        assert job.id is not None
        assert job.file_id == file_rec.id
        assert job.template_id == template_rec.id
        assert job.mapping_id == mapping_rec.id
        assert job.total_rows == 100
        assert job.processed_rows == 0
        assert job.failed_rows == 0
        assert job.status == "pending"

    def test_increment_processed_rows(self, db_session: Session):
        """Test incrementing processed rows."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()  # Flush to get IDs

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()  # Flush mapping to get its ID

        repo = JobRepository(db_session)
        job = repo.create_job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            total_rows=100,
        )

        updated = repo.increment_processed_rows(job.id, count=10)
        assert updated is not None
        assert updated.processed_rows == 10

        updated = repo.increment_processed_rows(job.id, count=5)
        assert updated.processed_rows == 15

    def test_increment_failed_rows(self, db_session: Session):
        """Test incrementing failed rows."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()  # Flush to get IDs

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()  # Flush mapping to get its ID

        repo = JobRepository(db_session)
        job = repo.create_job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            total_rows=100,
        )

        updated = repo.increment_failed_rows(job.id, count=3)
        assert updated is not None
        assert updated.failed_rows == 3


# JobOutputRepository Tests
class TestJobOutputRepository:
    """Test JobOutputRepository CRUD operations."""

    def test_create_output(self, db_session: Session):
        """Test creating a job output record."""
        # Create related job
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()  # Flush to get IDs

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()  # Flush mapping to get its ID

        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(job_rec)
        db_session.flush()  # Flush job to get its ID

        repo = JobOutputRepository(db_session)
        output = repo.create_output(
            job_id=job_rec.id,
            filename="output1.docx",
            file_path="/outputs/output1.docx",
        )

        assert output.id is not None
        assert output.job_id == job_rec.id
        assert output.filename == "output1.docx"
        assert output.file_path == "/outputs/output1.docx"
        assert output.created_at is not None

    def test_get_outputs_by_job(self, db_session: Session):
        """Test retrieving all outputs for a job."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()  # Flush to get IDs

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()  # Flush mapping to get its ID

        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(job_rec)
        db_session.flush()  # Flush job to get its ID

        repo = JobOutputRepository(db_session)
        repo.create_output(job_rec.id, "output1.docx", "/outputs/output1.docx")
        repo.create_output(job_rec.id, "output2.docx", "/outputs/output2.docx")
        repo.create_output(job_rec.id, "output3.docx", "/outputs/output3.docx")

        outputs = repo.get_outputs_by_job(job_rec.id)
        assert len(outputs) == 3

    def test_list_output_files(self, db_session: Session):
        """Test listing output filenames."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()  # Flush to get IDs

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()  # Flush mapping to get its ID

        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(job_rec)
        db_session.flush()  # Flush job to get its ID

        repo = JobOutputRepository(db_session)
        repo.create_output(job_rec.id, "file1.docx", "/outputs/file1.docx")
        repo.create_output(job_rec.id, "file2.docx", "/outputs/file2.docx")

        filenames = repo.list_output_files(job_rec.id)
        assert len(filenames) == 2
        assert "file1.docx" in filenames
        assert "file2.docx" in filenames

    def test_delete_job_outputs(self, db_session: Session):
        """Test deleting all outputs for a job."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()  # Flush to get IDs

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()  # Flush mapping to get its ID

        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(job_rec)
        db_session.flush()  # Flush job to get its ID

        repo = JobOutputRepository(db_session)
        repo.create_output(job_rec.id, "file1.docx", "/outputs/file1.docx")
        repo.create_output(job_rec.id, "file2.docx", "/outputs/file2.docx")

        count = repo.delete_job_outputs(job_rec.id)
        assert count == 2

        remaining = repo.get_outputs_by_job(job_rec.id)
        assert len(remaining) == 0


    def test_get_output_by_job_and_filename(self, db_session: Session):
        """Test retrieving specific output file for a job."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()

        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(job_rec)
        db_session.flush()

        repo = JobOutputRepository(db_session)
        repo.create_output(job_rec.id, "file1.docx", "/outputs/file1.docx")
        repo.create_output(job_rec.id, "file2.docx", "/outputs/file2.docx")

        output = repo.get_output_by_job_and_filename(job_rec.id, "file2.docx")
        assert output is not None
        assert output.filename == "file2.docx"

        not_found = repo.get_output_by_job_and_filename(job_rec.id, "nonexistent.docx")
        assert not_found is None

    def test_count_outputs(self, db_session: Session):
        """Test counting outputs for a job."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()

        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(job_rec)
        db_session.flush()

        repo = JobOutputRepository(db_session)
        assert repo.count_outputs(job_rec.id) == 0

        repo.create_output(job_rec.id, "file1.docx", "/outputs/file1.docx")
        repo.create_output(job_rec.id, "file2.docx", "/outputs/file2.docx")
        repo.create_output(job_rec.id, "file3.docx", "/outputs/file3.docx")

        assert repo.count_outputs(job_rec.id) == 3

    def test_get_output_by_id(self, db_session: Session):
        """Test retrieving output by ID."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()

        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(job_rec)
        db_session.flush()

        repo = JobOutputRepository(db_session)
        output = repo.create_output(job_rec.id, "file1.docx", "/outputs/file1.docx")

        retrieved = repo.get_output_by_id(output.id)
        assert retrieved is not None
        assert retrieved.id == output.id

        not_found = repo.get_output_by_id(uuid4())
        assert not_found is None

    def test_delete_output(self, db_session: Session):
        """Test deleting output by ID."""
        file_rec = File(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            file_path="/tmp/test.csv",
            status="pending",
            uploaded_at=datetime.utcnow(),
        )
        template_rec = Template(
            name="Test Template",
            placeholders=json.dumps(["field1"]),
            file_path="/templates/test.docx",
            created_at=datetime.utcnow(),
        )
        db_session.add_all([file_rec, template_rec])
        db_session.flush()

        mapping_rec = Mapping(
            file_id=file_rec.id,
            template_id=template_rec.id,
            column_mappings=json.dumps({"col": "field1"}),
            created_at=datetime.utcnow(),
        )
        db_session.add(mapping_rec)
        db_session.flush()

        job_rec = Job(
            file_id=file_rec.id,
            template_id=template_rec.id,
            mapping_id=mapping_rec.id,
            status="pending",
            total_rows=100,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(job_rec)
        db_session.flush()

        repo = JobOutputRepository(db_session)
        output = repo.create_output(job_rec.id, "file1.docx", "/outputs/file1.docx")

        assert repo.delete_output(output.id) is True
        assert repo.get_output_by_id(output.id) is None

        assert repo.delete_output(uuid4()) is False
