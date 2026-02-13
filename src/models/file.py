"""File upload model for fill application.

This module defines the UploadFile model which represents an uploaded file
with validation for:
- File extensions (xlsx, csv)
- File size limits (10MB)
- Required fields
"""

import time
import uuid
from dataclasses import dataclass, field

# Configuration constants
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"xlsx", "csv"}


class FileValidationError(Exception):
    """Raised when file validation fails."""

    pass


@dataclass
class UploadFile:
    """Represents an uploaded file with validation.

    Attributes:
        id: Unique identifier for the file
        filename: Name of the uploaded file
        content_type: MIME type of the file
        size: File size in bytes
        uploaded_at: Timestamp when file was uploaded
        status: Current status (pending, processing, completed, failed)
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    content_type: str = ""
    size: int = 0
    uploaded_at: float = field(default_factory=time.time)
    status: str = "pending"

    def __post_init__(self) -> None:
        """Validate file data after initialization.

        Raises:
            FileValidationError: If validation fails
        """
        self._validate_filename()
        self._validate_size()

    def _validate_filename(self) -> None:
        """Validate filename has allowed extension.

        Raises:
            FileValidationError: If filename is empty or has invalid extension
        """
        if not self.filename or not self.filename.strip():
            raise FileValidationError("Filename cannot be empty")

        # Extract extension
        parts = self.filename.rsplit(".", 1)
        if len(parts) != 2:
            raise FileValidationError(
                f"Invalid file extension. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        extension = parts[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise FileValidationError(
                f"Invalid file extension '.{extension}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

    def _validate_size(self) -> None:
        """Validate file size is within limits.

        Raises:
            FileValidationError: If file size is invalid
        """
        if self.size <= 0:
            raise FileValidationError("File size must be greater than zero")

        if self.size > MAX_FILE_SIZE_BYTES:
            raise FileValidationError(
                f"File size exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES} bytes "
                f"({MAX_FILE_SIZE_BYTES / (1024 * 1024):.1f}MB)"
            )
