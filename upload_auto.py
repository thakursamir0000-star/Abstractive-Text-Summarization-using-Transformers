"""
Automated upload script - takes token as input.
"""

import os
import sys
from pathlib import Path


def main(token):
    print("=" * 60)
    print("🚀 Uploading Model to Hugging Face Hub")
    print("=" * 60)
    print()
    
    # Check model
    model_dir = Path("fine_tuned_bart_model")
    if not model_dir.exists() or not (model_dir / "config.json").exists():
        print("❌ Error: fine_tuned_bart_model/config.json not found!")
        return False
    
    print("✓ Model folder found")
    print()
    
    try:
        from huggingface_hub import HfApi, login
    except ImportError:
        print("📦 Installing huggingface-hub...")
        os.system("pip install huggingface-hub -q")
        from huggingface_hub import HfApi, login
    
    # Login with token
    print("🔑 Logging in with your token...")
    try:
        login(token=token, add_to_git_credential=True)
        print("✓ Logged in!")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False
    
    print()
    print("📝 Model Details")
    print("-" * 60)
    
    # Get user info
    username = input("Your HF username: ").strip()
    if not username:
        print("❌ Username required")
        return False
    
    repo_name = input("Repository name (e.g., 'my-bart-model'): ").strip()
    if not repo_name:
        print("❌ Repository name required")
        return False
    
    repo_id = f"{username}/{repo_name}"
    
    print()
    print(f"📤 Uploading to: {repo_id}")
    print("-" * 60)
    
    try:
        api = HfApi()
        
        # Create repo
        print(f"Creating repository {repo_id}...")
        try:
            api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, private=False)
            print("✓ Repository ready")
        except Exception as e:
            print(f"⚠️  {e}")
        
        # Upload files
        print()
        print("Uploading model files...")
        files_uploaded = 0
        
        for file_path in sorted(model_dir.iterdir()):
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
                    print(f"❌ {e}")
        
        print()
        print(f"✓ Uploaded {files_uploaded} files!")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Update .env
    print()
    print("⚙️  Updating .env file...")
    
    env_file = Path(".env")
    env_content = ""
    
    if env_file.exists():
        env_content = env_file.read_text()
    
    # Update MODEL_PATH
    if "MODEL_PATH=" in env_content:
        lines = env_content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("MODEL_PATH="):
                lines[i] = f"MODEL_PATH={repo_id}"
        env_content = "\n".join(lines)
    else:
        env_content += f"\nMODEL_PATH={repo_id}\n"
    
    env_file.write_text(env_content)
    print(f"✓ Updated .env")
    
    print()
    print("=" * 60)
    print("✅ SUCCESS!")
    print("=" * 60)
    print()
    print(f"Model URL: https://huggingface.co/{repo_id}")
    print(f"MODEL_PATH={repo_id}")
    print()
    print("🚀 Next: Redeploy your Streamlit Cloud app!")
    print()
    
    return True


if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else None
    if not token:
        print("❌ No token provided")
        sys.exit(1)
    
    try:
        success = main(token)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        sys.exit(1)
