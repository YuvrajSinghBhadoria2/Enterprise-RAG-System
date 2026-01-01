import sys
import os
 
# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pipeline.query_pipeline import QueryPipeline
from dotenv import load_dotenv

# Ensure env is loaded
load_dotenv()

def verify():
    print("Initializing Pipeline (should use Pinecone)...")
    pipeline = QueryPipeline()
    
    query = "what is Emerging Contaminants according to DOD?"
    print(f"\nQuerying: {query}")
    
    result = pipeline.run(query)
    
    print("\n--- Result ---")
    print(f"Answer: {result['answer']}")
    print(f"Retrieval Score: {result['retrieval_score']}")
    print(f"Contexts Retrieved: {len(result['context'])}")
    if len(result['context']) > 0:
        print(f"Top Context: {result['context'][0][0][:200]}...")

if __name__ == "__main__":
    verify()
