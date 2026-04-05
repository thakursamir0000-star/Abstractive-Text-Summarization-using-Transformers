"""Configuration management for the text summarization app."""

import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load .env file so all os.getenv() calls pick up the values
load_dotenv()

# Get the root directory
ROOT_DIR = Path(__file__).parent.parent

# Model configuration
# Prefer the local fine-tuned model when it exists, otherwise fall back to HF Hub
_local_model = ROOT_DIR / "fine_tuned_bart_model"
_default_model = str(_local_model) if _local_model.exists() else "facebook/bart-large-cnn"
MODEL_PATH = os.getenv("MODEL_PATH", _default_model)
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 1024))
MAX_SUMMARY_LENGTH = int(os.getenv("MAX_SUMMARY_LENGTH", 150))
MIN_SUMMARY_LENGTH = int(os.getenv("MIN_SUMMARY_LENGTH", 40))
NUM_BEAMS = int(os.getenv("NUM_BEAMS", 4))

# App configuration
APP_TITLE = "Text Summarization using BART"
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validation
MIN_TEXT_LENGTH = 50  # Minimum characters for valid input
MAX_TEXT_LENGTH = 100000  # Maximum characters for input


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
    return logger
