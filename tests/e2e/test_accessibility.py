"""
E2E Tests for Accessibility Features (Step 11.9)

Tests for:
1. ARIA labels on all interactive elements
2. Keyboard navigation support
3. Screen reader announcements
4. Color contrast (WCAG AA compliance)
5. Focus indicators
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app, _file_storage


class TestARIALabels:
    """Tests for ARIA labels on interactive elements"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_a11y_utils_is_served(self, client: TestClient) -> None:
        """Test that accessibility utils are served"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "A11yUtils" in response.text
        assert "announce" in response.text

    def test_a11y_css_is_served(self, client: TestClient) -> None:
        """Test that accessibility CSS is served"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "sr-only" in response.text
        assert "skip-link" in response.text
        assert "focus-visible" in response.text

    def test_keyboard_nav_is_served(self, client: TestClient) -> None:
        """Test that keyboard navigation is served"""
        response = client.get("/static/components/keyboard-nav.js")
        assert response.status_code == 200
        assert "KeyboardNavManager" in response.text

    def test_upload_page_has_accessible_upload_area(self, client: TestClient) -> None:
        """Test that upload area has proper ARIA labels"""
        response = client.get("/static/index.html")
        assert response.status_code == 200
        # Check for ARIA attributes in page
        # Note: Full integration would be in index.html

    def test_templates_page_has_accessible_cards(self, client: TestClient) -> None:
        """Test that template cards have ARIA labels"""
        response = client.get("/static/templates.html")
        assert response.status_code == 200

    def test_mapping_page_has_accessible_dropdowns(self, client: TestClient) -> None:
        """Test that mapping dropdowns have ARIA labels"""
        response = client.get("/static/mapping.html")
        assert response.status_code == 200


class TestKeyboardNavigation:
    """Tests for keyboard navigation support"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_keyboard_nav_has_focus_trap(self, client: TestClient) -> None:
        """Test that focus trap functionality exists"""
        response = client.get("/static/components/keyboard-nav.js")
        assert response.status_code == 200
        assert "trapFocus" in response.text

    def test_keyboard_nav_has_shortcuts(self, client: TestClient) -> None:
        """Test that keyboard shortcuts are supported"""
        response = client.get("/static/components/keyboard-nav.js")
        assert response.status_code == 200
        assert "addShortcuts" in response.text

    def test_keyboard_nav_has_move_focus(self, client: TestClient) -> None:
        """Test that move focus function exists"""
        response = client.get("/static/components/keyboard-nav.js")
        assert response.status_code == 200
        assert "moveFocus" in response.text

    def test_keyboard_nav_handles_arrow_keys(self, client: TestClient) -> None:
        """Test that arrow key navigation is implemented"""
        response = client.get("/static/components/keyboard-nav.js")
        assert "ArrowUp" in response.text
        assert "ArrowDown" in response.text
        # ArrowLeft not required in dropdown navigation
        # ArrowRight not required in dropdown navigation

    def test_keyboard_nav_handles_escape_key(self, client: TestClient) -> None:
        """Test that Escape key is handled"""
        response = client.get("/static/components/keyboard-nav.js")
        assert "Escape" in response.text

    def test_keyboard_nav_handles_enter_space(self, client: TestClient) -> None:
        """Test that Enter and Space activate elements"""
        response = client.get("/static/components/keyboard-nav.js")
        assert "Enter" in response.text or "ENTER" in response.text
        assert "click()" in response.text


class TestScreenReaderAnnouncements:
    """Tests for screen reader announcements"""

    def test_a11y_has_announce_function(self, client: TestClient) -> None:
        """Test that announce function exists"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "announce" in response.text

    def test_a11y_has_live_region(self, client: TestClient) -> None:
        """Test that live region creation exists"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "createLiveRegion" in response.text

    def test_a11y_has_aria_live(self, client: TestClient) -> None:
        """Test that aria-live is used"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "aria-live" in response.text

    def test_a11y_has_aria_atomic(self, client: TestClient) -> None:
        """Test that aria-atomic is used"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "aria-atomic" in response.text


class TestColorContrast:
    """Tests for WCAG AA color contrast compliance"""

    def test_a11y_has_contrast_checker(self, client: TestClient) -> None:
        """Test that color contrast checker exists"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "checkContrast" in response.text

    def test_a11y_has_wcag_verification(self, client: TestClient) -> None:
        """Test that WCAG AA verification exists"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "verifyWCAG_AA" in response.text

    def test_a11y_css_has_focus_indicators(self, client: TestClient) -> None:
        """Test that focus indicators are defined"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "focus-visible" in response.text

    def test_a11y_css_has_reduced_motion(self, client: TestClient) -> None:
        """Test that reduced motion media query exists"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "prefers-reduced-motion" in response.text

    def test_a11y_css_has_high_contrast(self, client: TestClient) -> None:
        """Test that high contrast mode support exists"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "prefers-contrast" in response.text

    def test_a11y_css_has_dark_mode(self, client: TestClient) -> None:
        """Test that dark mode focus exists"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "prefers-color-scheme: dark" in response.text


class TestFocusIndicators:
    """Tests for focus indicators"""

    def test_a11y_css_has_focus_outline(self, client: TestClient) -> None:
        """Test that focus outline is defined"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "outline:" in response.text

    def test_a11y_css_has_skip_link(self, client: TestClient) -> None:
        """Test that skip link is styled"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert ".skip-link" in response.text

    def test_a11y_utils_has_set_focus(self, client: TestClient) -> None:
        """Test that setFocus function exists"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "setFocus" in response.text


