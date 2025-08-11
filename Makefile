# Makefile for EchoFlow MCP Server
.PHONY: help install test lint format type-check clean build docker-build docker-run

# Default target
help:
	@echo "EchoFlow MCP Server - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     Install development dependencies with UV"
	@echo "  test        Run all tests with coverage"
	@echo "  test-unit   Run unit tests only"  
	@echo "  test-integration  Run integration tests only"
	@echo "  test-phase2 Test Phase 2 AI capabilities (quick validation)"
	@echo "  lint        Run code linting (ruff)"
	@echo "  format      Format code (ruff format, isort)"
	@echo "  type-check  Run type checking (mypy)"
	@echo ""
	@echo "Quality:"
	@echo "  quality     Run all quality checks (lint + format + type-check + test)"
	@echo "  coverage    Generate HTML coverage report"
	@echo "  benchmark   Run performance benchmarks"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build         Build Docker image"
	@echo "  docker-run           Run Docker container interactively"
	@echo "  docker-run-detached  Run Docker container in background"
	@echo "  docker-test          Test Docker container with Phase 2 capabilities"
	@echo "  docker-shell         Open shell in Docker container"
	@echo "  docker-logs          Show logs from running container"
	@echo "  docker-stop          Stop and remove running container"
	@echo ""
	@echo "Deployment:"
	@echo "  clean       Clean build artifacts"
	@echo "  build       Build distribution packages"

# Virtual environment activation
VENV_ACTIVATE = source .venv/bin/activate

# Development setup
install:
	uv venv
	$(VENV_ACTIVATE) && uv pip install -e ".[dev]"

# Testing targets
test:
	$(VENV_ACTIVATE) && python -m pytest tests/ --cov=src/echoflow --cov-report=term-missing

test-unit:
	$(VENV_ACTIVATE) && python -m pytest tests/unit/ -v --cov=src/echoflow --cov-report=term-missing

test-integration:
	$(VENV_ACTIVATE) && python -m pytest tests/integration/ -v --tb=short

test-phase2:
	@echo "🧪 Running Phase 2 comprehensive tests..."
	$(VENV_ACTIVATE) && python scripts/test_phase2.py

# Code quality targets  
lint:
	$(VENV_ACTIVATE) && ruff check src tests

format:
	$(VENV_ACTIVATE) && ruff format src tests
	$(VENV_ACTIVATE) && isort src tests

type-check:
	$(VENV_ACTIVATE) && mypy src

# Combined quality check
quality: lint format type-check test

# Coverage reporting
coverage:
	$(VENV_ACTIVATE) && python -m pytest tests/unit/ --cov=src/echoflow --cov-report=html
	@echo "Coverage report generated in htmlcov/"

# Performance benchmarking (Phase 2+)
benchmark:
	$(VENV_ACTIVATE) && python -m pytest tests/performance/ --benchmark-only

# Docker targets
docker-build:
	docker build -t echoflow:latest .

docker-run:
	docker run --rm -it -p 3000:3000 echoflow:latest

docker-run-detached:
	docker run -d --name echoflow-server -p 3000:3000 echoflow:latest

docker-logs:
	docker logs echoflow-server

docker-stop:
	docker stop echoflow-server && docker rm echoflow-server

docker-shell:
	docker run --rm -it --entrypoint=/bin/sh echoflow:latest

docker-test:
	@echo "🐳 Running comprehensive EchoFlow Docker tests..."
	docker run --rm --entrypoint="" echoflow:latest python3 /app/scripts/docker_test.py

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/ .coverage build/ dist/ *.egg-info/

# Build distribution
build:
	$(VENV_ACTIVATE) && python -m build

# Development server (Phase 2+)
serve:
	$(VENV_ACTIVATE) && python -m echoflow.server.main

# Health check
health:
	$(VENV_ACTIVATE) && python -c "import asyncio; import sys; sys.path.insert(0, 'src'); from echoflow.server.health import health_check; asyncio.run(health_check())"