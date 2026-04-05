# 🔧 Developer Quick Reference

## Project Overview

A **production-ready text summarization application** using BART, Streamlit, and PyTorch with professional error handling, testing, and deployment support.

## Key Files at a Glance

| File | Purpose |
|------|---------|
| `app.py` | Streamlit web app entry point |
| `src/model.py` | BART model wrapper with error handling |
| `src/config.py` | Configuration and logging setup |
| `src/utils.py` | Utility functions |
| `tests/test_model.py` | Test suite (11+ tests) |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Docker containerization |
| `README.md` | Complete documentation |
| `.env.example` | Environment variables template |

## Common Workflows

### Setting Up Development Environment

```bash
# Unix/Linux/Mac
bash setup.sh

# Windows  
setup.bat

# Or manually
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install pytest black flake8 mypy  # Dev tools
```

### Running the App

```bash
# Start the app
streamlit run app.py

# With debug logging
LOG_LEVEL=DEBUG streamlit run app.py

# With different model path
MODEL_PATH=/path/to/model streamlit run app.py
```

### Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_model.py::TestSummarizationModel -v
```

### Code Quality

```bash
# Format code
black src/ tests/ app.py

# Check formatting
black --check src/ tests/ app.py

# Lint code
flake8 src/ tests/ app.py

# Type check
mypy src/

# Do all checks
make check  # or manually run: black, flake8, mypy
```

### Using Make Commands

```bash
make help       # Show all available commands
make install    # Install dependencies
make dev        # Run in dev mode
make test       # Run tests
make lint       # Run linting
make format     # Format code
make clean      # Clean up cache
```

### Docker

```bash
# Build image
docker build -t text-summarizer .

# Run container
docker run -p 8501:8501 text-summarizer

# Or use make
make docker-build
make docker-run
```

## Environment Variables

See `.env.example` for all options. Common ones:

```bash
MODEL_PATH=./fine_tuned_bart_model
MAX_INPUT_LENGTH=1024
MAX_SUMMARY_LENGTH=150
MIN_SUMMARY_LENGTH=40
NUM_BEAMS=4
DEBUG_MODE=false
LOG_LEVEL=INFO
```

## Project Dependencies

**Core:**
- `torch>=2.0.0` - Neural network framework
- `transformers>=4.30.0` - BART model
- `streamlit>=1.20.0` - Web UI
- `python-dotenv>=1.0.0` - Environment variables

**Dev (optional):**
- `pytest` - Testing framework
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Type checker

## Code Structure

### Model (src/model.py)
```python
# Using the model
from src.model import summarize

summary = summarize(text)  # Simple API

# Advanced usage
from src.model import SummarizationModel
model = SummarizationModel()
is_valid, error = model.validate_input(text)
if is_valid:
    summary = model.summarize(text)
```

### Configuration (src/config.py)
```python
from src.config import (
    MODEL_PATH,
    MAX_INPUT_LENGTH,
    get_logger,
)

logger = get_logger(__name__)
logger.info("Starting application")
```

### Utils (src/utils.py)
```python
from src.utils import estimate_reading_time, clean_text

time = estimate_reading_time(text)  # Minutes
cleaned = clean_text(text)  # Normalize text
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes
# ... edit files ...

# Run tests and checks
pytest tests/
make check

# Commit with descriptive message
git commit -am "Add feature: description"

# Push to fork
git push origin feature/your-feature

# Create Pull Request on GitHub
```

## Debugging Tips

### Enable Debug Logging
```bash
LOG_LEVEL=DEBUG streamlit run app.py
```

### Debug Python Shell
```bash
python
from src.model import get_model
model = get_model()
# Inspect model internals
```

### Run Tests with Output
```bash
pytest tests/ -v -s  # -s shows print statements
pytest tests/test_model.py::SpecificTest -vv
```

## Performance Optimization

### For Faster Summarization
- Reduce `NUM_BEAMS` in `.env` (default 4, try 2)
- Reduce `MAX_SUMMARY_LENGTH`
- Use GPU (automatic if available)

### For Lower Memory Usage
- Reduce `MAX_INPUT_LENGTH`
- Batch process (if implemented)
- Use smaller model variant

### Check Available Resources
```python
import torch
print(torch.cuda.is_available())  # True if GPU available
print(torch.cuda.get_device_name())  # GPU name if available
```

## Troubleshooting

### Model Fails to Load
```
FileNotFoundError: Model path does not exist
```
**Solution:** Ensure `fine_tuned_bart_model/` folder exists with all required files:
- `config.json`
- `model.safetensors` (or `pytorch_model.bin`)
- `tokenizer.json`

### Out of Memory
```
Cuda out of memory / RuntimeError
```
**Solutions:**
- Set `NUM_BEAMS=2` (faster, lower quality)
- Reduce `MAX_INPUT_LENGTH`
- Use CPU: `CUDA_VISIBLE_DEVICES='' streamlit run app.py`

### Import Errors
```
ModuleNotFoundError: No module named 'src'
```
**Solution:** Run from project root directory

### Tests Fail
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run with verbose output to see what fails
pytest tests/ -vv
```

## Key Development Commands

```bash
# Install and setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run app
streamlit run app.py           # Open http://localhost:8501

# Test everything
pytest tests/ -v               # Run all tests
black --check src/             # Check formatting
flake8 src/                    # Check linting
mypy src/                      # Check types

# Quick fixes
black src/ tests/ app.py       # Auto-format
pytest --cov=src              # Coverage report

# Build and deploy
docker build -t summarizer .
docker run -p 8501:8501 summarizer
```

## File Editing Checklist

When adding new features:

1. ✅ Add functionality to `src/model.py` or appropriate module
2. ✅ Add type hints and docstrings
3. ✅ Add unit tests to `tests/`
4. ✅ Run `pytest` to verify tests pass
5. ✅ Run `black` and `flake8` for code quality
6. ✅ Run `mypy` for type checking
7. ✅ Update `README.md` if user-facing changes
8. ✅ Commit with descriptive message

## Useful Links

- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PyTorch](https://pytorch.org/)
- [BART Paper](https://arxiv.org/abs/1910.13461)

## Performance Benchmarks

Typical performance on modern hardware:

| Input Length | Time | GPU | CPU |
|--------------|------|-----|-----|
| 500 chars | 2-3s | 1-2s | 5-10s |
| 2000 chars | 3-5s | 2-3s | 8-15s |
| 5000 chars | 5-8s | 3-5s | 15-20s |

## Version Information

- **Python**: 3.9+ required
- **PyTorch**: 2.0+
- **Transformers**: 4.30+
- **Streamlit**: 1.20+

---

**For detailed information, see README.md or CONTRIBUTING.md**
