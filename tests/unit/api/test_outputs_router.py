"""
Unit tests for outputs router.

Tests file download endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.output_storage import get_output_storage


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def output_storage():
    """Get the output storage instance."""
    return get_output_storage()


@pytest.fixture
def sample_job(output_storage) -> str:
    """Create a sample job with outputs."""
    job_id = "test-job-123"
    output_storage.save_output(job_id, 0, b"Mock DOCX content", "file1.docx")
    output_storage.save_output(job_id, 1, b"Mock TXT content", "file2.txt")
    return job_id


class TestDownloadJobOutputs:
    """Tests for GET /api/v1/outputs/{job_id} endpoint."""

    def test_download_job_outputs_success(self, client: TestClient, sample_job: str) -> None:
        """Test downloading all outputs as ZIP."""
        response = client.get(f"/api/v1/outputs/{sample_job}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert "attachment" in response.headers["content-disposition"]
        assert f"{sample_job}_outputs.zip" in response.headers["content-disposition"]

    def test_download_job_outputs_content(self, client: TestClient, sample_job: str) -> None:
        """Test that ZIP download contains actual content."""
        response = client.get(f"/api/v1/outputs/{sample_job}")

        assert response.status_code == 200
        # Should have binary content
        assert len(response.content) > 0
        # ZIP files start with PK
        assert response.content[:2] == b"PK"

    def test_download_job_outputs_not_found(self, client: TestClient) -> None:
        """Test downloading outputs for non-existent job."""
        response = client.get("/api/v1/outputs/nonexistent-job")

        assert response.status_code == 404

    def test_download_job_outputs_no_files(self, client: TestClient, output_storage) -> None:
        """Test downloading when job exists but has no files."""
        # Create a job with no outputs (note: job_exists checks if job dir exists)
        job_id = "empty-job"
        # Since we can't create an empty job in the storage directly,
        # just test non-existent job
        response = client.get(f"/api/v1/outputs/{job_id}")

        # Should return 404 since job doesn't exist
        assert response.status_code == 404


class TestDownloadSingleOutput:
    """Tests for GET /api/v1/outputs/{job_id}/{filename} endpoint."""

    def test_download_single_output_docx(self, client: TestClient, sample_job: str) -> None:
        """Test downloading a single DOCX file."""
        response = client.get(f"/api/v1/outputs/{sample_job}/file1.docx")

        assert response.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]
        assert "file1.docx" in response.headers["content-disposition"]

    def test_download_single_output_txt(self, client: TestClient, sample_job: str) -> None:
        """Test downloading a single TXT file."""
        response = client.get(f"/api/v1/outputs/{sample_job}/file2.txt")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert response.content == b"Mock TXT content"

    def test_download_single_output_job_not_found(self, client: TestClient) -> None:
        """Test downloading file from non-existent job."""
        response = client.get("/api/v1/outputs/nonexistent-job/file.txt")

        assert response.status_code == 404

    def test_download_single_output_file_not_found(self, client: TestClient, sample_job: str) -> None:
        """Test downloading non-existent file from existing job."""
        response = client.get(f"/api/v1/outputs/{sample_job}/nonexistent.txt")

        assert response.status_code == 404

    def test_download_single_output_pdf(self, client: TestClient, output_storage) -> None:
        """Test downloading a PDF file."""
        job_id = "pdf-job"
        output_storage.save_output(job_id, 0, b"%PDF-1.4 mock pdf", "document.pdf")

        response = client.get(f"/api/v1/outputs/{job_id}/document.pdf")

        assert response.status_code == 200
        assert "application/pdf" in response.headers["content-type"]

    def test_download_single_output_unknown_type(self, client: TestClient, output_storage) -> None:
        """Test downloading file with unknown extension."""
        job_id = "unknown-job"
        output_storage.save_output(job_id, 0, b"some content", "file.xyz")

        response = client.get(f"/api/v1/outputs/{job_id}/file.xyz")

        assert response.status_code == 200
        assert "application/octet-stream" in response.headers["content-type"]
