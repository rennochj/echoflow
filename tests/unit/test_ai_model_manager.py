"""Tests for AI Model Manager functionality."""

import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from echoflow.ai.model_manager import ModelManager
from echoflow.exceptions.base import ConversionError, ProcessingError


class TestModelManager:
    """Test cases for ModelManager class."""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """Create a temporary cache directory for testing."""
        return tmp_path / "test_cache"

    @pytest.fixture
    def model_manager(self, temp_cache_dir):
        """Create a ModelManager instance for testing."""
        return ModelManager(cache_dir=temp_cache_dir)

    def test_init(self, model_manager, temp_cache_dir):
        """Test ModelManager initialization."""
        assert model_manager.cache_dir == temp_cache_dir
        assert temp_cache_dir.exists()
        assert not model_manager._initialized
        assert model_manager._converter is None
        assert model_manager._last_health_check == 0.0

    @pytest.mark.asyncio
    async def test_initialize_success(self, model_manager):
        """Test successful model initialization."""
        mock_converter = Mock()

        with patch("echoflow.ai.model_manager.DocumentConverter") as mock_doc_converter:
            mock_doc_converter.return_value = mock_converter
            with patch.object(model_manager, "_verify_model_functionality", new_callable=AsyncMock):

                await model_manager.initialize()

                assert model_manager._initialized
                assert model_manager._converter == mock_converter
                mock_doc_converter.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self, model_manager):
        """Test that initialize skips if already initialized."""
        model_manager._initialized = True
        original_converter = Mock()
        model_manager._converter = original_converter

        with patch("echoflow.ai.model_manager.DocumentConverter") as mock_doc_converter:
            await model_manager.initialize()

            # Should not create new converter
            mock_doc_converter.assert_not_called()
            assert model_manager._converter == original_converter

    @pytest.mark.asyncio
    async def test_initialize_failure(self, model_manager):
        """Test model initialization failure."""
        with patch("echoflow.ai.model_manager.DocumentConverter") as mock_doc_converter:
            mock_doc_converter.side_effect = Exception("Initialization failed")

            with pytest.raises(ConversionError, match="AI model initialization failed"):
                await model_manager.initialize()

            assert not model_manager._initialized
            assert model_manager._converter is None

    @pytest.mark.asyncio
    async def test_get_converter_not_initialized(self, model_manager):
        """Test get_converter initializes if not ready."""
        mock_converter = Mock()

        with patch("echoflow.ai.model_manager.DocumentConverter") as mock_doc_converter:
            mock_doc_converter.return_value = mock_converter
            with patch.object(model_manager, "_verify_model_functionality", new_callable=AsyncMock):

                result = await model_manager.get_converter()

                assert result == mock_converter
                assert model_manager._initialized

    @pytest.mark.asyncio
    async def test_get_converter_already_initialized(self, model_manager):
        """Test get_converter when already initialized."""
        mock_converter = Mock()
        model_manager._initialized = True
        model_manager._converter = mock_converter

        result = await model_manager.get_converter()

        assert result == mock_converter

    @pytest.mark.asyncio
    async def test_get_converter_none_after_init(self, model_manager):
        """Test get_converter raises error if converter is None after init."""
        model_manager._initialized = True
        model_manager._converter = None

        with pytest.raises(ConversionError, match="Document converter not available"):
            await model_manager.get_converter()

    @pytest.mark.asyncio
    async def test_health_check_not_initialized(self, model_manager):
        """Test health check when not initialized."""
        result = await model_manager.health_check()

        assert not result

    @pytest.mark.asyncio
    async def test_health_check_cached_result(self, model_manager):
        """Test health check uses cached result within interval."""
        model_manager._initialized = True
        model_manager._converter = Mock()
        model_manager._last_health_check = time.time()

        # Should return True without calling verify
        with patch.object(model_manager, "_verify_model_functionality") as mock_verify:
            result = await model_manager.health_check()

            assert result
            mock_verify.assert_not_called()

    @pytest.mark.asyncio
    async def test_health_check_success(self, model_manager):
        """Test successful health check."""
        model_manager._initialized = True
        model_manager._converter = Mock()
        model_manager._last_health_check = 0.0  # Force check

        with patch.object(model_manager, "_verify_model_functionality", new_callable=AsyncMock):
            result = await model_manager.health_check()

            assert result
            assert model_manager._last_health_check > 0

    @pytest.mark.asyncio
    async def test_health_check_failure(self, model_manager):
        """Test health check failure."""
        model_manager._initialized = True
        model_manager._converter = Mock()
        model_manager._last_health_check = 0.0  # Force check

        with patch.object(model_manager, "_verify_model_functionality", new_callable=AsyncMock) as mock_verify:
            mock_verify.side_effect = Exception("Health check failed")

            result = await model_manager.health_check()

            assert not result
            assert model_manager._last_health_check > 0

    @pytest.mark.asyncio
    async def test_verify_model_functionality_success(self, model_manager):
        """Test successful model functionality verification."""
        mock_converter = Mock()
        model_manager._converter = mock_converter

        # Should not raise exception
        await model_manager._verify_model_functionality()

    @pytest.mark.asyncio
    async def test_verify_model_functionality_no_converter(self, model_manager):
        """Test model functionality verification with no converter."""
        model_manager._converter = None

        with pytest.raises(ProcessingError, match="Document converter not available"):
            await model_manager._verify_model_functionality()

    def test_get_model_info_not_initialized(self, model_manager):
        """Test get_model_info when not initialized."""
        info = model_manager.get_model_info()

        assert info["status"] == "not_initialized"
        assert info["converter_available"] == "False"
        assert "cache_dir" in info
        assert "supported_formats" in info

    def test_get_model_info_initialized(self, model_manager):
        """Test get_model_info when initialized."""
        model_manager._initialized = True
        model_manager._converter = Mock()

        info = model_manager.get_model_info()

        assert info["status"] == "initialized"
        assert info["converter_available"] == "True"

    @pytest.mark.asyncio
    async def test_cleanup(self, model_manager):
        """Test cleanup functionality."""
        model_manager._initialized = True
        model_manager._converter = Mock()

        await model_manager.cleanup()

        assert not model_manager._initialized
        assert model_manager._converter is None

    @pytest.mark.asyncio
    async def test_cleanup_with_exception(self, model_manager):
        """Test cleanup handles exceptions gracefully."""
        model_manager._initialized = True
        model_manager._converter = Mock()

        # Mock an exception during cleanup - should not raise
        with patch("echoflow.ai.model_manager.logger"):
            await model_manager.cleanup()

            # Cleanup should still complete
            assert not model_manager._initialized
            assert model_manager._converter is None
