from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .schema_versions import TeacherSchemaRegistry


class TeacherSchemaMigrationHelper:
    def __init__(self, *, config_dir: Path, state_dir: Path):
        self.schema_registry = TeacherSchemaRegistry(config_dir)
        self.state_dir = state_dir

    def ensure_manifest(self) -> dict[str, Any]:
        manifest = {
            "status_label": "LOCKED CANON",
            "generated_at": datetime.now(UTC).isoformat(),
            "manifest_schema_version": 1,
            "schema_registry": self.schema_registry.metadata(),
            "managed_tables": [
                "teacher_scorecards",
                "teacher_disagreement_artifacts",
                "teacher_evidence_bundles",
                "takeover_scorecards",
                "retirement_shadow_log",
                "teacher_trend_scorecards",
                "takeover_trend_reports",
                "teacher_benchmark_fleet_summaries",
                "teacher_cohort_scorecards",
                "replacement_readiness_reports",
            ],
            "migration_policy": "manifest-backed additive-json compatibility; startup auto-create remains enabled",
        }
        path = self.state_dir / "teacher-schema-manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        manifest["path"] = str(path)
        return manifest
