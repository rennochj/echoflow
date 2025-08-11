"""Base exception hierarchy for EchoFlow."""

from typing import Any, Optional


class EchoFlowError(Exception):
    """Base exception for all EchoFlow errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize EchoFlowError.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}


class ConfigurationError(EchoFlowError):
    """Configuration-related errors."""

    pass


class ConversionError(EchoFlowError):
    """Document conversion errors."""

    pass


class ValidationError(EchoFlowError):
    """Input validation errors."""

    pass


class ProcessingError(EchoFlowError):
    """Document processing errors."""

    pass


class FileSystemError(EchoFlowError):
    """File system operation errors."""

    pass


class NetworkError(EchoFlowError):
    """Network-related errors."""

    pass


class MCPError(EchoFlowError):
    """MCP protocol errors."""

    pass


class ServerError(EchoFlowError):
    """Server operation errors."""

    pass
