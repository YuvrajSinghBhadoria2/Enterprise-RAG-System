import os
import glob
from pathlib import Path
from typing import List
import numpy as np
from tqdm import tqdm

from src.ingestion.readers import get_reader
from src.ingestion.cleaner import clean_text
from src.ingestion.chunkers import SlidingWindowChunker
from src.embeddings.embedder import Embedder
from src.indexer.bm25_index import BM25Index
from src.indexer.faiss_index import FaissIndex

DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
INDEX_DIR = os.path.join(DATA_DIR, "index")

class IngestionPipeline:
    def __init__(self):
        self.chunker = SlidingWindowChunker()
        self.embedder = Embedder(model_name="all-MiniLM-L6-v2")
        self.bm25_index = BM25Index()
        # Dimension for all-MiniLM-L6-v2 is 384
        self.faiss_index = FaissIndex(dimension=384)
        
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
                    doc_map.append({"source": str(path), "content": chunk})
            except Exception as e:
                print(f"Error processing {path}: {e}")
                
        print(f"Total chunks generated: {len(all_chunks)}")
        
        # 2. Build BM25 Index
        print("Building BM25 Index...")
        self.bm25_index.build(all_chunks)
        os.makedirs(INDEX_DIR, exist_ok=True)
        self.bm25_index.save(os.path.join(INDEX_DIR, "bm25.pkl"))
        
        # 3. Embed and Build FAISS Index
        if not os.getenv("DISABLE_FAISS"):
            print("Embedding chunks and building FAISS Index...")
            batch_size = 32
            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i : i + batch_size]
                embeddings = self.embedder.embed(batch)
                self.faiss_index.add(embeddings)
                
            self.faiss_index.save(os.path.join(INDEX_DIR, "faiss.index"))
        else:
            print("Skipping FAISS build due to DISABLE_FAISS environment variable.")
            # Create a dummy file to satisfy file existence checks if any (though lazy loaded)
            with open(os.path.join(INDEX_DIR, "faiss.index"), "w") as f:
                f.write("dummy")
        
        # Save doc_map (simple persistence for retrieval lookup)
        import pickle
        with open(os.path.join(INDEX_DIR, "doc_map.pkl"), "wb") as f:
            pickle.dump(doc_map, f)
            
        print("Ingestion complete.")

if __name__ == "__main__":
    pipeline = IngestionPipeline()
    pipeline.run()
