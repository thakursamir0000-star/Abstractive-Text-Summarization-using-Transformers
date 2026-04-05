"""Utility functions for the summarization app."""

import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize input text.

    Args:
        text: Raw input text

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = " ".join(text.split())
    # Remove special characters but keep basic punctuation
    text = re.sub(r"[^\w\s\.\,\!\?\-\'\"]", "", text)
    return text


def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Input text
        max_length: Maximum length in characters

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def estimate_reading_time(text: str) -> int:
    """
    Estimate reading time in minutes.

    Args:
        text: Input text

    Returns:
        Estimated reading time in minutes
    """
    words = len(text.split())
    # Average reading speed is ~200 words per minute
    return max(1, words // 200)
