# Contributing to Git Client

Thank you for your interest in contributing to Git Client! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites
- Python 3.8+
- pip
- Git
- OpenSSH

### Setting Up Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd AI_Git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
```

## Project Structure

```
git_client/
├── core/                  # Core Git functionality
│   ├── git_operations.py  # Basic Git operations
│   ├── branch_manager.py  # Branch management
│   └── history_viewer.py  # History and diff operations
├── utils/                 # Utility modules
│   ├── ssh_manager.py     # SSH key management
│   ├── config_manager.py  # Configuration handling
│   └── logger.py          # Logging and error handling
└── cli/                   # Command-line interface
    └── main.py            # CLI application
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, readable code
- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Add type hints where appropriate

### 3. Test Your Changes

```bash
# Run tests (when test suite is available)
pytest

# Check code style
black git_client/
flake8 git_client/

# Type checking
mypy git_client/
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Add feature: your feature description"
```

Follow conventional commit messages:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Code Style

- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all public functions

Example:
```python
def add_remote(self, name: str, url: str) -> Tuple[bool, str]:
    """
    Add a remote repository

    Args:
        name: Remote name
        url: Remote URL

    Returns:
        Tuple of (success, message)
    """
    pass
```

### Documentation Style

- Use Google-style docstrings
- Include type hints
- Document all parameters and return values
- Add usage examples for complex functions

## Testing Guidelines

### Writing Tests

```python
import pytest
from git_client.core.git_operations import GitOperations

def test_init_repository():
    """Test repository initialization"""
    git_ops = GitOperations("./test_repo")
    success, message = git_ops.init()
    assert success == True
    assert "Initialized" in message
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=git_client

# Run specific test file
pytest tests/test_git_operations.py
```

## Adding New Features

### 1. Core Functionality

If adding new Git operations:
1. Add method to appropriate module in `git_client/core/`
2. Follow existing patterns (return `Tuple[bool, str]` or `Tuple[bool, Any]`)
3. Add comprehensive error handling
4. Document the function

### 2. CLI Commands

If adding new CLI commands:
1. Add command to `git_client/cli/main.py`
2. Use Click decorators
3. Add appropriate options and arguments
4. Include help text
5. Use Rich for formatted output

Example:
```python
@cli.command()
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='Force operation')
def mycommand(name, force):
    """Description of your command"""
    # Implementation
    pass
```

### 3. Utilities

If adding utility functions:
1. Add to appropriate module in `git_client/utils/`
2. Keep utilities generic and reusable
3. Add comprehensive documentation

## Error Handling

- Use try-except blocks for operations that might fail
- Return tuple of (success, message/data)
- Log errors using the Logger utility
- Provide helpful error messages

Example:
```python
try:
    # Operation
    return True, "Success message"
except GitCommandError as e:
    return False, f"Git error: {e.stderr}"
except Exception as e:
    return False, f"Error: {str(e)}"
```

## Documentation

### Updating README

- Update README.md for new features
- Add examples for new commands
- Update command reference

### Adding Examples

- Add usage examples to `examples.py`
- Include code comments
- Show both success and error cases

## Release Process

1. Update version in `setup.py` and `git_client/__init__.py`
2. Update CHANGELOG.md
3. Create a git tag
4. Push tag to GitHub

## Getting Help

- Open an issue for bugs or feature requests
- Join discussions on GitHub
- Check existing issues and pull requests

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Git Client!
