# Multi-stage build for EchoFlow MCP Server
# Using Chainguard Python base for security

# Build stage
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install UV package manager
RUN pip install --user uv

# Create virtual environment and install dependencies in user space
RUN python -m venv /tmp/venv
ENV PATH="/tmp/venv/bin:$PATH"

# Install the application
ENV PATH="/tmp/venv/bin:$PATH"
RUN /tmp/venv/bin/pip install -e .

# Production stage
FROM cgr.dev/chainguard/python:latest-dev

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app/src"

WORKDIR /app

# Copy application source
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/README.md ./

# Install UV and application using system Python
RUN pip install --user uv
RUN pip install -e .

# Create non-root user (Chainguard images already have this)
# Health check for MCP server
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD /usr/bin/python3 -c "import asyncio; import sys; sys.path.insert(0, '/app/src'); from echoflow.server.health import health_check; asyncio.run(health_check())" || exit 1

# Expose MCP server port (stdio by default for MCP)
EXPOSE 3000

# Command to run the application
CMD ["/usr/bin/python3", "-m", "echoflow.server.main"]