# AWS App Runner Deployment Guide

Follow these steps to deploy your Enterprise RAG System to AWS App Runner for a recruiter-ready showcase.

## 1. Local Verification
First, build and run your image locally to ensure the index is properly packaged:
```bash
docker build -t enterprise-rag .
docker run -p 8501:8501 -e GROQ_API_KEY=your_key_here enterprise-rag
```
Visit `http://localhost:8501` to verify.

## 2. Push to AWS ECR
You need to push your image to the Amazon Elastic Container Registry.

1. **Create Repository**:
   ```bash
   aws ecr create-repository --repository-name enterprise-rag --region your-region
   ```
2. **Login to ECR**:
   ```bash
   aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<your-region>.amazonaws.com
   ```
3. **Tag & Push**:
   ```bash
   docker tag enterprise-rag:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/enterprise-rag:latest
   docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/enterprise-rag:latest
   ```

## 3. Create App Runner Service
1. Go to **AWS Console** → **App Runner**.
2. Click **Create service**.
3. **Source**:
   - Repository type: **Container registry**.
   - Provider: **Amazon ECR**.
   - Container image: Select your `enterprise-rag` image.
   - Deployment settings: **Manual** (or Automatic if you want CI/CD).
4. **Configuration**:
   - Service name: `enterprise-rag-showcase`.
   - Virtual CPU & Memory: **1 vCPU & 2 GB** (Minimum recommended).
   - **Environment variables**:
     - `GROQ_API_KEY`: Paste your key here.
5. **Connectivity**:
   - Port: **8501**.
6. **Review & Create**.

## 4. Final Result
Once deployed, AWS will provide a public URL like `https://xxxxxx.us-east-1.awsapprunner.com`. This is the URL you can share with recruiters!
