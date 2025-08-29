
from __future__ import annotations
from typing import List, Tuple

def _lexical_score(q: str, a: str) -> float:
    qs = set(q.lower().split())
    as_ = set(a.lower().split())
    inter = len(qs & as_)
    return inter / max(1, len(qs))

def pairwise_rerank(query: str, candidates: List[str], ais_scores: List[float] | None = None) -> List[str]:
    scored: List[Tuple[str, float]] = []
    for i, c in enumerate(candidates):
        s = _lexical_score(query, c)
        if ais_scores and i < len(ais_scores):
            s = 0.7*s + 0.3*ais_scores[i]
        scored.append((c, s))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in scored]
