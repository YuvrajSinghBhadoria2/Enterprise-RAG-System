# Deployment Guide

 This guide ensures a smooth deployment of the Enterprise RAG system to any cloud VPS (Virtual Private Server) such as AWS EC2, DigitalOcean Droplet, Google Compute Engine, or Azure VM.

## 🚀 Prerequisites

*   **Server**: A Linux server (Ubuntu 22.04 LTS recommended).
*   **Specs**: Minimum 4GB RAM (8GB recommended for embeddings/FAISS), 2 vCPUs.
*   **Software**: Docker and Docker Compose installed.

## � Recommended Providers

 **Railway.app** (Easiest PaaS):
    *   Perfect for quick demos.
    *   Supports our `Dockerfile` setup out of the box.

## 🚂 Railway.app Deployment (Complete Setup)

Railway requires deploying **two separate services** from the same repository.

### Prerequisites
*   GitHub repository: `https://github.com/YuvrajSinghBhadoria2/Enterprise-RAG-System.git`
*   Railway account: [railway.app](https://railway.app)
*   Groq API Key

### Step 1: Deploy API Service

1. **Create New Project** in Railway
2. **Deploy from GitHub** → Select your repository
3. Railway will auto-detect the `railway.toml` and use the Dockerfile
4. **Add Environment Variables**:
   ```
   GROQ_API_KEY=gsk_your_key_here
   PORT=8000
   ```
5. **Deploy** - Railway will build using `docker/Dockerfile.api`
6. **Get API URL** - Copy the public URL (e.g., `https://enterprise-rag-production.up.railway.app`)

### Step 2: Deploy UI Service

1. In the **same Railway project**, click **+ New Service**
2. **Deploy from GitHub** → Select the **same repository**
3. **Configure Build**:
   - Go to **Settings** → **Build**
   - Set **Dockerfile Path**: `docker/Dockerfile.streamlit`
4. **Add Environment Variable**:
   ```
   API_URL=https://your-api-url-from-step1.up.railway.app/api/v1/chat
   ```
   *(Replace with your actual API URL from Step 1)*
5. **Deploy**

### Step 3: Generate Data (Critical!)

Railway containers are ephemeral, so you need to generate data on startup:

**Option A: One-time manual generation** (for testing):
```bash
# In Railway API service shell
python3 tools/generate-dataset.py
python3 src/ingestion/ingest.py
```

**Option B: Auto-generate on startup** (recommended):
Update the `railway.toml` start command to include data generation.

### Step 4: Access Your Application

- **UI**: `https://your-ui-service.up.railway.app`
- **API Docs**: `https://your-api-service.up.railway.app/docs`

### Troubleshooting

**Build Timeout?**
- Ensure `.dockerignore` excludes `venv/` and `data/`
- Check that `railway.toml` points to the correct Dockerfile

**UI Can't Connect to API?**
- Verify `API_URL` environment variable in UI service
- Ensure API service is deployed and running
- Check API URL includes `/api/v1/chat` endpoint

---

## 📦 Step-by-Step Deployment (VPS)

### 1. Provision & Access Server
SSH into your server:
```bash
ssh user@your-server-ip
```

### 2. Install Docker (If not installed)
```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose Plugin
sudo apt install docker-compose-plugin
```

### 3. Clone the Repository
```bash
git clone https://github.com/your-repo/enterprise-rag.git
cd enterprise-rag
```

### 4. Configure Environment
Create the production `.env` file:
```bash
cp .env.example .env
nano .env
```
*Paste your `GROQ_API_KEY` or `OPENAI_API_KEY` into the file.*

### 5. Build and Start Services
This command will build the images and start the API and UI in the background with auto-restart enabled.
```bash
# Using the Makefile shortcut
make up

# OR manually using docker compose
docker compose -f docker/docker-compose.yml up -d --build
```

### 6. Generate Data (Critical Step)
Fresh deployments start empty. You must ingest the datasets to make the search work.
```bash
# Run ingestion inside the running API container
docker compose -f docker/docker-compose.yml exec api python3 tools/generate-dataset.py
docker compose -f docker/docker-compose.yml exec api python3 src/ingestion/ingest.py
```

### 7. Access the Application
*   **UI**: `http://your-server-ip:8501`
*   **API**: `http://your-server-ip:8000/docs`

---

## 🔒 Production Hardening

### 1. Firewall (UFW)
Only open necessary ports.
```bash
sudo ufw allow 22/tcp
sudo ufw allow 8501/tcp  # Streamlit
sudo ufw allow 8000/tcp  # API
sudo ufw enable
```

### 2. Reverse Proxy (Nginx + SSL)
For HTTPS, use Nginx as a reverse proxy.
```nginx
server {
    listen 80;
    server_name rag.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🛠️ Maintenance

*   **View Logs**: `make logs`
*   **Restart Services**: `make down && make up`
*   **Update Code**:
    ```bash
    git pull
    make up
    ```
