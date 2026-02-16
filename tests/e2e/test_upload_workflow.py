"""
End-to-end tests for the file upload workflow.

These tests validate the complete user workflow from upload to retrieval.
Since there is no UI, tests operate at the API level.
"""

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.main import _file_storage, app


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


class TestUploadWorkflow:
    """
    End-to-end tests for the complete file upload workflow.

    Workflow:
    1. Upload a file
    2. List files to verify it appears
    3. Verify file metadata is correct
    """

    def test_complete_csv_upload_workflow(self, client: TestClient) -> None:
        """
        Test complete workflow: upload CSV file -> verify in list -> check metadata.

        Args:
            client: FastAPI test client
        """
        # Step 1: Upload a CSV file
        file_content = b"name,age,city\nAlice,30,NYC\nBob,25,LA"
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("employees.csv", io.BytesIO(file_content), "text/csv")},
        )

        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        file_id = upload_data["file_id"]

        # Verify upload response
        assert upload_data["message"] == "File uploaded successfully"
        assert upload_data["filename"] == "employees.csv"
        assert upload_data["size"] == len(file_content)
        assert upload_data["status"] == "pending"

        # Step 2: List files to verify the uploaded file appears
        list_response = client.get("/api/v1/files")
        assert list_response.status_code == 200

        list_data = list_response.json()
        assert list_data["total"] == 1
        assert len(list_data["files"]) == 1

        # Step 3: Verify file metadata in list matches upload response
        listed_file = list_data["files"][0]
        assert listed_file["file_id"] == file_id
        assert listed_file["filename"] == "employees.csv"
        assert listed_file["content_type"] == "text/csv"
        assert listed_file["size"] == len(file_content)
        assert listed_file["status"] == "pending"
        assert "uploaded_at" in listed_file

    def test_complete_xlsx_upload_workflow(self, client: TestClient) -> None:
        """
        Test complete workflow: upload Excel file -> verify in list.

        Args:
            client: FastAPI test client
        """
        # Step 1: Upload an Excel file
        file_content = b"PK\x03\x04" + b"\x00" * 100  # XLSX header prefix
        upload_response = client.post(
            "/api/v1/upload",
            files={
                "file": (
                    "report.xlsx",
                    io.BytesIO(file_content),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]

        # Step 2: Verify file appears in list
        list_response = client.get("/api/v1/files")
        list_data = list_response.json()

        assert list_data["total"] == 1
        assert list_data["files"][0]["file_id"] == file_id
        assert list_data["files"][0]["filename"] == "report.xlsx"
        assert list_data["files"][0]["content_type"] == (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def test_multiple_uploads_appear_in_list(self, client: TestClient) -> None:
        """
        Test uploading multiple files and verifying all appear in list.

        Args:
            client: FastAPI test client
        """
        # Step 1: Upload multiple files
        files_to_upload = [
            ("file1.csv", b"data1", "text/csv"),
            ("file2.csv", b"data2", "text/csv"),
            ("file3.csv", b"data3", "text/csv"),
        ]

        file_ids = []
        for filename, content, content_type in files_to_upload:
            response = client.post(
                "/api/v1/upload",
                files={"file": (filename, io.BytesIO(content), content_type)},
            )
            assert response.status_code == 201
            file_ids.append(response.json()["file_id"])

        # Step 2: Verify all files appear in list
        list_response = client.get("/api/v1/files")
        list_data = list_response.json()

        assert list_data["total"] == 3
        assert len(list_data["files"]) == 3

        # Verify all file_ids are present
        listed_ids = {f["file_id"] for f in list_data["files"]}
        assert set(file_ids) == listed_ids

    def test_upload_and_pagination_workflow(self, client: TestClient) -> None:
        """
        Test uploading many files and verifying pagination works correctly.

        Args:
            client: FastAPI test client
        """
        # Step 1: Upload 5 files
        for i in range(5):
            client.post(
                "/api/v1/upload",
                files={"file": (f"file{i}.csv", io.BytesIO(f"data{i}".encode()), "text/csv")},
            )

        # Step 2: Test pagination - first page
        page1 = client.get("/api/v1/files?limit=2&offset=0")
        page1_data = page1.json()
        assert page1_data["total"] == 5
        assert len(page1_data["files"]) == 2
        assert page1_data["has_more"] is True

        # Step 3: Test pagination - second page
        page2 = client.get("/api/v1/files?limit=2&offset=2")
        page2_data = page2.json()
        assert len(page2_data["files"]) == 2
        assert page2_data["has_more"] is True

        # Step 4: Test pagination - last page
        page3 = client.get("/api/v1/files?limit=2&offset=4")
        page3_data = page3.json()
        assert len(page3_data["files"]) == 1
        assert page3_data["has_more"] is False


class TestUploadErrorWorkflow:
    """
    End-to-end tests for error handling in the upload workflow.
    """

    def test_invalid_upload_does_not_affect_file_list(self, client: TestClient) -> None:
        """
        Test that an invalid upload (e.g., wrong file type) doesn't create a file entry.

        Args:
            client: FastAPI test client
        """
        # Step 1: Upload a valid file
        valid_response = client.post(
            "/api/v1/upload",
            files={"file": ("valid.csv", io.BytesIO(b"data"), "text/csv")},
        )
        assert valid_response.status_code == 201

        # Step 2: Try to upload an invalid file type
        invalid_response = client.post(
            "/api/v1/upload",
            files={"file": ("invalid.txt", io.BytesIO(b"data"), "text/plain")},
        )
        assert invalid_response.status_code == 400

        # Step 3: Verify only the valid file appears in the list
        list_response = client.get("/api/v1/files")
        list_data = list_response.json()

        assert list_data["total"] == 1
        assert list_data["files"][0]["filename"] == "valid.csv"

    def test_oversized_file_rejected_and_list_unchanged(self, client: TestClient) -> None:
        """
        Test that an oversized file is rejected and doesn't affect the file list.

        Args:
            client: FastAPI test client
        """
        # Step 1: Upload a valid file
        client.post(
            "/api/v1/upload",
            files={"file": ("small.csv", io.BytesIO(b"small data"), "text/csv")},
        )

        # Step 2: Try to upload a file larger than 10MB
        max_size = 10 * 1024 * 1024
        oversized_response = client.post(
            "/api/v1/upload",
            files={"file": ("large.csv", io.BytesIO(b"x" * (max_size + 1)), "text/csv")},
        )
        assert oversized_response.status_code == 413

        # Step 3: Verify only the small file is in the list
        list_response = client.get("/api/v1/files")
        list_data = list_response.json()

        assert list_data["total"] == 1
        assert list_data["files"][0]["filename"] == "small.csv"


class TestUploadDataConsistency:
    """
    End-to-end tests for data consistency across upload and listing.
    """

    def test_file_size_consistency(self, client: TestClient) -> None:
        """
        Test that file size is consistent between upload response and list response.

        Args:
            client: FastAPI test client
        """
        content = b"test,data,value\n1,2,3"
        size = len(content)

        # Upload
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("test.csv", io.BytesIO(content), "text/csv")},
        )

        upload_size = upload_response.json()["size"]

        # List
        list_response = client.get("/api/v1/files")
        list_size = list_response.json()["files"][0]["size"]

        assert upload_size == size
        assert list_size == size
        assert upload_size == list_size

    def test_filename_preserved_through_workflow(self, client: TestClient) -> None:
        """
        Test that filename is preserved exactly as uploaded.

        Args:
            client: FastAPI test client
        """
        original_filename = "MyDataFile.CSV"

        # Upload
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": (original_filename, io.BytesIO(b"data"), "text/csv")},
        )

        upload_filename = upload_response.json()["filename"]

        # List
        list_response = client.get("/api/v1/files")
        list_filename = list_response.json()["files"][0]["filename"]

        assert upload_filename == original_filename
        assert list_filename == original_filename

    def test_content_type_preserved_through_workflow(self, client: TestClient) -> None:
        """
        Test that content type is preserved correctly.

        Args:
            client: FastAPI test client
        """
        content_type = "application/csv"

        # Upload
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("test.csv", io.BytesIO(b"data"), content_type)},
        )
        upload_response_data = upload_response.json()

        # Note: Upload response doesn't include content_type, but list does
        file_id = upload_response_data["file_id"]

        # List
        list_response = client.get("/api/v1/files")
        files = list_response.json()["files"]

        # Find our file
        our_file = next(f for f in files if f["file_id"] == file_id)
        assert our_file["content_type"] == content_type


