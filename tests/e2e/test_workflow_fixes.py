"""
E2E tests for workflow fixes.

Tests cover the complete user journey fixes:
1. Template selection page exists and works
2. Upload page redirects to template selection (not broken mapping page)
3. Template selection passes both file_id and template_id to mapping
4. Mapping page shows confirmation before processing

The server fixture automatically starts uvicorn on port 8000 for these tests.

Note: These tests require Playwright browser automation.
Run in Docker container with Playwright installed, or skip if unavailable.
"""

import pytest

# Skip all tests in this module if playwright is not installed
pytest.importorskip("playwright.sync_api")

from playwright.sync_api import Page, expect


class TestTemplateSelectionPage:
    """Test template selection page exists and functions."""

    def test_template_list_page_exists(self, page: Page, server):
        """Template selection page should be accessible."""
        page.goto("http://localhost:8000/templates.html?file_id=test-file-123")
        
        # Should show template selection interface
        expect(page.locator("h1")).to_contain_text("选择模板")
        expect(page.locator("text=发票模板").first).to_be_visible()
        expect(page.locator("text=合同模板").first).to_be_visible()
    
    def test_template_list_shows_builtin_templates(self, page: Page, server):
        """Should show built-in example templates."""
        page.goto("http://localhost:8000/templates.html?file_id=test-file-123")
        
        # Should have at least 3 built-in templates
        templates = page.locator("[data-testid='template-card']")
        expect(templates).to_have_count(3)
    
    def test_template_selection_navigates_to_mapping(self, page: Page, server):
        """Selecting template should navigate to mapping with both IDs."""
        page.goto("http://localhost:8000/templates.html?file_id=test-file-123")
        
        # Click first template's "Use" button
        page.locator("[data-testid='use-template-btn']").first.click()
        
        # Should navigate to mapping page with both parameters
        page.wait_for_url(lambda url: "/mapping.html" in url and 
                         "file_id=test-file-123" in url and 
                         "template_id=" in url)
    
    def test_template_upload_option_available(self, page: Page, server):
        """Should have option to upload custom template."""
        page.goto("http://localhost:8000/templates.html?file_id=test-file-123")

        expect(page.locator("text=上传我的模板").first).to_be_visible()
        expect(page.locator("input[type='file'][accept='.docx,.txt']")).to_be_attached()


class TestUploadPageRedirectFix:
    """Test upload page redirects correctly (not to broken mapping page)."""

    @pytest.mark.xfail(reason="Upload button flow not yet implemented")
    def test_upload_success_shows_template_selection_button(self, page: Page, server):
        """After upload, should show button to select template."""
        page.goto("http://localhost:8000/")

        # Upload a test file
        page.locator("#fileInput").set_input_files({
            "name": "test_data.csv",
            "mimeType": "text/csv",
            "buffer": b"name,amount\nJohn,100\nJane,200"
        })

        # Click upload
        page.locator("#uploadBtn").click()

        # Wait for success and check button text
        page.wait_for_selector("text=选择模板")
        expect(page.locator("button:text('选择模板')")).to_be_visible()

    @pytest.mark.xfail(reason="Upload button flow not yet implemented")
    def test_upload_redirect_includes_file_id(self, page: Page, server):
        """Clicking 'select template' should redirect with file_id."""
        page.goto("http://localhost:8000/")

        # Upload and wait for success
        page.locator("#fileInput").set_input_files({
            "name": "test_data.csv",
            "mimeType": "text/csv",
            "buffer": b"name,amount\nJohn,100"
        })
        page.locator("#uploadBtn").click()
        page.wait_for_selector("text=选择模板")

        # Click select template button
        page.locator("button:text('选择模板')").click()

        # Should go to template selection page (not mapping)
        page.wait_for_url(lambda url: "/templates.html" in url)
        expect(page.url).to_contain("file_id=")


class TestMappingConfirmationFlow:
    """Test mapping page shows confirmation before processing."""

    @pytest.mark.xfail(reason="Preview UI not yet fully implemented")
    def test_mapping_page_shows_preview(self, page: Page, server):
        """Should show data preview and mappings before processing."""
        # Pre-seed with file and template
        page.goto("http://localhost:8000/mapping.html?file_id=demo&template_id=demo")

        # Should show data preview
        expect(page.locator("text=数据预览").first).to_be_visible()
        expect(page.locator("table")).to_be_visible()

    @pytest.mark.xfail(reason="Confirmation UI not yet fully implemented")
    def test_mapping_page_requires_confirmation(self, page: Page, server):
        """Should require explicit confirmation before generating."""
        page.goto("http://localhost:8000/mapping.html?file_id=demo&template_id=demo")

        # Should show confirmation modal/section
        expect(page.locator("text=确认生成").first).to_be_visible()
        expect(page.locator("text=将生成").first).to_be_visible()

    @pytest.mark.xfail(reason="Mapping page error handling not yet implemented")
    def test_missing_parameters_shows_helpful_error(self, page: Page, server):
        """Missing file_id or template_id should show helpful message."""
        page.goto("http://localhost:8000/mapping.html")

        # Should show helpful error (not just "missing parameters")
        expect(page.locator("text=请先上传数据文件").first).to_be_visible()
        expect(page.locator("text=选择模板").first).to_be_visible()  # CTA to fix


class TestDualEntryPoints:
    """Test both workflow entry points work."""

    def test_data_first_entry_point(self, page: Page, server):
        """User can start by uploading data first."""
        page.goto("http://localhost:8000/")

        # Should have data upload option
        expect(page.locator("text=我有数据文件").first).to_be_visible()

    def test_template_first_entry_point(self, page: Page, server):
        """User can start by selecting template first."""
        page.goto("http://localhost:8000/")

        # Should have template selection option
        expect(page.locator("text=从示例开始").first).to_be_visible()

    def test_template_first_flow_asks_for_data(self, page: Page, server):
        """Template-first flow should ask for data after template selection."""
        page.goto("http://localhost:8000/")

        # Click template-first option
        page.locator("text=我有模板文件").click()

        # Should show data upload step
        expect(page.locator("text=上传数据文件").first).to_be_visible()


class TestSmartMappingSuggestions:
    """Test smart mapping suggestions with confidence levels."""

    @pytest.mark.xfail(reason="Confidence indicators UI not yet fully implemented")
    def test_high_confidence_mapping_shows_checkmark(self, page: Page, server):
        """High confidence matches should show checkmark."""
        page.goto("http://localhost:8000/mapping.html?file_id=demo&template_id=demo")

        # High confidence match
        expect(page.locator("text=✅").first).to_be_visible()

    @pytest.mark.xfail(reason="Accept button for medium confidence not yet implemented")
    def test_medium_confidence_shows_warning(self, page: Page, server):
        """Medium confidence should show warning and require confirmation."""
        page.goto("http://localhost:8000/mapping.html?file_id=demo&template_id=demo")

        # Medium confidence match
        expect(page.locator("text=⚠️").first).to_be_visible()
        expect(page.locator("button:text('接受')").first).to_be_visible()

    @pytest.mark.xfail(reason="Manual selection UI not yet fully implemented")
    def test_low_confidence_requires_manual_selection(self, page: Page, server):
        """Low confidence should force manual selection."""
        page.goto("http://localhost:8000/mapping.html?file_id=demo&template_id=demo")

        # Should show dropdown for manual selection
        expect(page.locator("select").first).to_be_visible()
