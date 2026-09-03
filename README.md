---
title: Bart Summarizer Project
emoji: ✨
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

<div align="center">

# ✨ Abstractive Text Summarization using Transformers

**Condense lengthy articles, reports, and documents into crisp summaries — powered by a fine-tuned BART model.**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face%20Space-blue)](https://huggingface.co/spaces/samirthakur345/bart_summarizer_project)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[**Try the Live Demo →**](https://huggingface.co/spaces/samirthakur345/bart_summarizer_project)

</div>

---

## 📌 Overview

This project implements **abstractive text summarization** — the model doesn't just extract sentences, it reads the source material and generates entirely new, concise text that captures the key ideas.

Under the hood it uses [BART (Bidirectional and Auto-Regressive Transformers)](https://arxiv.org/abs/1910.13461), a sequence-to-sequence model from Facebook AI. The model can be swapped between the public `facebook/bart-large-cnn` checkpoint and a locally fine-tuned version stored in `fine_tuned_bart_model/`.

### Key Capabilities

| Feature | Details |
|---|---|
| **Abstractive summaries** | Generates new phrasing, not copy-paste extracts |
| **Beam-search decoding** | 4-beam search for higher-quality output |
| **Automatic GPU usage** | Falls back to CPU when CUDA is unavailable |
| **Configurable limits** | Input up to 100 000 chars; summary length, beam count, etc. via env vars |
| **Download results** | One-click export of summaries as `.txt` files |
| **Live statistics** | Compression ratio, word counts, and estimated reading-time savings |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Streamlit UI (app.py)               │
│  ┌───────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Text Input │→│  Summarize   │→│ Summary + Stats│  │
│  └───────────┘  └──────┬───────┘  └───────────────┘  │
└─────────────────────────┼────────────────────────────┘
                          │
         ┌────────────────▼────────────────┐
         │        src/model.py             │
         │  SummarizationModel (singleton) │
         │  • validate_input()             │
         │  • tokenize → generate → decode │
         └────────────────┬────────────────┘
                          │
         ┌────────────────▼────────────────┐
         │        src/config.py            │
         │  .env / env-var driven config   │
         │  MODEL_PATH, beam count, limits │
         └────────────────┬────────────────┘
                          │
              ┌───────────▼───────────┐
              │  BART Model Weights   │
              │  (local or HF Hub)    │
              └───────────────────────┘
```

---

## 🚀 Getting Started

### Option A — Use the hosted demo (no setup)

Open the Hugging Face Space:
**<https://huggingface.co/spaces/samirthakur345/bart_summarizer_project>**

### Option B — Run locally

**Prerequisites:** Python 3.9+ and pip.

```bash
# 1. Clone
git clone https://github.com/thakursamir0000-star/text-summarization.git
cd text-summarization

# 2. Create & activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch
streamlit run app.py
```

The app opens at **http://localhost:8501**. The first run downloads model weights (~1.5 GB); subsequent starts are instant.

### Option C — Docker

```bash
docker build -t text-summarizer .
docker run -p 7860:7860 text-summarizer
```

Open **http://localhost:7860**.

---

## 📋 Usage

1. **Paste or type** the text you want to summarize (50 – 100 000 characters).
2. Click **Summarize Text**.
3. View the generated summary along with compression statistics.
4. **Download** the summary as a `.txt` file if needed.

### Example

| | |
|---|---|
| **Input** (2 500 chars) | *"Artificial intelligence is transforming industries worldwide. From healthcare diagnostics to autonomous vehicles, AI systems are becoming integral to …"* |
| **Output** (250 chars) | *"AI is revolutionizing how businesses operate by automating tasks and improving decision-making processes across sectors."* |
| **Compression** | 10 % of original · ~10 min reading time saved |

---

## 📁 Project Structure

```
text-summarization/
├── app.py                    # Streamlit web application
├── Dockerfile                # Docker image for HF Spaces / self-hosting
├── requirements.txt          # Runtime Python dependencies
├── pyproject.toml            # Project metadata & dev tooling config
├── .env.example              # Environment variable template
├── LICENSE                   # MIT License
├── CONTRIBUTING.md           # Contribution guidelines
│
├── src/
│   ├── __init__.py
│   ├── config.py             # Env-var driven configuration
│   ├── model.py              # SummarizationModel wrapper (singleton)
│   ├── model_setup.py        # Model path resolution & download
│   └── utils.py              # Text cleaning, truncation, reading-time
│
└── fine_tuned_bart_model/    # (Optional) locally fine-tuned weights
```

---

## ⚙️ Configuration

All settings can be overridden via environment variables or a `.env` file (see [`.env.example`](.env.example)):

| Variable | Default | Description |
|---|---|---|
| `MODEL_PATH` | `fine_tuned_bart_model/` (local) or `facebook/bart-large-cnn` (fallback) | HF model ID or local path |
| `MAX_INPUT_LENGTH` | `1024` | Max tokenizer input length (tokens) |
| `MAX_SUMMARY_LENGTH` | `150` | Max generated summary length (tokens) |
| `MIN_SUMMARY_LENGTH` | `40` | Min generated summary length (tokens) |
| `NUM_BEAMS` | `4` | Beam-search width |
| `DEBUG_MODE` | `false` | Enable debug logging |
| `LOG_LEVEL` | `INFO` | Python log level |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | [Streamlit](https://streamlit.io/) |
| **Model** | [BART](https://huggingface.co/facebook/bart-large-cnn) (`transformers`) |
| **Deep Learning** | [PyTorch](https://pytorch.org/) |
| **Config** | [python-dotenv](https://pypi.org/project/python-dotenv/) |
| **Deployment** | Docker / [Hugging Face Spaces](https://huggingface.co/spaces) |

---

## 📊 Performance

Typical processing times (CPU, standard hardware):

| Input Length | Approx. Time |
|---|---|
| 500 chars | 2 – 3 s |
| 2 000 chars | 3 – 5 s |
| 5 000 chars | 5 – 8 s |

> GPU acceleration significantly reduces these times.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| **`ModuleNotFoundError`** | Run `pip install -r requirements.txt` |
| **First run is slow** | Model weights (~1.5 GB) are downloading — one-time only |
| **Out of memory** | Use shorter texts, reduce `NUM_BEAMS`, or switch to a smaller model |
| **Port 8501 in use** | `streamlit run app.py --server.port 8502` |
| **`Cannot copy out of meta tensor`** | Ensure `accelerate` is not overriding model loading (handled in code) |

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```
Fork → Branch → Commit → Pull Request
```

---

## 📄 License

This project is released under the [MIT License](LICENSE).

---

<div align="center">

**Made with ❤️ for better reading**

[Live Demo](https://huggingface.co/spaces/samirthakur345/bart_summarizer_project) · [Report Bug](https://github.com/thakursamir0000-star/Abstractive-Text-Summarization-using-Transformers/issues) · [Request Feature](https://github.com/thakursamir0000-star/Abstractive-Text-Summarization-using-Transformers/issues)

</div>
