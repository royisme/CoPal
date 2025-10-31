# Development Guide

This document provides guidance for developers contributing to CoPal.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip or another Python package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CoPal.git
   cd CoPal
   ```

2. Install in development mode with test dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

This installs CoPal in editable mode and includes pytest and pytest-cov for testing.

## Running Tests

### Run all tests

```bash
pytest
```

### Run tests with coverage report

```bash
pytest --cov=copal_cli --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run specific test files

```bash
pytest tests/test_cli.py
pytest tests/test_init.py
pytest tests/test_validator.py
```

### Run tests in verbose mode

```bash
pytest -v
```

### Run tests with output

```bash
pytest -s
```

## Code Quality

### Type Hints

All functions should include type hints using Python's `typing` module or `from __future__ import annotations`.

Example:
```python
from __future__ import annotations

def example_function(name: str, count: int = 0) -> bool:
    """Example function with type hints."""
    return len(name) > count
```

### Docstrings

All public functions, classes, and modules should have docstrings following Google style:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of the function.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        bool: Description of return value.

    Raises:
        ValueError: When param2 is negative.
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    return len(param1) > param2
```

## Project Structure

```
CoPal/
├── copal_cli/                  # Main package
│   ├── __init__.py
│   ├── cli.py                  # CLI entry point
│   ├── init.py                 # Init command
│   ├── validator.py            # YAML validation
│   └── templates/              # Template files
│       └── base/
│           ├── AGENTS.md
│           ├── UserAgents.md
│           └── .copal/
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_init.py
│   └── test_validator.py
├── docs/                       # Documentation
│   ├── USAGE.md
│   └── DEVELOPMENT.md
├── examples/                   # Example customizations
├── pyproject.toml              # Package configuration
├── pytest.ini                  # Pytest configuration
└── README.md                   # Main documentation
```

## Adding New Commands

To add a new command to the CLI:

1. Create a new module in `copal_cli/` (e.g., `new_command.py`)
2. Implement the command function:
   ```python
   def new_command(*, arg1: str, arg2: bool = False) -> int:
       """Command description.

       Args:
           arg1: Argument description.
           arg2: Flag description.

       Returns:
           int: Exit code (0 for success, non-zero for failure).
       """
       # Implementation
       return 0
   ```

3. Register the command in `cli.py`:
   ```python
   from .new_command import new_command

   def build_parser():
       # ... existing code ...

       new_parser = subparsers.add_parser("new", help="New command description")
       new_parser.add_argument("--arg1", required=True, help="Argument help")
       new_parser.add_argument("--arg2", action="store_true", help="Flag help")

       return parser

   def main(argv):
       # ... existing code ...

       elif args.command == "new":
           return new_command(arg1=args.arg1, arg2=args.arg2)
   ```

4. Write tests in `tests/test_new_command.py`

## Testing Best Practices

### Use tmp_path fixture

For tests that need to create files:

```python
def test_example(tmp_path):
    """Test that creates temporary files."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.exists()
```

### Mock external dependencies

Use `unittest.mock.patch` for mocking:

```python
from unittest.mock import patch

@patch("copal_cli.cli.init_command")
def test_main(mock_init):
    """Test with mocked init_command."""
    mock_init.return_value = 0
    result = main(["init"])
    assert result == 0
    mock_init.assert_called_once()
```

### Test both success and failure cases

```python
def test_success_case():
    """Test successful operation."""
    result = some_function(valid_input)
    assert result is True

def test_failure_case():
    """Test error handling."""
    with pytest.raises(ValueError):
        some_function(invalid_input)
```

## Logging

Use Python's `logging` module instead of `print()`:

```python
import logging

logger = logging.getLogger(__name__)

def example():
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.debug("Debug message")
```

Logging levels:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages for potentially problematic situations
- `ERROR`: Error messages for serious problems

## Release Process

### Version Bumping

1. Update version in `pyproject.toml`
2. Update CHANGELOG (if exists)
3. Commit changes:
   ```bash
   git commit -am "Bump version to X.Y.Z"
   ```
4. Tag the release:
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   ```
5. Push changes and tags:
   ```bash
   git push origin main --tags
   ```

### Building Distribution

```bash
python -m build
```

This creates distribution files in `dist/`:
- `copal_cli-X.Y.Z-py3-none-any.whl` (wheel)
- `copal_cli-X.Y.Z.tar.gz` (source)

### Publishing to PyPI

```bash
python -m twine upload dist/*
```

## Common Development Tasks

### Adding a new template file

1. Add file to `copal_cli/templates/base/`
2. Update `init.py` to copy the new file
3. Add tests for the new file

### Updating YAML validation rules

1. Modify `validator.py`:
   - Update `VALID_TYPES`, `VALID_ORIGINS`, etc.
   - Add new validation logic to `validate_file()`
2. Add tests to `tests/test_validator.py`

### Adding command-line options

1. Update `build_parser()` in `cli.py`
2. Update command function signature to accept new parameter
3. Add tests for new option

## Getting Help

- Check existing issues on GitHub
- Read the [USAGE.md](USAGE.md) document
- Review test files for examples
- Open a new issue for questions or problems

## Code Style Guidelines

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Keep functions focused and small
- Write self-documenting code with clear names
- Add comments only when necessary to explain "why", not "what"
- Use type hints consistently
- Write docstrings for all public APIs

## Contribution Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and write tests
4. Run tests: `pytest`
5. Commit with clear messages: `git commit -am "Add feature X"`
6. Push to your fork: `git push origin feature/my-feature`
7. Open a Pull Request

## Questions?

If you have questions about development, please:
1. Check this guide first
2. Look at existing code and tests for examples
3. Open an issue on GitHub with the "question" label
