from typing import List, Tuple
import numpy as np
from src.indexer.bm25_index import BM25Index
from src.indexer.faiss_index import FaissIndex
from src.embeddings.embedder import Embedder

class HybridRetriever:
    def __init__(self, bm25_path: str, faiss_path: str, doc_map_path: str, embedder: Embedder):
        self.bm25 = BM25Index()
        self.bm25.load(bm25_path)
        
        self.embedder = embedder
        self.embedder = embedder
        self.faiss = None
        import os
        if not os.getenv("DISABLE_FAISS"):
            try:
                self.faiss = FaissIndex(dimension=384) # adjust dimension if needed
                self.faiss.load(faiss_path)
                print("Successfully loaded FAISS index.")
            except Exception as e:
                print(f"WARNING: Could not load FAISS index ({e}). Running in BM25-only mode.")
        else:
            print("FAISS disabled via environment variable. Running in BM25-only mode.")

        # Load doc map
        import pickle
        with open(doc_map_path, 'rb') as f:
            self.doc_map = pickle.load(f)

    def search(self, query: str, top_k: int = 10, alpha: float = 0.5) -> List[dict]:
        """
        Hybrid search using BM25 and Dense embeddings.
        alpha: weight for dense score (0 = pure BM25, 1 = pure Dense)
        """
        # 1. BM25 Search
        # We need to normalize scores to combine them properly, usually RRF is safer if scores are not calibrated
        # For simplicity here, we get top N and use RRF
        
        top_n = top_k * 2
        
        # BM25
        bm25_docs, bm25_scores = self.bm25.search(query, top_k=top_n)
        
        scores = {}
        
        # Process BM25
        for rank, doc in enumerate(bm25_docs):
            key = doc
            scores[key] = scores.get(key, 0) + (1 / (60 + rank))

        # Dense (Only if FAISS is loaded)
        if self.faiss:
            try:
                query_emb = self.embedder.embed([query])
                dense_dists, dense_indices = self.faiss.search(query_emb, top_k=top_n)
                
                # Merge using Reciprocal Rank Fusion (RRF)
                # Dense indices refer to doc_map
                for rank, idx in enumerate(dense_indices[0]):
                    if idx == -1: continue
                    doc_data = self.doc_map[idx]
                    key = doc_data['content']
                    scores[key] = scores.get(key, 0) + (1 / (60 + rank))
            except Exception as e:
                print(f"Error during dense search: {e}")
            
        # Sort by RRF score
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in sorted_docs[:top_k]]
