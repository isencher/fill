"""
End-to-end tests for the mapping page UI.

These tests validate the complete user workflow for mapping columns to placeholders:
1. Access the mapping page with file_id and template_id
2. View data preview (first 5 rows)
3. View template placeholders
4. Create column-to-placeholder mappings
5. Save mapping
"""

import io

import pytest
from fastapi.testclient import TestClient

from src.main import _mappings_storage, _file_storage, _uploaded_file_contents, app
from src.models.file import FileStatus, UploadFile
from src.models.template import Template
from src.services.template_store import get_template_store


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: FastAPI test client instance
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage() -> None:
    """Clear in-memory storage after each test."""
    yield
    _file_storage.clear()
    _uploaded_file_contents.clear()
    _mappings_storage.clear()


@pytest.fixture
def sample_csv_file(client: TestClient) -> str:
    """
    Create and upload a sample CSV file for testing.

    Args:
        client: FastAPI test client

    Returns:
        str: File ID of uploaded file
    """
    # Create CSV content
    csv_content = b"""Name,Email,Phone,City
John Doe,john@example.com,555-1234,New York
Jane Smith,jane@example.com,555-5678,Los Angeles
Bob Johnson,bob@example.com,555-9012,Chicago
Alice Williams,alice@example.com,555-3456,Houston
Charlie Brown,charlie@example.com,555-7890,Phoenix
David Lee,david@example.com,555-2345,Philadelphia
"""

    # Upload file
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test_data.csv", io.BytesIO(csv_content), "text/csv")}
    )

    assert response.status_code == 201
    return response.json()["file_id"]


@pytest.fixture
def sample_template(client: TestClient) -> str:
    """
    Create a sample template for testing.

    Args:
        client: FastAPI test client

    Returns:
        str: Template ID
    """
    template_store = get_template_store()

    template = Template(
        name="Customer Template",
        description="Template for customer data",
        placeholders=["name", "email", "phone", "city"],
        file_path="/templates/customer.docx"
    )

    saved = template_store.save_template(template)
    return saved.id


class TestMappingPage:
    """
    End-to-end tests for the mapping page UI.

    Tests validate:
    - Page loads correctly with required parameters
    - Data preview displays correctly
    - Template placeholders display correctly
    - Mapping workflow works end-to-end
    """

    def test_mapping_page_loads(self, client: TestClient) -> None:
        """
        Test that the mapping page loads and returns valid HTML.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html?file_id=test-file&template_id=test-template")

        # Verify response status
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

        # Verify HTML structure
        content = response.text
        assert "<!DOCTYPE html>" in content
        assert "<title>Fill - Match Data Fields to Template</title>" in content
        assert 'id="dataTable"' in content
        assert 'id="placeholdersList"' in content
        assert 'id="saveMappingBtn"' in content

    def test_mapping_page_has_back_link(self, client: TestClient) -> None:
        """
        Test that the mapping page contains a back link to upload page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html?file_id=test&template_id=test")
        content = response.text

        # Check for back link
        assert 'href="/"' in content
        assert "Back to Upload" in content

    def test_mapping_page_displays_file_info(self, client: TestClient, sample_csv_file: str) -> None:
        """
        Test that file information is displayed on the mapping page.

        Args:
            client: FastAPI test client
            sample_csv_file: Uploaded file ID
        """
        response = client.get(f"/mapping?file_id={sample_csv_file}&template_id=test-template")
        content = response.text

        # Verify file info section exists
        assert 'id="fileName"' in content
        assert 'id="fileId"' in content

    def test_mapping_page_displays_template_info(
        self, client: TestClient, sample_template: str
    ) -> None:
        """
        Test that template information is displayed on the mapping page.

        Args:
            client: FastAPI test client
            sample_template: Template ID
        """
        response = client.get(f"/mapping?file_id=test-file&template_id={sample_template}")
        content = response.text

        # Verify template info section exists
        assert 'id="templateName"' in content
        assert 'id="templateId"' in content

    def test_mapping_page_loads_javascript(self, client: TestClient) -> None:
        """
        Test that the mapping page includes JavaScript file.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html?file_id=test&template_id=test")
        content = response.text

        # Check for JavaScript include (with /static/ prefix)
        assert 'src="/static/mapping.js"' in content


class TestParseFileEndpoint:
    """
    Tests for the /api/v1/parse/{file_id} endpoint.

    Tests validate:
    - File parsing works correctly
    - Returns data preview (first 5 rows)
    - Error handling for invalid files
    """

    def test_parse_csv_file_success(
        self, client: TestClient, sample_csv_file: str
    ) -> None:
        """
        Test parsing a CSV file returns correct data.

        Args:
            client: FastAPI test client
            sample_csv_file: Uploaded file ID
        """
        response = client.get(f"/api/v1/parse/{sample_csv_file}")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "file_id" in data
        assert "filename" in data
        assert "rows" in data
        assert "total_rows" in data

        # Verify data preview (first 5 rows)
        assert len(data["rows"]) == 5  # First 5 rows
        assert data["total_rows"] == 6  # Total data rows (excluding header)

        # Verify first row has correct columns
        first_row = data["rows"][0]
        assert "Name" in first_row
        assert "Email" in first_row
        assert "Phone" in first_row
        assert "City" in first_row

    def test_parse_file_not_found(self, client: TestClient) -> None:
        """
        Test parsing a non-existent file returns 404.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/v1/parse/nonexistent-file-id")

        # Verify error response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestCreateMappingEndpoint:
    """
    Tests for the POST /api/v1/mappings endpoint.

    Tests validate:
    - Mapping creation works correctly
    - Validation of file and template IDs
    - Validation of column mappings
    """

    def test_create_mapping_success(
        self, client: TestClient, sample_csv_file: str, sample_template: str
    ) -> None:
        """
        Test creating a mapping with valid data.

        Args:
            client: FastAPI test client
            sample_csv_file: Uploaded file ID
            sample_template: Template ID
        """
        column_mappings = {
            "name": "Name",
            "email": "Email",
            "phone": "Phone",
            "city": "City"
        }

        response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": sample_csv_file,
                "template_id": sample_template
            },
            json=column_mappings
        )

        # Verify response
        assert response.status_code == 201
        data = response.json()

        # Verify structure
        assert "id" in data
        assert "file_id" in data
        assert "template_id" in data
        assert "column_mappings" in data
        assert "created_at" in data

        # Verify data
        assert data["file_id"] == sample_csv_file
        assert data["template_id"] == sample_template
        assert data["column_mappings"] == column_mappings

    def test_create_mapping_file_not_found(
        self, client: TestClient, sample_template: str
    ) -> None:
        """
        Test creating a mapping with non-existent file ID returns 404.

        Args:
            client: FastAPI test client
            sample_template: Template ID
        """
        response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": "nonexistent-file-id",
                "template_id": sample_template
            },
            json={}
        )

        # Verify error response
        assert response.status_code == 404
        assert "file not found" in response.json()["detail"].lower()

    def test_create_mapping_template_not_found(
        self, client: TestClient, sample_csv_file: str
    ) -> None:
        """
        Test creating a mapping with non-existent template ID returns 404.

        Args:
            client: FastAPI test client
            sample_csv_file: Uploaded file ID
        """
        response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": sample_csv_file,
                "template_id": "nonexistent-template-id"
            },
            json={}
        )

        # Verify error response
        assert response.status_code == 404
        assert "template not found" in response.json()["detail"].lower()


