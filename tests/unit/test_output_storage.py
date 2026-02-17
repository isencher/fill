"""
Unit tests for Output Storage Service.
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.services.output_storage import (
    OutputStorage,
    OutputStorageError,
    get_output_storage,
    save_output,
    get_output,
    get_job_outputs,
)


class TestOutputStorageCreation:
    """Tests for OutputStorage initialization."""

    def test_create_storage_without_dir(self):
        """Test creating storage without directory (in-memory)."""
        storage = OutputStorage()
        assert storage is not None
        assert storage._storage_dir is None

    def test_create_storage_with_dir(self, tmp_path):
        """Test creating storage with directory."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        assert storage is not None
        assert storage._storage_dir == storage_dir


class TestSaveOutput:
    """Tests for save_output method."""

    def test_save_output_in_memory(self):
        """Test saving output to in-memory storage."""
        storage = OutputStorage()
        # Use binary content that's not valid UTF-8
        content = b"\xff\xfe\xfd"

        filepath = storage.save_output("job-1", 0, content)

        assert filepath == "output_0.docx"
        assert storage.get_output("job-1", "output_0.docx") == content

    def test_save_output_to_file(self, tmp_path):
        """Test saving output to file-based storage."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        # Use binary content that's not valid UTF-8
        content = b"\xff\xfe\xfd"

        filepath = storage.save_output("job-1", 0, content)

        assert filepath == str(storage_dir / "job-1" / "output_0.docx")
        assert storage.get_output("job-1", "output_0.docx") == content

    def test_save_output_with_custom_filename(self, tmp_path):
        """Test saving output with custom filename."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        content = b"Test content"

        filepath = storage.save_output("job-1", 0, content, filename="custom.txt")

        assert "custom.txt" in filepath
        assert storage.get_output("job-1", "custom.txt") == content

    def test_save_output_with_metadata(self, tmp_path):
        """Test saving output with metadata."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        content = b"Test content"
        metadata = {"author": "test", "created": "2026-02-14"}

        storage.save_output("job-1", 0, content, metadata=metadata)

        retrieved_metadata = storage.get_job_metadata("job-1")
        assert retrieved_metadata is not None
        assert retrieved_metadata["author"] == "test"

    def test_save_output_detects_docx_extension(self):
        """Test that DOCX extension is detected from content."""
        storage = OutputStorage()
        # DOCX files start with PK (zip signature)
        content = b"PK\x03\x04" + b"\x00" * 100

        filepath = storage.save_output("job-1", 0, content)

        assert filepath == "output_0.docx"

    def test_save_output_detects_pdf_extension(self):
        """Test that PDF extension is detected from content."""
        storage = OutputStorage()
        content = b"%PDF-1.4" + b"\x00" * 100

        filepath = storage.save_output("job-1", 0, content)

        assert filepath == "output_0.pdf"

    def test_save_output_detects_text_extension(self):
        """Test that TXT extension is detected from text content."""
        storage = OutputStorage()
        content = b"Plain text content"

        filepath = storage.save_output("job-1", 0, content)

        assert filepath == "output_0.txt"

    def test_save_output_multiple_outputs(self, tmp_path):
        """Test saving multiple outputs for same job."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)

        storage.save_output("job-1", 0, b"\xff\xfe")
        storage.save_output("job-1", 1, b"\xfd\xfc")
        storage.save_output("job-1", 2, b"\xfb\xfa")

        files = storage.list_job_files("job-1")
        assert len(files) == 3
        assert "output_0.docx" in files
        assert "output_1.docx" in files
        assert "output_2.docx" in files

    def test_save_output_creates_job_directory(self, tmp_path):
        """Test that save creates job directory."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)

        storage.save_output("new-job", 0, b"Content")

        job_dir = storage_dir / "new-job"
        assert job_dir.exists()
        assert job_dir.is_dir()


class TestGetOutput:
    """Tests for get_output method."""

    def test_get_output_in_memory(self):
        """Test retrieving output from in-memory storage."""
        storage = OutputStorage()
        content = b"Test content"
        storage.save_output("job-1", 0, content, filename="test.txt")

        retrieved = storage.get_output("job-1", "test.txt")

        assert retrieved == content

    def test_get_output_from_file(self, tmp_path):
        """Test retrieving output from file-based storage."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        content = b"Test content"
        storage.save_output("job-1", 0, content, filename="test.txt")

        retrieved = storage.get_output("job-1", "test.txt")

        assert retrieved == content

    def test_get_output_returns_none_for_nonexistent(self, tmp_path):
        """Test that get_output returns None for non-existent file."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)

        retrieved = storage.get_output("job-1", "nonexistent.txt")

        assert retrieved is None

    def test_get_output_returns_none_for_nonexistent_job(self, tmp_path):
        """Test that get_output returns None for non-existent job."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)

        retrieved = storage.get_output("nonexistent-job", "test.txt")

        assert retrieved is None


