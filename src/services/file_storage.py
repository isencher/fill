"""
File Storage Service - Centralized in-memory file content storage.

This service provides a thread-safe, centralized storage for file contents
that were previously managed using global variables.
"""

from uuid import UUID
from typing import Dict, Optional
import threading


class FileStorage:
    """
    Thread-safe storage for file contents.

    This service manages in-memory storage of uploaded file contents,
    providing methods to store, retrieve, and delete file data.
    """

    def __init__(self) -> None:
        """Initialize the file storage with empty storage dict and lock."""
        self._storage: Dict[UUID, bytes] = {}
        self._lock = threading.Lock()

    def store(self, file_id: UUID, content: bytes) -> None:
        """
        Store file content in memory.

        Args:
            file_id: Unique identifier for the file
            content: Binary content of the file
        """
        with self._lock:
            self._storage[file_id] = content

    def get(self, file_id: UUID) -> Optional[bytes]:
        """
        Retrieve file content from memory.

        Args:
            file_id: Unique identifier for the file

        Returns:
            File content as bytes, or None if not found
        """
        with self._lock:
            return self._storage.get(file_id)

    def delete(self, file_id: UUID) -> bool:
        """
        Delete file content from memory.

        Args:
            file_id: Unique identifier for the file

        Returns:
            True if file was deleted, False if not found
        """
        with self._lock:
            if file_id in self._storage:
                del self._storage[file_id]
                return True
            return False

    def clear(self) -> None:
        """Clear all stored file contents."""
        with self._lock:
            self._storage.clear()

    def exists(self, file_id: UUID) -> bool:
        """
        Check if file content exists in storage.

        Args:
            file_id: Unique identifier for the file

        Returns:
            True if file exists in storage, False otherwise
        """
        with self._lock:
            return file_id in self._storage

    def list_files(self) -> list[UUID]:
        """
        List all stored file IDs.

        Returns:
            List of file IDs currently in storage
        """
        with self._lock:
            return list(self._storage.keys())


# Global singleton instance
_file_storage = FileStorage()


def get_file_storage() -> FileStorage:
    """
    Get the global FileStorage singleton instance.

    Returns:
        The global FileStorage instance
    """
    return _file_storage
