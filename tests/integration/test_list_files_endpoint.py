"""
Integration tests for file listing endpoint.

Tests the GET /api/v1/files endpoint with various scenarios.
"""

import io

import pytest
from fastapi.testclient import TestClient

from src.main import _file_storage, app
from src.models.file import FileStatus


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: FastAPI test client instance
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_file_storage() -> None:
    """Clear in-memory uploaded files storage before each test."""
    _file_storage.clear()
    yield
    _file_storage.clear()


class TestListFilesBasic:
    """Tests for basic file listing functionality."""

    def test_list_files_empty_storage(self, client: TestClient) -> None:
        """
        Test that listing files when storage is empty returns empty list.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/v1/files")

        assert response.status_code == 200
        data = response.json()
        assert data["files"] == []
        assert data["total"] == 0
        assert data["limit"] == 100
        assert data["offset"] == 0
        assert data["has_more"] is False

    def test_list_files_single_file(self, client: TestClient) -> None:
        """
        Test that listing a single uploaded file returns correct data.

        Args:
            client: FastAPI test client
        """
        # Upload a file first
        file_content = b"name,age\nAlice,30"
        files = {"file": ("test.csv", io.BytesIO(file_content), "text/csv")}
        upload_response = client.post("/api/v1/upload", files=files)

        # Then list files
        response = client.get("/api/v1/files")

        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 1
        assert data["total"] == 1
        assert data["files"][0]["file_id"] == upload_response.json()["file_id"]
        assert data["files"][0]["filename"] == "test.csv"
        assert data["files"][0]["size"] == len(file_content)
        assert data["files"][0]["status"] == "pending"

    def test_list_files_multiple_files(self, client: TestClient) -> None:
        """
        Test that listing multiple files returns all files.

        Args:
            client: FastAPI test client
        """
        # Upload multiple files
        file1 = ("file1.csv", io.BytesIO(b"data1"), "text/csv")
        file2 = ("file2.csv", io.BytesIO(b"data2"), "text/csv")
        file3 = ("file3.csv", io.BytesIO(b"data3"), "text/csv")

        client.post("/api/v1/upload", files={"file": file1})
        client.post("/api/v1/upload", files={"file": file2})
        client.post("/api/v1/upload", files={"file": file3})

        response = client.get("/api/v1/files")

        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 3
        assert data["total"] == 3
        assert data["has_more"] is False

    def test_list_files_sorted_by_upload_date_desc(self, client: TestClient) -> None:
        """
        Test that files are sorted by upload date, newest first.

        Args:
            client: FastAPI test client
        """
        # Upload files in sequence
        response1 = client.post(
            "/api/v1/upload",
            files={"file": ("first.csv", io.BytesIO(b"first"), "text/csv")},
        )
        response2 = client.post(
            "/api/v1/upload",
            files={"file": ("second.csv", io.BytesIO(b"second"), "text/csv")},
        )
        response3 = client.post(
            "/api/v1/upload",
            files={"file": ("third.csv", io.BytesIO(b"third"), "text/csv")},
        )

        response = client.get("/api/v1/files")
        data = response.json()

        # Newest first
        assert data["files"][0]["filename"] == "third.csv"
        assert data["files"][1]["filename"] == "second.csv"
        assert data["files"][2]["filename"] == "first.csv"


class TestListFilesPagination:
    """Tests for pagination functionality."""

    def test_list_files_with_limit(self, client: TestClient) -> None:
        """
        Test that limit parameter correctly restricts number of results.

        Args:
            client: FastAPI test client
        """
        # Upload 5 files
        for i in range(5):
            client.post(
                "/api/v1/upload",
                files={"file": (f"file{i}.csv", io.BytesIO(b"data"), "text/csv")},
            )

        response = client.get("/api/v1/files?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 3
        assert data["total"] == 5
        assert data["limit"] == 3
        assert data["has_more"] is True

    def test_list_files_with_offset(self, client: TestClient) -> None:
        """
        Test that offset parameter correctly skips files.

        Args:
            client: FastAPI test client
        """
        # Upload 5 files
        filenames = []
        for i in range(5):
            filename = f"file{i}.csv"
            filenames.append(filename)
            client.post(
                "/api/v1/upload",
                files={"file": (filename, io.BytesIO(b"data"), "text/csv")},
            )

        response = client.get("/api/v1/files?offset=2&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 2
        assert data["total"] == 5
        assert data["offset"] == 2

    def test_list_files_with_limit_and_offset(self, client: TestClient) -> None:
        """
        Test that limit and offset work together correctly.

        Args:
            client: FastAPI test client
        """
        # Upload 10 files
        for i in range(10):
            client.post(
                "/api/v1/upload",
                files={"file": (f"file{i}.csv", io.BytesIO(b"data"), "text/csv")},
            )

        response = client.get("/api/v1/files?limit=3&offset=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 3
        assert data["total"] == 10
        assert data["limit"] == 3
        assert data["offset"] == 5
        assert data["has_more"] is True  # 5 + 3 = 8 < 10

    def test_list_files_has_more_flag(self, client: TestClient) -> None:
        """
        Test that has_more flag is calculated correctly.

        Args:
            client: FastAPI test client
        """
        # Upload 10 files
        for i in range(10):
            client.post(
                "/api/v1/upload",
                files={"file": (f"file{i}.csv", io.BytesIO(b"data"), "text/csv")},
            )

        # First page - has more
        response1 = client.get("/api/v1/files?limit=5&offset=0")
        assert response1.json()["has_more"] is True

        # Last full page - no more
        response2 = client.get("/api/v1/files?limit=5&offset=5")
        assert response2.json()["has_more"] is False

        # Exact match - no more
        response3 = client.get("/api/v1/files?limit=10&offset=0")
        assert response3.json()["has_more"] is False

    def test_list_files_offset_beyond_count(self, client: TestClient) -> None:
        """
        Test that offset beyond file count returns empty list.

        Args:
            client: FastAPI test client
        """
        # Upload 3 files
        for i in range(3):
            client.post(
                "/api/v1/upload",
                files={"file": (f"file{i}.csv", io.BytesIO(b"data"), "text/csv")},
            )

        response = client.get("/api/v1/files?offset=10")

        assert response.status_code == 200
        data = response.json()
        assert data["files"] == []
        assert data["total"] == 3
        assert data["offset"] == 10
        assert data["has_more"] is False

    def test_list_files_default_limit(self, client: TestClient) -> None:
        """
        Test that default limit is 100 when not specified.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/v1/files")

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 100


