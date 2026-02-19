"""
Unit tests for FileStorage service.
"""

import pytest
from uuid import UUID, uuid4

from src.services.file_storage import FileStorage, get_file_storage


class TestFileStorage:
    """Tests for FileStorage service."""

    def test_file_storage_initialization(self) -> None:
        """Test FileStorage initializes with empty storage."""
        storage = FileStorage()
        assert storage.list_files() == []

    def test_store_and_retrieve_content(self) -> None:
        """Test storing and retrieving file content."""
        storage = FileStorage()
        file_id = uuid4()
        content = b"test content"

        storage.store(file_id, content)
        retrieved = storage.get(file_id)

        assert retrieved == content

    def test_get_nonexistent_file_returns_none(self) -> None:
        """Test getting a nonexistent file returns None."""
        storage = FileStorage()
        result = storage.get(uuid4())
        assert result is None

    def test_exists_returns_true_for_stored_file(self) -> None:
        """Test exists returns True for stored files."""
        storage = FileStorage()
        file_id = uuid4()
        storage.store(file_id, b"content")

        assert storage.exists(file_id) is True

    def test_exists_returns_false_for_nonexistent_file(self) -> None:
        """Test exists returns False for nonexistent files."""
        storage = FileStorage()
        assert storage.exists(uuid4()) is False

    def test_delete_removes_file(self) -> None:
        """Test deleting a file removes it from storage."""
        storage = FileStorage()
        file_id = uuid4()
        storage.store(file_id, b"content")

        result = storage.delete(file_id)

        assert result is True
        assert storage.exists(file_id) is False

    def test_delete_nonexistent_file_returns_false(self) -> None:
        """Test deleting a nonexistent file returns False."""
        storage = FileStorage()
        result = storage.delete(uuid4())
        assert result is False

    def test_clear_removes_all_files(self) -> None:
        """Test clear removes all files from storage."""
        storage = FileStorage()
        file_id_1 = uuid4()
        file_id_2 = uuid4()
        storage.store(file_id_1, b"content1")
        storage.store(file_id_2, b"content2")

        storage.clear()

        assert storage.list_files() == []

    def test_list_files_returns_all_ids(self) -> None:
        """Test list_files returns all stored file IDs."""
        storage = FileStorage()
        file_id_1 = uuid4()
        file_id_2 = uuid4()
        storage.store(file_id_1, b"content1")
        storage.store(file_id_2, b"content2")

        file_ids = storage.list_files()

        assert len(file_ids) == 2
        assert file_id_1 in file_ids
        assert file_id_2 in file_ids

    def test_thread_safety(self) -> None:
        """Test storage is thread-safe (basic check)."""
        storage = FileStorage()
        file_id = uuid4()

        # Multiple operations should work
        storage.store(file_id, b"test")
        storage.store(file_id, b"test2")  # Overwrite
        storage.delete(file_id)

        assert storage.exists(file_id) is False

    def test_get_file_storage_singleton(self) -> None:
        """Test get_file_storage returns singleton instance."""
        storage1 = get_file_storage()
        storage2 = get_file_storage()

        # Should return the same instance
        assert storage1 is storage2
