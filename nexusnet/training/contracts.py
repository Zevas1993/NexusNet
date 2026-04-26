from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class TrainingDataExportRecord(BaseModel):
    """Trace-first training export row. It is data, not a promoted checkpoint."""

    trace_id: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    output: str = Field(min_length=1)
    provenance: list[dict[str, Any]] = Field(min_length=1)
    teacher_source: dict[str, Any] = Field(default_factory=dict)
    capsule_source: dict[str, Any] = Field(default_factory=dict)
    safety_labels: list[str] = Field(min_length=1)
    eval_target: str = Field(min_length=1)
    license_metadata: dict[str, Any] = Field(default_factory=dict)
    eval_report_id: str | None = None
    security_gate_status: str = "not_run"

    def ready_for_checkpoint(self) -> bool:
        return (
            bool(self.eval_report_id)
            and self.security_gate_status == "passed"
            and self.license_metadata.get("status") == "approved"
            and bool(self.provenance)
            and bool(self.safety_labels)
        )

    def export_payload(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "prompt": self.prompt,
            "output": self.output,
            "provenance": list(self.provenance),
            "teacher_source": dict(self.teacher_source),
            "capsule_source": dict(self.capsule_source),
            "safety_labels": list(self.safety_labels),
            "eval_target": self.eval_target,
            "license_metadata": dict(self.license_metadata),
            "checkpoint_promotion_ready": self.ready_for_checkpoint(),
        }


class TrainingDatasetExporter:
    """Writes trace-first training datasets as artifacts before any checkpoint promotion."""

    def __init__(self, artifacts_dir: Path | str):
        self.artifacts_dir = Path(artifacts_dir)

    def export_dataset(self, *, name: str, records: list[TrainingDataExportRecord]) -> dict[str, Any]:
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", name).strip("-") or "training-dataset"
        export_dir = self.artifacts_dir / "training" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = export_dir / f"{safe_name}.jsonl"
        manifest_path = export_dir / f"{safe_name}.manifest.json"
        payloads = [record.export_payload() for record in records]
        artifact_path.write_text(
            "".join(json.dumps(payload, sort_keys=True) + "\n" for payload in payloads),
            encoding="utf-8",
        )
        checkpoint_ready = bool(records) and all(record.ready_for_checkpoint() for record in records)
        manifest = {
            "name": name,
            "artifact_path": str(artifact_path),
            "sample_count": len(records),
            "checkpoint_promotion_ready": checkpoint_ready,
            "promotion_gate": "canon_traces_evals_memory_provenance_licenses_security",
            "records": [
                {
                    "trace_id": record.trace_id,
                    "eval_target": record.eval_target,
                    "license_status": record.license_metadata.get("status"),
                    "security_gate_status": record.security_gate_status,
                    "checkpoint_promotion_ready": record.ready_for_checkpoint(),
                }
                for record in records
            ],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        return {
            **manifest,
            "manifest_path": str(manifest_path),
            "real_training_status": "gated",
        }
