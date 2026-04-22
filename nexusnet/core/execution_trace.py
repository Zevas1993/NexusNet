from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _artifact_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


@dataclass
class CoreExecutionStage:
    sequence: int
    stage: str
    detail: dict[str, Any] = field(default_factory=dict)
    recorded_at: str = field(default_factory=utcnow_iso)

    def as_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "stage": self.stage,
            "detail": self.detail,
            "recorded_at": self.recorded_at,
        }


class CoreExecutionTraceRecorder:
    def __init__(self, *, trace_name: str):
        self.trace_name = trace_name
        self._stages: list[CoreExecutionStage] = []

    def record(self, stage: str, detail: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = CoreExecutionStage(
            sequence=len(self._stages) + 1,
            stage=stage,
            detail=detail or {},
        )
        self._stages.append(entry)
        return entry.as_dict()

    def stage_names(self) -> list[str]:
        return [item.stage for item in self._stages]

    def snapshot(self) -> list[dict[str, Any]]:
        return [item.as_dict() for item in self._stages]


def build_lineage_tags(
    *,
    teacher_registry_layer: str | None = None,
    teacher_id: str | None = None,
    attached_role: str | None = None,
    task_type: str | None = None,
    dream_lineage: str | None = None,
) -> list[str]:
    tags = ["nexusnet", "brain-first"]
    if teacher_registry_layer:
        tags.append(f"teacher-registry:{teacher_registry_layer}")
    if teacher_id:
        tags.append(f"teacher:{teacher_id}")
    if attached_role:
        tags.append(f"role:{attached_role}")
    if task_type:
        tags.append(f"task:{task_type}")
    if dream_lineage:
        tags.append(f"lineage:{dream_lineage}")
    else:
        tags.append("lineage:live-derived")
    return sorted(set(tags))


def persist_core_execution_artifact(
    *,
    store: Any,
    trace_id: str,
    session_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    artifact_id = f"coreexec_{_artifact_slug(trace_id)}"
    envelope = {
        "artifact_id": artifact_id,
        "trace_id": trace_id,
        "session_id": session_id,
        "created_at": utcnow_iso(),
        "summary": {
            "brain_first_execution": payload.get("brain_started_first", False),
            "selected_runtime_name": ((payload.get("qes_execution_plan") or {}).get("selected_runtime_name")),
            "model_id": ((payload.get("model_attachment") or {}).get("model_id")),
            "teacher_id": payload.get("teacher_id"),
            "teacher_registry_layer": payload.get("teacher_registry_layer"),
            "proposed_execution_mode": ((payload.get("execution_policy") or {}).get("proposed_execution_mode")),
            "execution_mode": ((payload.get("execution_policy") or {}).get("execution_mode")),
            "policy_id": ((payload.get("execution_policy") or {}).get("policy_id")),
            "native_execution_id": ((payload.get("native_execution") or {}).get("execution_id")),
            "governed_action": ((payload.get("promotion_linkage") or {}).get("governed_action"))
            or ((payload.get("execution_policy") or {}).get("governed_action")),
            "alignment_hold_required": ((payload.get("promotion_linkage") or {}).get("alignment_hold_required"))
            or (((payload.get("execution_policy") or {}).get("alignment_summary")) or {}).get("alignment_hold_required"),
            "native_execution_verdict": ((((payload.get("native_execution") or {}).get("teacher_comparison")) or {}).get("verdict")),
            "native_candidate_id": ((((payload.get("native_execution") or {}).get("native_candidate")) or {}).get("candidate_id")),
            "native_activation_mode": ((((payload.get("native_execution") or {}).get("native_candidate")) or {}).get("activation_mode")),
            "promotion_action": ((payload.get("promotion_linkage") or {}).get("execution_action")),
            "promotion_decision_id": ((payload.get("promotion_linkage") or {}).get("decision_id")),
        },
        "core_execution": payload,
    }
    artifact_path = store.write_artifact(
        f"core/execution/{artifact_id}.json",
        json.dumps(envelope, indent=2, ensure_ascii=True, default=str),
    )
    return {
        "artifact_id": artifact_id,
        "artifact_path": artifact_path,
    }
