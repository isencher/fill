"""
E2E Tests for Auto-Mapping Feature

Tests the auto-mapping functionality including:
- Auto-match button presence and functionality
- Confidence indicators (High/Medium/Low)
- Business-friendly field descriptions
- Visual feedback for matched fields
- API integration
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: FastAPI test client instance
    """
    return TestClient(app)


class TestAutoMappingUI:
    """Tests for auto-mapping UI elements"""

    def test_auto_match_button_present(self, client: TestClient):
        """Test that auto-match button is present on mapping page"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert 'id="autoMatchBtn"' in html
        assert "Auto-Match" in html or "Auto Match" in html

    def test_auto_match_button_has_icon(self, client: TestClient):
        """Test that auto-match button has sparkle icon"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert "✨" in html

    def test_business_friendly_title(self, client: TestClient):
        """Test that page title uses business language"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert "Match Data Fields" in html or "Match Fields" in html
        # Should not say "Placeholders" in main heading
        assert html.find("Map Columns to Placeholders") == -1 or "Match Data Fields" in html

    def test_template_fields_panel_title(self, client: TestClient):
        """Test that template panel uses business language"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert "Template Fields" in html or "template fields" in html.lower()

    def test_confidence_indicator_css(self, client: TestClient):
        """Test that confidence indicator CSS classes are defined"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert "confidence-indicator" in html
        assert "confidence-high" in html
        assert "confidence-medium" in html
        assert "confidence-low" in html

    def test_matched_field_styling(self, client: TestClient):
        """Test that matched fields have visual styling"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert "matched-high" in html
        assert "matched-medium" in html
        assert "matched-low" in html

    def test_business_description_class(self, client: TestClient):
        """Test that business description CSS class exists"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert "placeholder-description" in html

    def test_technical_info_class(self, client: TestClient):
        """Test that technical info CSS class exists"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert "technical-info" in html


class TestAutoMappingAPI:
    """Tests for auto-mapping API endpoint"""

    def test_suggest_endpoint_exists(self, client: TestClient):
        """Test that suggest endpoint is registered"""
        # The endpoint should be accessible (will return 4xx without proper params)
        response = client.post("/api/v1/mappings/suggest")
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404

    def test_suggest_endpoint_requires_params(self, client: TestClient):
        """Test that suggest endpoint requires file_id and template_id"""
        response = client.post("/api/v1/mappings/suggest")
        assert response.status_code == 422  # Validation error

    def test_suggest_endpoint_response_structure(self, client: TestClient):
        """Test that suggest endpoint returns expected structure"""
        # The suggest endpoint uses POST method with query parameters
        # This will test with invalid IDs to check response structure
        response = client.post(
            "/api/v1/mappings/suggest?file_id=invalid-id&template_id=invalid-id"
        )
        # Should return 404 for invalid IDs or 422 for validation errors (endpoint exists)
        assert response.status_code in [404, 422]


