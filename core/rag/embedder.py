
from __future__ import annotations
from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self, model_id: str):
        self.model = SentenceTransformer(model_id, trust_remote_code=True)
    def encode(self, texts):
        v = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.array(v).astype('float32')
