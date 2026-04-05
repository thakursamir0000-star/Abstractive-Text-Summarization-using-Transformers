# 🚀 Model Deployment Guide

## Problem
Your `fine_tuned_bart_model/` folder is too large for GitHub. Here's the best solution implemented:

## ✅ Solution: Git LFS + HF Hub Fallback

We've set up your app to:
1. **Use local model** if it exists (for local development)
2. **Auto-download from Hugging Face Hub** if running on cloud platforms

## 📋 For Cloud Deployment (Streamlit Cloud / HF Spaces)

### Step 1: Upload Your Model to Hugging Face Hub

1. **Create HF Account** (free): https://huggingface.co/
2. **Create a new repository**:
   - Go to https://huggingface.co/new
   - Name it: `my-text-summarizer` (or any name)
   - Choose "Model" as type
   - Create repository

3. **Upload your model files**:
   ```bash
   # Option A: Using Git LFS (recommended)
   git clone https://huggingface.co/your-username/my-text-summarizer
   cd my-text-summarizer
   git lfs install
   
   # Copy your model files
   cp -r /path/to/fine_tuned_bart_model/* .
   
   # Upload
   git add .
   git commit -m "Add model"
   git push
   ```

   **Option B: Using web UI** (easier):
   - Go to your repo on HF Hub
   - Click "Add file" → "Upload files"
   - Select: `config.json`, `model.safetensors`, `tokenizer.json`, etc.

### Step 2: Update Your `.env` File

```bash
# In your Streamlit Cloud/HF Spaces .env file, set:
MODEL_PATH=your-username/my-text-summarizer
```

### Step 3: Deploy!

Your app will automatically download the model on first run. ✅

---

## 💻 For Local Development

Keep using the local folder:
```bash
MODEL_PATH=./fine_tuned_bart_model
```

### Setup Git LFS (Optional but recommended)

```bash
# Install Git LFS
git lfs install

# This will automatically track large files
git add fine_tuned_bart_model/
git commit -m "Add model with Git LFS"
git push
```

---

## 🔑 Alternative: Use Pre-existing HF Model

If you want to use a public model instead:
```bash
# In .env:
MODEL_PATH=facebook/bart-large-cnn  # Any HF model
```

---

## 📝 Summary

| Where | MODEL_PATH Setting | What Happens |
|-------|-------------------|--------------|
| **Local (PC)** | `./fine_tuned_bart_model` | Uses local files |
| **Cloud (Streamlit/HF)** | `your-username/my-model` | Auto-downloads from HF Hub |
| **Cloud (any HF model)** | `facebook/bart-large-cnn` | Uses public HF model |

---

## 🆘 Troubleshooting

**Error: "Model not found"**
- Make sure `MODEL_PATH` is set correctly in `.env`
- If using HF Hub, check the model ID: `https://huggingface.co/your-username/your-model`

**Error: "huggingface-hub not installed"**
- Already added to requirements.txt ✅

**Large file not pushing to GitHub**
- Use Git LFS: `git lfs install && git add fine_tuned_bart_model/`

---

**Questions?** See README.md or check Hugging Face Hub documentation.
