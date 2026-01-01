import os
import glob
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from typing import List
import numpy as np
from tqdm import tqdm

from src.ingestion.readers import get_reader
from src.ingestion.cleaner import clean_text
from src.ingestion.chunkers import SlidingWindowChunker
# from src.embeddings.embedder import Embedder
from src.indexer.bm25_index import BM25Index
from src.indexer.faiss_index import FaissIndex
from src.indexer.pinecone_index import PineconeIndex
import uuid

DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
INDEX_DIR = os.path.join(DATA_DIR, "index")

class IngestionPipeline:
    def __init__(self):
        self.chunker = SlidingWindowChunker()
        # self.embedder = Embedder(model_name="all-MiniLM-L6-v2")
        self.bm25_index = BM25Index()
        
        # Check Vector DB Type
        self.vector_db_type = os.getenv("VECTOR_DB_TYPE", "faiss").lower()
        if self.vector_db_type == "pinecone":
            self.vector_index = PineconeIndex(dimension=384)
        else:
            self.vector_index = FaissIndex(dimension=384)
        
    def run(self):
        print("Starting ingestion...")
        files = glob.glob(os.path.join(RAW_DIR, "*.*"))
        
        all_chunks = []
        doc_map = [] # To map chunk index back to metadata/content if needed
        
        # 1. Read, Clean, Chunk
        print("Processing files...")
        for file_path in tqdm(files):
            path = Path(file_path)
            try:
                reader = get_reader(path)
                raw_text = reader.read(path)
                cleaned_text = clean_text(raw_text)
                chunks = self.chunker.chunk(cleaned_text)
                
                for chunk in chunks:
                    all_chunks.append(chunk)
                    # Generate a stable ID for metadata (for Pinecone)
                    chunk_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(path) + chunk[:50]))
                    doc_map.append({"source": str(path), "content": chunk, "id": chunk_id})
            except Exception as e:
                print(f"Error processing {path}: {e}")
                
        print(f"Total chunks generated: {len(all_chunks)}")
        
        # 2. Build BM25 Index
        print("Building BM25 Index...")
        self.bm25_index.build(all_chunks)
        os.makedirs(INDEX_DIR, exist_ok=True)
        self.bm25_index.save(os.path.join(INDEX_DIR, "bm25.pkl"))
        
        # 3. Embed and Build Vector Index
        print(f"Embedding chunks and updating {self.vector_db_type.upper()} Index...")
        if not os.getenv("DISABLE_VECTOR_DB"):
            batch_size = 32
            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i : i + batch_size]
                batch_meta = doc_map[i : i + batch_size]
                
                embeddings = self.embedder.embed(batch)
                
                # Add to index (with metadata for Pinecone)
                if self.vector_db_type == "pinecone":
                    self.vector_index.add(embeddings, metadata=batch_meta)
                else:
                    self.vector_index.add(embeddings)
                
            self.vector_index.save(os.path.join(INDEX_DIR, "faiss.index")) # No-op for Pinecone
        else:
            print("Skipping Vector DB build due to DISABLE_VECTOR_DB environment variable.")
        
        # Save doc_map (simple persistence for retrieval lookup)
        import pickle
        with open(os.path.join(INDEX_DIR, "doc_map.pkl"), "wb") as f:
            pickle.dump(doc_map, f)
            
        print("Ingestion complete.")

if __name__ == "__main__":
    pipeline = IngestionPipeline()
    pipeline.run()
