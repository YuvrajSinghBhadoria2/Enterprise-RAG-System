
import os
import sys
from huggingface_hub import hf_hub_download

# Config
REPO_ID = "yuvis/enterprise-rag-index"
DATA_DIR = "data"
INDEX_DIR = "data/index"

def download_index():
    print(f"🚀 Downloading index from {REPO_ID}...")
    
    # Create directory
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    try:
        # Download BM25
        print("Downloading BM25 Index...")
        hf_hub_download(
            repo_id=REPO_ID,
            filename="index/bm25.pkl",
            repo_type="dataset",
            local_dir=DATA_DIR,
            local_dir_use_symlinks=False
        )
        
        # Download Doc Map
        print("Downloading Metadata Map...")
        hf_hub_download(
            repo_id=REPO_ID,
            filename="index/doc_map.pkl",
            repo_type="dataset",
            local_dir=DATA_DIR,
            local_dir_use_symlinks=False
        )
        print("✅ Download complete! Files baked into image.")
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_index()
