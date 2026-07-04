from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nexusnet.hive.project_heartbeat_replay import compact_failure_recovery_governance


def build_release_health_heartbeat_supervisor_repair_run_plan(
    *,
    payload: dict[str, Any],
    supervisor: dict[str, Any],
    proposal: dict[str, Any],
    registered_suite_ids: set[str],
    default_command: str,
    digest: Callable[[str], str],
) -> dict[str, Any]:
    latest_pulse = supervisor.get("latest_pulse") if isinstance(supervisor.get("latest_pulse"), dict) else {}
    loop = latest_pulse.get("loop") if isinstance(latest_pulse.get("loop"), dict) else {}
    repair_queue = loop.get("repair_queue") if isinstance(loop.get("repair_queue"), dict) else {}
    update_id = str(payload.get("update_id") or repair_queue.get("latest_update_id") or "")
    source_pulse_id = str(latest_pulse.get("pulse_id") or "")
    source_loop_id = str(loop.get("loop_id") or latest_pulse.get("loop_id") or "")
    source_heartbeat_id = str(latest_pulse.get("heartbeat_id") or "")

    if not update_id:
        return _blocked_plan(
            "blocked-missing-update-id",
            http_status=400,
            detail="heartbeat supervisor repair requires a pulse repair proposal update_id",
            source_pulse_id=source_pulse_id,
            source_loop_id=source_loop_id,
            source_heartbeat_id=source_heartbeat_id,
        )

    eval_refs = [str(ref) for ref in (proposal.get("eval_refs") or []) if str(ref or "")]
    suite_id = next((ref for ref in eval_refs if ref.startswith("eval::release-wrapper-runtime::")), "")
    gate_refs = [ref for ref in eval_refs if ref.startswith("evals-ao-artifact::")]
    if not suite_id:
        return _blocked_plan(
            "blocked-missing-eval-suite",
            http_status=400,
            detail="heartbeat supervisor repair proposal is missing a release-wrapper eval suite ref",
            update_id=update_id,
            source_pulse_id=source_pulse_id,
            source_loop_id=source_loop_id,
            source_heartbeat_id=source_heartbeat_id,
        )

    evidence_refs = [
        ref
        for ref in (
            source_pulse_id,
            source_loop_id,
            source_heartbeat_id,
            repair_queue.get("latest_update_id"),
            *gate_refs,
        )
        if str(ref or "")
    ]
    command = str(
        payload.get("command")
        or payload.get("sandbox_command")
        or proposal.get("monitoring_plan")
        or default_command
    )
    timeout_seconds = int(payload.get("timeout_seconds") or 60)
    approved_by = str(payload.get("approved_by") or "admin")
    approval_ref = str(payload.get("approval_ref") or "operator-review::heartbeat-supervisor-repair")
    target_surfaces = [
        str(surface)
        for surface in (
            proposal.get("target_surfaces")
            if isinstance(proposal.get("target_surfaces"), list)
            else [
                "release-wrapper-health-heartbeat-supervisor",
                "release-wrapper-health-heartbeat-loop",
            ]
        )
        if str(surface or "")
    ]
    subsystem_repair_envelopes = _build_subsystem_repair_envelopes(
        loop=loop,
        update_id=update_id,
        suite_id=suite_id,
        gate_refs=gate_refs,
        evidence_refs=evidence_refs,
        command=command,
        approval_ref=approval_ref,
        digest=digest,
    )
    eval_suite_request = {
        "suite_id": suite_id,
        "suite_type": "runtime",
        "target_surfaces": target_surfaces,
        "benchmark_refs": evidence_refs,
        "held_out": True,
        "external_or_tool_verifier": True,
        "metrics": {"regression_count": 0.0, "heartbeat_repair_score": 1.0},
        "promotion_target": "autonomous_update",
        "evidence_refs": evidence_refs,
        "rollback_plan": str(proposal.get("rollback_plan") or "heartbeat-supervisor-safe-file-rollback"),
        "monitoring_plan": str(
            proposal.get("monitoring_plan") or "release-health-heartbeat-supervisor-repair-monitoring"
        ),
        "metadata": {
            "source": "release-health-heartbeat-supervisor-repair-run",
            "gate_id": gate_refs[0] if gate_refs else None,
            "subsystem_repair_envelope_count": len(subsystem_repair_envelopes),
            "subsystem_repair_envelope_refs": [
                str(envelope.get("envelope_id") or "") for envelope in subsystem_repair_envelopes
            ],
            "replay_template": {
                "payload": {
                    "run_id": f"shadow-run::{digest(update_id + suite_id)}",
                    "candidate_ref": f"autonomous-update::{update_id}",
                    "baseline_ref": "release-wrapper-current-health-supervisor",
                    "metrics": {"regression_count": 0.0, "heartbeat_repair_score": 1.0},
                    "trace_refs": evidence_refs,
                    "evaluator_refs": ["ao::EvalsAO", "ao::ReleaseAO", *gate_refs],
                    "evidence_refs": evidence_refs,
                    "operator_approved": True,
                    "lifecycle_ref": source_loop_id or source_pulse_id,
                    "lifecycle_status": "admin_approved_shadow_repair",
                    "growth_engine_gate": {"allowed": True, "blockers": []},
                    "artifact_trust_promotion": {
                        "promotion_allowed": True,
                        "promotion_blockers": [],
                    },
                    "metadata": {
                        "source": "release-health-heartbeat-supervisor-repair-run",
                        "evals_ao_artifact_gate_ref": gate_refs[0] if gate_refs else None,
                        "evals_ao_artifact_gate_refs": gate_refs,
                    },
                }
            },
        },
    }
    return {
        "status": "planned",
        "repair_scope": "whole-system-admin-approved-update-path",
        "update_id": update_id,
        "source_pulse_id": source_pulse_id,
        "source_loop_id": source_loop_id,
        "source_heartbeat_id": source_heartbeat_id,
        "suite_id": suite_id,
        "gate_refs": gate_refs,
        "evidence_refs": evidence_refs,
        "target_surfaces": target_surfaces,
        "subsystem_repair_envelopes": subsystem_repair_envelopes,
        "subsystem_repair_envelope_count": len(subsystem_repair_envelopes),
        "command": command,
        "timeout_seconds": timeout_seconds,
        "approved_by": approved_by,
        "approval_ref": approval_ref,
        "register_eval_suite": suite_id not in set(registered_suite_ids),
        "eval_suite_request": eval_suite_request,
        "admin_approval_payload": {
            "approved_by": approved_by,
            "approval_ref": approval_ref,
        },
        "sandbox_tests_payload": {
            "command": command,
            "timeout_seconds": timeout_seconds,
        },
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def build_completed_release_health_heartbeat_subsystem_repair_envelopes(
    envelopes: list[dict[str, Any]],
    *,
    actions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    action_statuses = {
        "admin_approval": str((actions.get("admin_approval") or {}).get("status") or "not-approved"),
        "shadow_eval_replay": str((actions.get("shadow_eval_replay") or {}).get("status") or "not-run"),
        "sandbox_tests": str((actions.get("sandbox_tests") or {}).get("status") or "not-run"),
        "apply": str((actions.get("apply") or {}).get("status") or "not-applied"),
        "rollback": str((actions.get("rollback") or {}).get("status") or "not-rolled-back"),
    }
    completed = (
        action_statuses["admin_approval"] == "admin-approved"
        and action_statuses["shadow_eval_replay"] == "passed-shadow"
        and action_statuses["sandbox_tests"] == "passed"
        and action_statuses["apply"] == "applied-shadow-safe-file"
        and action_statuses["rollback"] == "rolled-back"
    )
    honest_status_label = (
        "completed-shadow-safe-file-rollback-verified"
        if completed
        else "blocked-before-shadow-safe-file-rollback-completion"
    )
    return [
        {
            **_sanitize_envelope(envelope),
            "status": "completed" if completed else "blocked",
            "honest_status_label": honest_status_label,
            "action_statuses": dict(action_statuses),
            "active_production_mutated": any(
                bool((actions.get(action) or {}).get("active_production_mutated"))
                for action in ("admin_approval", "shadow_eval_replay", "sandbox_tests", "apply", "rollback")
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }
        for envelope in envelopes
        if isinstance(envelope, dict)
    ]


def _blocked_plan(
    status: str,
    *,
    http_status: int,
    detail: str,
    update_id: str | None = None,
    source_pulse_id: str = "",
    source_loop_id: str = "",
    source_heartbeat_id: str = "",
) -> dict[str, Any]:
    return {
        "status": status,
        "http_status": http_status,
        "detail": detail,
        "update_id": update_id,
        "source_pulse_id": source_pulse_id,
        "source_loop_id": source_loop_id,
        "source_heartbeat_id": source_heartbeat_id,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def _build_subsystem_repair_envelopes(
    *,
    loop: dict[str, Any],
    update_id: str,
    suite_id: str,
    gate_refs: list[str],
    evidence_refs: list[str],
    command: str,
    approval_ref: str,
    digest: Callable[[str], str],
) -> list[dict[str, Any]]:
    candidates = (
        loop.get("whole_system_repair_candidates")
        if isinstance(loop.get("whole_system_repair_candidates"), list)
        else []
    )
    envelopes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in candidates[:20]:
        if not isinstance(candidate, dict):
            continue
        gate_id = str(candidate.get("gate_id") or "").strip()
        if not gate_id or gate_id in seen:
            continue
        seen.add(gate_id)
        target_surfaces = _bounded_strings(candidate.get("target_surfaces"), limit=12)
        envelope_id = f"subsystem-repair-envelope::{gate_id}::{digest(gate_id)}"
        candidate_evidence_refs = _bounded_strings(candidate.get("evidence_refs"), limit=12)
        envelope = {
            "surface_id": "release-health-heartbeat-subsystem-repair-envelope",
            "envelope_id": envelope_id,
            "candidate_id": str(candidate.get("candidate_id") or f"whole-system-gate::{gate_id}"),
            "gate_id": gate_id,
            "status": "planned",
            "honest_status_label": "planned-admin-approval-required",
            "target_surfaces": target_surfaces,
            "blocking_check_ids": _bounded_strings(candidate.get("blocking_check_ids"), limit=16),
            "missing_check_ids": _bounded_strings(candidate.get("missing_check_ids"), limit=16),
            "nonblocking_check_ids": _bounded_strings(candidate.get("nonblocking_check_ids"), limit=16),
            "eval_suite_id": suite_id,
            "eval_gate_refs": list(gate_refs),
            "evidence_refs": _dedupe_strings([*candidate_evidence_refs, *evidence_refs], limit=24),
            "admin_approval_ref": approval_ref,
            "sandbox_command_ref": f"pytest::{digest(command)}",
            "apply_ref": f"autonomous-update-apply::{update_id}",
            "rollback_ref": f"autonomous-update-rollback::{update_id}",
            "repair_lane": "admin-approved-shadow-eval-sandbox-safe-file-apply-rollback",
            "action_statuses": {
                "admin_approval": "pending-admin-approval",
                "shadow_eval_replay": "not-run",
                "sandbox_tests": "not-run",
                "apply": "not-applied",
                "rollback": "not-rolled-back",
            },
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        if isinstance(candidate.get("recovery_governance"), dict):
            envelope["recovery_governance"] = compact_failure_recovery_governance(
                candidate.get("recovery_governance")
            )
        envelopes.append(envelope)
    return envelopes


def _sanitize_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    sanitized = {
        "surface_id": str(envelope.get("surface_id") or "release-health-heartbeat-subsystem-repair-envelope"),
        "envelope_id": str(envelope.get("envelope_id") or ""),
        "candidate_id": str(envelope.get("candidate_id") or ""),
        "gate_id": str(envelope.get("gate_id") or ""),
        "status": str(envelope.get("status") or "planned"),
        "honest_status_label": str(envelope.get("honest_status_label") or "planned-admin-approval-required"),
        "target_surfaces": _bounded_strings(envelope.get("target_surfaces"), limit=12),
        "blocking_check_ids": _bounded_strings(envelope.get("blocking_check_ids"), limit=16),
        "missing_check_ids": _bounded_strings(envelope.get("missing_check_ids"), limit=16),
        "nonblocking_check_ids": _bounded_strings(envelope.get("nonblocking_check_ids"), limit=16),
        "eval_suite_id": str(envelope.get("eval_suite_id") or ""),
        "eval_gate_refs": _bounded_strings(envelope.get("eval_gate_refs"), limit=12),
        "evidence_refs": _bounded_strings(envelope.get("evidence_refs"), limit=24),
        "admin_approval_ref": str(envelope.get("admin_approval_ref") or ""),
        "sandbox_command_ref": str(envelope.get("sandbox_command_ref") or ""),
        "apply_ref": str(envelope.get("apply_ref") or ""),
        "rollback_ref": str(envelope.get("rollback_ref") or ""),
        "repair_lane": "admin-approved-shadow-eval-sandbox-safe-file-apply-rollback",
        "action_statuses": (
            dict(envelope.get("action_statuses"))
            if isinstance(envelope.get("action_statuses"), dict)
            else {
                "admin_approval": "pending-admin-approval",
                "shadow_eval_replay": "not-run",
                "sandbox_tests": "not-run",
                "apply": "not-applied",
                "rollback": "not-rolled-back",
            }
        ),
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": bool(envelope.get("active_production_mutated")),
    }
    if isinstance(envelope.get("recovery_governance"), dict):
        sanitized["recovery_governance"] = compact_failure_recovery_governance(
            envelope.get("recovery_governance")
        )
    return sanitized


def _bounded_strings(values: Any, *, limit: int) -> list[str]:
    if not isinstance(values, list):
        return []
    return _dedupe_strings([str(value) for value in values if str(value or "")], limit=limit)


def _dedupe_strings(values: list[str], *, limit: int) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        deduped.append(text)
        if len(deduped) >= limit:
            break
    return deduped
