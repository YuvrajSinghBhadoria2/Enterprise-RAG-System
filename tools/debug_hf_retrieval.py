from src.retriever.hybrid_retriever import HybridRetriever
from src.embeddings.embedder import Embedder
from src.reranker.cross_encoder import Reranker
import os

def debug_retrieval():
    query = "what is Emerging Contaminants according to DOD?"
    
    print(f"--- Debugging Query: {query} ---")
    
    embedder = Embedder()
    retriever = HybridRetriever(
        bm25_path="data/index/bm25.pkl",
        faiss_path="data/index/faiss.index",
        doc_map_path="data/index/doc_map.pkl",
        embedder=embedder
    )
    
    reranker = Reranker()
    
    # 1. Hybrid Search
    print("\n1. Running Hybrid Search (top_k=20)...")
    results = retriever.search(query, top_k=20)
    
    print(f"Retrieved {len(results)} docs.")
    
    # 2. Reranking
    print("\n2. Reranking...")
    reranked = reranker.rerank(query, results, top_k=5)
    
    for i, (doc, score) in enumerate(reranked, 1):
        print(f"\n[{i}] Score: {score:.2f}")
        print(f"Content: {doc[:300]}...")

if __name__ == "__main__":
    debug_retrieval()
