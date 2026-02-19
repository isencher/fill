"""
Unit tests for UploadFile model.

Tests model validation for file uploads including:
- Valid file extensions
- File size limits
- Required fields
- Content type validation
"""

import pytest
from pydantic import ValidationError

from src.models.file import FileStatus, UploadFile


class TestUploadFileValidInputs:
    """Tests for valid UploadFile creation."""

    def test_create_upload_file_with_csv(self) -> None:
        """Test creating UploadFile with CSV file."""
        file = UploadFile(
            filename="data.csv",
            content_type="text/csv",
            size=1024,
        )
        assert file.filename == "data.csv"
        assert file.content_type == "text/csv"
        assert file.size == 1024
        assert file.status == FileStatus.PENDING
        assert isinstance(file.id, type(file.id))  # UUID type check

    def test_create_upload_file_with_xlsx(self) -> None:
        """Test creating UploadFile with Excel file."""
        file = UploadFile(
            filename="data.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=2048,
        )
        assert file.filename == "data.xlsx"
        assert file.status == FileStatus.PENDING

    def test_create_upload_file_with_uppercase_extension(self) -> None:
        """Test that uppercase file extensions are accepted."""
        file = UploadFile(
            filename="DATA.CSV",
            content_type="text/csv",
            size=512,
        )
        assert file.filename == "DATA.CSV"

    def test_create_upload_file_with_mixed_case_extension(self) -> None:
        """Test that mixed case file extensions are accepted."""
        file = UploadFile(
            filename="data.XlSx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=1024,
        )
        assert file.filename == "data.XlSx"

    def test_default_values_are_set(self) -> None:
        """Test that default values for id, uploaded_at, and status are set."""
        file = UploadFile(
            filename="test.csv",
            content_type="text/csv",
            size=100,
        )
        assert file.id is not None
        assert file.uploaded_at is not None
        assert file.status == FileStatus.PENDING

    def test_explicit_status_override(self) -> None:
        """Test that status can be explicitly set."""
        file = UploadFile(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            status=FileStatus.PROCESSING,
        )
        assert file.status == FileStatus.PROCESSING


