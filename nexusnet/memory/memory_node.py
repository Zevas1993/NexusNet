from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file, save_yaml_file

from .planes import MemoryPlaneRegistry, _default_plane_payload


class MemoryNode:
    def __init__(self, *, project_root: Path, runtime_configs: dict[str, Any] | None = None):
        self.project_root = Path(project_root)
        self.runtime_configs = runtime_configs or {}
        self.root_config_path = self.project_root / "config" / "planes.yaml"
        self.legacy_runtime_config_path = self.project_root / "runtime" / "config" / "planes.yaml"
        self._ensure_root_config()
        self.registry = MemoryPlaneRegistry(
            config_path=self.root_config_path,
            fallback_path=self.legacy_runtime_config_path if self.legacy_runtime_config_path.exists() else None,
        )

    def _ensure_root_config(self) -> None:
        if self.root_config_path.exists():
            return
        payload = load_yaml_file(
            self.legacy_runtime_config_path,
            self.runtime_configs.get("planes") or _default_plane_payload(),
        )
        save_yaml_file(self.root_config_path, payload)

    def summary(self) -> dict[str, Any]:
        configs = self.registry.list_configs()
        projection_adapters = self.registry.projection_adapters()
        return {
            "status_label": "LOCKED CANON",
            "config_path": str(self.root_config_path),
            "legacy_runtime_config_path": str(self.legacy_runtime_config_path),
            "plane_count": len(configs),
            "planes": [config.model_dump(mode="json") for config in configs],
            "projection_adapters": [adapter.model_dump(mode="json") for adapter in projection_adapters],
            "compatibility_views": ["3-plane", "8-plane", "11-plane-operational"],
            "routing_planes": [config.plane_name for config in configs if config.plane_name in {"conceptual", "goal", "predictive"}],
            "dreaming_planes": [config.plane_name for config in configs if config.plane_name in {"imaginal", "predictive", "metacognitive"}],
            "retrieval_planes": [config.plane_name for config in configs if "semantic" in config.projection_roles or "temporal" in config.projection_roles],
            "foundry_evidence_planes": [config.plane_name for config in configs if config.plane_name in {"metacognitive", "goal", "predictive"}],
            "metadata": self.registry.metadata(),
            "raw_config": load_yaml_file(self.root_config_path, _default_plane_payload()),
        }

    def execution_context(self, *, task_type: str, requested_plane_tags: list[str] | None = None) -> dict[str, Any]:
        summary = self.summary()
        requested = sorted(set(requested_plane_tags or []))
        active_planes = requested or summary["routing_planes"]
        return {
            "plane_count": summary["plane_count"],
            "active_planes": active_planes,
            "compatibility_views": summary["compatibility_views"],
            "projection_names": [adapter["projection_name"] for adapter in summary["projection_adapters"]],
            "config_path": summary["config_path"],
            "task_type": task_type,
            "dreaming_planes": summary["dreaming_planes"],
            "retrieval_planes": summary["retrieval_planes"],
            "foundry_evidence_planes": summary["foundry_evidence_planes"],
        }
