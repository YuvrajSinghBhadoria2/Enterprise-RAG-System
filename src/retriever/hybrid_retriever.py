from typing import List, Tuple
import numpy as np
from src.indexer.bm25_index import BM25Index
from src.indexer.faiss_index import FaissIndex
from src.indexer.pinecone_index import PineconeIndex
from src.embeddings.embedder import Embedder
import concurrent.futures

class HybridRetriever:
    def __init__(self, bm25_path: str, faiss_path: str, doc_map_path: str, embedder: Embedder):
        self.bm25 = BM25Index()
        self.bm25.load(bm25_path)
        
        self.embedder = embedder
        self.embedder = embedder
        self.vector_index = None
        import os
        self.vector_db_type = os.getenv("VECTOR_DB_TYPE", "faiss").lower()
        if not os.getenv("DISABLE_VECTOR_DB"):
            try:
                if self.vector_db_type == "pinecone":
                    self.vector_index = PineconeIndex(dimension=384)
                    print("Successfully connected to Pinecone.")
                else:
                    self.vector_index = FaissIndex(dimension=384)
                    self.vector_index.load(faiss_path)
                    print("Successfully loaded FAISS index.")
            except Exception as e:
                print(f"WARNING: Could not load Vector index ({e}). Running in BM25-only mode.")
        else:
            print("Vector DB disabled via environment variable. Running in BM25-only mode.")

        # Load doc map
        # Load doc map
        import pickle
        import gzip
        import os
        
        if doc_map_path.endswith(".gz") or (not os.path.exists(doc_map_path) and os.path.exists(doc_map_path + ".gz")):
             real_path = doc_map_path if doc_map_path.endswith(".gz") else doc_map_path + ".gz"
             print(f"Loading compressed doc_map from {real_path}")
             with gzip.open(real_path, 'rb') as f:
                 self.doc_map = pickle.load(f)
        else:
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
        scores = {}

        def run_bm25():
            try:
                return self.bm25.search(query, top_k=top_n)
            except Exception as e:
                print(f"BM25 Error: {e}")
                return [], []

        def run_vector():
            if self.vector_index:
                try:
                    query_emb = self.embedder.embed([query])
                    return self.vector_index.search(query_emb, top_k=top_n)
                except Exception as e:
                    print(f"Vector Search Error: {e}")
                    return None, None
            return None, None

        # Execute in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_bm25 = executor.submit(run_bm25)
            future_vector = executor.submit(run_vector)
            
            bm25_docs, bm25_scores = future_bm25.result()
            dense_dists, dense_ids = future_vector.result()

        # Process BM25
        for rank, doc in enumerate(bm25_docs):
            key = doc
            scores[key] = scores.get(key, 0) + (1 / (60 + rank))

        # Process Dense
        if dense_ids:
            try:
                # Merge using Reciprocal Rank Fusion (RRF)
                if self.vector_db_type == "pinecone":
                    # For Pinecone, dense_ids are unique chunk IDs (uuid), we need to map them to content/doc if possible
                    # or just trust the search result if metadata is rich.
                    # Since we keyed scores by content string for RRF, we need content.
                    # PineconeIndex.search returns matches with metadata inside (we need to update interface or return structure)
                    # Actually, our wrapper PineconeIndex.search returns (scores, ids).
                    # But ids in Pinecone are STRINGS. In local FAISS, dense_indices are INTEGERS (indexes into doc_map).
                    
                    # We need a way to look up content from ID.
                    # Doc map has ID now!
                    id_to_content = {d.get("id"): d["content"] for d in self.doc_map if "id" in d} # Optimization: Precompute in init?
                    
                    for rank, doc_id in enumerate(dense_ids[0]):
                         content = id_to_content.get(doc_id)
                         if content:
                             key = content
                             scores[key] = scores.get(key, 0) + (1 / (60 + rank))
                             
                else:
                    # Legacy FAISS (indices are ints)
                    for rank, idx in enumerate(dense_ids[0]):
                        if idx == -1: continue
                        doc_data = self.doc_map[idx]
                        key = doc_data['content']
                        scores[key] = scores.get(key, 0) + (1 / (60 + rank))
                        
            except Exception as e:
                print(f"Error during dense search: {e}")
            
        # Sort by RRF score
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in sorted_docs[:top_k]]
