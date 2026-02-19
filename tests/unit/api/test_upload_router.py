"""
Unit tests for upload router.

Tests file upload and file listing endpoints.
"""

import io

import pytest
from fastapi.testclient import TestClient

from src.main import app, _file_storage
from src.repositories.database import get_db_manager
from migrations import File as FileModel


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage() -> None:
    """Clear in-memory storage and database before each test."""
    # Clear in-memory file storage
    _file_storage.clear()

    # Clear database files table
    db_manager = get_db_manager()
    with db_manager.get_session() as db:
        # Delete all files
        db.query(FileModel).delete()
        db.commit()

    yield

    # Clean up again after test
    _file_storage.clear()
    with db_manager.get_session() as db:
        db.query(FileModel).delete()
        db.commit()


class TestUploadEndpoint:
    """Tests for POST /api/v1/upload endpoint."""

    def test_upload_csv_file_success(self, client: TestClient) -> None:
        """Test uploading a valid CSV file."""
        file_content = b"name,age\nAlice,30\nBob,25"
        files = {"file": ("test.csv", io.BytesIO(file_content), "text/csv")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "test.csv"
        assert data["size"] == len(file_content)
        assert data["status"] == "pending"

    def test_upload_xlsx_file_success(self, client: TestClient) -> None:
        """Test uploading a valid Excel file."""
        file_content = b"PK\x03\x04"  # ZIP header (xlsx is a zip file)
        files = {"file": ("test.xlsx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "test.xlsx"

    def test_upload_invalid_file_type(self, client: TestClient) -> None:
        """Test uploading an invalid file type returns 400."""
        files = {"file": ("test.txt", io.BytesIO(b"some text"), "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_file_too_large(self, client: TestClient) -> None:
        """Test uploading a file exceeding size limit returns 413."""
        # Create a file larger than 10MB
        large_content = b"x" * (10 * 1024 * 1024 + 1)
        files = {"file": ("large.csv", io.BytesIO(large_content), "text/csv")}
        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 413
        assert "exceeds maximum allowed size" in response.json()["detail"]

    def test_upload_empty_filename(self, client: TestClient) -> None:
        """Test uploading a file with empty filename."""
        files = {"file": ("", io.BytesIO(b"data"), "text/csv")}
        response = client.post("/api/v1/upload", files=files)

        # Should fail validation since file extension can't be checked
        # FastAPI returns 422 for validation errors
        assert response.status_code in (400, 422)


class TestListFilesEndpoint:
    """Tests for GET /api/v1/files endpoint."""

    def test_list_files_empty(self, client: TestClient) -> None:
        """Test listing files when none exist."""
        response = client.get("/api/v1/files")

        assert response.status_code == 200
        data = response.json()
        assert data["files"] == []
        assert data["total"] == 0

    def test_list_files_with_uploaded_file(self, client: TestClient) -> None:
        """Test listing files after uploading one."""
        # Upload a file first
        files = {"file": ("test.csv", io.BytesIO(b"data"), "text/csv")}
        client.post("/api/v1/upload", files=files)

        response = client.get("/api/v1/files")

        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 1
        assert data["total"] == 1

    def test_list_files_pagination(self, client: TestClient) -> None:
        """Test pagination parameters work correctly."""
        # Upload multiple files
        for i in range(5):
            files = {"file": (f"file{i}.csv", io.BytesIO(b"data"), "text/csv")}
            client.post("/api/v1/upload", files=files)

        response = client.get("/api/v1/files?limit=2&offset=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 2
        assert data["total"] == 5
        assert data["offset"] == 1
        assert data["limit"] == 2

    def test_list_files_invalid_limit(self, client: TestClient) -> None:
        """Test that invalid limit returns validation error."""
        response = client.get("/api/v1/files?limit=0")

        assert response.status_code == 422

    def test_list_files_invalid_offset(self, client: TestClient) -> None:
        """Test that negative offset returns validation error."""
        response = client.get("/api/v1/files?offset=-1")

        assert response.status_code == 422
