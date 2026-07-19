from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .event_spine import GenesisEventSpineService


GENESIS_HEARTBEAT_CHAIN_SCHEMA = "nexusnet-genesis-heartbeat-chain-v1"
GENESIS_HEARTBEAT_CHAIN_SURFACE_ID = "genesis-heartbeat-chain"
GENESIS_HEARTBEAT_RECORD_SCHEMA = "nexusnet-genesis-heartbeat-record-v1"
GENESIS_HEARTBEAT_RECORD_SURFACE_ID = "genesis-heartbeat-record"
GENESIS_HEARTBEAT_REF = "genesis/heartbeat/heartbeat_chain.jsonl"
GENESIS_HEARTBEAT_NEURAL_BUS_REF = "genesis/heartbeat/neural_bus_events.jsonl"
GENESIS_HEARTBEAT_BLACKBOARD_REF = "genesis/heartbeat/hive_blackboard_snapshots.jsonl"
GENESIS_HEARTBEAT_PLANE_TRACE_REF = "genesis/heartbeat/plane_traces.jsonl"

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


class GenesisHeartbeatService:
    """Append-only sanitized heartbeat chain for real NexusBrain runtime use."""

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
        self.heartbeat_dir = self.artifacts_dir / "genesis" / "heartbeat"
        self.chain_path = self.heartbeat_dir / "heartbeat_chain.jsonl"
        self.event_ledger_path = self.heartbeat_dir / "neural_bus_events.jsonl"
        self.blackboard_path = self.heartbeat_dir / "hive_blackboard_snapshots.jsonl"
        self.plane_trace_path = self.heartbeat_dir / "plane_traces.jsonl"

    def record_from_hive_result(self, *, session_id: str | None, hive_result: dict[str, Any]) -> dict[str, Any]:
        record = self._record(session_id=session_id, hive_result=hive_result)
        self.heartbeat_dir.mkdir(parents=True, exist_ok=True)
        existing = {item.get("record_id") for item in self._read_records()}
        if record["record_id"] not in existing:
            with self.chain_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
        self._ensure_projection_records(record)
        return record

    def summary(self, session_id: str | None = None) -> dict[str, Any]:
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        all_records = [self._record_with_projection(record) for record in self._read_records() if _is_valid_record(record)]
        for record in all_records:
            self._ensure_projection_records(record)
        scoped_records = [
            record
            for record in all_records
            if not session_ref_digest
            or str(record.get("per_user_global_learning_state", {}).get("session_ref_digest") or "")
            == session_ref_digest
        ]
        scoped_records = list(reversed(scoped_records))
        latest = scoped_records[0] if scoped_records else None
        status = "alive" if latest else "not-observed"
        scoped_record_ids = {str(record.get("record_id") or "") for record in scoped_records}
        all_events = [event for event in self._read_jsonl(self.event_ledger_path) if _is_valid_event(event)]
        all_blackboards = [snapshot for snapshot in self._read_jsonl(self.blackboard_path) if _is_valid_blackboard(snapshot)]
        all_traces = [trace for trace in self._read_jsonl(self.plane_trace_path) if _is_valid_plane_trace(trace)]
        scoped_events = _filter_projection_records(all_events, scoped_record_ids)
        scoped_blackboards = _filter_projection_records(all_blackboards, scoped_record_ids)
        scoped_traces = _filter_projection_records(all_traces, scoped_record_ids)
        latest_event = _latest_projection_for_record(scoped_events, latest)
        latest_blackboard = _latest_projection_for_record(scoped_blackboards, latest)
        latest_trace = _latest_projection_for_record(scoped_traces, latest)
        shared_summary = self.event_spine.summary(session_ref_digest=session_ref_digest)
        return {
            "schema_version": GENESIS_HEARTBEAT_CHAIN_SCHEMA,
            "surface_id": GENESIS_HEARTBEAT_CHAIN_SURFACE_ID,
            "status": status,
            "honest_status_label": (
                "genesis-heartbeat-chain-replayed-from-real-brain-use"
                if latest
                else "genesis-heartbeat-chain-not-observed"
            ),
            "runtime_state": "replayed-heartbeat-chain" if latest else "not-run",
            "source": "nexusbrain-generate" if latest else None,
            "session_ref_digest": session_ref_digest,
            "heartbeat_count": len(scoped_records),
            "global_heartbeat_count": len(all_records),
            "latest_record_id": latest.get("record_id") if latest else None,
            "latest_heartbeat_id": latest.get("project_heartbeat_id") if latest else None,
            "latest_source_hive_run_id": latest.get("source_hive_run_id") if latest else None,
            "latest_runtime_growth_receipt_id": latest.get("runtime_growth_receipt_id") if latest else None,
            "latest_federated_packet_id": latest.get("federated_packet_id") if latest else None,
            "records": scoped_records[:20],
            "neural_bus_event_ledger": self._event_ledger_summary(
                scoped_events=scoped_events,
                all_events=all_events,
                latest_event=latest_event,
            ),
            "hive_blackboard_projection": self._blackboard_ledger_summary(
                scoped_blackboards=scoped_blackboards,
                all_blackboards=all_blackboards,
                latest_blackboard=latest_blackboard,
            ),
            "plane_trace_projection": self._plane_trace_ledger_summary(
                scoped_traces=scoped_traces,
                all_traces=all_traces,
                latest_trace=latest_trace,
            ),
            "shared_event_spine": {
                "schema_version": "nexusnet-genesis-heartbeat-shared-event-spine-v1",
                "surface_id": "genesis-heartbeat-shared-event-spine",
                "status": shared_summary.get("status"),
                "latest_event_ref": (
                    latest.get("shared_event_spine", {}).get("event_ref")
                    if isinstance(latest.get("shared_event_spine"), dict)
                    else shared_summary.get("latest_event_ref")
                ) if latest else None,
                "event_count": shared_summary.get("event_type_counts", {}).get("genesis.heartbeat.recorded", 0),
                "global_event_count": shared_summary.get("global_event_count", 0),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            },
            "artifact_ref": GENESIS_HEARTBEAT_REF,
            "evidence_refs": _dedupe(
                [
                    GENESIS_HEARTBEAT_REF,
                    GENESIS_HEARTBEAT_NEURAL_BUS_REF,
                    GENESIS_HEARTBEAT_BLACKBOARD_REF,
                    GENESIS_HEARTBEAT_PLANE_TRACE_REF,
                    latest.get("record_id") if latest else None,
                    latest.get("project_heartbeat_id") if latest else None,
                    latest.get("runtime_growth_receipt_id") if latest else None,
                    latest.get("federated_packet_id") if latest else None,
                    latest_event.get("event_ref") if latest_event else None,
                    latest_blackboard.get("snapshot_ref") if latest_blackboard else None,
                    latest_trace.get("trace_ref") if latest_trace else None,
                    latest.get("shared_event_spine", {}).get("event_ref")
                    if latest and isinstance(latest.get("shared_event_spine"), dict)
                    else None,
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-genesis-heartbeat-chain-record-ids-counts-digests-and-artifact-refs-only-"
                "no-prompts-outputs-session-ids-or-local-paths"
            ),
            "mutation_boundary": "append-only-heartbeat-evidence-no-active-production-mutation",
        }

    def _record(self, *, session_id: str | None, hive_result: dict[str, Any]) -> dict[str, Any]:
        heartbeat = hive_result.get("project_heartbeat") if isinstance(hive_result.get("project_heartbeat"), dict) else {}
        runtime_receipt = (
            hive_result.get("runtime_growth_receipt")
            if isinstance(hive_result.get("runtime_growth_receipt"), dict)
            else {}
        )
        runtime_packet = (
            hive_result.get("runtime_growth_federated_packet")
            if isinstance(hive_result.get("runtime_growth_federated_packet"), dict)
            else {}
        )
        federated_packet = (
            hive_result.get("federated_learning_packet")
            if isinstance(hive_result.get("federated_learning_packet"), dict)
            else {}
        )
        dream_cycle = (
            hive_result.get("executable_dream_cycle_ledger")
            if isinstance(hive_result.get("executable_dream_cycle_ledger"), dict)
            else {}
        )
        checkpoint = hive_result.get("checkpoint") if isinstance(hive_result.get("checkpoint"), dict) else {}
        checkpoint_coverage = (
            hive_result.get("checkpoint_coverage_ledger")
            if isinstance(hive_result.get("checkpoint_coverage_ledger"), dict)
            else {}
        )
        runtime_decision = (
            hive_result.get("runtime_decision_ledger")
            if isinstance(hive_result.get("runtime_decision_ledger"), dict)
            else {}
        )
        backend_execution = (
            hive_result.get("backend_quantization_execution_ledger")
            if isinstance(hive_result.get("backend_quantization_execution_ledger"), dict)
            else {}
        )
        durable_storage = (
            hive_result.get("durable_storage_ledger")
            if isinstance(hive_result.get("durable_storage_ledger"), dict)
            else {}
        )
        activation = hive_result.get("activation") if isinstance(hive_result.get("activation"), dict) else {}
        neural_pathway = (
            hive_result.get("neural_pathway_map")
            if isinstance(hive_result.get("neural_pathway_map"), dict)
            else {}
        )
        synaptic_transmission = (
            hive_result.get("synaptic_transmission_ledger")
            if isinstance(hive_result.get("synaptic_transmission_ledger"), dict)
            else {}
        )
        source_metadata = hive_result.get("metadata") if isinstance(hive_result.get("metadata"), dict) else {}
        source_brain_generate_status = str(source_metadata.get("brain_generate_status") or "unknown").strip().lower()
        if source_brain_generate_status not in {
            "blocked",
            "completed",
            "covered",
            "error",
            "failed",
            "ok",
            "runtime-unavailable",
            "unknown",
            "warning",
        }:
            source_brain_generate_status = "unknown"
        source_critique_status = str(source_metadata.get("critique_status") or "unknown").strip().lower()
        if source_critique_status not in {"error", "not-run", "ok", "unknown", "warning"}:
            source_critique_status = "unknown"
        source_runtime_degraded = source_brain_generate_status in {
            "blocked",
            "error",
            "failed",
            "runtime-unavailable",
        }
        heartbeat_status = str(heartbeat.get("status") or "unknown")
        record_status = "alive" if heartbeat_status == "alive" and not source_runtime_degraded else "degraded"
        source_run_id = str(hive_result.get("run_id") or "")
        heartbeat_id = str(heartbeat.get("heartbeat_id") or "")
        recorded_at = str(hive_result.get("created_at") or _utcnow())
        record_id = f"genesis-heartbeat-record::{_digest('|'.join([source_run_id, heartbeat_id, recorded_at]))}"
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        runtime_growth_receipt_id = _value(runtime_receipt, "receipt_id")
        runtime_packet_id = _value(runtime_packet, "packet_id")
        federated_packet_id = runtime_packet_id or _value(federated_packet, "packet_id")
        lanes = _compact_lanes(heartbeat.get("lanes"))
        neural_bus_projection = _neural_bus_projection(
            record_id=record_id,
            source_run_id=source_run_id,
            heartbeat_id=heartbeat_id,
            runtime_growth_receipt_id=runtime_growth_receipt_id,
            federated_packet_id=federated_packet_id,
            recorded_at=recorded_at,
        )
        shared_event_spine = self._publish_shared_event(
            record_id=record_id,
            source_run_id=source_run_id,
            heartbeat_id=heartbeat_id,
            session_ref_digest=session_ref_digest,
            runtime_growth_receipt_id=runtime_growth_receipt_id,
            federated_packet_id=federated_packet_id,
            recorded_at=recorded_at,
        )
        return {
            "schema_version": GENESIS_HEARTBEAT_RECORD_SCHEMA,
            "surface_id": GENESIS_HEARTBEAT_RECORD_SURFACE_ID,
            "record_id": record_id,
            "status": record_status,
            "honest_status_label": (
                "real-nexusbrain-generate-heartbeat-recorded"
                if record_status == "alive"
                else "real-nexusbrain-generate-heartbeat-degraded"
            ),
            "source": "nexusbrain-generate",
            "source_hive_run_id": source_run_id or None,
            "source_hive_run_ref": f"hive-forward::{source_run_id}" if source_run_id else None,
            "source_brain_generate_status": source_brain_generate_status,
            "source_critique_status": source_critique_status,
            "hive_activation_id": _value(activation, "activation_id"),
            "neural_pathway_id": _value(neural_pathway, "pathway_id"),
            "synaptic_transmission_id": _value(synaptic_transmission, "transmission_id"),
            "recorded_at": recorded_at,
            "project_heartbeat_id": heartbeat_id or None,
            "project_heartbeat_status": heartbeat_status,
            "runtime_state": str(heartbeat.get("runtime_state") or "live-bound"),
            "runtime_growth_receipt_id": runtime_growth_receipt_id,
            "runtime_growth_packet_id": runtime_packet_id,
            "federated_packet_id": federated_packet_id,
            "dream_cycle_id": _value(dream_cycle, "dream_cycle_id"),
            "checkpoint_id": _value(checkpoint, "checkpoint_id"),
            "checkpoint_coverage_id": _value(checkpoint_coverage, "coverage_ledger_id"),
            "runtime_decision_id": _value(runtime_decision, "runtime_decision_id"),
            "backend_execution_id": _value(backend_execution, "backend_execution_id"),
            "durable_storage_id": _value(durable_storage, "storage_ledger_id"),
            "lane_count": int(heartbeat.get("lane_count") or len(lanes)),
            "alive_lane_count": int(heartbeat.get("alive_lane_count") or 0),
            "degraded_lane_count": int(heartbeat.get("degraded_lane_count") or 0),
            "degraded_lane_ids": _dedupe([str(lane_id) for lane_id in (heartbeat.get("degraded_lane_ids") or [])])[:24],
            "lanes": lanes[:24],
            "per_user_global_learning_state": {
                "surface_id": "genesis-heartbeat-per-user-global-learning-state",
                "session_ref_digest": session_ref_digest,
                "runtime_growth_captured": bool(runtime_growth_receipt_id),
                "global_federated_packet_captured": bool(federated_packet_id),
                "runtime_growth_receipt_id": runtime_growth_receipt_id,
                "federated_packet_id": federated_packet_id,
                "raw_content_included": False,
                "active_personal_data_training_allowed": False,
                "active_production_mutation_allowed": False,
            },
            "admin_update_governance": {
                "surface_id": "genesis-heartbeat-admin-update-governance",
                "status": "proposal-eligible-governed",
                "admin_approval_required": True,
                "sandbox_eval_required": True,
                "rollback_required": True,
                "safe_apply_allowed": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
                "evidence_refs": _dedupe(
                    [
                        runtime_growth_receipt_id,
                        federated_packet_id,
                        _value(checkpoint, "checkpoint_id"),
                        _value(checkpoint_coverage, "coverage_ledger_id"),
                    ]
                ),
                "raw_content_included": False,
            },
            "neural_bus_projection": neural_bus_projection,
            "shared_event_spine": shared_event_spine,
            "evidence_refs": _sanitize_refs(
                [
                    GENESIS_HEARTBEAT_REF,
                    *neural_bus_projection.get("evidence_refs", []),
                    *shared_event_spine.get("evidence_refs", []),
                    f"hive-forward::{source_run_id}" if source_run_id else None,
                    _value(activation, "activation_id"),
                    _value(neural_pathway, "pathway_id"),
                    _value(synaptic_transmission, "transmission_id"),
                    heartbeat_id,
                    runtime_growth_receipt_id,
                    federated_packet_id,
                    _value(dream_cycle, "dream_cycle_id"),
                    _value(checkpoint, "checkpoint_id"),
                    _value(checkpoint_coverage, "coverage_ledger_id"),
                    _value(runtime_decision, "runtime_decision_id"),
                    _value(backend_execution, "backend_execution_id"),
                    _value(durable_storage, "storage_ledger_id"),
                ]
            )[:48],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-genesis-heartbeat-record-ids-counts-digests-and-artifact-refs-only-"
                "no-prompts-outputs-session-ids-or-local-paths"
            ),
            "mutation_boundary": "append-only-heartbeat-record-no-active-production-mutation",
        }

    def _publish_shared_event(
        self,
        *,
        record_id: str,
        source_run_id: str,
        heartbeat_id: str,
        session_ref_digest: str | None,
        runtime_growth_receipt_id: str | None,
        federated_packet_id: str | None,
        recorded_at: str,
    ) -> dict[str, Any]:
        return self.event_spine.publish_event(
            event_type="genesis.heartbeat.recorded",
            source_surface_id=GENESIS_HEARTBEAT_RECORD_SURFACE_ID,
            correlation_ref=record_id,
            session_ref_digest=session_ref_digest,
            source_hive_run_ref=f"hive-forward::{source_run_id}" if source_run_id else None,
            heartbeat_record_id=record_id,
            privacy_label="sanitized-genesis-heartbeat",
            artifact_refs=[
                GENESIS_HEARTBEAT_REF,
                record_id,
                heartbeat_id,
                runtime_growth_receipt_id,
                federated_packet_id,
            ],
            planes=["runtime", "growth", "federation", "memory", "governance"],
            priority_trails=[
                {"topic": "genesis-heartbeat", "strength": 1.0, "artifact_ref": record_id},
                {"topic": "runtime-growth", "strength": 0.8, "artifact_ref": runtime_growth_receipt_id},
                {"topic": "federation", "strength": 0.7, "artifact_ref": federated_packet_id},
            ],
            created_at=recorded_at,
        )

    def _ensure_projection_records(self, record: dict[str, Any]) -> None:
        projection = self._record_with_projection(record).get("neural_bus_projection")
        if not isinstance(projection, dict):
            return
        envelope = projection.get("typed_event_envelope") if isinstance(projection.get("typed_event_envelope"), dict) else {}
        blackboard = (
            projection.get("hive_blackboard_snapshot")
            if isinstance(projection.get("hive_blackboard_snapshot"), dict)
            else {}
        )
        plane_trace = projection.get("plane_trace") if isinstance(projection.get("plane_trace"), dict) else {}
        event_ref = str(envelope.get("event_ref") or "")
        snapshot_ref = str(blackboard.get("snapshot_ref") or "")
        trace_ref = str(plane_trace.get("trace_ref") or "")
        if event_ref:
            event_record = {
                **envelope,
                "surface_id": "genesis-heartbeat-neural-bus-event",
                "heartbeat_record_id": record.get("record_id"),
                "source_hive_run_id": record.get("source_hive_run_id"),
                "source_hive_run_ref": record.get("source_hive_run_ref"),
                "recorded_at": record.get("recorded_at"),
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
            self._append_unique_jsonl(self.event_ledger_path, event_record, key="event_ref", key_value=event_ref)
        if snapshot_ref:
            self._append_unique_jsonl(self.blackboard_path, blackboard, key="snapshot_ref", key_value=snapshot_ref)
        if trace_ref:
            self._append_unique_jsonl(self.plane_trace_path, plane_trace, key="trace_ref", key_value=trace_ref)

    def _record_with_projection(self, record: dict[str, Any]) -> dict[str, Any]:
        if isinstance(record.get("neural_bus_projection"), dict) and isinstance(record.get("shared_event_spine"), dict):
            return record
        hydrated = dict(record)
        if not isinstance(hydrated.get("neural_bus_projection"), dict):
            hydrated["neural_bus_projection"] = _neural_bus_projection(
                record_id=str(record.get("record_id") or ""),
                source_run_id=str(record.get("source_hive_run_id") or ""),
                heartbeat_id=str(record.get("project_heartbeat_id") or ""),
                runtime_growth_receipt_id=_value(record, "runtime_growth_receipt_id"),
                federated_packet_id=_value(record, "federated_packet_id"),
                recorded_at=str(record.get("recorded_at") or ""),
            )
        if not isinstance(hydrated.get("shared_event_spine"), dict):
            learning_state = (
                record.get("per_user_global_learning_state")
                if isinstance(record.get("per_user_global_learning_state"), dict)
                else {}
            )
            hydrated["shared_event_spine"] = self._publish_shared_event(
                record_id=str(record.get("record_id") or ""),
                source_run_id=str(record.get("source_hive_run_id") or ""),
                heartbeat_id=str(record.get("project_heartbeat_id") or ""),
                session_ref_digest=learning_state.get("session_ref_digest"),
                runtime_growth_receipt_id=_value(record, "runtime_growth_receipt_id"),
                federated_packet_id=_value(record, "federated_packet_id"),
                recorded_at=str(record.get("recorded_at") or ""),
            )
        evidence_refs = list(record.get("evidence_refs") or [])
        evidence_refs.extend(hydrated["neural_bus_projection"].get("evidence_refs", []))
        evidence_refs.extend(hydrated["shared_event_spine"].get("evidence_refs", []))
        hydrated["evidence_refs"] = _sanitize_refs(evidence_refs)[:48]
        return hydrated

    def _append_unique_jsonl(self, path: Path, packet: dict[str, Any], *, key: str, key_value: str) -> None:
        self.heartbeat_dir.mkdir(parents=True, exist_ok=True)
        if path.is_file():
            for existing in self._read_jsonl(path):
                if str(existing.get(key) or "") == key_value:
                    return
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(packet, sort_keys=True) + "\n")

    def _event_ledger_summary(
        self,
        *,
        scoped_events: list[dict[str, Any]],
        all_events: list[dict[str, Any]],
        latest_event: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-heartbeat-neural-bus-ledger-v1",
            "surface_id": "genesis-heartbeat-neural-bus-event-ledger",
            "status": "live-control-plane" if latest_event else "not-observed",
            "mode": "append-only-file-backed",
            "ledger_ref": GENESIS_HEARTBEAT_NEURAL_BUS_REF,
            "event_count": len(scoped_events),
            "global_event_count": len(all_events),
            "latest_event_ref": latest_event.get("event_ref") if latest_event else None,
            "latest_heartbeat_record_id": latest_event.get("heartbeat_record_id") if latest_event else None,
            "latest_source_hive_run_ref": latest_event.get("source_hive_run_ref") if latest_event else None,
            "events": list(reversed(scoped_events))[:20],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def _blackboard_ledger_summary(
        self,
        *,
        scoped_blackboards: list[dict[str, Any]],
        all_blackboards: list[dict[str, Any]],
        latest_blackboard: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-heartbeat-hive-blackboard-ledger-v1",
            "surface_id": "genesis-heartbeat-hive-blackboard-ledger",
            "status": "live-control-plane" if latest_blackboard else "not-observed",
            "mode": "append-only-file-backed",
            "ledger_ref": GENESIS_HEARTBEAT_BLACKBOARD_REF,
            "snapshot_count": len(scoped_blackboards),
            "global_snapshot_count": len(all_blackboards),
            "latest_snapshot_ref": latest_blackboard.get("snapshot_ref") if latest_blackboard else None,
            "latest_heartbeat_record_id": latest_blackboard.get("source_heartbeat_record_id") if latest_blackboard else None,
            "latest_state": latest_blackboard.get("state") if latest_blackboard else None,
            "latest_priority_trails": latest_blackboard.get("priority_trails", []) if latest_blackboard else [],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def _plane_trace_ledger_summary(
        self,
        *,
        scoped_traces: list[dict[str, Any]],
        all_traces: list[dict[str, Any]],
        latest_trace: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-heartbeat-plane-trace-ledger-v1",
            "surface_id": "genesis-heartbeat-plane-trace-ledger",
            "status": "live-control-plane" if latest_trace else "not-observed",
            "mode": "append-only-file-backed",
            "ledger_ref": GENESIS_HEARTBEAT_PLANE_TRACE_REF,
            "trace_count": len(scoped_traces),
            "global_trace_count": len(all_traces),
            "latest_trace_ref": latest_trace.get("trace_ref") if latest_trace else None,
            "latest_heartbeat_record_id": latest_trace.get("source_heartbeat_record_id") if latest_trace else None,
            "latest_planes": latest_trace.get("planes", []) if latest_trace else [],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def _read_records(self) -> list[dict[str, Any]]:
        if not self.chain_path.is_file():
            return []
        return self._read_jsonl(self.chain_path)

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        records: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
        return records


def _compact_lanes(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    lanes: list[dict[str, Any]] = []
    for lane in value:
        if not isinstance(lane, dict):
            continue
        lanes.append(
            {
                "lane_id": str(lane.get("lane_id") or ""),
                "status": str(lane.get("status") or "unknown"),
                "artifact_refs": _sanitize_refs(lane.get("artifact_refs"))[:12],
                "blockers": _dedupe([str(blocker) for blocker in (lane.get("blockers") or [])])[:12],
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
        )
    return lanes


def _is_valid_record(record: dict[str, Any]) -> bool:
    return (
        isinstance(record, dict)
        and record.get("schema_version") == GENESIS_HEARTBEAT_RECORD_SCHEMA
        and record.get("surface_id") == GENESIS_HEARTBEAT_RECORD_SURFACE_ID
        and bool(record.get("record_id"))
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
    )


def _is_valid_event(record: dict[str, Any]) -> bool:
    return (
        isinstance(record, dict)
        and record.get("schema_version") == "nexusnet-neural-bus-event-envelope-v1"
        and record.get("surface_id") == "genesis-heartbeat-neural-bus-event"
        and bool(record.get("event_ref"))
        and bool(record.get("heartbeat_record_id"))
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
    )


def _is_valid_blackboard(record: dict[str, Any]) -> bool:
    return (
        isinstance(record, dict)
        and record.get("schema_version") == "nexusnet-hive-blackboard-snapshot-v1"
        and record.get("surface_id") == "genesis-heartbeat-hive-blackboard-snapshot"
        and bool(record.get("snapshot_ref"))
        and bool(record.get("source_heartbeat_record_id"))
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
    )


def _is_valid_plane_trace(record: dict[str, Any]) -> bool:
    return (
        isinstance(record, dict)
        and record.get("schema_version") == "nexusnet-plane-trace-ledger-v1"
        and record.get("surface_id") == "genesis-heartbeat-plane-trace"
        and bool(record.get("trace_ref"))
        and bool(record.get("source_heartbeat_record_id"))
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
    )


def _filter_projection_records(records: list[dict[str, Any]], heartbeat_record_ids: set[str]) -> list[dict[str, Any]]:
    if not heartbeat_record_ids:
        return records
    return [
        record
        for record in records
        if str(record.get("heartbeat_record_id") or record.get("source_heartbeat_record_id") or "")
        in heartbeat_record_ids
    ]


def _latest_projection_for_record(
    records: list[dict[str, Any]],
    latest_heartbeat_record: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not latest_heartbeat_record:
        return None
    latest_record_id = str(latest_heartbeat_record.get("record_id") or "")
    for record in reversed(records):
        projection_record_id = str(record.get("heartbeat_record_id") or record.get("source_heartbeat_record_id") or "")
        if projection_record_id == latest_record_id:
            return record
    return None


def _neural_bus_projection(
    *,
    record_id: str,
    source_run_id: str,
    heartbeat_id: str,
    runtime_growth_receipt_id: str | None,
    federated_packet_id: str | None,
    recorded_at: str,
) -> dict[str, Any]:
    event_digest = _digest(
        "|".join(
            [
                record_id,
                source_run_id,
                heartbeat_id,
                runtime_growth_receipt_id or "",
                federated_packet_id or "",
                recorded_at,
            ]
        )
    )
    event_ref = f"neural-bus-event::{event_digest}"
    snapshot_ref = f"hive-blackboard::{event_digest}"
    trace_ref = f"plane-trace::{event_digest}"
    source_hive_run_ref = f"hive-forward::{source_run_id}" if source_run_id else None
    evidence_refs = _sanitize_refs(
        [
            GENESIS_HEARTBEAT_NEURAL_BUS_REF,
            GENESIS_HEARTBEAT_BLACKBOARD_REF,
            GENESIS_HEARTBEAT_PLANE_TRACE_REF,
            event_ref,
            snapshot_ref,
            trace_ref,
            record_id,
            source_hive_run_ref,
            heartbeat_id,
            runtime_growth_receipt_id,
            federated_packet_id,
        ]
    )
    return {
        "schema_version": "nexusnet-genesis-heartbeat-neural-bus-projection-v1",
        "surface_id": "genesis-heartbeat-neural-bus-projection",
        "typed_event_envelope": {
            "schema_version": "nexusnet-neural-bus-event-envelope-v1",
            "event_ref": event_ref,
            "event_type": "genesis.heartbeat.recorded",
            "activation_ref": f"activation::{event_digest}",
            "correlation_ref": record_id,
            "source_hive_run_ref": source_hive_run_ref,
            "heartbeat_record_id": record_id,
            "event_privacy_label": "sanitized-genesis-heartbeat",
            "artifact_bound": True,
            "raw_content_included": False,
        },
        "hive_blackboard_snapshot": {
            "schema_version": "nexusnet-hive-blackboard-snapshot-v1",
            "surface_id": "genesis-heartbeat-hive-blackboard-snapshot",
            "snapshot_ref": snapshot_ref,
            "source_heartbeat_record_id": record_id,
            "source_hive_run_ref": source_hive_run_ref,
            "state": "genesis-heartbeat-record-projected",
            "priority_trails": [
                {"topic": "genesis-heartbeat", "strength": 1.0, "artifact_ref": record_id},
                {"topic": "runtime-growth", "strength": 0.8, "artifact_ref": runtime_growth_receipt_id},
                {"topic": "federation", "strength": 0.7, "artifact_ref": federated_packet_id},
            ],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        },
        "plane_trace": {
            "schema_version": "nexusnet-plane-trace-ledger-v1",
            "surface_id": "genesis-heartbeat-plane-trace",
            "trace_ref": trace_ref,
            "source_heartbeat_record_id": record_id,
            "source_hive_run_ref": source_hive_run_ref,
            "planes": ["runtime", "growth", "federation", "memory", "governance"],
            "artifact_bound_downstream_consumption_required": True,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        },
        "evidence_refs": evidence_refs,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


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


def _value(record: dict[str, Any], key: str) -> str | None:
    value = record.get(key)
    return str(value) if value else None


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
