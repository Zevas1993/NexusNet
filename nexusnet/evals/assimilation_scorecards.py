from __future__ import annotations

from typing import Any


def build_assimilation_scorecards(
    *,
    retrieval_rerank_evidence: dict[str, Any] | None = None,
    retrieval_rerank_review: dict[str, Any] | None = None,
    aitune_validation: dict[str, Any] | None = None,
    triattention_comparison: dict[str, Any] | None = None,
) -> dict[str, Any]:
    retrieval = retrieval_rerank_evidence or {}
    retrieval_review = retrieval_rerank_review or {}
    aitune = aitune_validation or {}
    triattention = triattention_comparison or {}
    return {
        "status_label": "STRONG ACCEPTED DIRECTION",
        "retrieval_rerank": {
            "bundle_id": retrieval.get("bundle_id"),
            "scorecard_id": retrieval.get("scorecard_id"),
            "review_report_id": retrieval.get("review_report_id"),
            "passed": retrieval.get("scorecard_passed"),
            "benchmark_family_id": retrieval.get("benchmark_family_id"),
            "threshold_set_id": retrieval.get("threshold_set_id"),
            "relevance_delta": retrieval.get("relevance_delta", 0.0),
            "groundedness_delta": retrieval.get("groundedness_delta", 0.0),
            "provenance_delta": retrieval.get("provenance_delta", 0.0),
            "human_summary": retrieval_review.get("human_summary"),
            "candidate_shift_count": ((retrieval_review.get("candidate_shift_summary") or {}).get("changed_count", 0)),
            "top_shift_chunk_id": ((retrieval_review.get("top_shift_preview") or {}).get("chunk_id")),
        },
        "aitune": {
            "current_status": aitune.get("current_status"),
            "execution_mode": aitune.get("execution_mode"),
            "supported_lane_status": ((aitune.get("supported_lane") or {}).get("status")),
            "provider_health": ((aitune.get("capability") or {}).get("provider_health")),
            "execution_plan_artifact_path": aitune.get("execution_plan_artifact_path"),
            "execution_plan_markdown_path": aitune.get("execution_plan_markdown_path"),
            "benchmark_artifact_path": aitune.get("benchmark_artifact_path"),
            "runner_artifact_path": aitune.get("runner_artifact_path"),
        },
        "triattention": {
            "report_id": triattention.get("report_id"),
            "scorecard_id": ((triattention.get("scorecard") or {}).get("scorecard_id")),
            "passed": ((triattention.get("scorecard") or {}).get("passed")),
            "baseline_count": len(triattention.get("baseline_providers", []) or []),
            "runtime_anchor_count": len((((triattention.get("summary") or {}).get("runtime_anchor_summary")) or {})),
            "runtime_anchor_available_count": ((((triattention.get("summary") or {}).get("runtime_anchor_quality_summary")) or {}).get("available_count")),
            "runtime_anchor_latency_anchored_count": ((((triattention.get("summary") or {}).get("runtime_anchor_quality_summary")) or {}).get("latency_anchored_count")),
            "avg_memory_ratio": ((triattention.get("summary") or {}).get("avg_kv_memory_ratio")),
        },
    }
