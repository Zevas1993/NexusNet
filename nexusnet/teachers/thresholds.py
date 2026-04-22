from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file


@dataclass(frozen=True)
class TeacherThresholdSpec:
    threshold_set_id: str
    version: int
    weighted_score_min: float
    metric_rules: dict[str, dict[str, Any]]
    canon_status: str


class TeacherThresholdRegistry:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.project_root = config_dir.parents[1]
        self.repo_root = Path(__file__).resolve().parents[2]
        self.package_dir = Path(__file__).resolve().parent
        self.manifest_path = config_dir / "teachers.yaml"
        self.fallback_manifest = self.repo_root / "runtime" / "config" / "teachers.yaml"
        self._manifest = load_yaml_file(self.manifest_path, {}) or load_yaml_file(self.fallback_manifest, {})
        self.path = self._resolve_thresholds_path()
        self._payload = load_yaml_file(self.path, {})
        self.status_label = self._payload.get("canon_status", "LOCKED CANON")
        self.schema_version = int(self._payload.get("schema_version", 1))
        self.default_threshold_set_id = self._payload.get("default_threshold_set_id", "teacher-v2026-r1")

    def metadata(self) -> dict[str, Any]:
        return {
            "status_label": self.status_label,
            "schema_version": self.schema_version,
            "default_threshold_set_id": self.default_threshold_set_id,
            "path": str(self.path),
            "threshold_sets": sorted(self._payload.get("threshold_sets", {}).keys()),
        }

    def resolve(
        self,
        *,
        subject: str,
        benchmark_family: str,
        threshold_set_id: str | None = None,
    ) -> TeacherThresholdSpec:
        selected_id = threshold_set_id or self.default_threshold_set_id
        threshold_sets = self._payload.get("threshold_sets", {})
        payload = threshold_sets.get(selected_id)
        if payload is None:
            raise KeyError(f"Unknown teacher threshold set: {selected_id}")
        metric_rules = dict(payload.get("default_metric_rules", {}))
        weighted_score_min = float(payload.get("default_weighted_score_min", 0.74))

        subject_overrides = payload.get("subject_overrides", {}).get(subject, {})
        metric_rules.update(subject_overrides.get("metric_rules", {}))
        weighted_score_min = float(subject_overrides.get("default_weighted_score_min", weighted_score_min))

        family_overrides = subject_overrides.get("family_overrides", {}).get(benchmark_family, {})
        metric_rules.update(family_overrides.get("metric_rules", {}))
        weighted_score_min = float(family_overrides.get("weighted_score_min", weighted_score_min))

        return TeacherThresholdSpec(
            threshold_set_id=selected_id,
            version=int(payload.get("version", 1)),
            weighted_score_min=weighted_score_min,
            metric_rules=metric_rules,
            canon_status=payload.get("canon_status", self.status_label),
        )

    def _resolve_thresholds_path(self) -> Path:
        refs = self._manifest.get("registry_files", {})
        ref = refs.get("thresholds", "nexusnet/teachers/teacher_benchmark_thresholds.yaml")
        candidate = Path(ref)
        if candidate.is_absolute() and candidate.exists():
            return candidate
        candidates = [
            self.config_dir / candidate.name,
            self.project_root / ref,
            self.repo_root / ref,
            self.package_dir / candidate.name,
        ]
        for path in candidates:
            if path.exists():
                return path
        return self.package_dir / candidate.name
