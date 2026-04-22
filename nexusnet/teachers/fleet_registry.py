from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file


def _resolve_fleet_path(config_dir: Path) -> Path:
    project_root = config_dir.parents[1]
    repo_root = Path(__file__).resolve().parents[2]
    package_dir = Path(__file__).resolve().parent
    manifest_path = config_dir / "teachers.yaml"
    fallback_manifest = repo_root / "runtime" / "config" / "teachers.yaml"
    manifest = load_yaml_file(manifest_path, {}) or load_yaml_file(fallback_manifest, {})
    refs = manifest.get("registry_files", {})
    ref = refs.get("fleets", "nexusnet/teachers/teacher_benchmark_fleets.yaml")
    candidate = Path(ref)
    if candidate.is_absolute() and candidate.exists():
        return candidate
    for path in (
        config_dir / candidate.name,
        project_root / ref,
        repo_root / ref,
        package_dir / candidate.name,
    ):
        if path.exists():
            return path
    return package_dir / candidate.name


@dataclass(frozen=True)
class TeacherBenchmarkFleetSpec:
    fleet_id: str
    canon_status: str
    description: str
    subjects: list[str]
    benchmark_families: list[str]
    teacher_pairs: list[str]
    budget_classes: list[str]
    output_forms: list[str]
    risk_tiers: list[str]
    localities: list[str]
    hardware_classes: list[str]
    lineage: list[str]
    threshold_set_id: str


class TeacherBenchmarkFleetRegistry:
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
            "fleets": sorted(self._payload.get("fleets", {}).keys()),
        }

    def list_fleets(self) -> list[TeacherBenchmarkFleetSpec]:
        return [self.resolve(fleet_id) for fleet_id in sorted(self._payload.get("fleets", {}).keys())]

    def resolve(self, fleet_id: str) -> TeacherBenchmarkFleetSpec:
        payload = (self._payload.get("fleets", {}) or {}).get(fleet_id)
        if payload is None:
            raise KeyError(f"Unknown benchmark fleet: {fleet_id}")
        return TeacherBenchmarkFleetSpec(
            fleet_id=fleet_id,
            canon_status=str(payload.get("canon_status", self.status_label)),
            description=str(payload.get("description", "")),
            subjects=list(payload.get("subjects", [])),
            benchmark_families=list(payload.get("benchmark_families", [])),
            teacher_pairs=list(payload.get("teacher_pairs", [])),
            budget_classes=list(payload.get("budget_classes", [])),
            output_forms=list(payload.get("output_forms", [])),
            risk_tiers=list(payload.get("risk_tiers", [])),
            localities=list(payload.get("localities", [])),
            hardware_classes=list(payload.get("hardware_classes", [])),
            lineage=list(payload.get("lineage", [])),
            threshold_set_id=str(payload.get("threshold_set_id", "teacher-v2026-r1")),
        )

    def fleets_for_subject(self, subject: str) -> list[TeacherBenchmarkFleetSpec]:
        return [fleet for fleet in self.list_fleets() if subject in fleet.subjects]

    def preferred_fleet_ids(self, *, subject: str, candidate_kind: str | None = None) -> list[str]:
        subject_fleets = {fleet.fleet_id for fleet in self.fleets_for_subject(subject)}
        if candidate_kind == "native-takeover" and "takeover_validation_fleet" in subject_fleets:
            return ["takeover_validation_fleet"]
        ordered = [
            "coding_agent_fleet",
            "multimodal_fleet",
            "long_context_fleet",
            "low_hardware_fleet",
            "safety_sensitive_fleet",
            "local_reasoning_fleet",
        ]
        for fleet_id in ordered:
            if fleet_id in subject_fleets:
                return [fleet_id]
        return sorted(subject_fleets)[:1]
