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
    
    from pathlib import Path
    local_path = Path(model_path)

    # Check if it's a real local directory with model files
    if local_path.exists() and local_path.is_dir():
        logger.info(f"✓ Using local fine-tuned model: {model_path}")
        return str(local_path)
    
    # Otherwise treat as a Hugging Face Hub model ID (e.g. "facebook/bart-large-cnn")
    logger.info(f"✓ Using Hugging Face Hub model: {model_path}")
    return model_path


if __name__ == "__main__":
    # Test
    model = setup_model()
    print(f"Model: {model}")

