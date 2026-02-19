"""
Unit tests for API dependencies module.

Tests shared dependency functions and service instances.
"""

import pytest

from src.api.dependencies import (
    _file_storage,
    _template_store,
    _output_storage,
    file_storage,
    template_store,
    output_storage,
    database,
)


class TestServiceInstances:
    """Tests for singleton service instances."""

    def test_file_storage_is_singleton(self) -> None:
        """Test that file_storage is a singleton instance."""
        assert _file_storage is not None
        # Getting it again should return the same instance
        from src.services.file_storage import get_file_storage
        assert get_file_storage() is _file_storage

    def test_template_store_is_singleton(self) -> None:
        """Test that template_store is a singleton instance."""
        assert _template_store is not None
        # Getting it again should return the same instance
        from src.services.template_store import get_template_store
        assert get_template_store() is _template_store

    def test_output_storage_is_singleton(self) -> None:
        """Test that output_storage is a singleton instance."""
        assert _output_storage is not None
        # Getting it again should return the same instance
        from src.services.output_storage import get_output_storage
        assert get_output_storage() is _output_storage


class TestDependencyFunctions:
    """Tests for dependency functions."""

    @pytest.mark.asyncio
    async def test_file_storage_dependency(self) -> None:
        """Test that file_storage dependency function yields storage."""
        result = []
        async_gen = file_storage()
        async for storage in async_gen:
            result.append(storage)
            break

        assert len(result) == 1
        assert result[0] is _file_storage

    @pytest.mark.asyncio
    async def test_template_store_dependency(self) -> None:
        """Test that template_store dependency function yields store."""
        result = []
        async_gen = template_store()
        async for store in async_gen:
            result.append(store)
            break

        assert len(result) == 1
        assert result[0] is _template_store

    @pytest.mark.asyncio
    async def test_output_storage_dependency(self) -> None:
        """Test that output_storage dependency function yields storage."""
        result = []
        async_gen = output_storage()
        async for storage in async_gen:
            result.append(storage)
            break

        assert len(result) == 1
        assert result[0] is _output_storage

    def test_database_dependency(self) -> None:
        """Test that database dependency function is a generator."""
        # The database dependency should be a generator function
        db_gen = database()
        # We can't easily test the full database session without a full DB setup
        # but we can verify it's a generator
        assert hasattr(db_gen, '__iter__') or hasattr(db_gen, '__aiter__')
        # Clean up
        try:
            if hasattr(db_gen, 'close'):
                db_gen.close()
        except:
            pass


class TestModuleExports:
    """Tests for module exports."""

    def test_module_exports_file_storage(self) -> None:
        """Test that module exports _file_storage."""
        import src.api.dependencies as deps
        assert hasattr(deps, '_file_storage')

    def test_module_exports_template_store(self) -> None:
        """Test that module exports _template_store."""
        import src.api.dependencies as deps
        assert hasattr(deps, '_template_store')

    def test_module_exports_output_storage(self) -> None:
        """Test that module exports _output_storage."""
        import src.api.dependencies as deps
        assert hasattr(deps, '_output_storage')

    def test_module_exports_dependency_functions(self) -> None:
        """Test that module exports dependency functions."""
        import src.api.dependencies as deps
        assert hasattr(deps, 'file_storage')
        assert hasattr(deps, 'template_store')
        assert hasattr(deps, 'output_storage')
        assert hasattr(deps, 'database')

    def test_module_exports_get_db(self) -> None:
        """Test that module re-exports get_db."""
        import src.api.dependencies as deps
        assert hasattr(deps, 'get_db')
