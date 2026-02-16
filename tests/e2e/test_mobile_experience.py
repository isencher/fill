"""
E2E Tests for Mobile Experience Improvements
Tests mobile viewport optimizations using TestClient
"""

import io

import pytest
from fastapi.testclient import TestClient

from src.main import app, _uploaded_files


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestMobileCSSLoad:
    """Test mobile CSS is properly loaded"""

    def test_index_html_includes_mobile_css(self, client: TestClient):
        """Test index.html includes mobile.css"""
        response = client.get("/static/index.html")
        assert response.status_code == 200

        # Check mobile.css is included
        assert 'href="/static/mobile.css"' in response.text

    def test_templates_html_includes_mobile_css(self, client: TestClient):
        """Test templates.html includes mobile.css"""
        response = client.get("/static/templates.html")
        assert response.status_code == 200

        # Check mobile.css is included
        assert 'href="/static/mobile.css"' in response.text

    def test_mapping_html_includes_mobile_css(self, client: TestClient):
        """Test mapping.html includes mobile.css"""
        response = client.get("/static/mapping.html")
        assert response.status_code == 200

        # Check mobile.css is included
        assert 'href="/static/mobile.css"' in response.text

    def test_onboarding_html_includes_mobile_css(self, client: TestClient):
        """Test onboarding.html includes mobile.css"""
        response = client.get("/static/onboarding.html")
        assert response.status_code == 200

        # Check mobile.css is included
        assert 'href="/static/mobile.css"' in response.text


