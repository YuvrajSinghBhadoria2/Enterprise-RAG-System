from sentence_transformers import SentenceTransformer
import torch

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.model = SentenceTransformer(model_name, device=self.device)

    def embed(self, texts: list[str]):
        return self.model.encode(texts, convert_to_numpy=True)
