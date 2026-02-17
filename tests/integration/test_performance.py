"""
Performance tests for the Fill application.

Tests large file handling, memory usage, and response times.
"""

import io
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


class TestFileUploadPerformance:
    """Test upload performance with various file sizes."""

    def test_upload_small_file(self, client: TestClient):
        """Test upload of small file (< 1KB)."""
        # ~500 bytes
        csv_content = b"Name,Email,Phone\n" + b"John,john@test.com,555-1234\n" * 10
        
        start_time = time.time()
        response = client.post(
            "/api/v1/upload",
            files={"file": ("small.csv", io.BytesIO(csv_content), "text/csv")}
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 201
        assert elapsed < 1.0, f"Small file upload took {elapsed:.2f}s, expected < 1s"

    def test_upload_medium_file(self, client: TestClient):
        """Test upload of medium file (~100KB)."""
        # Generate ~100KB CSV
        rows = [f"Row{i},Data{i},Value{i}".encode() for i in range(2000)]
        csv_content = b"Col1,Col2,Col3\n" + b"\n".join(rows)
        
        size_kb = len(csv_content) / 1024
        
        start_time = time.time()
        response = client.post(
            "/api/v1/upload",
            files={"file": ("medium.csv", io.BytesIO(csv_content), "text/csv")}
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 201
        assert elapsed < 3.0, f"Medium file ({size_kb:.0f}KB) upload took {elapsed:.2f}s, expected < 3s"

    def test_upload_large_file(self, client: TestClient):
        """Test upload of large file (~1MB)."""
        # Generate ~1MB CSV
        rows = [f"Row{i},Data{i},Value{i},Extra{i}".encode() for i in range(20000)]
        csv_content = b"Col1,Col2,Col3,Col4\n" + b"\n".join(rows)
        
        size_mb = len(csv_content) / (1024 * 1024)
        
        start_time = time.time()
        response = client.post(
            "/api/v1/upload",
            files={"file": ("large.csv", io.BytesIO(csv_content), "text/csv")}
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 201
        assert elapsed < 10.0, f"Large file ({size_mb:.1f}MB) upload took {elapsed:.2f}s, expected < 10s"

    def test_upload_file_size_limit(self, client: TestClient):
        """Test that files over 10MB are rejected."""
        # Generate 11MB content
        large_content = b"x" * (11 * 1024 * 1024)
        
        response = client.post(
            "/api/v1/upload",
            files={"file": ("huge.csv", io.BytesIO(large_content), "text/csv")}
        )
        
        assert response.status_code == 413
        assert "exceeds" in response.json()["detail"].lower()


class TestParsePerformance:
    """Test file parsing performance."""

    @pytest.fixture
    def uploaded_file_id(self, client: TestClient) -> str:
        """Create and upload a test file."""
        csv_content = b"Name,Email,Age,City\n" + b"John,john@test.com,30,NYC\n" * 100
        
        response = client.post(
            "/api/v1/upload",
            files={"file": ("parse_test.csv", io.BytesIO(csv_content), "text/csv")}
        )
        assert response.status_code == 201
        return response.json()["file_id"]

    def test_parse_small_file(self, client: TestClient, uploaded_file_id: str):
        """Test parsing small file performance."""
        start_time = time.time()
        response = client.get(f"/api/v1/parse/{uploaded_file_id}")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Parse took {elapsed:.2f}s, expected < 2s"
        
        data = response.json()
        assert "rows" in data
        assert len(data["rows"]) <= 5  # Preview limit

    def test_parse_returns_limited_preview(self, client: TestClient):
        """Test that parse only returns first 5 rows regardless of file size."""
        # Upload large file
        rows = [f"Row{i},Data{i}".encode() for i in range(1000)]
        csv_content = b"Col1,Col2\n" + b"\n".join(rows)
        
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("big_preview.csv", io.BytesIO(csv_content), "text/csv")}
        )
        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]
        
        # Parse should be fast even for large files
        start_time = time.time()
        response = client.get(f"/api/v1/parse/{file_id}")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_rows"] == 1000
        assert len(data["rows"]) == 5  # Only 5 rows in preview
        assert elapsed < 3.0, f"Large file preview took {elapsed:.2f}s"


