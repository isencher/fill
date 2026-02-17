"""
Unit tests for Job Model.

Tests batch job model for tracking fill operations.
"""

from datetime import datetime
from uuid import UUID

import pytest

from src.models.job import Job, JobStatus


class TestJobCreation:
    """Test Job model initialization and basic functionality."""

    def test_create_job_with_required_fields(self):
        """Test creating job with minimum required fields."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        assert job.file_id == "file-123"
        assert job.template_id == "template-456"
        assert job.mapping_id == "mapping-789"
        assert job.total_rows == 100
        assert job.status == JobStatus.PENDING
        assert job.processed_rows == 0
        assert job.failed_rows == 0
        assert job.error_message is None
        assert isinstance(job.id, UUID)
        assert isinstance(job.created_at, datetime)
        assert isinstance(job.updated_at, datetime)

    def test_create_job_with_all_fields(self):
        """Test creating job with all fields specified."""
        now = datetime.utcnow()
        status = JobStatus.PROCESSING

        job = Job(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            status=status,
            total_rows=100,
            processed_rows=50,
            failed_rows=2,
            created_at=now,
            updated_at=now,
            error_message="Test error",
        )

        assert str(job.id) == "12345678-1234-5678-1234-567812345678"
        assert job.status == JobStatus.PROCESSING
        assert job.processed_rows == 50
        assert job.failed_rows == 2
        assert job.error_message == "Test error"

    def test_job_auto_generates_id(self):
        """Test that job IDs are auto-generated and unique."""
        job1 = Job(
            file_id="file-1", template_id="template-1", mapping_id="mapping-1", total_rows=10
        )
        job2 = Job(
            file_id="file-2", template_id="template-2", mapping_id="mapping-2", total_rows=20
        )

        assert job1.id != job2.id
        assert isinstance(job1.id, UUID)
        assert isinstance(job2.id, UUID)

    def test_job_auto_generates_timestamps(self):
        """Test that timestamps are auto-generated."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        assert isinstance(job.created_at, datetime)
        assert isinstance(job.updated_at, datetime)
        # Timestamps should be very recent
        delta = datetime.utcnow() - job.created_at
        assert delta.total_seconds() < 5


class TestJobStatusEnum:
    """Test JobStatus enum values."""

    def test_status_values(self):
        """Test all status enum values."""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.PROCESSING.value == "processing"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"

    def test_status_comparison(self):
        """Test status comparison."""
        job1 = Job(
            file_id="file-1",
            template_id="template-1",
            mapping_id="mapping-1",
            total_rows=10,
            status=JobStatus.PROCESSING,
        )
        job2 = Job(
            file_id="file-2",
            template_id="template-2",
            mapping_id="mapping-2",
            total_rows=10,
            status=JobStatus.PROCESSING,
        )

        assert job1.status == job2.status
        assert job1.status == JobStatus.PROCESSING


