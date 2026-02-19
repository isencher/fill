"""
Integration tests for Template API endpoints.

Tests cover CRUD operations for templates via HTTP API.
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from src.main import app
from src.services.template_store import get_template_store


def normalize_path(path_str: str) -> str:
    """Normalize path for cross-platform testing."""
    return str(Path(path_str))


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: FastAPI test client instance
    """
    return TestClient(app)


class TestCreateTemplate:
    """Test POST /api/v1/templates endpoint."""

    def setup_method(self):
        """Clear template store before each test."""
        store = get_template_store()
        store.clear()

    def test_create_template_success(self, client: TestClient):
        """Test creating a template successfully."""
        response = client.post(
            "/api/v1/templates",
            params={
                "name": "Invoice Template",
                "file_path": "/templates/invoice.docx",
                "description": "Standard invoice template",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Template created successfully"
        assert "template" in data
        assert data["template"]["name"] == "Invoice Template"
        assert data["template"]["file_path"] == normalize_path("/templates/invoice.docx")
        assert data["template"]["description"] == "Standard invoice template"
        assert "id" in data["template"]
        assert "created_at" in data["template"]

    def test_create_template_with_placeholders(self, client: TestClient):
        """Test creating template with placeholders."""
        response = client.post(
            "/api/v1/templates",
            params={
                "name": "Contract Template",
                "file_path": "/templates/contract.docx",
                "placeholders": "party_name, start_date, end_date, amount",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["template"]["placeholders"] == ["party_name", "start_date", "end_date", "amount"]

    def test_create_template_with_empty_placeholders(self, client: TestClient):
        """Test creating template with empty placeholder list."""
        response = client.post(
            "/api/v1/templates",
            params={
                "name": "Simple Template",
                "file_path": "/templates/simple.docx",
                "placeholders": "",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["template"]["placeholders"] == []

    def test_create_template_missing_name(self, client: TestClient):
        """Test creating template without name fails."""
        response = client.post(
            "/api/v1/templates",
            params={
                "file_path": "/templates/test.docx",
            }
        )

        assert response.status_code == 422  # Validation error

    def test_create_template_missing_file_path(self, client: TestClient):
        """Test creating template without file_path fails."""
        response = client.post(
            "/api/v1/templates",
            params={
                "name": "Test Template",
            }
        )

        assert response.status_code == 422  # Validation error

    def test_create_template_invalid_name(self, client: TestClient):
        """Test creating template with invalid name (empty)."""
        response = client.post(
            "/api/v1/templates",
            params={
                "name": "",  # Empty name
                "file_path": "/templates/test.docx",
            }
        )

        assert response.status_code == 422  # Validation error

    def test_create_template_duplicate_placeholder_names(self, client: TestClient):
        """Test creating template with duplicate placeholder names fails."""
        response = client.post(
            "/api/v1/templates",
            params={
                "name": "Test Template",
                "file_path": "/templates/test.docx",
                "placeholders": "name, name, value",
            }
        )

        assert response.status_code == 400  # Pydantic validation error


class TestListTemplates:
    """Test GET /api/v1/templates endpoint."""

    def setup_method(self):
        """Clear and populate template store before each test."""
        store = get_template_store()
        store.clear()

    def test_list_empty_templates(self, client: TestClient):
        """Test listing templates when empty."""
        response = client.get("/api/v1/templates")

        assert response.status_code == 200
        data = response.json()
        assert data["templates"] == []
        assert data["total"] == 0
        assert data["has_more"] is False

    def test_list_templates_single(self, client: TestClient):
        """Test listing single template."""
        # Create template first
        client.post(
            "/api/v1/templates",
            params={
                "name": "Template 1",
                "file_path": "/templates/t1.docx",
            }
        )

        response = client.get("/api/v1/templates")

        assert response.status_code == 200
        data = response.json()
        assert len(data["templates"]) == 1
        assert data["total"] == 1
        assert data["templates"][0]["name"] == "Template 1"

    def test_list_templates_multiple(self, client: TestClient):
        """Test listing multiple templates."""
        # Create multiple templates
        for i in range(3):
            client.post(
                "/api/v1/templates",
                params={
                    "name": f"Template {i}",
                    "file_path": f"/templates/t{i}.docx",
                }
            )

        response = client.get("/api/v1/templates")

        assert response.status_code == 200
        data = response.json()
        assert len(data["templates"]) == 3
        assert data["total"] == 3

    def test_list_templates_with_limit(self, client: TestClient):
        """Test listing templates with limit parameter."""
        # Create 5 templates
        for i in range(5):
            client.post(
                "/api/v1/templates",
                params={
                    "name": f"Template {i}",
                    "file_path": f"/templates/t{i}.docx",
                }
            )

        response = client.get("/api/v1/templates?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data["templates"]) == 3
        assert data["limit"] == 3
        assert data["has_more"] is True

    def test_list_templates_with_offset(self, client: TestClient):
        """Test listing templates with offset parameter."""
        # Create 5 templates
        for i in range(5):
            client.post(
                "/api/v1/templates",
                params={
                    "name": f"Template {i}",
                    "file_path": f"/templates/t{i}.docx",
                }
            )

        response = client.get("/api/v1/templates?offset=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["templates"]) == 3
        assert data["offset"] == 2

    def test_list_templates_with_sort_by_name(self, client: TestClient):
        """Test listing templates sorted by name."""
        # Create templates with specific names
        names = ["Charlie", "Alpha", "Bravo"]
        for name in names:
            client.post(
                "/api/v1/templates",
                params={
                    "name": name,
                    "file_path": f"/templates/{name}.docx",
                }
            )

        response = client.get("/api/v1/templates?sort_by=name&order=asc")

        assert response.status_code == 200
        data = response.json()
        assert data["templates"][0]["name"] == "Alpha"
        assert data["templates"][1]["name"] == "Bravo"
        assert data["templates"][2]["name"] == "Charlie"

    def test_list_templates_invalid_sort_by(self, client: TestClient):
        """Test listing templates with invalid sort_by field."""
        response = client.get("/api/v1/templates?sort_by=invalid_field")

        assert response.status_code == 400

    def test_list_templates_invalid_sort_order(self, client: TestClient):
        """Test listing templates with invalid sort order."""
        response = client.get("/api/v1/templates?order=invalid_order")

        assert response.status_code == 400


class TestGetTemplate:
    """Test GET /api/v1/templates/{template_id} endpoint."""

    def setup_method(self):
        """Clear and populate template store before each test."""
        store = get_template_store()
        store.clear()

    def test_get_template_success(self, client: TestClient):
        """Test getting a template by ID."""
        # Create template first
        create_response = client.post(
            "/api/v1/templates",
            params={
                "name": "Test Template",
                "file_path": "/templates/test.docx",
            }
        )
        template_id = create_response.json()["template"]["id"]

        # Get template
        response = client.get(f"/api/v1/templates/{template_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id
        assert data["name"] == "Test Template"

    def test_get_template_not_found(self, client: TestClient):
        """Test getting nonexistent template returns 404."""
        response = client.get("/api/v1/templates/nonexistent-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestUpdateTemplate:
    """Test PUT /api/v1/templates/{template_id} endpoint."""

    def setup_method(self):
        """Clear and populate template store before each test."""
        store = get_template_store()
        store.clear()

    def test_update_template_name(self, client: TestClient):
        """Test updating template name."""
        # Create template first
        create_response = client.post(
            "/api/v1/templates",
            params={
                "name": "Original Name",
                "file_path": "/templates/test.docx",
            }
        )
        template_id = create_response.json()["template"]["id"]

        # Update name
        response = client.put(
            f"/api/v1/templates/{template_id}",
            params={"name": "Updated Name"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Template updated successfully"
        assert data["template"]["name"] == "Updated Name"
        assert data["template"]["file_path"] == normalize_path("/templates/test.docx")

    def test_update_template_description(self, client: TestClient):
        """Test updating template description."""
        # Create template first
        create_response = client.post(
            "/api/v1/templates",
            params={
                "name": "Test",
                "file_path": "/templates/test.docx",
            }
        )
        template_id = create_response.json()["template"]["id"]

        # Update description
        response = client.put(
            f"/api/v1/templates/{template_id}",
            params={"description": "New description"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["template"]["description"] == "New description"

    def test_update_template_placeholders(self, client: TestClient):
        """Test updating template placeholders."""
        # Create template first
        create_response = client.post(
            "/api/v1/templates",
            params={
                "name": "Test",
                "file_path": "/templates/test.docx",
            }
        )
        template_id = create_response.json()["template"]["id"]

        # Update placeholders
        response = client.put(
            f"/api/v1/templates/{template_id}",
            params={"placeholders": "field1, field2, field3"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["template"]["placeholders"] == ["field1", "field2", "field3"]

    def test_update_template_multiple_fields(self, client: TestClient):
        """Test updating multiple template fields."""
        # Create template first
        create_response = client.post(
            "/api/v1/templates",
            params={
                "name": "Original",
                "file_path": "/templates/original.docx",
            }
        )
        template_id = create_response.json()["template"]["id"]

        # Update multiple fields
        response = client.put(
            f"/api/v1/templates/{template_id}",
            params={
                "name": "Updated",
                "file_path": "/templates/updated.docx",
                "description": "Updated description",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["template"]["name"] == "Updated"
        assert data["template"]["file_path"] == normalize_path("/templates/updated.docx")
        assert data["template"]["description"] == "Updated description"

    def test_update_template_no_fields(self, client: TestClient):
        """Test updating template without any fields fails."""
        # Create template first
        create_response = client.post(
            "/api/v1/templates",
            params={
                "name": "Test",
                "file_path": "/templates/test.docx",
            }
        )
        template_id = create_response.json()["template"]["id"]

        # Update with no fields
        response = client.put(f"/api/v1/templates/{template_id}")

        assert response.status_code == 400

    def test_update_template_not_found(self, client: TestClient):
        """Test updating nonexistent template returns 404."""
        response = client.put(
            "/api/v1/templates/nonexistent-id",
            params={"name": "New Name"}
        )

        assert response.status_code == 404


class TestDeleteTemplate:
    """Test DELETE /api/v1/templates/{template_id} endpoint."""

    def setup_method(self):
        """Clear and populate template store before each test."""
        store = get_template_store()
        store.clear()

    def test_delete_template_success(self, client: TestClient):
        """Test deleting a template successfully."""
        # Create template first
        create_response = client.post(
            "/api/v1/templates",
            params={
                "name": "To Delete",
                "file_path": "/templates/delete.docx",
            }
        )
        template_id = create_response.json()["template"]["id"]

        # Delete template
        response = client.delete(f"/api/v1/templates/{template_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Template deleted successfully"
        assert data["template_id"] == template_id

        # Verify it's deleted
        get_response = client.get(f"/api/v1/templates/{template_id}")
        assert get_response.status_code == 404

    def test_delete_template_not_found(self, client: TestClient):
        """Test deleting nonexistent template returns 404."""
        response = client.delete("/api/v1/templates/nonexistent-id")

        assert response.status_code == 404
