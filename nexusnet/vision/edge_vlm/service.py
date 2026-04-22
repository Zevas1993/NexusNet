from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file

from .benchmarks import EdgeVisionOperationalBenchmarkSuite


class EdgeVisionLaneService:
    def __init__(self, *, config_dir: Path, artifacts_dir: Path, runtime_configs: dict[str, Any]):
        repo_default = Path(__file__).resolve().parents[3] / "runtime" / "config" / "vision_edge.yaml"
        self.config = runtime_configs.get("vision_edge") or load_yaml_file(config_dir / "vision_edge.yaml", load_yaml_file(repo_default, {}))
        self.benchmarks = EdgeVisionOperationalBenchmarkSuite(artifacts_dir=artifacts_dir, config=self.config)

    def summary(self) -> dict[str, Any]:
        provider_map = self.config.get("providers", {}) or {}
        providers: dict[str, Any] = {}
        for provider_id, payload in provider_map.items():
            item = dict(payload)
            item.setdefault("languages", list(item.get("multilingual_languages", [])))
            providers[provider_id] = item

        default_provider = providers.get(self.config.get("default_provider"), {})
        return {
            "status_label": self.config.get("canon_status", "EXPLORATORY / PROTOTYPE"),
            "enabled": bool(self.config.get("enabled", False)),
            "default_provider": self.config.get("default_provider"),
            "providers": providers,
            "latency_profiles": self.config.get("latency_profiles", {}),
            "function_catalog": self.config.get("function_catalog", []),
            "grounding_schema": self.config.get("grounding_schema", {}),
            "benchmark_summary": self.benchmarks.summary(),
            "teacher_candidates": [
                {
                    "teacher_id": default_provider.get("candidate_teacher_id"),
                    "subject": default_provider.get("candidate_teacher_subject"),
                    "modes": default_provider.get("candidate_modes", []),
                    "provider_name": default_provider.get("provider_name"),
                }
            ]
            if default_provider
            else [],
        }

    def benchmark(self, provider_id: str | None = None) -> dict[str, Any]:
        return self.benchmarks.run(provider_id=provider_id)