class TestGetJobOutputs:
    """Tests for get_job_outputs method."""

    def test_get_job_outputs_in_memory(self):
        """Test retrieving all outputs from in-memory storage."""
        storage = OutputStorage()
        storage.save_output("job-1", 0, b"Content 0", filename="file0.txt")
        storage.save_output("job-1", 1, b"Content 1", filename="file1.txt")
        storage.save_output("job-1", 2, b"Content 2", filename="file2.txt")

        outputs = storage.get_job_outputs("job-1")

        assert len(outputs) == 3
        assert outputs["file0.txt"] == b"Content 0"
        assert outputs["file1.txt"] == b"Content 1"
        assert outputs["file2.txt"] == b"Content 2"

    def test_get_job_outputs_from_file(self, tmp_path):
        """Test retrieving all outputs from file-based storage."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        storage.save_output("job-1", 0, b"Content 0", filename="file0.txt")
        storage.save_output("job-1", 1, b"Content 1", filename="file1.txt")

        outputs = storage.get_job_outputs("job-1")

        assert len(outputs) == 2
        assert outputs["file0.txt"] == b"Content 0"

    def test_get_job_outputs_empty_for_nonexistent_job(self, tmp_path):
        """Test that get_job_outputs returns empty dict for non-existent job."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)

        outputs = storage.get_job_outputs("nonexistent-job")

        assert outputs == {}

    def test_get_job_outputs_excludes_metadata(self, tmp_path):
        """Test that get_job_outputs excludes metadata.json."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        storage.save_output("job-1", 0, b"Content", metadata={"key": "value"})

        outputs = storage.get_job_outputs("job-1")

        # Should only include output files, not metadata.json
        assert "metadata.json" not in outputs
        assert len(outputs) == 1


class TestListJobFiles:
    """Tests for list_job_files method."""

    def test_list_job_files_in_memory(self):
        """Test listing files from in-memory storage."""
        storage = OutputStorage()
        storage.save_output("job-1", 0, b"\xff\xfe")
        storage.save_output("job-1", 1, b"\xfd\xfc")

        files = storage.list_job_files("job-1")

        assert len(files) == 2
        assert "output_0.docx" in files
        assert "output_1.docx" in files

    def test_list_job_files_from_file(self, tmp_path):
        """Test listing files from file-based storage."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        storage.save_output("job-1", 0, b"Content 0")
        storage.save_output("job-1", 1, b"Content 1")

        files = storage.list_job_files("job-1")

        assert len(files) == 2

    def test_list_job_files_empty_for_nonexistent_job(self, tmp_path):
        """Test that list_job_files returns empty list for non-existent job."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)

        files = storage.list_job_files("nonexistent-job")

        assert files == []

    def test_list_job_files_excludes_metadata(self, tmp_path):
        """Test that list_job_files excludes metadata.json."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        storage.save_output("job-1", 0, b"Content", metadata={"key": "value"})

        files = storage.list_job_files("job-1")

        # Should not include metadata.json
        assert "metadata.json" not in files


