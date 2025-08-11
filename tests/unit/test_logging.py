"""Unit tests for logging utilities."""

from src.echoflow.utils.logging import (
    CorrelationIDProcessor,
    clear_correlation_id,
    generate_correlation_id,
    get_correlation_id,
    get_logger,
    set_correlation_id,
)


class TestCorrelationID:
    """Test correlation ID functionality."""

    def test_generate_correlation_id(self):
        """Test correlation ID generation."""
        id1 = generate_correlation_id()
        id2 = generate_correlation_id()

        assert id1 != id2
        assert len(id1) > 0
        assert len(id2) > 0

    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        test_id = "test-correlation-id"

        set_correlation_id(test_id)
        retrieved_id = get_correlation_id()

        assert retrieved_id == test_id

    def test_set_correlation_id_auto_generate(self):
        """Test auto-generating correlation ID."""
        generated_id = set_correlation_id()
        retrieved_id = get_correlation_id()

        assert retrieved_id == generated_id
        assert len(generated_id) > 0

    def test_get_correlation_id_none(self):
        """Test getting correlation ID when none is set."""
        # Clear any existing correlation ID
        clear_correlation_id()

        retrieved_id = get_correlation_id()
        assert retrieved_id is None


class TestCorrelationIDProcessor:
    """Test CorrelationIDProcessor."""

    def test_processor_with_correlation_id(self):
        """Test processor adds correlation ID when present."""
        processor = CorrelationIDProcessor()
        set_correlation_id("test-id")

        event_dict = {"message": "test message"}
        result = processor(None, "info", event_dict)

        assert result["correlation_id"] == "test-id"
        assert result["message"] == "test message"

    def test_processor_without_correlation_id(self):
        """Test processor when no correlation ID is set."""
        processor = CorrelationIDProcessor()
        clear_correlation_id()

        event_dict = {"message": "test message"}
        result = processor(None, "info", event_dict)

        assert "correlation_id" not in result
        assert result["message"] == "test message"


class TestLogger:
    """Test logger functionality."""

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_module")

        assert logger is not None
        # Test that we can call logging methods without error
        logger.info("Test log message")
