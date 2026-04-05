"""Tests for the text summarization model."""

import pytest
from src.model import SummarizationModel, summarize
from src.config import get_logger


class TestSummarizationModel:
    """Test suite for SummarizationModel class."""

    @pytest.fixture
    def model(self):
        """Fixture to provide a model instance."""
        return SummarizationModel()

    def test_model_initialization(self, model):
        """Test that model initializes successfully."""
        assert model is not None
        assert model.tokenizer is not None
        assert model.model is not None

    def test_validate_input_valid_text(self, model):
        """Test validation with valid text."""
        valid_text = "This is a valid text that is long enough to be summarized properly."
        is_valid, error = model.validate_input(valid_text)
        assert is_valid is True
        assert error is None

    def test_validate_input_empty_text(self, model):
        """Test validation with empty text."""
        is_valid, error = model.validate_input("")
        assert is_valid is False
        assert error is not None

    def test_validate_input_too_short(self, model):
        """Test validation with text that's too short."""
        short_text = "Too short"
        is_valid, error = model.validate_input(short_text)
        assert is_valid is False
        assert "50 characters" in error

    def test_validate_input_too_long(self, model):
        """Test validation with text that exceeds maximum length."""
        long_text = "a" * 100001
        is_valid, error = model.validate_input(long_text)
        assert is_valid is False
        assert "100,000 characters" in error

    def test_validate_input_with_whitespace(self, model):
        """Test validation with extra whitespace."""
        text = "   This is valid text with extra spaces.   " * 2
        is_valid, error = model.validate_input(text)
        assert is_valid is True

    def test_summarize_valid_text(self, model):
        """Test summarization with valid text."""
        text = """
        Artificial intelligence is transforming the world. Machine learning models
        are being used in various applications from healthcare to finance. These models
        help in predicting patterns, automating tasks, and making better decisions.
        The future of AI is promising with continuous improvements and innovations.
        """
        summary = model.summarize(text)
        assert summary is not None
        assert len(summary) > 0
        assert isinstance(summary, str)

    def test_summarize_invalid_text_raises_valueerror(self, model):
        """Test that summarization raises ValueError for invalid text."""
        with pytest.raises(ValueError):
            model.summarize("Too short")

    def test_singleton_pattern(self):
        """Test that SummarizationModel follows singleton pattern."""
        model1 = SummarizationModel()
        model2 = SummarizationModel()
        assert model1 is model2

    def test_device_selection(self, model):
        """Test that device is properly selected."""
        assert model.device in ["cuda", "cpu"]


class TestModuleLevelFunctions:
    """Test module-level functions."""

    def test_summarize_function(self):
        """Test the module-level summarize function."""
        text = """
        Python is a popular programming language. It is known for its simplicity
        and readability. Python is used in web development, data science, and
        artificial intelligence. Many frameworks like Django and Flask are built
        with Python, making it a preferred choice for developers worldwide.
        """
        summary = summarize(text)
        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_summarize_raises_valueerror_for_invalid_input(self):
        """Test that summarize raises ValueError for invalid input."""
        with pytest.raises(ValueError):
            summarize("invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
