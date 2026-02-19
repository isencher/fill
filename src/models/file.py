"""
Fill Application - File Upload Model

Defines the UploadFile data model with validation for file uploads.
"""

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class FileStatus(str, Enum):
    """Status of an uploaded file."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadFile(BaseModel):
    """
    Represents an uploaded file with metadata.

    Attributes:
        id: Unique identifier for the file
        filename: Original filename from upload
        content_type: MIME type of the file
        size: File size in bytes
        uploaded_at: Timestamp when file was uploaded
        status: Current processing status
    """

    id: UUID = Field(default_factory=uuid4, description="Unique file identifier")
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    content_type: str = Field(..., pattern=r"^[a-z]+/[a-z0-9\-.]+$", description="MIME type")
    size: int = Field(..., gt=0, description="File size in bytes")
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Upload timestamp")
    status: FileStatus = Field(default=FileStatus.PENDING, description="Processing status")

    @field_validator("filename")
    @classmethod
    def validate_filename_extension(cls, v: str) -> str:
        """
        Validate that filename has an allowed extension.

        Args:
            v: Filename to validate

        Returns:
            The validated filename

        Raises:
            ValueError: If extension is not allowed
        """
        allowed_extensions = {".xlsx", ".csv"}
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(
                f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
            )
        return v

    @field_validator("size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """
        Validate that file size is within allowed limits.

        Args:
            v: File size in bytes

        Returns:
            The validated file size

        Raises:
            ValueError: If file exceeds maximum size
        """
        max_size = 10 * 1024 * 1024  # 10 MB
        if v > max_size:
            raise ValueError(f"File size exceeds maximum allowed size of {max_size} bytes")
        return v

    @model_validator(mode="after")
    def validate_content_type_matches_extension(self) -> "UploadFile":
        """
        Validate that content type matches filename extension.

        Returns:
            The validated UploadFile instance

        Raises:
            ValueError: If content type doesn't match extension
        """
        filename_lower = self.filename.lower()
        if filename_lower.endswith(".csv"):
            if self.content_type not in {"text/csv", "application/csv"}:
                raise ValueError("CSV files must have content-type: text/csv or application/csv")
        elif filename_lower.endswith(".xlsx"):
            if self.content_type not in {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel",
            }:
                raise ValueError("Excel files must have appropriate Excel content-type")
        return self

    model_config = ConfigDict(
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat(),
        },
        use_enum_values=True,
    )
