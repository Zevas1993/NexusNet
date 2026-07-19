from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .event_spine import GenesisEventSpineService
from .sensory import GenesisSensoryProvenanceService


GENESIS_MEMORY_ADMISSION_SCHEMA = "nexusnet-genesis-memory-admission-v1"
GENESIS_MEMORY_ADMISSION_SURFACE_ID = "genesis-memory-admission-gate"
GENESIS_MEMORY_DECISION_SCHEMA = "nexusnet-genesis-memory-admission-decision-v1"
GENESIS_MEMORY_DECISION_SURFACE_ID = "genesis-memory-admission-decision"
GENESIS_MEMORY_ADMISSION_REF = "genesis/memory-admission/decisions.jsonl"

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


class GenesisMemoryAdmissionService:
    """Layer 7a memory/retrieval admission gate over Layer 6 sensory provenance."""

    def __init__(
        self,
        *,
        artifacts_dir: Path | str,
        project_root: Path | str,
        sensory_service: GenesisSensoryProvenanceService,
        event_spine: GenesisEventSpineService | None = None,
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.project_root = Path(project_root)
        self.sensory_service = sensory_service
        self.event_spine = event_spine or GenesisEventSpineService(
            artifacts_dir=self.artifacts_dir,
            project_root=self.project_root,
        )
        self.admission_dir = self.artifacts_dir / "genesis" / "memory-admission"
        self.decisions_path = self.admission_dir / "decisions.jsonl"
        self.promotion_gate_dir = self.admission_dir / "promotion-gates"

    def record_from_hive_result(
        self,
        *,
        session_id: str | None,
        hive_result: dict[str, Any],
        sensory_event_id: str | None = None,
        heartbeat_record_id: str | None = None,
    ) -> dict[str, Any]:
        sensory_event = self._latest_sensory_event(session_id=session_id, sensory_event_id=sensory_event_id)
        decision = self._decision(
            session_id=session_id,
            hive_result=hive_result,
            sensory_event=sensory_event,
            heartbeat_record_id=heartbeat_record_id,
        )
        self.admission_dir.mkdir(parents=True, exist_ok=True)
        existing = {item.get("decision_id") for item in self._read_decisions()}
        if decision["decision_id"] not in existing:
            with self.decisions_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(decision, sort_keys=True) + "\n")
        return decision

    def record_manual_ingress(
        self,
        *,
        session_id: str | None,
        ingress_route: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        decision = self._manual_ingress_decision(
            session_id=session_id,
            ingress_route=ingress_route,
            content=content,
            metadata=metadata or {},
        )
        self.admission_dir.mkdir(parents=True, exist_ok=True)
        existing = {item.get("decision_id") for item in self._read_decisions()}
        if decision["decision_id"] not in existing:
            with self.decisions_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(decision, sort_keys=True) + "\n")
        return decision

    def summary(self, session_id: str | None = None) -> dict[str, Any]:
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        all_decisions = [decision for decision in self._read_decisions() if _is_valid_decision(decision)]
        scoped = [
            _replayed(decision)
            for decision in all_decisions
            if not session_ref_digest
            or str(decision.get("session_ref_digest") or "") == session_ref_digest
        ]
        scoped = list(reversed(scoped))
        latest = scoped[0] if scoped else None
        status = "live-control-plane" if latest else "not-observed"
        shared_summary = self.event_spine.summary(session_ref_digest=session_ref_digest)
        return {
            "schema_version": GENESIS_MEMORY_ADMISSION_SCHEMA,
            "surface_id": GENESIS_MEMORY_ADMISSION_SURFACE_ID,
            "status": status,
            "honest_status_label": (
                "genesis-layer7-memory-retrieval-admission-live-control-plane"
                if latest
                else "genesis-layer7-memory-retrieval-admission-not-observed"
            ),
            "authority": "NexusBrain",
            "source": "genesis-sensory-provenance-privacy-gate" if latest else None,
            "session_ref_digest": session_ref_digest,
            "decision_count": len(scoped),
            "global_decision_count": len(all_decisions),
            "latest_decision_id": latest.get("decision_id") if latest else None,
            "latest_sensory_event_id": latest.get("sensory_event_id") if latest else None,
            "latest_heartbeat_record_id": latest.get("heartbeat_record_id") if latest else None,
            "latest_operation_receipt_id": latest.get("operation_receipt_id") if latest else None,
            "latest_evidence_checkpoint_id": latest.get("evidence_checkpoint_id") if latest else None,
            "latest_source_brain_generate_status": latest.get("source_brain_generate_status") if latest else None,
            "latest_decision": latest,
            "decisions": scoped[:20],
            "shared_event_spine": {
                "schema_version": "nexusnet-genesis-memory-admission-shared-event-spine-v1",
                "surface_id": "genesis-memory-admission-shared-event-spine",
                "status": shared_summary.get("status"),
                "latest_event_ref": (
                    latest.get("shared_event_spine", {}).get("event_ref")
                    if latest and isinstance(latest.get("shared_event_spine"), dict)
                    else None
                ),
                "event_count": shared_summary.get("event_type_counts", {}).get(
                    "genesis.memory.admission.decision",
                    0,
                ),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            },
            "artifact_ref": GENESIS_MEMORY_ADMISSION_REF,
            "evidence_refs": _sanitize_refs(
                [
                    GENESIS_MEMORY_ADMISSION_REF,
                    latest.get("decision_id") if latest else None,
                    latest.get("sensory_event_id") if latest else None,
                    latest.get("heartbeat_record_id") if latest else None,
                    latest.get("operation_receipt_id") if latest else None,
                    latest.get("operation_content_ref") if latest else None,
                    latest.get("evidence_checkpoint_id") if latest else None,
                    latest.get("shared_event_spine", {}).get("event_ref")
                    if latest and isinstance(latest.get("shared_event_spine"), dict)
                    else None,
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-layer7-memory-admission-ids-digests-statuses-and-policy-decisions-only-"
                "no-prompts-outputs-session-ids-memory-content-or-local-paths"
            ),
            "mutation_boundary": "admission-decision-and-sanitized-receipt-only-no-raw-memory-training-or-retrieval-truth-write",
        }

    def replay(
        self,
        session_id: str | None = None,
        *,
        limit: int = 100,
        decision_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        all_decisions = [decision for decision in self._read_decisions() if _is_valid_decision(decision)]
        scoped = [
            _replayed(decision)
            for decision in all_decisions
            if not session_ref_digest
            or str(decision.get("session_ref_digest") or "") == session_ref_digest
        ]
        selected_ids = [
            ref
            for item in (decision_refs or [])
            if (ref := _first_safe_ref(item))
        ]
        if decision_refs is not None:
            available_ids = {str(decision.get("decision_id") or "") for decision in scoped}
            unknown_ids = [ref for ref in selected_ids if ref not in available_ids]
            if unknown_ids:
                raise ValueError("decision_refs must belong to the selected session replay")
            scoped = [
                decision
                for decision in scoped
                if str(decision.get("decision_id") or "") in set(selected_ids)
            ]
        scoped = list(reversed(scoped))
        visible = scoped[: max(1, int(limit))]
        route_replay = _route_replay(visible)
        blocked_count = sum(1 for decision in visible if decision.get("memory_write_allowed") is not True)
        allowed_count = len(visible) - blocked_count
        latest = visible[0] if visible else None
        return {
            "schema_version": "nexusnet-genesis-memory-replay-v1",
            "surface_id": "genesis-memory-replay",
            "status": "live-control-plane" if visible else "not-observed",
            "honest_status_label": (
                "genesis-layer7-memory-replay-live-control-plane"
                if visible
                else "genesis-layer7-memory-replay-not-observed"
            ),
            "authority": "NexusBrain",
            "source": "genesis-memory-admission-decisions",
            "session_ref_digest": session_ref_digest,
            "decision_count": len(visible),
            "global_decision_count": len(all_decisions),
            "blocked_count": blocked_count,
            "allowed_count": allowed_count,
            "route_counts": {item["route"]: item["decision_count"] for item in route_replay},
            "route_replay": route_replay,
            "latest_decision_id": latest.get("decision_id") if latest else None,
            "latest_route": _decision_route(latest) if latest else None,
            "decision_refs": _sanitize_refs([decision.get("decision_id") for decision in visible]),
            "selection_mode": "explicit-decision-refs" if decision_refs is not None else "session-replay",
            "blocked_decision_refs": _sanitize_refs(
                [
                    decision.get("decision_id")
                    for decision in visible
                    if decision.get("memory_write_allowed") is not True
                ]
            ),
            "memory_truth_state": {
                "memory_write_allowed": bool(visible) and blocked_count == 0,
                "retrieval_truth_allowed": bool(visible)
                and blocked_count == 0
                and all(decision.get("retrieval_truth_allowed") is True for decision in visible),
                "training_allowed": bool(visible)
                and blocked_count == 0
                and all(decision.get("training_allowed") is True for decision in visible),
                "raw_retrieval_fallback_allowed": False,
                "raw_content_included": False,
            },
            "recent_decisions": [_compact_decision(decision) for decision in visible[:20]],
            "artifact_ref": GENESIS_MEMORY_ADMISSION_REF,
            "evidence_refs": _sanitize_refs(
                [
                    GENESIS_MEMORY_ADMISSION_REF,
                    latest.get("decision_id") if latest else None,
                    *[item.get("latest_decision_id") for item in route_replay],
                ]
            ),
            "replay_status": "replayed" if visible else "not-observed",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-layer7-memory-replay-route-counts-decision-refs-digests-and-policy-booleans-only-"
                "no-prompts-outputs-session-ids-memory-content-or-local-paths"
            ),
            "mutation_boundary": "read-only-replay-no-memory-training-retrieval-or-production-mutation",
        }

    def promotion_gate(
        self,
        session_id: str | None = None,
        *,
        limit: int = 100,
        eval_refs: list[str] | None = None,
        sandbox_ref: str | None = None,
        artifact_trust_refs: list[str] | None = None,
        rollback_plan: str | None = None,
        governance_approval_ref: str | None = None,
        admin_approval_ref: str | None = None,
        decision_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        replay = self.replay(session_id=session_id, limit=limit, decision_refs=decision_refs)
        evidence = {
            "eval_refs": _sanitize_refs(eval_refs or []),
            "sandbox_ref": _first_safe_ref(sandbox_ref),
            "artifact_trust_refs": _sanitize_refs(artifact_trust_refs or []),
            "rollback_plan_ref": _first_safe_ref(rollback_plan),
            "governance_approval_ref": _first_safe_ref(governance_approval_ref),
            "admin_approval_ref": _first_safe_ref(admin_approval_ref),
        }
        controls = {
            "held_out_eval": bool(evidence["eval_refs"]),
            "sandbox_eval": bool(evidence["sandbox_ref"]),
            "artifact_trust": bool(evidence["artifact_trust_refs"]),
            "rollback_plan": bool(evidence["rollback_plan_ref"]),
            "governance_approval": bool(evidence["governance_approval_ref"]),
            "admin_approval": bool(evidence["admin_approval_ref"]),
        }
        submitted_control_evidence = {
            "status": "submitted" if any(controls.values()) else "missing",
            "control_count": sum(1 for passed in controls.values() if passed),
            "eval_ref_count": len(evidence["eval_refs"]),
            "artifact_trust_ref_count": len(evidence["artifact_trust_refs"]),
            "sandbox_ref": evidence["sandbox_ref"],
            "rollback_plan_ref": evidence["rollback_plan_ref"],
            "governance_approval_ref": evidence["governance_approval_ref"],
            "admin_approval_ref": evidence["admin_approval_ref"],
            "evidence_refs": _sanitize_refs(
                [
                    *evidence["eval_refs"],
                    evidence["sandbox_ref"],
                    *evidence["artifact_trust_refs"],
                    evidence["rollback_plan_ref"],
                    evidence["governance_approval_ref"],
                    evidence["admin_approval_ref"],
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        missing_controls = [control for control, passed in controls.items() if not passed]
        blocked_decisions_present = int(replay.get("blocked_count") or 0) > 0
        replay_observed = int(replay.get("decision_count") or 0) > 0
        promotion_targets = _promotion_targets(
            replay=replay,
            controls_passed=not missing_controls,
            blocked_decisions_present=blocked_decisions_present,
            replay_observed=replay_observed,
        )
        replay_decision_ids = {str(item) for item in replay.get("decision_refs") or []}
        source_bindings = [
            _promotion_source_binding(decision)
            for decision in self._read_decisions()
            if str(decision.get("decision_id") or "") in replay_decision_ids
        ]
        promotion_allowed = bool(promotion_targets) and all(
            target.get("allowed") is True for target in promotion_targets.values()
        )
        gate_seed = json.dumps(
            {
                "session_ref_digest": replay.get("session_ref_digest"),
                "decision_refs": replay.get("decision_refs") or [],
                "source_bindings": source_bindings,
                "evidence": evidence,
                "missing_controls": missing_controls,
                "promotion_allowed": promotion_allowed,
            },
            sort_keys=True,
        )
        gate_id = f"genesis-memory-promotion-gate::{_digest(gate_seed)}"
        artifact_ref = f"genesis/memory-admission/promotion-gates/{gate_id.replace('::', '--')}.json"
        packet = {
            "schema_version": "nexusnet-genesis-memory-replay-promotion-gate-v1",
            "surface_id": "genesis-memory-replay-promotion-gate",
            "gate_id": gate_id,
            "status": "promotion-allowed" if promotion_allowed else "blocked",
            "honest_status_label": (
                "genesis-layer10-memory-replay-promotion-gate-passed"
                if promotion_allowed
                else "genesis-layer10-memory-replay-promotion-gate-blocked"
            ),
            "authority": "NexusBrain",
            "source": "genesis-memory-replay",
            "session_ref_digest": replay.get("session_ref_digest"),
            "replay_status": replay.get("replay_status"),
            "replay_decision_count": replay.get("decision_count", 0),
            "blocked_decision_count": replay.get("blocked_count", 0),
            "allowed_decision_count": replay.get("allowed_count", 0),
            "route_counts": replay.get("route_counts") or {},
            "promotion_allowed": promotion_allowed,
            "promotion_targets": promotion_targets,
            "required_controls": list(controls),
            "missing_controls": missing_controls,
            "submitted_control_evidence": submitted_control_evidence,
            "eval_gate": {
                "required": True,
                "passed": controls["held_out_eval"],
                "evidence_refs": evidence["eval_refs"],
                "reason": "held-out eval evidence required before any memory replay promotion",
            },
            "sandbox_gate": {
                "required": True,
                "passed": controls["sandbox_eval"],
                "sandbox_ref": evidence["sandbox_ref"],
                "reason": "closed sandbox eval required before truth promotion",
            },
            "artifact_trust_gate": {
                "required": True,
                "passed": controls["artifact_trust"],
                "artifact_trust_refs": evidence["artifact_trust_refs"],
                "reason": "artifact trust evidence required for replay-derived truth promotion",
            },
            "rollback_gate": {
                "required": True,
                "passed": controls["rollback_plan"],
                "rollback_plan_ref": evidence["rollback_plan_ref"],
                "reason": "rollback plan required before memory/retrieval/training/graph truth promotion",
            },
            "governance_gate": {
                "required": True,
                "passed": controls["governance_approval"] and controls["admin_approval"],
                "governance_approval_ref": evidence["governance_approval_ref"],
                "admin_approval_ref": evidence["admin_approval_ref"],
                "reason": "governance and admin approval required before promotion",
            },
            "decision_refs": replay.get("decision_refs") or [],
            "source_bindings": source_bindings,
            "blocked_decision_refs": replay.get("blocked_decision_refs") or [],
            "artifact_ref": artifact_ref,
            "evidence_refs": _sanitize_refs(
                [
                    replay.get("artifact_ref"),
                    *(replay.get("decision_refs") or []),
                    *[ref for binding in source_bindings for ref in binding.get("evidence_refs", [])],
                    *evidence["eval_refs"],
                    evidence["sandbox_ref"],
                    *evidence["artifact_trust_refs"],
                    evidence["rollback_plan_ref"],
                    evidence["governance_approval_ref"],
                    evidence["admin_approval_ref"],
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-layer10-memory-replay-promotion-gate-refs-counts-booleans-and-blockers-only-"
                "no-prompts-outputs-session-ids-memory-content-or-local-paths"
            ),
            "mutation_boundary": "read-only-gate-no-truth-promotion-training-graph-write-or-production-mutation",
        }
        packet["shared_event_spine"] = self._publish_shared_event(
            event_type="genesis.memory.promotion.gate",
            source_surface_id="genesis-memory-replay-promotion-gate",
            correlation_ref=gate_id,
            session_ref_digest=packet.get("session_ref_digest"),
            source_hive_run_ref=None,
            heartbeat_record_id=None,
            artifact_refs=[artifact_ref, gate_id, *(packet.get("decision_refs") or [])],
            planes=["memory", "replay", "promotion", "eval", "governance"],
            priority_topic="genesis-memory-promotion-gate",
            created_at=None,
        )
        packet["evidence_refs"] = _sanitize_refs(
            [
                *(packet.get("evidence_refs") or []),
                *packet["shared_event_spine"].get("evidence_refs", []),
            ]
        )
        self._write_promotion_gate(packet, artifact_ref=artifact_ref)
        return packet

    def promotion_gate_summary(self, session_id: str | None = None, *, limit: int = 100) -> dict[str, Any]:
        replay = self.replay(session_id=session_id, limit=limit)
        latest_submitted = self._latest_submitted_promotion_gate(
            session_ref_digest=replay.get("session_ref_digest"),
            decision_refs=replay.get("decision_refs") or [],
        )
        if latest_submitted:
            return self._with_latest_governed_application(latest_submitted)
        return self._with_latest_governed_application(self.promotion_gate(session_id=session_id, limit=limit))

    def promotion_gate_apply(self, payload: dict[str, Any]) -> dict[str, Any]:
        gate_id = _first_safe_ref(payload.get("gate_id"))
        if not gate_id:
            raise ValueError("gate_id is required")
        gate = self._promotion_gate_by_id(gate_id)
        if not gate:
            raise KeyError(f"unknown promotion gate: {gate_id}")
        sandbox_eval_run_id = _first_safe_ref(payload.get("sandbox_eval_run_id"))
        sandbox_eval_run = self._sandbox_eval_by_id(sandbox_eval_run_id) if sandbox_eval_run_id else None
        evidence = {
            "eval_result_refs": _sanitize_refs(payload.get("eval_result_refs") or []),
            "sandbox_eval_ref": _first_safe_ref(payload.get("sandbox_eval_ref")),
            "sandbox_eval_run_id": sandbox_eval_run_id,
            "artifact_trust_ref": _first_safe_ref(payload.get("artifact_trust_ref")),
            "rollback_proof_ref": _first_safe_ref(payload.get("rollback_proof_ref")),
            "admin_decision_ref": _first_safe_ref(payload.get("admin_decision_ref")),
        }
        controls = {
            "eval_result": bool(evidence["eval_result_refs"]) or (
                isinstance(sandbox_eval_run, dict) and sandbox_eval_run.get("passed") is True
            ),
            "sandbox_eval": isinstance(sandbox_eval_run, dict) and sandbox_eval_run.get("passed") is True,
            "artifact_trust": bool(evidence["artifact_trust_ref"]),
            "rollback_proof": bool(evidence["rollback_proof_ref"]),
            "admin_decision": bool(evidence["admin_decision_ref"]),
        }
        missing_controls = [
            control
            for control, passed in controls.items()
            if not passed and control not in {"eval_result", "sandbox_eval"}
        ]
        gate_promotion_allowed = gate.get("promotion_allowed") is True
        blockers: list[str] = []
        if not gate_promotion_allowed:
            blockers.append("promotion_gate_not_allowed")
        if not sandbox_eval_run_id:
            blockers.append("closed_sandbox_eval_receipt_required")
        elif not sandbox_eval_run or sandbox_eval_run.get("passed") is not True:
            blockers.append("sandbox_eval_passed_required")
        if missing_controls:
            blockers.append("eval_sandbox_artifact_trust_rollback_and_admin_decision_required")
        apply_allowed = gate_promotion_allowed and not blockers
        created_at = _utcnow()
        seed = json.dumps(
            {
                "gate_id": gate_id,
                "decision_refs": gate.get("decision_refs") or [],
                "evidence": evidence,
                "apply_allowed": apply_allowed,
                "created_at": created_at,
            },
            sort_keys=True,
        )
        application_id = f"genesis-memory-promotion-application::{_digest(seed)}"
        application_ref = (
            f"genesis/memory-admission/promotion-applications/{_artifact_id(application_id)}.json"
        )
        shadow_candidate_ref = (
            f"genesis/memory-admission/promotion-candidates/{_artifact_id(application_id)}.json"
            if apply_allowed
            else None
        )
        admin_identity = str(payload.get("approved_by") or "admin")
        packet = {
            "schema_version": "nexusnet-genesis-memory-replay-promotion-application-v1",
            "surface_id": "genesis-memory-replay-promotion-application",
            "application_id": application_id,
            "application_ref": application_ref,
            "gate_id": gate_id,
            "status": "shadow-candidate-written" if apply_allowed else "blocked",
            "honest_status_label": (
                "genesis-layer10-memory-promotion-application-shadow-candidate-written"
                if apply_allowed
                else "genesis-layer10-memory-promotion-application-blocked"
            ),
            "authority": "NexusBrain",
            "source": "genesis-memory-replay-promotion-gate",
            "session_ref_digest": gate.get("session_ref_digest"),
            "gate_promotion_allowed": gate_promotion_allowed,
            "apply_allowed": apply_allowed,
            "blockers": blockers,
            "missing_apply_controls": missing_controls,
            "shadow_candidate_written": bool(shadow_candidate_ref),
            "shadow_candidate_ref": shadow_candidate_ref,
            "shadow_candidate_scope": "genesis-memory-replay-shadow-candidate-only",
            "promotion_targets": gate.get("promotion_targets") or {},
            "decision_refs": gate.get("decision_refs") or [],
            "admin_decision_packet": {
                "schema_version": "nexusnet-genesis-memory-promotion-admin-decision-v1",
                "surface_id": "genesis-memory-promotion-admin-decision",
                "decision": "admin-approved-shadow-only" if apply_allowed else "admin-blocked-shadow-apply",
                "admin_decision_ref": evidence["admin_decision_ref"],
                "admin_actor_digest": _privacy_digest(admin_identity),
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
                "raw_content_included": False,
            },
            "sandbox_eval": {
                "required": True,
                "passed": controls["sandbox_eval"],
                "sandbox_eval_ref": evidence["sandbox_eval_ref"],
                "eval_run_id": sandbox_eval_run.get("eval_run_id") if sandbox_eval_run else sandbox_eval_run_id,
                "artifact_ref": sandbox_eval_run.get("artifact_ref") if sandbox_eval_run else None,
                "case_count": sandbox_eval_run.get("case_count", 0) if sandbox_eval_run else 0,
                "failed_count": sandbox_eval_run.get("failed_count", 0) if sandbox_eval_run else 0,
                "raw_content_included": False,
            },
            "eval_result_gate": {
                "required": True,
                "passed": controls["eval_result"],
                "eval_result_refs": evidence["eval_result_refs"],
                "raw_content_included": False,
            },
            "artifact_trust_gate": {
                "required": True,
                "passed": controls["artifact_trust"],
                "artifact_trust_ref": evidence["artifact_trust_ref"],
                "raw_content_included": False,
            },
            "rollback_proof": {
                "required": True,
                "passed": controls["rollback_proof"],
                "rollback_available": controls["rollback_proof"],
                "rollback_proof_ref": evidence["rollback_proof_ref"],
                "restore_strategy": "delete-or-retain-shadow-candidate-with-rollback-receipt-no-production-truth-write",
                "raw_content_included": False,
            },
            "created_at": created_at,
            "evidence_refs": _sanitize_refs(
                [
                    gate.get("artifact_ref"),
                    gate_id,
                    application_ref,
                    shadow_candidate_ref,
                    sandbox_eval_run.get("artifact_ref") if sandbox_eval_run else None,
                    sandbox_eval_run_id,
                    *evidence["eval_result_refs"],
                    evidence["sandbox_eval_ref"],
                    evidence["artifact_trust_ref"],
                    evidence["rollback_proof_ref"],
                    evidence["admin_decision_ref"],
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-layer10-memory-promotion-application-ids-digests-refs-counts-and-status-only-"
                "no-prompts-outputs-session-ids-admin-identities-memory-content-or-local-paths"
            ),
            "mutation_boundary": "shadow-candidate-artifact-only-no-memory-training-graph-truth-or-production-mutation",
        }
        if shadow_candidate_ref:
            self._write_shadow_candidate(packet, gate=gate, artifact_ref=shadow_candidate_ref)
        self._write_json_artifact(packet, artifact_ref=application_ref)
        return packet

    def promotion_gate_commit(self, payload: dict[str, Any]) -> dict[str, Any]:
        application_id = _first_safe_ref(payload.get("application_id"))
        if not application_id:
            raise ValueError("application_id is required")
        application = self._promotion_application_by_id(application_id)
        if not application:
            raise KeyError(f"unknown promotion application: {application_id}")
        gate_id = str(application.get("gate_id") or "")
        gate = self._promotion_gate_by_id(gate_id)
        if not gate:
            raise KeyError(f"unknown promotion gate: {gate_id}")
        foundation = getattr(self, "memory_foundation", None)
        if foundation is None or not callable(getattr(foundation, "commit", None)):
            raise ValueError("genesis memory foundation is not configured")
        raw_contents = payload.get("source_content_by_decision_id")
        if not isinstance(raw_contents, dict):
            raise ValueError("source_content_by_decision_id must be an object")
        source_contents = {
            str(decision_id): str(content)
            for decision_id, content in raw_contents.items()
            if isinstance(content, str)
        }
        governance_commit_ref = _first_safe_ref(payload.get("governance_commit_ref"))
        admin_commit_ref = _first_safe_ref(payload.get("admin_commit_ref"))
        if not governance_commit_ref or not admin_commit_ref:
            raise ValueError("governance_commit_ref and admin_commit_ref are required")
        decisions = [
            decision
            for decision_ref in gate.get("decision_refs") or []
            if (decision := self._decision_by_id(str(decision_ref))) is not None
        ]
        return foundation.commit(
            application=application,
            gate=gate,
            decisions=decisions,
            source_content_by_decision_id=source_contents,
            governance_commit_ref=governance_commit_ref,
            admin_commit_ref=admin_commit_ref,
            admin_actor_digest=_privacy_digest(str(payload.get("approved_by") or "admin")),
        )

    def promotion_gate_sandbox_eval(self, payload: dict[str, Any]) -> dict[str, Any]:
        gate_id = _first_safe_ref(payload.get("gate_id"))
        if not gate_id:
            raise ValueError("gate_id is required")
        gate = self._promotion_gate_by_id(gate_id)
        if not gate:
            raise KeyError(f"unknown promotion gate: {gate_id}")
        artifact_trust_ref = _first_safe_ref(payload.get("artifact_trust_ref"))
        rollback_proof_ref = _first_safe_ref(payload.get("rollback_proof_ref"))
        cases = _normalize_sandbox_eval_cases(payload.get("eval_cases"))
        case_results = [
            _sandbox_eval_case_result(case, gate=gate)
            for case in cases
        ]
        missing_controls = [
            control
            for control, passed in {
                "artifact_trust": bool(artifact_trust_ref),
                "rollback_proof": bool(rollback_proof_ref),
            }.items()
            if not passed
        ]
        failed_count = sum(1 for case in case_results if case.get("passed") is not True)
        passed = bool(case_results) and failed_count == 0 and not missing_controls
        seed = json.dumps(
            {
                "gate_id": gate_id,
                "case_results": case_results,
                "artifact_trust_ref": artifact_trust_ref,
                "rollback_proof_ref": rollback_proof_ref,
            },
            sort_keys=True,
        )
        eval_run_id = f"genesis-memory-sandbox-eval::{_digest(seed)}"
        artifact_ref = f"genesis/memory-admission/promotion-sandbox-evals/{_artifact_id(eval_run_id)}.json"
        packet = {
            "schema_version": "nexusnet-genesis-memory-replay-sandbox-eval-v1",
            "surface_id": "genesis-memory-replay-sandbox-eval",
            "eval_run_id": eval_run_id,
            "artifact_ref": artifact_ref,
            "gate_id": gate_id,
            "status": "passed" if passed else "failed",
            "honest_status_label": (
                "genesis-layer10-memory-promotion-closed-sandbox-eval-passed"
                if passed
                else "genesis-layer10-memory-promotion-closed-sandbox-eval-failed"
            ),
            "authority": "NexusBrain",
            "source": "genesis-memory-replay-promotion-gate",
            "session_ref_digest": gate.get("session_ref_digest"),
            "sandbox_tier": "closed-deterministic",
            "passed": passed,
            "case_count": len(case_results),
            "failed_count": failed_count,
            "missing_controls": missing_controls,
            "artifact_trust_ref": artifact_trust_ref,
            "rollback_proof_ref": rollback_proof_ref,
            "case_results": case_results,
            "created_at": _utcnow(),
            "evidence_refs": _sanitize_refs(
                [
                    gate.get("artifact_ref"),
                    gate_id,
                    artifact_ref,
                    artifact_trust_ref,
                    rollback_proof_ref,
                    *[case.get("case_ref") for case in case_results],
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-layer10-closed-sandbox-eval-case-ids-targets-booleans-and-refs-only-"
                "no-prompts-outputs-session-ids-memory-content-or-local-paths"
            ),
            "mutation_boundary": "closed-sandbox-eval-receipt-only-no-shadow-candidate-or-production-mutation",
        }
        packet["shared_event_spine"] = self._publish_shared_event(
            event_type="genesis.memory.promotion.sandbox_eval",
            source_surface_id="genesis-memory-replay-sandbox-eval",
            correlation_ref=eval_run_id,
            session_ref_digest=packet.get("session_ref_digest"),
            source_hive_run_ref=None,
            heartbeat_record_id=None,
            artifact_refs=[artifact_ref, eval_run_id, gate_id, artifact_trust_ref, rollback_proof_ref],
            planes=["memory", "promotion", "sandbox", "eval", "governance"],
            priority_topic="genesis-memory-promotion-sandbox-eval",
            created_at=str(packet.get("created_at") or ""),
        )
        packet["evidence_refs"] = _sanitize_refs(
            [
                *(packet.get("evidence_refs") or []),
                *packet["shared_event_spine"].get("evidence_refs", []),
            ]
        )
        self._write_json_artifact(packet, artifact_ref=artifact_ref)
        return packet

    def promotion_gate_rollback(self, payload: dict[str, Any]) -> dict[str, Any]:
        application_id = _first_safe_ref(payload.get("application_id"))
        if not application_id:
            raise ValueError("application_id is required")
        application = self._promotion_application_by_id(application_id)
        if not application:
            raise KeyError(f"unknown promotion application: {application_id}")
        created_at = _utcnow()
        reason_ref = f"rollback-reason::{_digest(str(payload.get('reason') or 'operator-requested'))}"
        foundation = getattr(self, "memory_foundation", None)
        foundation_rollback = (
            foundation.rollback_application(application_id=application_id, reason_ref=reason_ref)
            if foundation is not None and callable(getattr(foundation, "rollback_application", None))
            else None
        )
        rollback_id = (
            str(foundation_rollback.get("rollback_id"))
            if isinstance(foundation_rollback, dict)
            else f"genesis-memory-promotion-rollback::{_digest('|'.join([application_id, created_at]))}"
        )
        rollback_ref = f"genesis/memory-admission/promotion-rollbacks/{_artifact_id(rollback_id)}.json"
        canonical_reverted = isinstance(foundation_rollback, dict)
        packet = {
            "schema_version": "nexusnet-genesis-memory-replay-promotion-rollback-v1",
            "surface_id": "genesis-memory-replay-promotion-rollback",
            "rollback_id": rollback_id,
            "rollback_ref": rollback_ref,
            "application_id": application_id,
            "gate_id": application.get("gate_id"),
            "status": "rollback-recorded",
            "rollback_state": "canonical-memory-reverted" if canonical_reverted else "shadow-candidate-reverted",
            "shadow_candidate_ref": application.get("shadow_candidate_ref"),
            "shadow_candidate_retained_for_audit": True,
            "reverted_memory_count": int(foundation_rollback.get("reverted_memory_count") or 0)
            if canonical_reverted
            else 0,
            "memory_foundation_rollback_ref": foundation_rollback.get("rollback_ref")
            if canonical_reverted
            else None,
            "runtime_deactivation": foundation_rollback.get("runtime_deactivation")
            if canonical_reverted
            else {
                "status": "not-applied-shadow-only",
                "raw_content_included": False,
            },
            "reason_ref": reason_ref,
            "rolled_back_at": created_at,
            "evidence_refs": _sanitize_refs(
                [
                    application.get("application_ref"),
                    application_id,
                    application.get("gate_id"),
                    application.get("shadow_candidate_ref"),
                    foundation_rollback.get("rollback_ref") if canonical_reverted else None,
                    foundation_rollback.get("commit_id") if canonical_reverted else None,
                    reason_ref,
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": canonical_reverted,
            "active_production_mutated": bool(
                canonical_reverted and int(foundation_rollback.get("reverted_memory_count") or 0) > 0
            ),
            "privacy_boundary": (
                "sanitized-layer10-memory-promotion-rollback-ids-digests-refs-and-status-only-"
                "no-rollback-reason-text-session-ids-memory-content-or-local-paths"
            ),
            "mutation_boundary": (
                "governed-layer7-canonical-memory-tombstone-shadow-and-audit-evidence-retained"
                if canonical_reverted
                else "rollback-receipt-only-shadow-candidate-retained-for-audit-no-production-mutation"
            ),
        }
        self._write_json_artifact(packet, artifact_ref=rollback_ref)
        return packet

    def _decision(
        self,
        *,
        session_id: str | None,
        hive_result: dict[str, Any],
        sensory_event: dict[str, Any],
        heartbeat_record_id: str | None,
    ) -> dict[str, Any]:
        privacy_gate = sensory_event.get("privacy_gate") if isinstance(sensory_event.get("privacy_gate"), dict) else {}
        quarantine = (
            privacy_gate.get("quarantine_decision")
            if isinstance(privacy_gate.get("quarantine_decision"), dict)
            else {}
        )
        privacy_class = str(privacy_gate.get("privacy_class") or "unknown")
        consent_status = str(privacy_gate.get("consent_status") or "unknown")
        rights_status = str(privacy_gate.get("rights_license_status") or "unknown")
        source_run_id = str(hive_result.get("run_id") or "")
        sensory_event_id = str(sensory_event.get("event_id") or "")
        operation_receipt_id = str(sensory_event.get("operation_receipt_id") or "")
        operation_content_ref = str(sensory_event.get("operation_content_ref") or "")
        evidence_checkpoint_id = str(sensory_event.get("evidence_checkpoint_id") or "")
        source_brain_generate_status = str(sensory_event.get("source_brain_generate_status") or "unknown")
        source_critique_status = str(sensory_event.get("source_critique_status") or "unknown")
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        allow_memory = (
            privacy_class not in {"operator-private", "unknown"}
            and consent_status in {"memory-approved", "training-approved"}
            and rights_status in {"approved-for-memory", "approved-for-training"}
            and quarantine.get("memory_write_allowed") is True
        )
        allow_retrieval_truth = allow_memory and quarantine.get("retrieval_truth_allowed") is True
        allow_training = (
            allow_memory
            and consent_status == "training-approved"
            and rights_status == "approved-for-training"
            and quarantine.get("training_allowed") is True
        )
        decision = "admitted" if allow_memory else "blocked-private-runtime-content"
        created_at = _utcnow()
        seed = json.dumps(
            {
                "session_ref_digest": session_ref_digest,
                "source_run_id": source_run_id,
                "sensory_event_id": sensory_event_id,
                "heartbeat_record_id": heartbeat_record_id,
                "operation_receipt_id": operation_receipt_id,
                "evidence_checkpoint_id": evidence_checkpoint_id,
                "source_brain_generate_status": source_brain_generate_status,
                "decision": decision,
                "created_at": created_at,
            },
            sort_keys=True,
        )
        decision_id = f"genesis-memory-admission::{_digest(seed)}"
        shared_event_spine = self._publish_shared_event(
            event_type="genesis.memory.admission.decision",
            source_surface_id=GENESIS_MEMORY_DECISION_SURFACE_ID,
            correlation_ref=decision_id,
            session_ref_digest=session_ref_digest,
            source_hive_run_ref=f"hive-forward::{source_run_id}" if source_run_id else None,
            heartbeat_record_id=heartbeat_record_id,
            artifact_refs=[
                GENESIS_MEMORY_ADMISSION_REF,
                decision_id,
                sensory_event_id,
                heartbeat_record_id,
                operation_receipt_id,
                operation_content_ref,
                evidence_checkpoint_id,
            ],
            planes=["memory", "provenance", "privacy", "admission", "governance"],
            priority_topic="genesis-memory-admission",
            created_at=created_at,
        )
        return {
            "schema_version": GENESIS_MEMORY_DECISION_SCHEMA,
            "surface_id": GENESIS_MEMORY_DECISION_SURFACE_ID,
            "decision_id": decision_id,
            "status": "memory-admission-decided",
            "decision": decision,
            "source": "nexusbrain-generate",
            "source_hive_run_ref": f"hive-forward::{source_run_id}" if source_run_id else None,
            "sensory_event_id": sensory_event_id or None,
            "heartbeat_record_id": heartbeat_record_id,
            "operation_receipt_id": operation_receipt_id or None,
            "operation_content_ref": operation_content_ref or None,
            "evidence_checkpoint_id": evidence_checkpoint_id or None,
            "source_brain_generate_status": source_brain_generate_status,
            "source_critique_status": source_critique_status,
            "session_ref_digest": session_ref_digest,
            "privacy_class": privacy_class,
            "consent_status": consent_status,
            "rights_license_status": rights_status,
            "memory_write_allowed": allow_memory,
            "retrieval_truth_allowed": allow_retrieval_truth,
            "training_allowed": allow_training,
            "sanitized_receipt_written": True,
            "blocked_routes": [
                route
                for route, allowed in {
                    "raw-inference-memory": allow_memory,
                    "retrieval-truth-promotion": allow_retrieval_truth,
                    "training-material": allow_training,
                }.items()
                if not allowed
            ],
            "shared_event_spine": shared_event_spine,
            "evidence_refs": _sanitize_refs(
                [
                    sensory_event_id,
                    heartbeat_record_id,
                    operation_receipt_id,
                    operation_content_ref,
                    evidence_checkpoint_id,
                    f"hive-forward::{source_run_id}",
                    *shared_event_spine.get("evidence_refs", []),
                ]
            ),
            "created_at": created_at,
            "replay_status": "recorded",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def _manual_ingress_decision(
        self,
        *,
        session_id: str | None,
        ingress_route: str,
        content: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        privacy_class = str(metadata.get("privacy_class") or ("operator-private" if _looks_private(content) else "unspecified"))
        consent_status = str(metadata.get("consent_status") or "not-declared")
        rights_status = str(metadata.get("rights_license_status") or metadata.get("license_status") or "not-declared")
        source_kind = str(metadata.get("source_kind") or ingress_route)
        source_ref = _first_safe_ref(metadata.get("source_ref"))
        explicit_private = privacy_class == "operator-private" or _looks_private(content)
        explicit_blocked_rights = rights_status in {
            "not-approved-for-training",
            "blocked",
            "blocked_tos_risk",
            "blocked_unknown_license",
        }
        memory_write_allowed = not explicit_private and consent_status in {
            "memory-approved",
            "training-approved",
            "operator-approved",
            "not-declared",
        }
        retrieval_truth_allowed = (
            ingress_route == "retrieval-document-ingest"
            and memory_write_allowed
            and not explicit_blocked_rights
        )
        training_allowed = (
            memory_write_allowed
            and consent_status == "training-approved"
            and rights_status == "approved-for-training"
        )
        blocked = not memory_write_allowed or (
            ingress_route == "retrieval-document-ingest" and not retrieval_truth_allowed
        )
        decision = "blocked-private-manual-ingress" if blocked else "admitted-manual-ingress"
        created_at = _utcnow()
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        content_ref = f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"
        seed = json.dumps(
            {
                "session_ref_digest": session_ref_digest,
                "ingress_route": ingress_route,
                "source_kind": source_kind,
                "source_ref": source_ref,
                "content_ref": content_ref,
                "decision": decision,
                "created_at": created_at,
            },
            sort_keys=True,
        )
        decision_id = f"genesis-memory-admission::{_digest(seed)}"
        shared_event_spine = self._publish_shared_event(
            event_type="genesis.memory.manual_ingress.decision",
            source_surface_id=GENESIS_MEMORY_DECISION_SURFACE_ID,
            correlation_ref=decision_id,
            session_ref_digest=session_ref_digest,
            source_hive_run_ref=None,
            heartbeat_record_id=None,
            artifact_refs=[GENESIS_MEMORY_ADMISSION_REF, decision_id, content_ref, f"manual-ingress::{ingress_route}"],
            planes=["memory", "manual-ingress", "privacy", "admission", "governance"],
            priority_topic="genesis-memory-manual-ingress",
            created_at=created_at,
        )
        return {
            "schema_version": GENESIS_MEMORY_DECISION_SCHEMA,
            "surface_id": GENESIS_MEMORY_DECISION_SURFACE_ID,
            "decision_id": decision_id,
            "status": "memory-admission-decided",
            "decision": decision,
            "source": "manual-ingress",
            "ingress_route": ingress_route,
            "source_kind": source_kind,
            "source_ref": source_ref,
            "content_ref": content_ref,
            "session_ref_digest": session_ref_digest,
            "privacy_class": privacy_class,
            "consent_status": consent_status,
            "rights_license_status": rights_status,
            "memory_write_allowed": memory_write_allowed,
            "retrieval_truth_allowed": retrieval_truth_allowed,
            "training_allowed": training_allowed,
            "sanitized_receipt_written": True,
            "blocked_routes": [
                route
                for route, allowed in {
                    "manual-memory-write": memory_write_allowed,
                    "retrieval-truth-promotion": retrieval_truth_allowed
                    if ingress_route == "retrieval-document-ingest"
                    else True,
                    "training-material": training_allowed,
                }.items()
                if not allowed
            ],
            "shared_event_spine": shared_event_spine,
            "evidence_refs": _sanitize_refs(
                [
                    content_ref,
                    f"manual-ingress::{ingress_route}",
                    *shared_event_spine.get("evidence_refs", []),
                ]
            ),
            "created_at": created_at,
            "replay_status": "recorded",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def _latest_sensory_event(self, *, session_id: str | None, sensory_event_id: str | None) -> dict[str, Any]:
        summary = self.sensory_service.summary(session_id=session_id)
        events = summary.get("events") if isinstance(summary.get("events"), list) else []
        if sensory_event_id:
            for event in events:
                if str(event.get("event_id") or "") == sensory_event_id:
                    return event
        return events[0] if events else {}

    def _read_decisions(self) -> list[dict[str, Any]]:
        if not self.decisions_path.is_file():
            return []
        records: list[dict[str, Any]] = []
        for line in self.decisions_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
        return records

    def _write_promotion_gate(self, packet: dict[str, Any], *, artifact_ref: str) -> None:
        self._write_json_artifact(packet, artifact_ref=artifact_ref)

    def _write_json_artifact(self, packet: dict[str, Any], *, artifact_ref: str) -> None:
        path = self.artifacts_dir / artifact_ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")

    def _write_shadow_candidate(self, packet: dict[str, Any], *, gate: dict[str, Any], artifact_ref: str) -> None:
        candidate = {
            "schema_version": "nexusnet-genesis-memory-replay-shadow-candidate-v1",
            "surface_id": "genesis-memory-replay-shadow-candidate",
            "status": "shadow-candidate",
            "application_id": packet.get("application_id"),
            "gate_id": packet.get("gate_id"),
            "shadow_candidate_ref": artifact_ref,
            "session_ref_digest": gate.get("session_ref_digest"),
            "promotion_targets": gate.get("promotion_targets") or {},
            "decision_refs": gate.get("decision_refs") or [],
            "source_application_ref": packet.get("application_ref"),
            "source_gate_ref": gate.get("artifact_ref"),
            "created_at": packet.get("created_at"),
            "evidence_refs": _sanitize_refs(
                [
                    packet.get("application_ref"),
                    packet.get("application_id"),
                    packet.get("gate_id"),
                    gate.get("artifact_ref"),
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-shadow-candidate-refs-status-and-policy-targets-only-"
                "no-memory-content-prompts-outputs-session-ids-or-local-paths"
            ),
            "mutation_boundary": "shadow-candidate-artifact-only-no-production-truth-write",
        }
        self._write_json_artifact(candidate, artifact_ref=artifact_ref)

    def _publish_shared_event(
        self,
        *,
        event_type: str,
        source_surface_id: str,
        correlation_ref: str,
        session_ref_digest: str | None,
        source_hive_run_ref: str | None,
        heartbeat_record_id: str | None,
        artifact_refs: list[str | None],
        planes: list[str],
        priority_topic: str,
        created_at: str | None,
    ) -> dict[str, Any]:
        return self.event_spine.publish_event(
            event_type=event_type,
            source_surface_id=source_surface_id,
            correlation_ref=correlation_ref,
            session_ref_digest=session_ref_digest,
            source_hive_run_ref=source_hive_run_ref,
            heartbeat_record_id=heartbeat_record_id,
            privacy_label=f"sanitized-{source_surface_id}",
            artifact_refs=artifact_refs,
            planes=planes,
            priority_trails=[
                {"topic": priority_topic, "strength": 1.0, "artifact_ref": correlation_ref}
            ],
            created_at=created_at or None,
        )

    def _promotion_gate_by_id(self, gate_id: str) -> dict[str, Any] | None:
        if not self.promotion_gate_dir.is_dir():
            return None
        for path in self.promotion_gate_dir.glob("*.json"):
            try:
                packet = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if _is_valid_promotion_gate(packet) and packet.get("gate_id") == gate_id:
                return packet
        return None

    def _promotion_application_by_id(self, application_id: str) -> dict[str, Any] | None:
        applications_dir = self.admission_dir / "promotion-applications"
        if not applications_dir.is_dir():
            return None
        for path in applications_dir.glob("*.json"):
            try:
                packet = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if _is_valid_promotion_application(packet) and packet.get("application_id") == application_id:
                return packet
        return None

    def _decision_by_id(self, decision_id: str) -> dict[str, Any] | None:
        return next(
            (
                decision
                for decision in self._read_decisions()
                if _is_valid_decision(decision) and decision.get("decision_id") == decision_id
            ),
            None,
        )

    def _sandbox_eval_by_id(self, eval_run_id: str | None) -> dict[str, Any] | None:
        evals_dir = self.admission_dir / "promotion-sandbox-evals"
        if not eval_run_id or not evals_dir.is_dir():
            return None
        for path in evals_dir.glob("*.json"):
            try:
                packet = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if _is_valid_sandbox_eval(packet) and packet.get("eval_run_id") == eval_run_id:
                return packet
        return None

    def _with_latest_governed_application(self, gate: dict[str, Any]) -> dict[str, Any]:
        packet = dict(gate)
        latest_sandbox_eval = self._latest_sandbox_eval_run(gate_id=str(packet.get("gate_id") or ""))
        packet["latest_sandbox_eval_run"] = latest_sandbox_eval or {
            "surface_id": "genesis-memory-replay-sandbox-eval",
            "status": "not-observed",
            "eval_run_id": None,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        latest_application = self._latest_governed_application(gate_id=str(packet.get("gate_id") or ""))
        packet["latest_governed_application"] = latest_application or {
            "surface_id": "genesis-memory-replay-promotion-application",
            "status": "not-observed",
            "application_id": None,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        latest_rollback = self._latest_rollback_record(
            application_id=str(latest_application.get("application_id") or "") if latest_application else ""
        )
        packet["latest_rollback_record"] = latest_rollback or {
            "surface_id": "genesis-memory-replay-promotion-rollback",
            "status": "not-observed",
            "rollback_id": None,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        foundation = getattr(self, "memory_foundation", None)
        packet["memory_foundation_status"] = (
            foundation.summary(session_ref_digest=packet.get("session_ref_digest"))
            if foundation is not None and callable(getattr(foundation, "summary", None))
            else {
                "surface_id": "genesis-memory-foundation",
                "status": "not-configured",
                "honest_status_label": "genesis-layer7-memory-foundation-not-configured",
                "active_memory_count": 0,
                "revoked_memory_count": 0,
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
        )
        return packet

    def _latest_sandbox_eval_run(self, *, gate_id: str) -> dict[str, Any] | None:
        evals_dir = self.admission_dir / "promotion-sandbox-evals"
        if not gate_id or not evals_dir.is_dir():
            return None
        candidates: list[tuple[float, dict[str, Any]]] = []
        for path in evals_dir.glob("*.json"):
            try:
                packet = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not _is_valid_sandbox_eval(packet):
                continue
            if packet.get("gate_id") != gate_id:
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                mtime = 0.0
            candidates.append((mtime, packet))
        if not candidates:
            return None
        return sorted(candidates, key=lambda item: item[0], reverse=True)[0][1]

    def _latest_governed_application(self, *, gate_id: str) -> dict[str, Any] | None:
        applications_dir = self.admission_dir / "promotion-applications"
        if not gate_id or not applications_dir.is_dir():
            return None
        candidates: list[tuple[float, dict[str, Any]]] = []
        for path in applications_dir.glob("*.json"):
            try:
                packet = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not _is_valid_promotion_application(packet):
                continue
            if packet.get("gate_id") != gate_id:
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                mtime = 0.0
            candidates.append((mtime, packet))
        if not candidates:
            return None
        return sorted(candidates, key=lambda item: item[0], reverse=True)[0][1]

    def _latest_rollback_record(self, *, application_id: str) -> dict[str, Any] | None:
        rollbacks_dir = self.admission_dir / "promotion-rollbacks"
        if not application_id or not rollbacks_dir.is_dir():
            return None
        candidates: list[tuple[float, dict[str, Any]]] = []
        for path in rollbacks_dir.glob("*.json"):
            try:
                packet = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not _is_valid_promotion_rollback(packet):
                continue
            if packet.get("application_id") != application_id:
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                mtime = 0.0
            candidates.append((mtime, packet))
        if not candidates:
            return None
        return sorted(candidates, key=lambda item: item[0], reverse=True)[0][1]

    def _latest_submitted_promotion_gate(
        self,
        *,
        session_ref_digest: str | None,
        decision_refs: list[str],
    ) -> dict[str, Any] | None:
        if not self.promotion_gate_dir.is_dir():
            return None
        candidates: list[tuple[float, dict[str, Any]]] = []
        for path in self.promotion_gate_dir.glob("*.json"):
            try:
                packet = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not _is_valid_promotion_gate(packet):
                continue
            if packet.get("session_ref_digest") != session_ref_digest:
                continue
            submitted = (
                packet.get("submitted_control_evidence")
                if isinstance(packet.get("submitted_control_evidence"), dict)
                else {}
            )
            if int(submitted.get("control_count") or 0) <= 0:
                continue
            if list(packet.get("decision_refs") or []) != list(decision_refs):
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                mtime = 0.0
            candidates.append((mtime, packet))
        if not candidates:
            return None
        return sorted(candidates, key=lambda item: item[0], reverse=True)[0][1]


def _is_valid_decision(decision: dict[str, Any]) -> bool:
    return (
        isinstance(decision, dict)
        and decision.get("schema_version") == GENESIS_MEMORY_DECISION_SCHEMA
        and decision.get("surface_id") == GENESIS_MEMORY_DECISION_SURFACE_ID
        and bool(decision.get("decision_id"))
        and decision.get("raw_content_included") is False
        and decision.get("active_production_mutation_allowed") is False
        and decision.get("active_production_mutated") is False
    )


def _is_valid_promotion_gate(packet: dict[str, Any]) -> bool:
    return (
        isinstance(packet, dict)
        and packet.get("schema_version") == "nexusnet-genesis-memory-replay-promotion-gate-v1"
        and packet.get("surface_id") == "genesis-memory-replay-promotion-gate"
        and bool(packet.get("gate_id"))
        and packet.get("raw_content_included") is False
        and packet.get("active_production_mutation_allowed") is False
        and packet.get("active_production_mutated") is False
    )


def _is_valid_promotion_application(packet: dict[str, Any]) -> bool:
    return (
        isinstance(packet, dict)
        and packet.get("schema_version") == "nexusnet-genesis-memory-replay-promotion-application-v1"
        and packet.get("surface_id") == "genesis-memory-replay-promotion-application"
        and bool(packet.get("application_id"))
        and packet.get("raw_content_included") is False
        and packet.get("active_production_mutation_allowed") is False
        and packet.get("active_production_mutated") is False
    )


def _is_valid_promotion_rollback(packet: dict[str, Any]) -> bool:
    return (
        isinstance(packet, dict)
        and packet.get("schema_version") == "nexusnet-genesis-memory-replay-promotion-rollback-v1"
        and packet.get("surface_id") == "genesis-memory-replay-promotion-rollback"
        and bool(packet.get("rollback_id"))
        and packet.get("raw_content_included") is False
        and packet.get("active_production_mutation_allowed") is False
        and packet.get("active_production_mutated") is False
    )


def _is_valid_sandbox_eval(packet: dict[str, Any]) -> bool:
    return (
        isinstance(packet, dict)
        and packet.get("schema_version") == "nexusnet-genesis-memory-replay-sandbox-eval-v1"
        and packet.get("surface_id") == "genesis-memory-replay-sandbox-eval"
        and bool(packet.get("eval_run_id"))
        and packet.get("raw_content_included") is False
        and packet.get("active_production_mutation_allowed") is False
        and packet.get("active_production_mutated") is False
    )


def _replayed(decision: dict[str, Any]) -> dict[str, Any]:
    copy = dict(decision)
    copy["replay_status"] = "replayed"
    return copy


def _route_replay(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for decision in decisions:
        grouped.setdefault(_decision_route(decision), []).append(decision)
    return [
        _route_replay_row(route, items)
        for route, items in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _route_replay_row(route: str, decisions: list[dict[str, Any]]) -> dict[str, Any]:
    blocked = [decision for decision in decisions if decision.get("memory_write_allowed") is not True]
    latest = decisions[0] if decisions else {}
    return {
        "route": route,
        "decision_count": len(decisions),
        "blocked_count": len(blocked),
        "allowed_count": len(decisions) - len(blocked),
        "latest_decision_id": latest.get("decision_id"),
        "latest_decision": latest.get("decision"),
        "memory_write_allowed": bool(decisions) and not blocked,
        "retrieval_truth_allowed": bool(decisions)
        and not blocked
        and any(decision.get("retrieval_truth_allowed") is True for decision in decisions),
        "training_allowed": bool(decisions)
        and not blocked
        and any(decision.get("training_allowed") is True for decision in decisions),
        "decision_refs": _sanitize_refs([decision.get("decision_id") for decision in decisions]),
        "blocked_decision_refs": _sanitize_refs([decision.get("decision_id") for decision in blocked]),
        "raw_content_included": False,
    }


def _compact_decision(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_id": decision.get("decision_id"),
        "route": _decision_route(decision),
        "decision": decision.get("decision"),
        "source": decision.get("source"),
        "source_kind": decision.get("source_kind"),
        "privacy_class": decision.get("privacy_class"),
        "consent_status": decision.get("consent_status"),
        "rights_license_status": decision.get("rights_license_status"),
        "memory_write_allowed": decision.get("memory_write_allowed") is True,
        "retrieval_truth_allowed": decision.get("retrieval_truth_allowed") is True,
        "training_allowed": decision.get("training_allowed") is True,
        "blocked_routes": list(decision.get("blocked_routes") or []),
        "evidence_refs": _sanitize_refs(decision.get("evidence_refs") or []),
        "replay_status": "replayed",
        "raw_content_included": False,
    }


def _promotion_source_binding(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_id": decision.get("decision_id"),
        "source_ref": decision.get("source_ref"),
        "source_kind": decision.get("source_kind"),
        "content_ref": decision.get("content_ref") or decision.get("operation_content_ref"),
        "operation_receipt_id": decision.get("operation_receipt_id"),
        "evidence_checkpoint_id": decision.get("evidence_checkpoint_id"),
        "privacy_class": decision.get("privacy_class"),
        "consent_status": decision.get("consent_status"),
        "rights_license_status": decision.get("rights_license_status"),
        "evidence_refs": _sanitize_refs(
            [
                decision.get("decision_id"),
                decision.get("source_ref"),
                decision.get("content_ref"),
                decision.get("operation_receipt_id"),
                decision.get("operation_content_ref"),
                decision.get("evidence_checkpoint_id"),
            ]
        ),
        "raw_content_included": False,
    }


def _decision_route(decision: dict[str, Any] | None) -> str:
    if not isinstance(decision, dict):
        return "unknown"
    route = decision.get("ingress_route") or decision.get("source") or "unknown"
    text = str(route or "unknown").strip() or "unknown"
    return "redacted-route" if _unsafe_ref(text) else text


def _promotion_targets(
    *,
    replay: dict[str, Any],
    controls_passed: bool,
    blocked_decisions_present: bool,
    replay_observed: bool,
) -> dict[str, dict[str, Any]]:
    memory_truth_state = replay.get("memory_truth_state") if isinstance(replay.get("memory_truth_state"), dict) else {}
    return {
        "memory_truth": _promotion_target(
            base_allowed=memory_truth_state.get("memory_write_allowed") is True,
            controls_passed=controls_passed,
            blocked_decisions_present=blocked_decisions_present,
            replay_observed=replay_observed,
        ),
        "retrieval_truth": _promotion_target(
            base_allowed=memory_truth_state.get("retrieval_truth_allowed") is True,
            controls_passed=controls_passed,
            blocked_decisions_present=blocked_decisions_present,
            replay_observed=replay_observed,
        ),
        "training_material": _promotion_target(
            base_allowed=memory_truth_state.get("training_allowed") is True,
            controls_passed=controls_passed,
            blocked_decisions_present=blocked_decisions_present,
            replay_observed=replay_observed,
        ),
        "graph_truth": _promotion_target(
            base_allowed=memory_truth_state.get("memory_write_allowed") is True
            and memory_truth_state.get("retrieval_truth_allowed") is True,
            controls_passed=controls_passed,
            blocked_decisions_present=blocked_decisions_present,
            replay_observed=replay_observed,
        ),
    }


def _promotion_target(
    *,
    base_allowed: bool,
    controls_passed: bool,
    blocked_decisions_present: bool,
    replay_observed: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    if not replay_observed:
        blockers.append("no_memory_replay_decisions_observed")
    if blocked_decisions_present:
        blockers.append("blocked_private_or_unapproved_decisions_present")
    if not controls_passed:
        blockers.append("eval_sandbox_artifact_trust_rollback_and_governance_controls_required")
    if not base_allowed:
        blockers.append("replay_memory_truth_state_denies_target")
    return {
        "allowed": bool(replay_observed and base_allowed and controls_passed and not blocked_decisions_present),
        "blockers": blockers,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
    }


def _normalize_sandbox_eval_cases(value: Any) -> list[dict[str, Any]]:
    records = [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
    if not records:
        records = [
            {"case_id": "memory-truth-default", "target": "memory_truth", "expected_allowed": True},
            {"case_id": "retrieval-truth-default", "target": "retrieval_truth", "expected_allowed": True},
            {"case_id": "training-material-default", "target": "training_material", "expected_allowed": True},
            {"case_id": "graph-truth-default", "target": "graph_truth", "expected_allowed": True},
        ]
    cases: list[dict[str, Any]] = []
    allowed_targets = {"memory_truth", "retrieval_truth", "training_material", "graph_truth"}
    for index, record in enumerate(records, start=1):
        target = str(record.get("target") or "memory_truth")
        if target not in allowed_targets:
            target = "unknown"
        expected = record.get("expected_allowed")
        expected_allowed = expected if isinstance(expected, bool) else str(expected).lower() != "false"
        case_id = _first_safe_ref(record.get("case_id")) or f"sandbox-eval-case::{index}"
        cases.append(
            {
                "case_id": case_id,
                "target": target,
                "expected_allowed": bool(expected_allowed),
            }
        )
    return cases


def _sandbox_eval_case_result(case: dict[str, Any], *, gate: dict[str, Any]) -> dict[str, Any]:
    target = str(case.get("target") or "unknown")
    promotion_targets = gate.get("promotion_targets") if isinstance(gate.get("promotion_targets"), dict) else {}
    target_state = promotion_targets.get(target) if isinstance(promotion_targets.get(target), dict) else {}
    observed_allowed = target_state.get("allowed") is True
    expected_allowed = case.get("expected_allowed") is True
    seed = json.dumps(
        {
            "gate_id": gate.get("gate_id"),
            "case_id": case.get("case_id"),
            "target": target,
            "expected_allowed": expected_allowed,
            "observed_allowed": observed_allowed,
        },
        sort_keys=True,
    )
    return {
        "case_id": case.get("case_id"),
        "case_ref": f"sandbox-eval-case::{_digest(seed)}",
        "target": target,
        "expected_allowed": expected_allowed,
        "observed_allowed": observed_allowed,
        "passed": observed_allowed == expected_allowed,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def _first_safe_ref(value: Any) -> str | None:
    refs = _sanitize_refs([value] if value else [])
    return refs[0] if refs else None


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


def _looks_private(value: str) -> bool:
    normalized = value.lower()
    return any(marker in normalized for marker in ("secret", "password", "api-key", "apikey", "token"))


def _dedupe(values: list[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and not _unsafe_ref(text) and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _artifact_id(value: str) -> str:
    return str(value or "artifact").replace("::", "--").replace("/", "-").replace("\\", "-")


def _privacy_digest(value: str | None) -> str:
    return "sha256:" + hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