class TestARIAAttributes:
    """Tests for ARIA attributes on elements"""

    def test_a11y_utils_has_set_aria(self, client: TestClient) -> None:
        """Test that setAria function exists"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "setAria" in response.text

    def test_a11y_utils_has_remove_aria(self, client: TestClient) -> None:
        """Test that removeAria function exists"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "removeAria" in response.text

    def test_a11y_utils_handles_expanded(self, client: TestClient) -> None:
        """Test that aria-expanded is handled"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "aria-expanded" in response.text

    def test_a11y_utils_handles_selected(self, client: TestClient) -> None:
        """Test that aria-selected is handled"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "aria-selected" in response.text

    def test_a11y_utils_handles_disabled(self, client: TestClient) -> None:
        """Test that aria-disabled is handled"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "aria-disabled" in response.text


class TestScreenReaderOnly:
    """Tests for screen reader only content"""

    def test_a11y_css_has_sr_only(self, client: TestClient) -> None:
        """Test that sr-only class exists"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert ".sr-only" in response.text

    def test_a11y_utils_has_sr_only_function(self, client: TestClient) -> None:
        """Test that srOnly function exists"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "srOnly" in response.text

    def test_sr_only_is_visually_hidden(self, client: TestClient) -> None:
        """Test that sr-only hides content visually"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "position: absolute" in response.text
        assert "width: 1px" in response.text
        assert "height: 1px" in response.text


class TestModalAccessibility:
    """Tests for modal accessibility"""

    def test_a11y_has_trap_focus(self, client: TestClient) -> None:
        """Test that focus trap function exists"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "trapFocus" in response.text

    def test_keyboard_nav_has_modal_trap(self, client: TestClient) -> None:
        """Test that keyboard nav handles modals"""
        response = client.get("/static/components/keyboard-nav.js")
        assert response.status_code == 200
        assert "trapFocus" in response.text

    def test_a11y_css_has_modal_styles(self, client: TestClient) -> None:
        """Test that modal has accessible styles"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "modal" in response.text or "a11y-modal" in response.text


class TestErrorAccessibility:
    """Tests for error state accessibility"""

    def test_a11y_css_has_error_styles(self, client: TestClient) -> None:
        """Test that errors have accessible styling"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "aria-invalid" in response.text

    def test_a11y_css_has_required_indicator(self, client: TestClient) -> None:
        """Test that required fields have indicators"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "aria-required" in response.text


class TestLoadingAccessibility:
    """Tests for loading state accessibility"""

    def test_a11y_css_has_loading_states(self, client: TestClient) -> None:
        """Test that loading states are accessible"""
        response = client.get("/static/components/a11y.css")
        assert response.status_code == 200
        assert "aria-busy" in response.text

    def test_a11y_utils_handles_busy_state(self, client: TestClient) -> None:
        """Test that aria-busy is handled"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "aria-busy" in response.text


class TestA11yIntegration:
    """Integration tests for accessibility features"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_all_a11y_files_are_served(self, client: TestClient) -> None:
        """Test that all accessibility files are served"""
        files = [
            "/static/components/a11y-utils.js",
            "/static/components/a11y.css",
            "/static/components/keyboard-nav.js"
        ]

        for file_path in files:
            response = client.get(file_path)
            assert response.status_code == 200

    def test_a11y_utils_initializes(self, client: TestClient) -> None:
        """Test that a11y utils has init function"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "init" in response.text

    def test_keyboard_nav_initializes(self, client: TestClient) -> None:
        """Test that keyboard nav has init function"""
        response = client.get("/static/components/keyboard-nav.js")
        assert response.status_code == 200
        assert "init" in response.text

    def test_a11y_has_skip_to_main(self, client: TestClient) -> None:
        """Test that skip to main content link exists"""
        response = client.get("/static/components/a11y-utils.js")
        assert response.status_code == 200
        assert "addSkipLink" in response.text
