"""Unit tests for converter base classes."""

from pathlib import Path

import pytest

from src.echoflow.converters.base import (
    BaseConverter,
    ConversionMetadata,
    ConversionOptions,
    ConversionResult,
    ConverterRegistry,
    ExtractedImage,
)
from src.echoflow.exceptions.base import ValidationError


class MockConverter(BaseConverter):
    """Mock converter for testing."""

    def __init__(self):
        super().__init__("MockConverter", ["pdf", "txt"])

    async def _convert_document(
        self, file_path: Path, output_dir: Path, options: ConversionOptions
    ) -> ConversionResult:
        return ConversionResult(
            success=True,
            markdown_content="# Mock Content",
            metadata=ConversionMetadata(title="Mock Document"),
            converter_used=self.name,
        )


class TestConversionMetadata:
    """Test ConversionMetadata dataclass."""

    def test_default_metadata(self):
        """Test default metadata creation."""
        metadata = ConversionMetadata()

        assert metadata.title is None
        assert metadata.author is None
        assert metadata.keywords == []
        assert metadata.custom_properties == {}

    def test_metadata_with_values(self):
        """Test metadata with specific values."""
        metadata = ConversionMetadata(
            title="Test Document",
            author="Test Author",
            page_count=5,
            keywords=["test", "document"],
            custom_properties={"subject": "Testing"},
        )

        assert metadata.title == "Test Document"
        assert metadata.author == "Test Author"
        assert metadata.page_count == 5
        assert metadata.keywords == ["test", "document"]
        assert metadata.custom_properties == {"subject": "Testing"}


class TestExtractedImage:
    """Test ExtractedImage dataclass."""

    def test_basic_image(self):
        """Test basic image creation."""
        image = ExtractedImage(filename="test.png", format="png")

        assert image.filename == "test.png"
        assert image.format == "png"
        assert image.width is None
        assert image.height is None


class TestConversionResult:
    """Test ConversionResult dataclass."""

    def test_successful_result(self):
        """Test successful conversion result."""
        result = ConversionResult(
            success=True,
            markdown_content="# Test",
            metadata=ConversionMetadata(title="Test"),
            converter_used="TestConverter",
        )

        assert result.success is True
        assert result.markdown_content == "# Test"
        assert result.metadata.title == "Test"
        assert result.converter_used == "TestConverter"
        assert result.extracted_images == []
        assert result.error_message is None


class TestConversionOptions:
    """Test ConversionOptions dataclass."""

    def test_default_options(self):
        """Test default conversion options."""
        options = ConversionOptions()

        assert options.extract_images is True
        assert options.preserve_formatting is True
        assert options.extract_hyperlinks is True
        assert options.output_format == "markdown"
        assert options.timeout_seconds == 300


class TestBaseConverter:
    """Test BaseConverter abstract class."""

    def test_converter_properties(self):
        """Test converter basic properties."""
        converter = MockConverter()

        assert converter.name == "MockConverter"
        assert converter.supported_formats == ["pdf", "txt"]

    def test_can_convert_valid_format(self, sample_pdf_path):
        """Test can_convert with supported format."""
        converter = MockConverter()

        assert converter.can_convert(sample_pdf_path) is True

    def test_can_convert_invalid_format(self, temp_dir):
        """Test can_convert with unsupported format."""
        converter = MockConverter()
        docx_path = temp_dir / "test.docx"
        docx_path.write_text("test")

        assert converter.can_convert(docx_path) is False

    def test_can_convert_nonexistent_file(self, temp_dir):
        """Test can_convert with nonexistent file."""
        converter = MockConverter()
        nonexistent = temp_dir / "nonexistent.pdf"

        assert converter.can_convert(nonexistent) is False

    def test_validate_input_success(self, sample_txt_path):
        """Test successful input validation."""
        converter = MockConverter()
        options = ConversionOptions()

        # Should not raise
        converter.validate_input(sample_txt_path, options)

    def test_validate_input_file_not_exists(self, temp_dir):
        """Test validation with non-existent file."""
        converter = MockConverter()
        options = ConversionOptions()
        nonexistent = temp_dir / "nonexistent.pdf"

        with pytest.raises(ValidationError, match="File does not exist"):
            converter.validate_input(nonexistent, options)

    def test_validate_input_unsupported_format(self, temp_dir):
        """Test validation with unsupported format."""
        converter = MockConverter()
        options = ConversionOptions()
        unsupported = temp_dir / "test.docx"
        unsupported.write_text("test")

        with pytest.raises(ValidationError, match="Unsupported file format"):
            converter.validate_input(unsupported, options)

    @pytest.mark.asyncio
    async def test_convert_success(self, sample_txt_path, temp_dir):
        """Test successful conversion."""
        converter = MockConverter()
        options = ConversionOptions()

        result = await converter.convert(sample_txt_path, temp_dir, options)

        assert result.success is True
        assert result.markdown_content == "# Mock Content"
        assert result.converter_used == "MockConverter"
        assert result.processing_time_seconds >= 0

    @pytest.mark.asyncio
    async def test_convert_validation_error(self, temp_dir):
        """Test conversion with validation error."""
        converter = MockConverter()
        options = ConversionOptions()
        nonexistent = temp_dir / "nonexistent.pdf"

        result = await converter.convert(nonexistent, temp_dir, options)

        assert result.success is False
        assert "File does not exist" in result.error_message
        assert result.converter_used == "MockConverter"


class TestConverterRegistry:
    """Test ConverterRegistry class."""

    def test_register_converter(self):
        """Test registering a converter."""
        registry = ConverterRegistry()
        converter = MockConverter()

        registry.register(converter)

        assert len(registry._converters) == 1
        assert registry._converters[0] is converter

    def test_get_converter_success(self, sample_txt_path):
        """Test getting converter for supported file."""
        registry = ConverterRegistry()
        converter = MockConverter()
        registry.register(converter)

        result = registry.get_converter(sample_txt_path)

        assert result is converter

    def test_get_converter_not_found(self, temp_dir):
        """Test getting converter for unsupported file."""
        registry = ConverterRegistry()
        converter = MockConverter()
        registry.register(converter)

        unsupported = temp_dir / "test.docx"
        unsupported.write_text("test")

        result = registry.get_converter(unsupported)

        assert result is None

    def test_get_converters_for_format(self):
        """Test getting converters by format."""
        registry = ConverterRegistry()
        converter = MockConverter()
        registry.register(converter)

        pdf_converters = registry.get_converters_for_format("pdf")
        txt_converters = registry.get_converters_for_format(".txt")
        docx_converters = registry.get_converters_for_format("docx")

        assert len(pdf_converters) == 1
        assert pdf_converters[0] is converter
        assert len(txt_converters) == 1
        assert len(docx_converters) == 0

    def test_list_supported_formats(self):
        """Test listing all supported formats."""
        registry = ConverterRegistry()
        converter1 = MockConverter()  # pdf, txt
        registry.register(converter1)

        formats = registry.list_supported_formats()

        assert sorted(formats) == ["pdf", "txt"]
