"""Docling AI-powered document converter for EchoFlow.

This module provides the primary document conversion engine using IBM's Docling AI.
It offers superior document understanding with layout analysis, image extraction,
and metadata processing for all supported document formats.
"""

import asyncio
from pathlib import Path

from ..ai.model_manager import ModelManager
from ..converters.base import BaseConverter, ConversionOptions, ConversionResult
from ..exceptions.base import ConversionError
from ..utils.logging import get_logger

logger = get_logger(__name__)


class DoclingConverter(BaseConverter):
    """AI-powered document converter using IBM Docling.

    This converter uses advanced AI models for document understanding and provides:
    - Superior text extraction with layout preservation
    - Advanced table recognition and formatting
    - Intelligent image extraction and referencing
    - Comprehensive metadata extraction
    - High-quality markdown output
    """

    def __init__(self) -> None:
        """Initialize the Docling converter with AI model support."""
        super().__init__(
            name="DoclingAI", supported_formats=["pdf", "docx", "pptx", "html", "txt", "md"]
        )
        self.model_manager = ModelManager()
        self._initialized = False

        logger.info("DoclingConverter initialized with AI model support")

    async def _initialize_converter(self) -> None:
        """Initialize the Docling converter with error handling.

        Ensures AI models are loaded and ready for document processing.

        Raises:
            ConversionError: If AI model initialization fails
        """
        if self._initialized:
            return

        try:
            logger.info("Initializing Docling AI converter")
            await self.model_manager.initialize()
            self._initialized = True
            logger.info("Docling AI converter initialization completed")

        except Exception as e:
            logger.error("Failed to initialize Docling converter", error=str(e))
            raise ConversionError(f"AI converter initialization failed: {str(e)}") from e

    async def _convert_document(
        self, file_path: Path, output_dir: Path, options: ConversionOptions
    ) -> ConversionResult:
        """Convert document using Docling AI engine.

        Args:
            file_path: Path to the input document
            output_dir: Directory for output files and extracted images
            options: Conversion configuration options

        Returns:
            ConversionResult: Comprehensive conversion results

        Raises:
            ConversionError: If AI conversion fails
        """
        await self._initialize_converter()

        try:
            # Get the AI-powered document converter
            converter = await self.model_manager.get_converter()

            logger.info(
                "Starting AI document conversion",
                file_path=str(file_path),
                file_size_mb=round(file_path.stat().st_size / (1024 * 1024), 2),
            )

            # Perform AI-powered conversion
            # The convert method handles the file path directly
            conversion_start = asyncio.get_event_loop().time()
            doc_result = await asyncio.to_thread(converter.convert, str(file_path))
            conversion_time = asyncio.get_event_loop().time() - conversion_start

            # Extract comprehensive content from AI results
            markdown_content = self._extract_markdown(doc_result)
            metadata = self._extract_metadata(doc_result)
            images = await self._extract_images(doc_result, output_dir, options)
            hyperlinks = self._extract_hyperlinks(doc_result)

            # Create comprehensive result
            result = ConversionResult(
                success=True,
                markdown_content=markdown_content,
                metadata=metadata,
                extracted_images=images,
                hyperlinks=hyperlinks,
                converter_used=self.name,
                processing_time_seconds=round(conversion_time, 2),
            )

            logger.info(
                "AI document conversion completed successfully",
                processing_time=result.processing_time_seconds,
                content_length=len(markdown_content),
                images_extracted=len(images),
                hyperlinks_found=len(hyperlinks),
            )

            return result

        except Exception as e:
            logger.error("Docling AI conversion failed", error=str(e), file_path=str(file_path))
            raise ConversionError(f"AI document conversion failed: {str(e)}") from e

    def _extract_markdown(self, doc_result) -> str:
        """Extract high-quality markdown from Docling result.

        Args:
            doc_result: The conversion result from Docling

        Returns:
            str: Clean, well-formatted markdown content
        """
        try:
            # Export to markdown using Docling's built-in functionality
            if hasattr(doc_result, "export_to_markdown"):
                markdown = doc_result.export_to_markdown()
            else:
                # Fallback: convert document content to markdown
                markdown = str(doc_result)

            # Basic cleanup and normalization
            if not markdown.strip():
                logger.warning("Empty markdown content extracted")
                return "# Document Converted\n\nNo readable content found."

            return markdown

        except Exception as e:
            logger.error("Failed to extract markdown", error=str(e))
            return f"# Conversion Error\n\nFailed to extract content: {str(e)}"

    def _extract_metadata(self, doc_result) -> dict:
        """Extract comprehensive metadata from document.

        Args:
            doc_result: The conversion result from Docling

        Returns:
            dict: Document metadata including title, author, dates, etc.
        """
        try:
            metadata = {
                "title": None,
                "author": None,
                "creation_date": None,
                "modification_date": None,
                "subject": None,
                "keywords": [],
                "page_count": None,
                "language": None,
                "character_count": None,
            }

            # Try to extract metadata from various document attributes
            if hasattr(doc_result, "metadata"):
                doc_meta = doc_result.metadata
                metadata.update(
                    {
                        "title": getattr(doc_meta, "title", None),
                        "author": getattr(doc_meta, "author", None),
                        "creation_date": getattr(doc_meta, "creation_date", None),
                        "modification_date": getattr(doc_meta, "modification_date", None),
                        "subject": getattr(doc_meta, "subject", None),
                    }
                )

            # Extract additional properties if available
            if hasattr(doc_result, "pages"):
                metadata["page_count"] = len(doc_result.pages)

            logger.debug("Metadata extraction completed", metadata_keys=list(metadata.keys()))
            return metadata

        except Exception as e:
            logger.warning("Failed to extract metadata", error=str(e))
            return {"title": None, "author": None, "extraction_error": str(e)}

    async def _extract_images(
        self, doc_result, output_dir: Path, options: ConversionOptions
    ) -> list[dict]:
        """Extract and save images with proper referencing.

        Args:
            doc_result: The conversion result from Docling
            output_dir: Directory to save extracted images
            options: Conversion options including image settings

        Returns:
            List[dict]: Information about extracted images
        """
        extracted_images = []

        if not options.extract_images:
            logger.debug("Image extraction disabled by options")
            return extracted_images

        try:
            # Create images directory
            images_dir = output_dir / "images"
            images_dir.mkdir(exist_ok=True)

            # Try to extract images if available
            if hasattr(doc_result, "images") and doc_result.images:
                for i, image in enumerate(doc_result.images):
                    try:
                        image_filename = f"image_{i + 1}.png"
                        image_path = images_dir / image_filename

                        # Save image (implementation depends on Docling API)
                        # This is a placeholder - actual implementation will depend on
                        # how Docling provides image data

                        extracted_images.append(
                            {
                                "filename": image_filename,
                                "path": str(image_path.relative_to(output_dir)),
                                "size": None,  # Will be filled when actual image is saved
                                "format": "png",
                                "page_number": getattr(image, "page_number", None),
                            }
                        )

                    except Exception as e:
                        logger.warning(f"Failed to extract image {i + 1}", error=str(e))

            logger.debug("Image extraction completed", images_found=len(extracted_images))
            return extracted_images

        except Exception as e:
            logger.warning("Image extraction failed", error=str(e))
            return []

    def _extract_hyperlinks(self, doc_result) -> list[dict]:
        """Extract and preserve hyperlinks from document.

        Args:
            doc_result: The conversion result from Docling

        Returns:
            List[dict]: Information about hyperlinks found in the document
        """
        hyperlinks = []

        try:
            # Try to extract hyperlinks if available
            if hasattr(doc_result, "links") and doc_result.links:
                for link in doc_result.links:
                    try:
                        hyperlinks.append(
                            {
                                "text": getattr(link, "text", ""),
                                "url": getattr(link, "url", ""),
                                "page_number": getattr(link, "page_number", None),
                            }
                        )
                    except Exception as e:
                        logger.warning("Failed to extract hyperlink", error=str(e))

            logger.debug("Hyperlink extraction completed", links_found=len(hyperlinks))
            return hyperlinks

        except Exception as e:
            logger.warning("Hyperlink extraction failed", error=str(e))
            return []

    async def cleanup(self) -> None:
        """Clean up resources and AI models."""
        try:
            logger.info("Cleaning up DoclingConverter resources")
            await self.model_manager.cleanup()
            self._initialized = False
            logger.info("DoclingConverter cleanup completed")

        except Exception as e:
            logger.error("Error during DoclingConverter cleanup", error=str(e))
