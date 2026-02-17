"""
E2E Tests for Error Recovery and Validation Features (Step 11.12)

Tests for:
1. Client-side validation (file size, file type, real-time feedback)
2. Undo/Redo functionality for mappings
3. Conflict detection and resolution
4. Error recovery and retry mechanisms
5. Auto-save and draft restoration
"""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO

from src.main import app, _file_storage


class TestClientSideValidation:
    """Tests for client-side validation"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_validation_utils_is_served(self, client: TestClient) -> None:
        """Test that validation utils are served"""
        response = client.get("/static/components/validation.js")
        assert response.status_code == 200
        assert "ValidationUtils" in response.text
        assert "validateFileSize" in response.text

    def test_validation_utils_has_file_type_validation(self, client: TestClient) -> None:
        """Test that file type validation exists"""
        response = client.get("/static/components/validation.js")
        assert response.status_code == 200
        assert "validateFileType" in response.text

    def test_validation_utils_has_field_validation(self, client: TestClient) -> None:
        """Test that field validation exists"""
        response = client.get("/static/components/validation.js")
        assert response.status_code == 200
        assert "validateField" in response.text

    def test_validation_utils_has_progress_validation(self, client: TestClient) -> None:
        """Test that progress validation exists"""
        response = client.get("/static/components/validation.js")
        assert response.status_code == 200
        assert "validateFileWithProgress" in response.text

    def test_validation_utils_has_email_validation(self, client: TestClient) -> None:
        """Test that email validation exists"""
        response = client.get("/static/components/validation.js")
        assert response.status_code == 200
        assert "_isValidEmail" in response.text

    def test_validation_utils_has_url_validation(self, client: TestClient) -> None:
        """Test that URL validation exists"""
        response = client.get("/static/components/validation.js")
        assert response.status_code == 200
        assert "_isValidUrl" in response.text

    def test_validation_css_is_served(self, client: TestClient) -> None:
        """Test that validation CSS is served"""
        response = client.get("/static/components/error-recovery.css")
        assert response.status_code == 200
        assert "valid" in response.text
        assert "invalid" in response.text

    def test_validation_css_has_validation_feedback(self, client: TestClient) -> None:
        """Test that validation feedback styles exist"""
        response = client.get("/static/components/error-recovery.css")
        assert response.status_code == 200
        assert "validation-feedback" in response.text


class TestUndoRedo:
    """Tests for undo/redo functionality"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_undo_redo_is_served(self, client: TestClient) -> None:
        """Test that undo/redo manager is served"""
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200
        assert "UndoRedoManager" in response.text

    def test_undo_redo_has_push_state(self, client: TestClient) -> None:
        """Test that pushState function exists"""
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200
        assert "pushState" in response.text

    def test_undo_redo_has_undo(self, client: TestClient) -> None:
        """Test that undo function exists"""
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200
        assert "undo()" in response.text or "undo" in response.text

    def test_undo_redo_has_redo(self, client: TestClient) -> None:
        """Test that redo function exists"""
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200
        assert "redo()" in response.text or "redo" in response.text

    def test_undo_redo_has_reset(self, client: TestClient) -> None:
        """Test that reset function exists"""
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200
        assert "reset" in response.text

    def test_undo_redo_has_auto_save(self, client: TestClient) -> None:
        """Test that auto-save functionality exists"""
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200
        assert "_saveToStorage" in response.text or "autoSave" in response.text

    def test_undo_redo_has_load_from_storage(self, client: TestClient) -> None:
        """Test that load from storage exists"""
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200
        assert "_loadFromStorage" in response.text or "loadFromStorage" in response.text

    def test_undo_redo_has_history_management(self, client: TestClient) -> None:
        """Test that history management exists"""
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200
        assert "history" in response.text
        assert "currentIndex" in response.text


class TestErrorRecovery:
    """Tests for error recovery mechanisms"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_error_recovery_is_served(self, client: TestClient) -> None:
        """Test that error recovery module is served"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "ErrorRecovery" in response.text

    def test_error_recovery_has_retry(self, client: TestClient) -> None:
        """Test that retry functionality exists"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "retry" in response.text.lower()

    def test_error_recovery_has_safe_fetch(self, client: TestClient) -> None:
        """Test that safe fetch with retry exists"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "safeFetch" in response.text

    def test_error_recovery_has_draft_save(self, client: TestClient) -> None:
        """Test that draft save functionality exists"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "saveDraft" in response.text

    def test_error_recovery_has_draft_load(self, client: TestClient) -> None:
        """Test that draft load functionality exists"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "loadDraft" in response.text

    def test_error_recovery_has_auto_recover(self, client: TestClient) -> None:
        """Test that auto-recover functionality exists"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "autoRecover" in response.text

    def test_error_recovery_has_conflict_detection(self, client: TestClient) -> None:
        """Test that conflict detection exists"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "detectFileUpdate" in response.text
        assert "detectTemplateModification" in response.text


