from __future__ import annotations

from typing import Any

from nexus.schemas import new_id, utcnow


def build_rerank_scorecard(
    *,
    metrics: dict[str, Any],
    thresholds: dict[str, Any],
    threshold_report: dict[str, Any],
    cases: list[dict[str, Any]],
    policy_mode: str,
    benchmark_family_id: str = "retrieval-rerank-operational",
    threshold_set_id: str = "retrieval-rerank-v2026-r1",
) -> dict[str, Any]:
    passing_cases = sum(1 for case in cases if case.get("passed"))
    failing_cases = len(cases) - passing_cases
    return {
        "scorecard_id": new_id("retrievalscore"),
        "status_label": "STRONG ACCEPTED DIRECTION",
        "created_at": utcnow().isoformat(),
        "policy_mode": policy_mode,
        "benchmark_family_id": benchmark_family_id,
        "threshold_set_id": threshold_set_id,
        "passed": threshold_report.get("passed", False),
        "metrics": metrics,
        "thresholds": thresholds,
        "threshold_report": threshold_report,
        "summary": {
            "case_count": len(cases),
            "passing_case_count": passing_cases,
            "failing_case_count": failing_cases,
            "provider_names": sorted({case.get("reranker_provider") for case in cases if case.get("reranker_provider")}),
        },
        "cases": cases,
    }
