from src.llm.llm_client import LLMClient

class RelevancyGrader:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def grade(self, query: str, answer: str) -> dict:
        """
        Returns score (0-1) on whether the answer addresses the query.
        """
        system_prompt = "You are a grader assessing if a generated answer is relevant to the user query."
        user_prompt = f"""
        User Query: {query}
        Generated Answer: {answer}
        
        Does the answer directly address the query?
        Give a score between 0 and 1, and a boolean label (true/false).
        Return JSON format: {{"score": 0.9, "relevant": true}}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.llm.chat(messages, response_format={"type": "json_object"})
            import json
            data = json.loads(response)
            # print(f"DEBUG_RELEVANCY_RAW: {response}")
            return data
        except Exception as e:
            print(f"DEBUG_RELEVANCY_ERROR: {e}")
            print(f"DEBUG_RELEVANCY_RESPONSE_WAS: {locals().get('response', 'Not generated')}")
            return {"score": 0.5, "relevant": False, "error": str(e)}
