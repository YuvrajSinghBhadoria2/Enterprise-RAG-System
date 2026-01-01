import os
import json
from datasets import load_dataset
from tqdm import tqdm
import numpy as np
from src.pipeline.query_pipeline import QueryPipeline
from src.eval.retrieval_metrics import recall_at_k, mrr_score, precision_at_k
from src.eval.hallucination import HallucinationGrader
from src.eval.relevancy import RelevancyGrader

def main():
    print("Initializing Pipeline...")
    pipeline = QueryPipeline()
    grader = HallucinationGrader(pipeline.llm)
    relevancy_grader = RelevancyGrader(pipeline.llm)

    print("Loading Evaluation Data (WikiQA Test Split)...")
    # For meaningful evaluation, we need questions that actually have answers in our indexed subset.
    # Since we indexed the 'train' split of WikiQA (first 100), we should evaluate on that same subset 
    # to test "retrieval ability" (can it find what we vaguely know is there).
    # In a real scenario, you'd test on a hold-out set, but only if you indexed the whole knowledge base.
    try:
        ds = load_dataset("microsoft/wiki_qa", split="train[:20]", trust_remote_code=True)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # Metrics
    recalls = []
    precisions = []
    mrrs = []
    hallucination_scores = []
    relevancy_scores = []
    
    print("Running Evaluation...")
    for i, row in tqdm(enumerate(ds), total=len(ds)):
        query = row['question']
        relevant_doc_content = row['answer'] # The correct sentence
        is_correct = row['label'] == 1




        if not is_correct:
            # If this row isn't a correct answer pair, skip for retrieval accuracy measurement 
            # (or treat as a negative, but for RAG recall we usually care about positive queries)
            continue
            
        result = pipeline.run(query, top_k_retrieval=10, top_k_rerank=3)
        
        # Retrieval Metrics
        retrieved_contents = [doc if isinstance(doc, str) else doc['content'] for doc, score in result['context']]
        


        
        # Check if relevant content is in retrieved
        # The ingestion pipeline might add metadata like "Source: ...". 
        # So we check if the relevant content SUBSTRING is in the retrieved chunks.
        is_hit = False
        for content in retrieved_contents:
            if relevant_doc_content in content:
                is_hit = True
                break
        
        recalls.append(1.0 if is_hit else 0.0)
        # Precision (strict: is the retrieved doc the specific sentence?)
        # Since we only retrieve 10 and usually there is only 1 relevant sentence in WikiQA:
        # Precision will be at best 0.1 if is_hit is true.
        precisions.append(1.0/10.0 if is_hit else 0.0)
        
        # MRR
        # Find rank
        rank = -1
        for idx, content in enumerate(retrieved_contents):
            if relevant_doc_content in content:
                rank = idx + 1
                break
        
        if rank > 0:
            mrrs.append(1.0 / rank)
        else:
            mrrs.append(0.0)
            
        # Generation / Hallucination Metric
        # We ask the LLM to grade if the answer supported by context
        grade = grader.grade(
            context="\n".join(retrieved_contents),
            answer=result['answer']
        )
        hallucination_scores.append(grade.get('score', 0.0))
        
        # New: Answer Relevancy
        rel_grade = relevancy_grader.grade(query=query, answer=result['answer'])
        relevancy_scores.append(rel_grade.get('score', 0.0))
        
    print("\nXXX Evaluation Results XXX")
    print(f"Average Recall@10: {np.mean(recalls):.4f}")
    print(f"Average Precision@10: {np.mean(precisions):.4f}")
    print(f"Average MRR: {np.mean(mrrs):.4f}")
    print(f"Average Factuality Score: {np.mean(hallucination_scores):.4f}")
    print(f"Average Answer Relevancy: {np.mean(relevancy_scores):.4f}")

if __name__ == "__main__":
    main()
