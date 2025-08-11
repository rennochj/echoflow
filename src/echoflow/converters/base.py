"""Abstract base classes for document converters."""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol

from ..exceptions.base import ConversionError, ValidationError


@dataclass
class ConversionMetadata:
    """Metadata extracted from document conversion."""

    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    language: Optional[str] = None
    keywords: list[str] = field(default_factory=list)
    custom_properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedImage:
    """Information about an extracted image."""

    filename: str
    format: str  # png, jpg, etc.
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: Optional[int] = None
    page_number: Optional[int] = None
    position: Optional[dict[str, float]] = None  # x, y, width, height


@dataclass
class ConversionResult:
    """Result of a document conversion operation."""

    success: bool
    markdown_content: str
    metadata: ConversionMetadata
    extracted_images: list[ExtractedImage] = field(default_factory=list)
    hyperlinks: list[dict[str, str]] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    converter_used: str = ""
    error_message: Optional[str] = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class ConversionOptions:
    """Options for document conversion."""

    extract_images: bool = True
    preserve_formatting: bool = True
    extract_hyperlinks: bool = True
    extract_metadata: bool = True
    extract_tables: bool = True
    output_format: str = "markdown"
    image_format: str = "png"
    max_image_size: int = 5 * 1024 * 1024  # 5MB
    timeout_seconds: int = 300  # 5 minutes


class ConverterProtocol(Protocol):
    """Protocol for document converters."""

    @property
    def name(self) -> str:
        """Return the name of the converter."""
        ...

    @property
    def supported_formats(self) -> list[str]:
        """Return list of supported file extensions."""
        ...

    def can_convert(self, file_path: Path) -> bool:
        """Check if this converter can handle the given file."""
        ...

    async def convert(
        self, file_path: Path, output_dir: Path, options: ConversionOptions
    ) -> ConversionResult:
        """Convert a document to markdown."""
        ...


class BaseConverter(ABC):
    """Abstract base class for all document converters."""

    def __init__(self, name: str, supported_formats: list[str]) -> None:
        """Initialize the converter.

        Args:
            name: Human-readable name of the converter
            supported_formats: List of supported file extensions (without dots)
        """
        self._name = name
        self._supported_formats = [fmt.lower() for fmt in supported_formats]

    @property
    def name(self) -> str:
        """Return the name of the converter."""
        return self._name

    @property
    def supported_formats(self) -> list[str]:
        """Return list of supported file extensions."""
        return self._supported_formats.copy()

    def can_convert(self, file_path: Path) -> bool:
        """Check if this converter can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            True if this converter supports the file format
        """
        if not file_path.exists():
            return False

        suffix = file_path.suffix.lower().lstrip(".")
        return suffix in self._supported_formats

    def validate_input(self, file_path: Path, options: ConversionOptions) -> None:
        """Validate input parameters.

        Args:
            file_path: Path to the file to convert
            options: Conversion options

        Raises:
            ValidationError: If input is invalid
        """
        if not file_path.exists():
            raise ValidationError(f"File does not exist: {file_path}")

        if not file_path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")

        if not self.can_convert(file_path):
            raise ValidationError(f"Unsupported file format: {file_path.suffix}")

        # Check file size
        file_size = file_path.stat().st_size
        max_size = 100 * 1024 * 1024  # 100MB default limit
        if file_size > max_size:
            raise ValidationError(f"File too large: {file_size} bytes (max: {max_size})")

    @abstractmethod
    async def _convert_document(
        self, file_path: Path, output_dir: Path, options: ConversionOptions
    ) -> ConversionResult:
        """Convert a document to markdown.

        This method must be implemented by subclasses.

        Args:
            file_path: Path to the document to convert
            output_dir: Directory to save converted files
            options: Conversion options

        Returns:
            ConversionResult with the conversion outcome
        """
        pass

    async def convert(
        self, file_path: Path, output_dir: Path, options: ConversionOptions
    ) -> ConversionResult:
        """Convert a document to markdown with validation and error handling.

        Args:
            file_path: Path to the document to convert
            output_dir: Directory to save converted files
            options: Conversion options

        Returns:
            ConversionResult with the conversion outcome
        """
        import time

        start_time = time.time()

        try:
            # Validate input
            self.validate_input(file_path, options)

            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Perform conversion
            result = await asyncio.wait_for(
                self._convert_document(file_path, output_dir, options),
                timeout=options.timeout_seconds,
            )

            # Update timing and converter info
            result.processing_time_seconds = time.time() - start_time
            result.converter_used = self.name

            return result

        except asyncio.TimeoutError:
            error_msg = f"Conversion timed out after {options.timeout_seconds} seconds"
            return ConversionResult(
                success=False,
                markdown_content="",
                metadata=ConversionMetadata(),
                processing_time_seconds=time.time() - start_time,
                converter_used=self.name,
                error_message=error_msg,
            )
        except ValidationError as e:
            return ConversionResult(
                success=False,
                markdown_content="",
                metadata=ConversionMetadata(),
                processing_time_seconds=time.time() - start_time,
                converter_used=self.name,
                error_message=str(e),
            )
        except ConversionError as e:
            return ConversionResult(
                success=False,
                markdown_content="",
                metadata=ConversionMetadata(),
                processing_time_seconds=time.time() - start_time,
                converter_used=self.name,
                error_message=str(e),
            )
        except Exception as e:
            error_msg = f"Unexpected error during conversion: {str(e)}"
            return ConversionResult(
                success=False,
                markdown_content="",
                metadata=ConversionMetadata(),
                processing_time_seconds=time.time() - start_time,
                converter_used=self.name,
                error_message=error_msg,
            )


class ConverterRegistry:
    """Registry for managing document converters."""

    def __init__(self) -> None:
        """Initialize the converter registry."""
        self._converters: list[ConverterProtocol] = []

    def register(self, converter: ConverterProtocol) -> None:
        """Register a converter.

        Args:
            converter: Converter instance to register
        """
        self._converters.append(converter)

    def get_converter(self, file_path: Path) -> Optional[ConverterProtocol]:
        """Get the best converter for a file.

        Args:
            file_path: Path to the file

        Returns:
            Converter instance or None if no suitable converter found
        """
        for converter in self._converters:
            if converter.can_convert(file_path):
                return converter
        return None

    def get_converters_for_format(self, file_extension: str) -> list[ConverterProtocol]:
        """Get all converters that support a file format.

        Args:
            file_extension: File extension (with or without dot)

        Returns:
            List of converters that support the format
        """
        extension = file_extension.lower().lstrip(".")
        return [
            converter for converter in self._converters if extension in converter.supported_formats
        ]

    def list_supported_formats(self) -> list[str]:
        """Get all supported file formats.

        Returns:
            List of supported file extensions
        """
        formats = set()
        for converter in self._converters:
            formats.update(converter.supported_formats)
        return sorted(formats)


# Global converter registry instance
converter_registry = ConverterRegistry()
