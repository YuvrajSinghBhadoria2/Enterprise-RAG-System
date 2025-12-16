# AWS Free Tier Deployment - Enterprise RAG System

## ✅ Perfect for Free Tier!

Your Enterprise RAG system can run on AWS Free Tier with these optimizations.

## Free Tier Limits (12 months)
- ✅ 750 hours/month of t2.micro EC2 (enough for 24/7)
- ✅ 30GB EBS storage
- ✅ 15GB data transfer out

## Quick Deploy (Free Tier)

### Step 1: Launch t2.micro Instance

1. **AWS Console** → **EC2** → **Launch Instance**
2. **Configure:**
   - **Name**: `enterprise-rag`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**: **t2.micro** (1GB RAM - Free tier eligible)
   - **Key pair**: Create new or use existing
   - **Storage**: 20GB gp3 (within free tier)
   
3. **Security Group** (Important!):
   - SSH (22): Your IP only
   - Custom TCP (8501): 0.0.0.0/0 (Streamlit UI)
   - Custom TCP (8000): 0.0.0.0/0 (API)

4. **Launch Instance**

### Step 2: Connect to Instance

```bash
# Download your key pair (e.g., enterprise-rag-key.pem)
chmod 400 enterprise-rag-key.pem

# Connect
ssh -i enterprise-rag-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Re-login to apply docker group
exit
# SSH back in
```

### Step 4: Deploy Application

```bash
# Clone repository
git clone https://github.com/YuvrajSinghBhadoria2/Enterprise-RAG-System.git
cd Enterprise-RAG-System

# Create environment file
nano .env
# Add this line:
# GROQ_API_KEY=your_actual_groq_key_here
# Save: Ctrl+O, Enter, Ctrl+X

# Build and run (optimized for t2.micro)
docker build -f Dockerfile -t enterprise-rag .

# Run with memory limits for t2.micro
docker run -d \
  --name enterprise-rag \
  --env-file .env \
  -p 8501:8501 \
  --memory="900m" \
  --memory-swap="1g" \
  enterprise-rag
```

### Step 5: Generate Data

```bash
# Enter container
docker exec -it enterprise-rag bash

# Generate dataset (this will take a few minutes)
python3 tools/generate-dataset.py
python3 src/ingestion/ingest.py

# Exit container
exit
```

### Step 6: Access Your App

Your app is now live at:
- **UI**: `http://YOUR_EC2_PUBLIC_IP:8501`
- **API**: `http://YOUR_EC2_PUBLIC_IP:8000/docs`

Replace `YOUR_EC2_PUBLIC_IP` with your actual EC2 public IP from AWS console.

## Important Notes for Free Tier

### Memory Optimization
t2.micro has only 1GB RAM. The app is configured to run within this limit by:
- Using BM25-only mode (no FAISS)
- Memory limits on Docker container
- Optimized model loading

### Cost Monitoring
- ✅ **Free**: EC2 t2.micro (750 hours/month)
- ✅ **Free**: 30GB storage
- ⚠️ **Watch**: Data transfer (15GB free/month)

### Keep Costs $0
1. Stop instance when not in use (doesn't count toward 750 hours)
2. Delete instance before 12 months to avoid charges
3. Monitor data transfer in CloudWatch

## Troubleshooting

**Out of Memory?**
```bash
# Check memory usage
docker stats enterprise-rag

# Restart container
docker restart enterprise-rag
```

**Container crashed?**
```bash
# View logs
docker logs enterprise-rag

# Restart
docker start enterprise-rag
```

**Can't connect?**
- Check Security Group allows port 8501
- Verify EC2 instance is running
- Check public IP hasn't changed

## Maintenance

**Update code:**
```bash
cd Enterprise-RAG-System
git pull
docker stop enterprise-rag
docker rm enterprise-rag
docker build -f Dockerfile -t enterprise-rag .
docker run -d --name enterprise-rag --env-file .env -p 8501:8501 --memory="900m" enterprise-rag
```

**View logs:**
```bash
docker logs -f enterprise-rag
```

## Next Steps

1. ✅ Deploy on Free Tier EC2
2. ✅ Test your app
3. ✅ Share the public URL
4. ✅ Add to your resume!

Your Enterprise RAG system is now running on AWS for **FREE**! 🎉
