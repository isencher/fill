"""
Fill Application - Batch Job Model

Defines batch processing job model for tracking fill operations.
"""

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobStatus(str, Enum):
    """
    Status of a batch processing job.

    Attributes:
        PENDING: Job is queued and waiting to be processed
        PROCESSING: Job is currently being processed
        COMPLETED: Job has completed successfully
        FAILED: Job has failed
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    """
    Batch processing job model for tracking fill operations.

    Tracks the progress of batch fill operations where a template
    is filled with data from each row of an uploaded file.

    Attributes:
        id: Unique identifier for the job (auto-generated UUID)
        file_id: ID of the source file being processed
        template_id: ID of the template being filled
        mapping_id: ID of the column-to-placeholder mapping
        status: Current status of the job
        total_rows: Total number of rows to process
        processed_rows: Number of rows processed so far
        failed_rows: Number of rows that failed to process
        created_at: Timestamp when job was created (auto-generated)
        updated_at: Timestamp when job was last updated (auto-generated)
        error_message: Error message if job failed (optional)
    """

    id: UUID = Field(default_factory=uuid4)
    file_id: str = Field(..., min_length=1)
    template_id: str = Field(..., min_length=1)
    mapping_id: str = Field(..., min_length=1)
    status: JobStatus = Field(default=JobStatus.PENDING)
    total_rows: int = Field(..., ge=0)
    processed_rows: int = Field(default=0, ge=0)
    failed_rows: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: str | None = None

    model_config = ConfigDict(
        # Use enum values (strings) instead of enum objects
        use_enum_values=True,
        # Validate assignment to ensure data integrity
        validate_assignment=True,
        # Allow arbitrary types for additional flexibility
        arbitrary_types_allowed=True,
    )

    @field_validator("file_id", "template_id", "mapping_id", mode="before")
    @classmethod
    def trim_string_fields(cls, value: str | None) -> str | None:
        """
        Trim whitespace from string fields.

        Args:
            value: String value to trim

        Returns:
            Trimmed string value or None

        Raises:
            ValueError: If trimmed value is empty
        """
        if value is None:
            return None

        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or whitespace only")

        return trimmed

    @field_validator("error_message", mode="before")
    @classmethod
    def validate_error_message(cls, value: str | None) -> str | None:
        """
        Validate error message field.

        Args:
            value: Error message to validate

        Returns:
            Trimmed error message or None
        """
        if value is None:
            return None

        trimmed = value.strip()
        # Allow empty string to clear error message
        return trimmed if trimmed else None

    @property
    def progress_percentage(self) -> float:
        """
        Calculate job progress as a percentage.

        Returns:
            Progress percentage (0-100), or 0 if total_rows is 0
        """
        if self.total_rows == 0:
            return 0.0

        return (self.processed_rows / self.total_rows) * 100

    @property
    def is_complete(self) -> bool:
        """
        Check if job is complete (successfully or with failures).

        Returns:
            True if job status is COMPLETED or FAILED
        """
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED]

    @property
    def is_running(self) -> bool:
        """
        Check if job is currently running.

        Returns:
            True if job status is PROCESSING
        """
        return self.status == JobStatus.PROCESSING

    def increment_processed(self, count: int = 1) -> None:
        """
        Increment the processed row count and update timestamp.

        Args:
            count: Number of rows to increment by (default: 1)

        Raises:
            ValueError: If count is negative
        """
        if count < 0:
            raise ValueError("Count cannot be negative")

        self.processed_rows += count
        self.updated_at = datetime.utcnow()

    def increment_failed(self, count: int = 1) -> None:
        """
        Increment the failed row count and update timestamp.

        Args:
            count: Number of rows to increment by (default: 1)

        Raises:
            ValueError: If count is negative
        """
        if count < 0:
            raise ValueError("Count cannot be negative")

        self.failed_rows += count
        self.updated_at = datetime.utcnow()

    def set_status(
        self, status: JobStatus | Literal["pending", "processing", "completed", "failed"]
    ) -> None:
        """
        Update job status and timestamp.

        Args:
            status: New job status
        """
        # Convert string to JobStatus enum if needed
        if isinstance(status, str):
            status = JobStatus(status.lower())

        self.status = status
        self.updated_at = datetime.utcnow()

    def set_error(self, error_message: str) -> None:
        """
        Set error message and mark job as failed.

        Args:
            error_message: Error message describing the failure
        """
        self.error_message = error_message.strip()
        self.status = JobStatus.FAILED
        self.updated_at = datetime.utcnow()
