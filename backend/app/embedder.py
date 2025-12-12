from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self):
        # small, fast, free embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
