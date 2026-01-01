import os
import time
from typing import List, Optional
import numpy as np
from pinecone import Pinecone, ServerlessSpec

class PineconeIndex:
    def __init__(self, dimension: int, index_name: str = "enterprise-rag"):
        self.dimension = dimension
        self.index_name = index_name
        self.api_key = os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
        
        # Check if index exists, create if not
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index_exists(self):
        """Create a serverless index if it doesn't exist"""
        existing_indexes = [i.name for i in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating Pinecone index '{self.index_name}'...")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            # Wait for index to be ready
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            print("Pinecone index created successfully.")

    def add(self, embeddings: np.ndarray, metadata: List[dict] = None):
        """
        Add embeddings to Pinecone.
        metadata is expected to be a list of dicts corresponding to each embedding.
        If None, we'll generate dummy IDs.
        """
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension mismatch. Expected {self.dimension}, got {embeddings.shape[1]}")
            
        # Pinecone expects (id, vector, metadata)
        vectors = []
        for i, embedding in enumerate(embeddings):
            # If metadata provided, use a hash or index as ID. For now simple index fallback.
            # In a real pipeline, better to pass explicit unique doc_ids.
            vector_id = str(hash(embedding.tobytes())) if metadata is None else metadata[i].get("id", f"vec_{i}")
             # Ensure metadata is flat dict if possible, or limited
            meta = metadata[i] if metadata else {}
            
            vectors.append({
                "id": vector_id,
                "values": embedding.tolist(),
                "metadata": meta
            })
            
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            self.index.upsert(vectors=batch)

    def search(self, query_embedding: np.ndarray, top_k: int = 10):
        """
        Search for nearest neighbors.
        Returns:
            distances: list of list of float (scores)
            indices: list of list of doc_ids (or whatever ID was stored)
            matches: Full match objects if needed later
        """
        # Pinecone query expects a list of vectors
        # If passed a batch (N, dim), loop
        
        # Ensure query is (1, dim) or (dim,)
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        results = []
        
        for q_vec in query_embedding:
            response = self.index.query(
                vector=q_vec.tolist(),
                top_k=top_k,
                include_metadata=True
            )
            results.append(response)
            
        # Format to match FAISS return style: (distances, indices)
        # Distances in Pinecone (cosine) are scores.
        all_scores = []
        all_ids = []
        
        for res in results:
            scores = [match['score'] for match in res['matches']]
            ids = [match['id'] for match in res['matches']]
            all_scores.append(scores)
            all_ids.append(ids)
            
        return np.array(all_scores), all_ids

    def save(self, path: str):
        """Pinecone is serverless, no local save needed."""
        pass

    def load(self, path: str):
        """Pinecone is serverless, it holds its own state."""
        pass
