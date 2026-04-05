---
title: Bart Summarizer Project
emoji: ✨
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

# 📝 Text Summarizer Pro

An AI-powered text summarization application using BART (Bidirectional and Auto-Regressive Transformers) model. Quickly summarize long articles, reports, and documents with advanced abstractive summarization.

**Live Demo:** https://share.streamlit.io/thakursamir0000-star/text-summarization

---

## ✨ Features

- **Abstractive Summarization** - Generates new concise text, not just extracts
- **Fast Processing** - GPU-accelerated for quick results
- **Flexible Input** - Handles documents up to 100,000 characters
- **Beautiful UI** - Modern, intuitive web interface
- **Download Results** - Save summaries as text files
- **Statistics** - See compression ratios and reading time savings

---

## 🚀 Quick Start

### Option 1: Use Online (Easiest)
**No installation needed!** Open the live app: https://share.streamlit.io/thakursamir0000-star/text-summarization

### Option 2: Run Locally

**Requirements:**
- Python 3.8+
- pip (Python package manager)

**Steps:**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thakursamir0000-star/text-summarization.git
   cd text-summarization
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser:**
   ```
   http://localhost:8501
   ```

---

## 📋 How to Use

1. **Paste Text** - Enter the text you want to summarize
2. **Click Summarize** - Click the "Summarize Text" button
3. **View Results** - See the summary with statistics
4. **Download** - Save the summary as a text file

**Requirements:**
- Minimum 50 characters
- Maximum 100,000 characters
- Works best with well-structured text

---

## 📁 Project Structure

```
text-summarization/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── LICENSE                # MIT License
├── .env.example           # Environment variables template
├── fine_tuned_bart_model/ # Pre-trained model files
├── src/
│   ├── model.py          # BART model wrapper
│   ├── config.py         # Configuration management
│   ├── utils.py          # Utility functions
│   └── model_setup.py    # Model initialization
└── Notebook/
    └── [Your notebooks]
```

---

## 🛠️ Technology Stack

- **Frontend:** [Streamlit](https://streamlit.io/) - Python web framework
- **Model:** [BART](https://huggingface.co/facebook/bart-large-cnn) - Transformer model
- **Framework:** [Transformers](https://huggingface.co/transformers/) - NLP library
- **Deep Learning:** [PyTorch](https://pytorch.org/) - Neural networks

---

## 📦 Dependencies

```
torch>=2.0.0
transformers>=4.30.0
streamlit>=1.28.0
python-dotenv>=1.0.0
huggingface-hub>=0.17.0
```

See `requirements.txt` for complete list.

---

## ⚙️ Configuration

The app uses a public BART model by default. To customize:

1. **Edit `.env` file:**
   ```
   MODEL_PATH=facebook/bart-large-cnn
   APP_TITLE=Text Summarizer Pro
   DEBUG_MODE=false
   LOG_LEVEL=INFO
   ```

2. **Or use environment variables:**
   ```bash
   export MODEL_PATH=your-model-name
   streamlit run app.py
   ```

---

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Connect your GitHub repository
4. Deploy with one click!

### Docker

```bash
docker build -t text-summarizer .
docker run -p 8501:8501 text-summarizer
```

### Other Platforms

- **Heroku** - Deploy from GitHub
- **Railway.app** - Simple cloud deployment
- **AWS/Google Cloud** - Full control & scaling

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### App runs slowly
- The first run downloads the model (~1.5GB)
- Subsequent runs are faster
- GPU acceleration speeds up processing

### Out of memory
- Try shorter texts
- Reduce `NUM_BEAMS` in code
- Use a smaller model

### Port 8501 already in use
```bash
streamlit run app.py --server.port 8502
```

---

## 📊 Example

**Input:**
```
Artificial intelligence is transforming industries...
(long text here...)
```

**Output:**
```
AI is revolutionizing how businesses operate by automating tasks 
and improving decision-making processes across sectors.
```

**Statistics:**
- Original: 2,500 chars → Summary: 250 chars
- Compression: 10% of original length
- Time saved: ~10 minutes reading time

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📞 Support

- **Issues:** Use GitHub Issues for bug reports
- **Questions:** Open a Discussion on GitHub
- **Documentation:** Check the main README

---

## ✅ Key Highlights

✨ **No credit card needed** - Free to use online  
✨ **Privacy first** - Process text locally  
✨ **Fast & accurate** - AI-powered summarization  
✨ **Easy to deploy** - Works anywhere  
✨ **Production ready** - Professional quality code  

---

## 🔗 Links

- **Live App:** https://share.streamlit.io/thakursamir0000-star/text-summarization
- **GitHub:** https://github.com/thakursamir0000-star/text-summarization
- **BART Model:** https://huggingface.co/facebook/bart-large-cnn
- **Streamlit Docs:** https://docs.streamlit.io/

---

## 📈 Performance

Typical processing times on standard hardware:

| Text Length | Time |
|-------------|------|
| 500 chars | ~2-3 seconds |
| 2,000 chars | ~3-5 seconds |
| 5,000 chars | ~5-8 seconds |

*Times may vary based on hardware and internet speed*

---

**Made with ❤️ for better reading**