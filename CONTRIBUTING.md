# Contributing to Nostr Shitposter Agent

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check if the issue has already been reported
2. Verify you're using the latest version
3. Check the [troubleshooting section](README.md#troubleshooting) in the README

When reporting bugs, please include:
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, and relevant package versions
- **Logs**: Relevant log output (redact any secrets/keys)

### Suggesting Features

Feature suggestions are welcome! Please:
1. Check if the feature has already been suggested
2. Provide a clear description of the feature
3. Explain the use case and benefits
4. Consider implementation complexity

### Pull Requests

1. **Fork the repository** and clone your fork
2. **Create a branch** from `main`: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Follow the code style guidelines below
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass
4. **Commit your changes** with clear, descriptive messages
5. **Push to your fork**: `git push origin feature/your-feature-name`
6. **Open a Pull Request** with a clear description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/nostr-agent.git
cd nostr-agent

# Add upstream remote
git remote add upstream https://github.com/ftw2100/nostr-agent.git

# Install dependencies
pipenv install --dev

# Run tests
pipenv run pytest

# Run with verbose output
pipenv run pytest -v
```

## Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints for all function signatures
- Maximum line length: 100 characters (soft limit)
- Use 4 spaces for indentation (no tabs)

### Code Organization

- **Functions**: Should be focused and do one thing
- **Classes**: Use clear, descriptive names
- **Docstrings**: Add docstrings to all public functions and classes
- **Imports**: Organize imports (stdlib, third-party, local)

### Example

```python
from typing import Optional

def process_message(message: str, max_length: int = 500) -> Optional[str]:
    """
    Process a message and return the processed version.
    
    Args:
        message: The message to process
        max_length: Maximum length of the processed message
        
    Returns:
        Processed message or None if invalid
        
    Raises:
        ValueError: If message is empty
    """
    if not message:
        raise ValueError("Message cannot be empty")
    
    processed = message.strip()
    if len(processed) > max_length:
        processed = processed[:max_length]
    
    return processed
```

## Testing

- Write tests for all new functionality
- Ensure existing tests continue to pass
- Aim for good test coverage
- Use descriptive test names

### Running Tests

```bash
# Run all tests
pipenv run pytest

# Run specific test file
pipenv run pytest tests/test_nostr_client.py

# Run with coverage
pipenv run pytest --cov=src tests/

# Run with verbose output
pipenv run pytest -v
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update CHANGELOG.md for significant changes
- Keep comments clear and concise

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add rate limiting for commands
fix: Fix memory leak in posting loop
docs: Update installation instructions
test: Add tests for command handler
refactor: Simplify config loading logic
```

Prefixes:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `chore`: Maintenance tasks

## Review Process

1. All PRs require review before merging
2. Address review comments promptly
3. Keep PRs focused - one feature/fix per PR
4. Keep PRs reasonably sized for easier review

## Questions?

- Open an issue for questions
- Check existing issues and discussions
- Review the README.md for common questions

Thank you for contributing! 🎉
