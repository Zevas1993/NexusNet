from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .event_spine import GenesisEventSpineService
from .heartbeat import GenesisHeartbeatService


GENESIS_EVIDENCE_SPINE_SCHEMA = "nexusnet-genesis-evidence-spine-v1"
GENESIS_EVIDENCE_SPINE_SURFACE_ID = "genesis-evidence-checkpoint-spine"
GENESIS_SAFE_FILE_PREFIX = "genesis/safe-files/"


class GenesisEvidenceSpineService:
    """Layer 5 evidence, checkpoint, safe-apply, and rollback spine."""

    def __init__(
        self,
        *,
        artifacts_dir: Path | str,
        project_root: Path | str,
        heartbeat_service: GenesisHeartbeatService,
        event_spine: GenesisEventSpineService | None = None,
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.project_root = Path(project_root)
        self.heartbeat_service = heartbeat_service
        self.event_spine = event_spine or GenesisEventSpineService(
            artifacts_dir=self.artifacts_dir,
            project_root=self.project_root,
        )
        self.spine_dir = self.artifacts_dir / "genesis" / "evidence-spine"
        self.checkpoints_dir = self.spine_dir / "checkpoints"
        self.operation_receipts_dir = self.spine_dir / "operation-receipts"
        self.proposals_path = self.spine_dir / "proposals.jsonl"
        self.approvals_path = self.spine_dir / "approvals.jsonl"
        self.applied_path = self.spine_dir / "applied.jsonl"
        self.rollbacks_path = self.spine_dir / "rollbacks.jsonl"
        self.safe_files_dir = self.artifacts_dir / "genesis" / "safe-files"

    def summary(self, session_id: str | None = None) -> dict[str, Any]:
        heartbeat = self.heartbeat_service.summary(session_id=session_id)
        latest_record = heartbeat.get("records", [None])[0] if heartbeat.get("records") else None
        checkpoint = self._ensure_checkpoint(latest_record) if isinstance(latest_record, dict) else self._empty_checkpoint()
        operation_receipt = (
            self._ensure_operation_receipt(latest_record, checkpoint)
            if isinstance(latest_record, dict)
            else self._empty_operation_receipt()
        )
        shared_checkpoint_event = (
            self._publish_checkpoint_event(latest_record, checkpoint, operation_receipt)
            if isinstance(latest_record, dict) and checkpoint.get("checkpoint_id")
            else {}
        )
        if shared_checkpoint_event:
            checkpoint = dict(checkpoint)
            checkpoint["shared_event_spine"] = shared_checkpoint_event
        trust_records = self._artifact_trust_records(latest_record, checkpoint, operation_receipt)
        proposals = self._read_jsonl(self.proposals_path)
        approvals = self._read_jsonl(self.approvals_path)
        applied = self._read_jsonl(self.applied_path)
        rollbacks = self._read_jsonl(self.rollbacks_path)
        latest_proposal = proposals[-1] if proposals else {}
        latest_apply = applied[-1] if applied else {}
        latest_rollback = rollbacks[-1] if rollbacks else {}
        status = "live-control-plane" if latest_record else "not-observed"
        return {
            "schema_version": GENESIS_EVIDENCE_SPINE_SCHEMA,
            "surface_id": GENESIS_EVIDENCE_SPINE_SURFACE_ID,
            "status": status,
            "honest_status_label": (
                "layer5-evidence-checkpoint-spine-live-control-plane"
                if latest_record
                else "layer5-evidence-checkpoint-spine-not-observed"
            ),
            "authority": "NexusBrain",
            "source": "genesis-heartbeat-chain" if latest_record else None,
            "latest_heartbeat_record_id": latest_record.get("record_id") if latest_record else None,
            "checkpoint_snapshot": checkpoint,
            "operation_receipt": operation_receipt,
            "content_addressed_evidence_refs": _dedupe(
                [record.get("content_ref") for record in trust_records]
            ),
            "artifact_trust_registry": {
                "schema_version": "nexusnet-genesis-artifact-trust-registry-v1",
                "surface_id": "genesis-artifact-trust-registry",
                "trust_status": "trusted" if trust_records else "not-observed",
                "trusted_ref_count": len(trust_records),
                "records": trust_records,
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            },
            "safe_apply_governance": {
                "schema_version": "nexusnet-genesis-safe-apply-governance-v1",
                "surface_id": "genesis-safe-apply-governance",
                "proposal_count": len(proposals),
                "approval_count": len(approvals),
                "apply_count": len(applied),
                "rollback_count": len(rollbacks),
                "latest_proposal_id": latest_proposal.get("proposal_id"),
                "latest_apply_status": latest_apply.get("status"),
                "latest_rollback_status": latest_rollback.get("status"),
                "admin_approval_required": True,
                "sandbox_eval_required": True,
                "rollback_required": True,
                "safe_file_scope": [GENESIS_SAFE_FILE_PREFIX],
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
                "raw_content_included": False,
            },
            "shared_event_spine": {
                "schema_version": "nexusnet-genesis-evidence-shared-event-spine-v1",
                "surface_id": "genesis-evidence-shared-event-spine",
                "status": "live-control-plane" if shared_checkpoint_event else "not-observed",
                "latest_event_ref": shared_checkpoint_event.get("event_ref"),
                "source_checkpoint_id": checkpoint.get("checkpoint_id"),
                "operation_receipt_id": operation_receipt.get("operation_receipt_id"),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            },
            "evidence_refs": _dedupe(
                [
                    heartbeat.get("artifact_ref"),
                    latest_record.get("record_id") if latest_record else None,
                    checkpoint.get("checkpoint_id"),
                    operation_receipt.get("operation_receipt_id"),
                    operation_receipt.get("content_ref"),
                    shared_checkpoint_event.get("event_ref") if shared_checkpoint_event else None,
                    latest_proposal.get("proposal_id"),
                    latest_apply.get("apply_id"),
                    latest_rollback.get("rollback_id"),
                    *[record.get("content_ref") for record in trust_records],
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-layer5-evidence-ids-digests-counts-statuses-and-artifact-refs-only-"
                "no-prompts-outputs-session-ids-approver-text-or-local-paths"
            ),
            "mutation_boundary": "safe-file-shadow-apply-only-under-artifacts-genesis-safe-files-with-rollback",
        }

    def record_runtime_transaction(self, *, session_id: str | None) -> dict[str, Any]:
        evidence = self.summary(session_id=session_id)
        operation_receipt = (
            evidence.get("operation_receipt")
            if isinstance(evidence.get("operation_receipt"), dict)
            else {}
        )
        checkpoint = (
            evidence.get("checkpoint_snapshot")
            if isinstance(evidence.get("checkpoint_snapshot"), dict)
            else {}
        )
        return {
            "schema_version": "nexusnet-genesis-runtime-evidence-bridge-v1",
            "surface_id": "genesis-runtime-evidence-bridge",
            "status": operation_receipt.get("status") or "not-observed",
            "operation_receipt_id": operation_receipt.get("operation_receipt_id"),
            "operation_content_ref": operation_receipt.get("content_ref"),
            "checkpoint_id": checkpoint.get("checkpoint_id"),
            "replay_status": operation_receipt.get("replay_status"),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def propose_safe_file(self, payload: dict[str, Any]) -> dict[str, Any]:
        session_id = str(payload.get("session_id") or "")
        target_ref = _safe_target_ref(str(payload.get("target_ref") or ""))
        content = str(payload.get("content") or "")
        if not content:
            raise ValueError("content is required")
        checkpoint = self.summary(session_id=session_id).get("checkpoint_snapshot") or {}
        created_at = _utcnow()
        proposal_id = f"genesis-proposal::{_digest('|'.join([target_ref, _sha256(content), created_at]))}"
        proposal = {
            "schema_version": "nexusnet-genesis-safe-file-proposal-v1",
            "surface_id": "genesis-safe-file-proposal",
            "proposal_id": proposal_id,
            "status": "proposal",
            "target_ref": target_ref,
            "content_sha256": f"sha256:{_sha256(content)}",
            "proposed_content": content,
            "created_at": created_at,
            "checkpoint_id": checkpoint.get("checkpoint_id"),
            "admin_approval_required": True,
            "safe_apply_allowed": False,
            "rollback_plan": {
                "surface_id": "genesis-safe-file-rollback-plan",
                "rollback_available": True,
                "checkpoint_ref": checkpoint.get("checkpoint_id"),
                "restore_strategy": "restore-previous-safe-file-content-or-delete-new-file",
                "raw_content_included": False,
            },
            "evidence_refs": _dedupe([checkpoint.get("checkpoint_id"), checkpoint.get("content_ref")]),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        self._append_jsonl(self.proposals_path, proposal)
        return _public_proposal(proposal)

    def approve(self, proposal_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        proposal = self._find(self.proposals_path, "proposal_id", proposal_id)
        approved_by = str(payload.get("approved_by") or "admin")
        approval_ref = str(payload.get("approval_ref") or f"admin-approval::{_digest(proposal_id)}")
        approval = {
            "schema_version": "nexusnet-genesis-admin-approval-v1",
            "surface_id": "genesis-admin-approval",
            "proposal_id": proposal_id,
            "status": "admin-approved",
            "operator_approved": True,
            "approval_ref": _safe_ref(approval_ref),
            "approver_digest": f"sha256:{_sha256(approved_by)[:16]}",
            "approved_at": _utcnow(),
            "safe_apply_allowed": True,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "evidence_refs": _dedupe([proposal.get("proposal_id"), proposal.get("checkpoint_id"), approval_ref]),
        }
        self._append_jsonl(self.approvals_path, approval)
        return approval

    def apply(self, proposal_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        proposal = self._find(self.proposals_path, "proposal_id", proposal_id)
        approval = self._find(self.approvals_path, "proposal_id", proposal_id)
        if approval.get("operator_approved") is not True:
            raise ValueError("admin approval is required before apply")
        test_results = _normalize_test_results(payload.get("test_results"))
        if not test_results or any(result["passed"] is not True or result["failure_count"] != 0 for result in test_results):
            raise ValueError("passing sandbox test evidence is required before apply")
        target_ref = _safe_target_ref(str(proposal.get("target_ref") or ""))
        safe_file = self._safe_file_path(target_ref)
        safe_file.parent.mkdir(parents=True, exist_ok=True)
        previous_content = safe_file.read_text(encoding="utf-8") if safe_file.is_file() else None
        content = str(proposal.get("proposed_content") or "")
        safe_file.write_text(content, encoding="utf-8")
        apply_id = f"genesis-apply::{_digest('|'.join([proposal_id, _sha256(content), _utcnow()]))}"
        rollback_ref = f"genesis-rollback::{_digest(apply_id)}"
        applied = {
            "schema_version": "nexusnet-genesis-safe-file-apply-v1",
            "surface_id": "genesis-safe-file-apply",
            "apply_id": apply_id,
            "proposal_id": proposal_id,
            "status": "applied-shadow-safe-file",
            "safe_file_ref": target_ref,
            "content_sha256": proposal.get("content_sha256"),
            "previous_content": previous_content,
            "previous_content_sha256": f"sha256:{_sha256(previous_content)}" if previous_content is not None else None,
            "rollback_ref": rollback_ref,
            "test_results": test_results,
            "applied_at": _utcnow(),
            "active_production_mutated": False,
            "active_production_mutation_allowed": False,
            "raw_content_included": False,
            "evidence_refs": _dedupe([proposal_id, approval.get("approval_ref"), rollback_ref]),
        }
        self._append_jsonl(self.applied_path, applied)
        return _public_apply(applied)

    def rollback(self, proposal_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        applied = self._find(self.applied_path, "proposal_id", proposal_id, latest=True)
        target_ref = _safe_target_ref(str(applied.get("safe_file_ref") or ""))
        safe_file = self._safe_file_path(target_ref)
        previous_content = applied.get("previous_content")
        if previous_content is None:
            if safe_file.is_file():
                safe_file.unlink()
            rollback_restored = True
        else:
            safe_file.parent.mkdir(parents=True, exist_ok=True)
            safe_file.write_text(str(previous_content), encoding="utf-8")
            rollback_restored = True
        rollback = {
            "schema_version": "nexusnet-genesis-safe-file-rollback-v1",
            "surface_id": "genesis-safe-file-rollback",
            "rollback_id": str(applied.get("rollback_ref") or f"genesis-rollback::{_digest(proposal_id)}"),
            "proposal_id": proposal_id,
            "apply_id": applied.get("apply_id"),
            "status": "rolled-back",
            "reason_ref": f"rollback-reason::{_digest(str(payload.get('reason') or 'operator-requested'))}",
            "safe_file_ref": target_ref,
            "rollback_restored": rollback_restored,
            "rolled_back_at": _utcnow(),
            "active_production_mutated": False,
            "active_production_mutation_allowed": False,
            "raw_content_included": False,
            "evidence_refs": _dedupe([applied.get("apply_id"), applied.get("rollback_ref")]),
        }
        self._append_jsonl(self.rollbacks_path, rollback)
        return rollback

    def _ensure_checkpoint(self, heartbeat_record: dict[str, Any]) -> dict[str, Any]:
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        source_record_id = str(heartbeat_record.get("record_id") or "")
        seed = json.dumps(
            {
                "record_id": source_record_id,
                "source_hive_run_id": heartbeat_record.get("source_hive_run_id"),
                "project_heartbeat_id": heartbeat_record.get("project_heartbeat_id"),
                "runtime_growth_receipt_id": heartbeat_record.get("runtime_growth_receipt_id"),
                "federated_packet_id": heartbeat_record.get("federated_packet_id"),
                "checkpoint_id": heartbeat_record.get("checkpoint_id"),
                "source_brain_generate_status": heartbeat_record.get("source_brain_generate_status"),
                "source_critique_status": heartbeat_record.get("source_critique_status"),
                "hive_activation_id": heartbeat_record.get("hive_activation_id"),
                "neural_pathway_id": heartbeat_record.get("neural_pathway_id"),
                "synaptic_transmission_id": heartbeat_record.get("synaptic_transmission_id"),
            },
            sort_keys=True,
            default=str,
        )
        checkpoint_id = f"genesis-checkpoint::{_digest(seed)}"
        path = self.checkpoints_dir / f"{_safe_id(checkpoint_id)}.json"
        checkpoint = {
            "schema_version": "nexusnet-genesis-checkpoint-snapshot-v1",
            "surface_id": "genesis-checkpoint-snapshot",
            "checkpoint_id": checkpoint_id,
            "source_heartbeat_record_id": source_record_id,
            "source_hive_run_id": heartbeat_record.get("source_hive_run_id"),
            "source_brain_generate_status": heartbeat_record.get("source_brain_generate_status"),
            "source_critique_status": heartbeat_record.get("source_critique_status"),
            "hive_activation_id": heartbeat_record.get("hive_activation_id"),
            "neural_pathway_id": heartbeat_record.get("neural_pathway_id"),
            "synaptic_transmission_id": heartbeat_record.get("synaptic_transmission_id"),
            "runtime_growth_receipt_id": heartbeat_record.get("runtime_growth_receipt_id"),
            "federated_packet_id": heartbeat_record.get("federated_packet_id"),
            "content_ref": f"sha256:{_sha256(seed)}",
            "restore_strategy": "replay-heartbeat-evidence-and-safe-file-rollback-ledger",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        if path.is_file():
            persisted = _read_json(path)
            if isinstance(persisted, dict):
                persisted["replay_status"] = "replayed"
                return persisted
        checkpoint["replay_status"] = "recorded"
        path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True), encoding="utf-8")
        return checkpoint

    def _ensure_operation_receipt(
        self,
        heartbeat_record: dict[str, Any],
        checkpoint: dict[str, Any],
    ) -> dict[str, Any]:
        self.operation_receipts_dir.mkdir(parents=True, exist_ok=True)
        receipt_seed = {
            "source_heartbeat_record_id": heartbeat_record.get("record_id"),
            "source_hive_run_id": heartbeat_record.get("source_hive_run_id"),
            "source_brain_generate_status": heartbeat_record.get("source_brain_generate_status"),
            "source_critique_status": heartbeat_record.get("source_critique_status"),
            "hive_activation_id": heartbeat_record.get("hive_activation_id"),
            "neural_pathway_id": heartbeat_record.get("neural_pathway_id"),
            "synaptic_transmission_id": heartbeat_record.get("synaptic_transmission_id"),
            "checkpoint_id": checkpoint.get("checkpoint_id"),
            "runtime_growth_receipt_id": heartbeat_record.get("runtime_growth_receipt_id"),
            "federated_packet_id": heartbeat_record.get("federated_packet_id"),
        }
        seed = json.dumps(receipt_seed, sort_keys=True, default=str)
        operation_receipt_id = f"genesis-operation::{_digest(seed)}"
        path = self.operation_receipts_dir / f"{_safe_id(operation_receipt_id)}.json"
        source_status = str(heartbeat_record.get("source_brain_generate_status") or "unknown")
        source_degraded = source_status in {"blocked", "error", "failed", "runtime-unavailable"}
        receipt = {
            "schema_version": "nexusnet-genesis-operation-receipt-v1",
            "surface_id": "genesis-operation-receipt",
            "operation_receipt_id": operation_receipt_id,
            "status": "degraded-source" if source_degraded else "recorded",
            **receipt_seed,
            "content_ref": f"sha256:{_sha256(seed)}",
            "rollback_aware": True,
            "rollback_strategy": "restore-checkpoint-and-replay-sanitized-heartbeat-evidence",
            "admin_approval_required_for_mutation": True,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
        }
        if path.is_file():
            persisted = _read_json(path)
            if isinstance(persisted, dict):
                persisted["replay_status"] = "replayed"
                return persisted
        receipt["replay_status"] = "recorded"
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
        return receipt

    def _artifact_trust_records(
        self,
        heartbeat_record: dict[str, Any] | None,
        checkpoint: dict[str, Any],
        operation_receipt: dict[str, Any],
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        if isinstance(heartbeat_record, dict):
            heartbeat_seed = json.dumps(_public_heartbeat_record(heartbeat_record), sort_keys=True, default=str)
            records.append(
                _trust_record(
                    artifact_ref=str(heartbeat_record.get("record_id") or ""),
                    artifact_kind="genesis-heartbeat-record",
                    content_ref=f"sha256:{_sha256(heartbeat_seed)}",
                )
            )
        if checkpoint.get("checkpoint_id"):
            records.append(
                _trust_record(
                    artifact_ref=str(checkpoint.get("checkpoint_id") or ""),
                    artifact_kind="genesis-checkpoint-snapshot",
                    content_ref=str(checkpoint.get("content_ref") or ""),
                )
            )
        if operation_receipt.get("operation_receipt_id"):
            records.append(
                _trust_record(
                    artifact_ref=str(operation_receipt.get("operation_receipt_id") or ""),
                    artifact_kind="genesis-operation-receipt",
                    content_ref=str(operation_receipt.get("content_ref") or ""),
                )
            )
        return records

    def _publish_checkpoint_event(
        self,
        heartbeat_record: dict[str, Any],
        checkpoint: dict[str, Any],
        operation_receipt: dict[str, Any],
    ) -> dict[str, Any]:
        learning_state = (
            heartbeat_record.get("per_user_global_learning_state")
            if isinstance(heartbeat_record.get("per_user_global_learning_state"), dict)
            else {}
        )
        return self.event_spine.publish_event(
            event_type="genesis.evidence.checkpoint",
            source_surface_id="genesis-checkpoint-snapshot",
            correlation_ref=str(checkpoint.get("checkpoint_id") or ""),
            session_ref_digest=learning_state.get("session_ref_digest"),
            source_hive_run_ref=heartbeat_record.get("source_hive_run_ref"),
            heartbeat_record_id=str(heartbeat_record.get("record_id") or ""),
            privacy_label="sanitized-genesis-evidence-checkpoint",
            artifact_refs=[
                checkpoint.get("checkpoint_id"),
                checkpoint.get("content_ref"),
                operation_receipt.get("operation_receipt_id"),
                operation_receipt.get("content_ref"),
                heartbeat_record.get("record_id"),
                heartbeat_record.get("runtime_growth_receipt_id"),
                heartbeat_record.get("federated_packet_id"),
            ],
            planes=["evidence", "checkpoint", "artifact_trust", "rollback", "governance"],
            priority_trails=[
                {
                    "topic": "genesis-evidence-checkpoint",
                    "strength": 1.0,
                    "artifact_ref": checkpoint.get("checkpoint_id"),
                }
            ],
            created_at=str(checkpoint.get("checkpoint_id") or checkpoint.get("content_ref") or ""),
        )

    def _empty_checkpoint(self) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-checkpoint-snapshot-v1",
            "surface_id": "genesis-checkpoint-snapshot",
            "checkpoint_id": None,
            "source_heartbeat_record_id": None,
            "replay_status": "not-observed",
            "content_ref": None,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def _empty_operation_receipt(self) -> dict[str, Any]:
        return {
            "schema_version": "nexusnet-genesis-operation-receipt-v1",
            "surface_id": "genesis-operation-receipt",
            "operation_receipt_id": None,
            "status": "not-observed",
            "replay_status": "not-observed",
            "content_ref": None,
            "rollback_aware": True,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
        }

    def _safe_file_path(self, target_ref: str) -> Path:
        relative = target_ref.removeprefix(GENESIS_SAFE_FILE_PREFIX)
        path = (self.safe_files_dir / relative).resolve()
        safe_root = self.safe_files_dir.resolve()
        if safe_root != path and safe_root not in path.parents:
            raise ValueError("target_ref escapes genesis safe-files scope")
        return path

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
        records = [record for record in self._read_jsonl(path) if str(record.get(key) or "") == value]
        if not records:
            raise KeyError(value)
        return records[-1] if latest else records[0]


def _safe_target_ref(target_ref: str) -> str:
    normalized = target_ref.strip().replace("\\", "/")
    if (
        not normalized.startswith(GENESIS_SAFE_FILE_PREFIX)
        or ".." in normalized
        or ":" in normalized
        or normalized.endswith("/")
    ):
        raise ValueError("target_ref must stay within genesis/safe-files/")
    return normalized


def _normalize_test_results(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    results: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        results.append(
            {
                "command_ref": f"command::{_digest(str(item.get('command') or ''))}",
                "passed": item.get("passed") is True,
                "failure_count": int(item.get("failure_count") or 0),
                "evidence_ref": _safe_ref(str(item.get("evidence_ref") or "")),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            }
        )
    return results


def _public_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in proposal.items() if key != "proposed_content"}


def _public_apply(applied: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in applied.items() if key != "previous_content"}


def _public_heartbeat_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": record.get("record_id"),
        "source_hive_run_id": record.get("source_hive_run_id"),
        "source_brain_generate_status": record.get("source_brain_generate_status"),
        "source_critique_status": record.get("source_critique_status"),
        "hive_activation_id": record.get("hive_activation_id"),
        "neural_pathway_id": record.get("neural_pathway_id"),
        "synaptic_transmission_id": record.get("synaptic_transmission_id"),
        "project_heartbeat_id": record.get("project_heartbeat_id"),
        "runtime_growth_receipt_id": record.get("runtime_growth_receipt_id"),
        "federated_packet_id": record.get("federated_packet_id"),
        "checkpoint_id": record.get("checkpoint_id"),
    }


def _trust_record(*, artifact_ref: str, artifact_kind: str, content_ref: str) -> dict[str, Any]:
    return {
        "schema_version": "nexusnet-genesis-artifact-trust-record-v1",
        "surface_id": "genesis-artifact-trust-record",
        "artifact_ref": artifact_ref,
        "artifact_kind": artifact_kind,
        "content_ref": content_ref,
        "trust_status": "trusted",
        "trust_reason": "local-sanitized-genesis-evidence-artifact",
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
    }


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _safe_ref(value: str) -> str:
    text = value.strip().replace("\\", "/")
    if not text or ".." in text or ":\\" in text:
        return ""
    return text[:180]


def _safe_id(value: str) -> str:
    return value.replace(":", "_").replace("/", "_").replace("\\", "_")


def _dedupe(values: list[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _sha256(value: str | None) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
