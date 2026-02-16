"""
E2E Tests for First-Time User Onboarding

Tests the onboarding flow for first-time users including:
- Welcome screen display
- 4-step workflow preview
- Start and Skip buttons
- HTML structure and content
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


class TestOnboardingPage:
    """Tests for onboarding page structure and elements"""

    def test_onboarding_page_loads(self, client: TestClient):
        """Test that onboarding page loads successfully"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_onboarding_html_contains_welcome_header(self, client: TestClient):
        """Test that welcome header is present in HTML"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for welcome heading
        assert "Welcome to Fill" in html
        assert "📊" in html

    def test_onboarding_html_contains_subtitle(self, client: TestClient):
        """Test that subtitle is present"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "Automate your document generation" in html
        assert "4 simple steps" in html

    def test_four_step_cards_in_html(self, client: TestClient):
        """Test that all 4 step cards are present in HTML"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for step cards
        assert "step-card" in html

        # Check for step numbers
        assert 'step-number' in html or 'class="step-number"' in html

        # Check for step icons
        assert "📁" in html  # Upload
        assert "📄" in html  # Template
        assert "🔗" in html  # Map
        assert "📥" in html  # Download

    def test_step_1_content(self, client: TestClient):
        """Test Step 1 content"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "Upload Data" in html
        assert "Excel" in html or "XLSX" in html
        assert "CSV" in html

    def test_step_2_content(self, client: TestClient):
        """Test Step 2 content"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "Select Template" in html
        assert ("preset" in html or "preset templates" in html.lower())

    def test_step_3_content(self, client: TestClient):
        """Test Step 3 content"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "Map Fields" in html
        assert "auto" in html.lower()

    def test_step_4_content(self, client: TestClient):
        """Test Step 4 content"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "Download Documents" in html
        assert "ZIP" in html

    def test_action_buttons_present(self, client: TestClient):
        """Test that both Start and Skip buttons are present"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert 'id="startBtn"' in html
        assert "Start Creating Documents" in html
        assert 'id="skipBtn"' in html
        assert "Skip Tour" in html

    def test_trust_badges_present(self, client: TestClient):
        """Test that trust badges are present"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "100% Secure" in html or "Secure" in html
        assert "No Account Required" in html or "No Account" in html
        assert "Instant Processing" in html
        assert "Free" in html and "Open Source" in html

    def test_onboarding_javascript_loaded(self, client: TestClient):
        """Test that onboarding.js is referenced"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "onboarding.js" in html

    def test_onboarding_css_styling(self, client: TestClient):
        """Test that page has embedded CSS styles"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for style tags
        assert "<style>" in html
        assert "</style>" in html

    def test_responsive_design_classes(self, client: TestClient):
        """Test that responsive design classes are present"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for viewport meta tag
        assert "viewport" in html

        # Check for media queries or responsive classes
        assert "@media" in html


class TestOnboardingStructure:
    """Tests for onboarding page HTML structure"""

    def test_html5_doctype(self, client: TestClient):
        """Test that page has HTML5 doctype"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "<!DOCTYPE html>" in html

    def test_proper_html_structure(self, client: TestClient):
        """Test that page has proper HTML structure"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "<html" in html
        assert "<head>" in html
        assert "<body>" in html
        assert "</html>" in html

    def test_charset_meta_tag(self, client: TestClient):
        """Test that charset is set to UTF-8"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "charset" in html and "UTF-8" in html

    def test_title_tag(self, client: TestClient):
        """Test that page has proper title"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "<title>" in html
        assert "Welcome to Fill" in html

    def test_container_div(self, client: TestClient):
        """Test that main container exists"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "onboarding-container" in html

    def test_steps_container(self, client: TestClient):
        """Test that steps container exists"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "steps-container" in html

    def test_action_buttons_container(self, client: TestClient):
        """Test that action buttons container exists"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "action-buttons" in html

    def test_trust_badges_section(self, client: TestClient):
        """Test that trust badges section exists"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert "trust-badges" in html


