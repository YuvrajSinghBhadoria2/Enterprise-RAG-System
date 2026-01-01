import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def maximal_marginal_relevance(query_embedding: np.ndarray, doc_embeddings: np.ndarray, lambda_mult: float = 0.5, top_k: int = 5):
    """
    Selects docs that are relevant to query but diverse from each other.
    """
    if len(doc_embeddings) == 0:
        return []
    
    # Simple MMR implementation
    selected_indices = []
    candidate_indices = list(range(len(doc_embeddings)))
    
    for _ in range(top_k):
        best_score = -np.inf
        best_idx = -1
        
        for idx in candidate_indices:
            # Relevance
            rel_score = cosine_similarity(query_embedding.reshape(1, -1), doc_embeddings[idx].reshape(1, -1))[0][0]
            
            # Diversity (sim to already selected)
            if not selected_indices:
                div_score = 0
            else:
                sims = cosine_similarity(doc_embeddings[idx].reshape(1, -1), doc_embeddings[selected_indices])[0]
                div_score = np.max(sims)
                
            mmr_score = lambda_mult * rel_score - (1 - lambda_mult) * div_score
            
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx
                
        if best_idx != -1:
            selected_indices.append(best_idx)
            candidate_indices.remove(best_idx)
            
    return selected_indices

def deduplicate_docs(docs: list[dict], threshold: float = 0.95) -> list[dict]:
    """
    Remove near-duplicates based on content string similarity (simple) 
    or just exact match for now to be fast.
    """
    seen = set()
    unique_docs = []
    for doc in docs:
        # Assuming doc is a string or dict with 'content'
        content = doc if isinstance(doc, str) else doc.get('content', '')
        if content not in seen:
            seen.add(content)
            unique_docs.append(doc)
    return unique_docs
