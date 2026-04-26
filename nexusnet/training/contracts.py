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
        self.export_dir = self.artifacts_dir / "training" / "exports"

    def export_dataset(self, *, name: str, records: list[TrainingDataExportRecord]) -> dict[str, Any]:
        safe_name = self._safe_name(name)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = self.export_dir / f"{safe_name}.jsonl"
        manifest_path = self.export_dir / f"{safe_name}.manifest.json"
        payloads = [record.export_payload() for record in records]
        artifact_path.write_text(
            "".join(json.dumps(payload, sort_keys=True) + "\n" for payload in payloads),
            encoding="utf-8",
        )
        checkpoint_ready = bool(records) and all(record.ready_for_checkpoint() for record in records)
        manifest = {
            "artifact_type": "dataset_manifest",
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

    def export_reward_spec(
        self,
        *,
        name: str,
        objectives: list[str],
        metrics: dict[str, Any],
        safety_constraints: list[str],
        provenance: list[dict[str, Any]],
    ) -> dict[str, Any]:
        safe_name = self._safe_name(name)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = self.export_dir / f"{safe_name}.reward.json"
        payload = {
            "artifact_type": "reward_spec",
            "name": name,
            "status": "draft_reward_spec",
            "objectives": list(objectives),
            "metrics": dict(metrics),
            "safety_constraints": list(safety_constraints),
            "provenance": list(provenance),
            "checkpoint_promotion_ready": False,
            "promotion_gate": "eval_reports_license_security_and_policy_required",
            "artifact_path": str(artifact_path),
        }
        artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return payload

    def export_eval_report(
        self,
        *,
        name: str,
        dataset_artifact_path: str,
        reward_spec_path: str | None,
        scenario_ids: list[str],
        results: dict[str, Any],
        license_status: str,
        security_gate_status: str,
    ) -> dict[str, Any]:
        safe_name = self._safe_name(name)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = self.export_dir / f"{safe_name}.eval-report.json"
        blocked_by: list[str] = []
        if license_status != "approved":
            blocked_by.append("approved_license_required")
        if security_gate_status != "passed":
            blocked_by.append("security_gate_pass_required")
        if any(results.get(scenario_id) != "passed" for scenario_id in scenario_ids):
            blocked_by.append("all_eval_scenarios_must_pass")

        payload = {
            "artifact_type": "eval_report",
            "name": name,
            "status": "evaluation_report",
            "dataset_artifact_path": dataset_artifact_path,
            "reward_spec_path": reward_spec_path,
            "scenario_ids": list(scenario_ids),
            "results": dict(results),
            "license_status": license_status,
            "security_gate_status": security_gate_status,
            "blocked_by": blocked_by,
            "promotion_recommendation": "promote" if not blocked_by else "hold",
            "checkpoint_promotion_ready": not blocked_by,
            "artifact_path": str(artifact_path),
        }
        artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return payload

    def list_artifacts(self) -> dict[str, Any]:
        self.export_dir.mkdir(parents=True, exist_ok=True)
        artifacts: list[dict[str, Any]] = []
        for path in sorted(self.export_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            artifact_type = payload.get("artifact_type")
            if not artifact_type:
                continue
            artifacts.append(
                {
                    "artifact_type": artifact_type,
                    "name": payload.get("name"),
                    "artifact_path": str(path),
                    "checkpoint_promotion_ready": bool(payload.get("checkpoint_promotion_ready")),
                    "promotion_recommendation": payload.get("promotion_recommendation"),
                }
            )
        return {"artifact_count": len(artifacts), "artifacts": artifacts}

    def _safe_name(self, name: str) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]+", "-", name).strip("-") or "training-dataset"
