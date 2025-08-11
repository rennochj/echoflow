"""Pytest configuration and fixtures for EchoFlow tests."""

import asyncio
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from mcp.server import Server

from src.echoflow.config.settings import ProcessingConfig, ServerConfig, Settings
from src.echoflow.converters.base import ConversionOptions, ConverterRegistry
from src.echoflow.utils.container import Container
from src.echoflow.utils.logging import configure_logging


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_settings(temp_dir: Path) -> Settings:
    """Create test settings with temporary directories."""
    return Settings(
        app_name="EchoFlow Test",
        version="0.1.0-test",
        debug=True,
        server=ServerConfig(
            host="localhost",
            port=3001,  # Different port for tests
            log_level="DEBUG",
        ),
        processing=ProcessingConfig(
            temp_dir=temp_dir / "processing",
            max_file_size=10 * 1024 * 1024,  # 10MB for tests
            timeout_seconds=60,  # 1 minute for tests
        ),
    )


@pytest.fixture
def container() -> Generator[Container, None, None]:
    """Create a fresh container for each test."""
    test_container = Container()
    yield test_container
    test_container.clear()


@pytest.fixture
def converter_registry() -> ConverterRegistry:
    """Create a fresh converter registry for tests."""
    return ConverterRegistry()


@pytest.fixture
def conversion_options() -> ConversionOptions:
    """Create default conversion options for tests."""
    return ConversionOptions(
        extract_images=True,
        preserve_formatting=True,
        extract_hyperlinks=True,
        extract_metadata=True,
        timeout_seconds=30,  # Shorter timeout for tests
    )


@pytest.fixture
def sample_pdf_path(temp_dir: Path) -> Path:
    """Create a sample PDF file for testing."""
    pdf_path = temp_dir / "sample.pdf"
    # Create a minimal PDF content (just for path testing)
    pdf_path.write_text("This is not a real PDF, just for testing file paths")
    return pdf_path


@pytest.fixture
def sample_docx_path(temp_dir: Path) -> Path:
    """Create a sample DOCX file for testing."""
    docx_path = temp_dir / "sample.docx"
    docx_path.write_text("This is not a real DOCX, just for testing file paths")
    return docx_path


@pytest.fixture
def sample_txt_path(temp_dir: Path) -> Path:
    """Create a sample TXT file for testing."""
    txt_path = temp_dir / "sample.txt"
    txt_path.write_text("This is a sample text file for testing.\nIt has multiple lines.")
    return txt_path


@pytest.fixture
def sample_files(temp_dir: Path) -> dict[str, Path]:
    """Create multiple sample files for testing."""
    files = {}

    # Create various file types
    file_contents = {
        "sample.pdf": "Fake PDF content",
        "sample.docx": "Fake DOCX content",
        "sample.pptx": "Fake PPTX content",
        "sample.txt": "Real text content for testing",
        "sample.html": "<html><body><h1>Test HTML</h1></body></html>",
        "sample.md": "# Test Markdown\n\nThis is a test.",
    }

    for filename, content in file_contents.items():
        file_path = temp_dir / filename
        file_path.write_text(content)
        files[filename] = file_path

    return files


@pytest.fixture
def mock_mcp_server() -> Generator[MagicMock, None, None]:
    """Create a mock MCP server for testing."""
    mock_server = MagicMock(spec=Server)
    mock_server.list_tools = AsyncMock()
    mock_server.call_tool = AsyncMock()
    mock_server.list_resources = AsyncMock()
    yield mock_server


@pytest.fixture(autouse=True)
def configure_test_logging() -> None:
    """Configure logging for tests."""
    configure_logging()


@pytest.fixture
def mock_conversion_result():
    """Create a mock conversion result for testing."""
    from src.echoflow.converters.base import ConversionMetadata, ConversionResult

    return ConversionResult(
        success=True,
        markdown_content="# Test Document\n\nThis is converted content.",
        metadata=ConversionMetadata(
            title="Test Document",
            author="Test Author",
            page_count=1,
        ),
        processing_time_seconds=0.5,
        converter_used="TestConverter",
    )


@pytest_asyncio.fixture
async def async_temp_dir() -> AsyncGenerator[Path, None]:
    """Create an async temporary directory fixture."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


# Pytest markers for different test types
pytest.mark.unit = pytest.mark.mark("unit")
pytest.mark.integration = pytest.mark.mark("integration")
pytest.mark.slow = pytest.mark.mark("slow")


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    """Modify test items to add default markers."""
    for item in items:
        # Add 'unit' marker to all tests by default unless they have other markers
        if not any(marker.name in ["integration", "slow"] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