class TestListFilesParameterValidation:
    """Tests for parameter validation."""

    def test_list_files_limit_minimum(self, client: TestClient) -> None:
        """
        Test that limit must be at least 1.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/v1/files?limit=0")

        assert response.status_code == 422  # Validation error

    def test_list_files_limit_maximum(self, client: TestClient) -> None:
        """
        Test that limit cannot exceed 1000.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/v1/files?limit=1001")

        assert response.status_code == 422  # Validation error

    def test_list_files_maximum_allowed_limit(self, client: TestClient) -> None:
        """
        Test that limit of exactly 1000 is accepted.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/v1/files?limit=1000")

        assert response.status_code == 200

    def test_list_files_offset_negative(self, client: TestClient) -> None:
        """
        Test that offset cannot be negative.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/v1/files?offset=-1")

        assert response.status_code == 422  # Validation error


class TestListFilesResponseFormat:
    """Tests for response format consistency."""

    def test_list_files_response_structure(self, client: TestClient) -> None:
        """
        Test that response contains all required fields.

        Args:
            client: FastAPI test client
        """
        # Upload a file first
        files = {"file": ("test.csv", io.BytesIO(b"data"), "text/csv")}
        client.post("/api/v1/upload", files=files)

        response = client.get("/api/v1/files")
        data = response.json()

        # Check top-level structure
        assert "files" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data

        # Check file object structure
        file_data = data["files"][0]
        assert "file_id" in file_data
        assert "filename" in file_data
        assert "content_type" in file_data
        assert "size" in file_data
        assert "uploaded_at" in file_data
        assert "status" in file_data

    def test_list_files_upload_timestamp_format(self, client: TestClient) -> None:
        """
        Test that uploaded_at is returned in ISO 8601 format.

        Args:
            client: FastAPI test client
        """
        files = {"file": ("test.csv", io.BytesIO(b"data"), "text/csv")}
        client.post("/api/v1/upload", files=files)

        response = client.get("/api/v1/files")
        file_data = response.json()["files"][0]

        # ISO 8601 format should contain 'T' and end with 'Z' or timezone
        assert "T" in file_data["uploaded_at"]

    def test_list_files_status_enum_value(self, client: TestClient) -> None:
        """
        Test that status is returned as string value, not enum.

        Args:
            client: FastAPI test client
        """
        files = {"file": ("test.csv", io.BytesIO(b"data"), "text/csv")}
        client.post("/api/v1/upload", files=files)

        response = client.get("/api/v1/files")
        file_data = response.json()["files"][0]

        assert isinstance(file_data["status"], str)
        assert file_data["status"] == FileStatus.PENDING.value

    def test_list_files_file_id_is_string(self, client: TestClient) -> None:
        """
        Test that file_id is returned as string, not UUID.

        Args:
            client: FastAPI test client
        """
        files = {"file": ("test.csv", io.BytesIO(b"data"), "text/csv")}
        upload_response = client.post("/api/v1/upload", files=files)

        response = client.get("/api/v1/files")
        file_data = response.json()["files"][0]

        assert isinstance(file_data["file_id"], str)
        assert file_data["file_id"] == upload_response.json()["file_id"]


class TestListFilesEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_list_files_with_large_offset(self, client: TestClient) -> None:
        """
        Test that very large offset returns empty list gracefully.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/v1/files?offset=999999")

        assert response.status_code == 200
        data = response.json()
        assert data["files"] == []
        assert data["total"] == 0

    def test_list_files_with_one_per_page(self, client: TestClient) -> None:
        """
        Test pagination with limit=1.

        Args:
            client: FastAPI test client
        """
        # Upload 3 files
        for i in range(3):
            client.post(
                "/api/v1/upload",
                files={"file": (f"file{i}.csv", io.BytesIO(b"data"), "text/csv")},
            )

        response1 = client.get("/api/v1/files?limit=1&offset=0")
        response2 = client.get("/api/v1/files?limit=1&offset=1")
        response3 = client.get("/api/v1/files?limit=1&offset=2")

        assert len(response1.json()["files"]) == 1
        assert len(response2.json()["files"]) == 1
        assert len(response3.json()["files"]) == 1

    def test_list_files_content_types_preserved(self, client: TestClient) -> None:
        """
        Test that different content types are preserved in listings.

        Args:
            client: FastAPI test client
        """
        # Upload files with different content types
        client.post(
            "/api/v1/upload",
            files={
                "file": (
                    "file1.csv",
                    io.BytesIO(b"data1"),
                    "text/csv",
                )
            },
        )
        client.post(
            "/api/v1/upload",
            files={
                "file": (
                    "file2.xlsx",
                    io.BytesIO(b"PK\x03\x04"),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

        response = client.get("/api/v1/files")
        files = response.json()["files"]

        assert len(files) == 2
        content_types = {f["content_type"] for f in files}
        assert "text/csv" in content_types
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in content_types
