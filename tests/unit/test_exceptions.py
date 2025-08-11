"""Unit tests for custom exceptions."""

from src.echoflow.exceptions.base import (
    ConfigurationError,
    ConversionError,
    EchoFlowError,
    FileSystemError,
    MCPError,
    NetworkError,
    ProcessingError,
    ServerError,
    ValidationError,
)


class TestEchoFlowError:
    """Test base EchoFlowError class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = EchoFlowError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.context == {}

    def test_error_with_code_and_context(self):
        """Test error with code and context."""
        context = {"file": "test.pdf", "line": 42}
        error = EchoFlowError("Test error", error_code="TEST_ERROR", context=context)

        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.context == context


class TestSpecificErrors:
    """Test specific error types."""

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Invalid config")

        assert isinstance(error, EchoFlowError)
        assert str(error) == "Invalid config"

    def test_conversion_error(self):
        """Test ConversionError."""
        error = ConversionError("Conversion failed")

        assert isinstance(error, EchoFlowError)
        assert str(error) == "Conversion failed"

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid input")

        assert isinstance(error, EchoFlowError)
        assert str(error) == "Invalid input"

    def test_processing_error(self):
        """Test ProcessingError."""
        error = ProcessingError("Processing failed")

        assert isinstance(error, EchoFlowError)
        assert str(error) == "Processing failed"

    def test_filesystem_error(self):
        """Test FileSystemError."""
        error = FileSystemError("File not found")

        assert isinstance(error, EchoFlowError)
        assert str(error) == "File not found"

    def test_network_error(self):
        """Test NetworkError."""
        error = NetworkError("Connection failed")

        assert isinstance(error, EchoFlowError)
        assert str(error) == "Connection failed"

    def test_mcp_error(self):
        """Test MCPError."""
        error = MCPError("MCP protocol error")

        assert isinstance(error, EchoFlowError)
        assert str(error) == "MCP protocol error"

    def test_server_error(self):
        """Test ServerError."""
        error = ServerError("Server startup failed")

        assert isinstance(error, EchoFlowError)
        assert str(error) == "Server startup failed"
