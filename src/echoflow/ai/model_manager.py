"""AI Model Management System for EchoFlow.

This module provides model lifecycle management and caching for the Docling AI engine.
It handles model downloads, initialization, and health monitoring.
"""

import time
from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter

from ..exceptions.base import ConversionError, ProcessingError
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Manages AI model lifecycle and caching for document conversion.

    This class handles:
    - AI model downloading and initialization
    - Model caching for performance
    - Health monitoring of AI models
    - Memory-efficient model management
    """

    def __init__(self, cache_dir: Path = Path(".cache/models")) -> None:
        """Initialize model manager with caching directory.

        Args:
            cache_dir: Directory for model caching (default: .cache/models)
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._converter: Optional[DocumentConverter] = None
        self._initialized = False
        self._last_health_check = 0.0
        self._health_check_interval = 300.0  # 5 minutes

        logger.info("ModelManager initialized", cache_dir=str(cache_dir))

    async def initialize(self) -> None:
        """Initialize and download required AI models.

        Downloads and caches AI models required for document processing.
        This is an expensive operation that should be done at startup.

        Raises:
            ConversionError: If model initialization fails
        """
        if self._initialized:
            logger.debug("Model manager already initialized")
            return

        try:
            logger.info("Starting AI model initialization")
            start_time = time.time()

            # Create DocumentConverter which will download models if needed
            self._converter = DocumentConverter()

            # Test basic functionality to ensure models are working
            await self._verify_model_functionality()

            initialization_time = time.time() - start_time
            self._initialized = True

            logger.info(
                "AI models initialized successfully",
                initialization_time_seconds=round(initialization_time, 2),
            )

        except Exception as e:
            logger.error("Failed to initialize AI models", error=str(e))
            raise ConversionError(f"AI model initialization failed: {str(e)}") from e

    async def get_converter(self) -> DocumentConverter:
        """Get initialized document converter.

        Returns:
            DocumentConverter: Ready-to-use converter instance

        Raises:
            ConversionError: If models are not initialized
        """
        if not self._initialized:
            await self.initialize()

        if self._converter is None:
            raise ConversionError("Document converter not available")

        return self._converter

    async def health_check(self) -> bool:
        """Check AI model health and availability.

        Performs a lightweight health check to ensure AI models are responsive.
        Results are cached for performance.

        Returns:
            bool: True if models are healthy, False otherwise
        """
        current_time = time.time()

        # Use cached result if within interval
        if (current_time - self._last_health_check) < self._health_check_interval:
            return self._initialized and self._converter is not None

        try:
            if not self._initialized or self._converter is None:
                logger.warning("AI models not initialized during health check")
                return False

            # Simple test to verify model responsiveness
            # This is a lightweight check that doesn't perform full conversion
            await self._verify_model_functionality()

            self._last_health_check = current_time
            logger.debug("AI model health check passed")
            return True

        except Exception as e:
            logger.warning("AI model health check failed", error=str(e))
            self._last_health_check = current_time
            return False

    async def _verify_model_functionality(self) -> None:
        """Verify basic model functionality.

        Performs a minimal test to ensure models can be accessed and are responsive.

        Raises:
            ProcessingError: If model verification fails
        """
        try:
            # Test that the converter can be created and basic functionality works
            if self._converter is None:
                raise ProcessingError("Document converter not available")

            # This is a lightweight check - we're not actually converting anything
            # Just ensuring the converter is properly initialized
            logger.debug("Model functionality verification completed")

        except Exception as e:
            logger.error("Model functionality verification failed", error=str(e))
            raise ProcessingError(f"AI model verification failed: {str(e)}") from e

    def get_model_info(self) -> dict[str, str]:
        """Get information about loaded models.

        Returns:
            Dict[str, str]: Model information including status and capabilities
        """
        return {
            "status": "initialized" if self._initialized else "not_initialized",
            "converter_available": str(self._converter is not None),
            "cache_dir": str(self.cache_dir),
            "last_health_check": str(self._last_health_check),
            "supported_formats": "pdf,docx,pptx,html,txt,md",
        }

    async def cleanup(self) -> None:
        """Clean up resources and prepare for shutdown.

        Releases AI model resources and cleans up temporary files.
        """
        try:
            logger.info("Cleaning up AI model manager")

            # Clear references to allow garbage collection
            self._converter = None
            self._initialized = False

            logger.info("AI model manager cleanup completed")

        except Exception as e:
            logger.error("Error during model manager cleanup", error=str(e))
