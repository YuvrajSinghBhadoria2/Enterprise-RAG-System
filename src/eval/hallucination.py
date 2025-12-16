from src.llm.llm_client import LLMClient

class HallucinationGrader:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def grade(self, context: str, answer: str) -> dict:
        """
        Returns hallucination score based on token overlap.
        """
        # 1. Check for refusal
        if "not enough information" in answer.lower():
            return {"score": 0.0, "grounded": True}

        # 2. Key Term Overlap
        # Normalize and tokenize
        def tokenize(text):
            import re
            text = text.lower()
            tokens = re.findall(r'\w+', text)
            # Remove stopwords
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were'}
            return set([t for t in tokens if t not in stop_words])

        answer_tokens = tokenize(answer)
        context_tokens = tokenize(context)

        if not answer_tokens:
             return {"score": 0.1, "grounded": True} # Default for empty answer

        # Calculate overlap
        intersection = answer_tokens.intersection(context_tokens)
        overlap_ratio = len(intersection) / len(answer_tokens)
        
        # User Rule: if overlap < 0.25 -> 1.0 (Hallucination)
        # Else -> 0.1 (Grounded) -- User requested 0.1 specifically
        
        if overlap_ratio < 0.25:
             return {"score": 1.0, "grounded": False}
        else:
             return {"score": 0.1, "grounded": True}
