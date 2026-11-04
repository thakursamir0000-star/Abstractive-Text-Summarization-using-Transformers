FROM python:3.11-slim

# Hugging Face Spaces runs containers as user 1000; never run as root.
RUN useradd --create-home --uid 1000 user
WORKDIR /home/user/app

# CPU-only PyTorch: the default CUDA build is several GB larger, and the free
# Spaces / most servers have no GPU. requirements.txt then sees torch as installed.
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .
USER user

ENV HF_HOME=/home/user/.cache/huggingface \
    MODEL_PATH=facebook/bart-large-cnn \
    PYTHONUNBUFFERED=1

# HF Spaces uses port 7860
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/_stcore/health')"

CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
