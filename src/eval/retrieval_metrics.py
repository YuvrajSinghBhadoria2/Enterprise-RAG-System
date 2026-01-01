from typing import List

def mrr_score(relevant_doc_ids: List[str], retrieved_doc_ids: List[str]) -> float:
    """Calculates Mean Reciprocal Rank"""
    for i, doc_id in enumerate(retrieved_doc_ids):
        if doc_id in relevant_doc_ids:
            return 1.0 / (i + 1)
    return 0.0

def recall_at_k(relevant_doc_ids: List[str], retrieved_doc_ids: List[str], k: int) -> float:
    """Calculates Recall@K"""
    retrieved_at_k = set(retrieved_doc_ids[:k])
    relevant_set = set(relevant_doc_ids)
    
    if not relevant_set:
        return 0.0
        
    hits = len(relevant_set.intersection(retrieved_at_k))
    return hits / len(relevant_set)

def precision_at_k(relevant_doc_ids: List[str], retrieved_doc_ids: List[str], k: int) -> float:
    """Calculates Precision@K"""
    retrieved_at_k = set(retrieved_doc_ids[:k])
    relevant_set = set(relevant_doc_ids)
    
    if not retrieved_at_k:
        return 0.0
        
    hits = len(relevant_set.intersection(retrieved_at_k))
    return hits / len(retrieved_at_k)
