from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence_spine import GenesisEvidenceSpineService
from .event_spine import GenesisEventSpineService


GENESIS_SELF_REPAIR_SCHEMA = "nexusnet-genesis-self-repair-v1"
GENESIS_SELF_REPAIR_SURFACE_ID = "genesis-self-repair-governed-loop"


class GenesisSelfRepairService:
    """Layer 9 governed self-repair loop fed by the shared Genesis event spine."""

    def __init__(
        self,
        *,
        artifacts_dir: Path | str,
        project_root: Path | str,
        event_spine: GenesisEventSpineService,
        evidence_spine: GenesisEvidenceSpineService,
        federated_outcomes: Any | None = None,
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.project_root = Path(project_root)
        self.event_spine = event_spine
        self.evidence_spine = evidence_spine
        self.federated_outcomes = federated_outcomes
        self.repair_dir = self.artifacts_dir / "genesis" / "self-repair"
        self.proposals_path = self.repair_dir / "proposals.jsonl"
        self.sandbox_evals_path = self.repair_dir / "sandbox-evals.jsonl"
        self.approvals_path = self.repair_dir / "approvals.jsonl"
        self.applications_path = self.repair_dir / "applications.jsonl"
        self.rollbacks_path = self.repair_dir / "rollbacks.jsonl"

    def summary(self, session_id: str | None = None, *, limit: int = 100) -> dict[str, Any]:
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        proposals = self._scoped(self._read_jsonl(self.proposals_path), session_ref_digest)
        sandbox_evals = self._scoped(self._read_jsonl(self.sandbox_evals_path), session_ref_digest)
        approvals = self._scoped(self._read_jsonl(self.approvals_path), session_ref_digest)
        applications = self._scoped(self._read_jsonl(self.applications_path), session_ref_digest)
        rollbacks = self._scoped(self._read_jsonl(self.rollbacks_path), session_ref_digest)
        automatic_degraded_heartbeat_proposals = [
            proposal
            for proposal in proposals
            if proposal.get("proposal_origin") == "automatic-degraded-heartbeat"
        ]
        latest_proposal = proposals[-1] if proposals else {}
        latest_sandbox_eval = sandbox_evals[-1] if sandbox_evals else {}
        latest_approval = approvals[-1] if approvals else {}
        latest_application = applications[-1] if applications else {}
        latest_rollback = rollbacks[-1] if rollbacks else {}
        shared_summary = self.event_spine.summary(session_ref_digest=session_ref_digest, limit=limit)
        event_type_counts = shared_summary.get("event_type_counts") or {}
        self_repair_event_count = sum(
            int(event_type_counts.get(event_type, 0) or 0)
            for event_type in [
                "genesis.self_repair.proposal",
                "genesis.self_repair.sandbox_eval",
                "genesis.self_repair.approval",
                "genesis.self_repair.apply",
                "genesis.self_repair.rollback",
            ]
        )
        status = "live-control-plane" if latest_proposal else "not-observed"
        return {
            "schema_version": GENESIS_SELF_REPAIR_SCHEMA,
            "surface_id": GENESIS_SELF_REPAIR_SURFACE_ID,
            "status": status,
            "honest_status_label": (
                "genesis-layer9-self-repair-admin-approved-loop-live-control-plane"
                if latest_proposal
                else "genesis-layer9-self-repair-admin-approved-loop-not-observed"
            ),
            "authority": "NexusBrain",
            "source": "genesis-shared-event-spine" if latest_proposal else None,
            "session_ref_digest": session_ref_digest,
            "proposal_count": len(proposals),
            "sandbox_eval_count": len(sandbox_evals),
            "approval_count": len(approvals),
            "application_count": len(applications),
            "rollback_count": len(rollbacks),
            "latest_proposal_id": latest_proposal.get("proposal_id"),
            "latest_sandbox_eval_run": latest_sandbox_eval,
            "latest_approval": latest_approval,
            "latest_application": latest_application,
            "latest_rollback": latest_rollback,
            "recent_proposals": [_public_record(record) for record in reversed(proposals[-20:])],
            "shared_event_spine": {
                "schema_version": "nexusnet-genesis-self-repair-shared-event-spine-v1",
                "surface_id": "genesis-self-repair-shared-event-spine",
                "status": shared_summary.get("status"),
                "event_count": self_repair_event_count,
                "latest_event_ref": _latest_shared_event_ref(
                    latest_rollback,
                    latest_application,
                    latest_approval,
                    latest_sandbox_eval,
                    latest_proposal,
                ),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            },
            "automatic_observation": {
                "surface_id": "genesis-self-repair-automatic-observation",
                "status": (
                    "degraded-heartbeat-proposal-observed"
                    if automatic_degraded_heartbeat_proposals
                    else "no-degraded-heartbeat-proposal-observed"
                ),
                "degraded_heartbeat_proposal_count": len(automatic_degraded_heartbeat_proposals),
                "latest_degraded_heartbeat_proposal_id": (
                    automatic_degraded_heartbeat_proposals[-1].get("proposal_id")
                    if automatic_degraded_heartbeat_proposals
                    else None
                ),
                "sandbox_eval_started": False,
                "admin_approval_started": False,
                "safe_apply_started": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
                "raw_content_included": False,
            },
            "safe_apply_governance": {
                "admin_approval_required": True,
                "sandbox_eval_required": True,
                "rollback_required": True,
                "safe_file_scope": ["genesis/safe-files/self-repair/"],
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
                "raw_content_included": False,
            },
            "evidence_refs": _sanitize_refs(
                [
                    latest_proposal.get("proposal_id"),
                    latest_proposal.get("source_event_ref"),
                    latest_proposal.get("evidence_spine_proposal_id"),
                    latest_sandbox_eval.get("eval_run_id"),
                    latest_approval.get("approval_ref"),
                    latest_application.get("apply_id"),
                    latest_rollback.get("rollback_id"),
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-genesis-self-repair-ids-digests-statuses-event-refs-and-safe-file-refs-only-"
                "no-prompts-outputs-session-ids-admin-identities-local-paths-or-raw-content"
            ),
            "mutation_boundary": "admin-approved-sandbox-evaluated-shadow-safe-file-apply-with-rollback-only",
        }

    def propose_from_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        session_id = str(payload.get("session_id") or "")
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        event_ref = _safe_ref(payload.get("event_ref"))
        if not event_ref:
            raise ValueError("event_ref is required")
        event = self._find_event(event_ref=event_ref, session_id=session_id or None)
        target_ref = _safe_target_ref(str(payload.get("target_ref") or ""))
        repair_objective = str(payload.get("repair_objective") or "restore governed runtime posture")
        proposal_origin = _proposal_origin(payload.get("proposal_origin"))
        requested_proposal_id = _safe_ref(payload.get("proposal_id"))
        if requested_proposal_id:
            existing = next(
                (
                    proposal
                    for proposal in self._read_jsonl(self.proposals_path)
                    if str(proposal.get("proposal_id") or "") == requested_proposal_id
                ),
                None,
            )
            if existing is not None:
                replayed = _public_record(existing)
                replayed["status"] = "proposal-replayed"
                replayed["proposal_status"] = str(existing.get("status") or "proposal")
                return replayed
        created_at = _utcnow()
        proposal_id = requested_proposal_id or f"genesis-self-repair::{_digest('|'.join([event_ref, target_ref, created_at]))}"
        safe_content = {
            "schema_version": "nexusnet-genesis-self-repair-safe-file-v1",
            "surface_id": "genesis-self-repair-safe-file",
            "repair_status": "shadow-safe-file-applied",
            "self_repair_proposal_id": proposal_id,
            "source_event_ref": event_ref,
            "source_event_type": event.get("event_type"),
            "source_event_correlation_ref": event.get("correlation_ref"),
            "source_surface_id": event.get("source_surface_id"),
            "session_ref_digest": event.get("session_ref_digest") or session_ref_digest,
            "repair_objective_ref": f"repair-objective::{_digest(repair_objective)}",
            "safe_file_ref": target_ref,
            "sandbox_eval_required": True,
            "admin_approval_required": True,
            "rollback_required": True,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        evidence_proposal = self.evidence_spine.propose_safe_file(
            {
                "session_id": session_id,
                "target_ref": target_ref,
                "content": json.dumps(safe_content, sort_keys=True),
                "reason": "genesis-self-repair-shadow-safe-file",
            }
        )
        shared_event_spine = self.event_spine.publish_event(
            event_type="genesis.self_repair.proposal",
            source_surface_id=GENESIS_SELF_REPAIR_SURFACE_ID,
            correlation_ref=proposal_id,
            session_ref_digest=event.get("session_ref_digest") or session_ref_digest,
            source_hive_run_ref=event.get("source_hive_run_ref"),
            heartbeat_record_id=event.get("heartbeat_record_id"),
            privacy_label="sanitized-genesis-self-repair-proposal",
            artifact_refs=[
                event_ref,
                target_ref,
                evidence_proposal.get("proposal_id"),
                event.get("correlation_ref"),
            ],
            planes=["self_repair", "governance", "event_spine", "sandbox", "rollback"],
            priority_trails=[
                {
                    "topic": "genesis-self-repair",
                    "strength": 1.0,
                    "artifact_ref": event_ref,
                }
            ],
        )
        proposal = {
            "schema_version": "nexusnet-genesis-self-repair-proposal-v1",
            "surface_id": "genesis-self-repair-proposal",
            "proposal_id": proposal_id,
            "status": "proposal",
            "proposal_origin": proposal_origin,
            "session_ref_digest": event.get("session_ref_digest") or session_ref_digest,
            "source_event_ref": event_ref,
            "source_event_type": str(event.get("event_type") or "unknown"),
            "source_event_correlation_ref": event.get("correlation_ref"),
            "target_ref": target_ref,
            "repair_objective_ref": safe_content["repair_objective_ref"],
            "evidence_spine_proposal_id": evidence_proposal.get("proposal_id"),
            "evidence_spine_proposal": evidence_proposal,
            "shared_event_spine": shared_event_spine,
            "created_at": created_at,
            "admin_approval_required": True,
            "sandbox_eval_required": True,
            "safe_apply_allowed": False,
            "rollback_required": True,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "evidence_refs": _sanitize_refs(
                [
                    proposal_id,
                    event_ref,
                    evidence_proposal.get("proposal_id"),
                    shared_event_spine.get("event_ref"),
                    target_ref,
                ]
            ),
        }
        proposal["federated_outcome_packet"] = self._record_federated_outcome(
            outcome_type="self_repair_proposed",
            session_id=session_id,
            session_ref_digest=proposal.get("session_ref_digest"),
            source_event_ref=proposal.get("source_event_ref"),
            source_event_type=proposal.get("source_event_type"),
            linked_self_repair_proposal_id=proposal_id,
            evidence_refs=proposal.get("evidence_refs"),
        )
        self._append_jsonl(self.proposals_path, proposal)
        return _public_record(proposal)

    def propose_from_degraded_heartbeat(
        self,
        *,
        session_id: str | None,
        heartbeat_record: dict[str, Any],
    ) -> dict[str, Any]:
        """Create one replay-safe proposal for a sanitized degraded heartbeat only."""
        if not isinstance(heartbeat_record, dict):
            return _automatic_observation("not-eligible", reason="missing-heartbeat-record")
        if heartbeat_record.get("status") != "degraded":
            return _automatic_observation("not-eligible", reason="heartbeat-not-degraded")
        if heartbeat_record.get("raw_content_included") is not False:
            return _automatic_observation("not-eligible", reason="heartbeat-not-sanitized")
        if heartbeat_record.get("active_production_mutation_allowed") is not False:
            return _automatic_observation("not-eligible", reason="heartbeat-allows-production-mutation")
        if heartbeat_record.get("active_production_mutated") is not False:
            return _automatic_observation("not-eligible", reason="heartbeat-mutated-production")

        shared_event = heartbeat_record.get("shared_event_spine")
        event_ref = _safe_ref(shared_event.get("event_ref") if isinstance(shared_event, dict) else None)
        if not event_ref:
            return _automatic_observation("not-eligible", reason="missing-heartbeat-event-ref")
        event = self._find_event(event_ref=event_ref, session_id=session_id)
        if event.get("event_type") != "genesis.heartbeat.recorded":
            return _automatic_observation("not-eligible", reason="unexpected-heartbeat-event-type")
        if str(event.get("heartbeat_record_id") or "") != str(heartbeat_record.get("record_id") or ""):
            return _automatic_observation("not-eligible", reason="heartbeat-event-mismatch")

        event_digest = _digest(event_ref)
        proposal_id = f"genesis-self-repair::automatic-degraded-heartbeat::{event_digest}"
        proposal = self.propose_from_event(
            {
                "session_id": session_id or "",
                "event_ref": event_ref,
                "target_ref": f"genesis/safe-files/self-repair/automatic-degraded-heartbeat-{event_digest}.json",
                "repair_objective": "restore degraded governed runtime posture after a sanitized heartbeat failure",
                "proposal_id": proposal_id,
                "proposal_origin": "automatic-degraded-heartbeat",
            }
        )
        return proposal

    def proposal_by_id(self, proposal_id: str) -> dict[str, Any]:
        return _public_record(self._find(self.proposals_path, "proposal_id", proposal_id))

    def sandbox_eval(self, proposal_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        proposal = self._find(self.proposals_path, "proposal_id", proposal_id)
        cases = _normalize_eval_cases(payload.get("eval_cases"))
        if not cases:
            raise ValueError("eval_cases are required")
        failed = [
            case
            for case in cases
            if case.get("passed") is not True
        ]
        status = "passed" if not failed else "failed"
        eval_run_id = f"genesis-self-repair-eval::{_digest('|'.join([proposal_id, json.dumps(cases, sort_keys=True), _utcnow()]))}"
        shared_event_spine = self.event_spine.publish_event(
            event_type="genesis.self_repair.sandbox_eval",
            source_surface_id=GENESIS_SELF_REPAIR_SURFACE_ID,
            correlation_ref=eval_run_id,
            session_ref_digest=proposal.get("session_ref_digest"),
            heartbeat_record_id=None,
            privacy_label="sanitized-genesis-self-repair-sandbox-eval",
            artifact_refs=[
                proposal_id,
                proposal.get("source_event_ref"),
                proposal.get("evidence_spine_proposal_id"),
                payload.get("artifact_trust_ref"),
                payload.get("rollback_proof_ref"),
            ],
            planes=["self_repair", "closed_eval", "sandbox", "governance"],
            priority_trails=[
                {
                    "topic": "genesis-self-repair-sandbox-eval",
                    "strength": 1.0,
                    "artifact_ref": proposal_id,
                }
            ],
        )
        record = {
            "schema_version": "nexusnet-genesis-self-repair-sandbox-eval-v1",
            "surface_id": "genesis-self-repair-sandbox-eval",
            "eval_run_id": eval_run_id,
            "proposal_id": proposal_id,
            "status": status,
            "passed": status == "passed",
            "session_ref_digest": proposal.get("session_ref_digest"),
            "source_event_ref": proposal.get("source_event_ref"),
            "case_count": len(cases),
            "failed_count": len(failed),
            "eval_cases": cases,
            "sandbox_tier": "closed-deterministic",
            "artifact_trust_ref": _safe_ref(payload.get("artifact_trust_ref")),
            "rollback_proof_ref": _safe_ref(payload.get("rollback_proof_ref")),
            "shared_event_spine": shared_event_spine,
            "created_at": _utcnow(),
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "evidence_refs": _sanitize_refs(
                [
                    proposal_id,
                    proposal.get("source_event_ref"),
                    proposal.get("evidence_spine_proposal_id"),
                    shared_event_spine.get("event_ref"),
                    payload.get("artifact_trust_ref"),
                    payload.get("rollback_proof_ref"),
                ]
            ),
        }
        record["federated_outcome_packet"] = self._record_federated_outcome(
            outcome_type=(
                "self_repair_sandbox_eval_passed"
                if status == "passed"
                else "self_repair_sandbox_eval_failed"
            ),
            session_ref_digest=proposal.get("session_ref_digest"),
            source_event_ref=proposal.get("source_event_ref"),
            source_event_type=proposal.get("source_event_type"),
            linked_self_repair_proposal_id=proposal_id,
            sandbox_eval_run_id=eval_run_id,
            evidence_refs=record.get("evidence_refs"),
        )
        self._append_jsonl(self.sandbox_evals_path, record)
        return record

    def approve(self, proposal_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        proposal = self._find(self.proposals_path, "proposal_id", proposal_id)
        self._latest_passing_eval(proposal_id)
        evidence_approval = self.evidence_spine.approve(
            str(proposal.get("evidence_spine_proposal_id") or ""),
            payload,
        )
        approved_by = str(payload.get("approved_by") or "admin")
        approval_ref = _safe_ref(payload.get("approval_ref")) or f"admin-approval::{_digest(proposal_id)}"
        shared_event_spine = self.event_spine.publish_event(
            event_type="genesis.self_repair.approval",
            source_surface_id=GENESIS_SELF_REPAIR_SURFACE_ID,
            correlation_ref=approval_ref,
            session_ref_digest=proposal.get("session_ref_digest"),
            privacy_label="sanitized-genesis-self-repair-admin-approval",
            artifact_refs=[
                proposal_id,
                proposal.get("source_event_ref"),
                proposal.get("evidence_spine_proposal_id"),
                evidence_approval.get("approval_ref"),
            ],
            planes=["self_repair", "admin_approval", "governance"],
        )
        record = {
            "schema_version": "nexusnet-genesis-self-repair-admin-approval-v1",
            "surface_id": "genesis-self-repair-admin-approval",
            "proposal_id": proposal_id,
            "status": "admin-approved",
            "operator_approved": True,
            "session_ref_digest": proposal.get("session_ref_digest"),
            "approval_ref": approval_ref,
            "approver_digest": f"sha256:{_sha256(approved_by)[:16]}",
            "evidence_spine_approval": evidence_approval,
            "shared_event_spine": shared_event_spine,
            "approved_at": _utcnow(),
            "safe_apply_allowed": True,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "evidence_refs": _sanitize_refs(
                [
                    proposal_id,
                    proposal.get("source_event_ref"),
                    approval_ref,
                    evidence_approval.get("approval_ref"),
                    shared_event_spine.get("event_ref"),
                ]
            ),
        }
        self._append_jsonl(self.approvals_path, record)
        return record

    def apply(self, proposal_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        proposal = self._find(self.proposals_path, "proposal_id", proposal_id)
        sandbox_eval = self._latest_passing_eval(proposal_id)
        approval = self._latest_approval(proposal_id)
        immune_governance = getattr(self, "immune_governance", None)
        immune_decision = (
            immune_governance.require_decision(
                decision_id=payload.get("immune_governance_decision_id"),
                candidate_ref=proposal_id,
                candidate_kind="self-repair-safe-apply",
            )
            if immune_governance is not None
            else None
        )
        evidence_apply = self.evidence_spine.apply(
            str(proposal.get("evidence_spine_proposal_id") or ""),
            payload,
        )
        shared_event_spine = self.event_spine.publish_event(
            event_type="genesis.self_repair.apply",
            source_surface_id=GENESIS_SELF_REPAIR_SURFACE_ID,
            correlation_ref=str(evidence_apply.get("apply_id") or proposal_id),
            session_ref_digest=proposal.get("session_ref_digest"),
            privacy_label="sanitized-genesis-self-repair-apply",
            artifact_refs=[
                proposal_id,
                proposal.get("source_event_ref"),
                approval.get("approval_ref"),
                sandbox_eval.get("eval_run_id"),
                (immune_decision or {}).get("decision_id"),
                evidence_apply.get("apply_id"),
                evidence_apply.get("rollback_ref"),
                evidence_apply.get("safe_file_ref"),
            ],
            planes=["self_repair", "safe_apply", "rollback", "governance"],
        )
        record = {
            "schema_version": "nexusnet-genesis-self-repair-application-v1",
            "surface_id": "genesis-self-repair-application",
            "proposal_id": proposal_id,
            "apply_id": evidence_apply.get("apply_id"),
            "status": evidence_apply.get("status"),
            "self_repair_status": "applied",
            "session_ref_digest": proposal.get("session_ref_digest"),
            "source_event_ref": proposal.get("source_event_ref"),
            "sandbox_eval_run_id": sandbox_eval.get("eval_run_id"),
            "approval_ref": approval.get("approval_ref"),
            "immune_governance_decision": immune_decision,
            "safe_file_ref": evidence_apply.get("safe_file_ref"),
            "rollback_ref": evidence_apply.get("rollback_ref"),
            "evidence_spine_apply": evidence_apply,
            "shared_event_spine": shared_event_spine,
            "applied_at": _utcnow(),
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "evidence_refs": _sanitize_refs(
                [
                    proposal_id,
                    proposal.get("source_event_ref"),
                    sandbox_eval.get("eval_run_id"),
                    approval.get("approval_ref"),
                    (immune_decision or {}).get("decision_id"),
                    evidence_apply.get("apply_id"),
                    evidence_apply.get("rollback_ref"),
                    shared_event_spine.get("event_ref"),
                ]
            ),
        }
        record["federated_outcome_packet"] = self._record_federated_outcome(
            outcome_type="self_repair_applied",
            session_ref_digest=proposal.get("session_ref_digest"),
            source_event_ref=proposal.get("source_event_ref"),
            source_event_type=proposal.get("source_event_type"),
            linked_self_repair_proposal_id=proposal_id,
            sandbox_eval_run_id=sandbox_eval.get("eval_run_id"),
            apply_id=evidence_apply.get("apply_id"),
            evidence_refs=record.get("evidence_refs"),
        )
        self._append_jsonl(self.applications_path, record)
        return record

    def rollback(self, proposal_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        proposal = self._find(self.proposals_path, "proposal_id", proposal_id)
        application = self._find(self.applications_path, "proposal_id", proposal_id, latest=True)
        evidence_rollback = self.evidence_spine.rollback(
            str(proposal.get("evidence_spine_proposal_id") or ""),
            payload,
        )
        shared_event_spine = self.event_spine.publish_event(
            event_type="genesis.self_repair.rollback",
            source_surface_id=GENESIS_SELF_REPAIR_SURFACE_ID,
            correlation_ref=str(evidence_rollback.get("rollback_id") or proposal_id),
            session_ref_digest=proposal.get("session_ref_digest"),
            privacy_label="sanitized-genesis-self-repair-rollback",
            artifact_refs=[
                proposal_id,
                proposal.get("source_event_ref"),
                application.get("apply_id"),
                evidence_rollback.get("rollback_id"),
                evidence_rollback.get("safe_file_ref"),
            ],
            planes=["self_repair", "rollback", "governance"],
        )
        record = {
            "schema_version": "nexusnet-genesis-self-repair-rollback-v1",
            "surface_id": "genesis-self-repair-rollback",
            "proposal_id": proposal_id,
            "rollback_id": evidence_rollback.get("rollback_id"),
            "apply_id": application.get("apply_id"),
            "status": evidence_rollback.get("status"),
            "self_repair_status": "rolled-back",
            "session_ref_digest": proposal.get("session_ref_digest"),
            "source_event_ref": proposal.get("source_event_ref"),
            "safe_file_ref": evidence_rollback.get("safe_file_ref"),
            "rollback_restored": evidence_rollback.get("rollback_restored") is True,
            "evidence_spine_rollback": evidence_rollback,
            "shared_event_spine": shared_event_spine,
            "rolled_back_at": _utcnow(),
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "evidence_refs": _sanitize_refs(
                [
                    proposal_id,
                    proposal.get("source_event_ref"),
                    application.get("apply_id"),
                    evidence_rollback.get("rollback_id"),
                    shared_event_spine.get("event_ref"),
                ]
            ),
        }
        record["federated_outcome_packet"] = self._record_federated_outcome(
            outcome_type="self_repair_rolled_back",
            session_ref_digest=proposal.get("session_ref_digest"),
            source_event_ref=proposal.get("source_event_ref"),
            source_event_type=proposal.get("source_event_type"),
            linked_self_repair_proposal_id=proposal_id,
            apply_id=application.get("apply_id"),
            rollback_id=evidence_rollback.get("rollback_id"),
            evidence_refs=record.get("evidence_refs"),
        )
        self._append_jsonl(self.rollbacks_path, record)
        return record

    def _record_federated_outcome(self, **payload: Any) -> dict[str, Any]:
        if not hasattr(self.federated_outcomes, "record_outcome"):
            return {
                "schema_version": "nexusnet-genesis-federated-outcome-packet-v1",
                "surface_id": "genesis-federated-outcome-packet",
                "status": "not-configured",
                "raw_content_included": False,
                "contains_personal_data": False,
                "active_production_mutation_allowed": False,
            }
        return self.federated_outcomes.record_outcome(
            source_surface_id=GENESIS_SELF_REPAIR_SURFACE_ID,
            status="self-repair-outcome-recorded",
            **payload,
        )

    def _find_event(self, *, event_ref: str, session_id: str | None = None) -> dict[str, Any]:
        summary = self.event_spine.summary(session_id=session_id, limit=500)
        for event in summary.get("events") or []:
            if str(event.get("event_ref") or "") == event_ref:
                if event.get("raw_content_included") is not False:
                    raise ValueError("source event must be sanitized")
                if event.get("active_production_mutation_allowed") is not False:
                    raise ValueError("source event must not allow production mutation")
                return event
        raise KeyError(event_ref)

    def _latest_passing_eval(self, proposal_id: str) -> dict[str, Any]:
        evals = [
            record
            for record in self._read_jsonl(self.sandbox_evals_path)
            if str(record.get("proposal_id") or "") == proposal_id
        ]
        if not evals:
            raise ValueError("passing sandbox eval is required before apply")
        latest = evals[-1]
        if latest.get("passed") is not True or latest.get("status") != "passed":
            raise ValueError("passing sandbox eval is required before apply")
        return latest

    def _latest_approval(self, proposal_id: str) -> dict[str, Any]:
        approvals = [
            record
            for record in self._read_jsonl(self.approvals_path)
            if str(record.get("proposal_id") or "") == proposal_id
        ]
        if not approvals:
            raise ValueError("admin approval is required before apply")
        latest = approvals[-1]
        if latest.get("operator_approved") is not True:
            raise ValueError("admin approval is required before apply")
        return latest

    def _scoped(self, records: list[dict[str, Any]], session_ref_digest: str | None) -> list[dict[str, Any]]:
        if not session_ref_digest:
            return records
        return [
            record
            for record in records
            if str(record.get("session_ref_digest") or "") == session_ref_digest
        ]

    def _append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        records: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                records.append(item)
        return records

    def _find(self, path: Path, key: str, value: str, *, latest: bool = False) -> dict[str, Any]:
        records = [
            record
            for record in self._read_jsonl(path)
            if str(record.get(key) or "") == value
        ]
        if not records:
            raise KeyError(value)
        return records[-1] if latest else records[0]


def _normalize_eval_cases(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    cases: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        expected = str(item.get("expected") or "").strip()
        case_id = _safe_ref(item.get("case_id")) or f"case::{_digest(expected)}"
        cases.append(
            {
                "case_id": case_id,
                "expected_ref": f"expected::{_digest(expected)}",
                "passed": bool(expected),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            }
        )
    return cases


def _latest_shared_event_ref(*records: dict[str, Any]) -> str | None:
    for record in records:
        shared = record.get("shared_event_spine") if isinstance(record, dict) else None
        if isinstance(shared, dict) and shared.get("event_ref"):
            return str(shared.get("event_ref"))
    return None


def _safe_target_ref(target_ref: str) -> str:
    normalized = target_ref.strip().replace("\\", "/")
    if (
        not normalized.startswith("genesis/safe-files/self-repair/")
        or ".." in normalized
        or ":" in normalized
        or normalized.endswith("/")
    ):
        raise ValueError("target_ref must stay within genesis/safe-files/self-repair/")
    return normalized


def _proposal_origin(value: Any) -> str:
    origin = str(value or "manual-event").strip().lower()
    if origin not in {"automatic-degraded-heartbeat", "manual-event"}:
        return "manual-event"
    return origin


def _automatic_observation(status: str, *, reason: str) -> dict[str, Any]:
    return {
        "surface_id": "genesis-self-repair-automatic-observation",
        "status": status,
        "reason": reason,
        "proposal_id": None,
        "admin_approval_required": True,
        "sandbox_eval_required": True,
        "safe_apply_allowed": False,
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
    seen: set[str] = set()
    result: list[str] = []
    for item in candidates:
        ref = _safe_ref(item)
        if ref and ref not in seen:
            seen.add(ref)
            result.append(ref)
    return result


def _safe_ref(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    normalized = text.lower()
    if (
        not text
        or ".." in text
        or ":\\" in text
        or "secret" in normalized
        or "token" in normalized
        or "password" in normalized
        or "api-key" in normalized
        or "apikey" in normalized
        or "runtime/test-fixtures" in normalized
    ):
        return ""
    return text[:220]


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.items()
        if key not in {"proposed_content", "previous_content"}
    }


def _privacy_digest(value: str | None) -> str:
    return "sha256:" + hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _sha256(value: str | None) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