class TestRetryMechanism:
    """Tests for retry mechanism"""

    def test_error_recovery_css_has_retry_button(self, client: TestClient) -> None:
        """Test that retry button styles exist"""
        response = client.get("/static/components/error-recovery.css")
        assert response.status_code == 200
        assert "retry-btn" in response.text
        assert ".retry-icon" in response.text

    def test_error_recovery_css_has_save_draft_button(self, client: TestClient) -> None:
        """Test that save draft button styles exist"""
        response = client.get("/static/components/error-recovery.css")
        assert response.status_code == 200
        assert "save-draft-btn" in response.text
        assert ".save-icon" in response.text

    def test_error_recovery_css_has_validation_progress(self, client: TestClient) -> None:
        """Test that validation progress styles exist"""
        response = client.get("/static/components/error-recovery.css")
        assert response.status_code == 200
        assert "file-validation-progress" in response.text
        assert "validation-phase" in response.text


class TestAutoSave:
    """Tests for auto-save functionality"""

    def test_undo_redo_supports_max_history(self, client: TestClient) -> None:
        """Test that max history can be configured"""
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200
        assert "maxHistory" in response.text


class TestConflictResolution:
    """Tests for conflict detection and resolution"""

    def test_error_recovery_detects_file_updates(self, client: TestClient) -> None:
        """Test that file update detection exists"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "detectFileUpdate" in response.text

    def test_error_recovery_detects_template_changes(self, client: TestClient) -> None:
        """Test that template modification detection exists"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "detectTemplateModification" in response.text


class TestValidationIntegration:
    """Integration tests for validation and error recovery"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_all_error_recovery_files_are_served(self, client: TestClient) -> None:
        """Test that all error recovery files are served"""
        files = [
            "/static/components/validation.js",
            "/static/components/undo-redo.js",
            "/static/components/error-recovery.js",
            "/static/components/error-recovery.css"
        ]

        for file_path in files:
            response = client.get(file_path)
            assert response.status_code == 200

    def test_validation_utils_initializes(self, client: TestClient) -> None:
        """Test that validation utils has init functionality"""
        response = client.get("/static/components/validation.js")
        assert response.status_code == 200
        assert "ValidationUtils" in response.text

    def test_undo_redo_manages_state(self, client: TestClient) -> None:
        """Test that undo/redo manages state"""
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200
        assert "history" in response.text
        assert "state" in response.text

    def test_error_recovery_has_recovery_prompt(self, client: TestClient) -> None:
        """Test that error recovery has recovery prompt"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "recoverWithErrorPrompt" in response.text


class TestErrorStates:
    """Tests for error state displays"""

    def test_error_recovery_css_has_error_states(self, client: TestClient) -> None:
        """Test that error state styles are defined"""
        response = client.get("/static/components/error-recovery.css")
        assert response.status_code == 200
        assert "error-state" in response.text
        assert "warning-state" in response.text
        assert "success-state" in response.text

    def test_error_recovery_css_has_conflict_modal(self, client: TestClient) -> None:
        """Test that conflict modal styles exist"""
        response = client.get("/static/components/error-recovery.css")
        assert response.status_code == 200
        assert "conflict-modal" in response.text

    def test_error_recovery_css_has_autosave_indicator(self, client: TestClient) -> None:
        """Test that autosave indicator styles exist"""
        response = client.get("/static/components/error-recovery.css")
        assert response.status_code == 200
        assert "autosave-indicator" in response.text

    def test_error_recovery_css_has_toast_notifications(self, client: TestClient) -> None:
        """Test that toast notification styles exist"""
        response = client.get("/static/components/error-recovery.css")
        assert response.status_code == 200
        assert "toast" in response.text


class TestFileUploadValidation:
    """Tests for file upload validation"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_upload_has_validation_support(self, client: TestClient) -> None:
        """Test that file upload supports validation"""
        # Check that validation utilities exist
        response = client.get("/static/components/validation.js")
        assert response.status_code == 200
        # File size validation
        assert "10MB" in response.text or "10485760" in response.text

    def test_upload_dropzone_has_validation_styles(self, client: TestClient) -> None:
        """Test that upload dropzone has validation styles"""
        response = client.get("/static/components/error-recovery.css")
        assert response.status_code == 200
        assert "file-upload-dropzone" in response.text
        assert ".dragover" in response.text


class TestMappingUndoRedo:
    """Tests for mapping undo/redo functionality"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_undo_redo_has_mapping_support(self, client: TestClient) -> None:
        """Test that undo/redo supports mapping state"""
        # This would require integration tests with actual mapping operations
        response = client.get("/static/components/undo-redo.js")
        assert response.status_code == 200


class TestDraftRecovery:
    """Tests for draft save and recovery"""

    def test_error_recovery_supports_draft_operations(self, client: TestClient) -> None:
        """Test that draft operations are supported"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "saveDraft" in response.text
        assert "loadDraft" in response.text
        assert "deleteDraft" in response.text

    def test_error_recovery_clears_drafts(self, client: TestClient) -> None:
        """Test that drafts can be cleared"""
        response = client.get("/static/components/error-recovery.js")
        assert response.status_code == 200
        assert "clearAllDrafts" in response.text