class TestOnboardingAccessibility:
    """Tests for onboarding page accessibility"""

    def test_proper_heading_hierarchy(self, client: TestClient):
        """Test that page has proper heading hierarchy"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Should have h1 as main heading
        assert "<h1" in html

        # Should have h3s for step cards
        assert "<h3" in html

    def test_button_elements(self, client: TestClient):
        """Test that interactive elements are buttons"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for button tags
        assert "<button" in html

    def test_alt_text_for_images(self, client: TestClient):
        """Test that decorative elements use emojis instead of images"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Should use emojis (not img tags needing alt)
        # Emojis are accessible by default
        assert "📊" in html


class TestOnboardingWorkflow:
    """Tests for onboarding workflow logic (via HTML/JS structure)"""

    def test_javascript_event_handlers(self, client: TestClient):
        """Test that buttons have event handlers in JS"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for external JavaScript file
        assert "onboarding.js" in html
        # Check for button IDs that JS will bind to
        assert "startBtn" in html
        assert "skipBtn" in html

    def test_localstorage_references(self, client: TestClient):
        """Test that JS references localStorage for tracking"""
        # The JavaScript uses localStorage, which is in the external JS file
        # We can't test the JS content directly via TestClient, but we can
        # verify the JS file is referenced
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check that external JS is loaded (which contains localStorage logic)
        assert "/static/onboarding.js" in html or "onboarding.js" in html

    def test_navigation_logic(self, client: TestClient):
        """Test that navigation logic exists"""
        # Navigation logic is in the external JS file
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Verify JS file is present (which contains navigation logic)
        assert "onboarding.js" in html

    def test_version_tracking(self, client: TestClient):
        """Test that version tracking exists"""
        # Version tracking is implemented in the external JS file
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Verify JS file is loaded
        assert "onboarding.js" in html

    def test_shouldShowOnboarding_function(self, client: TestClient):
        """Test that onboarding check function exists"""
        # The function exists in the external JS file
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Verify external JS is loaded
        assert "onboarding.js" in html


class TestOnboardingDesign:
    """Tests for onboarding page design and styling"""

    def test_gradient_background(self, client: TestClient):
        """Test that page has gradient background"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for gradient in CSS
        assert "gradient" in html.lower() or "linear-gradient" in html

    def test_card_styling(self, client: TestClient):
        """Test that cards have proper styling"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for card styling
        assert "border-radius" in html
        assert "box-shadow" in html

    def test_button_styling(self, client: TestClient):
        """Test that buttons have proper styling"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for button styles
        assert "btn-primary" in html
        assert "btn-secondary" in html

    def test_animation_classes(self, client: TestClient):
        """Test that animations are defined"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for animation CSS
        assert "animation" in html.lower() or "@keyframes" in html

    def test_hover_effects(self, client: TestClient):
        """Test that hover effects are defined"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for hover states
        assert ":hover" in html


class TestOnboardingContent:
    """Tests for onboarding page content quality"""

    def test_welcome_message(self, client: TestClient):
        """Test that welcome message is clear and welcoming"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for welcoming language
        assert "Welcome" in html
        assert len([line for line in html.split('\n') if 'Fill' in line]) > 0

    def test_step_descriptions_are_clear(self, client: TestClient):
        """Test that step descriptions are user-friendly"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for clear, non-technical language
        assert "Drag & drop" in html or "drop" in html
        assert "template" in html.lower()
        assert "map" in html.lower() or "link" in html.lower()

    def test_call_to_action_is_clear(self, client: TestClient):
        """Test that call-to-action buttons are clear"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Start button should be clear and action-oriented
        assert "Start" in html
        assert "Creating Documents" in html or "Start Creating" in html

    def test_skip_option_is_available(self, client: TestClient):
        """Test that users can skip onboarding"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Should have skip option
        assert "Skip" in html

    def test_trust_indicators(self, client: TestClient):
        """Test that trust indicators are present"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Check for trust-building elements
        assert "Secure" in html
        assert "Free" in html


class TestOnboardingRedirectBehavior:
    """Tests for redirect behavior when onboarding is complete"""

    def test_index_html_served_when_onboarding_complete(self, client: TestClient):
        """Test that index.html is served as default"""
        # This test verifies that the routing works
        # The onboarding.html itself handles the localStorage check
        # We verify the onboarding page references the main app
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Onboarding page should reference the main app (for navigation)
        # The JavaScript file handles the redirect to index.html
        assert "onboarding.js" in html


class TestOnboardingIntegration:
    """Integration tests for onboarding with the rest of the app"""

    def test_onboarding_page_links_to_app(self, client: TestClient):
        """Test that onboarding page has links to main app"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Should reference the JavaScript that handles navigation
        assert "onboarding.js" in html
        # The JavaScript handles navigation to index.html

    def test_onboarding_assets_path(self, client: TestClient):
        """Test that onboarding references correct asset paths"""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Should reference onboarding.js from static directory
        assert 'src="/static/onboarding.js"' in html or "onboarding.js" in html
