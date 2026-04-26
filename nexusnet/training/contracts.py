from __future__ import annotations

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
