"""Health check utilities for EchoFlow server."""

import asyncio
import sys
from typing import Any

from ..config.settings import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


async def health_check() -> bool:
    """Perform a comprehensive health check of the server.

    Returns:
        True if all health checks pass, False otherwise.
    """
    try:
        health_status = await get_health_status()

        # Check if all components are healthy (allowing not_initialized as acceptable)
        overall_healthy = health_status["status"] in ["healthy", "degraded"]
        for component, status in health_status["components"].items():
            if status not in ["healthy", "not_initialized"]:
                logger.warning(f"Component {component} is not healthy: {status}")
                overall_healthy = False
            elif status == "not_initialized":
                logger.info(f"Component {component} is not yet initialized: {status}")

        if overall_healthy:
            logger.info("All health checks passed")
        else:
            logger.error("Some health checks failed", status=health_status)

        return overall_healthy

    except Exception as e:
        logger.error("Health check execution failed", error=str(e))
        return False


async def get_health_status() -> dict[str, Any]:
    """Get detailed health status of all components.

    Returns:
        Dictionary containing health status information.
    """
    try:
        # Check basic server components
        components_status = {
            "server": "healthy",
            "config": _check_config_health(),
            "logging": _check_logging_health(),
            "filesystem": _check_filesystem_health(),
            "converters": "not_initialized",  # Will be updated in Phase 2
            "ai_models": await _check_ai_models_health(),
        }

        # Determine overall status
        overall_status = "healthy"
        for status in components_status.values():
            if status == "unhealthy":
                overall_status = "unhealthy"
                break
            elif status == "degraded":
                overall_status = "degraded"

        return {
            "status": overall_status,
            "version": settings.version,
            "app_name": settings.app_name,
            "components": components_status,
            "timestamp": "N/A",  # TODO: Add proper timestamp
            "uptime": "N/A",  # TODO: Add uptime tracking
        }

    except Exception as e:
        logger.error("Failed to get health status", error=str(e))
        return {"status": "error", "error": str(e), "components": {}}


def _check_config_health() -> str:
    """Check configuration health."""
    try:
        # Verify settings are accessible
        _ = settings.app_name
        _ = settings.version
        _ = settings.processing.temp_dir
        return "healthy"
    except Exception:
        return "unhealthy"


def _check_logging_health() -> str:
    """Check logging system health."""
    try:
        # Test logger functionality
        logger.debug("Health check: Testing logger")
        return "healthy"
    except Exception:
        return "unhealthy"


def _check_filesystem_health() -> str:
    """Check filesystem access health."""
    try:
        # Check if temp directory is accessible
        temp_dir = settings.processing.temp_dir
        if not temp_dir.exists():
            temp_dir.mkdir(parents=True, exist_ok=True)

        # Try to write a test file
        test_file = temp_dir / "health_check.tmp"
        test_file.write_text("health_check")
        test_file.unlink()

        return "healthy"
    except Exception:
        return "unhealthy"


async def _check_ai_models_health() -> str:
    """Check AI model availability and performance.

    Returns:
        String indicating health status: "healthy", "degraded", or "unhealthy"
    """
    try:
        from ..ai.model_manager import ModelManager

        # Create a model manager instance for health checking
        manager = ModelManager()

        # Check if models can be initialized and are healthy
        if await manager.health_check():
            return "healthy"
        else:
            return "degraded"

    except ImportError:
        # AI models not available (expected in early phases)
        return "not_initialized"
    except Exception as e:
        logger.warning("AI model health check failed", error=str(e))
        return "unhealthy"


if __name__ == "__main__":
    """Allow health check to be run directly."""

    async def main() -> None:
        success = await health_check()
        sys.exit(0 if success else 1)

    asyncio.run(main())
