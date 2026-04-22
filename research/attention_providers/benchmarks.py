from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow

from .triattention import TriAttentionComparativeBenchmark


class AttentionBenchmarkSuite:
    def __init__(self, *, artifacts_dir: Path, registry: Any, runtime_profile_provider: Any | None = None, retrieval_config: dict[str, Any] | None = None):
        self.artifacts_dir = artifacts_dir
        self.registry = registry
        self.runtime_profile_provider = runtime_profile_provider
        self.retrieval_config = retrieval_config or {}

    def run(self, *, provider_name: str = "triattention", context_windows: list[int] | None = None) -> dict[str, Any]:
        provider = self.registry.get_provider(provider_name)
        context_windows = context_windows or [4096, 8192, 16384, 32768]
        if provider is None:
            return {
                "status_label": "IMPLEMENTATION BRANCH",
                "provider_name": provider_name,
                "summary": {"reason": "Unknown attention provider."},
                "artifacts": {},
            }
        if provider_name == "triattention":
            runtime_profiles = self.runtime_profile_provider() if self.runtime_profile_provider is not None else []
            return TriAttentionComparativeBenchmark(
                artifacts_dir=self.artifacts_dir,
                provider=provider,
                runtime_profiles=runtime_profiles,
                retrieval_config=self.retrieval_config,
            ).run(context_windows=context_windows)

        cases = [provider.estimate(context_tokens=value) for value in context_windows]
        summary = {
            "provider_name": provider_name,
            "case_count": len(cases),
            "avg_kv_memory_mb": round(sum(case["kv_memory_mb"] for case in cases) / max(len(cases), 1), 3),
            "avg_throughput_tokens_per_s": round(sum(case["throughput_tokens_per_s"] for case in cases) / max(len(cases), 1), 3),
            "avg_stability_score": round(sum(case["stability_score"] for case in cases) / max(len(cases), 1), 3),
            "avg_reasoning_quality": round(sum(case["reasoning_quality"] for case in cases) / max(len(cases), 1), 3),
            "avg_long_context_regression": round(sum(case["long_context_regression"] for case in cases) / max(len(cases), 1), 3),
            "generated_at": utcnow().isoformat(),
        }
        report_id = new_id("attentionbench")
        destination = self.artifacts_dir / "research" / "attention" / provider_name / report_id
        destination.mkdir(parents=True, exist_ok=True)
        metrics_path = destination / "metrics.json"
        cases_path = destination / "cases.json"
        report_path = destination / "report.md"
        metrics_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        cases_path.write_text(json.dumps(cases, indent=2), encoding="utf-8")
        report_path.write_text(
            "\n".join(
                [
                    f"# Attention Research Benchmark {report_id}",
                    "",
                    f"- Provider: {provider_name}",
                    f"- Case count: {summary['case_count']}",
                    f"- Average KV memory MB: {summary['avg_kv_memory_mb']}",
                    f"- Average throughput tokens/s: {summary['avg_throughput_tokens_per_s']}",
                    f"- Average stability score: {summary['avg_stability_score']}",
                    f"- Average reasoning quality: {summary['avg_reasoning_quality']}",
                    f"- Average long-context regression: {summary['avg_long_context_regression']}",
                ]
            ),
            encoding="utf-8",
        )
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "report_id": report_id,
            "summary": summary,
            "cases": cases,
            "artifacts": {
                "metrics": str(metrics_path),
                "cases": str(cases_path),
                "report": str(report_path),
            },
        }

    def summary(self) -> dict:
        latest = None
        latest_scorecard = None
        latest_comparative_summary = None
        base = self.artifacts_dir / "research" / "attention"
        if base.exists():
            candidates = sorted(base.glob("*/*/metrics.json"), reverse=True)
            if candidates:
                latest = json.loads(candidates[0].read_text(encoding="utf-8"))
            scorecards = sorted(base.glob("triattention/*/scorecard.json"), reverse=True)
            if scorecards:
                latest_scorecard = json.loads(scorecards[0].read_text(encoding="utf-8"))
            comparative = sorted(base.glob("triattention/*/comparative_summary.json"), reverse=True)
            if comparative:
                latest_comparative_summary = json.loads(comparative[0].read_text(encoding="utf-8"))
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "benchmarks": ["kv-memory", "throughput", "stability", "reasoning-quality", "long-context-regression"],
            "default_on": False,
            "latest_benchmark": latest,
            "latest_comparative_scorecard": latest_scorecard,
            "latest_comparative_summary": latest_comparative_summary,
        }
