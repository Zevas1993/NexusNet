from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file

from .thresholds import TeacherThresholdRegistry


class TeacherBenchmarkRegistry:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.project_root = config_dir.parents[1]
        self.repo_root = Path(__file__).resolve().parents[2]
        self.package_dir = Path(__file__).resolve().parent
        self.manifest_path = config_dir / "teachers.yaml"
        self.fallback_manifest = self.repo_root / "runtime" / "config" / "teachers.yaml"
        self._manifest = load_yaml_file(self.manifest_path, {}) or load_yaml_file(self.fallback_manifest, {})
        self.path = self._resolve_benchmarks_path()
        self._payload = load_yaml_file(self.path, {})
        self.status_label = self._payload.get("canon_status", "LOCKED CANON")
        self.schema_version = int(self._payload.get("schema_version", 1))
        self.default_threshold_set_id = self._payload.get("default_threshold_set_id", "teacher-v2026-r1")
        self.thresholds = TeacherThresholdRegistry(config_dir)

    def metadata(self) -> dict[str, Any]:
        return {
            "status_label": self.status_label,
            "schema_version": self.schema_version,
            "path": str(self.path),
            "default_threshold_set_id": self.default_threshold_set_id,
            "subjects": sorted(self._payload.get("subjects", {}).keys()),
        }

    def subject_catalog(self, subject: str) -> dict[str, Any]:
        return dict(self._payload.get("subjects", {}).get(subject, {}))

    def families_for_subject(self, subject: str) -> list[dict[str, Any]]:
        catalog = self.subject_catalog(subject)
        return list(catalog.get("families", []))

    def family(self, subject: str, benchmark_family: str) -> dict[str, Any]:
        catalog = self.subject_catalog(subject)
        for payload in catalog.get("families", []):
            if payload.get("name") == benchmark_family:
                merged = dict(payload)
                merged["subject"] = subject
                merged["default_dimensions"] = dict(catalog.get("default_dimensions", {}))
                merged["canon_status"] = catalog.get("canon_status", self.status_label)
                merged["regimen_ref"] = catalog.get("regimen_ref")
                merged["auxiliary"] = bool(catalog.get("auxiliary", False))
                merged["threshold_set_id"] = catalog.get("threshold_set_id", self.default_threshold_set_id)
                return merged
        raise KeyError(f"Unknown benchmark family '{benchmark_family}' for subject '{subject}'")

    def default_family(self, subject: str) -> str | None:
        families = self.families_for_subject(subject)
        return families[0]["name"] if families else None

    def subject_for_family(self, benchmark_family: str) -> str | None:
        for subject, catalog in self._payload.get("subjects", {}).items():
            for payload in catalog.get("families", []):
                if payload.get("name") == benchmark_family:
                    return subject
        return None

    def resolve_threshold_spec(self, subject: str, benchmark_family: str, threshold_set_id: str | None = None):
        family = self.family(subject, benchmark_family)
        return self.thresholds.resolve(
            subject=subject,
            benchmark_family=benchmark_family,
            threshold_set_id=threshold_set_id or family.get("threshold_set_id"),
        )

    def _resolve_benchmarks_path(self) -> Path:
        refs = self._manifest.get("registry_files", {})
        ref = refs.get("benchmarks", "nexusnet/teachers/teacher_benchmark_families.yaml")
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
