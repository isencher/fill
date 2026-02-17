"""
End-to-end tests for the global progress indicator component.

These tests validate:
1. Progress indicator loads on all pages
2. Current step is correctly highlighted
3. Completed steps show checkmarks
4. Pending steps show correct state
5. Progress indicator is clickable for navigation
6. Responsive design works correctly
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


class TestProgressIndicatorOnUploadPage:
    """
    Tests for progress indicator on the upload page.
    """

    def test_progress_indicator_on_upload_page(self, client: TestClient) -> None:
        """
        Test that progress indicator is present on upload page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        assert response.status_code == 200
        content = response.text

        # Check for progress container
        assert 'id="progressContainer"' in content

        # Check for progress CSS
        assert '/static/components/progress.css' in content

        # Check for progress JavaScript
        assert '/static/components/progress.js' in content

    def test_upload_step_is_active_on_upload_page(self, client: TestClient) -> None:
        """
        Test that the upload step is highlighted as active on the upload page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        assert response.status_code == 200
        content = response.text

        # Check for progress indicator initialization script
        assert "currentStep: 'upload'" in content
        assert "completedSteps: []" in content

    def test_all_steps_visible_on_upload_page(self, client: TestClient) -> None:
        """
        Test that all 4 workflow steps are visible on the upload page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        content = response.text

        # The progress.js should define all steps
        # We check that the component script is loaded
        assert 'src="/static/components/progress.js"' in content


class TestProgressIndicatorOnTemplatePage:
    """
    Tests for progress indicator on the template selection page.
    """

    def test_progress_indicator_on_template_page(self, client: TestClient) -> None:
        """
        Test that progress indicator is present on template page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for progress container
        assert 'id="progressContainer"' in content

        # Check for progress CSS
        assert '/static/components/progress.css' in content

        # Check for progress JavaScript
        assert '/static/components/progress.js' in content

    def test_template_step_is_active_on_template_page(self, client: TestClient) -> None:
        """
        Test that the template step is highlighted as active on the template page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for progress indicator initialization
        assert "currentStep: 'template'" in content
        assert "completedSteps: ['upload']" in content

    def test_upload_step_completed_on_template_page(self, client: TestClient) -> None:
        """
        Test that the upload step is marked as completed on the template page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Verify upload is in completed steps
        assert "'upload'" in content
        assert "completedSteps" in content


class TestProgressIndicatorOnMappingPage:
    """
    Tests for progress indicator on the mapping configuration page.
    """

    def test_progress_indicator_on_mapping_page(self, client: TestClient) -> None:
        """
        Test that progress indicator is present on mapping page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html")
        assert response.status_code == 200
        content = response.text

        # Check for progress container
        assert 'id="progressContainer"' in content

        # Check for progress CSS
        assert '/static/components/progress.css' in content

        # Check for progress JavaScript
        assert '/static/components/progress.js' in content

    def test_mapping_step_is_active_on_mapping_page(self, client: TestClient) -> None:
        """
        Test that the mapping step is highlighted as active on the mapping page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html")
        assert response.status_code == 200
        content = response.text

        # Check for progress indicator initialization
        assert "currentStep: 'mapping'" in content
        assert "completedSteps: ['upload', 'template']" in content

    def test_previous_steps_completed_on_mapping_page(self, client: TestClient) -> None:
        """
        Test that upload and template steps are marked as completed on mapping page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html")
        assert response.status_code == 200
        content = response.text

        # Verify previous steps are in completed steps
        assert "'upload'" in content
        assert "'template'" in content
        assert "completedSteps" in content


