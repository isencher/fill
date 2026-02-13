"""Unit tests for UploadFile model.

This module tests the file upload model including:
- Valid file extensions (xlsx, csv)
- File size limits (10MB)
- Required fields
- Model validation

Following TDD: Red -> Green -> Refactor
"""

import pytest

from src.models.file import UploadFile, FileValidationError, MAX_FILE_SIZE_BYTES, ALLOWED_EXTENSIONS


class TestUploadFileModel:
    """Test suite for UploadFile model validation."""

    def test_upload_file_with_valid_xlsx_extension(self) -> None:
        """Test creating UploadFile with valid .xlsx extension.

        Acceptance: Model accepts valid Excel file extension.
        """
        file_data = UploadFile(
            filename="test_data.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=1024,
        )
        assert file_data.filename == "test_data.xlsx"
        assert file_data.status == "pending"

    def test_upload_file_with_valid_csv_extension(self) -> None:
        """Test creating UploadFile with valid .csv extension.

        Acceptance: Model accepts valid CSV file extension.
        """
        file_data = UploadFile(
            filename="test_data.csv",
            content_type="text/csv",
            size=512,
        )
        assert file_data.filename == "test_data.csv"
        assert file_data.status == "pending"

    def test_upload_file_rejects_invalid_extension(self) -> None:
        """Test creating UploadFile with invalid file extension.

        Acceptance: Model rejects non-Excel/CSV files (e.g., .txt, .pdf).
        """
        with pytest.raises(FileValidationError) as exc_info:
            UploadFile(
                filename="document.pdf",
                content_type="application/pdf",
                size=1024,
            )
        assert "Invalid file extension" in str(exc_info.value)

    def test_upload_file_rejects_xlsx_but_with_wrong_case(self) -> None:
        """Test that file extension validation is case-insensitive.

        Acceptance: Model accepts .XLSX, .Xlsx, etc.
        """
        # Should work - case insensitive
        file_data = UploadFile(
            filename="DATA.XLSX",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=1024,
        )
        assert file_data.filename == "DATA.XLSX"

        file_data2 = UploadFile(
            filename="data.Xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=1024,
        )
        assert file_data2.filename == "data.Xlsx"

    def test_upload_file_rejects_oversized_file(self) -> None:
        """Test creating UploadFile exceeding size limit.

        Acceptance: Model rejects files larger than 10MB.
        """
        with pytest.raises(FileValidationError) as exc_info:
            UploadFile(
                filename="large_file.xlsx",
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                size=MAX_FILE_SIZE_BYTES + 1,
            )
        assert "File size exceeds" in str(exc_info.value)

    def test_upload_file_accepts_exactly_max_size(self) -> None:
        """Test creating UploadFile at exactly the size limit.

        Acceptance: Model accepts files at exactly 10MB limit.
        """
        file_data = UploadFile(
            filename="max_size.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=MAX_FILE_SIZE_BYTES,
        )
        assert file_data.size == MAX_FILE_SIZE_BYTES

    def test_upload_file_rejects_zero_size_file(self) -> None:
        """Test creating UploadFile with zero size.

        Acceptance: Model rejects empty files.
        """
        with pytest.raises(FileValidationError) as exc_info:
            UploadFile(
                filename="empty.xlsx",
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                size=0,
            )
        assert "File size must be greater than zero" in str(exc_info.value)

    def test_upload_file_rejects_negative_size_file(self) -> None:
        """Test creating UploadFile with negative size.

        Acceptance: Model rejects negative file sizes.
        """
        with pytest.raises(FileValidationError) as exc_info:
            UploadFile(
                filename="negative.xlsx",
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                size=-100,
            )
        assert "File size must be greater than zero" in str(exc_info.value)

    def test_upload_file_requires_filename(self) -> None:
        """Test that filename is a required field.

        Acceptance: Model validation fails without filename.
        """
        with pytest.raises(FileValidationError):
            UploadFile(
                filename="",  # Empty filename
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                size=1024,
            )

    def test_upload_file_rejects_filename_without_extension(self) -> None:
        """Test creating UploadFile with filename that has no extension.

        Acceptance: Model rejects filenames without extensions (e.g., "file" with no dot).
        """
        with pytest.raises(FileValidationError) as exc_info:
            UploadFile(
                filename="noextension",
                content_type="application/octet-stream",
                size=1024,
            )
        assert "Invalid file extension" in str(exc_info.value)

    def test_upload_file_has_unique_id(self) -> None:
        """Test that each UploadFile instance gets a unique ID.

        Acceptance: Each file gets a unique identifier.
        """
        file1 = UploadFile(
            filename="file1.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=1024,
        )
        file2 = UploadFile(
            filename="file2.csv",
            content_type="text/csv",
            size=512,
        )
        assert file1.id != file2.id
        assert isinstance(file1.id, str)
        assert len(file1.id) > 0

    def test_upload_file_has_uploaded_at_timestamp(self) -> None:
        """Test that UploadFile has uploaded_at timestamp.

        Acceptance: Model records upload time.
        """
        import time

        before = time.time()
        file_data = UploadFile(
            filename="timestamp_test.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=1024,
        )
        after = time.time()

        assert file_data.uploaded_at is not None
        assert before <= file_data.uploaded_at <= after

    def test_upload_file_default_status_is_pending(self) -> None:
        """Test that default status is 'pending'.

        Acceptance: New files have pending status by default.
        """
        file_data = UploadFile(
            filename="status_test.csv",
            content_type="text/csv",
            size=1024,
        )
        assert file_data.status == "pending"

    def test_upload_file_status_can_be_changed(self) -> None:
        """Test that file status can be updated.

        Acceptance: File status can be changed to 'processing', 'completed', etc.
        """
        file_data = UploadFile(
            filename="status_change.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size=1024,
        )
        assert file_data.status == "pending"

        file_data.status = "processing"
        assert file_data.status == "processing"

        file_data.status = "completed"
        assert file_data.status == "completed"

    def test_allowed_extensions_constant(self) -> None:
        """Test that ALLOWED_EXTENSIONS contains expected values.

        Acceptance: Configuration includes xlsx and csv extensions.
        """
        assert "xlsx" in ALLOWED_EXTENSIONS
        assert "csv" in ALLOWED_EXTENSIONS
        assert isinstance(ALLOWED_EXTENSIONS, (list, set, tuple))

    def test_max_file_size_constant(self) -> None:
        """Test that MAX_FILE_SIZE_BYTES is correctly defined.

        Acceptance: Size limit is 10MB (10 * 1024 * 1024 bytes).
        """
        expected_max = 10 * 1024 * 1024  # 10MB
        assert MAX_FILE_SIZE_BYTES == expected_max