class TestListFilesPerformance:
    """Test file listing performance."""

    def test_list_files_performance(self, client: TestClient):
        """Test that listing files is fast even with many files."""
        # Upload several files
        for i in range(10):
            csv_content = f"Data{i}\nValue{i}\n".encode()
            response = client.post(
                "/api/v1/upload",
                files={"file": (f"perf{i}.csv", io.BytesIO(csv_content), "text/csv")}
            )
            assert response.status_code == 201
        
        # Test list performance
        start_time = time.time()
        response = client.get("/api/v1/files")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 1.0, f"List files took {elapsed:.2f}s, expected < 1s"
        
        data = response.json()
        assert data["total"] >= 10

    def test_pagination_performance(self, client: TestClient):
        """Test that pagination is efficient."""
        # Upload files
        for i in range(20):
            csv_content = f"Data{i}\n".encode()
            client.post(
                "/api/v1/upload",
                files={"file": (f"page{i}.csv", io.BytesIO(csv_content), "text/csv")}
            )
        
        # Request multiple pages
        start_time = time.time()
        
        for offset in [0, 5, 10, 15]:
            response = client.get(f"/api/v1/files?limit=5&offset={offset}")
            assert response.status_code == 200
        
        elapsed = time.time() - start_time
        assert elapsed < 2.0, f"Multiple pagination requests took {elapsed:.2f}s"


class TestMemoryUsage:
    """Test memory efficiency with large files."""

    def test_large_file_does_not_cause_memory_error(self, client: TestClient):
        """Test that large files don't cause memory issues."""
        # Create 5MB file (under limit but substantial)
        rows = [f"Row{i},Data{i},Value{i}".encode() for i in range(100000)]
        csv_content = b"Col1,Col2,Col3\n" + b"\n".join(rows)
        
        size_mb = len(csv_content) / (1024 * 1024)
        
        # Should upload without memory error
        response = client.post(
            "/api/v1/upload",
            files={"file": ("memory_test.csv", io.BytesIO(csv_content), "text/csv")}
        )
        
        assert response.status_code == 201
        
        file_id = response.json()["file_id"]
        
        # Parse should also work
        parse_response = client.get(f"/api/v1/parse/{file_id}")
        assert parse_response.status_code == 200
        
        data = parse_response.json()
        assert data["total_rows"] == 100000


class TestConcurrentOperations:
    """Test concurrent operation performance."""

    def test_multiple_uploads(self, client: TestClient):
        """Test handling multiple uploads."""
        start_time = time.time()
        
        # Upload 5 files in sequence
        for i in range(5):
            csv_content = f"Data{i}\nValue{i}\n".encode()
            response = client.post(
                "/api/v1/upload",
                files={"file": (f"concurrent{i}.csv", io.BytesIO(csv_content), "text/csv")}
            )
            assert response.status_code == 201
        
        elapsed = time.time() - start_time
        assert elapsed < 5.0, f"5 uploads took {elapsed:.2f}s"
        
        # All files should be listed
        list_response = client.get("/api/v1/files")
        assert list_response.status_code == 200
        data = list_response.json()
        assert data["total"] >= 5


class TestResponseTimeBenchmarks:
    """Benchmark key API endpoints."""

    def test_api_response_times(self, client: TestClient):
        """Benchmark key endpoints response times."""
        benchmarks = {}
        
        # Upload endpoint
        csv_content = b"Test,Data\nValue1,Value2\n"
        start = time.time()
        upload_resp = client.post(
            "/api/v1/upload",
            files={"file": ("bench.csv", io.BytesIO(csv_content), "text/csv")}
        )
        benchmarks["upload"] = time.time() - start
        assert upload_resp.status_code == 201
        file_id = upload_resp.json()["file_id"]
        
        # Parse endpoint
        start = time.time()
        parse_resp = client.get(f"/api/v1/parse/{file_id}")
        benchmarks["parse"] = time.time() - start
        assert parse_resp.status_code == 200
        
        # List files endpoint
        start = time.time()
        list_resp = client.get("/api/v1/files")
        benchmarks["list"] = time.time() - start
        assert list_resp.status_code == 200
        
        # Log benchmark results
        print("\nPerformance Benchmarks:")
        for endpoint, duration in benchmarks.items():
            print(f"  {endpoint}: {duration:.3f}s")
        
        # Assert reasonable performance
        assert benchmarks["upload"] < 2.0
        assert benchmarks["parse"] < 2.0
        assert benchmarks["list"] < 1.0
