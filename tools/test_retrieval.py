import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.embedder import Embedder
from src.retriever.hybrid_retriever import HybridRetriever

def test_retrieval():
    print("Initializing test retrieval...")
    embedder = Embedder()
    retriever = HybridRetriever(
        bm25_path="data/index/bm25.pkl",
        faiss_path="data/index/faiss.index",
        doc_map_path="data/index/doc_map.pkl",
        embedder=embedder
    )
    
    queries = [
        "What is GovReport about?",
        "Financial results for the last quarter",
        "WikiQA question answers"
    ]
    
    for query in queries:
        print(f"\n--- Query: {query} ---")
        results = retriever.search(query, top_k=3)
        for i, doc_text in enumerate(results):
            content = doc_text[:200].replace('\n', ' ')
            print(f"{i+1}. {content}...")

if __name__ == "__main__":
    test_retrieval()