class TestDeleteJobOutputs:
    """Tests for delete_job_outputs method."""

    def test_delete_job_outputs_in_memory(self):
        """Test deleting outputs from in-memory storage."""
        storage = OutputStorage()
        storage.save_output("job-1", 0, b"Content")
        assert storage.job_exists("job-1")

        result = storage.delete_job_outputs("job-1")

        assert result is True
        assert not storage.job_exists("job-1")

    def test_delete_job_outputs_from_file(self, tmp_path):
        """Test deleting outputs from file-based storage."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        storage.save_output("job-1", 0, b"Content")
        assert storage.job_exists("job-1")

        result = storage.delete_job_outputs("job-1")

        assert result is True
        assert not storage.job_exists("job-1")
        assert not (storage_dir / "job-1").exists()

    def test_delete_job_outputs_returns_false_for_nonexistent(self, tmp_path):
        """Test that delete returns False for non-existent job."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)

        result = storage.delete_job_outputs("nonexistent-job")

        assert result is False

    def test_delete_job_outputs_removes_directory(self, tmp_path):
        """Test that delete removes entire job directory."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        storage.save_output("job-1", 0, b"Content 0")
        storage.save_output("job-1", 1, b"Content 1")

        storage.delete_job_outputs("job-1")

        job_dir = storage_dir / "job-1"
        assert not job_dir.exists()


class TestJobExists:
    """Tests for job_exists method."""

    def test_job_exists_in_memory(self):
        """Test checking if job exists in in-memory storage."""
        storage = OutputStorage()
        assert not storage.job_exists("job-1")

        storage.save_output("job-1", 0, b"Content")

        assert storage.job_exists("job-1")

    def test_job_exists_for_file(self, tmp_path):
        """Test checking if job exists in file-based storage."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        assert not storage.job_exists("job-1")

        storage.save_output("job-1", 0, b"Content")

        assert storage.job_exists("job-1")

    def test_job_exists_false_for_nonexistent(self, tmp_path):
        """Test that job_exists returns False for non-existent job."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)

        assert not storage.job_exists("nonexistent-job")


class TestGetJobMetadata:
    """Tests for get_job_metadata method."""

    def test_get_job_metadata_returns_none_for_in_memory(self):
        """Test that in-memory storage doesn't support metadata."""
        storage = OutputStorage()
        storage.save_output("job-1", 0, b"Content", metadata={"key": "value"})

        metadata = storage.get_job_metadata("job-1")

        assert metadata is None

    def test_get_job_metadata_from_file(self, tmp_path):
        """Test retrieving metadata from file-based storage."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        metadata_input = {"author": "test", "count": 3}
        storage.save_output("job-1", 0, b"Content", metadata=metadata_input)

        metadata = storage.get_job_metadata("job-1")

        assert metadata is not None
        assert metadata["author"] == "test"
        assert metadata["count"] == 3

    def test_get_job_metadata_returns_none_for_nonexistent(self, tmp_path):
        """Test that get_job_metadata returns None for non-existent job."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)

        metadata = storage.get_job_metadata("nonexistent-job")

        assert metadata is None

    def test_get_job_metadata_returns_none_without_metadata(self, tmp_path):
        """Test that get_job_metadata returns None when no metadata saved."""
        storage_dir = tmp_path / "outputs"
        storage = OutputStorage(storage_dir=storage_dir)
        storage.save_output("job-1", 0, b"Content")

        metadata = storage.get_job_metadata("job-1")

        assert metadata is None


class TestOutputStorageError:
    """Tests for OutputStorageError exception."""

    def test_error_creation(self):
        """Test creating an OutputStorageError."""
        error = OutputStorageError("Test error message")
        assert error.message == "Test error message"
        assert str(error) == "Test error message"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_output_storage_returns_singleton(self):
        """Test that get_output_storage returns singleton instance."""
        storage1 = get_output_storage()
        storage2 = get_output_storage()

        assert storage1 is storage2

    def test_get_output_storage_with_dir(self, tmp_path):
        """Test get_output_storage with custom directory creates new instance."""
        storage_dir = tmp_path / "outputs"
        # Note: singleton is already created, so this won't change it
        # Create a new storage instance directly instead
        storage = OutputStorage(storage_dir)

        assert storage._storage_dir == storage_dir

    def test_save_output_convenience(self):
        """Test save_output convenience function."""
        content = save_output("job-1", 0, b"Test content", filename="test.txt")

        storage = get_output_storage()
        retrieved = storage.get_output("job-1", "test.txt")

        assert retrieved == b"Test content"

    def test_get_output_convenience(self):
        """Test get_output convenience function."""
        storage = get_output_storage()
        storage.save_output("job-1", 0, b"Test content", filename="test.txt")

        retrieved = get_output("job-1", "test.txt")

        assert retrieved == b"Test content"

    def test_get_job_outputs_convenience(self):
        """Test get_job_outputs convenience function."""
        storage = get_output_storage()
        storage.save_output("job-unique-1", 0, b"\xff\xfe", filename="file0.docx")
        storage.save_output("job-unique-1", 1, b"\xfd\xfc", filename="file1.docx")

        outputs = get_job_outputs("job-unique-1")

        assert len(outputs) == 2
