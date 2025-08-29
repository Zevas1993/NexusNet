from typing import List, Tuple, Dict
def rrf_fuse(runs: List[List[Tuple[str, float]]], k=60) -> List[Tuple[str, float]]:
    ranks = {}
    for run in runs:
        for rank, (doc_id, _) in enumerate(run, start=1):
            ranks.setdefault(doc_id, 0.0)
            ranks[doc_id] += 1.0 / (k + rank)
    return sorted(ranks.items(), key=lambda x: x[1], reverse=True)
class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L6-v2", device: str = "cpu"):
        self.model_name, self.device, self.m = model_name, device, None
    def _ensure(self):
        if self.m is None:
            from sentence_transformers import CrossEncoder
            self.m = CrossEncoder(self.model_name, device=self.device)
    def rerank(self, q: str, docs: List[Dict], topk: int = 8) -> List[Dict]:
        self._ensure()
        if not docs: return []
        pairs = [[q, d["text"]] for d in docs]
        scores = self.m.predict(pairs, convert_to_tensor=False)
        for d, s in zip(docs, scores): d["ce_score"] = float(s)
        return sorted(docs, key=lambda d: d["ce_score"], reverse=True)[:topk]
