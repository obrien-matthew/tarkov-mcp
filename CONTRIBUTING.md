=======

# Contributing to Tarkov MCP

Thank you for your interest in contributing to the Tarkov MCP! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip or poetry

### Installation

1. Clone your fork:

```bash
git clone https://github.com/yourusername/tarkov-mcp.git
cd tarkov-mcp
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -e ".[dev]"
```

4. Set up pre-commit hooks:

```bash
pre-commit install
```

5. Copy the example environment file:

```bash
cp .env.example .env
```

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-new-tool` - for new features
- `fix/rate-limit-bug` - for bug fixes
- `docs/update-readme` - for documentation updates
- `refactor/client-cleanup` - for refactoring

### Commit Messages

Follow conventional commit format:

- `feat: add new quest search functionality`
- `fix: resolve rate limiting issue`
- `docs: update API documentation`
- `test: add tests for item tools`
- `refactor: simplify GraphQL client`

## Testing

### Running Tests

Run the full test suite:

```bash
pytest tests/ -v
```

Run specific test files:

```bash
pytest tests/test_tools.py -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Follow the existing test patterns
- Mock external API calls
- Test both success and error cases

Example test structure:

```python
@pytest.mark.asyncio
async def test_new_feature_success(self, mock_client):
    # Arrange
    mock_client.return_value = expected_data

    # Act
    result = await tool.new_feature(arguments)

    # Assert
    assert result is not None
    assert len(result) > 0
```

## Code Style

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Linting
- **MyPy**: Type checking

### Running Code Quality Tools

Format code:

```bash
black src/ tests/
isort src/ tests/
```

Lint code:

```bash
ruff check src/ tests/
```

Type check:

```bash
mypy src/
```

Or run all checks:

```bash
pre-commit run --all-files
```

### Code Style Guidelines

- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use descriptive variable names
- Follow PEP 8 conventions
- Maximum line length is 100 characters

## Submitting Changes

### Pull Request Process

1. Ensure your code passes all tests and quality checks
2. Update documentation if needed
3. Add or update tests for your changes
4. Update the CHANGELOG.md if applicable
5. Create a pull request with a clear title and description

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Error messages or logs
- Minimal code example if applicable

### Feature Requests

For feature requests, please include:

- Clear description of the proposed feature
- Use case or problem it solves
- Possible implementation approach
- Any relevant examples or references

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `question` - Further information is requested

## Development Guidelines

### Adding New Tools

When adding new MCP tools:

1. Create the tool method in the appropriate tool class
2. Add comprehensive error handling
3. Include proper logging
4. Add type hints and docstrings
5. Write comprehensive tests
6. Update documentation

### API Integration

When working with the Tarkov API:

- Respect rate limits
- Handle API errors gracefully
- Use proper GraphQL queries
- Cache responses when appropriate
- Log API interactions for debugging

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately
- Don't expose sensitive information in errors

## Getting Help

If you need help:

- Check existing issues and documentation
- Ask questions in GitHub Discussions
- Reach out to maintainers

Thank you for contributing to the Tarkov MCP Server!
