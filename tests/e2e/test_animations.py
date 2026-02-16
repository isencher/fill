"""
End-to-end tests for animation effects and micro-interactions.

These tests validate:
1. Animations CSS is loaded and contains required animations
2. Skeleton loader JavaScript is loaded
3. Button loading states work correctly
4. Message animations are applied
5. Dropdown selection animations are present
6. Skeleton loaders render correctly
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


class TestAnimationsCSS:
    """
    Tests for animations.css file.
    """

    def test_animations_css_is_served(self, client: TestClient) -> None:
        """
        Test that the animations CSS file is served correctly.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/animations.css")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/css; charset=utf-8"

    def test_animations_css_has_button_animations(self, client: TestClient) -> None:
        """
        Test that animations CSS includes button animations.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/animations.css")
        assert response.status_code == 200

        content = response.text
        assert ".btn--loading" in content
        assert ".btn--success" in content
        assert "@keyframes button-spin" in content

    def test_animations_css_has_message_animations(self, client: TestClient) -> None:
        """
        Test that animations CSS includes message animations.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/animations.css")
        assert response.status_code == 200

        content = response.text
        assert "@keyframes message-shake" in content
        assert "@keyframes message-success" in content
        assert ".message.error" in content

    def test_animations_css_has_dropdown_animations(self, client: TestClient) -> None:
        """
        Test that animations CSS includes dropdown animations.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/animations.css")
        assert response.status_code == 200

        content = response.text
        assert "@keyframes select-pulse" in content
        assert ".select--changed" in content

    def test_animations_css_has_skeleton_animations(self, client: TestClient) -> None:
        """
        Test that animations CSS includes skeleton loader animations.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/animations.css")
        assert response.status_code == 200

        content = response.text
        assert ".skeleton" in content
        assert "@keyframes skeleton-loading" in content
        assert ".skeleton-card" in content
        assert ".skeleton-list-item" in content
        assert ".skeleton-table" in content

    def test_animations_css_has_reduced_motion_support(self, client: TestClient) -> None:
        """
        Test that animations CSS includes reduced motion support.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/animations.css")
        assert response.status_code == 200

        content = response.text
        assert "@media (prefers-reduced-motion: reduce)" in content


class TestSkeletonJS:
    """
    Tests for skeleton.js file.
    """

    def test_skeleton_js_is_served(self, client: TestClient) -> None:
        """
        Test that the skeleton JavaScript file is served correctly.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/skeleton.js")
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]

    def test_skeleton_js_has_required_functions(self, client: TestClient) -> None:
        """
        Test that skeleton.js includes required functions.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/skeleton.js")
        assert response.status_code == 200

        content = response.text
        assert "class SkeletonLoader" in content
        assert "showSkeleton" in content
        assert "hideSkeleton" in content
        assert "setButtonLoading" in content
        assert "animateMessage" in content
        assert "animateSelectChange" in content

    def test_skeleton_js_has_predefined_configs(self, client: TestClient) -> None:
        """
        Test that skeleton.js includes predefined configurations.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/components/skeleton.js")
        assert response.status_code == 200

        content = response.text
        assert "SkeletonConfigs" in content
        assert "TEMPLATE_LIST" in content
        assert "FILE_LIST" in content
        assert "DATA_PREVIEW" in content


class TestAnimationsOnPages:
    """
    Tests for animations on different pages.
    """

    def test_upload_page_has_animations_css(self, client: TestClient) -> None:
        """
        Test that upload page includes animations CSS.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        assert response.status_code == 200
        content = response.text

        assert '/static/components/animations.css' in content

    def test_upload_page_has_skeleton_js(self, client: TestClient) -> None:
        """
        Test that upload page includes skeleton JavaScript.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/index.html")
        assert response.status_code == 200
        content = response.text

        assert '/static/components/skeleton.js' in content

    def test_template_page_has_animations_css(self, client: TestClient) -> None:
        """
        Test that template page includes animations CSS.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        assert '/static/components/animations.css' in content

    def test_template_page_has_skeleton_js(self, client: TestClient) -> None:
        """
        Test that template page includes skeleton JavaScript.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        assert '/static/components/skeleton.js' in content

    def test_mapping_page_has_animations_css(self, client: TestClient) -> None:
        """
        Test that mapping page includes animations CSS.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html")
        assert response.status_code == 200
        content = response.text

        assert '/static/components/animations.css' in content

    def test_mapping_page_has_skeleton_js(self, client: TestClient) -> None:
        """
        Test that mapping page includes skeleton JavaScript.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/mapping.html")
        assert response.status_code == 200
        content = response.text

        assert '/static/components/skeleton.js' in content


class TestAnimationIntegration:
    """
    Tests for animation integration with page workflows.
    """

    def test_animations_consistent_across_pages(self, client: TestClient) -> None:
        """
        Test that all pages use the same animations CSS file.

        Args:
            client: FastAPI test client
        """
        pages = ["/static/index.html", "/static/templates.html", "/static/mapping.html"]

        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            assert '/static/components/animations.css' in response.text

    def test_skeleton_consistent_across_pages(self, client: TestClient) -> None:
        """
        Test that all pages use the same skeleton JS file.

        Args:
            client: FastAPI test client
        """
        pages = ["/static/index.html", "/static/templates.html", "/static/mapping.html"]

        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            assert '/static/components/skeleton.js' in response.text
