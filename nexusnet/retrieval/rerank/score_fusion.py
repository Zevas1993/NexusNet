from __future__ import annotations

from collections import defaultdict
from typing import Any

from nexus.schemas import RetrievalHit


def _copy_hit(hit: RetrievalHit, *, score: float, metadata: dict[str, Any]) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=hit.chunk_id,
        doc_id=hit.doc_id,
        source=hit.source,
        content=hit.content,
        score=score,
        metadata=metadata,
    )


def groundedness_score(hit: RetrievalHit) -> float:
    metadata = hit.metadata or {}
    sources = set(metadata.get("candidate_sources", []))
    if metadata.get("backend") == "graphrag":
        sources.add("graph")
    if metadata.get("backend") == "memory":
        sources.add("memory")
    if metadata.get("backend") == "temporal":
        sources.add("temporal")
    base = 0.45 + min(len(sources), 3) * 0.12
    if metadata.get("provenance") or metadata.get("graph_source"):
        base += 0.12
    if metadata.get("retrieval_stage") == "stage2-reranked":
        base += 0.08
    return round(min(base, 1.0), 3)


def provenance_score(hit: RetrievalHit) -> float:
    metadata = hit.metadata or {}
    score = 0.0
    if metadata.get("provenance"):
        score += 0.45
    if metadata.get("graph_source"):
        score += 0.2
    if metadata.get("candidate_sources"):
        score += min(len(metadata.get("candidate_sources", [])), 3) * 0.1
    if metadata.get("retrieval_stage") == "stage2-reranked":
        score += 0.05
    return round(min(score, 1.0), 3)


def average_relevance(hits: list[RetrievalHit]) -> float:
    if not hits:
        return 0.0
    return round(sum(float(hit.score) for hit in hits) / len(hits), 4)


def average_groundedness(hits: list[RetrievalHit]) -> float:
    if not hits:
        return 0.0
    return round(sum(groundedness_score(hit) for hit in hits) / len(hits), 4)


def average_provenance(hits: list[RetrievalHit]) -> float:
    if not hits:
        return 0.0
    return round(sum(provenance_score(hit) for hit in hits) / len(hits), 4)


def compute_quality_delta(before_hits: list[RetrievalHit], after_hits: list[RetrievalHit]) -> dict[str, float]:
    return {
        "relevance_delta": round(average_relevance(after_hits) - average_relevance(before_hits), 4),
        "groundedness_delta": round(average_groundedness(after_hits) - average_groundedness(before_hits), 4),
        "provenance_delta": round(average_provenance(after_hits) - average_provenance(before_hits), 4),
    }


def weighted_reciprocal_rank_fusion(
    *,
    runs: dict[str, list[RetrievalHit]],
    weights: dict[str, float],
    rrf_k: int = 60,
    limit: int = 12,
) -> list[RetrievalHit]:
    if not runs:
        return []

    merged: dict[str, dict[str, Any]] = {}
    for source_name, hits in runs.items():
        weight = float(weights.get(source_name, 1.0))
        for rank, hit in enumerate(hits, start=1):
            bucket = merged.setdefault(
                hit.chunk_id,
                {
                    "hit": hit,
                    "score": 0.0,
                    "sources": set(),
                    "source_scores": {},
                    "backend": hit.metadata.get("backend"),
                    "provenance": hit.metadata.get("provenance"),
                },
            )
            bucket["score"] += weight * (1.0 / (rrf_k + rank))
            bucket["sources"].add(source_name)
            bucket["source_scores"][source_name] = float(hit.score)
            if hit.metadata.get("provenance") and not bucket.get("provenance"):
                bucket["provenance"] = hit.metadata.get("provenance")
            if hit.metadata.get("backend") and not bucket.get("backend"):
                bucket["backend"] = hit.metadata.get("backend")

    fused: list[RetrievalHit] = []
    for bucket in merged.values():
        hit = bucket["hit"]
        metadata = dict(hit.metadata)
        metadata.update(
            {
                "candidate_sources": sorted(bucket["sources"]),
                "candidate_source_scores": bucket["source_scores"],
                "fusion_score": round(bucket["score"], 6),
                "retrieval_stage": "stage1-fused",
            }
        )
        if bucket.get("backend") and "backend" not in metadata:
            metadata["backend"] = bucket["backend"]
        if bucket.get("provenance") and "provenance" not in metadata:
            metadata["provenance"] = bucket["provenance"]
        fused.append(_copy_hit(hit, score=round(bucket["score"], 6), metadata=metadata))

    fused.sort(key=lambda hit: hit.score, reverse=True)
    return fused[:limit]
