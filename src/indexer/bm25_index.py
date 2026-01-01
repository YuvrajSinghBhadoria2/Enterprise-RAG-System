import pickle
from rank_bm25 import BM25Okapi
from typing import List
import os

class BM25Index:
    def __init__(self):
        self.bm25 = None
        self.corpus = []

    def _tokenize(self, text: str) -> List[str]:
        import re
        return re.findall(r'\w+', text.lower())

    def build(self, corpus: List[str]):
        """
        Builds the BM25 index from a list of documents/chunks.
        """
        self.corpus = corpus
        tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, top_k: int = 10):
        if not self.bm25:
            raise ValueError("Index not built.")
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_n = self.bm25.get_top_n(tokenized_query, self.corpus, n=top_k)
        return top_n, scores

    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump((self.bm25, self.corpus), f)

    def load(self, path: str):
        import gzip
        # Check for gzip file if original path absent or has .gz extension
        if path.endswith(".gz") or (not os.path.exists(path) and os.path.exists(path + ".gz")):
            real_path = path if path.endswith(".gz") else path + ".gz"
            print(f"Loading compressed index from {real_path}")
            with gzip.open(real_path, 'rb') as f:
                self.bm25, self.corpus = pickle.load(f)
            return

        with open(path, 'rb') as f:
            self.bm25, self.corpus = pickle.load(f)
