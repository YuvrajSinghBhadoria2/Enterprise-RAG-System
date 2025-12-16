# Hugging Face Spaces Deployment Guide

## Quick Deploy to Hugging Face Spaces

### Step 1: Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in details:
   - **Owner**: `yuvis` (your username)
   - **Space name**: `enterprise-rag-system`
   - **License**: MIT
   - **Select SDK**: **Streamlit**
   - **Space hardware**: CPU basic (free) or upgrade for better performance

### Step 2: Connect Your Repository

**Option A: Direct Git Push**
```bash
# Clone your new Space
git clone https://huggingface.co/spaces/yuvis/enterprise-rag-system
cd enterprise-rag-system

# Copy files from this project
cp -r /path/to/enterprise-rag/* .

# Push to HF
git add .
git commit -m "Initial deployment"
git push
```

**Option B: Link GitHub Repository**
1. In Space settings, go to **"Files and versions"**
2. Click **"Import from GitHub"**
3. Enter: `https://github.com/YuvrajSinghBhadoria2/Enterprise-RAG-System`

### Step 3: Configure Environment Variables

1. Go to **Space Settings** → **Variables and secrets**
2. Add secret:
   - **Name**: `GROQ_API_KEY`
   - **Value**: `gsk_your_key_here`

### Step 4: Generate Data (One-time)

Since HF Spaces has persistent storage, you need to generate data once:

1. Go to **"Files and versions"** → **"Terminal"** (if available)
2. Or add a startup script:

Create `startup.sh`:
```bash
#!/bin/bash
if [ ! -d "data/index" ]; then
    echo "Generating initial data..."
    python3 tools/generate-dataset.py
    python3 src/ingestion/ingest.py
fi
```

### Step 5: Access Your Space

Your app will be live at:
`https://huggingface.co/spaces/yuvis/enterprise-rag-system`

## Files Required for HF Spaces

✅ `app.py` - Main Streamlit application (already created)
✅ `requirements.txt` - Python dependencies (already exists)
✅ `README.md` - Space description (rename `README_HF.md` to `README.md`)

## Troubleshooting

**Space fails to build?**
- Check `requirements.txt` for incompatible versions
- Ensure `GROQ_API_KEY` is set in secrets

**Out of memory?**
- Upgrade to a better hardware tier (Settings → Hardware)
- Consider using CPU-only versions of ML libraries

**Data not persisting?**
- HF Spaces has persistent storage in `/data` directory
- Move your `data/` folder there for persistence
