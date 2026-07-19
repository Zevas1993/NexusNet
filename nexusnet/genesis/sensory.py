from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .event_spine import GenesisEventSpineService


GENESIS_SENSORY_PROVENANCE_SCHEMA = "nexusnet-genesis-sensory-provenance-v1"
GENESIS_SENSORY_PROVENANCE_SURFACE_ID = "genesis-sensory-provenance-privacy-gate"
GENESIS_SENSORY_EVENT_SCHEMA = "nexusnet-genesis-sensory-event-v1"
GENESIS_SENSORY_EVENT_SURFACE_ID = "genesis-sensory-event"
GENESIS_SENSORY_REF = "genesis/sensory/sensory_events.jsonl"

_UNSAFE_REF_MARKERS = (
    "raw-prompt",
    "raw-output",
    "secret",
    "token",
    "password",
    "api-key",
    "apikey",
    ":\\",
    "runtime/test-fixtures",
)


class GenesisSensoryProvenanceService:
    """Layer 6 sensory source, provenance, and privacy gate for real brain use."""

    def __init__(
        self,
        *,
        artifacts_dir: Path | str,
        project_root: Path | str,
        event_spine: GenesisEventSpineService | None = None,
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.project_root = Path(project_root)
        self.event_spine = event_spine or GenesisEventSpineService(
            artifacts_dir=self.artifacts_dir,
            project_root=self.project_root,
        )
        self.sensory_dir = self.artifacts_dir / "genesis" / "sensory"
        self.events_path = self.sensory_dir / "sensory_events.jsonl"

    def record_from_hive_result(
        self,
        *,
        session_id: str | None,
        hive_result: dict[str, Any],
        heartbeat_record: dict[str, Any] | None = None,
        evidence_record: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = self._record(
            session_id=session_id,
            hive_result=hive_result,
            heartbeat_record=heartbeat_record or {},
            evidence_record=evidence_record or {},
        )
        self.sensory_dir.mkdir(parents=True, exist_ok=True)
        existing = {item.get("event_id") for item in self._read_records()}
        if record["event_id"] not in existing:
            with self.events_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    def summary(self, session_id: str | None = None) -> dict[str, Any]:
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        all_records = [self._record_with_shared_event(record) for record in self._read_records() if _is_valid_record(record)]
        scoped_records = [
            _replayed(record)
            for record in all_records
            if not session_ref_digest
            or str(record.get("source_identity", {}).get("source_ref_digest") or "") == session_ref_digest
        ]
        scoped_records = list(reversed(scoped_records))
        latest = scoped_records[0] if scoped_records else None
        status = "live-control-plane" if latest else "not-observed"
        shared_summary = self.event_spine.summary(session_ref_digest=session_ref_digest)
        return {
            "schema_version": GENESIS_SENSORY_PROVENANCE_SCHEMA,
            "surface_id": GENESIS_SENSORY_PROVENANCE_SURFACE_ID,
            "status": status,
            "honest_status_label": (
                "genesis-layer6-sensory-provenance-privacy-gate-live-control-plane"
                if latest
                else "genesis-layer6-sensory-provenance-privacy-gate-not-observed"
            ),
            "authority": "NexusBrain",
            "source": "nexusbrain-generate" if latest else None,
            "session_ref_digest": session_ref_digest,
            "sensory_event_count": len(scoped_records),
            "global_sensory_event_count": len(all_records),
            "latest_event_id": latest.get("event_id") if latest else None,
            "latest_heartbeat_record_id": latest.get("heartbeat_record_id") if latest else None,
            "latest_source_hive_run_id": latest.get("source_hive_run_id") if latest else None,
            "latest_operation_receipt_id": latest.get("operation_receipt_id") if latest else None,
            "latest_evidence_checkpoint_id": latest.get("evidence_checkpoint_id") if latest else None,
            "latest_source_brain_generate_status": latest.get("source_brain_generate_status") if latest else None,
            "latest_privacy_class": (latest.get("privacy_gate") or {}).get("privacy_class") if latest else None,
            "latest_redaction_status": (latest.get("privacy_gate") or {}).get("redaction_status") if latest else None,
            "events": scoped_records[:20],
            "shared_event_spine": {
                "schema_version": "nexusnet-genesis-sensory-shared-event-spine-v1",
                "surface_id": "genesis-sensory-shared-event-spine",
                "status": shared_summary.get("status"),
                "latest_event_ref": (
                    latest.get("shared_event_spine", {}).get("event_ref")
                    if latest and isinstance(latest.get("shared_event_spine"), dict)
                    else None
                ),
                "event_count": shared_summary.get("event_type_counts", {}).get("genesis.sensory.provenance", 0),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            },
            "artifact_ref": GENESIS_SENSORY_REF,
            "evidence_refs": _sanitize_refs(
                [
                    GENESIS_SENSORY_REF,
                    latest.get("event_id") if latest else None,
                    latest.get("heartbeat_record_id") if latest else None,
                    latest.get("source_hive_run_ref") if latest else None,
                    latest.get("operation_receipt_id") if latest else None,
                    latest.get("operation_content_ref") if latest else None,
                    latest.get("evidence_checkpoint_id") if latest else None,
                    latest.get("shared_event_spine", {}).get("event_ref")
                    if latest and isinstance(latest.get("shared_event_spine"), dict)
                    else None,
                    *(((latest.get("neural_bus_projection") or {}).get("evidence_refs") or []) if latest else []),
                ]
            )[:48],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-layer6-source-provenance-privacy-gate-ids-digests-statuses-and-artifact-refs-only-"
                "no-prompts-outputs-session-ids-or-local-paths"
            ),
            "mutation_boundary": "append-only-sensory-provenance-events-no-memory-training-or-production-mutation",
        }

    def _record(
        self,
        *,
        session_id: str | None,
        hive_result: dict[str, Any],
        heartbeat_record: dict[str, Any],
        evidence_record: dict[str, Any],
    ) -> dict[str, Any]:
        source_run_id = str(hive_result.get("run_id") or "")
        heartbeat_record_id = str(heartbeat_record.get("record_id") or "")
        operation_receipt_id = str(evidence_record.get("operation_receipt_id") or "")
        operation_content_ref = str(evidence_record.get("operation_content_ref") or "")
        evidence_checkpoint_id = str(evidence_record.get("checkpoint_id") or "")
        source_metadata = hive_result.get("metadata") if isinstance(hive_result.get("metadata"), dict) else {}
        source_brain_generate_status = str(source_metadata.get("brain_generate_status") or "unknown")
        source_critique_status = str(source_metadata.get("critique_status") or "unknown")
        failure_observation_only = source_brain_generate_status in {
            "blocked",
            "error",
            "failed",
            "runtime-unavailable",
        }
        recorded_at = str(hive_result.get("created_at") or _utcnow())
        source_ref_digest = _privacy_digest(session_id) if session_id else None
        event_seed = json.dumps(
            {
                "source_run_id": source_run_id,
                "heartbeat_record_id": heartbeat_record_id,
                "operation_receipt_id": operation_receipt_id,
                "evidence_checkpoint_id": evidence_checkpoint_id,
                "source_brain_generate_status": source_brain_generate_status,
                "session_ref_digest": source_ref_digest,
                "recorded_at": recorded_at,
            },
            sort_keys=True,
        )
        event_id = f"genesis-sensory-event::{_digest(event_seed)}"
        projection = _neural_bus_projection(
            event_id=event_id,
            source_run_id=source_run_id,
            heartbeat_record_id=heartbeat_record_id,
        )
        shared_event_spine = self._publish_shared_event(
            event_id=event_id,
            source_run_id=source_run_id,
            heartbeat_record_id=heartbeat_record_id,
            operation_receipt_id=operation_receipt_id,
            operation_content_ref=operation_content_ref,
            evidence_checkpoint_id=evidence_checkpoint_id,
            session_ref_digest=source_ref_digest,
            recorded_at=recorded_at,
        )
        return {
            "schema_version": GENESIS_SENSORY_EVENT_SCHEMA,
            "surface_id": GENESIS_SENSORY_EVENT_SURFACE_ID,
            "event_id": event_id,
            "status": "sensory-provenance-gated",
            "honest_status_label": "real-nexusbrain-generate-sensory-input-gated-before-memory-or-training",
            "source": "nexusbrain-generate",
            "source_hive_run_id": source_run_id or None,
            "source_hive_run_ref": f"hive-forward::{source_run_id}" if source_run_id else None,
            "heartbeat_record_id": heartbeat_record_id or None,
            "operation_receipt_id": operation_receipt_id or None,
            "operation_content_ref": operation_content_ref or None,
            "evidence_checkpoint_id": evidence_checkpoint_id or None,
            "source_brain_generate_status": source_brain_generate_status,
            "source_critique_status": source_critique_status,
            "recorded_at": recorded_at,
            "source_identity": {
                "surface_id": "genesis-sensory-source-identity",
                "source_kind": "end-user-wrapper-model-interaction",
                "source_ref_digest": source_ref_digest,
                "source_authority": "NexusBrain",
                "source_observation": "real-brain-forward-pass-metadata",
                "raw_content_included": False,
            },
            "source_kind": "end-user-wrapper-model-interaction",
            "trust_tier": "local-runtime-observed",
            "privacy_gate": {
                "schema_version": "nexusnet-genesis-sensory-privacy-gate-v1",
                "surface_id": "genesis-sensory-privacy-gate",
                "privacy_class": "operator-private",
                "redaction_status": "metadata-only-redacted",
                "consent_status": "runtime-use-only",
                "source_outcome_status": source_brain_generate_status,
                "failure_observation_only": failure_observation_only,
                "rights_license_status": "not-approved-for-training",
                "source_quarantine_status": "quarantined-for-memory-training-and-egress",
                "quarantine_decision": {
                    "surface_id": "genesis-sensory-quarantine-decision",
                    "memory_write_allowed": False,
                    "training_allowed": False,
                    "protocol_egress_allowed": False,
                    "requires_operator_review": True,
                    "raw_content_included": False,
                },
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            },
            "provenance_refs": _sanitize_refs(
                [
                    f"hive-forward::{source_run_id}" if source_run_id else None,
                    heartbeat_record_id,
                    operation_receipt_id,
                    operation_content_ref,
                    evidence_checkpoint_id,
                    (hive_result.get("project_heartbeat") or {}).get("heartbeat_id")
                    if isinstance(hive_result.get("project_heartbeat"), dict)
                    else None,
                ]
            ),
            "neural_bus_projection": projection,
            "shared_event_spine": shared_event_spine,
            "replay_status": "recorded",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-sensory-source-provenance-privacy-gate-only-no-user-prompt-output-session-id-or-path"
            ),
            "mutation_boundary": "sensory-event-record-only-memory-training-egress-and-production-mutation-denied",
        }

    def _record_with_shared_event(self, record: dict[str, Any]) -> dict[str, Any]:
        if isinstance(record.get("shared_event_spine"), dict):
            return record
        hydrated = dict(record)
        source_identity = (
            record.get("source_identity")
            if isinstance(record.get("source_identity"), dict)
            else {}
        )
        hydrated["shared_event_spine"] = self._publish_shared_event(
            event_id=str(record.get("event_id") or ""),
            source_run_id=str(record.get("source_hive_run_id") or ""),
            heartbeat_record_id=str(record.get("heartbeat_record_id") or ""),
            operation_receipt_id=str(record.get("operation_receipt_id") or ""),
            operation_content_ref=str(record.get("operation_content_ref") or ""),
            evidence_checkpoint_id=str(record.get("evidence_checkpoint_id") or ""),
            session_ref_digest=source_identity.get("source_ref_digest"),
            recorded_at=str(record.get("recorded_at") or ""),
        )
        evidence_refs = list(record.get("evidence_refs") or [])
        evidence_refs.extend(hydrated["shared_event_spine"].get("evidence_refs", []))
        hydrated["evidence_refs"] = _sanitize_refs(evidence_refs)[:48]
        return hydrated

    def _publish_shared_event(
        self,
        *,
        event_id: str,
        source_run_id: str,
        heartbeat_record_id: str,
        operation_receipt_id: str,
        operation_content_ref: str,
        evidence_checkpoint_id: str,
        session_ref_digest: str | None,
        recorded_at: str,
    ) -> dict[str, Any]:
        return self.event_spine.publish_event(
            event_type="genesis.sensory.provenance",
            source_surface_id=GENESIS_SENSORY_EVENT_SURFACE_ID,
            correlation_ref=event_id,
            session_ref_digest=session_ref_digest,
            source_hive_run_ref=f"hive-forward::{source_run_id}" if source_run_id else None,
            heartbeat_record_id=heartbeat_record_id,
            privacy_label="sanitized-sensory-provenance",
            artifact_refs=[
                GENESIS_SENSORY_REF,
                event_id,
                heartbeat_record_id,
                operation_receipt_id,
                operation_content_ref,
                evidence_checkpoint_id,
            ],
            planes=["sensory", "provenance", "privacy", "neural_bus"],
            priority_trails=[
                {"topic": "genesis-sensory-provenance", "strength": 1.0, "artifact_ref": event_id}
            ],
            created_at=recorded_at or None,
        )

    def _read_records(self) -> list[dict[str, Any]]:
        if not self.events_path.is_file():
            return []
        records: list[dict[str, Any]] = []
        for line in self.events_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
        return records


