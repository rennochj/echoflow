"""Main MCP server entry point for EchoFlow."""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    Tool,
)

from ..config.settings import settings
from ..exceptions.base import EchoFlowError, MCPError, ServerError
from ..utils.logging import configure_logging, get_logger, set_correlation_id

# Initialize logging
configure_logging()
logger = get_logger(__name__)

# Initialize MCP server
app = Server("echoflow")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    correlation_id = set_correlation_id()
    logger.info("Listing available MCP tools", correlation_id=correlation_id)

    try:
        tools = [
            Tool(
                name="convert_document",
                description="Convert a single document to markdown format",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the document to convert",
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for converted files",
                            "default": "./output",
                        },
                        "extract_images": {
                            "type": "boolean",
                            "description": "Whether to extract images from the document",
                            "default": True,
                        },
                        "preserve_metadata": {
                            "type": "boolean",
                            "description": "Whether to preserve document metadata",
                            "default": True,
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            Tool(
                name="convert_directory",
                description="Convert all supported documents in a directory to markdown",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "input_dir": {
                            "type": "string",
                            "description": "Directory containing documents to convert",
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Output directory for converted files",
                            "default": "./output",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Whether to process subdirectories recursively",
                            "default": False,
                        },
                        "file_filter": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File extensions to include (e.g., ['pdf', 'docx'])",
                            "default": ["pdf", "docx", "pptx", "txt", "html", "md"],
                        },
                        "create_zip": {
                            "type": "boolean",
                            "description": "Whether to create a ZIP archive of outputs",
                            "default": False,
                        },
                    },
                    "required": ["input_dir"],
                },
            ),
            Tool(
                name="list_supported_formats",
                description="List all supported document formats and their capabilities",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_conversion_status",
                description="Get the status of a conversion operation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation_id": {
                            "type": "string",
                            "description": "ID of the conversion operation to check",
                        }
                    },
                    "required": ["operation_id"],
                },
            ),
            Tool(
                name="health_check",
                description="Check the health status of the EchoFlow server",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

        logger.info(
            "Successfully listed MCP tools", tool_count=len(tools), correlation_id=correlation_id
        )
        return tools

    except Exception as e:
        logger.error("Failed to list MCP tools", error=str(e), correlation_id=correlation_id)
        raise MCPError(f"Failed to list tools: {str(e)}", error_code="TOOL_LIST_ERROR") from e


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle MCP tool calls."""
    correlation_id = set_correlation_id()
    logger.info(
        "Calling MCP tool", tool_name=name, arguments=arguments, correlation_id=correlation_id
    )

    try:
        if name == "health_check":
            return await handle_health_check()
        elif name == "list_supported_formats":
            return await handle_list_supported_formats()
        elif name == "convert_document":
            return await handle_convert_document(arguments)
        elif name == "convert_directory":
            return await handle_convert_directory(arguments)
        elif name == "get_conversion_status":
            return await handle_get_conversion_status(arguments)
        else:
            raise MCPError(f"Unknown tool: {name}", error_code="UNKNOWN_TOOL")

    except EchoFlowError:
        # Re-raise EchoFlow errors as-is
        raise
    except Exception as e:
        logger.error(
            "Tool call failed", tool_name=name, error=str(e), correlation_id=correlation_id
        )
        raise MCPError(f"Tool execution failed: {str(e)}", error_code="TOOL_EXECUTION_ERROR") from e


async def handle_health_check() -> list[TextContent]:
    """Handle health check requests."""
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "version": settings.version,
            "app_name": settings.app_name,
            "uptime": "N/A",  # TODO: Implement uptime tracking
            "components": {
                "server": "healthy",
                "config": "healthy",
                "logging": "healthy",
                "converters": "not_initialized",  # Will be updated in Phase 2
            },
        }

        logger.info("Health check completed successfully", status=health_status)
        return [TextContent(type="text", text=f"Health Status: {health_status}")]

    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise ServerError(f"Health check failed: {str(e)}", error_code="HEALTH_CHECK_ERROR") from e


async def handle_list_supported_formats() -> list[TextContent]:
    """Handle list supported formats requests."""
    try:
        formats = {
            "supported_formats": settings.processing.supported_formats,
            "capabilities": {
                "pdf": {
                    "text_extraction": True,
                    "image_extraction": True,
                    "metadata_extraction": True,
                    "table_extraction": True,
                    "ai_powered": True,
                },
                "docx": {
                    "text_extraction": True,
                    "image_extraction": True,
                    "metadata_extraction": True,
                    "table_extraction": True,
                    "ai_powered": True,
                },
                "pptx": {
                    "text_extraction": True,
                    "image_extraction": True,
                    "metadata_extraction": True,
                    "ai_powered": True,
                },
                "txt": {
                    "text_extraction": True,
                    "image_extraction": False,
                    "metadata_extraction": False,
                    "ai_powered": False,
                },
                "html": {
                    "text_extraction": True,
                    "image_extraction": True,
                    "metadata_extraction": True,
                    "ai_powered": True,
                },
                "md": {
                    "text_extraction": True,
                    "image_extraction": True,
                    "metadata_extraction": True,
                    "ai_powered": False,
                },
            },
        }

        return [TextContent(type="text", text=f"Supported Formats: {formats}")]

    except Exception as e:
        logger.error("Failed to list supported formats", error=str(e))
        raise ServerError(f"Failed to list formats: {str(e)}", error_code="FORMAT_LIST_ERROR") from e


async def handle_convert_document(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle single document conversion (placeholder for Phase 2)."""
    file_path = arguments.get("file_path")

    # Validation
    if not file_path:
        raise MCPError("file_path is required", error_code="MISSING_PARAMETER")

    # TODO: Implement actual conversion in Phase 2
    logger.info("Document conversion requested (not yet implemented)", file_path=file_path)

    return [
        TextContent(
            type="text",
            text=f"Document conversion for '{file_path}' will be implemented in Phase 2",
        )
    ]


async def handle_convert_directory(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle directory conversion (placeholder for Phase 3)."""
    input_dir = arguments.get("input_dir")

    # Validation
    if not input_dir:
        raise MCPError("input_dir is required", error_code="MISSING_PARAMETER")

    # TODO: Implement batch processing in Phase 3
    logger.info("Directory conversion requested (not yet implemented)", input_dir=input_dir)

    return [
        TextContent(
            type="text",
            text=f"Directory conversion for '{input_dir}' will be implemented in Phase 3",
        )
    ]


async def handle_get_conversion_status(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle conversion status requests (placeholder for Phase 3)."""
    operation_id = arguments.get("operation_id")

    # Validation
    if not operation_id:
        raise MCPError("operation_id is required", error_code="MISSING_PARAMETER")

    # TODO: Implement status tracking in Phase 3
    logger.info("Status check requested (not yet implemented)", operation_id=operation_id)

    return [
        TextContent(
            type="text",
            text=f"Status tracking for operation '{operation_id}' will be implemented in Phase 3",
        )
    ]


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    correlation_id = set_correlation_id()
    logger.info("Listing available resources", correlation_id=correlation_id)

    try:
        # TODO: Implement resource listing in later phases
        resources: list[Resource] = []

        logger.info(
            "Successfully listed resources",
            resource_count=len(resources),
            correlation_id=correlation_id,
        )
        return resources

    except Exception as e:
        logger.error("Failed to list resources", error=str(e), correlation_id=correlation_id)
        raise MCPError(f"Failed to list resources: {str(e)}", error_code="RESOURCE_LIST_ERROR") from e


async def main() -> None:
    """Main server entry point."""
    try:
        logger.info("Starting EchoFlow MCP Server", version=settings.version)

        # Create required directories
        settings.processing.temp_dir.mkdir(parents=True, exist_ok=True)
        settings.cache.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info("EchoFlow MCP Server initialized successfully")

        # Run the MCP server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error("Server startup failed", error=str(e))
        raise ServerError(f"Server startup failed: {str(e)}", error_code="STARTUP_ERROR") from e


if __name__ == "__main__":
    asyncio.run(main())
