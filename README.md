---
title: Enterprise RAG System
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.32.2"
app_file: app.py
pinned: false
---

# 🔍 Enterprise RAG System

> **A production-ready Retrieval Augmented Generation system featuring Hybrid Search, Reranking, and Hallucination Prevention.**

[![Live Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20Demo-blue)](https://huggingface.co/spaces/yuvis/Enterprise-RAG-System)

## 🌟 Key Differentiators

Unlike basic RAG tutorials, this system handles real-world edge cases:

1.  **Hybrid Search (BM25 + Semantic)**: accurately retrieves both specific keywords (IDs, names) and conceptual matches.
2.  **Safety First**: Implements **Confidence Gating**—the system explicitly refuses to answer if retrieved context is insufficient, preventing hallucinations.
3.  **Zero-Latency Deployment**: Uses a custom **Build-Time Artifact Injection** pipeline to bake index files into the Docker container, eliminating startup delays.

## 🛠️ Architecture

```mermaid
graph LR
    User[User Query] --> A[Hybrid Retriever]
    A -->|Keywords| B(BM25 Index)
    A -->|Semantics| C(Pinecone/FAISS)
    B & C --> D[Rank Fusion (RRF)]
    D --> E[Cross-Encoder Reranker]
    E --> F{Confidence Check}
    F -->|Low Score| G[Fallback Response]
    F -->|High Score| H[LLM Generation]
```

## 🚀 Quick Start

### Local Development
```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Generate Index
python src/ingestion/ingest.py

# 3. Run App
streamlit run app.py
```

### Deployment Strategy
We treat Data and Code separately for scalability:
- **Code**: GitHub (`app.py`, `src/`)
- **Artifacts**: Hugging Face Datasets (`data/index/`)

The `Dockerfile` automatically fetches the latest index during build, ensuring the deployed container is always ready-to-serve.

## 🧪 Tech Stack
- **LlamaIndex / Custom Pipeline**: Hybrid Retrieval Logic
- **Pinecone**: Serverless Vector Database
- **Sentence-Transformers**: Embeddings & Reranking
- **Streamlit**: Conversational UI
- **Docker**: Containerized Deployment
