"""
End-to-end tests for the upload page UI.

These tests validate the complete user workflow using the web interface:
1. Access the upload page
2. Upload a file via form POST
3. Verify success response
"""

import io

import pytest
from fastapi.testclient import TestClient

from src.main import _file_storage, app
from src.repositories.database import get_db_manager
from migrations import File as FileModel


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


class TestUploadPage:
    """
    End-to-end tests for the upload page UI.

    Tests validate:
    - Page loads correctly
    - HTML structure is valid
    - JavaScript and CSS are served
    - File upload workflow works end-to-end
    """

    def test_upload_page_loads(self, client: TestClient) -> None:
        """
        Test that the upload page loads and returns valid HTML.

        Note: Accesses /static/index.html directly to bypass onboarding.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")

        # Verify response status
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

        # Verify HTML structure
        content = response.text
        assert "<!DOCTYPE html>" in content
        assert "<title>Fill - 2D Table Data Auto-Filling</title>" in content
        assert 'id="uploadArea"' in content
        assert 'id="fileInput"' in content
        assert 'id="uploadBtn"' in content

    def test_upload_page_has_form_elements(self, client: TestClient) -> None:
        """
        Test that the upload page contains required form elements.

        Note: Accesses /static/index.html directly to bypass onboarding.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # Check for file input
        assert 'type="file"' in content
        assert 'accept=".xlsx,.csv,.XLSX,.CSV"' in content

        # Check for upload button
        assert 'id="uploadBtn"' in content

        # Check for message area
        assert 'id="message"' in content

        # Check for progress bar
        assert 'id="progress"' in content
        assert 'id="progressFill"' in content

    def test_upload_page_has_styling(self, client: TestClient) -> None:
        """
        Test that the upload page includes CSS styling.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # Verify CSS is present
        assert "<style>" in content
        assert ".upload-area" in content
        assert ".btn" in content
        assert ".message" in content

    def test_upload_page_loads_javascript(self, client: TestClient) -> None:
        """
        Test that the upload page loads JavaScript.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # Verify JavaScript source is included (with /static/ prefix)
        assert 'src="/static/upload.js"' in content

    def test_javascript_file_served(self, client: TestClient) -> None:
        """
        Test that the upload.js JavaScript file is served correctly.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/upload.js")

        # Verify JavaScript file is served
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]

        # Verify JavaScript content
        content = response.text
        assert "uploadFile" in content
        assert "handleFileSelect" in content
        assert "formatFileSize" in content
        assert "/api/v1/upload" in content

    def test_complete_upload_workflow_csv(self, client: TestClient) -> None:
        """
        Test complete E2E workflow: upload CSV file via form POST.

        This simulates what happens when a user submits the upload form.

        Args:
            client: FastAPI test client
        """
        # Create test CSV file
        csv_content = b"name,age\nAlice,30\nBob,25"

        # Upload file using multipart/form-data (same as browser)
        files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        response = client.post("/api/v1/upload", files=files)

        # Verify upload success
        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "test.csv"
        assert data["status"] == "pending"
        assert "message" in data

    def test_complete_upload_workflow_xlsx(self, client: TestClient) -> None:
        """
        Test complete E2E workflow: upload XLSX file via form POST.

        Args:
            client: FastAPI test client
        """
        # Create test XLSX file (minimal valid XLSX)
        xlsx_content = b"PK\x03\x04" + b"\x00" * 100  # XLSX magic bytes

        files = {"file": ("test.xlsx", io.BytesIO(xlsx_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = client.post("/api/v1/upload", files=files)

        # Verify upload success
        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "test.xlsx"

    def test_upload_workflow_invalid_type(self, client: TestClient) -> None:
        """
        Test that invalid file types are rejected.

        Args:
            client: FastAPI test client
        """
        # Try to upload a text file (invalid type)
        txt_content = b"This is a text file"
        files = {"file": ("test.txt", io.BytesIO(txt_content), "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        # Verify upload fails with 400
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid file type" in data["detail"]

    def test_upload_workflow_file_too_large(self, client: TestClient) -> None:
        """
        Test that files exceeding 10MB limit are rejected.

        Args:
            client: FastAPI test client
        """
        # Create a file larger than 10MB (10MB + 1 byte)
        large_content = b"x" * (10 * 1024 * 1024 + 1)
        files = {"file": ("large.csv", io.BytesIO(large_content), "text/csv")}
        response = client.post("/api/v1/upload", files=files)

        # Verify upload fails with 413
        assert response.status_code == 413
        data = response.json()
        assert "detail" in data
        assert "exceeds maximum" in data["detail"]

    def test_upload_and_list_workflow(self, client: TestClient) -> None:
        """
        Test complete workflow: upload file -> list files -> verify presence.

        Args:
            client: FastAPI test client
        """
        # Upload a file
        csv_content = b"id,value\n1,first\n2,second"
        files = {"file": ("data.csv", io.BytesIO(csv_content), "text/csv")}
        upload_response = client.post("/api/v1/upload", files=files)

        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        file_id = upload_data["file_id"]

        # List files to verify it appears
        list_response = client.get("/api/v1/files")
        assert list_response.status_code == 200
        list_data = list_response.json()

        # Verify file is in the list
        assert list_data["total"] == 1
        assert len(list_data["files"]) == 1
        assert list_data["files"][0]["file_id"] == file_id
        assert list_data["files"][0]["filename"] == "data.csv"

    def test_upload_page_responsive_design(self, client: TestClient) -> None:
        """
        Test that the upload page has responsive design elements.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # Check for viewport meta tag (responsive design)
        assert '<meta name="viewport"' in content

        # Check for responsive CSS (media queries or flexbox)
        assert "min-height: 100vh" in content or "max-width" in content

    def test_upload_page_accessibility(self, client: TestClient) -> None:
        """
        Test that the upload page has basic accessibility features.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # Check for language attribute
        assert '<html lang="en">' in content

        # Check for proper heading structure
        assert "<h1>" in content

        # Check for labels or readable text
        assert "Drop your file here" in content or "click to browse" in content

    def test_upload_page_has_data_preview_section(self, client: TestClient) -> None:
        """
        Test that the upload page has a data preview section.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # Check for data preview container
        assert 'id="dataPreview"' in content

    def test_upload_page_has_preview_stats(self, client: TestClient) -> None:
        """
        Test that the data preview section includes stats display.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # Check for preview stats elements
        assert 'previewRowCount' in content
        assert 'previewColCount' in content

    def test_upload_page_has_preview_table(self, client: TestClient) -> None:
        """
        Test that the data preview section includes a table.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # Check for preview table
        assert 'id="previewTable"' in content

    def test_upload_page_has_preview_toggle(self, client: TestClient) -> None:
        """
        Test that the data preview section has a toggle button.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # Check for preview toggle button
        assert 'id="previewToggle"' in content
        assert 'previewToggleIcon' in content

    def test_upload_page_preview_css_is_styled(self, client: TestClient) -> None:
        """
        Test that the data preview section has proper CSS styling.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # Check for preview-related CSS classes
        assert '.data-preview' in content
        assert '.preview-header' in content
        assert '.preview-table' in content
        assert '.preview-stats' in content
