"""
Integration tests for database-backed API endpoints.

Tests that API endpoints properly use SQLite database for persistence.
"""

import io
import json
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app, _file_storage
from src.repositories.database import DatabaseManager, init_db, get_db_manager
from migrations import File as FileModel


@pytest.fixture
def client() -> TestClient:
    """Create a test client with database initialization."""
    # Use temporary database for tests
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    db_url = f"sqlite:///{db_path}"
    
    # Initialize database
    import os
    os.environ["DATABASE_URL"] = db_url
    init_db()
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    import os
    if Path(db_path).exists():
        os.unlink(db_path)


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


class TestUploadEndpointWithDatabase:
    """Test file upload endpoint stores data in database."""

    def test_upload_creates_database_record(self, client: TestClient):
        """Test that file upload creates a record in the database."""
        csv_content = b"Name,Email\nJohn,john@test.com\nJane,jane@test.com"
        
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        
        # Verify file appears in list endpoint
        list_response = client.get("/api/v1/files")
        assert list_response.status_code == 200
        files_data = list_response.json()
        
        assert files_data["total"] >= 1
        file_ids = [f["file_id"] for f in files_data["files"]]
        assert data["file_id"] in file_ids

    def test_uploaded_file_persists_in_list(self, client: TestClient):
        """Test that uploaded files persist and can be listed."""
        # Upload multiple files
        for i in range(3):
            csv_content = f"Name{i},Email{i}\n".encode()
            response = client.post(
                "/api/v1/upload",
                files={"file": (f"test{i}.csv", io.BytesIO(csv_content), "text/csv")}
            )
            assert response.status_code == 201
        
        # List should return all files
        list_response = client.get("/api/v1/files")
        assert list_response.status_code == 200
        data = list_response.json()
        
        assert data["total"] >= 3
        filenames = [f["filename"] for f in data["files"]]
        assert "test0.csv" in filenames
        assert "test1.csv" in filenames
        assert "test2.csv" in filenames


class TestMappingEndpointWithDatabase:
    """Test mapping endpoint uses database storage."""

    def test_create_mapping_stores_in_database(self, client: TestClient):
        """Test that creating a mapping stores it in database."""
        # First upload a file
        csv_content = b"Name,Email,Phone\nJohn,john@test.com,555-1234"
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("mapping_test.csv", io.BytesIO(csv_content), "text/csv")}
        )
        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]
        
        # Create a template using the API
        template_response = client.post(
            "/api/v1/templates/upload",
            files={"file": ("template.docx", io.BytesIO(b"fake docx content"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"name": "Test Template", "description": "Test"}
        )
        
        # If template upload fails, use query param endpoint
        if template_response.status_code != 201:
            template_response = client.post(
                "/api/v1/templates",
                params={
                    "name": "Test Template",
                    "file_path": "/templates/test.docx",
                    "placeholders": "name,email,phone"
                }
            )
        
        assert template_response.status_code == 201
        template_id = template_response.json()["template"]["id"]
        
        # Create mapping
        mapping_response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": file_id,
                "template_id": template_id
            },
            json={
                "Name": "name",
                "Email": "email",
                "Phone": "phone"
            }
        )
        
        assert mapping_response.status_code == 201
        mapping_data = mapping_response.json()
        assert "id" in mapping_data
        assert mapping_data["column_mappings"] == {
            "Name": "name",
            "Email": "email",
            "Phone": "phone"
        }


class TestDataPersistenceAcrossRequests:
    """Test that data persists across multiple requests."""

    def test_file_data_survives_multiple_requests(self, client: TestClient):
        """Test that uploaded file data is available in subsequent requests."""
        # Upload file
        csv_content = b"Product,Price\nWidget,19.99\nGadget,29.99"
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("products.csv", io.BytesIO(csv_content), "text/csv")}
        )
        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]
        
        # Parse endpoint should work
        parse_response = client.get(f"/api/v1/parse/{file_id}")
        assert parse_response.status_code == 200
        
        parse_data = parse_response.json()
        assert parse_data["file_id"] == file_id
        assert len(parse_data["rows"]) == 2
        assert parse_data["total_rows"] == 2

    def test_pagination_with_database(self, client: TestClient):
        """Test that pagination works with database-backed storage."""
        # Upload 5 files
        for i in range(5):
            csv_content = f"Col{i}\nValue{i}\n".encode()
            response = client.post(
                "/api/v1/upload",
                files={"file": (f"page{i}.csv", io.BytesIO(csv_content), "text/csv")}
            )
            assert response.status_code == 201
        
        # Test pagination
        page1 = client.get("/api/v1/files?limit=2&offset=0")
        assert page1.status_code == 200
        data1 = page1.json()
        assert len(data1["files"]) == 2
        assert data1["has_more"] is True
        
        page2 = client.get("/api/v1/files?limit=2&offset=2")
        assert page2.status_code == 200
        data2 = page2.json()
        assert len(data2["files"]) == 2
        
        page3 = client.get("/api/v1/files?limit=2&offset=4")
        assert page3.status_code == 200
        data3 = page3.json()
        assert len(data3["files"]) == 1
        assert data3["has_more"] is False
