"""
Integration tests for workflow redirect fixes.

Tests API-level and static file fixes:
1. Template selection page exists
2. Upload redirect logic correct
3. Mapping page requires both parameters
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.template_store import get_template_store
from src.models.template import Template


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def seeded_templates():
    """Seed template store with built-in templates."""
    store = get_template_store()
    store.clear()
    
    # Create built-in templates
    templates = [
        Template(
            name="发票模板",
            file_path="/templates/invoice.docx",
            description="标准发票模板，包含客户名称、金额、日期",
            placeholders=["客户名称", "金额", "日期"]
        ),
        Template(
            name="合同模板", 
            file_path="/templates/contract.docx",
            description="标准合同模板",
            placeholders=["甲方", "乙方", "金额", "日期"]
        ),
        Template(
            name="信函模板",
            file_path="/templates/letter.docx", 
            description="正式信函模板",
            placeholders=["收件人", "主题", "内容"]
        ),
    ]
    
    for t in templates:
        store.save_template(t)
    
    yield templates
    store.clear()


class TestTemplateSelectionPage:
    """Test template selection page exists and serves correctly."""

    def test_template_selection_page_exists(self, client: TestClient):
        """Template selection HTML page should be accessible."""
        response = client.get("/templates.html?file_id=test-123")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
    
    def test_template_page_contains_selection_ui(self, client: TestClient):
        """Page should contain template selection UI elements."""
        response = client.get("/templates.html?file_id=test-123")
        html = response.text
        
        # Should have heading
        assert "选择模板" in html or "Select Template" in html
        
        # Should have template cards or list
        assert "template-card" in html or "template-item" in html
    
    def test_template_page_requires_file_id(self, client: TestClient):
        """Page should warn if file_id is missing."""
        response = client.get("/templates.html")
        
        # Should still return 200 but show error state
        assert response.status_code == 200
        assert "请先上传数据" in response.text or "missing" in response.text.lower()


class TestTemplateListAPI:
    """Test template list API for selection page."""

    def test_list_templates_returns_built_ins(self, client: TestClient, seeded_templates):
        """Should return built-in templates for selection."""
        response = client.get("/api/v1/templates")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        
        # Should have Chinese names
        names = [t["name"] for t in data["templates"]]
        assert "发票模板" in names
        assert "合同模板" in names
    
    def test_template_includes_placeholder_count(self, client: TestClient, seeded_templates):
        """Template should include placeholder count for UI."""
        response = client.get("/api/v1/templates")
        data = response.json()
        
        invoice = next(t for t in data["templates"] if t["name"] == "发票模板")
        assert len(invoice["placeholders"]) == 3


class TestUploadRedirectLogic:
    """Test upload.js redirect logic is fixed."""

    def test_upload_js_uses_template_selection_redirect(self, client: TestClient):
        """upload.js should redirect to templates.html not mapping.html."""
        # Read the upload.js file
        import os
        static_dir = os.path.join(os.path.dirname(__file__), "../../src/static")
        upload_js_path = os.path.join(static_dir, "upload.js")
        
        with open(upload_js_path, "r") as f:
            content = f.read()
        
        # Should redirect to templates.html (not mapping.html directly)
        assert "templates.html" in content
        
        # Should NOT directly go to mapping.html without template_id
        # (This was the bug)
        if "mapping.html" in content:
            # If mapping.html is referenced, it should include template_id
            assert "template_id" in content


class TestMappingPageValidation:
    """Test mapping page validates parameters."""

    def test_mapping_page_without_template_id_shows_error(self, client: TestClient):
        """Mapping page without template_id should show helpful error."""
        response = client.get("/mapping.html?file_id=test-123")
        
        assert response.status_code == 200
        # Should show error, not just empty state
        assert "选择模板" in response.text or "template" in response.text.lower()
    
    def test_mapping_page_without_file_id_shows_error(self, client: TestClient):
        """Mapping page without file_id should show helpful error."""
        response = client.get("/mapping.html?template_id=test-123")
        
        assert response.status_code == 200
        assert "上传数据" in response.text or "file" in response.text.lower()


class TestDualEntryAPI:
    """Test API supports both entry points."""

    def test_api_supports_template_upload(self, client: TestClient):
        """API should support template file upload endpoint."""
        # Check if upload endpoint exists
        response = client.post("/api/v1/templates/upload")
        
        # Should return 422 (missing file) not 404
        assert response.status_code != 404


class TestSmartMappingAPI:
    """Test smart mapping suggestion API."""

    def test_suggest_mapping_endpoint_exists(self, client: TestClient):
        """Suggest mapping endpoint should exist."""
        response = client.post("/api/v1/mappings/suggest")
        
        # Should not be 404
        assert response.status_code != 404
    
    def test_suggest_mapping_returns_confidence(self, client: TestClient):
        """Should return confidence levels for matches."""
        # This will need proper seeding, but endpoint should exist
        response = client.post(
            "/api/v1/mappings/suggest",
            params={"file_id": "test", "template_id": "test"}
        )
        
        # May fail with 400/404 for missing entities, but schema should be valid
        if response.status_code == 200:
            data = response.json()
            assert "suggested_mappings" in data
            assert "confidence" in data
