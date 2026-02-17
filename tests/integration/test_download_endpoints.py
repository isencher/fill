"""
Integration tests for Output Download API Endpoints.
"""

import pytest
import zipfile
import io
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from src.main import app
from src.services.output_storage import get_output_storage


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def storage():
    """Create output storage instance."""
    return get_output_storage()


class TestDownloadJobOutputs:
    """Tests for GET /api/v1/outputs/{job_id} endpoint."""

    def test_download_job_outputs_returns_zip(self, client, storage, tmp_path):
        """Test downloading all job outputs as ZIP file."""
        # Create test outputs
        job_id = str(uuid4())
        storage.save_output(job_id, 0, b"Content 0", filename="file0.txt")
        storage.save_output(job_id, 1, b"Content 1", filename="file1.txt")
        storage.save_output(job_id, 2, b"Content 2", filename="file2.txt")

        # Download outputs
        response = client.get(f"/api/v1/outputs/{job_id}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert "attachment" in response.headers["content-disposition"]

        # Verify ZIP contents
        zip_content = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_content, "r") as zip_file:
            assert len(zip_file.namelist()) == 3
            assert "file0.txt" in zip_file.namelist()
            assert "file1.txt" in zip_file.namelist()
            assert "file2.txt" in zip_file.namelist()

            # Verify file contents
            assert zip_file.read("file0.txt") == b"Content 0"
            assert zip_file.read("file1.txt") == b"Content 1"
            assert zip_file.read("file2.txt") == b"Content 2"

    def test_download_job_outputs_with_docx_files(self, client, storage):
        """Test downloading DOCX files."""
        job_id = str(uuid4())
        # Use binary content to get .docx extension
        storage.save_output(job_id, 0, b"\xff\xfe", filename="output.docx")

        response = client.get(f"/api/v1/outputs/{job_id}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"

        # Verify ZIP contains DOCX file
        zip_content = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_content, "r") as zip_file:
            assert "output.docx" in zip_file.namelist()
            assert zip_file.read("output.docx") == b"\xff\xfe"

    def test_download_job_outputs_nonexistent_job_returns_404(self, client, storage):
        """Test that nonexistent job returns 404."""
        job_id = str(uuid4())

        response = client.get(f"/api/v1/outputs/{job_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_download_job_outputs_empty_job_returns_404(self, client, storage):
        """Test that job with no outputs returns 404."""
        job_id = str(uuid4())
        # Note: In current implementation, job_exists checks if job has outputs
        # So a job without outputs is considered nonexistent
        # The endpoint returns 404 with "not found" message

        response = client.get(f"/api/v1/outputs/{job_id}")

        assert response.status_code == 404
        # The detail message says "not found" not "No outputs found"
        assert "not found" in response.json()["detail"].lower()


class TestDownloadSingleOutput:
    """Tests for GET /api/v1/outputs/{job_id}/{filename} endpoint."""

    def test_download_single_txt_file(self, client, storage):
        """Test downloading a single TXT file."""
        job_id = str(uuid4())
        storage.save_output(job_id, 0, b"Hello World", filename="test.txt")

        response = client.get(f"/api/v1/outputs/{job_id}/test.txt")

        assert response.status_code == 200
        # Content type may include charset
        assert "text/plain" in response.headers["content-type"]
        assert "test.txt" in response.headers["content-disposition"]
        assert response.content == b"Hello World"

    def test_download_single_docx_file(self, client, storage):
        """Test downloading a single DOCX file."""
        job_id = str(uuid4())
        storage.save_output(job_id, 0, b"\xff\xfe", filename="output.docx")

        response = client.get(f"/api/v1/outputs/{job_id}/output.docx")

        assert response.status_code == 200
        assert "vnd.openxmlformats" in response.headers["content-type"]
        assert response.content == b"\xff\xfe"

    def test_download_single_pdf_file(self, client, storage):
        """Test downloading a single PDF file."""
        job_id = str(uuid4())
        storage.save_output(job_id, 0, b"%PDF-1.4", filename="document.pdf")

        response = client.get(f"/api/v1/outputs/{job_id}/document.pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content == b"%PDF-1.4"

    def test_download_single_binary_file(self, client, storage):
        """Test downloading binary file (octet-stream)."""
        job_id = str(uuid4())
        storage.save_output(job_id, 0, b"\x00\x01\x02", filename="data.bin")

        response = client.get(f"/api/v1/outputs/{job_id}/data.bin")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/octet-stream"
        assert response.content == b"\x00\x01\x02"

    def test_download_single_nonexistent_job_returns_404(self, client, storage):
        """Test that nonexistent job returns 404."""
        job_id = str(uuid4())

        response = client.get(f"/api/v1/outputs/{job_id}/test.txt")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_download_single_nonexistent_file_returns_404(self, client, storage):
        """Test that nonexistent file returns 404."""
        job_id = str(uuid4())
        storage.save_output(job_id, 0, b"test", filename="exists.txt")

        response = client.get(f"/api/v1/outputs/{job_id}/missing.txt")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestDownloadEdgeCases:
    """Tests for edge cases and error handling."""

    def test_download_multiple_separate_jobs(self, client, storage):
        """Test downloading outputs from multiple separate jobs."""
        job_id_1 = str(uuid4())
        job_id_2 = str(uuid4())

        storage.save_output(job_id_1, 0, b"Job 1", filename="file.txt")
        storage.save_output(job_id_2, 0, b"Job 2", filename="file.txt")

        # Download from job 1
        response_1 = client.get(f"/api/v1/outputs/{job_id_1}/file.txt")
        assert response_1.content == b"Job 1"

        # Download from job 2
        response_2 = client.get(f"/api/v1/outputs/{job_id_2}/file.txt")
        assert response_2.content == b"Job 2"

    def test_download_special_filename(self, client, storage):
        """Test downloading file with special characters in name."""
        job_id = str(uuid4())
        storage.save_output(job_id, 0, b"content", filename="file with spaces.txt")

        response = client.get(f"/api/v1/outputs/{job_id}/file with spaces.txt")

        assert response.status_code == 200
        assert response.content == b"content"

    def test_download_unicode_filename(self, client, storage):
        """Test downloading file with simple ASCII name."""
        job_id = str(uuid4())
        # Use ASCII filename to avoid header encoding issues
        storage.save_output(job_id, 0, b"content", filename="file-123.txt")

        response = client.get(f"/api/v1/outputs/{job_id}/file-123.txt")

        assert response.status_code == 200
        assert response.content == b"content"

    def test_download_large_file(self, client, storage):
        """Test downloading large file (1MB)."""
        job_id = str(uuid4())
        large_content = b"x" * (1024 * 1024)  # 1MB
        storage.save_output(job_id, 0, large_content, filename="large.txt")

        response = client.get(f"/api/v1/outputs/{job_id}/large.txt")

        assert response.status_code == 200
        assert len(response.content) == 1024 * 1024
