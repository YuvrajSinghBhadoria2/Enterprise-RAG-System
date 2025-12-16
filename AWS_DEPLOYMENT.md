# AWS Deployment Guide - Enterprise RAG System

## Prerequisites
- AWS Account
- AWS CLI installed and configured
- Docker installed locally

## Deployment Options

### Option 1: AWS EC2 (Recommended for Full Control)

#### Step 1: Launch EC2 Instance
1. Go to AWS Console → EC2
2. Click **"Launch Instance"**
3. Choose:
   - **AMI**: Ubuntu 22.04 LTS
   - **Instance Type**: t3.medium (4GB RAM minimum)
   - **Storage**: 20GB
4. Configure Security Group:
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 8501) from anywhere
   - Allow HTTP (port 8000) from anywhere

#### Step 2: Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

#### Step 3: Install Docker
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose-plugin
```

#### Step 4: Clone Repository
```bash
git clone https://github.com/YuvrajSinghBhadoria2/Enterprise-RAG-System.git
cd Enterprise-RAG-System
```

#### Step 5: Configure Environment
```bash
# Create .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
EOF
```

#### Step 6: Build and Run
```bash
# Using Docker Compose
docker compose -f docker/docker-compose.yml up -d --build

# Generate data (one-time)
docker compose -f docker/docker-compose.yml exec api python3 tools/generate-dataset.py
docker compose -f docker/docker-compose.yml exec api python3 src/ingestion/ingest.py
```

#### Step 7: Access Application
- **UI**: `http://your-ec2-public-ip:8501`
- **API**: `http://your-ec2-public-ip:8000/docs`

---

### Option 2: AWS ECS (Fargate) - Serverless

#### Step 1: Push Docker Image to ECR
```bash
# Create ECR repository
aws ecr create-repository --repository-name enterprise-rag

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -f docker/Dockerfile.api -t enterprise-rag .
docker tag enterprise-rag:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/enterprise-rag:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/enterprise-rag:latest
```

#### Step 2: Create ECS Task Definition
1. Go to ECS Console
2. Create new Task Definition (Fargate)
3. Add container:
   - Image: Your ECR image URI
   - Memory: 4GB
   - Port: 8501
4. Add environment variable: `GROQ_API_KEY`

#### Step 3: Create ECS Service
1. Create ECS Cluster
2. Create Service from Task Definition
3. Configure Load Balancer (optional)

---

### Option 3: AWS Lightsail (Simplest)

#### Step 1: Create Lightsail Instance
1. Go to Lightsail Console
2. Create Instance:
   - Platform: Linux/Unix
   - Blueprint: Ubuntu 22.04
   - Plan: $10/month (2GB RAM)

#### Step 2: Deploy
Same as EC2 steps 2-7 above

---

## Cost Estimates

| Service | Cost/Month | Best For |
|---------|-----------|----------|
| EC2 t3.medium | ~$30 | Full control, testing |
| ECS Fargate | ~$40 | Production, auto-scaling |
| Lightsail | $10-20 | Simple deployment |

## Recommended: EC2 t3.medium

For your use case, I recommend **EC2 t3.medium** because:
- ✅ Full control
- ✅ Easy to manage
- ✅ Cost-effective
- ✅ Can run Docker Compose easily

## Maintenance

**Update code:**
```bash
cd Enterprise-RAG-System
git pull
docker compose -f docker/docker-compose.yml up -d --build
```

**View logs:**
```bash
docker compose -f docker/docker-compose.yml logs -f
```

**Restart services:**
```bash
docker compose -f docker/docker-compose.yml restart
```
