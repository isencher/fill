"""
Unit tests for mappings router.

Tests mapping suggestions and parsing endpoints.
"""

import io

import pytest
from fastapi.testclient import TestClient

from src.main import app, _file_storage
from src.services.template_store import get_template_store
from src.repositories.database import get_db_manager
from migrations import File as FileModel


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_state() -> None:
    """Clear storage and database before each test."""
    _file_storage.clear()
    store = get_template_store()
    store._storage.clear()

    db_manager = get_db_manager()
    with db_manager.get_session() as db:
        db.query(FileModel).delete()
        db.commit()

    yield

    _file_storage.clear()
    store._storage.clear()
    with db_manager.get_session() as db:
        db.query(FileModel).delete()
        db.commit()


@pytest.fixture
def uploaded_file(client: TestClient) -> str:
    """Upload a test file and return its ID."""
    file_content = b"name,age,email\nAlice,30,alice@example.com\nBob,25,bob@example.com"
    files = {"file": ("test.csv", io.BytesIO(file_content), "text/csv")}
    response = client.post("/api/v1/upload", files=files)
    return response.json()["file_id"]


@pytest.fixture
def created_template(client: TestClient) -> str:
    """Create a test template and return its ID."""
    response = client.post(
        "/api/v1/templates",
        params={
            "name": "Test Template",
            "file_path": "/path/to/template.docx",
            "placeholders": "name,age,email",
        }
    )
    return response.json()["template"]["id"]


class TestSuggestMapping:
    """Tests for POST /api/v1/mappings/suggest endpoint."""

    def test_suggest_mapping_success(self, client: TestClient, uploaded_file: str, created_template: str) -> None:
        """Test getting mapping suggestions."""
        response = client.post(
            "/api/v1/mappings/suggest",
            params={"file_id": uploaded_file, "template_id": created_template}
        )

        assert response.status_code == 200
        data = response.json()
        assert "suggested_mappings" in data
        assert "confidence" in data
        assert "can_auto_fill" in data
        assert "unmapped_columns" in data
        assert "unmapped_placeholders" in data

    def test_suggest_mapping_file_not_found(self, client: TestClient, created_template: str) -> None:
        """Test suggesting with non-existent file."""
        response = client.post(
            "/api/v1/mappings/suggest",
            params={"file_id": "nonexistent-id", "template_id": created_template}
        )

        assert response.status_code == 404

    def test_suggest_mapping_template_not_found(self, client: TestClient, uploaded_file: str) -> None:
        """Test suggesting with non-existent template."""
        response = client.post(
            "/api/v1/mappings/suggest",
            params={"file_id": uploaded_file, "template_id": "nonexistent-id"}
        )

        assert response.status_code == 404

    def test_suggest_mapping_invalid_file_id(self, client: TestClient, created_template: str) -> None:
        """Test suggesting with invalid file ID format."""
        response = client.post(
            "/api/v1/mappings/suggest",
            params={"file_id": "not-a-uuid", "template_id": created_template}
        )

        assert response.status_code == 404


class TestCreateMapping:
    """Tests for POST /api/v1/mappings endpoint."""

    def test_create_mapping_success(self, client: TestClient, uploaded_file: str, created_template: str) -> None:
        """Test creating a column-to-placeholder mapping."""
        response = client.post(
            "/api/v1/mappings",
            params={"file_id": uploaded_file, "template_id": created_template},
            json={"name": "name", "age": "age", "email": "email"}
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["file_id"] == uploaded_file
        assert data["template_id"] == created_template
        assert "column_mappings" in data

    def test_create_mapping_empty_mappings(self, client: TestClient, uploaded_file: str, created_template: str) -> None:
        """Test creating a mapping with empty column mappings."""
        response = client.post(
            "/api/v1/mappings",
            params={"file_id": uploaded_file, "template_id": created_template},
            json={}
        )

        assert response.status_code == 201

    def test_create_mapping_file_not_found(self, client: TestClient, created_template: str) -> None:
        """Test creating mapping with non-existent file."""
        response = client.post(
            "/api/v1/mappings",
            params={"file_id": "nonexistent-id", "template_id": created_template},
            json={"name": "name"}
        )

        assert response.status_code == 404

    def test_create_mapping_template_not_found(self, client: TestClient, uploaded_file: str) -> None:
        """Test creating mapping with non-existent template."""
        response = client.post(
            "/api/v1/mappings",
            params={"file_id": uploaded_file, "template_id": "nonexistent-id"},
            json={"name": "name"}
        )

        assert response.status_code == 404


class TestParseFile:
    """Tests for GET /api/v1/parse/{file_id} endpoint."""

    def test_parse_file_success(self, client: TestClient, uploaded_file: str) -> None:
        """Test parsing an uploaded file."""
        response = client.get(f"/api/v1/parse/{uploaded_file}")

        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert "filename" in data
        assert "rows" in data
        assert "total_rows" in data
        # Should return first 5 rows for preview
        assert len(data["rows"]) <= 5

    def test_parse_file_not_found(self, client: TestClient) -> None:
        """Test parsing a non-existent file."""
        response = client.get("/api/v1/parse/nonexistent-id")

        assert response.status_code == 404

    def test_parse_file_invalid_id(self, client: TestClient) -> None:
        """Test parsing with invalid file ID format."""
        response = client.get("/api/v1/parse/not-a-uuid")

        assert response.status_code == 404
