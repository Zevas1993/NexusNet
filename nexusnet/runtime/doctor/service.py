from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file


class RuntimeDoctorService:
    def __init__(
        self,
        *,
        config_dir: Path,
        runtime_configs: dict[str, Any],
        runtime_registry: Any,
        runtime_profiler: Any,
        init_service: Any,
        edge_vision_service: Any,
    ):
        repo_default = Path(__file__).resolve().parents[3] / "runtime" / "config" / "openjarvis_lane.yaml"
        self.config = runtime_configs.get("openjarvis_lane") or load_yaml_file(
            config_dir / "openjarvis_lane.yaml",
            load_yaml_file(repo_default, {}),
        )
        self.runtime_registry = runtime_registry
        self.runtime_profiler = runtime_profiler
        self.init_service = init_service
        self.edge_vision_service = edge_vision_service

    def summary(self) -> dict[str, Any]:
        profiles = [profile.model_dump(mode="json") for profile in self.runtime_registry.list_profiles()]
        available = [profile["runtime_name"] for profile in profiles if profile.get("available")]
        recommendation = self.init_service.recommend()
        findings = [
            "Keep local-first runtimes ahead of cloud fallback recommendations.",
            "Prefer preset bundles that already fit visible local runtimes and the current device profile.",
            "Preserve scheduled-monitor and edge-lane workflows as subordinate AO surfaces, not a second command shell.",
        ]
        if not available:
            findings.append("No live local runtime detected; keep fallback guidance informational and non-destructive.")
        if self.edge_vision_service.summary().get("enabled"):
            findings.append("Edge vision lane remains available for low-power or safe-mode workflows.")
        return {
            "status_label": self.config.get("canon_status", "STRONG ACCEPTED DIRECTION"),
            "device_profile": self.runtime_profiler.device_profile().model_dump(mode="json"),
            "runtime_profiles": profiles,
            "available_runtimes": available,
            "recommendation_matrix": self.init_service.recommendation_matrix(),
            "recommended_preset": recommendation,
            "checks": {
                "local_runtime_detected": bool(available),
                "edge_vision_enabled": bool(self.edge_vision_service.summary().get("enabled")),
                "cloud_only_when_necessary": bool((self.config.get("doctor") or {}).get("cloud_only_when_necessary", True)),
            },
            "findings": findings,
        }