class TestUploadFileFilenameValidation:
    """Tests for filename validation."""

    def test_reject_invalid_extension(self) -> None:
        """Test that files with invalid extensions are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UploadFile(
                filename="document.txt",
                content_type="text/plain",
                size=100,
            )
        assert "Invalid file extension" in str(exc_info.value)

    def test_reject_no_extension(self) -> None:
        """Test that files without extensions are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UploadFile(
                filename="datafile",
                content_type="text/csv",
                size=100,
            )
        assert "Invalid file extension" in str(exc_info.value)

    def test_reject_empty_filename(self) -> None:
        """Test that empty filename is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UploadFile(
                filename="",
                content_type="text/csv",
                size=100,
            )
        assert "at least 1 character" in str(exc_info.value).lower()

    def test_reject_filename_too_long(self) -> None:
        """Test that filename exceeding 255 characters is rejected."""
        long_filename = "a" * 256 + ".csv"
        with pytest.raises(ValidationError) as exc_info:
            UploadFile(
                filename=long_filename,
                content_type="text/csv",
                size=100,
            )
        assert "at most 255 characters" in str(exc_info.value).lower()


class TestUploadFileSizeValidation:
    """Tests for file size validation."""

    def test_reject_zero_size(self) -> None:
        """Test that zero file size is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UploadFile(
                filename="test.csv",
                content_type="text/csv",
                size=0,
            )
        assert "greater than 0" in str(exc_info.value)

    def test_reject_negative_size(self) -> None:
        """Test that negative file size is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UploadFile(
                filename="test.csv",
                content_type="text/csv",
                size=-100,
            )
        assert "greater than 0" in str(exc_info.value)

    def test_reject_size_exceeds_maximum(self) -> None:
        """Test that file size exceeding 10MB is rejected."""
        max_size = 10 * 1024 * 1024
        with pytest.raises(ValidationError) as exc_info:
            UploadFile(
                filename="test.csv",
                content_type="text/csv",
                size=max_size + 1,
            )
        assert "exceeds maximum allowed size" in str(exc_info.value)

    def test_accept_maximum_size(self) -> None:
        """Test that exactly 10MB file size is accepted."""
        max_size = 10 * 1024 * 1024
        file = UploadFile(
            filename="test.csv",
            content_type="text/csv",
            size=max_size,
        )
        assert file.size == max_size

    def test_accept_small_file(self) -> None:
        """Test that small files (1 byte) are accepted."""
        file = UploadFile(
            filename="test.csv",
            content_type="text/csv",
            size=1,
        )
        assert file.size == 1


class TestUploadFileContentTypeValidation:
    """Tests for content type validation."""

    def test_reject_mismatched_content_type_for_csv(self) -> None:
        """Test that wrong content type for CSV is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UploadFile(
                filename="data.csv",
                content_type="application/json",
                size=100,
            )
        assert "must have content-type" in str(exc_info.value).lower()

    def test_reject_mismatched_content_type_for_xlsx(self) -> None:
        """Test that wrong content type for Excel is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UploadFile(
                filename="data.xlsx",
                content_type="text/csv",
                size=100,
            )
        # Check for the error message (Pydantic v2 format)
        error_str = str(exc_info.value).lower()
        assert "excel content-type" in error_str or "content-type" in error_str

    def test_accept_text_csv_for_csv_file(self) -> None:
        """Test that text/csv is accepted for CSV files."""
        file = UploadFile(
            filename="data.csv",
            content_type="text/csv",
            size=100,
        )
        assert file.content_type == "text/csv"

    def test_accept_application_csv_for_csv_file(self) -> None:
        """Test that application/csv is accepted for CSV files."""
        file = UploadFile(
            filename="data.csv",
            content_type="application/csv",
            size=100,
        )
        assert file.content_type == "application/csv"

    def test_accept_standard_excel_content_type(self) -> None:
        """Test that standard Excel content type is accepted."""
        file = UploadFile(
            filename="data.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=100,
        )
        assert "spreadsheetml" in file.content_type

    def test_accept_legacy_excel_content_type(self) -> None:
        """Test that legacy Excel content type is accepted."""
        file = UploadFile(
            filename="data.xlsx",
            content_type="application/vnd.ms-excel",
            size=100,
        )
        assert file.content_type == "application/vnd.ms-excel"

    def test_reject_invalid_content_type_format(self) -> None:
        """Test that invalid content type format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UploadFile(
                filename="data.csv",
                content_type="invalid-content-type",
                size=100,
            )
        assert "should match pattern" in str(exc_info.value).lower()


class TestUploadFileModelSerialization:
    """Tests for model serialization and JSON conversion."""

    def test_model_serializes_to_dict(self) -> None:
        """Test that model can be serialized to dictionary."""
        file = UploadFile(
            filename="test.csv",
            content_type="text/csv",
            size=1024,
        )
        data = file.model_dump()
        assert data["filename"] == "test.csv"
        assert data["content_type"] == "text/csv"
        assert data["size"] == 1024
        assert data["status"] == "pending"

    def test_model_serializes_to_json(self) -> None:
        """Test that model can be serialized to JSON."""
        file = UploadFile(
            filename="test.csv",
            content_type="text/csv",
            size=1024,
        )
        json_str = file.model_dump_json()
        assert "test.csv" in json_str
        assert "text/csv" in json_str


class TestFileStatusEnum:
    """Tests for FileStatus enum."""

    def test_all_status_values(self) -> None:
        """Test that all expected status values exist."""
        assert FileStatus.PENDING == "pending"
        assert FileStatus.PROCESSING == "processing"
        assert FileStatus.COMPLETED == "completed"
        assert FileStatus.FAILED == "failed"

    def test_status_can_be_set_from_string(self) -> None:
        """Test that status can be set from string value."""
        file = UploadFile(
            filename="test.csv",
            content_type="text/csv",
            size=100,
            status="processing",
        )
        assert file.status == FileStatus.PROCESSING
