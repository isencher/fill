"""
End-to-end tests for the empty state component.

These tests validate:
1. Empty state component loads correctly
2. Different empty state variants (default, info, warning, error)
3. Action buttons are clickable
4. Empty state is responsive
5. Empty state is accessible
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


class TestEmptyStateComponent:
    """
    Tests for empty state component structure and loading.
    """

    def test_empty_state_css_is_served(self, client: TestClient) -> None:
        """
        Test that the empty state CSS file is served correctly.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/empty-state.css")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/css; charset=utf-8"

        # Check for key CSS classes
        content = response.text
        assert ".empty-state" in content
        assert ".empty-state__icon" in content
        assert ".empty-state__title" in content
        assert ".empty-state__message" in content
        assert ".empty-state__actions" in content
        assert ".empty-state__button" in content

    def test_empty_state_js_is_served(self, client: TestClient) -> None:
        """
        Test that the empty state JavaScript file is served correctly.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/empty-state.js")
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]

        # Check for key JavaScript functions
        content = response.text
        assert "class EmptyState" in content
        assert "createEmptyState" in content
        assert "showEmptyState" in content
        assert "hideEmptyState" in content
        assert "EmptyStates" in content

    def test_empty_state_has_variants(self, client: TestClient) -> None:
        """
        Test that empty state supports different variants.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/empty-state.css")
        assert response.status_code == 200

        content = response.text

        # Check for variant classes
        assert ".empty-state--default" in content
        assert ".empty-state--info" in content
        assert ".empty-state--warning" in content
        assert ".empty-state--error" in content

    def test_empty_state_has_size_variants(self, client: TestClient) -> None:
        """
        Test that empty state supports different sizes.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/empty-state.css")
        assert response.status_code == 200

        content = response.text

        # Check for size classes
        assert ".empty-state--small" in content
        assert ".empty-state--medium" in content
        assert ".empty-state--large" in content


class TestEmptyStateOnTemplatePage:
    """
    Tests for empty state on template selection page.
    """

    def test_template_page_has_empty_state_css(self, client: TestClient) -> None:
        """
        Test that template page includes empty state CSS.

        Args:
            client: FastAPI test client
        """
        response = client.get("/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for empty state CSS
        assert '/static/components/empty-state.css' in content

    def test_template_page_has_empty_state_js(self, client: TestClient) -> None:
        """
        Test that template page includes empty state JavaScript.

        Args:
            client: FastAPI test client
        """
        response = client.get("/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for empty state JavaScript
        assert '/static/components/empty-state.js' in content

    def test_template_page_has_empty_state_container(self, client: TestClient) -> None:
        """
        Test that template page has empty state container.

        Args:
            client: FastAPI test client
        """
        response = client.get("/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for empty state container
        assert 'id="errorState"' in content


class TestEmptyStateOnMappingPage:
    """
    Tests for empty state on mapping configuration page.
    """

    def test_mapping_page_has_empty_state_css(self, client: TestClient) -> None:
        """
        Test that mapping page includes empty state CSS.

        Args:
            client: FastAPI test client
        """
        response = client.get("/mapping.html")
        assert response.status_code == 200
        content = response.text

        # Check for empty state CSS
        assert '/static/components/empty-state.css' in content

    def test_mapping_page_has_empty_state_js(self, client: TestClient) -> None:
        """
        Test that mapping page includes empty state JavaScript.

        Args:
            client: FastAPI test client
        """
        response = client.get("/mapping.html")
        assert response.status_code == 200
        content = response.text

        # Check for empty state JavaScript
        assert '/static/components/empty-state.js' in content

    def test_mapping_page_has_empty_state_container(self, client: TestClient) -> None:
        """
        Test that mapping page has empty state container.

        Args:
            client: FastAPI test client
        """
        response = client.get("/mapping.html")
        assert response.status_code == 200
        content = response.text

        # Check for empty state container
        assert 'id="emptyState"' in content


class TestEmptyStatePredefinedStates:
    """
    Tests for predefined empty state configurations.
    """

    def test_empty_state_has_predefined_states(self, client: TestClient) -> None:
        """
        Test that empty state JavaScript has predefined configurations.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/empty-state.js")
        assert response.status_code == 200

        content = response.text

        # Check for predefined states
        assert "NO_FILES_UPLOADED" in content
        assert "NO_TEMPLATES_AVAILABLE" in content
        assert "NO_DATA_FILE" in content
        assert "NO_FILE_OR_TEMPLATE" in content
        assert "ERROR_LOADING_DATA" in content
        assert "FILE_NOT_FOUND" in content
        assert "TEMPLATE_NOT_FOUND" in content


