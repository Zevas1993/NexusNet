from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nexusnet.hive.project_heartbeat_replay import compact_failure_recovery_governance


def build_release_health_heartbeat_supervisor_repair_history(
    *,
    readiness_runs: list[dict[str, Any]],
    pulses: list[dict[str, Any]],
    session_ref_digest: str | None,
    safe_ref: Callable[[str], str],
) -> dict[str, Any]:
    runs = [
        run
        for run in readiness_runs
        if "heartbeat-supervisor-repair" in str(run.get("status") or "")
        and (not session_ref_digest or str(run.get("session_ref_digest") or "") == session_ref_digest)
    ]
    global_repair_count = sum(
        1 for run in readiness_runs if "heartbeat-supervisor-repair" in str(run.get("status") or "")
    )
    pulses_by_update: dict[str, dict[str, Any]] = {}
    for pulse in pulses:
        loop = pulse.get("loop") if isinstance(pulse.get("loop"), dict) else {}
        repair_queue = loop.get("repair_queue") if isinstance(loop.get("repair_queue"), dict) else {}
        update_id = str(repair_queue.get("latest_update_id") or "")
        if update_id:
            pulses_by_update[update_id] = pulse
            pulses_by_update[safe_ref(update_id)] = pulse

    repairs: list[dict[str, Any]] = []
    for run in runs[-20:]:
        safe_update_id = str(run.get("update_id") or "")
        pulse = pulses_by_update.get(safe_update_id) or {}
        loop = pulse.get("loop") if isinstance(pulse.get("loop"), dict) else {}
        repair_queue = loop.get("repair_queue") if isinstance(loop.get("repair_queue"), dict) else {}
        source_update_id = str(repair_queue.get("latest_update_id") or safe_update_id)
        actions = run.get("actions") if isinstance(run.get("actions"), dict) else {}
        subsystem_repair_envelopes = _sanitize_subsystem_repair_envelopes(
            run.get("subsystem_repair_envelopes")
            if isinstance(run.get("subsystem_repair_envelopes"), list)
            else []
        )
        repairs.append(
            {
                "run_id": run.get("run_id") if isinstance(run.get("run_id"), str) else None,
                "status": str(run.get("status") or "not-run"),
                "update_id": source_update_id,
                "safe_update_id": safe_update_id,
                "pulse_id": pulse.get("pulse_id") if isinstance(pulse.get("pulse_id"), str) else None,
                "loop_id": pulse.get("loop_id") if isinstance(pulse.get("loop_id"), str) else None,
                "heartbeat_id": pulse.get("heartbeat_id") if isinstance(pulse.get("heartbeat_id"), str) else None,
                "action_statuses": {
                    "admin_approval": str((actions.get("admin_approval") or {}).get("status") or "not-approved"),
                    "shadow_eval_replay": str(
                        (actions.get("shadow_eval_replay") or {}).get("status") or "not-run"
                    ),
                    "sandbox_tests": str((actions.get("sandbox_tests") or {}).get("status") or "not-run"),
                    "apply": str((actions.get("apply") or {}).get("status") or "not-applied"),
                    "rollback": str((actions.get("rollback") or {}).get("status") or "not-rolled-back"),
                },
                "subsystem_repair_envelopes": subsystem_repair_envelopes,
                "subsystem_repair_envelope_count": len(subsystem_repair_envelopes),
                "active_production_mutated": bool(run.get("active_production_mutated")),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            }
        )

    latest = repairs[-1] if repairs else {}
    return {
        "surface_id": "release-health-heartbeat-supervisor-repair-history",
        "status": "recorded" if repairs else "not-run",
        "scope": "session" if session_ref_digest else "global",
        "session_ref_digest": session_ref_digest,
        "repair_count": len(repairs),
        "global_repair_count": global_repair_count,
        "latest_status": latest.get("status") or "not-run",
        "latest_run_id": latest.get("run_id"),
        "latest_update_id": latest.get("update_id"),
        "latest_safe_update_id": latest.get("safe_update_id"),
        "latest_pulse_id": latest.get("pulse_id"),
        "latest_loop_id": latest.get("loop_id"),
        "latest_heartbeat_id": latest.get("heartbeat_id"),
        "latest_subsystem_repair_envelopes": latest.get("subsystem_repair_envelopes") or [],
        "latest_subsystem_repair_envelope_count": len(latest.get("subsystem_repair_envelopes") or []),
        "repairs": repairs,
        "active_production_mutated": any(bool(repair.get("active_production_mutated")) for repair in repairs),
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "mutation_boundary": "admin-approved-shadow-eval-sandbox-safe-file-apply-rollback-only",
        "privacy_boundary": "sanitized-heartbeat-repair-run-ids-statuses-and-pulse-refs-only-no-prompts-outputs-session-ids",
    }


