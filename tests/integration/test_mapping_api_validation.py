"""
Integration tests for Mapping API parameter validation.

Tests error handling and parameter passing for the mapping endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app, _file_storage
from src.services.template_store import get_template_store
from src.models.file import UploadFile, FileStatus
from src.models.template import Template
from src.repositories.database import get_db_manager
from migrations import File as FileModel
import io


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear in-memory storage and database before each test."""
    _file_storage.clear()

    # Clear database files table
    db_manager = get_db_manager()
    with db_manager.get_session() as db:
        db.query(FileModel).delete()
        db.commit()

    # Note: TemplateStore is a singleton, we don't clear it between tests
    yield

    # Clean up again after test
    _file_storage.clear()
    with db_manager.get_session() as db:
        db.query(FileModel).delete()
        db.commit()


@pytest.fixture
def sample_file_id() -> str:
    """Create and return a sample uploaded file ID."""
    csv_content = b"Name,Email,Phone\nJohn,john@test.com,555-1234\nJane,jane@test.com,555-5678"

    file_id_uuid = uuid4()
    file_id = str(file_id_uuid)
    upload_file = UploadFile(
        id=file_id,
        filename="test.csv",
        content_type="text/csv",
        size=len(csv_content),
        status=FileStatus.PENDING,
    )
    _file_storage.store(file_id, csv_content)

    # Also create database record with UUID object
    db_manager = get_db_manager()
    with db_manager.get_session() as db:
        db_file = FileModel(
            id=file_id_uuid,  # Use UUID object, not string
            filename="test.csv",
            content_type="text/csv",
            size=len(csv_content),
            status=FileStatus.PENDING.value,
            file_path=f"/memory/{file_id}",  # Required field for in-memory storage
        )
        db.add(db_file)
        db.commit()

    return file_id


@pytest.fixture
def sample_template_id() -> str:
    """Create and return a sample template ID."""
    template_store = get_template_store()
    template = Template(
        name="Test Template",
        description="Test template for mapping",
        placeholders=["name", "email", "phone"],
        file_path="/templates/test.docx",
    )
    saved = template_store.save_template(template)
    return saved.id


class TestMappingAPIValidation:
    """Test mapping API parameter validation and error handling."""

    def test_create_mapping_success(
        self, client: TestClient, sample_file_id: str, sample_template_id: str
    ):
        """Test successful mapping creation with valid parameters."""
        column_mappings = {
            "Name": "name",
            "Email": "email",
            "Phone": "phone",
        }

        response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": sample_file_id,
                "template_id": sample_template_id,
            },
            json=column_mappings,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["file_id"] == sample_file_id
        assert data["template_id"] == sample_template_id
        assert data["column_mappings"] == column_mappings
        assert "created_at" in data

    def test_create_mapping_empty_body(
        self, client: TestClient, sample_file_id: str, sample_template_id: str
    ):
        """Test mapping creation with empty column mappings."""
        response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": sample_file_id,
                "template_id": sample_template_id,
            },
            json={},
        )

        # Should succeed with empty mappings
        assert response.status_code == 201
        data = response.json()
        assert data["column_mappings"] == {}

    def test_create_mapping_file_not_found(
        self, client: TestClient, sample_template_id: str
    ):
        """Test error handling for non-existent file."""
        response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": "non-existent-file",
                "template_id": sample_template_id,
            },
            json={"col": "field"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "file not found" in data["detail"].lower()

    def test_create_mapping_template_not_found(
        self, client: TestClient, sample_file_id: str
    ):
        """Test error handling for non-existent template."""
        response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": sample_file_id,
                "template_id": "non-existent-template",
            },
            json={"col": "field"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "template not found" in data["detail"].lower()

    def test_create_mapping_invalid_file_id_format(
        self, client: TestClient, sample_template_id: str
    ):
        """Test error handling for invalid file ID format."""
        response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": "",  # Empty file_id
                "template_id": sample_template_id,
            },
            json={"col": "field"},
        )

        # FastAPI should validate min_length
        assert response.status_code == 422
        data = response.json()
        # Error should be about file_id validation
        assert "file_id" in str(data).lower() or "detail" in data

    def test_error_message_format(
        self, client: TestClient, sample_template_id: str
    ):
        """Test that error messages are properly formatted (not [object Object])."""
        response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": "invalid-uuid-format-that-does-not-exist",
                "template_id": sample_template_id,
            },
            json={"col": "field"},
        )

        # Should get a proper error message
        assert response.status_code in [404, 422]
        data = response.json()
        
        # Error detail should be a string, not contain [object Object]
        detail = str(data.get("detail", ""))
        assert "[object object]" not in detail.lower()
        # Should contain meaningful error message
        assert len(detail) > 0

    def test_create_mapping_with_special_characters(
        self, client: TestClient, sample_file_id: str, sample_template_id: str
    ):
        """Test mapping with special characters in column names."""
        column_mappings = {
            "Column 名称": "placeholder_名称",
            "Column (Special)": "placeholder_special",
            "UPPER_CASE": "upper_case",
        }

        response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": sample_file_id,
                "template_id": sample_template_id,
            },
            json=column_mappings,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["column_mappings"] == column_mappings
