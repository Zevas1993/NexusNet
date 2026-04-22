from __future__ import annotations

from nexus.runtimes import RuntimeRegistry


class QESRuntimeMetrics:
    def __init__(self, runtime_registry: RuntimeRegistry):
        self.runtime_registry = runtime_registry

    def collect(self) -> list[dict]:
        metrics = []
        for profile in self.runtime_registry.list_profiles():
            payload = profile.model_dump(mode="json")
            payload["ttft_ms"] = payload.get("metrics", {}).get("latency_ms", 0)
            payload["throughput_tokens_per_s"] = max(1, int(1000 / max(payload["ttft_ms"] or 1, 1)))
            payload["failure_rate"] = 0.0 if payload.get("available") else 1.0
            metrics.append(payload)
        return metrics
