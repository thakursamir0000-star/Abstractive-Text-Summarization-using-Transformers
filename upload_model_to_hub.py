"""
Upload the local fine_tuned_bart_model/ folder to the Hugging Face Hub.

    huggingface-cli login            # once; or set HF_TOKEN in the environment / .env
    python upload_model_to_hub.py --repo your-name/bart-text-summarizer

The token is never passed on the command line, so it does not end up in shell history.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi

LOCAL_MODEL_DIR = Path(__file__).parent / "fine_tuned_bart_model"
DEFAULT_REPO = "samirthakur345/bart-text-summarizer"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=DEFAULT_REPO, help="Hub repo id, e.g. user/model-name")
    parser.add_argument("--private", action="store_true")
    args = parser.parse_args()

    if not LOCAL_MODEL_DIR.exists():
        sys.exit(f"Model folder not found: {LOCAL_MODEL_DIR}")

    load_dotenv()
    api = HfApi(token=os.getenv("HF_TOKEN"))  # None falls back to the `huggingface-cli login` token
    api.create_repo(args.repo, private=args.private, exist_ok=True)
    print(f"Uploading {LOCAL_MODEL_DIR} (about 1.6 GB) to https://huggingface.co/{args.repo} ...")
    api.upload_folder(folder_path=str(LOCAL_MODEL_DIR), repo_id=args.repo, commit_message="Upload model")
    print("Done. To use it in the app, set MODEL_PATH=" + args.repo)


if __name__ == "__main__":
    main()