class TestUploadSorting:
    """
    End-to-end tests for file sorting in the listing.
    """

    def test_files_sorted_newest_first(self, client: TestClient) -> None:
        """
        Test that files are sorted by upload date, newest first.

        Args:
            client: FastAPI test client
        """
        # Step 1: Upload files in sequence
        file_ids = []
        for i in range(3):
            response = client.post(
                "/api/v1/upload",
                files={
                    "file": (
                        f"file{i}.csv",
                        io.BytesIO(f"data{i}".encode()),
                        "text/csv",
                    )
                },
            )
            file_ids.append((i, response.json()["file_id"]))

        # Step 2: Verify newest (highest index) appears first
        list_response = client.get("/api/v1/files")
        files = list_response.json()["files"]

        # The last uploaded file should be first in the list
        assert files[0]["file_id"] == file_ids[2][1]
        assert files[1]["file_id"] == file_ids[1][1]
        assert files[2]["file_id"] == file_ids[0][1]


class TestEdgeCaseWorkflows:
    """
    End-to-end tests for edge case workflows.
    """

    def test_empty_list_before_first_upload(self, client: TestClient) -> None:
        """
        Test that file list is empty before any uploads.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/v1/files")
        data = response.json()

        assert data["total"] == 0
        assert data["files"] == []
        assert data["has_more"] is False

    def test_list_with_limit_of_one(self, client: TestClient) -> None:
        """
        Test listing files with limit=1 (smallest allowed value).

        Args:
            client: FastAPI test client
        """
        # Upload 3 files
        for i in range(3):
            client.post(
                "/api/v1/upload",
                files={"file": (f"file{i}.csv", io.BytesIO(b"data"), "text/csv")},
            )

        # List with limit=1
        response = client.get("/api/v1/files?limit=1")
        data = response.json()

        assert len(data["files"]) == 1
        assert data["total"] == 3
        assert data["has_more"] is True

    def test_maximum_limit_value(self, client: TestClient) -> None:
        """
        Test that maximum limit value (1000) works correctly.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/v1/files?limit=1000")

        # Should not error, even with no files
        assert response.status_code == 200
        assert response.json()["limit"] == 1000

    def test_upload_same_filename_multiple_times(self, client: TestClient) -> None:
        """
        Test uploading the same filename multiple times creates separate entries.

        Args:
            client: FastAPI test client
        """
        filename = "data.csv"

        # Upload same filename 3 times
        responses = []
        for _ in range(3):
            response = client.post(
                "/api/v1/upload",
                files={"file": (filename, io.BytesIO(b"data"), "text/csv")},
            )
            assert response.status_code == 201
            responses.append(response.json())

        # All should have different file_ids
        file_ids = [r["file_id"] for r in responses]
        assert len(set(file_ids)) == 3

        # List should show 3 files
        list_response = client.get("/api/v1/files")
        assert list_response.json()["total"] == 3
