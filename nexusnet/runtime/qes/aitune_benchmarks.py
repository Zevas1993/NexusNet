from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus.schemas import ModelRegistration

from ...schemas import BenchmarkMatrixRecord


class AITuneBenchmarkSuite:
    def __init__(self, *, config: dict[str, Any]):
        self.config = config

    def build_result(
        self,
        *,
        model: ModelRegistration,
        capability: dict[str, Any],
        applicability: dict[str, Any],
        adapter_result: dict[str, Any],
        compatibility_artifact_path: str,
        benchmark_artifact_path: str | None = None,
        tuned_artifact_path: str | None = None,
    ) -> dict[str, Any]:
        selected_backend = adapter_result.get("selected_backend")
        rollback_reference = applicability.get("rollback_reference")
        host_specific = applicability.get("host_specific", True)
        portable = not host_specific and bool(tuned_artifact_path)
        metrics = self._metrics_for(
            capability=capability,
            applicability=applicability,
            adapter_result=adapter_result,
            rollback_reference=rollback_reference,
            tuned_artifact_path=tuned_artifact_path,
            benchmark_artifact_path=benchmark_artifact_path,
        )
        records: list[BenchmarkMatrixRecord] = []
        if adapter_result.get("status") == "completed" and selected_backend:
            records.append(
                BenchmarkMatrixRecord(
                    model_id=model.model_id,
                    runtime_name=f"aitune::{selected_backend}",
                    lineage="live-derived",
                    metrics=metrics,
                    status_label="EXPLORATORY / PROTOTYPE",
                )
            )
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "provider_name": "aitune",
            "status": adapter_result.get("status", "skipped"),
            "reason": adapter_result.get("reason"),
            "records": [record.model_dump(mode="json") for record in records],
            "environment": capability,
            "applicability": applicability,
            "selected_backend": selected_backend,
            "host_specific": host_specific,
            "portable": portable,
            "rollback_reference": rollback_reference,
            "artifacts": {
                "compatibility": compatibility_artifact_path,
                "benchmark": benchmark_artifact_path,
                "tuned_artifact": tuned_artifact_path,
            },
            "governance": {
                "require_external_evaluation": bool((self.config.get("rollout") or {}).get("require_external_evaluation", True)),
                "require_promotion_approval": bool((self.config.get("rollout") or {}).get("require_promotion_approval", True)),
                "require_rollback_reference": bool((self.config.get("rollout") or {}).get("require_rollback_reference", True)),
            },
            "errors": adapter_result.get("errors", []),
        }

    def _metrics_for(
        self,
        *,
        capability: dict[str, Any],
        applicability: dict[str, Any],
        adapter_result: dict[str, Any],
        rollback_reference: str,
        tuned_artifact_path: str | None,
        benchmark_artifact_path: str | None,
    ) -> dict[str, Any]:
        defaults = self.config.get("benchmark_defaults", {}) or {}
        raw_metrics = dict(adapter_result.get("metrics", {}) or {})
        latency_ms = float(raw_metrics.get("latency_ms", defaults.get("latency_budget_ms", 0.0)) or 0.0)
        throughput = float(raw_metrics.get("throughput_tokens_per_s", defaults.get("throughput_floor", 0.0)) or 0.0)
        correctness = float(raw_metrics.get("correctness", defaults.get("correctness_floor", 0.0)) or 0.0)
        return {
            "latency_ms": latency_ms,
            "ttft_ms": latency_ms,
            "throughput_tokens_per_s": throughput,
            "correctness": correctness,
            "hardware_profile": {
                "platform_name": capability.get("platform_name"),
                "python_version": capability.get("python_version"),
                "torch_cuda_available": capability.get("torch_cuda_available"),
                "cuda_device_count": capability.get("cuda_device_count"),
            },
            "artifact_lineage": {
                "source_model": applicability.get("source_model"),
                "source_runtime": applicability.get("source_runtime"),
                "target_lane": applicability.get("target_lane"),
                "selected_backend": adapter_result.get("selected_backend"),
            },
            "environment_compatibility": {
                "available": capability.get("available", False),
                "provider_health": capability.get("provider_health"),
                "portable": applicability.get("portable", False),
                "host_specific": applicability.get("host_specific", True),
            },
            "rollback_reference": rollback_reference,
            "benchmark_artifact_path": benchmark_artifact_path,
            "tuned_artifact_path": tuned_artifact_path,
            "qes_provider": "aitune",
            "provider_status": adapter_result.get("status"),
        }
