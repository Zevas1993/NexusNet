from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow

from ..comparative_long_context import ComparativeLongContextSuite
from .scorecards import build_triattention_scorecard
from .thresholds import load_triattention_thresholds


class TriAttentionComparativeBenchmark:
    def __init__(self, *, artifacts_dir: Path, provider: Any, runtime_profiles: list[dict[str, Any]] | None = None, retrieval_config: dict[str, Any] | None = None):
        self.artifacts_dir = artifacts_dir
        self.provider = provider
        self.baselines = ComparativeLongContextSuite(runtime_profiles=runtime_profiles, retrieval_config=retrieval_config)

    def run(self, *, context_windows: list[int]) -> dict[str, Any]:
        cases: list[dict[str, Any]] = []
        primary_ratios: list[float] = []
        throughput_ratios: list[float] = []
        latency_ratios: list[float] = []
        stability_deltas: list[float] = []
        reasoning_deltas: list[float] = []
        regression_deltas: list[float] = []
        baseline_providers: set[str] = set()
        comparative_findings: list[dict[str, Any]] = []
        baseline_registry = self.baselines.baseline_catalog()
        runtime_anchor_registry = self.baselines.runtime_anchor_catalog()
        for context_tokens in context_windows:
            tri = self.provider.estimate(context_tokens=context_tokens)
            baselines = self.baselines.baseline_cases(context_tokens=context_tokens)
            runtime_anchors = self.baselines.runtime_anchor_cases(context_tokens=context_tokens)
            primary = baselines[0]
            baseline_providers.update(item["provider_name"] for item in baselines)
            primary_ratios.append(float(tri["kv_memory_mb"]) / max(float(primary["kv_memory_mb"]), 1.0))
            throughput_ratios.append(float(tri["throughput_tokens_per_s"]) / max(float(primary["throughput_tokens_per_s"]), 1.0))
            latency_ratios.append(float(tri["latency_ms"]) / max(float(primary["latency_ms"]), 1.0))
            stability_deltas.append(float(tri["stability_score"]) - float(primary["stability_score"]))
            reasoning_deltas.append(float(tri["reasoning_quality"]) - float(primary["reasoning_quality"]))
            regression_deltas.append(float(tri["long_context_regression"]) - float(primary["long_context_regression"]))
            comparisons = []
            for baseline in baselines:
                comparison = (
                    {
                        "provider_name": baseline["provider_name"],
                        "comparison_kind": baseline.get("comparison_kind"),
                        "source_refs": baseline.get("source_refs", []),
                        "kv_memory_ratio": round(float(tri["kv_memory_mb"]) / max(float(baseline["kv_memory_mb"]), 1.0), 4),
                        "throughput_ratio": round(float(tri["throughput_tokens_per_s"]) / max(float(baseline["throughput_tokens_per_s"]), 1.0), 4),
                        "latency_ratio": round(float(tri["latency_ms"]) / max(float(baseline["latency_ms"]), 1.0), 4),
                        "stability_delta": round(float(tri["stability_score"]) - float(baseline["stability_score"]), 4),
                        "reasoning_delta": round(float(tri["reasoning_quality"]) - float(baseline["reasoning_quality"]), 4),
                        "regression_delta": round(float(tri["long_context_regression"]) - float(baseline["long_context_regression"]), 4),
                    }
                )
                comparisons.append(comparison)
                comparative_findings.append(
                    {
                        "context_tokens": context_tokens,
                        "provider_name": baseline["provider_name"],
                        "wins_memory": comparison["kv_memory_ratio"] < 1.0,
                        "wins_throughput": comparison["throughput_ratio"] > 1.0,
                        "wins_latency": comparison["latency_ratio"] < 1.0,
                        "wins_stability": comparison["stability_delta"] > 0.0,
                        "wins_reasoning": comparison["reasoning_delta"] > 0.0,
                        "wins_regression": comparison["regression_delta"] < 0.0,
                        "source_refs": baseline.get("source_refs", []),
                    }
                )
            runtime_anchor_comparisons = []
            for anchor in runtime_anchors:
                runtime_anchor_comparisons.append(
                    {
                        "provider_name": anchor["provider_name"],
                        "available": anchor.get("available", False),
                        "measurement_mode": anchor.get("measurement_mode"),
                        "source_health": anchor.get("source_health"),
                        "backend_type": anchor.get("backend_type"),
                        "source_refs": anchor.get("source_refs", []),
                        "kv_memory_ratio": round(float(tri["kv_memory_mb"]) / max(float(anchor["kv_memory_mb"]), 1.0), 4),
                        "throughput_ratio": round(float(tri["throughput_tokens_per_s"]) / max(float(anchor["throughput_tokens_per_s"]), 1.0), 4),
                        "latency_ratio": round(float(tri["latency_ms"]) / max(float(anchor["latency_ms"]), 1.0), 4),
                        "stability_delta": round(float(tri["stability_score"]) - float(anchor["stability_score"]), 4),
                        "reasoning_delta": round(float(tri["reasoning_quality"]) - float(anchor["reasoning_quality"]), 4),
                        "regression_delta": round(float(tri["long_context_regression"]) - float(anchor["long_context_regression"]), 4),
                    }
                )
            cases.append(
                {
                    "context_tokens": context_tokens,
                    "triattention": tri,
                    "baselines": baselines,
                    "comparisons": comparisons,
                    "runtime_anchors": runtime_anchor_comparisons,
                }
            )
        head_to_head: dict[str, dict[str, float | int]] = {}
        for provider_name in sorted(baseline_providers):
            comparisons = [
                comparison
                for case in cases
                for comparison in case["comparisons"]
                if comparison["provider_name"] == provider_name
            ]
            head_to_head[provider_name] = {
                "case_count": len(comparisons),
                "avg_kv_memory_ratio": round(sum(item["kv_memory_ratio"] for item in comparisons) / max(len(comparisons), 1), 4),
                "avg_throughput_ratio": round(sum(item["throughput_ratio"] for item in comparisons) / max(len(comparisons), 1), 4),
                "avg_latency_ratio": round(sum(item["latency_ratio"] for item in comparisons) / max(len(comparisons), 1), 4),
                "avg_stability_delta": round(sum(item["stability_delta"] for item in comparisons) / max(len(comparisons), 1), 4),
                "avg_reasoning_delta": round(sum(item["reasoning_delta"] for item in comparisons) / max(len(comparisons), 1), 4),
                "avg_regression_delta": round(sum(item["regression_delta"] for item in comparisons) / max(len(comparisons), 1), 4),
            }
        runtime_anchor_summary: dict[str, dict[str, float | int | bool]] = {}
        for anchor in runtime_anchor_registry:
            provider_name = anchor["provider_name"]
            comparisons = [
                comparison
                for case in cases
                for comparison in case["runtime_anchors"]
                if comparison["provider_name"] == provider_name
            ]
            runtime_anchor_summary[provider_name] = {
                "available": bool(anchor.get("available", False)),
                "case_count": len(comparisons),
                "measurement_mode": anchor.get("measurement_mode"),
                "source_health": anchor.get("health_mode"),
                "observed_latency_ms": anchor.get("observed_latency_ms"),
                "avg_kv_memory_ratio": round(sum(item["kv_memory_ratio"] for item in comparisons) / max(len(comparisons), 1), 4),
                "avg_throughput_ratio": round(sum(item["throughput_ratio"] for item in comparisons) / max(len(comparisons), 1), 4),
                "avg_latency_ratio": round(sum(item["latency_ratio"] for item in comparisons) / max(len(comparisons), 1), 4),
                "avg_stability_delta": round(sum(item["stability_delta"] for item in comparisons) / max(len(comparisons), 1), 4),
                "avg_reasoning_delta": round(sum(item["reasoning_delta"] for item in comparisons) / max(len(comparisons), 1), 4),
                "avg_regression_delta": round(sum(item["regression_delta"] for item in comparisons) / max(len(comparisons), 1), 4),
            }
        runtime_anchor_quality_summary = {
            "anchor_count": len(runtime_anchor_registry),
            "available_count": sum(1 for anchor in runtime_anchor_registry if anchor.get("available")),
            "latency_anchored_count": sum(1 for anchor in runtime_anchor_registry if anchor.get("measurement_mode") == "runtime-profile-latency-anchored"),
            "measurement_modes": {
                mode: sum(1 for anchor in runtime_anchor_registry if anchor.get("measurement_mode") == mode)
                for mode in sorted({str(anchor.get("measurement_mode") or "unknown") for anchor in runtime_anchor_registry})
            },
        }
        summary = {
            "provider_name": "triattention",
            "case_count": len(cases),
            "avg_kv_memory_ratio": round(sum(primary_ratios) / max(len(primary_ratios), 1), 4),
            "avg_throughput_ratio": round(sum(throughput_ratios) / max(len(throughput_ratios), 1), 4),
            "avg_latency_ratio": round(sum(latency_ratios) / max(len(latency_ratios), 1), 4),
            "avg_stability_delta": round(sum(stability_deltas) / max(len(stability_deltas), 1), 4),
            "avg_reasoning_delta": round(sum(reasoning_deltas) / max(len(reasoning_deltas), 1), 4),
            "avg_regression_delta": round(sum(regression_deltas) / max(len(regression_deltas), 1), 4),
            "comparative_findings": comparative_findings[:12],
            "head_to_head": head_to_head,
            "runtime_anchor_summary": runtime_anchor_summary,
            "runtime_anchor_quality_summary": runtime_anchor_quality_summary,
            "generated_at": utcnow().isoformat(),
        }
        thresholds = load_triattention_thresholds()
        scorecard = build_triattention_scorecard(
            summary=summary,
            thresholds=thresholds,
            baseline_providers=sorted(baseline_providers),
        )
        report_id = new_id("triattnbench")
        destination = self.artifacts_dir / "research" / "attention" / "triattention" / report_id
        destination.mkdir(parents=True, exist_ok=True)
        metrics_path = destination / "metrics.json"
        cases_path = destination / "cases.json"
        scorecard_path = destination / "scorecard.json"
        comparative_path = destination / "comparative_summary.json"
        report_path = destination / "report.md"
        summary["baseline_registry"] = baseline_registry
        summary["runtime_anchor_registry"] = runtime_anchor_registry
        metrics_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        cases_path.write_text(json.dumps(cases, indent=2), encoding="utf-8")
        comparative_path.write_text(
            json.dumps(
                {
                    "head_to_head": head_to_head,
                    "baseline_registry": baseline_registry,
                    "runtime_anchor_registry": runtime_anchor_registry,
                    "runtime_anchor_summary": runtime_anchor_summary,
                    "runtime_anchor_quality_summary": runtime_anchor_quality_summary,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        scorecard["report_id"] = report_id
        scorecard["artifact_path"] = str(scorecard_path)
        scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
        report_path.write_text(
            "\n".join(
                [
                    f"# TriAttention Comparative Benchmark {report_id}",
                    "",
                    f"- Case count: {summary['case_count']}",
                    f"- Average KV memory ratio: {summary['avg_kv_memory_ratio']}",
                    f"- Average throughput ratio: {summary['avg_throughput_ratio']}",
                    f"- Average latency ratio: {summary['avg_latency_ratio']}",
                    f"- Average stability delta: {summary['avg_stability_delta']}",
                    f"- Average reasoning delta: {summary['avg_reasoning_delta']}",
                    f"- Average long-context regression delta: {summary['avg_regression_delta']}",
                    f"- Thresholds passed: {scorecard['passed']}",
                    f"- Baseline providers: {', '.join(sorted(baseline_providers))}",
                    f"- Runtime anchors: {', '.join(item['provider_name'] for item in runtime_anchor_registry) if runtime_anchor_registry else 'none'}",
                    f"- Runtime anchors available: {runtime_anchor_quality_summary['available_count']}/{runtime_anchor_quality_summary['anchor_count']}",
                    f"- Latency-anchored runtime baselines: {runtime_anchor_quality_summary['latency_anchored_count']}",
                ]
            ),
            encoding="utf-8",
        )
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "report_id": report_id,
            "provider_name": "triattention",
            "summary": summary,
            "cases": cases,
            "baseline_providers": sorted(baseline_providers),
            "baseline_registry": baseline_registry,
            "runtime_anchor_registry": runtime_anchor_registry,
            "scorecard": scorecard,
            "artifacts": {
                "metrics": str(metrics_path),
                "cases": str(cases_path),
                "scorecard": str(scorecard_path),
                "comparative_summary": str(comparative_path),
                "report": str(report_path),
            },
        }