def _sanitize_subsystem_repair_envelopes(envelopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized: list[dict[str, Any]] = []
    for envelope in envelopes[:20]:
        if not isinstance(envelope, dict):
            continue
        sanitized_envelope = {
            "surface_id": str(
                envelope.get("surface_id") or "release-health-heartbeat-subsystem-repair-envelope"
            ),
            "envelope_id": envelope.get("envelope_id") if isinstance(envelope.get("envelope_id"), str) else None,
            "candidate_id": envelope.get("candidate_id") if isinstance(envelope.get("candidate_id"), str) else None,
            "gate_id": envelope.get("gate_id") if isinstance(envelope.get("gate_id"), str) else None,
            "status": str(envelope.get("status") or "not-run"),
            "honest_status_label": str(envelope.get("honest_status_label") or "not-run"),
            "target_surfaces": _bounded_strings(envelope.get("target_surfaces"), limit=12),
            "blocking_check_ids": _bounded_strings(envelope.get("blocking_check_ids"), limit=16),
            "missing_check_ids": _bounded_strings(envelope.get("missing_check_ids"), limit=16),
            "nonblocking_check_ids": _bounded_strings(envelope.get("nonblocking_check_ids"), limit=16),
            "eval_suite_id": envelope.get("eval_suite_id") if isinstance(envelope.get("eval_suite_id"), str) else None,
            "eval_gate_refs": _bounded_strings(envelope.get("eval_gate_refs"), limit=12),
            "evidence_refs": _bounded_strings(envelope.get("evidence_refs"), limit=24),
            "admin_approval_ref": (
                envelope.get("admin_approval_ref") if isinstance(envelope.get("admin_approval_ref"), str) else None
            ),
            "sandbox_command_ref": (
                envelope.get("sandbox_command_ref") if isinstance(envelope.get("sandbox_command_ref"), str) else None
            ),
            "apply_ref": envelope.get("apply_ref") if isinstance(envelope.get("apply_ref"), str) else None,
            "rollback_ref": envelope.get("rollback_ref") if isinstance(envelope.get("rollback_ref"), str) else None,
            "repair_lane": str(
                envelope.get("repair_lane")
                or "admin-approved-shadow-eval-sandbox-safe-file-apply-rollback"
            ),
            "action_statuses": (
                dict(envelope.get("action_statuses"))
                if isinstance(envelope.get("action_statuses"), dict)
                else {}
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": bool(envelope.get("active_production_mutated")),
        }
        if isinstance(envelope.get("recovery_governance"), dict):
            sanitized_envelope["recovery_governance"] = compact_failure_recovery_governance(
                envelope.get("recovery_governance")
            )
        sanitized.append(sanitized_envelope)
    return sanitized


def _bounded_strings(values: Any, *, limit: int) -> list[str]:
    if not isinstance(values, list):
        return []
    seen: set[str] = set()
    bounded: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        bounded.append(text)
        if len(bounded) >= limit:
            break
    return bounded