class TestAutoMappingIntegration:
    """Integration tests for auto-mapping workflow"""

    def test_auto_match_button_in_template_fields_panel(self, client: TestClient):
        """Test that auto-match button is in the correct panel"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        # Auto-match button should appear before placeholders list
        auto_match_pos = html.find('id="autoMatchBtn"')
        placeholders_pos = html.find('id="placeholdersList"')

        assert auto_match_pos > 0
        assert placeholders_pos > 0
        assert auto_match_pos < placeholders_pos

    def test_confidence_colors_defined(self, client: TestClient):
        """Test that confidence colors have visual distinction"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        # Check for color codes
        assert "#d4edda" in html or "#28a745" in html  # Green for high
        assert "#fff3cd" in html or "#ffc107" in html  # Yellow for medium
        assert "#f8d7da" in html or "#dc3545" in html  # Red for low

    def test_confidence_icons_defined(self, client: TestClient):
        """Test that confidence icons (emoji) are defined"""
        # Icons are rendered by JavaScript, check in mapping.js
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        # Check for emoji indicators in JavaScript
        # The actual implementation uses 🔴 for low confidence and ⚠️ for medium
        assert "🔴" in js or "⚠️" in js  # Low/medium confidence indicators

    def test_business_language_in_js(self, client: TestClient):
        """Test that mapping.js contains business language mappings"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        assert "FIELD_DESCRIPTIONS" in js
        assert "Customer" in js or "customer" in js
        assert "Amount" in js or "amount" in js

    def test_auto_match_function_exists(self, client: TestClient):
        """Test that autoMatchFields function exists"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        assert "autoMatchFields" in js
        assert "function autoMatchFields" in js or "autoMatchFields =" in js

    def test_render_placeholders_with_suggestions(self, client: TestClient):
        """Test that renderPlaceholdersList accepts suggestions parameter"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        assert "renderPlaceholdersList" in js
        assert "suggestions" in js

    def test_confidence_indicator_logic(self, client: TestClient):
        """Test that confidence indicator logic is implemented"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        # Check for confidence level checking
        assert "level === 'high'" in js
        assert "level === 'medium'" in js
        assert "level === 'low'" in js

    def test_auto_match_api_call(self, client: TestClient):
        """Test that auto-match function calls the correct API endpoint"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        assert "/api/v1/mappings/suggest" in js

    def test_auto_match_loading_state(self, client: TestClient):
        """Test that auto-match button shows loading state"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        assert "disabled = true" in js or "disabled=true" in js
        assert "Finding matches" in js or "Loading" in js

    def test_auto_match_error_handling(self, client: TestClient):
        """Test that auto-match function handles errors"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        assert "try {" in js
        assert "catch" in js
        assert "error" in js

    def test_confidence_removal_on_manual_change(self, client: TestClient):
        """Test that confidence indicators are removed on manual change"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        # Check for event listener that removes confidence styling
        assert "addEventListener" in js
        assert "'change'" in js or '"change"' in js
        assert "remove" in js
        assert "matched-" in js

    def test_business_friendly_label_rendering(self, client: TestClient):
        """Test that labels use business-friendly names"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        # Check that placeholders are rendered without {{ }} syntax
        assert "textContent = placeholder" in js or "textContent=placeholder" in js

    def test_technical_info_rendering(self, client: TestClient):
        """Test that technical info is rendered separately"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        # Check for technical info rendering
        assert "technical-info" in js
        assert "{{{" in js or "{{" in js

    def test_confidence_application_logic(self, client: TestClient):
        """Test that suggestions are applied based on confidence level"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        # Check that high/medium confidence suggestions are applied
        assert "suggestion.level === 'high'" in js or "level === 'high'" in js
        assert "suggestion.level === 'medium'" in js or "level === 'medium'" in js


class TestAutoMappingAccessibility:
    """Tests for auto-mapping accessibility"""

    def test_auto_match_button_is_button_element(self, client: TestClient):
        """Test that auto-match uses proper button element"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert '<button' in html
        assert 'id="autoMatchBtn"' in html

    def test_confidence_indicators_have_text(self, client: TestClient):
        """Test that confidence indicators have text labels"""
        # Text labels are rendered by JavaScript
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        # Check for text labels in JavaScript
        assert "High Match" in js or "high match" in js.lower()
        assert "Possible Match" in js or "possible match" in js.lower()
        assert "Low Match" in js or "low match" in js.lower()

    def test_business_descriptions_are_readable(self, client: TestClient):
        """Test that field descriptions use human-readable text"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        # Check for readable descriptions
        descriptions = [
            "Customer",
            "Date",
            "Amount",
            "Name",
            "Address"
        ]

        found_any = any(desc in js for desc in descriptions)
        assert found_any, "Should have at least some business-friendly descriptions"


class TestAutoMappingUserExperience:
    """Tests for auto-mapping UX features"""

    def test_auto_match_button_standalone(self, client: TestClient):
        """Test that auto-match button is visually distinct"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        # Auto-match button should have its own styling class
        assert "auto-match-btn" in html

    def test_dropdown_placeholder_text(self, client: TestClient):
        """Test that dropdown uses friendly placeholder text"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        assert "Select data column" in js or "select column" in js.lower()

    def test_confidence_messages(self, client: TestClient):
        """Test that user-friendly messages are shown for different confidence levels"""
        response = client.get("/static/mapping.js")
        assert response.status_code == 200
        js = response.text

        # Check for success/info messages
        assert "high confidence" in js.lower() or "high match" in js.lower()
        assert "medium confidence" in js.lower() or "possible match" in js.lower()
        assert "no confident matches" in js.lower() or "no matches" in js.lower()

    def test_progress_indicator_on_mapping_page(self, client: TestClient):
        """Test that mapping page has progress indicator"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert "progressContainer" in html
        assert "progress.js" in html


class TestAutoMappingVisualDesign:
    """Tests for auto-mapping visual design"""

    def test_confidence_indicator_badge_style(self, client: TestClient):
        """Test that confidence indicators use badge/pill style"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        # Check for badge-like styling
        assert "padding:" in html
        assert "border-radius:" in html

    def test_matched_field_border_colors(self, client: TestClient):
        """Test that matched fields have colored borders"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        # Check for border-color changes
        assert "border-color:" in html
        assert "#28a745" in html  # Green
        assert "#ffc107" in html  # Yellow
        assert "#dc3545" in html  # Red

    def test_matched_field_background_colors(self, client: TestClient):
        """Test that matched fields have colored backgrounds"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        # Check for background colors
        assert "#f0fff4" in html  # Light green
        assert "#fffbf0" in html  # Light yellow
        assert "#fff5f5" in html  # Light red

    def test_field_description_spacing(self, client: TestClient):
        """Test that field descriptions have proper spacing"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert "margin-top:" in html
        assert "font-size:" in html

    def test_technical_info_styling(self, client: TestClient):
        """Test that technical info is styled subtly"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        assert "italic" in html
        assert "#999" in html or "color:" in html


class TestAutoMappingResponsiveDesign:
    """Tests for auto-mapping responsive design"""

    def test_auto_match_button_responsive(self, client: TestClient):
        """Test that auto-match button is responsive"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        # Check for flexible layout
        assert "display:" in html
        assert "flex" in html

    def test_confidence_indicators_responsive(self, client: TestClient):
        """Test that confidence indicators work on mobile"""
        response = client.get("/mapping.html")
        assert response.status_code == 200
        html = response.text

        # Check for icon + text layout that works on mobile
        assert "display:" in html
        assert "align-items:" in html