class TestJobFieldValidation:
    """Test field validation in Job model."""

    def test_file_id_validation_empty(self):
        """Test that empty file_id raises error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            Job(
                file_id="",
                template_id="template-456",
                mapping_id="mapping-789",
                total_rows=100,
            )

    def test_file_id_validation_whitespace(self):
        """Test that whitespace-only file_id raises error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            Job(
                file_id="   ",
                template_id="template-456",
                mapping_id="mapping-789",
                total_rows=100,
            )

    def test_file_id_trimming(self):
        """Test that file_id is trimmed."""
        job = Job(
            file_id="  file-123  ",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        assert job.file_id == "file-123"

    def test_template_id_validation_empty(self):
        """Test that empty template_id raises error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            Job(
                file_id="file-123",
                template_id="",
                mapping_id="mapping-789",
                total_rows=100,
            )

    def test_template_id_trimming(self):
        """Test that template_id is trimmed."""
        job = Job(
            file_id="file-123",
            template_id="  template-456  ",
            mapping_id="mapping-789",
            total_rows=100,
        )

        assert job.template_id == "template-456"

    def test_mapping_id_validation_empty(self):
        """Test that empty mapping_id raises error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            Job(
                file_id="file-123",
                template_id="template-456",
                mapping_id="",
                total_rows=100,
            )

    def test_mapping_id_trimming(self):
        """Test that mapping_id is trimmed."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="  mapping-789  ",
            total_rows=100,
        )

        assert job.mapping_id == "mapping-789"

    def test_total_rows_negative(self):
        """Test that negative total_rows raises error."""
        with pytest.raises(ValueError):  # Pydantic validation error
            Job(
                file_id="file-123",
                template_id="template-456",
                mapping_id="mapping-789",
                total_rows=-1,
            )

    def test_total_rows_zero(self):
        """Test that zero total_rows is allowed."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=0,
        )

        assert job.total_rows == 0

    def test_processed_rows_default(self):
        """Test that processed_rows defaults to 0."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        assert job.processed_rows == 0

    def test_processed_rows_negative(self):
        """Test that negative processed_rows raises error."""
        with pytest.raises(ValueError):  # Pydantic validation error
            Job(
                file_id="file-123",
                template_id="template-456",
                mapping_id="mapping-789",
                total_rows=100,
                processed_rows=-1,
            )

    def test_failed_rows_default(self):
        """Test that failed_rows defaults to 0."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        assert job.failed_rows == 0

    def test_failed_rows_negative(self):
        """Test that negative failed_rows raises error."""
        with pytest.raises(ValueError):  # Pydantic validation error
            Job(
                file_id="file-123",
                template_id="template-456",
                mapping_id="mapping-789",
                total_rows=100,
                failed_rows=-1,
            )

    def test_error_message_default(self):
        """Test that error_message defaults to None."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        assert job.error_message is None

    def test_error_message_empty_string_becomes_none(self):
        """Test that empty string error_message becomes None."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            error_message="",
        )

        assert job.error_message is None

    def test_error_message_whitespace_becomes_none(self):
        """Test that whitespace-only error_message becomes None."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            error_message="   ",
        )

        assert job.error_message is None

    def test_error_message_trimming(self):
        """Test that error_message is trimmed."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            error_message="  Test error  ",
        )

        assert job.error_message == "Test error"


class TestJobProperties:
    """Test Job model properties."""

    def test_progress_percentage_zero_total(self):
        """Test progress_percentage when total_rows is 0."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=0,
            processed_rows=0,
        )

        assert job.progress_percentage == 0.0

    def test_progress_percentage_no_progress(self):
        """Test progress_percentage when no rows processed."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            processed_rows=0,
        )

        assert job.progress_percentage == 0.0

    def test_progress_percentage_half_complete(self):
        """Test progress_percentage at 50%."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            processed_rows=50,
        )

        assert job.progress_percentage == 50.0

    def test_progress_percentage_fully_complete(self):
        """Test progress_percentage at 100%."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            processed_rows=100,
        )

        assert job.progress_percentage == 100.0

    def test_progress_percentage_partial(self):
        """Test progress_percentage with partial progress."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=7,
            processed_rows=3,
        )

        assert job.progress_percentage == pytest.approx(42.857, rel=1e-3)

    def test_is_complete_pending(self):
        """Test is_complete property for pending job."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            status=JobStatus.PENDING,
        )

        assert not job.is_complete

    def test_is_complete_processing(self):
        """Test is_complete property for processing job."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            status=JobStatus.PROCESSING,
        )

        assert not job.is_complete

    def test_is_complete_completed(self):
        """Test is_complete property for completed job."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            status=JobStatus.COMPLETED,
        )

        assert job.is_complete

    def test_is_complete_failed(self):
        """Test is_complete property for failed job."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            status=JobStatus.FAILED,
        )

        assert job.is_complete

    def test_is_running_pending(self):
        """Test is_running property for pending job."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            status=JobStatus.PENDING,
        )

        assert not job.is_running

    def test_is_running_processing(self):
        """Test is_running property for processing job."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            status=JobStatus.PROCESSING,
        )

        assert job.is_running

    def test_is_running_completed(self):
        """Test is_running property for completed job."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            status=JobStatus.COMPLETED,
        )

        assert not job.is_running


