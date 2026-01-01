import faiss
import numpy as np
import os

class FaissIndex:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        # Store metadata/mapping if needed, for now just simpler index

    def add(self, embeddings: np.ndarray):
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension mismatch. Expected {self.dimension}, got {embeddings.shape[1]}")
        self.index.add(embeddings)

    def search(self, query_embedding: np.ndarray, top_k: int = 10):
        distances, indices = self.index.search(query_embedding, top_k)
        return distances, indices

    def save(self, path: str):
        faiss.write_index(self.index, path)

    def load(self, path: str):
        self.index = faiss.read_index(path)
