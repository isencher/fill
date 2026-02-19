"""
Integration tests for file upload endpoint.

Tests the POST /api/v1/upload endpoint with various scenarios.
"""

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from src.main import app, _uploaded_files


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: FastAPI test client instance
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_uploaded_files() -> None:
    """Clear the in-memory uploaded files storage before each test."""
    _uploaded_files.clear()
    yield
    _uploaded_files.clear()


class TestValidFileUpload:
    """Tests for valid file uploads."""

    def test_upload_csv_file_success(self, client: TestClient) -> None:
        """
        Test that uploading a valid CSV file succeeds.

        Args:
            client: FastAPI test client
        """
        # Create a mock CSV file
        file_content = b"name,age,city\nAlice,30,NYC\nBob,25,LA"
        files = {"file": ("test.csv", io.BytesIO(file_content), "text/csv")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "File uploaded successfully"
        assert "file_id" in data
        assert data["filename"] == "test.csv"
        assert data["size"] == len(file_content)
        assert data["status"] == "pending"

    def test_upload_xlsx_file_success(self, client: TestClient) -> None:
        """
        Test that uploading a valid Excel file succeeds.

        Args:
            client: FastAPI test client
        """
        # Create a mock XLSX file (simplified, just binary content)
        file_content = b"PK\x03\x04" + b"\x00" * 100  # XLSX header prefix
        files = {
            "file": (
                "data.xlsx",
                io.BytesIO(file_content),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "data.xlsx"

    def test_upload_with_uppercase_extension(self, client: TestClient) -> None:
        """
        Test that files with uppercase extensions are accepted.

        Args:
            client: FastAPI test client
        """
        file_content = b"data1,data2\nvalue1,value2"
        files = {"file": ("TEST.CSV", io.BytesIO(file_content), "text/csv")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 201
        assert response.json()["filename"] == "TEST.CSV"

    def test_upload_returns_unique_file_id(self, client: TestClient) -> None:
        """
        Test that each upload returns a unique file_id.

        Args:
            client: FastAPI test client
        """
        file_content = b"data"
        files = {"file": ("file1.csv", io.BytesIO(file_content), "text/csv")}

        response1 = client.post("/api/v1/upload", files=files)
        response2 = client.post("/api/v1/upload", files=files)

        file_id_1 = response1.json()["file_id"]
        file_id_2 = response2.json()["file_id"]

        assert file_id_1 != file_id_2

    def test_upload_small_file(self, client: TestClient) -> None:
        """
        Test that uploading a 1-byte file succeeds.

        Args:
            client: FastAPI test client
        """
        file_content = b"x"
        files = {"file": ("tiny.csv", io.BytesIO(file_content), "text/csv")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 201
        assert response.json()["size"] == 1


class TestInvalidFileType:
    """Tests for invalid file type rejection."""

    def test_upload_txt_file_rejected(self, client: TestClient) -> None:
        """
        Test that .txt files are rejected with 400 status.

        Args:
            client: FastAPI test client
        """
        file_content = b"some text content"
        files = {"file": ("document.txt", io.BytesIO(file_content), "text/plain")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_json_file_rejected(self, client: TestClient) -> None:
        """
        Test that .json files are rejected with 400 status.

        Args:
            client: FastAPI test client
        """
        file_content = b'{"key": "value"}'
        files = {"file": ("data.json", io.BytesIO(file_content), "application/json")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_pdf_file_rejected(self, client: TestClient) -> None:
        """
        Test that .pdf files are rejected with 400 status.

        Args:
            client: FastAPI test client
        """
        file_content = b"%PDF-1.4"
        files = {"file": ("doc.pdf", io.BytesIO(file_content), "application/pdf")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 400

    def test_upload_file_without_extension_rejected(self, client: TestClient) -> None:
        """
        Test that files without extensions are rejected.

        Args:
            client: FastAPI test client
        """
        file_content = b"some data"
        files = {"file": ("filename", io.BytesIO(file_content), "text/plain")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 400


class TestFileSizeValidation:
    """Tests for file size validation."""

    def test_upload_oversized_file_rejected(self, client: TestClient) -> None:
        """
        Test that files larger than 10MB are rejected with 413 status.

        Args:
            client: FastAPI test client
        """
        # Create a file larger than 10MB
        max_size = 10 * 1024 * 1024
        file_content = b"x" * (max_size + 1)
        files = {"file": ("large.csv", io.BytesIO(file_content), "text/csv")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 413
        assert "exceeds maximum allowed size" in response.json()["detail"]

    def test_upload_exactly_10mb_file_accepted(self, client: TestClient) -> None:
        """
        Test that a file exactly 10MB is accepted.

        Args:
            client: FastAPI test client
        """
        max_size = 10 * 1024 * 1024
        file_content = b"x" * max_size
        files = {"file": ("max_size.csv", io.BytesIO(file_content), "text/csv")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 201
        assert response.json()["size"] == max_size


class TestFileStorage:
    """Tests for file storage functionality."""

    def test_uploaded_file_metadata_stored(self, client: TestClient) -> None:
        """
        Test that uploaded file metadata is stored in memory.

        Args:
            client: FastAPI test client
        """
        file_content = b"test,data\nvalue1,value2"
        files = {"file": ("test.csv", io.BytesIO(file_content), "text/csv")}

        response = client.post("/api/v1/upload", files=files)
        file_id = response.json()["file_id"]

        # Verify the file metadata is stored (convert string to UUID)
        from uuid import UUID
        file_id_uuid = UUID(file_id)
        assert file_id_uuid in _uploaded_files
        stored_file = _uploaded_files[file_id_uuid]
        assert stored_file.filename == "test.csv"
        assert stored_file.size == len(file_content)

    def test_multiple_files_stored_separately(self, client: TestClient) -> None:
        """
        Test that multiple uploaded files are stored separately.

        Args:
            client: FastAPI test client
        """
        files = {
            "file": ("file1.csv", io.BytesIO(b"data1"), "text/csv")
        }
        response1 = client.post("/api/v1/upload", files=files)

        files = {
            "file": ("file2.csv", io.BytesIO(b"data2"), "text/csv")
        }
        response2 = client.post("/api/v1/upload", files=files)

        file_id_1 = response1.json()["file_id"]
        file_id_2 = response2.json()["file_id"]

        # Convert string IDs to UUID for dictionary lookup
        from uuid import UUID
        file_id_1_uuid = UUID(file_id_1)
        file_id_2_uuid = UUID(file_id_2)

        assert file_id_1_uuid in _uploaded_files
        assert file_id_2_uuid in _uploaded_files
        assert _uploaded_files[file_id_1_uuid].filename == "file1.csv"
        assert _uploaded_files[file_id_2_uuid].filename == "file2.csv"


class TestErrorResponseFormat:
    """Tests for error response format consistency."""

    def test_error_response_contains_detail(self, client: TestClient) -> None:
        """
        Test that error responses contain a 'detail' field.

        Args:
            client: FastAPI test client
        """
        files = {"file": ("bad.txt", io.BytesIO(b"data"), "text/plain")}
        response = client.post("/api/v1/upload", files=files)

        assert "detail" in response.json()

    def test_error_responses_use_correct_status_codes(self, client: TestClient) -> None:
        """
        Test that different error types return appropriate status codes.

        Args:
            client: FastAPI test client
        """
        # Invalid type -> 400
        response = client.post(
            "/api/v1/upload",
            files={"file": ("file.txt", io.BytesIO(b"x"), "text/plain")},
        )
        assert response.status_code == 400

        # File too large -> 413
        max_size = 10 * 1024 * 1024
        response = client.post(
            "/api/v1/upload",
            files={"file": ("large.csv", io.BytesIO(b"x" * (max_size + 1)), "text/csv")},
        )
        assert response.status_code == 413


class TestContentTypeHandling:
    """Tests for content type handling."""

    def test_upload_with_application_csv(self, client: TestClient) -> None:
        """
        Test that application/csv content type is accepted.

        Args:
            client: FastAPI test client
        """
        file_content = b"col1,col2\nval1,val2"
        files = {
            "file": ("data.csv", io.BytesIO(file_content), "application/csv")
        }

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 201

    def test_upload_with_legacy_excel_content_type(self, client: TestClient) -> None:
        """
        Test that legacy Excel content type is accepted.

        Args:
            client: FastAPI test client
        """
        file_content = b"PK\x03\x04" + b"\x00" * 100
        files = {
            "file": ("data.xlsx", io.BytesIO(file_content), "application/vnd.ms-excel")
        }

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 201
