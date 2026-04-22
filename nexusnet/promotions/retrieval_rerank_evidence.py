from __future__ import annotations

from typing import Any

from nexus.schemas import new_id, utcnow


def _representative_rerank_score(after_candidates: list[dict[str, Any]]) -> float:
    if not after_candidates:
        return 0.0
    first = after_candidates[0]
    score = first.get("rerank_score")
    if score is None:
        return 0.0
    return round(float(score), 6)


def build_retrieval_rerank_evidence_bundle(
    *,
    subject_id: str,
    policy_mode: str,
    challenger_reference: str,
    traceability: dict[str, Any],
    scorecard: dict[str, Any],
    scorecard_artifacts: dict[str, str] | None = None,
    evaluator_artifact_refs: dict[str, str] | None = None,
) -> dict[str, Any]:
    reranker = traceability.get("reranker") or {}
    before_candidates = list(traceability.get("candidate_list_before_rerank", []))
    after_candidates = list(traceability.get("candidate_list_after_rerank", []))
    return {
        "bundle_id": new_id("retrievalev"),
        "schema_family": "retrieval-rerank-evidence-bundle",
        "schema_version": 1,
        "status_label": "STRONG ACCEPTED DIRECTION",
        "created_at": utcnow().isoformat(),
        "subject_id": subject_id,
        "policy_mode": policy_mode,
        "challenger_reference": challenger_reference,
        "trace_id": traceability.get("trace_id"),
        "session_id": traceability.get("session_id"),
        "stage_1_top_k": int(traceability.get("top_k_before_rerank", len(before_candidates)) or 0),
        "stage_2_top_k_after_rerank": int(traceability.get("top_k_after_rerank", len(after_candidates)) or 0),
        "rerank_score": _representative_rerank_score(after_candidates),
        "reranker_provider": reranker.get("provider"),
        "latency_delta_ms": float(reranker.get("latency_delta_ms", 0.0) or 0.0),
        "relevance_delta": float(reranker.get("relevance_delta", 0.0) or 0.0),
        "groundedness_delta": float(reranker.get("groundedness_delta", 0.0) or 0.0),
        "provenance_delta": float(reranker.get("provenance_delta", 0.0) or 0.0),
        "candidate_source_counts": dict(traceability.get("candidate_source_counts", {})),
        "stage_1_candidates": before_candidates,
        "stage_2_candidates": after_candidates,
        "benchmark_family_id": scorecard.get("benchmark_family_id"),
        "threshold_set_id": scorecard.get("threshold_set_id"),
        "scorecard_id": scorecard.get("scorecard_id"),
        "scorecard_passed": bool(scorecard.get("passed", False)),
        "scorecard_summary": dict(scorecard.get("summary", {})),
        "threshold_report": dict(scorecard.get("threshold_report", {})),
        "scorecard_artifacts": dict(scorecard_artifacts or {}),
        "evaluator_artifact_refs": dict(evaluator_artifact_refs or {}),
    }
