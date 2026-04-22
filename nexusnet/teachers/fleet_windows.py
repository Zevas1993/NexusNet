from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file

from .fleet_registry import _resolve_fleet_path


@dataclass(frozen=True)
class TeacherFleetWindowSpec:
    window_id: str
    canon_status: str
    description: str
    lookback_runs: int
    minimum_sample_count: int
    maximum_age_days: int


class TeacherFleetWindowRegistry:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.path = _resolve_fleet_path(config_dir)
        self._payload = load_yaml_file(self.path, {})
        self.status_label = self._payload.get("canon_status", "LOCKED CANON")
        self.schema_version = int(self._payload.get("schema_version", 1))
        self.default_window_id = str(self._payload.get("default_window_id", "medium"))

    def metadata(self) -> dict[str, Any]:
        return {
            "status_label": self.status_label,
            "schema_version": self.schema_version,
            "path": str(self.path),
            "default_window_id": self.default_window_id,
            "windows": sorted((self._payload.get("governance_windows", {}) or {}).keys()),
        }

    def resolve(self, window_id: str | None = None) -> TeacherFleetWindowSpec:
        selected = window_id or self.default_window_id
        payload = (self._payload.get("governance_windows", {}) or {}).get(selected)
        if payload is None:
            raise KeyError(f"Unknown teacher fleet window: {selected}")
        return TeacherFleetWindowSpec(
            window_id=selected,
            canon_status=str(payload.get("canon_status", self.status_label)),
            description=str(payload.get("description", "")),
            lookback_runs=int(payload.get("lookback_runs", 12)),
            minimum_sample_count=int(payload.get("minimum_sample_count", 5)),
            maximum_age_days=int(payload.get("maximum_age_days", 21)),
        )
