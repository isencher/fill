"""
Unit tests for templates router.

Tests template CRUD operations.
"""

import io

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.template_store import get_template_store


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_template_store() -> None:
    """Clear template store before each test."""
    store = get_template_store()
    # Clear the in-memory storage
    store._storage.clear()

    yield

    # Clean up again after test
    store._storage.clear()


class TestCreateTemplate:
    """Tests for POST /api/v1/templates endpoint."""

    def test_create_template_success(self, client: TestClient) -> None:
        """Test creating a new template."""
        response = client.post(
            "/api/v1/templates",
            params={
                "name": "Test Template",
                "file_path": "/path/to/template.docx",
                "description": "A test template",
                "placeholders": "name,age,address",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["template"]["name"] == "Test Template"
        assert data["template"]["description"] == "A test template"
        assert data["template"]["placeholders"] == ["name", "age", "address"]

    def test_create_template_minimal(self, client: TestClient) -> None:
        """Test creating a template with only required fields."""
        response = client.post(
            "/api/v1/templates",
            params={
                "name": "Minimal Template",
                "file_path": "/path/to/template.docx",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["template"]["name"] == "Minimal Template"
        assert data["template"]["placeholders"] == []

    def test_create_template_with_empty_placeholders(self, client: TestClient) -> None:
        """Test creating a template with empty placeholder string."""
        response = client.post(
            "/api/v1/templates",
            params={
                "name": "Test Template",
                "file_path": "/path/to/template.docx",
                "placeholders": "",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["template"]["placeholders"] == []


class TestUploadTemplate:
    """Tests for POST /api/v1/templates/upload endpoint."""

    def test_upload_template_docx(self, client: TestClient) -> None:
        """Test uploading a DOCX template file."""
        file_content = b"PK\x03\x04"  # ZIP header (docx is a zip file)
        files = {"file": ("template.docx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        data = {"name": "Uploaded Template", "description": "Test"}

        response = client.post("/api/v1/templates/upload", files=files, data=data)

        assert response.status_code == 201
        resp_data = response.json()
        assert resp_data["template"]["name"] == "Uploaded Template"
        assert "extracted_placeholders" in resp_data

    def test_upload_template_txt(self, client: TestClient) -> None:
        """Test uploading a TXT template file."""
        file_content = b"Hello {{name}}, your order {{order_id}} is ready."
        files = {"file": ("template.txt", io.BytesIO(file_content), "text/plain")}
        data = {"name": "Text Template"}

        response = client.post("/api/v1/templates/upload", files=files, data=data)

        assert response.status_code == 201
        resp_data = response.json()
        assert resp_data["template"]["name"] == "Text Template"

    def test_upload_template_invalid_type(self, client: TestClient) -> None:
        """Test uploading an invalid file type."""
        files = {"file": ("template.pdf", io.BytesIO(b"%PDF"), "application/pdf")}
        data = {"name": "PDF Template"}

        response = client.post("/api/v1/templates/upload", files=files, data=data)

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]


class TestListTemplates:
    """Tests for GET /api/v1/templates endpoint."""

    def test_list_templates_empty(self, client: TestClient) -> None:
        """Test listing templates when none exist."""
        response = client.get("/api/v1/templates")

        assert response.status_code == 200
        data = response.json()
        assert data["templates"] == []
        assert data["total"] == 0

    def test_list_templates_with_created(self, client: TestClient) -> None:
        """Test listing templates after creating one."""
        # Create a template first
        client.post(
            "/api/v1/templates",
            params={"name": "Test", "file_path": "/path/to/template.docx"}
        )

        response = client.get("/api/v1/templates")

        assert response.status_code == 200
        data = response.json()
        assert len(data["templates"]) == 1
        assert data["total"] == 1

    def test_list_templates_pagination(self, client: TestClient) -> None:
        """Test pagination parameters."""
        # Create multiple templates
        for i in range(5):
            client.post(
                "/api/v1/templates",
                params={"name": f"Template {i}", "file_path": f"/path/{i}.docx"}
            )

        response = client.get("/api/v1/templates?limit=2&offset=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data["templates"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 1

    def test_list_templates_sort_by_name(self, client: TestClient) -> None:
        """Test sorting by name."""
        client.post("/api/v1/templates", params={"name": "Zebra", "file_path": "/z.docx"})
        client.post("/api/v1/templates", params={"name": "Apple", "file_path": "/a.docx"})

        response = client.get("/api/v1/templates?sort_by=name&order=asc")

        assert response.status_code == 200
        data = response.json()
        assert data["templates"][0]["name"] == "Apple"
        assert data["templates"][1]["name"] == "Zebra"


class TestGetTemplate:
    """Tests for GET /api/v1/templates/{id} endpoint."""

    def test_get_template_by_id(self, client: TestClient) -> None:
        """Test getting a template by ID."""
        # Create a template
        create_response = client.post(
            "/api/v1/templates",
            params={"name": "Test Template", "file_path": "/path/doc.docx"}
        )
        template_id = create_response.json()["template"]["id"]

        response = client.get(f"/api/v1/templates/{template_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Template"

    def test_get_nonexistent_template(self, client: TestClient) -> None:
        """Test getting a template that doesn't exist."""
        response = client.get("/api/v1/templates/nonexistent-id")

        assert response.status_code == 404


class TestUpdateTemplate:
    """Tests for PUT /api/v1/templates/{id} endpoint."""

    def test_update_template_name(self, client: TestClient) -> None:
        """Test updating template name."""
        # Create a template
        create_response = client.post(
            "/api/v1/templates",
            params={"name": "Original Name", "file_path": "/path/doc.docx"}
        )
        template_id = create_response.json()["template"]["id"]

        response = client.put(
            f"/api/v1/templates/{template_id}",
            params={"name": "Updated Name"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["template"]["name"] == "Updated Name"

    def test_update_template_no_fields(self, client: TestClient) -> None:
        """Test updating with no fields returns error."""
        # Create a template
        create_response = client.post(
            "/api/v1/templates",
            params={"name": "Test", "file_path": "/path/doc.docx"}
        )
        template_id = create_response.json()["template"]["id"]

        response = client.put(f"/api/v1/templates/{template_id}")

        assert response.status_code == 400
        assert "No update fields provided" in response.json()["detail"]

    def test_update_nonexistent_template(self, client: TestClient) -> None:
        """Test updating a template that doesn't exist."""
        response = client.put(
            "/api/v1/templates/nonexistent-id",
            params={"name": "New Name"}
        )

        assert response.status_code == 404


class TestDeleteTemplate:
    """Tests for DELETE /api/v1/templates/{id} endpoint."""

    def test_delete_template_success(self, client: TestClient) -> None:
        """Test deleting a template."""
        # Create a template
        create_response = client.post(
            "/api/v1/templates",
            params={"name": "To Delete", "file_path": "/path/doc.docx"}
        )
        template_id = create_response.json()["template"]["id"]

        response = client.delete(f"/api/v1/templates/{template_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["template_id"] == template_id

        # Verify it's deleted
        get_response = client.get(f"/api/v1/templates/{template_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_template(self, client: TestClient) -> None:
        """Test deleting a template that doesn't exist."""
        response = client.delete("/api/v1/templates/nonexistent-id")

        assert response.status_code == 404
