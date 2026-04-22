from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file


class CostEnergyEvaluationService:
    def __init__(self, *, config_dir: Path, runtime_configs: dict[str, Any]):
        repo_default = Path(__file__).resolve().parents[3] / "runtime" / "config" / "openjarvis_lane.yaml"
        self.config = runtime_configs.get("openjarvis_lane") or load_yaml_file(
            config_dir / "openjarvis_lane.yaml",
            load_yaml_file(repo_default, {}),
        )

    def summarize(self, traces: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        traces = traces or []
        cfg = ((self.config.get("cost_energy") or {}).get("defaults") or {})
        remote_hints = set((self.config.get("cost_energy") or {}).get("remote_runtime_hints", []))
        totals = {
            "trace_count": len(traces),
            "latency_ms": 0.0,
            "energy_wh": 0.0,
            "estimated_flops": 0.0,
            "dollar_cost": 0.0,
        }
        by_runtime: dict[str, dict[str, float]] = {}
        for trace in traces:
            runtime_name = str(trace.get("runtime_name") or "unknown")
            metrics = trace.get("metrics") or {}
            latency = float(metrics.get("brain_latency_ms") or trace.get("latency_ms") or 0.0)
            is_remote = runtime_name in remote_hints or "openai" in runtime_name or "cloud" in runtime_name
            energy_rate = float(cfg.get("remote_energy_wh_per_latency_ms" if is_remote else "local_energy_wh_per_latency_ms", 0.0))
            flops_rate = float(cfg.get("remote_flops_per_latency_ms" if is_remote else "local_flops_per_latency_ms", 0.0))
            cost_rate = float(cfg.get("remote_dollar_per_latency_ms" if is_remote else "local_dollar_per_latency_ms", 0.0))
            energy = round(latency * energy_rate, 6)
            flops = round(latency * flops_rate, 2)
            cost = round(latency * cost_rate, 6)
            bucket = by_runtime.setdefault(runtime_name, {"latency_ms": 0.0, "energy_wh": 0.0, "estimated_flops": 0.0, "dollar_cost": 0.0})
            bucket["latency_ms"] += latency
            bucket["energy_wh"] += energy
            bucket["estimated_flops"] += flops
            bucket["dollar_cost"] += cost
            totals["latency_ms"] += latency
            totals["energy_wh"] += energy
            totals["estimated_flops"] += flops
            totals["dollar_cost"] += cost
        for bucket in by_runtime.values():
            for key in bucket:
                bucket[key] = round(bucket[key], 6 if key != "estimated_flops" else 2)
        for key in totals:
            if key != "trace_count":
                totals[key] = round(totals[key], 6 if key != "estimated_flops" else 2)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "summary": totals,
            "by_runtime": by_runtime,
            "dimensions": ["energy_wh", "estimated_flops", "latency_ms", "dollar_cost"],
        }
