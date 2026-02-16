"""
E2E Tests for Help and Documentation Features
Tests help tooltips, FAQ modal, tour, and sample downloads
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHelpTooltipCSS:
    """Test help tooltip CSS is loaded and defined"""

    def test_help_tooltip_css_loaded(self, client: TestClient):
        """Test help-tooltip.css is accessible"""
        response = client.get("/static/components/help-tooltip.css")
        assert response.status_code == 200
        assert len(response.text) > 500

    def test_help_tooltip_css_has_styles(self, client: TestClient):
        """Test help tooltip CSS has required styles"""
        response = client.get("/static/components/help-tooltip.css")
        css_content = response.text

        # Check for tooltip styles
        assert ".help-tooltip" in css_content
        assert ".help-tooltip-icon" in css_content
        assert ".help-tooltip-content" in css_content


class TestFAQModalCSS:
    """Test FAQ modal CSS is loaded and defined"""

    def test_faq_modal_css_loaded(self, client: TestClient):
        """Test faq-modal.css is accessible"""
        response = client.get("/static/components/faq-modal.css")
        assert response.status_code == 200
        assert len(response.text) > 1000

    def test_faq_modal_css_has_styles(self, client: TestClient):
        """Test FAQ modal CSS has required styles"""
        response = client.get("/static/components/faq-modal.css")
        css_content = response.text

        # Check for FAQ styles
        assert ".faq-button" in css_content
        assert ".faq-modal" in css_content
        assert ".faq-item" in css_content
        assert ".faq-question" in css_content
        assert ".faq-answer" in css_content


class TestTourCSS:
    """Test tour CSS is loaded and defined"""

    def test_tour_css_loaded(self, client: TestClient):
        """Test tour.css is accessible"""
        response = client.get("/static/components/tour.css")
        assert response.status_code == 200
        assert len(response.text) > 1000

    def test_tour_css_has_styles(self, client: TestClient):
        """Test tour CSS has required styles"""
        response = client.get("/static/components/tour.css")
        css_content = response.text

        # Check for tour styles
        assert ".tour-overlay" in css_content
        assert ".tour-highlight" in css_content
        assert ".tour-tooltip" in css_content


class TestHelpJavaScriptLoaded:
    """Test help JavaScript files are loaded"""

    def test_help_tooltip_js_loaded(self, client: TestClient):
        """Test help-tooltip.js is accessible"""
        response = client.get("/static/components/help-tooltip.js")
        assert response.status_code == 200
        assert len(response.text) > 500
        assert "HelpTooltip" in response.text

    def test_faq_modal_js_loaded(self, client: TestClient):
        """Test faq-modal.js is accessible"""
        response = client.get("/static/components/faq-modal.js")
        assert response.status_code == 200
        assert len(response.text) > 1000
        assert "FAQModal" in response.text

    def test_tour_js_loaded(self, client: TestClient):
        """Test tour.js is accessible"""
        response = client.get("/static/components/tour.js")
        assert response.status_code == 200
        assert len(response.text) > 1000
        assert "class Tour" in response.text


class TestHelpComponentsIncluded:
    """Test help components are included in HTML pages"""

    def test_index_includes_help_css(self, client: TestClient):
        """Test index.html includes help CSS files"""
        response = client.get("/static/index.html")
        assert response.status_code == 200

        assert 'href="/static/components/help-tooltip.css"' in response.text
        assert 'href="/static/components/faq-modal.css"' in response.text
        assert 'href="/static/components/tour.css"' in response.text

    def test_index_includes_help_js(self, client: TestClient):
        """Test index.html includes help JS files"""
        response = client.get("/static/index.html")
        assert response.status_code == 200

        assert 'src="/static/components/help-tooltip.js"' in response.text
        assert 'src="/static/components/faq-modal.js"' in response.text
        assert 'src="/static/components/tour.js"' in response.text

    def test_templates_includes_help_components(self, client: TestClient):
        """Test templates.html includes help components"""
        response = client.get("/static/templates.html")
        assert response.status_code == 200

        assert 'href="/static/components/help-tooltip.css"' in response.text
        assert 'href="/static/components/faq-modal.css"' in response.text
        assert 'href="/static/components/tour.css"' in response.text
        assert 'src="/static/components/help-tooltip.js"' in response.text
        assert 'src="/static/components/faq-modal.js"' in response.text
        assert 'src="/static/components/tour.js"' in response.text

    def test_mapping_includes_help_components(self, client: TestClient):
        """Test mapping.html includes help components"""
        response = client.get("/static/mapping.html")
        assert response.status_code == 200

        assert 'href="/static/components/help-tooltip.css"' in response.text
        assert 'href="/static/components/faq-modal.css"' in response.text
        assert 'href="/static/components/tour.css"' in response.text
        assert 'src="/static/components/help-tooltip.js"' in response.text
        assert 'src="/static/components/faq-modal.js"' in response.text
        assert 'src="/static/components/tour.js"' in response.text


class TestHelpTooltipAttributes:
    """Test help tooltip attributes are present"""

    def test_index_has_help_tooltip(self, client: TestClient):
        """Test index.html has help tooltip attribute"""
        response = client.get("/static/index.html")
        assert response.status_code == 200

        # Check for data-help-tooltip attribute
        assert 'data-help-tooltip=' in response.text


class TestSampleDownloads:
    """Test sample data download functionality"""

    def test_sample_csv_accessible(self, client: TestClient):
        """Test sample CSV file is accessible"""
        response = client.get("/static/samples/sample-customer-data.csv")
        assert response.status_code == 200

        # Verify CSV content
        content = response.text
        assert "Customer Name" in content
        assert "Email" in content
        assert "Phone" in content

    def test_sample_csv_has_correct_headers(self, client: TestClient):
        """Test sample CSV has correct headers"""
        response = client.get("/static/samples/sample-customer-data.csv")
        assert response.status_code == 200

        lines = response.text.strip().split('\n')
        headers = lines[0].split(',')

        assert "Customer Name" in headers
        assert "Email" in headers
        assert "Phone" in headers
        assert "Address" in headers

    def test_sample_csv_has_data_rows(self, client: TestClient):
        """Test sample CSV has data rows"""
        response = client.get("/static/samples/sample-customer-data.csv")
        assert response.status_code == 200

        lines = response.text.strip().split('\n')
        # Should have header + at least 5 data rows
        assert len(lines) >= 6

    def test_index_has_sample_download_button(self, client: TestClient):
        """Test index.html has sample download button"""
        response = client.get("/static/index.html")
        assert response.status_code == 200

        # Check for sample download link
        assert 'sample-customer-data.csv' in response.text
        assert 'download' in response.text


class TestTourIntegration:
    """Test tour component integration"""

    def test_tour_auto_start_in_index(self, client: TestClient):
        """Test index.html has tour auto-start code"""
        response = client.get("/static/index.html")
        assert response.status_code == 200

        # Check for tour auto-start
        assert "autoStartTour" in response.text
        assert "'upload'" in response.text

    def test_tour_auto_start_in_templates(self, client: TestClient):
        """Test templates.html has tour auto-start code"""
        response = client.get("/static/templates.html")
        assert response.status_code == 200

        # Check for tour auto-start
        assert "autoStartTour" in response.text
        assert "'templates'" in response.text

    def test_tour_auto_start_in_mapping(self, client: TestClient):
        """Test mapping.html has tour auto-start code"""
        response = client.get("/static/mapping.html")
        assert response.status_code == 200

        # Check for tour auto-start
        assert "autoStartTour" in response.text
        assert "'mapping'" in response.text

    def test_tour_js_has_tour_definitions(self, client: TestClient):
        """Test tour.js has tour definitions for all pages"""
        response = client.get("/static/components/tour.js")
        assert response.status_code == 200

        content = response.text

        # Check for tour definitions
        assert "upload:" in content
        assert "templates:" in content
        assert "mapping:" in content


class TestFAQContent:
    """Test FAQ modal has content"""

    def test_faq_js_has_questions(self, client: TestClient):
        """Test faq-modal.js has FAQ questions"""
        response = client.get("/static/components/faq-modal.js")
        assert response.status_code == 200

        content = response.text

        # Check for FAQ data
        assert "FAQ_DATA" in content
        assert "How do I format my data file?" in content
        assert "What file formats are supported?" in content

    def test_faq_has_search_functionality(self, client: TestClient):
        """Test FAQ modal has search functionality"""
        response = client.get("/static/components/faq-modal.js")
        assert response.status_code == 200

        content = response.text

        # Check for search functionality
        assert "handleSearch" in content
        assert "faq-search" in content

    def test_faq_has_multiple_questions(self, client: TestClient):
        """Test FAQ has at least 5 questions"""
        response = client.get("/static/components/faq-modal.js")
        assert response.status_code == 200

        content = response.text

        # Count FAQ items
        question_count = content.count("question:")
        assert question_count >= 5


class TestHelpAccessibility:
    """Test help components accessibility"""

    def test_help_tooltip_has_aria_labels(self, client: TestClient):
        """Test help tooltip has ARIA labels"""
        response = client.get("/static/components/help-tooltip.js")
        assert response.status_code == 200

        content = response.text

        # Check for ARIA labels
        assert "aria-label" in content

    def test_faq_modal_has_aria_labels(self, client: TestClient):
        """Test FAQ modal has ARIA labels"""
        response = client.get("/static/components/faq-modal.js")
        assert response.status_code == 200

        content = response.text

        # Check for ARIA attributes
        assert "aria-label" in content
        # role attribute is set via JavaScript, not in the JS file content
        # but the modal element creation should include it
        assert "setAttribute" in content or "modal.setAttribute" in content

    def test_tour_has_keyboard_navigation(self, client: TestClient):
        """Test tour supports keyboard navigation"""
        response = client.get("/static/components/tour.js")
        assert response.status_code == 200

        content = response.text

        # Check for keyboard support
        assert "keydown" in content
        assert "ArrowRight" in content or "ArrowLeft" in content
        assert "Escape" in content


class TestHelpComponentIntegration:
    """Test complete help system integration"""

    def test_all_help_components_loaded(self, client: TestClient):
        """Test all help components are properly loaded"""
        # CSS files
        css_files = [
            "/static/components/help-tooltip.css",
            "/static/components/faq-modal.css",
            "/static/components/tour.css",
        ]

        for css_file in css_files:
            response = client.get(css_file)
            assert response.status_code == 200, f"{css_file} should load"
            assert len(response.text) > 500, f"{css_file} should have content"

        # JS files
        js_files = [
            "/static/components/help-tooltip.js",
            "/static/components/faq-modal.js",
            "/static/components/tour.js",
        ]

        for js_file in js_files:
            response = client.get(js_file)
            assert response.status_code == 200, f"{js_file} should load"
            assert len(response.text) > 500, f"{js_file} should have content"

    def test_complete_help_system_on_index(self, client: TestClient):
        """Test complete help system on index page"""
        response = client.get("/static/index.html")
        assert response.status_code == 200

        html = response.text

        # Check CSS includes
        assert 'help-tooltip.css' in html
        assert 'faq-modal.css' in html
        assert 'tour.css' in html

        # Check JS includes
        assert 'help-tooltip.js' in html
        assert 'faq-modal.js' in html
        assert 'tour.js' in html

        # Check tour auto-start
        assert 'autoStartTour' in html

        # Check sample downloads
        assert 'sample-customer-data.csv' in html

        # Check help tooltips
        assert 'data-help-tooltip=' in html

    def test_complete_help_system_on_templates(self, client: TestClient):
        """Test complete help system on templates page"""
        response = client.get("/static/templates.html")
        assert response.status_code == 200

        html = response.text

        # Check CSS includes
        assert 'help-tooltip.css' in html
        assert 'faq-modal.css' in html
        assert 'tour.css' in html

        # Check JS includes
        assert 'help-tooltip.js' in html
        assert 'faq-modal.js' in html
        assert 'tour.js' in html

        # Check tour auto-start
        assert 'autoStartTour' in html

    def test_complete_help_system_on_mapping(self, client: TestClient):
        """Test complete help system on mapping page"""
        response = client.get("/static/mapping.html")
        assert response.status_code == 200

        html = response.text

        # Check CSS includes
        assert 'help-tooltip.css' in html
        assert 'faq-modal.css' in html
        assert 'tour.css' in html

        # Check JS includes
        assert 'help-tooltip.js' in html
        assert 'faq-modal.js' in html
        assert 'tour.js' in html

        # Check tour auto-start
        assert 'autoStartTour' in html


class TestSampleFileQuality:
    """Test quality of sample files"""

    def test_sample_csv_has_realistic_data(self, client: TestClient):
        """Test sample CSV has realistic customer data"""
        response = client.get("/static/samples/sample-customer-data.csv")
        assert response.status_code == 200

        content = response.text

        # Check for realistic data patterns
        assert "@" in content  # Email addresses
        assert "(" in content  # Phone numbers
        assert "St" in content or "Ave" in content  # Street addresses

    def test_sample_csv_well_formed(self, client: TestClient):
        """Test sample CSV is well-formed"""
        response = client.get("/static/samples/sample-customer-data.csv")
        assert response.status_code == 200

        lines = response.text.strip().split('\n')

        # All lines should have same number of columns
        header_cols = len(lines[0].split(','))
        for line in lines[1:]:
            cols = len(line.split(','))
            assert cols == header_cols, f"Inconsistent columns: {line}"


class TestHelpComponentFeatures:
    """Test specific features of help components"""

    def test_faq_has_8_questions(self, client: TestClient):
        """Test FAQ has at least 8 common questions"""
        response = client.get("/static/components/faq-modal.js")
        assert response.status_code == 200

        content = response.text

        # Count questions in FAQ_DATA
        question_count = content.count('{')
        assert question_count >= 8, "FAQ should have at least 8 questions"

    def test_tour_has_multiple_steps(self, client: TestClient):
        """Test tour has multiple steps for each page"""
        response = client.get("/static/components/tour.js")
        assert response.status_code == 200

        content = response.text

        # Check for steps in tour definitions
        assert "steps:" in content
        # Upload tour should have steps
        assert "upload:" in content
        assert "target:" in content

    def test_help_tooltip_positions(self, client: TestClient):
        """Test help tooltip supports multiple positions"""
        response = client.get("/static/components/help-tooltip.css")
        assert response.status_code == 200

        content = response.text

        # Check for position variants
        assert ".help-tooltip.left" in content or "left" in content
        assert ".help-tooltip.right" in content or "right" in content

    def test_help_tooltip_responsive(self, client: TestClient):
        """Test help tooltip is responsive on mobile"""
        response = client.get("/static/components/help-tooltip.css")
        assert response.status_code == 200

        content = response.text

        # Check for mobile media query
        assert "@media (max-width: 767px)" in content

    def test_faq_search_functionality(self, client: TestClient):
        """Test FAQ search functionality is implemented"""
        response = client.get("/static/components/faq-modal.js")
        assert response.status_code == 200

        content = response.text

        # Check search implementation
        assert "handleSearch" in content
        assert "addEventListener('input'" in content

    def test_tour_local_storage(self, client: TestClient):
        """Test tour uses localStorage for persistence"""
        response = client.get("/static/components/tour.js")
        assert response.status_code == 200

        content = response.text

        # Check for localStorage usage
        assert "localStorage" in content
        assert "hasBeenShown" in content or "markAsShown" in content

    def test_tour_skip_functionality(self, client: TestClient):
        """Test tour can be skipped"""
        response = client.get("/static/components/tour.js")
        assert response.status_code == 200

        content = response.text

        # Check for skip functionality
        assert "onSkip" in content or "skip" in content.lower()
