"""Model setup and management utilities."""

import os
import logging

logger = logging.getLogger(__name__)


def setup_model(model_path: str = None) -> str:
    """
    Get the model path - handles both local and HF Hub models.
    
    Args:
        model_path: Local model path or HF Hub model ID
        
    Returns:
        Model path/ID to use with transformers
    """
    if model_path is None:
        model_path = os.getenv("MODEL_PATH", "facebook/bart-large-cnn")
    
    # For HF Hub models (contains "/" or doesn't look like a local path)
    if "/" in model_path:
        logger.info(f"✓ Using Hugging Face model: {model_path}")
        return model_path
    
    # For local paths - just return as is
    logger.info(f"✓ Using model from: {model_path}")
    return model_path


if __name__ == "__main__":
    # Test
    model = setup_model()
    print(f"Model: {model}")

