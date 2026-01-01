import os
import time
from typing import Optional
from src.retriever.hybrid_retriever import HybridRetriever
from src.retriever.hyde import HyDERetriever
from src.reranker.cross_encoder import Reranker
from src.llm.llm_client import OpenAIClient, VLLMClient, GroqClient
from src.embeddings.embedder import Embedder
from src.pipeline.context_opt import deduplicate_docs

class QueryPipeline:
    def __init__(self, use_hyde: bool = False):
        self.embedder = Embedder()
        self.retriever = HybridRetriever(
            bm25_path="data/index/bm25.pkl",
            faiss_path="data/index/faiss.index",
            doc_map_path="data/index/doc_map.pkl",
            embedder=self.embedder
        )
        
        # LLM Client Strategy
        if os.getenv("GROQ_API_KEY"):
             self.llm = GroqClient()
        elif os.getenv("VLLM_API_URL"):
            self.llm = VLLMClient()
        else:
            self.llm = OpenAIClient()
            
        if use_hyde:
            self.retriever = HyDERetriever(self.llm, self.retriever)
            
        self.reranker = Reranker()

    def run(self, query: str, top_k_retrieval: int = 20, top_k_rerank: int = 5):
        # 1. Retrieve
        print(f"Retrieving for query: {query}")
        t0 = time.time()
        retrieved_docs = self.retriever.search(query, top_k=top_k_retrieval)
        t1 = time.time()
        print(f"⏱️ Retrieval took: {t1 - t0:.2f}s")
        
        # 2. Deduplicate
        unique_docs = deduplicate_docs(retrieved_docs)
        
        # 3. Rerank
        # Reranker expects strings
        # Reranker expects strings
        doc_contents = [d if isinstance(d, str) else d['content'] for d in unique_docs]
        
        # OPTIMIZATION: Limit reranking to top 10 to reduce CPU latency
        doc_contents = doc_contents[:10]
        
        t2 = time.time()
        reranked = self.reranker.rerank(query, doc_contents, top_k=top_k_rerank)
        t3 = time.time()
        print(f"⏱️ Reranking took: {t3 - t2:.2f}s")
        
        # 4. Generate
        
        # Retrieval Score Gate
        RETRIEVAL_SCORE_THRESHOLD = -4.0
        
        # reranked is list of (doc, score)
        if not reranked or reranked[0][1] < RETRIEVAL_SCORE_THRESHOLD:
            return {
                "query": query,
                "answer": "I do not have enough information in the provided documents to answer this question.",
                "context": [],
                "retrieval_score": reranked[0][1] if reranked else -99.9,
                "hallucination_score": 0.0,
                "groundedness": 1.0
            }
            
        context_text = "\n\n".join([doc for doc, score in reranked])
        
        SYSTEM_PROMPT = """
You are an enterprise-grade question answering system.

Rules:
1. Answer strictly using ONLY the provided context.
2. DO NOT use prior knowledge or assumptions.
3. If the answer is not explicitly stated in the context, respond EXACTLY with:
   "I do not have enough information in the provided documents to answer this question."
4. Do not add explanations, guesses, or external facts.
"""
        
        user_prompt = f"""
{SYSTEM_PROMPT}

Context:
{context_text}

Question:
{query}
"""
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        t4 = time.time()
        answer = self.llm.chat(messages)
        t5 = time.time()
        print(f"⏱️ LLM Generation took: {t5 - t4:.2f}s")
        
        return {
            "query": query,
            "answer": answer,
            "context": reranked,
            "retrieval_score": reranked[0][1]
        }
