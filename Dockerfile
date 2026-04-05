FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# HF Spaces uses port 7860
EXPOSE 7860

# Default to public BART model (override via Space secret MODEL_PATH)
ENV MODEL_PATH=facebook/bart-large-cnn

CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
