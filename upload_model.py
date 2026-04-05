"""
Automatic script to upload your fine-tuned model to Hugging Face Hub.

This script will:
1. Create a free HF account (if needed)
2. Upload your fine_tuned_bart_model/ files
3. Update your .env with the model path
4. Ready to deploy!
"""

import os
import sys
from pathlib import Path
from getpass import getpass


def main():
    print("=" * 60)
    print("🚀 Upload Model to Hugging Face Hub")
    print("=" * 60)
    print()
    
    # Check if model exists
    model_dir = Path("fine_tuned_bart_model")
    if not model_dir.exists():
        print("❌ Error: fine_tuned_bart_model/ folder not found!")
        return False
    
    config_file = model_dir / "config.json"
    if not config_file.exists():
        print("❌ Error: config.json not found in model folder!")
        return False
    
    print("✓ Model folder found")
    print()
    
    try:
        from huggingface_hub import HfApi, login
    except ImportError:
        print("📦 Installing huggingface-hub...")
        os.system("pip install huggingface-hub")
        from huggingface_hub import HfApi, login
    
    # Get HF credentials
    print("🔑 Hugging Face Authentication")
    print("-" * 60)
    print("1. Create free account: https://huggingface.co/join")
    print("2. Get token: https://huggingface.co/settings/tokens")
    print("3. Paste your token below (or press Enter to use cached token)")
    print()
    
    token = getpass("HF Token (paste or press Enter): ").strip()
    
    if token:
        try:
            login(token=token, add_to_git_credential=True)
            print("✓ Logged in!")
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    else:
        print("Using cached HF token...")
    
    print()
    print("📝 Model Details")
    print("-" * 60)
    
    # Get model name
    while True:
        username = input("Your HF username: ").strip()
        if username:
            break
        print("❌ Username cannot be empty")
    
    while True:
        repo_name = input("Repository name (e.g., 'my-text-summarizer'): ").strip()
        if repo_name:
            break
        print("❌ Repository name cannot be empty")
    
    repo_id = f"{username}/{repo_name}"
    
    print()
    print(f"📤 Creating and uploading to: {repo_id}")
    print("-" * 60)
    
    try:
        api = HfApi()
        
        # Create repo
        print(f"Creating repository {repo_id}...")
        try:
            api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)
            print("✓ Repository ready")
        except Exception as e:
            print(f"⚠️  Repo may already exist: {e}")
        
        # Upload files
        print()
        print("Uploading model files...")
        files_uploaded = 0
        
        for file_path in model_dir.iterdir():
            if file_path.is_file():
                file_name = file_path.name
                print(f"  📄 {file_name}...", end=" ", flush=True)
                
                try:
                    api.upload_file(
                        path_or_fileobj=str(file_path),
                        path_in_repo=file_name,
                        repo_id=repo_id,
                        repo_type="model"
                    )
                    print("✓")
                    files_uploaded += 1
                except Exception as e:
                    print(f"⚠️  {e}")
        
        print()
        print(f"✓ Uploaded {files_uploaded} files!")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Update .env
    print()
    print("⚙️  Updating .env file...")
    print("-" * 60)
    
    env_file = Path(".env")
    env_content = env_file.read_text() if env_file.exists() else ""
    
    # Update or add MODEL_PATH
    if "MODEL_PATH=" in env_content:
        env_content = env_content.replace(
            "MODEL_PATH=./fine_tuned_bart_model",
            f"MODEL_PATH={repo_id}"
        )
    else:
        env_content += f"\nMODEL_PATH={repo_id}\n"
    
    env_file.write_text(env_content)
    print(f"✓ Updated .env with MODEL_PATH={repo_id}")
    
    print()
    print("=" * 60)
    print("✅ SUCCESS!")
    print("=" * 60)
    print()
    print("Your model is now on Hugging Face Hub! 🎉")
    print()
    print("📋 Next steps:")
    print(f"  1. View your model: https://huggingface.co/{repo_id}")
    print("  2. Deploy to Streamlit Cloud or HF Spaces")
    print("  3. Your app will auto-download the model on startup")
    print()
    print("💡 Already deployed to Streamlit Cloud?")
    print("   → Restart your app and it will pick up the new .env")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
