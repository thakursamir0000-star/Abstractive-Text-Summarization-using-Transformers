# Text Summarization with BART

A professional-grade **abstractive text summarization** application built with a fine-tuned BART model, Streamlit, and PyTorch.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B)

## 🌟 Features

- **Abstractive Summarization**: Generates new summaries, not just extracts text
- **Error Handling**: Robust validation and graceful error management
- **GPU Support**: Leverages GPU acceleration when available
- **Cloud Ready**: Deployable to Hugging Face Spaces, Streamlit Cloud, or Docker
- **User-Friendly**: Clean, intuitive web interface with helpful statistics
- **Configurable**: Environment-based configuration for production use
- **Logged**: Comprehensive logging for debugging and monitoring

## 📋 Requirements

- Python 3.9 or higher
- PyTorch 2.0+
- CUDA 11.8+ (optional, for GPU acceleration)
- ~8GB RAM (16GB+ recommended for large documents)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/text-summarization.git
cd text-summarization
```

### 2. Create a Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n summarizer python=3.9
conda activate summarizer
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 🌐 Cloud Deployment

### Hugging Face Spaces

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Choose "Streamlit" as the runtime
3. Upload your code and `.env.example` file
4. Rename `.env.example` to `.env` in the space
5. Your app will be live at `https://huggingface.co/spaces/username/your-space`

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repo
4. Deploy with one click

### Docker

```bash
# Build the image
docker build -t text-summarizer .

# Run the container
docker run -p 8501:8501 text-summarizer

# Access at http://localhost:8501
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Available options:

```bash
# Model configuration
MODEL_PATH=./fine_tuned_bart_model
MAX_INPUT_LENGTH=1024
MAX_SUMMARY_LENGTH=150
MIN_SUMMARY_LENGTH=40
NUM_BEAMS=4

# App configuration
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### Configuration File

Edit `src/config.py` for hardcoded defaults or environment variables.

## 📂 Project Structure

```
text-summarization/
├── src/                          # Source code package
│   ├── __init__.py              # Package initialization
│   ├── model.py                 # BART model wrapper with error handling
│   ├── config.py                # Configuration management
│   └── utils.py                 # Utility functions
├── fine_tuned_bart_model/       # Pre-trained model files
│   ├── config.json
│   ├── model.safetensors
│   ├── tokenizer.json
│   └── ...
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_model.py
├── Notebook/                     # Jupyter notebooks
│   └── Text_summarization_bart.ipynb
├── .github/workflows/           # CI/CD configurations
│   └── ci.yml
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── Dockerfile                   # Docker configuration
├── setup.py                     # Package setup
└── README.md                    # This file
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_model.py -v
```

## 📊 Usage Examples

### Basic Usage

```python
from src.model import summarize

text = "Your long text here..."
summary = summarize(text)
print(summary)
```

### With Error Handling

```python
from src.model import summarize

try:
    summary = summarize(text)
except ValueError as e:
    print(f"Input error: {e}")
except RuntimeError as e:
    print(f"Summarization error: {e}")
```

### Using the Model Class

```python
from src.model import SummarizationModel

model = SummarizationModel()

# Validate input
is_valid, error = model.validate_input(text)
if is_valid:
    summary = model.summarize(text)
```

## 🔧 Development

### Code Quality

Format and lint your code:

```bash
# Format with Black
black src/ tests/ app.py

# Check with flake8
flake8 src/ tests/ app.py

# Type check with mypy
mypy src/
```

### Adding New Features

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make your changes and add tests
3. Run tests: `pytest`
4. Format code: `black .` and `flake8 .`
5. Commit and push: `git commit -am "Add feature"` and `git push`
6. Create a Pull Request

## 🐛 Troubleshooting

### Model Fails to Load

**Problem**: `FileNotFoundError: Model path does not exist`

**Solution**: Ensure the `fine_tuned_bart_model` folder is in the project root directory with all required files:
- `config.json`
- `model.safetensors`
- `tokenizer.json`
- `tokenizer_config.json`

### Out of Memory Error

**Problem**: `CUDA out of memory` or `RuntimeError`

**Solutions**:
- Reduce `MAX_INPUT_LENGTH` in `.env`
- Reduce `NUM_BEAMS` for faster but lower-quality summaries
- Use CPU instead of GPU: `CUDA_VISIBLE_DEVICES=''`

### Text Too Short

**Problem**: "Text must be at least 50 characters long"

**Solution**: Use longer input text. The model works better with substantial content.

## 📝 Logging

Logs are printed to console. Configure logging level:

```bash
LOG_LEVEL=DEBUG streamlit run app.py
```

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🙋 Support

For issues, questions, or suggestions:

1. Check [existing issues](https://github.com/yourusername/text-summarization/issues)
2. [Create a new issue](https://github.com/yourusername/text-summarization/issues/new)

## 📚 References

- [BART Paper](https://arxiv.org/abs/1910.13461)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PyTorch Documentation](https://pytorch.org/docs/)

## ✨ Acknowledgments

- Built with [Hugging Face Transformers](https://huggingface.co/transformers/)
- Frontend powered by [Streamlit](https://streamlit.io/)
- Model training based on [BART](https://arxiv.org/abs/1910.13461)

---

**Happy Summarizing!** 📝✨