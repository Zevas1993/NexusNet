
from __future__ import annotations
from typing import List, Tuple
try:
    from sentence_transformers import CrossEncoder
except Exception:
    CrossEncoder = None

class Reranker:
    def __init__(self, model_id: str):
        if CrossEncoder is None: raise RuntimeError("CrossEncoder not available")
        self.ce = CrossEncoder(model_id)
    def rerank(self, query: str, passages: List[str], top_k: int = 8) -> List[Tuple[int,float]]:
        pairs = [[query, p] for p in passages]
        scores = self.ce.predict(pairs).tolist()
        return sorted(list(enumerate(scores)), key=lambda x:x[1], reverse=True)[:top_k]