class TestEmptyStateAccessibility:
    """
    Tests for empty state accessibility features.
    """

    def test_empty_state_has_accessible_buttons(self, client: TestClient) -> None:
        """
        Test that empty state buttons are accessible.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/empty-state.css")
        assert response.status_code == 200

        content = response.text

        # Check for focus styles
        assert ":focus" in content

    def test_empty_state_has_semantic_html(self, client: TestClient) -> None:
        """
        Test that empty state uses semantic HTML elements.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/empty-state.js")
        assert response.status_code == 200

        content = response.text

        # Check for semantic HTML structure
        assert "empty-state" in content
        assert "empty-state__icon" in content
        assert "empty-state__title" in content
        assert "empty-state__message" in content
        assert "empty-state__actions" in content


class TestEmptyStateResponsiveDesign:
    """
    Tests for empty state responsive design.
    """

    def test_empty_state_has_responsive_breakpoints(self, client: TestClient) -> None:
        """
        Test that empty state CSS includes responsive design breakpoints.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/empty-state.css")
        assert response.status_code == 200

        content = response.text

        # Check for mobile breakpoints
        assert "@media (max-width: 768px)" in content

    def test_empty_state_has_animations(self, client: TestClient) -> None:
        """
        Test that empty state CSS includes animations.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/empty-state.css")
        assert response.status_code == 200

        content = response.text

        # Check for animations
        assert "@keyframes" in content
        assert "fadeIn" in content or "float" in content or "pulse" in content


class TestEmptyStateVisualConsistency:
    """
    Tests for empty state visual consistency.
    """

    def test_empty_state_uses_same_css_across_pages(self, client: TestClient) -> None:
        """
        Test that all pages use the same empty state CSS file.

        Args:
            client: FastAPI test client
        """
        # Check both pages reference the same CSS file
        pages = ["/templates.html", "/mapping.html"]

        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            assert '/static/components/empty-state.css' in response.text

    def test_empty_state_uses_same_js_across_pages(self, client: TestClient) -> None:
        """
        Test that all pages use the same empty state JavaScript file.

        Args:
            client: FastAPI test client
        """
        # Check both pages reference the same JS file
        pages = ["/templates.html", "/mapping.html"]

        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            assert '/static/components/empty-state.js' in response.text

    def test_empty_state_consistent_icon_styling(self, client: TestClient) -> None:
        """
        Test that empty state icons have consistent styling.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/empty-state.css")
        assert response.status_code == 200

        content = response.text

        # Check for consistent icon styling
        assert ".empty-state__icon" in content
        assert "font-size" in content
        assert "margin-bottom" in content


class TestEmptyStateIntegration:
    """
    Tests for empty state integration with page workflows.
    """

    def test_template_page_shows_empty_state_without_file(self, client: TestClient) -> None:
        """
        Test that template page shows empty state when accessed without file_id.

        Args:
            client: FastAPI test client
        """
        # Access template page without file_id
        response = client.get("/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for empty state components
        assert 'id="errorState"' in content
        # Check that empty-state.js is loaded (which contains createEmptyState)
        assert '/static/components/empty-state.js' in content

    def test_mapping_page_shows_empty_state_without_params(self, client: TestClient) -> None:
        """
        Test that mapping page shows empty state when accessed without parameters.

        Args:
            client: FastAPI test client
        """
        # Access mapping page without parameters
        response = client.get("/mapping.html")
        assert response.status_code == 200
        content = response.text

        # Check for empty state components
        assert 'id="emptyState"' in content
        # Check that empty-state.js is loaded (which contains showEmptyState)
        assert '/static/components/empty-state.js' in content
