"""Text summarization model wrapper with error handling."""

import logging
from typing import Optional
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from src.config import (
    MODEL_PATH,
    MAX_INPUT_LENGTH,
    MAX_SUMMARY_LENGTH,
    MIN_SUMMARY_LENGTH,
    NUM_BEAMS,
    get_logger,
)
from src.model_setup import setup_model

logger = get_logger(__name__)


class SummarizationModel:
    """BART-based text summarization model."""

    _instance = None  # Singleton pattern to avoid reloading model

    def __new__(cls):
        """Implement singleton pattern to load model only once."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the model (only once due to singleton pattern)."""
        if self._initialized:
            return

        try:
            self._load_model()
            self._initialized = True
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    def _load_model(self) -> None:
        """Load tokenizer and model from the specified path."""
        try:
            # Get model path (HF Hub ID or local path)
            model_path = setup_model(MODEL_PATH)
            logger.info(f"Loading model: {model_path}")
        except Exception as e:
            logger.error(f"Model setup failed: {e}")
            raise

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        
        # Move to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        logger.info(f"Using device: {self.device}")

    def validate_input(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Validate input text.

        Args:
            text: Input text to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not isinstance(text, str):
            return False, "Input must be a non-empty text string."

        text = text.strip()
        
        if len(text) < 50:
            return False, "Text must be at least 50 characters long."
        
        if len(text) > 100000:
            return False, "Text exceeds maximum length of 100,000 characters."

        return True, None

    def summarize(self, text: str) -> str:
        """
        Generate a summary of the input text.

        Args:
            text: Input text to summarize

        Returns:
            Generated summary

        Raises:
            ValueError: If input validation fails
            RuntimeError: If summarization fails
        """
        # Validate input
        is_valid, error_msg = self.validate_input(text)
        if not is_valid:
            raise ValueError(error_msg)

        try:
            text = text.strip()
            logger.info(f"Summarizing text of length {len(text)}")

            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=MAX_INPUT_LENGTH,
                truncation=True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate summary
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs["input_ids"],
                    max_length=MAX_SUMMARY_LENGTH,
                    min_length=MIN_SUMMARY_LENGTH,
                    num_beams=NUM_BEAMS,
                    early_stopping=True,
                )

            # Decode summary
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            logger.info("Summarization completed successfully")
            
            return summary

        except RuntimeError as e:
            logger.error(f"Model inference failed: {str(e)}")
            raise RuntimeError(f"Failed to generate summary: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during summarization: {str(e)}")
            raise


# Module-level function for backward compatibility
_model = None


def get_model() -> SummarizationModel:
    """Get or initialize the summarization model."""
    global _model
    if _model is None:
        _model = SummarizationModel()
    return _model


def summarize(text: str) -> str:
    """
    Summarize input text using the BART model.

    Args:
        text: Input text to summarize

    Returns:
        Generated summary

    Raises:
        ValueError: If input validation fails
        RuntimeError: If summarization fails
    """
    model = get_model()
    return model.summarize(text)
