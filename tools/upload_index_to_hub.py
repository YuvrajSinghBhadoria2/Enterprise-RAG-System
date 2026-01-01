
import os
import sys

# Ensure src is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from huggingface_hub import HfApi, create_repo
import shutil

# Config
REPO_ID = "yuvis/enterprise-rag-index"
DATA_DIR = "data/index"

def upload_index():
    print(f"🚀 Preparing to upload index to {REPO_ID}...")
    
    # Check if index exists
    if not os.path.exists(DATA_DIR):
        print("❌ data/index directory not found. Please generate index first.")
        # Attempt generation? 
        # For now assume user generated it.
        return

    # Create Repo (if not exists)
    try:
        api = HfApi()
        api.create_repo(repo_id=REPO_ID, repo_type="dataset", exist_ok=True)
        print(f"✅ Repository {REPO_ID} checked/created.")
    except Exception as e:
        print(f"❌ Error creating repo: {e}")
        return

    # Compress if not already (Actually, Datasets handles large files well, but gzip saves bandwidth)
    # We will upload the raw .pkl files or .gz if present.
    
    print("📤 Uploading files...")
    try:
        api.upload_folder(
            folder_path=DATA_DIR,
            repo_id=REPO_ID,
            repo_type="dataset",
            path_in_repo="index"
        )
        print("✅ Upload complete!")
        print(f"🔗 https://huggingface.co/datasets/{REPO_ID}")

    except Exception as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    upload_index()
