
import os
from src.pipeline.query_pipeline import QueryPipeline

def test_manual_query():
    print("Initializing Pipeline...")
    pipeline = QueryPipeline()
    
    query = 'what is emerging contaminants according to DOD?'
    print(f"\nProcessing Query: {query}")
    
    # Run pipeline
    result = pipeline.run(query, top_k_retrieval=5, top_k_rerank=3)
    
    print("\n--- Retrieved Context (Top 3) ---")
    for doc, score in result['context']:
        content = doc if isinstance(doc, str) else doc['content']
        print(f"[Score: {score:.4f}] {content[:150]}...")
        
    print("\n--- Generated Answer ---")
    print(result['answer'])
    
    print("\n--- Scores ---")
    print(f"Retrieval Score: {result.get('retrieval_score', 'N/A')}")
    print(f"Hallucination Score: {result.get('hallucination_score', 'N/A')}")
    print(f"Groundedness: {result.get('groundedness', 'N/A')}")

if __name__ == "__main__":
    test_manual_query()
