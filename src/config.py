"""Settings for the summarization app, read from environment variables (or .env)."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
LOCAL_MODEL_DIR = ROOT_DIR / "fine_tuned_bart_model"

BASE_MODEL = "facebook/bart-large-cnn"
FAST_MODEL = "sshleifer/distilbart-cnn-12-6"

# Models offered in the app: label -> Hugging Face Hub id or local folder.
MODEL_CHOICES = {
    "BART large CNN (best quality)": BASE_MODEL,
    "DistilBART CNN 12-6 (faster)": FAST_MODEL,
}
if LOCAL_MODEL_DIR.exists():
    MODEL_CHOICES["Local fine-tuned BART (experiment)"] = str(LOCAL_MODEL_DIR)

MODEL_PATH = os.getenv("MODEL_PATH", BASE_MODEL)
if MODEL_PATH not in MODEL_CHOICES.values():
    MODEL_CHOICES = {f"Custom: {MODEL_PATH}": MODEL_PATH, **MODEL_CHOICES}

# Longest input the model reads in one pass; longer text is split into chunks.
MAX_INPUT_TOKENS = int(os.getenv("MAX_INPUT_TOKENS", 1024))
CHUNK_OVERLAP_TOKENS = int(os.getenv("CHUNK_OVERLAP_TOKENS", 64))
NUM_BEAMS = int(os.getenv("NUM_BEAMS", 4))

# Summary length presets as (min, max) tokens. "Standard" is the setting
# bart-large-cnn was published and evaluated with.
LENGTH_PRESETS = {
    "Short": (20, 60),
    "Standard": (56, 142),
    "Detailed": (100, 220),
}
DEFAULT_LENGTH = "Standard"

MIN_TEXT_CHARS = 50
MAX_TEXT_CHARS = 100_000

APP_TITLE = "Text Summarizer"
REPO_URL = "https://github.com/thakursamir0000-star/Abstractive-Text-Summarization-using-Transformers"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
        logger.propagate = False  # avoid duplicate lines when a library configures the root logger
    return logger
