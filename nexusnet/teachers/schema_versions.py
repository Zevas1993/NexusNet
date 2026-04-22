from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file


@dataclass(frozen=True)
class TeacherSchemaSpec:
    schema_family: str
    version: int
    min_reader_version: int
    current_writer_version: int
    migration_policy: str
    compatible_readers: list[int]
    canon_status: str
    notes: list[str]


class TeacherSchemaRegistry:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.project_root = config_dir.parents[1]
        self.repo_root = Path(__file__).resolve().parents[2]
        self.package_dir = Path(__file__).resolve().parent
        self.path = self._resolve_path()
        self._payload = load_yaml_file(self.path, {})
        self.status_label = self._payload.get("canon_status", "LOCKED CANON")
        self.schema_version = int(self._payload.get("schema_version", 1))
        self.migration_notes = list(self._payload.get("migration_notes", []))

    def metadata(self) -> dict[str, Any]:
        return {
            "status_label": self.status_label,
            "schema_version": self.schema_version,
            "path": str(self.path),
            "families": {
                family: {
                    "version": spec.version,
                    "min_reader_version": spec.min_reader_version,
                    "current_writer_version": spec.current_writer_version,
                    "migration_policy": spec.migration_policy,
                    "compatible_readers": spec.compatible_readers,
                }
                for family, spec in ((family, self.spec(family)) for family in sorted(self._payload.get("families", {}).keys()))
            },
            "migration_notes": self.migration_notes,
        }

    def spec(self, schema_family: str) -> TeacherSchemaSpec:
        payload = (self._payload.get("families", {}) or {}).get(schema_family)
        if payload is None:
            raise KeyError(f"Unknown teacher schema family: {schema_family}")
        return TeacherSchemaSpec(
            schema_family=schema_family,
            version=int(payload.get("version", 1)),
            min_reader_version=int(payload.get("min_reader_version", 1)),
            current_writer_version=int(payload.get("current_writer_version", payload.get("version", 1))),
            migration_policy=str(payload.get("migration_policy", "additive-json")),
            compatible_readers=[int(item) for item in payload.get("compatible_readers", [1])],
            canon_status=str(payload.get("canon_status", self.status_label)),
            notes=list(payload.get("notes", [])),
        )

    def envelope(self, schema_family: str) -> dict[str, Any]:
        spec = self.spec(schema_family)
        return {
            "schema_family": spec.schema_family,
            "schema_version": spec.version,
            "schema_compatibility": {
                "min_reader_version": spec.min_reader_version,
                "current_writer_version": spec.current_writer_version,
                "migration_policy": spec.migration_policy,
                "compatible_readers": spec.compatible_readers,
                "manifest_path": str(self.path),
            },
        }

    def _resolve_path(self) -> Path:
        candidate = self.config_dir / "schema_versions.yaml"
        if candidate.exists():
            return candidate
        fallback = self.repo_root / "runtime" / "config" / "schema_versions.yaml"
        if fallback.exists():
            return fallback
        return candidate