def _neural_bus_projection(*, event_id: str, source_run_id: str, heartbeat_record_id: str) -> dict[str, Any]:
    event_digest = _digest("|".join([event_id, source_run_id, heartbeat_record_id]))
    event_ref = f"neural-bus-event::{event_digest}"
    blackboard_ref = f"hive-blackboard::{event_digest}"
    plane_trace_ref = f"plane-trace::{event_digest}"
    return {
        "schema_version": "nexusnet-genesis-sensory-neural-bus-projection-v1",
        "surface_id": "genesis-sensory-neural-bus-projection",
        "typed_event_envelope": {
            "schema_version": "nexusnet-neural-bus-event-envelope-v1",
            "event_ref": event_ref,
            "event_type": "genesis.sensory.provenance",
            "activation_ref": f"activation::{event_digest}",
            "correlation_ref": event_id,
            "source_hive_run_ref": f"hive-forward::{source_run_id}" if source_run_id else None,
            "event_privacy_label": "sanitized-sensory-provenance",
            "artifact_bound": True,
            "raw_content_included": False,
        },
        "hive_blackboard_snapshot": {
            "schema_version": "nexusnet-hive-blackboard-snapshot-v1",
            "snapshot_ref": blackboard_ref,
            "state": "sensory-provenance-gated",
            "priority_trails": [
                {
                    "topic": "genesis-sensory-provenance",
                    "strength": 1.0,
                    "artifact_ref": event_id,
                }
            ],
            "raw_content_included": False,
        },
        "plane_trace": {
            "schema_version": "nexusnet-plane-trace-ledger-v1",
            "trace_ref": plane_trace_ref,
            "planes": ["sensory", "provenance", "privacy", "neural_bus"],
            "artifact_bound_downstream_consumption_required": True,
            "raw_content_included": False,
        },
        "evidence_refs": _sanitize_refs([event_ref, blackboard_ref, plane_trace_ref, heartbeat_record_id]),
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def _is_valid_record(record: dict[str, Any]) -> bool:
    return (
        isinstance(record, dict)
        and record.get("schema_version") == GENESIS_SENSORY_EVENT_SCHEMA
        and record.get("surface_id") == GENESIS_SENSORY_EVENT_SURFACE_ID
        and bool(record.get("event_id"))
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
    )


def _replayed(record: dict[str, Any]) -> dict[str, Any]:
    copy = dict(record)
    copy["replay_status"] = "replayed"
    return copy


def _sanitize_refs(value: Any) -> list[str]:
    if isinstance(value, str):
        candidates = [value]
    elif isinstance(value, list):
        candidates = value
    else:
        candidates = []
    return _dedupe(
        [
            str(candidate)
            for candidate in candidates
            if str(candidate or "").strip() and not _unsafe_ref(str(candidate))
        ]
    )


def _unsafe_ref(value: str) -> bool:
    normalized = value.lower().replace("\\", "/")
    return any(marker in normalized for marker in _UNSAFE_REF_MARKERS)


def _dedupe(values: list[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and not _unsafe_ref(text) and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _privacy_digest(value: str | None) -> str:
    return "sha256:" + hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
