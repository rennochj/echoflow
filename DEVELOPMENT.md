# EchoFlow Development Workflow

This document outlines the development workflow for EchoFlow, following the standards defined in CLAUDE.md.

## Prerequisites

- Python 3.9+
- UV package manager
- Docker (for containerized development)
- Git
- VS Code (recommended IDE)

## Initial Setup

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd echoflow

# Create virtual environment with UV
uv venv
source .venv/bin/activate

# Install development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 2. VS Code Setup

The repository includes pre-configured VS Code settings in `.vscode/`:
- Python interpreter auto-detection
- Integrated linting and formatting
- Test discovery and debugging
- Docker support

## Development Process

### Code Standards Compliance

All code must follow CLAUDE.md standards:

#### Type Hints
```python
# ✅ Good - Full type annotations
async def convert_document(
    file_path: Path,
    options: ConversionOptions
) -> ConversionResult:
    pass

# ❌ Bad - Missing type hints
async def convert_document(file_path, options):
    pass
```

#### Error Handling
```python
# ✅ Good - Specific exception types
try:
    result = await converter.convert(file_path, output_dir, options)
except ValidationError as e:
    logger.error("Validation failed", error=str(e))
    raise
except ConversionError as e:
    logger.error("Conversion failed", error=str(e))
    raise

# ❌ Bad - Generic exception handling
try:
    result = await converter.convert(file_path, output_dir, options)
except Exception as e:
    print(f"Error: {e}")
```

#### Logging
```python
# ✅ Good - Structured logging with correlation IDs
from echoflow.utils.logging import get_logger, set_correlation_id

logger = get_logger(__name__)

async def process_document(file_path: Path) -> None:
    correlation_id = set_correlation_id()
    logger.info("Starting document processing", 
                file_path=str(file_path), 
                correlation_id=correlation_id)
```

#### Async Patterns
```python
# ✅ Good - Proper async/await usage
async def convert_multiple(files: List[Path]) -> List[ConversionResult]:
    tasks = [convert_single(file) for file in files]
    return await asyncio.gather(*tasks)

# ❌ Bad - Blocking operations in async context
async def convert_multiple(files: List[Path]) -> List[ConversionResult]:
    results = []
    for file in files:
        result = convert_single(file)  # Missing await
        results.append(result)
    return results
```

## Quality Gates

### Pre-commit Hooks

Every commit automatically runs:
- `ruff` for linting and formatting
- `isort` for import organization  
- `mypy` for type checking
- `bandit` for security scanning
- `pytest` for unit tests

### Manual Quality Checks

```bash
# Run all quality checks
source .venv/bin/activate

# Linting and formatting
ruff check src tests
ruff format src tests

# Type checking
mypy src

# Import sorting
isort src tests

# Security scanning
bandit -r src/

# Test suite with coverage
pytest tests/unit/ --cov=src/echoflow --cov-report=term-missing
```

### Coverage Requirements

- **Minimum:** 80% test coverage
- **Target:** 90% test coverage
- All new code must include comprehensive tests
- Edge cases and error conditions must be tested

## Testing Strategy

### Unit Tests
```bash
# Run unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src/echoflow --cov-report=html
```

### Integration Tests
```bash
# Run integration tests (Phase 2+)
pytest tests/integration/ -v
```

### Test Organization
```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests
│   ├── test_config.py
│   ├── test_converters.py
│   └── test_exceptions.py
├── integration/          # Integration tests
└── fixtures/             # Test data
```

### Writing Tests

Follow these patterns for comprehensive test coverage:

```python
# ✅ Good - Comprehensive test class
class TestDocumentConverter:
    """Test DocumentConverter functionality."""
    
    async def test_convert_pdf_success(self, sample_pdf_path, temp_dir):
        """Test successful PDF conversion."""
        converter = PDFConverter()
        options = ConversionOptions()
        
        result = await converter.convert(sample_pdf_path, temp_dir, options)
        
        assert result.success is True
        assert len(result.markdown_content) > 0
        assert result.metadata.page_count > 0
    
    async def test_convert_invalid_file(self, temp_dir):
        """Test conversion with invalid file."""
        converter = PDFConverter()
        options = ConversionOptions()
        invalid_file = temp_dir / "nonexistent.pdf"
        
        result = await converter.convert(invalid_file, temp_dir, options)
        
        assert result.success is False
        assert "File does not exist" in result.error_message
```

