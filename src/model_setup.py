"""Model setup and management utilities."""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def setup_model(model_path: Optional[str] = None) -> str:
    """
    Ensure model is available, download from HF Hub if needed.
    
    Args:
        model_path: Local model path or HF Hub model ID
        
    Returns:
        Path to the model directory
        
    Raises:
        FileNotFoundError: If model cannot be found or downloaded
    """
    if model_path is None:
        model_path = os.getenv("MODEL_PATH", "./fine_tuned_bart_model")
    
    model_dir = Path(model_path)
    
    # Check if local model exists
    if model_dir.exists() and (model_dir / "config.json").exists():
        logger.info(f"✓ Model found at {model_path}")
        return str(model_dir)
    
    # If path looks like HF Hub ID (contains "/" or is referenced in env)
    if "/" in model_path or model_path.startswith("models/"):
        logger.info(f"📥 Downloading model from Hugging Face Hub: {model_path}")
        return download_from_hub(model_path)
    
    # Model not found locally and not a HF Hub ID
    logger.warning(f"⚠️ Model not found at {model_path}")
    logger.info("💡 Set MODEL_PATH to HF Hub model ID (e.g., 'username/model-name')")
    raise FileNotFoundError(
        f"Model not found at {model_path}. "
        "Either: 1) Upload model files, 2) Set MODEL_PATH to HF Hub model ID"
    )


def download_from_hub(model_id: str, local_dir: str = "fine_tuned_bart_model") -> str:
    """
    Download model from Hugging Face Hub.
    
    Args:
        model_id: Hugging Face model ID (e.g., 'username/model-name')
        local_dir: Local directory to save model
        
    Returns:
        Path to downloaded model
    """
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        raise ImportError(
            "huggingface-hub required for downloading models. "
            "Install with: pip install huggingface-hub"
        )
    
    try:
        logger.info(f"Downloading {model_id} to {local_dir}...")
        path = snapshot_download(model_id, local_dir=local_dir, repo_type="model")
        logger.info(f"✓ Model downloaded to {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        raise


if __name__ == "__main__":
    # Test script
    import sys
    try:
        path = setup_model()
        print(f"✅ Model ready at: {path}")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
