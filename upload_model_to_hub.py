"""
Login to Hugging Face and upload the fine-tuned BART model.
Usage:  python login_and_upload.py
You will be prompted to paste your HF write token.
"""

import sys
from pathlib import Path

from huggingface_hub import login, HfApi
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ── Configuration ──────────────────────────────────────────────────────────────
LOCAL_MODEL_DIR = Path(__file__).parent / "fine_tuned_bart_model"
HF_REPO_ID      = "samirthakur345/bart-text-summarizer"
PRIVATE         = False
# ───────────────────────────────────────────────────────────────────────────────


def main():
    # ── Step 1: Login ──────────────────────────────────────────────────────────
    print("=" * 60)
    print("  Hugging Face Hub — Model Upload")
    print("=" * 60)
    print()

    if len(sys.argv) < 2:
        print("Usage: python upload_model_to_hub.py YOUR_HF_TOKEN")
        print("Get token: https://huggingface.co/settings/tokens")
        sys.exit(1)

    token = sys.argv[1].strip()
    login(token=token)
    print("✅ Logged in to Hugging Face Hub")
    print()

    # ── Step 2: Validate local model ───────────────────────────────────────────
    if not LOCAL_MODEL_DIR.exists():
        print(f"❌ Model directory not found: {LOCAL_MODEL_DIR}")
        sys.exit(1)

    print(f"📦 Loading model from: {LOCAL_MODEL_DIR}")
    print("   (This may take a minute — model is ~1.6 GB)")
    tokenizer = AutoTokenizer.from_pretrained(str(LOCAL_MODEL_DIR))
    model = AutoModelForSeq2SeqLM.from_pretrained(
        str(LOCAL_MODEL_DIR),
        low_cpu_mem_usage=False,
    )
    print("✅ Model loaded")
    print()

    # ── Step 3: Push to Hub ────────────────────────────────────────────────────
    print(f"🚀 Uploading to: https://huggingface.co/{HF_REPO_ID}")
    print("   Uploading tokenizer...")
    tokenizer.push_to_hub(HF_REPO_ID, private=PRIVATE)
    print("   Uploading model weights (~1.6 GB, please wait)...")
    model.push_to_hub(HF_REPO_ID, private=PRIVATE)

    print()
    print("=" * 60)
    print("✅ Upload complete!")
    print(f"   Model URL  : https://huggingface.co/{HF_REPO_ID}")
    print()
    print("📋 NEXT STEPS — Streamlit Community Cloud:")
    print("   1. Go to https://share.streamlit.io")
    print("   2. Click 'New app'")
    print("   3. Repo   : thakursamir0000-star/Abstractive-Text-Summarization-using-Transformers")
    print("   4. Branch : main")
    print("   5. File   : app.py")
    print("   6. Advanced settings → Secrets → paste:")
    print()
    print(f'      MODEL_PATH = "{HF_REPO_ID}"')
    print()
    print("   7. Click Deploy 🚀")
    print("=" * 60)


if __name__ == "__main__":
    main()
