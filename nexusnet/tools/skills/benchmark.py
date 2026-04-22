from __future__ import annotations

from collections import Counter
from typing import Any


class SkillBenchmarkService:
    def __init__(self, *, skill_registry: Any):
        self.skill_registry = skill_registry

    def benchmark_from_traces(self, traces: list[dict[str, Any]]) -> dict[str, Any]:
        packages = self.skill_registry.list_packages()
        hits = Counter()
        latencies: list[float] = []
        for trace in traces:
            selected_tools = ((trace.get("metrics") or {}).get("requested_tools") or []) + ((trace.get("metrics") or {}).get("resolved_tools") or [])
            normalized_tools = {str(item) for item in selected_tools}
            for package in packages:
                if normalized_tools.intersection(package.get("allowed_tools", [])):
                    hits[package["skill_id"]] += 1
            latency = (trace.get("metrics") or {}).get("brain_latency_ms")
            if latency is not None:
                latencies.append(float(latency))
        return {
            "trace_count": len(traces),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
            "top_impacted_skills": [
                {"skill_id": skill_id, "observed_hits": count}
                for skill_id, count in hits.most_common(8)
            ],
            "benchmark_mode": "local-trace-history",
        }

    def optimize_from_traces(self, traces: list[dict[str, Any]]) -> dict[str, Any]:
        benchmark = self.benchmark_from_traces(traces)
        proposals = []
        for item in benchmark.get("top_impacted_skills", [])[:4]:
            proposals.append(
                {
                    "skill_id": item["skill_id"],
                    "suggestion": "increase-catalog-visibility" if item["observed_hits"] >= 2 else "keep-shadow",
                    "requires_review": True,
                    "source": "local-trace-history",
                }
            )
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "proposal_count": len(proposals),
            "proposals": proposals,
            "governance": {
                "requires_evalsao": True,
                "requires_gateway_allowlist_review": True,
            },
        }
