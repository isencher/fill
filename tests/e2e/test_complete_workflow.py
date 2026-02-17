"""
End-to-end tests for the complete Fill application workflow.

Tests the full user journey: upload → parse → map → generate
"""

import io
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.database import init_db


@pytest.fixture
def client() -> TestClient:
    """Create a test client with fresh database."""
    # Use temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    import os
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    init_db()
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    if Path(db_path).exists():
        os.unlink(db_path)


class TestCompleteWorkflow:
    """Test the complete workflow from upload to output generation."""

    def test_upload_parse_workflow(self, client: TestClient):
        """Test upload followed by parse."""
        # Step 1: Upload a CSV file
        csv_content = b"Name,Email,Phone\nJohn Doe,john@example.com,555-1234\nJane Smith,jane@example.com,555-5678"
        
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("customers.csv", io.BytesIO(csv_content), "text/csv")}
        )
        
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        file_id = upload_data["file_id"]
        
        # Step 2: Parse the uploaded file
        parse_response = client.get(f"/api/v1/parse/{file_id}")
        
        assert parse_response.status_code == 200
        parse_data = parse_response.json()
        
        assert parse_data["file_id"] == file_id
        assert parse_data["filename"] == "customers.csv"
        assert parse_data["total_rows"] == 2
        assert len(parse_data["rows"]) == 2
        
        # Verify row data
        first_row = parse_data["rows"][0]
        assert "Name" in first_row
        assert "Email" in first_row
        assert "Phone" in first_row

    def test_upload_list_workflow(self, client: TestClient):
        """Test upload followed by list files."""
        # Upload multiple files
        files = [
            ("file1.csv", b"Col1\nVal1\n"),
            ("file2.csv", b"Col2\nVal2\n"),
            ("file3.csv", b"Col3\nVal3\n"),
        ]
        
        uploaded_ids = []
        for filename, content in files:
            response = client.post(
                "/api/v1/upload",
                files={"file": (filename, io.BytesIO(content), "text/csv")}
            )
            assert response.status_code == 201
            uploaded_ids.append(response.json()["file_id"])
        
        # List files
        list_response = client.get("/api/v1/files")
        
        assert list_response.status_code == 200
        list_data = list_response.json()
        
        assert list_data["total"] >= 3
        file_ids = [f["file_id"] for f in list_data["files"]]
        
        for uid in uploaded_ids:
            assert uid in file_ids

    def test_full_workflow_upload_parse_map(self, client: TestClient):
        """Test complete workflow: upload → parse → create mapping."""
        # Step 1: Upload data file
        csv_content = b"Customer,Amount,Date\nAcme Corp,1000.00,2024-01-15\nGlobex Inc,2500.50,2024-01-16"
        
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("invoices.csv", io.BytesIO(csv_content), "text/csv")}
        )
        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]
        
        # Step 2: Parse file
        parse_response = client.get(f"/api/v1/parse/{file_id}")
        assert parse_response.status_code == 200
        parse_data = parse_response.json()
        assert parse_data["total_rows"] == 2
        
        # Step 3: Create template
        template_response = client.post(
            "/api/v1/templates",
            params={
                "name": "Invoice Template",
                "file_path": "/templates/invoice.docx",
                "placeholders": "customer,amount,date",
                "description": "Standard invoice template"
            }
        )
        assert template_response.status_code == 201
        template_id = template_response.json()["template"]["id"]
        
        # Step 4: Create mapping
        mapping_response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": file_id,
                "template_id": template_id
            },
            json={
                "Customer": "customer",
                "Amount": "amount",
                "Date": "date"
            }
        )
        
        assert mapping_response.status_code == 201
        mapping_data = mapping_response.json()
        assert mapping_data["file_id"] == file_id
        assert mapping_data["template_id"] == template_id
        assert mapping_data["column_mappings"] == {
            "Customer": "customer",
            "Amount": "amount",
            "Date": "date"
        }

    def test_workflow_with_pagination(self, client: TestClient):
        """Test workflow with paginated file listing."""
        # Upload 5 files
        for i in range(5):
            csv_content = f"Data{i}\nValue{i}\n".encode()
            response = client.post(
                "/api/v1/upload",
                files={"file": (f"batch{i}.csv", io.BytesIO(csv_content), "text/csv")}
            )
            assert response.status_code == 201
        
        # Test pagination
        all_files = []
        offset = 0
        limit = 2
        
        while True:
            response = client.get(f"/api/v1/files?limit={limit}&offset={offset}")
            assert response.status_code == 200
            data = response.json()
            
            all_files.extend(data["files"])
            
            if not data["has_more"]:
                break
            
            offset += limit
        
        # Should have retrieved all files
        assert len(all_files) >= 5

    def test_error_handling_workflow(self, client: TestClient):
        """Test error handling in workflow."""
        # Try to parse non-existent file
        parse_response = client.get(f"/api/v1/parse/{uuid4()}")
        assert parse_response.status_code == 404
        
        # Try to create mapping with non-existent file
        mapping_response = client.post(
            "/api/v1/mappings",
            params={
                "file_id": str(uuid4()),
                "template_id": str(uuid4())
            },
            json={"col": "field"}
        )
        assert mapping_response.status_code == 404

    def test_multiple_mappings_for_same_file(self, client: TestClient):
        """Test creating multiple mappings for the same file."""
        # Upload file
        csv_content = b"Name,Email\nJohn,john@test.com"
        
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("multi_map.csv", io.BytesIO(csv_content), "text/csv")}
        )
        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]
        
        # Create two templates
        template_ids = []
        for i in range(2):
            template_response = client.post(
                "/api/v1/templates",
                params={
                    "name": f"Template {i}",
                    "file_path": f"/templates/t{i}.docx",
                    "placeholders": "name,email"
                }
            )
            assert template_response.status_code == 201
            template_ids.append(template_response.json()["template"]["id"])
        
        # Create mapping for each template
        for template_id in template_ids:
            mapping_response = client.post(
                "/api/v1/mappings",
                params={
                    "file_id": file_id,
                    "template_id": template_id
                },
                json={
                    "Name": "name",
                    "Email": "email"
                }
            )
            assert mapping_response.status_code == 201


class TestDataPersistenceWorkflow:
    """Test that data persists across requests."""

    def test_file_persists_after_upload(self, client: TestClient):
        """Test uploaded file remains accessible in subsequent requests."""
        # Upload
        csv_content = b"Product,Price\nWidget,9.99"
        
        upload_response = client.post(
            "/api/v1/upload",
            files={"file": ("persist_test.csv", io.BytesIO(csv_content), "text/csv")}
        )
        assert upload_response.status_code == 201
        file_id = upload_response.json()["file_id"]
        
        # First parse
        parse1 = client.get(f"/api/v1/parse/{file_id}")
        assert parse1.status_code == 200
        
        # Second parse - should still work
        parse2 = client.get(f"/api/v1/parse/{file_id}")
        assert parse2.status_code == 200
        
        # Data should be identical
        assert parse1.json() == parse2.json()