## Docker Development

### Local Development
```bash
# Build development image
docker build -t echoflow:dev .

# Run with volume mounting for live development
docker run -it --rm \
  -v $(pwd):/app \
  -p 3000:3000 \
  echoflow:dev
```

### Testing Docker Build
```bash
# Test Docker build
docker build -t echoflow:test .
docker run --rm echoflow:test python -c "import src.echoflow; print('Success')"
```

## Git Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature development
- `hotfix/*` - Critical fixes

### Commit Messages
Follow conventional commit format:
```
feat: add PDF table extraction support
fix: resolve memory leak in large file processing  
docs: update API documentation
test: add edge case tests for converter registry
refactor: simplify error handling in MCP handlers
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/add-docx-converter
   ```

2. **Develop with Quality Gates**
   - Pre-commit hooks run on every commit
   - All tests must pass
   - Coverage must be maintained

3. **Push and Create PR**
   ```bash
   git push origin feature/add-docx-converter
   # Create PR via GitHub interface
   ```

4. **CI/CD Pipeline Validation**
   - Automated tests across Python versions
   - Security scanning
   - Docker build verification
   - Integration test execution

## Debugging

### VS Code Debugging

Launch configurations are pre-configured:
- **EchoFlow MCP Server** - Debug the main server
- **Python: Current File** - Debug current Python file
- **Python: Pytest** - Debug test cases

### Logging for Debugging

```python
# Enable debug logging
import os
os.environ["ECHOFLOW_LOG_LEVEL"] = "DEBUG"

# Use structured logging
logger = get_logger(__name__)
logger.debug("Processing document", 
             file_size=file_path.stat().st_size,
             format=file_path.suffix)
```

### Health Checks

```bash
# Check server health
source .venv/bin/activate
python -c "
import asyncio
from src.echoflow.server.health import health_check
asyncio.run(health_check())
"
```

## Performance Profiling

### Memory Profiling
```bash
# Install memory profiler
uv pip install memory-profiler

# Profile memory usage
python -m memory_profiler src/echoflow/server/main.py
```

### Performance Testing
```bash
# Install performance testing tools
uv pip install pytest-benchmark

# Run performance tests
pytest tests/performance/ --benchmark-only
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure PYTHONPATH includes src/
   export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
   ```

2. **Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf .venv
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

3. **Pre-commit Hook Failures**
   ```bash
   # Update pre-commit hooks
   pre-commit autoupdate
   pre-commit run --all-files
   ```

4. **Docker Build Issues**
   ```bash
   # Clean Docker cache
   docker system prune -a
   docker build --no-cache -t echoflow:latest .
   ```

### Getting Help

1. Check existing GitHub issues
2. Review CLAUDE.md for coding standards
3. Consult the build plan in `plan/echoflow.plan.md`
4. Reach out to the development team

## Phase-Specific Guidelines

### Phase 1: Foundation (Current)
- Focus on MCP server stability
- Comprehensive error handling
- High test coverage (>80%)
- All quality gates must pass

### Phase 2: Document Processing (Next)
- Implement Docling integration
- Add fallback conversion systems
- Performance optimization required
- Memory management critical

### Phase 3: MCP Tools & Batch Operations
- Complete MCP API implementation
- Batch processing optimization
- Real-time progress reporting
- Concurrent processing safety

### Phase 4: Production Optimization
- Performance tuning and caching
- Advanced monitoring and alerting
- Security hardening
- Production readiness validation

### Phase 5: Deployment & Integration
- Docker production configuration
- End-to-end integration testing
- Documentation completion
- Deployment automation

## Code Review Checklist

Before submitting any code for review, ensure:

- [ ] All type hints are present and correct
- [ ] Comprehensive error handling with specific exception types
- [ ] Structured logging with correlation IDs
- [ ] Async/await patterns used correctly
- [ ] Unit tests with >80% coverage
- [ ] Integration tests for new features
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Follows CLAUDE.md standards

This development workflow ensures high code quality, maintainability, and adherence to the project's architectural standards while supporting efficient development practices.