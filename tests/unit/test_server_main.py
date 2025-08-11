"""Tests for server main functionality."""

import pytest

from echoflow.server import main


class TestServerMain:
    """Test cases for server main functionality."""

    def test_app_initialization(self):
        """Test that MCP server app is initialized."""
        assert main.app is not None
        assert main.app.name == "echoflow"

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available MCP tools."""
        tools = await main.list_tools()

        assert len(tools) >= 2  # Should have at least convert_document and convert_directory
        tool_names = [tool.name for tool in tools]
        assert "convert_document" in tool_names
        assert "convert_directory" in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_basic(self):
        """Test basic list_tools functionality."""
        tools = await main.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
