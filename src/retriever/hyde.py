from src.llm.llm_client import LLMClient

class HyDERetriever:
    def __init__(self, llm_client: LLMClient, base_retriever):
        self.llm = llm_client
        self.retriever = base_retriever

    def generate_hypothetical_doc(self, query: str) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Write a hypothetical answer to the user's question. Do not include any explanation, just the answer."},
            {"role": "user", "content": query}
        ]
        return self.llm.chat(messages, temperature=0.7)

    def search(self, query: str, top_k: int = 10):
        # 1. Generate hypothetical doc
        hypothetical_doc = self.generate_hypothetical_doc(query)
        print(f"DEBUG: HyDE Doc: {hypothetical_doc[:100]}...")
        
        # 2. Retrieve using the hypothetical doc as query
        return self.retriever.search(hypothetical_doc, top_k=top_k)
