from __future__ import annotations

import math
import re
import time
from typing import Any

from nexus.schemas import RetrievalHit

from .base import StageTwoRerankResult
from .score_fusion import compute_quality_delta


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if token}


def _heuristic_pair_score(query: str, hit: RetrievalHit) -> float:
    query_tokens = _tokens(query)
    if not query_tokens:
        return 0.0
    content_tokens = _tokens(hit.content)
    overlap = len(query_tokens & content_tokens)
    coverage = overlap / max(len(query_tokens), 1)
    metadata = hit.metadata or {}
    source_bonus = 0.05 * len(metadata.get("candidate_sources", []))
    provenance_bonus = 0.08 if metadata.get("provenance") or metadata.get("graph_source") else 0.0
    backend_bonus = 0.04 if metadata.get("backend") == "graphrag" else 0.0
    return round(coverage + source_bonus + provenance_bonus + backend_bonus, 6)


class CrossEncoderStageTwoReranker:
    def __init__(self, *, model_name: str, device: str = "cpu", fallback_provider: str = "heuristic-cross-encoder"):
        self.model_name = model_name
        self.device = device
        self.fallback_provider = fallback_provider
        self._model: Any | None = None

    def rerank(self, *, query: str, candidates: list[RetrievalHit], top_k: int) -> StageTwoRerankResult:
        before_hits = list(candidates[:top_k])
        if not before_hits or top_k <= 0:
            return StageTwoRerankResult(
                provider_name=self.model_name,
                applied=False,
                top_k_before=len(before_hits),
                top_k_after=0,
                latency_ms=0,
                hits=[],
                diagnostics={"reason": "No rerank candidates available."},
            )

        started = time.perf_counter()
        provider_name = self.model_name
        try:
            scores = self._predict(query, before_hits)
        except Exception:
            provider_name = self.fallback_provider
            scores = [_heuristic_pair_score(query, hit) for hit in before_hits]

        reranked = []
        rerank_scores: dict[str, float] = {}
        for hit, score in zip(before_hits, scores):
            score_value = float(score)
            rerank_scores[hit.chunk_id] = score_value
            metadata = dict(hit.metadata)
            metadata.update(
                {
                    "rerank_score": round(score_value, 6),
                    "reranker_provider": provider_name,
                    "retrieval_stage": "stage2-reranked",
                }
            )
            reranked.append(
                RetrievalHit(
                    chunk_id=hit.chunk_id,
                    doc_id=hit.doc_id,
                    source=hit.source,
                    content=hit.content,
                    score=round(score_value, 6),
                    metadata=metadata,
                )
            )

        reranked.sort(key=lambda hit: hit.score, reverse=True)
        latency_ms = int((time.perf_counter() - started) * 1000)
        quality_delta = compute_quality_delta(before_hits, reranked[:top_k])
        return StageTwoRerankResult(
            provider_name=provider_name,
            applied=True,
            top_k_before=len(before_hits),
            top_k_after=min(top_k, len(reranked)),
            latency_ms=latency_ms,
            hits=reranked[:top_k],
            rerank_scores=rerank_scores,
            diagnostics={
                **quality_delta,
                "fallback_used": provider_name == self.fallback_provider,
                "score_spread": round(max(rerank_scores.values()) - min(rerank_scores.values()), 6) if rerank_scores else 0.0,
                "score_entropy_hint": round(
                    -sum(
                        (abs(score) / max(sum(abs(value) for value in rerank_scores.values()), 1e-9))
                        * math.log(max(abs(score) / max(sum(abs(value) for value in rerank_scores.values()), 1e-9), 1e-9))
                        for score in rerank_scores.values()
                    ),
                    6,
                )
                if rerank_scores
                else 0.0,
            },
        )

    def _predict(self, query: str, candidates: list[RetrievalHit]) -> list[float]:
        if self._model is None:
            from sentence_transformers import CrossEncoder  # type: ignore

            self._model = CrossEncoder(self.model_name, device=self.device)
        pairs = [[query, hit.content] for hit in candidates]
        scores = self._model.predict(pairs, convert_to_tensor=False)
        return [float(score) for score in scores]
