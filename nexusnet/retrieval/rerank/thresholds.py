from __future__ import annotations

from typing import Any


def load_rerank_thresholds(config: dict[str, Any]) -> dict[str, Any]:
    operational = (config.get("operationalization") or {})
    thresholds = dict(operational.get("thresholds", {}))
    return {
        "min_case_count": int(thresholds.get("min_case_count", 4)),
        "min_pass_rate": float(thresholds.get("min_pass_rate", 0.75)),
        "min_relevance_delta": float(thresholds.get("min_relevance_delta", 0.0)),
        "min_groundedness_delta": float(thresholds.get("min_groundedness_delta", 0.0)),
        "min_provenance_delta": float(thresholds.get("min_provenance_delta", 0.0)),
        "max_latency_delta_ms": float(thresholds.get("max_latency_delta_ms", 120.0)),
        "min_provider_coverage": float(thresholds.get("min_provider_coverage", 0.5)),
    }


def evaluate_rerank_thresholds(metrics: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "case_count": {
            "passed": int(metrics.get("case_count", 0)) >= thresholds["min_case_count"],
            "actual": int(metrics.get("case_count", 0)),
            "expected": thresholds["min_case_count"],
        },
        "pass_rate": {
            "passed": float(metrics.get("pass_rate", 0.0)) >= thresholds["min_pass_rate"],
            "actual": float(metrics.get("pass_rate", 0.0)),
            "expected": thresholds["min_pass_rate"],
        },
        "relevance_delta": {
            "passed": float(metrics.get("avg_relevance_delta", 0.0)) >= thresholds["min_relevance_delta"],
            "actual": float(metrics.get("avg_relevance_delta", 0.0)),
            "expected": thresholds["min_relevance_delta"],
        },
        "groundedness_delta": {
            "passed": float(metrics.get("avg_groundedness_delta", 0.0)) >= thresholds["min_groundedness_delta"],
            "actual": float(metrics.get("avg_groundedness_delta", 0.0)),
            "expected": thresholds["min_groundedness_delta"],
        },
        "provenance_delta": {
            "passed": float(metrics.get("avg_provenance_delta", 0.0)) >= thresholds["min_provenance_delta"],
            "actual": float(metrics.get("avg_provenance_delta", 0.0)),
            "expected": thresholds["min_provenance_delta"],
        },
        "latency_delta_ms": {
            "passed": float(metrics.get("avg_latency_delta_ms", 0.0)) <= thresholds["max_latency_delta_ms"],
            "actual": float(metrics.get("avg_latency_delta_ms", 0.0)),
            "expected": thresholds["max_latency_delta_ms"],
        },
        "provider_coverage": {
            "passed": float(metrics.get("provider_coverage", 0.0)) >= thresholds["min_provider_coverage"],
            "actual": float(metrics.get("provider_coverage", 0.0)),
            "expected": thresholds["min_provider_coverage"],
        },
    }
    return {
        "passed": all(item["passed"] for item in checks.values()),
        "checks": checks,
    }
