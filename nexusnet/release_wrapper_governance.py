from __future__ import annotations

from typing import Any


REQUIRED_GOVERNED_UPDATE_ACTIONS = ("admin_approval", "sandbox_tests", "apply", "rollback")
EXPECTED_GOVERNED_UPDATE_STATUSES = {
    "admin_approval": "admin-approved",
    "sandbox_tests": "passed",
    "apply": "applied-shadow-safe-file",
    "rollback": "rolled-back",
}


def apply_federated_import_governed_update_path(
    *,
    update_id: str,
    import_id: str,
    source_packet_ref: str,
    record: dict[str, Any],
    receipt: dict[str, Any],
    run: dict[str, Any] | None = None,
    action_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    run = run if isinstance(run, dict) else {}
    actions = run.get("actions") if isinstance(run.get("actions"), dict) else {}
    latest_manual_actions: dict[str, dict[str, Any]] = {}
    latest_manual_action: str | None = None
    latest_manual_action_status: str | None = None
    for action_record in action_records or []:
        if not isinstance(action_record, dict):
            continue
        action_id = str(action_record.get("action") or "")
        if action_id not in REQUIRED_GOVERNED_UPDATE_ACTIONS:
            continue
        latest_manual_actions[action_id] = action_record
        latest_manual_action = action_id
        latest_manual_action_status = str(action_record.get("status") or "missing")
    manual_governance_recorded = bool(latest_manual_actions)
    action_statuses: dict[str, str] = {}
    action_operation_receipt_ids: dict[str, str] = {}
    action_evidence_refs: list[str] = []
    for action_id in REQUIRED_GOVERNED_UPDATE_ACTIONS:
        if manual_governance_recorded:
            action_record = latest_manual_actions.get(action_id) or {}
            action_statuses[action_id] = str(action_record.get("status") or "missing")
            operation_receipt = (
                action_record.get("operation_receipt")
                if isinstance(action_record.get("operation_receipt"), dict)
                else {}
            )
            action_evidence_refs.extend(
                str(ref)
                for ref in action_record.get("evidence_refs") or []
                if str(ref or "").strip()
            )
        else:
            action_result = actions.get(action_id) if isinstance(actions.get(action_id), dict) else {}
            action_statuses[action_id] = str(action_result.get("status") or "missing")
            self_repair = (
                action_result.get("release_wrapper_self_repair")
                if isinstance(action_result.get("release_wrapper_self_repair"), dict)
                else {}
            )
            operation_receipt = (
                self_repair.get("operation_receipt")
                if isinstance(self_repair.get("operation_receipt"), dict)
                else {}
            )
            action_evidence_refs.extend(
                str(ref)
                for ref in self_repair.get("evidence_refs") or []
                if str(ref or "").strip()
            )
        receipt_id = str(operation_receipt.get("receipt_id") or "")
        if receipt_id:
            action_operation_receipt_ids[action_id] = receipt_id
            action_evidence_refs.append(f"operation-receipt::{receipt_id}")
    active_production_mutated = (
        any(bool(action_record.get("active_production_mutated")) for action_record in latest_manual_actions.values())
        if manual_governance_recorded
        else bool(run.get("active_production_mutated"))
    )
    run_id = run.get("run_id")
    run_status = str(run.get("status") or "")
    complete = (
        (run_status == "completed" or manual_governance_recorded)
        and action_statuses == EXPECTED_GOVERNED_UPDATE_STATUSES
        and set(action_operation_receipt_ids) == set(REQUIRED_GOVERNED_UPDATE_ACTIONS)
        and active_production_mutated is False
    )
    governed_status = (
        "completed-admin-approved-sandbox-applied-rolled-back"
        if complete
        else "partial-admin-governance-recorded"
    )
    admin_action = actions.get("admin_approval") if isinstance(actions.get("admin_approval"), dict) else {}
    linked_eval_replay = (
        admin_action.get("linked_eval_replay")
        if isinstance(admin_action.get("linked_eval_replay"), dict)
        else {}
    )
    safe_update_id = _safe_ref(update_id)
    governed_update_path = {
        **(
            receipt.get("governed_update_path")
            if isinstance(receipt.get("governed_update_path"), dict)
            else {}
        ),
        "status": governed_status,
        "update_id": safe_update_id,
        "proposal_ref": f"update::{safe_update_id}",
        "source_packet_ref": source_packet_ref or record.get("source_packet_ref"),
        "readiness_run_id": run_id,
        "readiness_run_status": run.get("status"),
        "manual_governance_recorded": manual_governance_recorded,
        "latest_manual_action": latest_manual_action if manual_governance_recorded else None,
        "latest_manual_action_status": latest_manual_action_status if manual_governance_recorded else None,
        "action_statuses": action_statuses,
        "action_operation_receipt_ids": action_operation_receipt_ids,
        "action_evidence_refs": _dedupe_strings(action_evidence_refs)[:16],
        "admin_approval_status": action_statuses["admin_approval"],
        "sandbox_status": action_statuses["sandbox_tests"],
        "apply_status": action_statuses["apply"],
        "rollback_status": action_statuses["rollback"],
        "linked_eval_replay_status": linked_eval_replay.get("status") or None,
        "linked_eval_replay_run_id": linked_eval_replay.get("run_id") or None,
        "linked_eval_replay_suite_id": linked_eval_replay.get("suite_id") or None,
        "active_production_mutation_allowed": False,
        "active_production_mutated": active_production_mutated,
        "raw_content_included": False,
    }
    receipt["governed_update_path"] = governed_update_path
    receipt["replay"] = {
        **(receipt.get("replay") if isinstance(receipt.get("replay"), dict) else {}),
        "status": "persisted-for-shadow-replay",
        "latest_readiness_run_id": run_id,
        "latest_readiness_run_status": run.get("status"),
        "latest_manual_governance_update_id": safe_update_id if manual_governance_recorded else None,
        "latest_manual_action": latest_manual_action if manual_governance_recorded else None,
        "latest_manual_action_status": latest_manual_action_status if manual_governance_recorded else None,
        "artifact_ref": "release-wrapper-runtime/federated-packet-imports.jsonl",
        "readiness_evidence_ref": "release-wrapper-runtime/release-readiness-evidence-runs.jsonl",
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
    }
    receipt["evidence_refs"] = _dedupe_strings(
        [
            *[str(ref) for ref in receipt.get("evidence_refs") or [] if str(ref or "").strip()],
            *([f"release-readiness-run::{run_id}"] if run_id else []),
            *action_evidence_refs,
        ]
    )[:20]
    receipt["active_production_mutated"] = active_production_mutated
    record["whole_system_enforcement_receipt"] = receipt
    record["whole_system_enforcement_receipt_id"] = receipt.get("receipt_id")
    record["governed_update_path_status"] = governed_status
    return {
        "status": governed_status,
        "update_id": safe_update_id,
        "federated_packet_import_id": import_id,
        "whole_system_enforcement_receipt_id": receipt.get("receipt_id"),
        "readiness_run_id": run_id,
        "manual_governance_recorded": manual_governance_recorded,
        "latest_manual_action": latest_manual_action if manual_governance_recorded else None,
        "latest_manual_action_status": latest_manual_action_status if manual_governance_recorded else None,
        "action_operation_receipt_ids": action_operation_receipt_ids,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": active_production_mutated,
    }


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        deduped.append(text)
    return deduped


def _safe_ref(value: str) -> str:
    return value.replace(":", "_").replace("/", "_").replace("\\", "_")

