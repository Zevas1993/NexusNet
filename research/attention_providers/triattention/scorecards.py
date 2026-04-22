from __future__ import annotations

from typing import Any

from nexus.schemas import new_id, utcnow


def build_triattention_scorecard(*, summary: dict[str, Any], thresholds: dict[str, Any], baseline_providers: list[str]) -> dict[str, Any]:
    checks = {
        "kv_memory_ratio": float(summary.get("avg_kv_memory_ratio", 1.0)) <= float(thresholds.get("max_avg_kv_memory_ratio", 1.0)),
        "throughput_ratio": float(summary.get("avg_throughput_ratio", 0.0)) >= float(thresholds.get("min_avg_throughput_ratio", 0.0)),
        "latency_ratio": float(summary.get("avg_latency_ratio", 1.0)) <= float(thresholds.get("max_avg_latency_ratio", 1.0)),
        "stability_delta": float(summary.get("avg_stability_delta", 0.0)) >= float(thresholds.get("min_avg_stability_delta", 0.0)),
        "reasoning_delta": float(summary.get("avg_reasoning_delta", 0.0)) >= float(thresholds.get("min_avg_reasoning_delta", 0.0)),
        "regression_delta": float(summary.get("avg_regression_delta", 0.0)) <= float(thresholds.get("max_avg_regression_delta", 0.0)),
    }
    return {
        "scorecard_id": new_id("triattnscore"),
        "schema_family": "triattention-comparative-scorecard",
        "schema_version": 1,
        "status_label": "EXPLORATORY / PROTOTYPE",
        "provider_name": "triattention",
        "created_at": utcnow().isoformat(),
        "baseline_providers": baseline_providers,
        "threshold_set_id": thresholds.get("threshold_set_id"),
        "passed": all(checks.values()),
        "checks": checks,
        "summary": summary,
        "comparative_findings": summary.get("comparative_findings", []),
        "runtime_anchor_quality_summary": summary.get("runtime_anchor_quality_summary", {}),
        "thresholds": thresholds,
    }
