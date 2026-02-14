"""
Output Storage Service for Fill Application.

This service provides persistent storage for generated documents,
allowing retrieval of outputs by job ID and individual file names.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import shutil
import uuid


class OutputStorageError(Exception):
    """Exception raised for output storage errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class OutputStorage:
    """
    Service for storing and retrieving generated documents.

    Storage structure:
        storage_dir/
            {job_id}/
                output_0.ext
                output_1.ext
                metadata.json
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize OutputStorage.

        Args:
            storage_dir: Directory for storing outputs. If None, uses in-memory storage.
        """
        self._storage_dir = storage_dir
        self._memory_storage: Dict[str, Dict[str, bytes]] = {}

    def save_output(
        self,
        job_id: str,
        row_index: int,
        content: bytes,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save output document for a job.

        Args:
            job_id: Job identifier
            row_index: Row index in source file
            content: Document content as bytes
            filename: Optional filename (default: output_{row_index}.ext)
            metadata: Optional metadata dictionary

        Returns:
            Path to saved file (or file identifier for in-memory)

        Raises:
            OutputStorageError: If save fails
        """
        # Generate filename if not provided
        if filename is None:
            # Try to detect extension from content or default to .docx
            ext = self._detect_extension(content)
            filename = f"output_{row_index}{ext}"

        if self._storage_dir is None:
            # In-memory storage
            if job_id not in self._memory_storage:
                self._memory_storage[job_id] = {}
            self._memory_storage[job_id][filename] = content
            return filename

        # File-based storage
        try:
            job_dir = self._storage_dir / job_id
            job_dir.mkdir(parents=True, exist_ok=True)

            output_path = job_dir / filename
            output_path.write_bytes(content)

            # Save metadata if provided
            if metadata:
                self._save_metadata(job_dir, metadata)

            return str(output_path)

        except Exception as e:
            raise OutputStorageError(f"Failed to save output: {e}") from e

    def get_output(self, job_id: str, filename: str) -> Optional[bytes]:
        """
        Retrieve a single output document.

        Args:
            job_id: Job identifier
            filename: Name of the file to retrieve

        Returns:
            File content as bytes, or None if not found
        """
        if self._storage_dir is None:
            # In-memory storage
            job_outputs = self._memory_storage.get(job_id, {})
            return job_outputs.get(filename)

        # File-based storage
        output_path = self._storage_dir / job_id / filename
        if output_path.exists():
            return output_path.read_bytes()
        return None

    def get_job_outputs(self, job_id: str) -> Dict[str, bytes]:
        """
        Retrieve all output documents for a job.

        Args:
            job_id: Job identifier

        Returns:
            Dictionary mapping filenames to content bytes
        """
        if self._storage_dir is None:
            # In-memory storage
            return self._memory_storage.get(job_id, {})

        # File-based storage
        job_dir = self._storage_dir / job_id
        if not job_dir.exists():
            return {}

        outputs = {}
        for file_path in job_dir.iterdir():
            if file_path.is_file() and file_path.name != "metadata.json":
                try:
                    outputs[file_path.name] = file_path.read_bytes()
                except Exception:
                    # Skip files that can't be read
                    pass

        return outputs

    def list_job_files(self, job_id: str) -> List[str]:
        """
        List all output filenames for a job.

        Args:
            job_id: Job identifier

        Returns:
            List of filenames
        """
        if self._storage_dir is None:
            # In-memory storage
            return list(self._memory_storage.get(job_id, {}).keys())

        # File-based storage
        job_dir = self._storage_dir / job_id
        if not job_dir.exists():
            return []

        return [
            f.name for f in job_dir.iterdir()
            if f.is_file() and f.name != "metadata.json"
        ]

    def delete_job_outputs(self, job_id: str) -> bool:
        """
        Delete all outputs for a job.

        Args:
            job_id: Job identifier

        Returns:
            True if deleted, False if job not found
        """
        if self._storage_dir is None:
            # In-memory storage
            if job_id in self._memory_storage:
                del self._memory_storage[job_id]
                return True
            return False

        # File-based storage
        job_dir = self._storage_dir / job_id
        if job_dir.exists():
            shutil.rmtree(job_dir)
            return True
        return False

    def job_exists(self, job_id: str) -> bool:
        """
        Check if a job has any outputs.

        Args:
            job_id: Job identifier

        Returns:
            True if job exists with outputs
        """
        if self._storage_dir is None:
            # In-memory storage
            return job_id in self._memory_storage

        # File-based storage
        job_dir = self._storage_dir / job_id
        return job_dir.exists() and job_dir.is_dir()

    def get_job_metadata(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a job.

        Args:
            job_id: Job identifier

        Returns:
            Metadata dictionary, or None if not found
        """
        if self._storage_dir is None:
            # In-memory storage doesn't support metadata
            return None

        # File-based storage
        metadata_path = self._storage_dir / job_id / "metadata.json"
        if not metadata_path.exists():
            return None

        try:
            import json
            return json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _save_metadata(self, job_dir: Path, metadata: Dict[str, Any]) -> None:
        """
        Save metadata to job directory.

        Args:
            job_dir: Job directory path
            metadata: Metadata dictionary to save
        """
        try:
            import json
            metadata_path = job_dir / "metadata.json"
            metadata_path.write_text(
                json.dumps(metadata, indent=2, default=str),
                encoding="utf-8"
            )
        except Exception:
            # Metadata save failure is not critical
            pass

    def _detect_extension(self, content: bytes) -> str:
        """
        Detect file extension from content bytes.

        Args:
            content: Content bytes

        Returns:
            File extension (default: .docx)
        """
        # Check for DOCX signature (PK zip signature)
        if content[:2] == b"PK":
            return ".docx"

        # Check for PDF signature
        if content[:4] == b"%PDF":
            return ".pdf"

        # Check for text
        try:
            content.decode("utf-8")
            return ".txt"
        except UnicodeDecodeError:
            pass

        # Default to DOCX
        return ".docx"


# Convenience functions
_default_storage: Optional[OutputStorage] = None


def get_output_storage(storage_dir: Optional[Path] = None) -> OutputStorage:
    """
    Get or create the default OutputStorage instance.

    Args:
        storage_dir: Optional storage directory

    Returns:
        OutputStorage instance
    """
    global _default_storage
    if _default_storage is None:
        _default_storage = OutputStorage(storage_dir)
    return _default_storage


def save_output(
    job_id: str,
    row_index: int,
    content: bytes,
    filename: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to save output using default storage.

    Args:
        job_id: Job identifier
        row_index: Row index in source file
        content: Document content as bytes
        filename: Optional filename
        metadata: Optional metadata dictionary

    Returns:
        Path to saved file
    """
    storage = get_output_storage()
    return storage.save_output(job_id, row_index, content, filename, metadata)


def get_output(job_id: str, filename: str) -> Optional[bytes]:
    """
    Convenience function to retrieve output using default storage.

    Args:
        job_id: Job identifier
        filename: Name of the file to retrieve

    Returns:
        File content as bytes, or None if not found
    """
    storage = get_output_storage()
    return storage.get_output(job_id, filename)


def get_job_outputs(job_id: str) -> Dict[str, bytes]:
    """
    Convenience function to retrieve all job outputs using default storage.

    Args:
        job_id: Job identifier

    Returns:
        Dictionary mapping filenames to content bytes
    """
    storage = get_output_storage()
    return storage.get_job_outputs(job_id)
