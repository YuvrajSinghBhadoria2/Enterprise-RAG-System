import pickle
from rank_bm25 import BM25Okapi
from typing import List
import os

class BM25Index:
    def __init__(self):
        self.bm25 = None
        self.corpus = []

    def build(self, corpus: List[str]):
        """
        Builds the BM25 index from a list of documents/chunks.
        """
        self.corpus = corpus
        tokenized_corpus = [doc.split(" ") for doc in corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, top_k: int = 10):
        if not self.bm25:
            raise ValueError("Index not built.")
        tokenized_query = query.split(" ")
        scores = self.bm25.get_scores(tokenized_query)
        top_n = self.bm25.get_top_n(tokenized_query, self.corpus, n=top_k)
        return top_n, scores

    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump((self.bm25, self.corpus), f)

    def load(self, path: str):
        with open(path, 'rb') as f:
            self.bm25, self.corpus = pickle.load(f)
