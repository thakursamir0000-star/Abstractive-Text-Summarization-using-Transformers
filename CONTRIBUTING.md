# CONTRIBUTING.md

## Contributing to Text Summarization

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

### Code of Conduct

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback

### Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<your-username>/Abstractive-Text-Summarization-using-Transformers.git`
3. Create a virtual environment
4. Install development dependencies: `pip install -r requirements-dev.txt`
5. Create a feature branch: `git checkout -b feature/my-feature`

### Development Workflow

1. **Make changes** in your feature branch
2. **Write tests** for new functionality
3. **Lint**: `ruff check .`
4. **Run tests**: `pytest`
5. **If you changed the model or generation settings**, re-run the evaluation: `python -m evaluation.benchmark`
6. **Commit changes**: `git commit -am "Add feature"`
7. **Push to fork**: `git push origin feature/my-feature`
8. **Create Pull Request** on GitHub

### Pull Request Guidelines

- Provide a clear description of changes
- Reference related issues if applicable
- Ensure all tests pass
- Update documentation if needed
- Keep commits focused and logical

### Testing

Write tests for all new features:

```bash
# Run all tests
pytest

# Only the fast tests that need no model download
pytest -m "not model"

# One file
pytest tests/test_chunking.py -v
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for functions
- Add docstrings to functions and classes
- Maximum line length: 120 characters (`ruff`)

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Document configuration options
- Include usage examples

### Reporting Issues

When reporting bugs, include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment information (OS, Python version, etc.)
- Error logs/tracebacks

### Feature Requests

Provide:

- Clear use case and motivation
- Example usage
- Potential implementation approach

---

Thank you for contributing!
