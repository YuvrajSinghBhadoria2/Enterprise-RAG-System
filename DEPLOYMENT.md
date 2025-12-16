# Deployment Guide

 This guide ensures a smooth deployment of the Enterprise RAG system to any cloud VPS (Virtual Private Server) such as AWS EC2, DigitalOcean Droplet, Google Compute Engine, or Azure VM.

## 🚀 Prerequisites

*   **Server**: A Linux server (Ubuntu 22.04 LTS recommended).
*   **Specs**: Minimum 4GB RAM (8GB recommended for embeddings/FAISS), 2 vCPUs.
*   **Software**: Docker and Docker Compose installed.

## � Recommended Providers

For this Docker-based application, we recommend a **Virtual Private Server (VPS)** for full control and cost-effectiveness:

1.  **DigitalOcean** (Recommended):
    *   **Product**: Basic Droplet
    *   **Size**: 4GB RAM / 2 CPU (approx $24/mo)
    *   **OS**: Ubuntu 24.04 LTS Docker
    *   *Why? Easiest to set up, one-click Docker pre-installed.*

2.  **AWS (Amazon Web Services)**:
    *   **Product**: EC2 (t3.medium) or Lightsail
    *   **Why?** Enterprise standard, reliable global availability.

3.  **Google Cloud Platform**:
    *   **Product**: Compute Engine (e2-medium)

4.  **Railway.app** (Easiest PaaS):
    *   Perfect for quick demos.
    *   Supports our `Dockerfile` setup out of the box.

## 🚂 Railway.app Deployment (PaaS)

Railway is great for deploying without managing a server. You will deploy two separate services: **API** and **UI**.

### 1. Prerequisites
*   Fork this repository to your GitHub account.
*   Sign up at [Railway.app](https://railway.app).

### 2. Deploy API Service
1.  **New Project** -> **Deploy from GitHub repo** -> Select `enterprise-rag`.
2.  Click the specific service card to configure it.
3.  **Settings** -> **Build**:
    *   **Dockerfile Path**: `docker/Dockerfile.api`
4.  **Variables**:
    *   `GROQ_API_KEY`: `gsk_...`
    *   `PORT`: `8000`
5.  **Build & Deploy**: Click Deploy.
6.  **Data Generation** (Critical):
    *   Since Railway is ephemeral, you need to generate data on startup or use a Volume.
    *   **Easiest way for Demo**: Update "Start Command" in settings to:
        ```bash
        python3 tools/generate-dataset.py && python3 src/ingestion/ingest.py && uvicorn src.app.main:app --host 0.0.0.0 --port 8000
        ```
    *   *Note: This regenerates the index on every restart (takes ~30s).*

### 3. Deploy UI Service
1.  In the same project, click **+ New** -> **GitHub Repo** -> `enterprise-rag` (Again).
2.  **Settings** -> **Build**:
    *   **Dockerfile Path**: `docker/Dockerfile.streamlit`
3.  **Variables**:
    *   `API_URL`: Use the **Public Domain** (or private internal URL) of your API service (e.g., `https://web-production-1234.up.railway.app/api/v1/chat`).
4.  **Deploy**.

### 4. Verified
Open your UI Service URL. It should connect to the API and serve answers.

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
