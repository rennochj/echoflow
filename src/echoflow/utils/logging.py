"""Structured logging configuration for EchoFlow."""

import logging
import uuid
from contextvars import ContextVar
from typing import Any, Optional

import structlog
from structlog.typing import FilteringBoundLogger

from ..config.settings import settings

# Context variables for correlation IDs
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class CorrelationIDProcessor:
    """Processor to add correlation ID to log records."""

    def __call__(
        self, logger: FilteringBoundLogger, method_name: str, event_dict: dict[str, Any]
    ) -> dict[str, Any]:
        """Add correlation ID to event dictionary."""
        correlation_id = correlation_id_ctx.get()
        if correlation_id:
            event_dict["correlation_id"] = correlation_id
        return event_dict


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set correlation ID in context."""
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    correlation_id_ctx.set(correlation_id)
    return correlation_id


def clear_correlation_id() -> None:
    """Clear correlation ID from context."""
    correlation_id_ctx.set(None)


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID from context."""
    return correlation_id_ctx.get()


def configure_logging() -> None:
    """Configure structured logging for the application."""

    # Configure structlog
    structlog.configure(
        processors=[
            # Add correlation ID to all log records
            CorrelationIDProcessor(),
            # Add timestamp
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            # Format stack info if present
            structlog.processors.StackInfoRenderer(),
            # Format exception info if present
            structlog.dev.ConsoleRenderer()
            if settings.debug
            else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.server.log_level.upper()),
    )


def get_logger(name: str) -> FilteringBoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Application logger
logger = get_logger(__name__)
