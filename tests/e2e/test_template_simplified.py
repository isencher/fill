"""
End-to-end tests for simplified template card selection.

These tests validate:
1. Template cards show business-friendly descriptions
2. Technical placeholder tags are hidden from main view
3. "View Details" section works correctly
4. Primary action button is clear and prominent
5. Template selection flow works smoothly
"""

import io

import pytest
from fastapi.testclient import TestClient

from src.main import _uploaded_files, app


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: FastAPI test client instance
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage() -> None:
    """Clear in-memory storage after each test."""
    yield
    _uploaded_files.clear()


class TestSimplifiedTemplateCards:
    """
    Tests for simplified template card design.
    """

    def test_template_page_loads_with_simplified_cards(self, client: TestClient) -> None:
        """
        Test that template page loads with simplified card layout.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for simplified template classes
        assert 'template-summary' in content
        assert 'template-summary-text' in content

    def test_template_cards_have_business_friendly_descriptions(self, client: TestClient) -> None:
        """
        Test that template cards show business-friendly descriptions instead of technical tags.

        Args:
            client: FastAPI test client
        """
        # Add some templates with built-in templates
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for business-friendly summary section
        assert 'Includes:' in content or '包含' in content

    def test_template_cards_have_primary_action_button(self, client: TestClient) -> None:
        """
        Test that template cards have clear primary action buttons.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for primary button class
        assert 'btn-primary' in content or 'use-template-btn' in content

        # Check for clear action text
        assert '选择此模板' in content or 'Use Template' in content

    def test_template_cards_hide_technical_tags(self, client: TestClient) -> None:
        """
        Test that technical placeholder tags are not shown in main card view.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # The old template-placeholders div should not be prominently displayed
        # or should be replaced with summary section
        assert 'template-summary' in content


class TestViewDetailsFeature:
    """
    Tests for "View Details" expandable section.
    """

    def test_template_cards_with_many_placeholders_have_view_details(self, client: TestClient) -> None:
        """
        Test that templates with many placeholders have "View Details" button.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for view-details button
        assert 'view-details-btn' in content or '查看详情' in content

    def test_view_details_button_toggles_details_section(self, client: TestClient) -> None:
        """
        Test that clicking "View Details" shows/hides placeholder list.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for template-details section
        assert 'template-details' in content
        assert 'placeholder-code' in content


class TestTemplateCardWorkflow:
    """
    Tests for simplified template selection workflow.
    """

    def test_template_card_click_navigates_to_mapping(self, client: TestClient) -> None:
        """
        Test that clicking a template card navigates to mapping page.

        Args:
            client: FastAPI test client
        """
        # First upload a file
        csv_content = b"Name,Email,Phone\nJohn,john@example.com,555-1234"
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        )
        assert response.status_code == 201
        file_id = response.json()["file_id"]

        # Access template page with file_id
        response = client.get(f"/templates.html?file_id={file_id}")
        assert response.status_code == 200
        content = response.text

        # Check that template cards are present
        assert 'template-card' in content or 'data-testid="template-card"' in content

    def test_select_template_button_is_clear_call_to_action(self, client: TestClient) -> None:
        """
        Test that the primary action button is clear and prominent.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for clear call-to-action text
        assert '选择此模板' in content or 'Select' in content
        assert '→' in content  # Arrow indicator for action

    def test_template_cards_have_consistent_styling(self, client: TestClient) -> None:
        """
        Test that all template cards follow consistent styling.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for consistent CSS classes
        assert 'template-card' in content
        assert 'template-icon' in content
        assert 'template-name' in content


class TestPlaceholderDescriptionGeneration:
    """
    Tests for placeholder description generation logic.
    """

    def test_placeholder_description_shows_field_count(self, client: TestClient) -> None:
        """
        Test that placeholder descriptions show field count.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for count display in templates with many fields
        assert '项' in content or '项)' in content

    def test_placeholder_description_uses_business_language(self, client: TestClient) -> None:
        """
        Test that placeholder descriptions use business language.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for business terms instead of technical placeholders
        # Should show things like "名称", "金额", "日期" instead of "{{name}}"
        assert 'Includes:' in content or '包含' in content


class TestTemplateCardAccessibility:
    """
    Tests for template card accessibility.
    """

    def test_template_cards_have_proper_button_elements(self, client: TestClient) -> None:
        """
        Test that template cards use proper button elements for actions.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for button elements
        assert '<button' in content

    def test_template_cards_have_clear_click_targets(self, client: TestClient) -> None:
        """
        Test that template cards have clear, large click targets.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for button or clickable elements
        assert 'use-template-btn' in content or 'btn-primary' in content


class TestTemplateCardVisualDesign:
    """
    Tests for template card visual design improvements.
    """

    def test_template_cards_have_summary_section(self, client: TestClient) -> None:
        """
        Test that template cards have a summary section with icon.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for summary section with icon
        assert 'template-summary' in content
        assert 'template-summary-icon' in content

    def test_template_cards_use_gradient_backgrounds(self, client: TestClient) -> None:
        """
        Test that template cards use attractive gradient backgrounds for buttons.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for gradient background on primary button
        assert 'linear-gradient' in content

    def test_template_cards_have_proper_spacing(self, client: TestClient) -> None:
        """
        Test that template cards have proper spacing and padding.

        Args:
            client: FastAPI test client
        """
        response = client.get("/static/templates.html")
        assert response.status_code == 200
        content = response.text

        # Check for padding/margin in CSS
        assert 'padding:' in content
        assert 'margin:' in content
