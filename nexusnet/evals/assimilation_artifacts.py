from __future__ import annotations

from typing import Any


def build_assimilation_artifact_catalog(
    *,
    retrieval_rerank_evidence: dict[str, Any] | None = None,
    retrieval_rerank_review: dict[str, Any] | None = None,
    gateway_provenance: dict[str, Any] | None = None,
    edge_vision_benchmark: dict[str, Any] | None = None,
    aitune_validation: dict[str, Any] | None = None,
    triattention_comparison: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "status_label": "STRONG ACCEPTED DIRECTION",
        "retrieval_rerank_evidence": retrieval_rerank_evidence or {},
        "retrieval_rerank_review": {
            "report_id": (retrieval_rerank_evidence or {}).get("review_report_id"),
            "review_summary": (retrieval_rerank_evidence or {}).get("review_summary", []),
            "review_artifacts": (retrieval_rerank_evidence or {}).get("review_artifacts", {}),
            "human_summary": (retrieval_rerank_review or {}).get("human_summary"),
            "review_badges": (retrieval_rerank_review or {}).get("review_badges", {}),
            "candidate_shift_summary": (retrieval_rerank_review or {}).get("candidate_shift_summary", {}),
            "threshold_summary": (retrieval_rerank_review or {}).get("threshold_summary", {}),
            "evaluator_artifact_summary": (retrieval_rerank_review or {}).get("evaluator_artifact_summary", {}),
        },
        "gateway_provenance": gateway_provenance or {},
        "edge_vision_benchmark": edge_vision_benchmark or {},
        "aitune_validation": {
            **(aitune_validation or {}),
            "execution_plan_artifact_path": (aitune_validation or {}).get("execution_plan_artifact_path"),
            "execution_plan_markdown_path": (aitune_validation or {}).get("execution_plan_markdown_path"),
            "benchmark_artifact_path": (aitune_validation or {}).get("benchmark_artifact_path"),
            "tuned_artifact_path": (aitune_validation or {}).get("tuned_artifact_path"),
            "runner_artifact_path": (aitune_validation or {}).get("runner_artifact_path"),
        },
        "triattention_comparison": {
            **(triattention_comparison or {}),
            "comparative_summary_artifact": ((triattention_comparison or {}).get("artifacts") or {}).get("comparative_summary"),
            "runtime_anchor_summary": ((triattention_comparison or {}).get("summary") or {}).get("runtime_anchor_summary", {}),
            "runtime_anchor_quality_summary": ((triattention_comparison or {}).get("summary") or {}).get("runtime_anchor_quality_summary", {}),
        },
    }