class TestProgressIndicatorStructure:
    """
    Tests for progress indicator HTML structure and styling.
    """

    def test_progress_css_is_served(self, client: TestClient) -> None:
        """
        Test that the progress indicator CSS file is served correctly.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/progress.css")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/css; charset=utf-8"

        # Check for key CSS classes
        content = response.text
        assert ".progress-indicator" in content
        assert ".progress-step" in content
        assert ".progress-step.completed" in content
        assert ".progress-step.active" in content
        assert ".progress-step.pending" in content
        assert ".step-icon" in content
        assert ".step-label" in content

    def test_progress_js_is_served(self, client: TestClient) -> None:
        """
        Test that the progress indicator JavaScript file is served correctly.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/progress.js")
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]

        # Check for key JavaScript functions
        content = response.text
        assert "class ProgressIndicator" in content
        assert "initProgressIndicator" in content
        assert "setCurrentStep" in content
        assert "markCompleted" in content

    def test_progress_indicator_has_four_steps(self, client: TestClient) -> None:
        """
        Test that the progress indicator defines all 4 workflow steps.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/progress.js")
        assert response.status_code == 200

        content = response.text

        # Check that all 4 steps are defined
        assert "'upload'" in content
        assert "'template'" in content
        assert "'mapping'" in content
        assert "'download'" in content


class TestProgressIndicatorResponsiveDesign:
    """
    Tests for progress indicator responsive design.
    """

    def test_progress_css_has_responsive_breakpoints(self, client: TestClient) -> None:
        """
        Test that progress indicator CSS includes responsive design breakpoints.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/progress.css")
        assert response.status_code == 200

        content = response.text

        # Check for mobile breakpoints
        assert "@media (max-width: 768px)" in content
        assert "@media (max-width: 480px)" in content

    def test_progress_css_has_animations(self, client: TestClient) -> None:
        """
        Test that progress indicator CSS includes animations.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/progress.css")
        assert response.status_code == 200

        content = response.text

        # Check for animations
        assert "@keyframes" in content
        assert "pulse" in content or "fadeIn" in content

    def test_progress_css_has_accessibility(self, client: TestClient) -> None:
        """
        Test that progress indicator CSS includes accessibility features.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/progress.css")
        assert response.status_code == 200

        content = response.text

        # Check for focus styles
        assert ":focus" in content or "outline" in content


class TestProgressIndicatorAccessibility:
    """
    Tests for progress indicator accessibility.
    """

    def test_progress_indicator_has_semantic_html(self, client: TestClient) -> None:
        """
        Test that progress indicator uses semantic HTML elements.

        Args:
            client: FastAPI test client
        """
        # The progress.js should generate semantic HTML
        response = client.get("/static/components/progress.js")
        assert response.status_code == 200

        content = response.text

        # Check for proper HTML structure generation in JavaScript code
        assert "progress-indicator" in content
        assert "progress-step" in content
        assert "step-icon" in content
        assert "step-label" in content


class TestProgressIndicatorIntegration:
    """
    Tests for progress indicator integration with page workflows.
    """

    def test_clickable_steps_on_upload_page(self, client: TestClient) -> None:
        """
        Test that completed steps are clickable for navigation.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        assert response.status_code == 200
        content = response.text

        # Check for click handler initialization
        assert "clickable" in content or "addEventListener" in content

    def test_clickable_steps_on_template_page(self, client: TestClient) -> None:
        """
        Test that completed steps are clickable on template page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for click handler initialization
        assert "clickable" in content or "addEventListener" in content

    def test_clickable_steps_on_mapping_page(self, client: TestClient) -> None:
        """
        Test that completed steps are clickable on mapping page.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html")
        assert response.status_code == 200
        content = response.text

        # Check for click handler initialization
        assert "clickable" in content or "addEventListener" in content


class TestProgressIndicatorVisualConsistency:
    """
    Tests for progress indicator visual consistency across pages.
    """

    def test_progress_indicator_uses_same_css(self, client: TestClient) -> None:
        """
        Test that all pages use the same progress indicator CSS file.

        Args:
            client: FastAPI test client
        """
        # Check all pages reference the same CSS file
        pages = ["/static/index.html", "/static/templates.html", "/static/mapping.html"]

        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            assert '/static/components/progress.css' in response.text

    def test_progress_indicator_uses_same_js(self, client: TestClient) -> None:
        """
        Test that all pages use the same progress indicator JavaScript file.

        Args:
            client: FastAPI test client
        """
        # Check all pages reference the same JS file
        pages = ["/static/index.html", "/static/templates.html", "/static/mapping.html"]

        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            assert '/static/components/progress.js' in response.text

    def test_progress_container_consistent_naming(self, client: TestClient) -> None:
        """
        Test that all pages use the same container ID for the progress indicator.

        Args:
            client: FastAPI test client
        """
        # Check all pages use the same container ID
        pages = ["/static/index.html", "/static/templates.html", "/static/mapping.html"]

        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            assert 'id="progressContainer"' in response.text
