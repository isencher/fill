"""
File Storage Service - Centralized in-memory file content storage.

This service provides a thread-safe, centralized storage for file contents
that were previously managed using global variables.
"""

from datetime import datetime, timedelta
from uuid import UUID
from typing import Dict, Optional, Tuple
import threading


class FileStorage:
    """
    Thread-safe storage for file contents with TTL-based cleanup.

    This service manages in-memory storage of uploaded file contents,
    providing methods to store, retrieve, and delete file data.
    Files are automatically cleaned up after the TTL expires.
    """

    def __init__(self, ttl_hours: int = 24) -> None:
        """
        Initialize the file storage with empty storage dict and lock.

        Args:
            ttl_hours: Time-to-live for stored files in hours
        """
        self._storage: Dict[UUID, Tuple[bytes, datetime]] = {}
        self._lock = threading.Lock()
        self._ttl = timedelta(hours=ttl_hours)

    def store(self, file_id: UUID, content: bytes) -> None:
        """
        Store file content in memory with timestamp.

        Args:
            file_id: Unique identifier for the file
            content: Binary content of the file
        """
        with self._lock:
            self._storage[file_id] = (content, datetime.now())

    def get(self, file_id: UUID) -> Optional[bytes]:
        """
        Retrieve file content from memory.

        Args:
            file_id: Unique identifier for the file

        Returns:
            File content as bytes, or None if not found
        """
        with self._lock:
            entry = self._storage.get(file_id)
            return entry[0] if entry else None

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

    def cleanup_expired(self) -> int:
        """
        Clean up expired files based on TTL.

        Returns:
            Number of files removed
        """
        with self._lock:
            now = datetime.now()
            expired = [
                fid for fid, (_, ts) in self._storage.items()
                if now - ts > self._ttl
            ]
            for fid in expired:
                del self._storage[fid]
            return len(expired)


# Global singleton instance - initialized with default TTL
# Will be re-initialized with settings-based TTL in dependencies
_file_storage: FileStorage | None = None


def _get_global_storage() -> FileStorage:
    """Get or create the global FileStorage instance."""
    global _file_storage
    if _file_storage is None:
        _file_storage = FileStorage()
    return _file_storage


def get_file_storage() -> FileStorage:
    """
    Get the global FileStorage singleton instance.

    Returns:
        The global FileStorage instance
    """
    return _get_global_storage()