class TestMobileCSSContent:
    """Test mobile CSS has required optimizations"""

    def test_mobile_css_has_media_queries(self, client: TestClient):
        """Test mobile.css includes responsive media queries"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for mobile media query
        assert "@media (max-width: 767px)" in css_content

    def test_mobile_css_has_touch_target_sizes(self, client: TestClient):
        """Test mobile.css defines touch target sizes"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for minimum touch target sizing
        assert "min-height: 44px" in css_content
        assert "min-width: 44px" in css_content

    def test_mobile_css_has_font_size_prevent_zoom(self, client: TestClient):
        """Test mobile.css prevents iOS zoom on input focus"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for 16px font size to prevent zoom
        assert "font-size: 16px" in css_content

    def test_mobile_css_has_sticky_buttons(self, client: TestClient):
        """Test mobile.css includes sticky button positioning"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for sticky positioning
        assert "position: sticky" in css_content
        assert "bottom: 0" in css_content

    def test_mobile_css_has_full_width_dropdowns(self, client: TestClient):
        """Test mobile.css makes dropdowns full width"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for full width selects
        assert ".placeholder-select" in css_content
        assert "width: 100%" in css_content

    def test_mobile_css_has_table_scroll(self, client: TestClient):
        """Test mobile.css enables table scrolling"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for scrollable tables
        assert ".data-table-wrapper" in css_content
        assert "overflow" in css_content

    def test_mobile_css_has_vertical_stack(self, client: TestClient):
        """Test mobile.css stacks layout vertically"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for single column grid
        assert "grid-template-columns: 1fr" in css_content

    def test_mobile_css_has_reduced_motion(self, client: TestClient):
        """Test mobile.css respects reduced motion preference"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for reduced motion support
        assert "prefers-reduced-motion" in css_content

    def test_mobile_css_has_safe_area_support(self, client: TestClient):
        """Test mobile.css supports safe area for notched devices"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for safe area support
        assert "safe-area-inset" in css_content

    def test_mobile_css_has_landscape_optimizations(self, client: TestClient):
        """Test mobile.css includes landscape mode optimizations"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for landscape media query
        assert "orientation: landscape" in css_content

    def test_mobile_css_has_tablet_optimizations(self, client: TestClient):
        """Test mobile.css includes tablet optimizations"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for tablet media query
        assert "@media (min-width: 768px)" in css_content


class TestMobileResponsiveLayout:
    """Test responsive layout behavior"""

    def test_mapping_page_responsive_markup(self, client: TestClient):
        """Test mapping.html has responsive markup structure"""
        response = client.get("/static/mapping.html")
        assert response.status_code == 200

        html_content = response.text

        # Check for content grid that can be stacked
        assert 'class="content"' in html_content

        # Check for panels that can stack
        assert 'class="panel"' in html_content

    def test_templates_page_responsive_markup(self, client: TestClient):
        """Test templates.html has responsive markup structure"""
        response = client.get("/static/templates.html")
        assert response.status_code == 200

        html_content = response.text

        # Check for templates grid (id is templateGrid)
        assert 'template-grid' in html_content or 'templateGrid' in html_content

        # Check for template cards
        assert 'template-card' in html_content

    def test_upload_page_responsive_markup(self, client: TestClient):
        """Test index.html has responsive markup structure"""
        response = client.get("/static/index.html")
        assert response.status_code == 200

        html_content = response.text

        # Check for upload area
        assert 'class="upload-area"' in html_content

        # Check for responsive viewport meta tag
        assert '<meta name="viewport"' in html_content
        assert 'width=device-width' in html_content


class TestMobileTouchTargets:
    """Test touch target optimizations"""

    def test_buttons_have_adequate_padding(self, client: TestClient):
        """Test buttons have padding for adequate touch targets"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for button padding
        assert "button" in css_content
        assert "padding:" in css_content

    def test_links_have_adequate_touch_area(self, client: TestClient):
        """Test links have adequate touch area"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for link touch targets
        assert "a {" in css_content or "a\n{" in css_content
        assert "min-height" in css_content


class TestMobileAccessibility:
    """Test accessibility improvements on mobile"""

    def test_focus_visible_styles(self, client: TestClient):
        """Test focus states are visible for keyboard navigation"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for focus-visible styles
        assert ":focus-visible" in css_content
        assert "outline" in css_content

    def test_active_state_feedback(self, client: TestClient):
        """Test active states provide visual feedback"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for active states
        assert ":active" in css_content
        assert "transform" in css_content


class TestMobileViewportMeta:
    """Test viewport meta tag configuration"""

    def test_index_html_viewport_meta(self, client: TestClient):
        """Test index.html has proper viewport meta tag"""
        response = client.get("/static/index.html")
        assert response.status_code == 200

        html_content = response.text

        # Check for viewport meta tag
        assert '<meta name="viewport"' in html_content
        assert 'width=device-width' in html_content
        assert 'initial-scale=1.0' in html_content

    def test_templates_html_viewport_meta(self, client: TestClient):
        """Test templates.html has proper viewport meta tag"""
        response = client.get("/static/templates.html")
        assert response.status_code == 200

        html_content = response.text

        # Check for viewport meta tag
        assert '<meta name="viewport"' in html_content
        assert 'width=device-width' in html_content

    def test_mapping_html_viewport_meta(self, client: TestClient):
        """Test mapping.html has proper viewport meta tag"""
        response = client.get("/static/mapping.html")
        assert response.status_code == 200

        html_content = response.text

        # Check for viewport meta tag
        assert '<meta name="viewport"' in html_content
        assert 'width=device-width' in html_content


class TestMobilePerformance:
    """Test performance optimizations"""

    def test_reduced_motion_media_query(self, client: TestClient):
        """Test reduced motion is respected"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for reduced motion media query
        assert "@media (prefers-reduced-motion: reduce)" in css_content

    def test_animation_durations_reduced(self, client: TestClient):
        """Test animations can be reduced for performance"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for reduced animation durations
        assert "animation-duration: 0.01ms" in css_content


class TestMobileFileAccess:
    """Test mobile.css file is accessible"""

    def test_mobile_css_content_type(self, client: TestClient):
        """Test mobile.css has correct content type"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        # Check content type
        assert response.headers["content-type"] == "text/css; charset=utf-8" or \
               "text/css" in response.headers["content-type"]

    def test_mobile_css_not_empty(self, client: TestClient):
        """Test mobile.css has content"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        # Check file has substantial content
        assert len(response.text) > 1000

    def test_mobile_css_well_formed(self, client: TestClient):
        """Test mobile.css is well-formed CSS"""
        response = client.get("/static/mobile.css")
        assert response.status_code == 200

        css_content = response.text

        # Check for CSS structure
        assert "/*" in css_content  # Has comments
        assert "{" in css_content  # Has rules
        assert "}" in css_content  # Has closing braces
        assert css_content.count("{") == css_content.count("}")  # Balanced braces


class TestMobileIntegration:
    """Test mobile optimizations work together"""

    def test_complete_mobile_stack(self, client: TestClient):
        """Test complete mobile optimization stack is present"""
        # 1. Check mobile.css exists and loads
        css_response = client.get("/static/mobile.css")
        assert css_response.status_code == 200
        assert len(css_response.text) > 1000

        # 2. Check index.html includes mobile.css
        index_response = client.get("/static/index.html")
        assert index_response.status_code == 200
        assert 'href="/static/mobile.css"' in index_response.text

        # 3. Check mobile.css has all key features
        css_content = css_response.text
        assert "@media (max-width: 767px)" in css_content  # Mobile breakpoint
        assert "min-height: 44px" in css_content  # Touch targets
        assert "position: sticky" in css_content  # Sticky buttons
        assert "width: 100%" in css_content  # Full width elements
        assert "overflow" in css_content  # Scrollable tables

    def test_all_pages_include_mobile_css(self, client: TestClient):
        """Test all main pages include mobile.css"""

        pages = [
            "/static/index.html",
            "/static/templates.html",
            "/static/mapping.html",
            "/static/onboarding.html",
        ]

        for page in pages:
            response = client.get(page)
            assert response.status_code == 200, f"{page} should load"
            assert 'href="/static/mobile.css"' in response.text, f"{page} should include mobile.css"
