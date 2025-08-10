# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Custom Instructions for Claude

### Behavioral Guidelines
- Always use type hints in Python code for better clarity and maintainability
- Implement comprehensive error handling with specific exception types
- Log important operations using the Python logging module
- Prefer async/await patterns for I/O operations in the MCP server
- Write docstrings for all classes and functions following Google style
- When suggesting code changes, explain the reasoning briefly

### Code Style Requirements
- Follow PEP 8 for Python code style
- Use meaningful variable and function names
- Keep functions focused on a single responsibility
- Maximum line length: 100 characters
- Use f-strings for string formatting
- Group imports: standard library, third-party, local imports

### Testing Approach
- Write unit tests for all new functionality
- Use pytest as the testing framework
- Aim for at least 80% code coverage
- Test edge cases and error conditions
- Mock external dependencies in tests

## Project Overview

EchoFlow is an MCP (Model Context Protocol) server designed for converting documents in various formats to markdown. The project focuses on:
- High-quality document conversion with format preservation
- Extensible architecture for adding new document types
- Fast and efficient processing of large documents
- Clean, maintainable code following best practices

## Development Environment

The project uses a Docker-based development container with:
- **Base Image**: Chainguard Python (latest-dev)
- **Python Package Manager**: UV (preferred over pip)
- **Shell**: Zsh with Oh My Zsh
- **Additional Tools**: Docker, Node.js, AWS CLI, MCP tools (claude-code, gemini-cli, perplexity-mcp)

## Common Commands

### Python Development
```bash
# Install dependencies (when requirements.txt exists)
uv pip install -r requirements.txt

# Install a new package
uv pip install package-name

# Create virtual environment (if needed)
uv venv

# Activate virtual environment
source .venv/bin/activate
```

### Testing & Quality
Since no test framework is currently set up, consider using:
```bash
# Install testing tools
uv pip install pytest pytest-cov black isort mypy ruff

# Run tests (once implemented)
pytest

# Format code
black .
isort .

# Lint code
ruff check .

# Type checking
mypy .
```

## Tools and Libraries
- **Package Management**: UV for Python package management
- **Testing**: pytest for unit tests
- **Linting**: ruff for code style checks
- **Type Checking**: mypy for static type analysis
- **Formatting**: black and isort for code formatting
- **Logging**: structlog for structured logging
- **Documentation**: Sphinx for generating documentation
- **Async I/O**: asyncio for asynchronous operations
- **MCP Protocol**: FastMCP for handling Model Context Protocol interactions

## Code Architecture

### Expected Structure
As an MCP server for document conversion, the codebase should include:
- **MCP Server Implementation**: Core server handling MCP protocol
- **Document Converters**: Modules for converting various document formats to markdown
- **Configuration**: Settings for server behavior and conversion options
- **CLI Interface**: Command-line interface for running the server

### MCP-Specific Patterns
- Implement tools as async functions for better performance
- Use structured input schemas for all MCP tools
- Return proper TextContent or ImageContent types
- Handle errors gracefully with informative error messages
- Support batch operations for processing multiple files
- Implement progress reporting for long-running conversions

### Development Guidelines
- Use UV for all Python package management
- Follow Python type hints for better code clarity
- The project is configured for VS Code with extensive Python extensions
- Docker is available for containerized testing and deployment
- Prefer composition over inheritance for converter classes
- Use dependency injection for external services
- Implement proper logging at DEBUG, INFO, WARNING, and ERROR levels

### Response Format Guidelines
When Claude responds about this project:
- Provide code examples when explaining concepts
- Include the specific file path and line numbers when referencing code
- Suggest test cases for new functionality
- Highlight potential performance implications
- Mention security considerations where relevant