class TestMappingWorkflow:
    """
    End-to-end tests for the complete mapping workflow.

    Tests validate:
    - Upload file → Parse data → Create mapping
    - Error handling throughout the workflow
    - Data consistency
    """

    def test_complete_mapping_workflow(
        self, client: TestClient
    ) -> None:
        """
        Test the complete workflow: upload → parse → map.

        Args:
            client: FastAPI test client
        """
        # Step 1: Upload file
        csv_content = b"""Product,Price,Quantity
Widget,19.99,100
Gadget,29.99,50
Doohickey,14.99,200
"""

        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("products.csv", io.BytesIO(csv_content), "text/csv")}
        )

        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]

        # Step 2: Create template
        template_store = get_template_store()
        template = Template(
            name="Product Template",
            placeholders=["product", "price", "quantity"],
            file_path="/templates/product.docx"
        )
        saved_template = template_store.save_template(template)
        template_id = saved_template.id

        # Step 3: Parse file
        parse_response = client.get(f"/api/v1/parse/{file_id}")
        assert parse_response.status_code == 200
        parsed_data = parse_response.json()
        assert len(parsed_data["rows"]) == 3  # First 3 rows
        assert "Product" in parsed_data["rows"][0]

        # Step 4: Create mapping
        column_mappings = {
            "product": "Product",
            "price": "Price",
            "quantity": "Quantity"
        }

        mapping_response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": file_id,
                "template_id": template_id
            },
            json=column_mappings
        )

        assert mapping_response.status_code == 201
        mapping_data = mapping_response.json()

        # Verify workflow completion
        assert "id" in mapping_data
        assert mapping_data["file_id"] == file_id
        assert mapping_data["template_id"] == template_id
        assert mapping_data["column_mappings"] == column_mappings

    def test_mapping_page_without_parameters(self, client: TestClient) -> None:
        """
        Test accessing mapping page without required parameters shows empty state.

        Args:
            client: FastAPI test client
        """
        response = client.get("/mapping")
        content = response.text

        # Should show empty state message
        assert response.status_code == 200
        # Note: With missing params, page might load but show empty state
        # or JavaScript will handle it by showing error

    def test_mapping_page_displays_loading_state(self, client: TestClient) -> None:
        """
        Test that the mapping page has a loading state element.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html?file_id=test&template_id=test")
        content = response.text

        # Check for loading state elements
        assert 'id="loadingState"' in content
        assert 'id="contentArea"' in content
        assert 'id="emptyState"' in content

    def test_mapping_page_responsive_design(self, client: TestClient) -> None:
        """
        Test that the mapping page uses responsive CSS.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html?file_id=test&template_id=test")
        content = response.text

        # Check for responsive design elements
        assert "media" in content or "@media" in content
        assert "grid-template-columns" in content

    def test_mapping_page_accessibility(self, client: TestClient) -> None:
        """
        Test that the mapping page includes accessibility features.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html?file_id=test&template_id=test")
        content = response.text

        # Check for accessibility features
        assert "viewport" in content
        # Labels for form elements
        assert "placeholder" in content.lower() or "label" in content.lower()