class TestJobMethods:
    """Test Job model methods."""

    def test_increment_processed_default(self):
        """Test increment_processed with default count."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        initial_processed = job.processed_rows
        job.increment_processed()

        assert job.processed_rows == initial_processed + 1
        assert job.updated_at > job.created_at

    def test_increment_processed_custom_count(self):
        """Test increment_processed with custom count."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        job.increment_processed(5)

        assert job.processed_rows == 5

    def test_increment_processed_negative_count(self):
        """Test that negative increment_processed raises error."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        with pytest.raises(ValueError, match="Count cannot be negative"):
            job.increment_processed(-1)

    def test_increment_failed_default(self):
        """Test increment_failed with default count."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        initial_failed = job.failed_rows
        job.increment_failed()

        assert job.failed_rows == initial_failed + 1
        assert job.updated_at > job.created_at

    def test_increment_failed_custom_count(self):
        """Test increment_failed with custom count."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        job.increment_failed(3)

        assert job.failed_rows == 3

    def test_increment_failed_negative_count(self):
        """Test that negative increment_failed raises error."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        with pytest.raises(ValueError, match="Count cannot be negative"):
            job.increment_failed(-1)

    def test_set_status_with_enum(self):
        """Test set_status with JobStatus enum."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        job.set_status(JobStatus.PROCESSING)

        assert job.status == JobStatus.PROCESSING
        assert job.updated_at > job.created_at

    def test_set_status_with_string(self):
        """Test set_status with string value."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        job.set_status("processing")

        assert job.status == JobStatus.PROCESSING
        assert job.updated_at > job.created_at

    def test_set_status_uppercase_string(self):
        """Test set_status with uppercase string value."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        job.set_status("COMPLETED")

        assert job.status == JobStatus.COMPLETED

    def test_set_error(self):
        """Test set_error method."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            status=JobStatus.PROCESSING,
        )

        job.set_error("Template file not found")

        assert job.status == JobStatus.FAILED
        assert job.error_message == "Template file not found"
        assert job.updated_at > job.created_at

    def test_set_error_trims_message(self):
        """Test that set_error trims whitespace."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        job.set_error("  Error message  ")

        assert job.error_message == "Error message"


class TestJobSerialization:
    """Test Job model serialization."""

    def test_model_dump(self):
        """Test model_dump method."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
            processed_rows=50,
            status=JobStatus.PROCESSING,
        )

        data = job.model_dump()

        assert data["file_id"] == "file-123"
        assert data["template_id"] == "template-456"
        assert data["mapping_id"] == "mapping-789"
        assert data["total_rows"] == 100
        assert data["processed_rows"] == 50
        assert data["status"] == "processing"

    def test_model_dump_json(self):
        """Test model_dump_json method."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        json_str = job.model_dump_json()

        assert '"file_id":"file-123"' in json_str
        assert '"template_id":"template-456"' in json_str
        assert '"total_rows":100' in json_str

    def test_model_validate_json(self):
        """Test model_validate_json method."""
        json_str = '''
        {
            "file_id": "file-123",
            "template_id": "template-456",
            "mapping_id": "mapping-789",
            "total_rows": 100,
            "processed_rows": 50,
            "status": "processing"
        }
        '''

        job = Job.model_validate_json(json_str)

        assert job.file_id == "file-123"
        assert job.template_id == "template-456"
        assert job.status == JobStatus.PROCESSING
        assert job.processed_rows == 50


class TestJobEdgeCases:
    """Test edge cases and special scenarios."""

    def test_large_total_rows(self):
        """Test job with very large total_rows."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=1_000_000,
        )

        assert job.total_rows == 1_000_000
        assert job.progress_percentage == 0.0

    def test_unicode_in_ids(self):
        """Test job with Unicode characters in IDs."""
        job = Job(
            file_id="文件-123",
            template_id="模板-456",
            mapping_id="映射-789",
            total_rows=100,
        )

        assert job.file_id == "文件-123"
        assert job.template_id == "模板-456"
        assert job.mapping_id == "映射-789"

    def test_long_error_message(self):
        """Test job with long error message."""
        long_message = "Error: " + "x" * 1000
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        job.set_error(long_message)

        assert job.error_message == long_message
        assert len(job.error_message) > 1000

    def test_multiple_status_updates(self):
        """Test multiple status updates."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        # PENDING -> PROCESSING
        job.set_status(JobStatus.PROCESSING)
        assert job.status == JobStatus.PROCESSING

        # PROCESSING -> COMPLETED
        job.set_status(JobStatus.COMPLETED)
        assert job.status == JobStatus.COMPLETED

    def test_process_and_fail_mix(self):
        """Test job with both processed and failed rows."""
        job = Job(
            file_id="file-123",
            template_id="template-456",
            mapping_id="mapping-789",
            total_rows=100,
        )

        job.increment_processed(95)
        job.increment_failed(5)

        assert job.processed_rows == 95
        assert job.failed_rows == 5
        assert job.progress_percentage == 95.0
