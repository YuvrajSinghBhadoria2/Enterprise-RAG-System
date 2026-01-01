from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, docs: list[str], top_k: int = 5):
        if not docs:
            return []
        
        pairs = [[query, doc] for doc in docs]
        scores = self.model.predict(pairs).tolist()
        
        # Combine docs with scores
        doc_scores = list(zip(docs, scores))
        # Sort by score descending
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        return doc_scores[:top_k]
