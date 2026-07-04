from __future__ import annotations

from typing import Any

from nexusnet.hive.project_heartbeat_replay import compact_failure_recovery_governance


NATIVE_PROJECT_HEARTBEAT_RECOVERY_GATE_ID = "native-project-heartbeat-recovery-governance"


WHOLE_SYSTEM_GATE_TARGET_SURFACES: dict[str, tuple[str, ...]] = {
    "wrapper-product-entrypoint": ("release-wrapper-runtime", "wrapper-product-entrypoint"),
    "live-model-provider-path": ("release-wrapper-runtime", "model-provider-path"),
    "teacher-expert-birth-registry": ("teacher-expert-registry", "expert-birth-stack"),
    "developmental-growth-promotion-governance": (
        "developmental-growth",
        "growth-engine",
        "promotion-governance",
    ),
    "authority-evidence-tool-governance": (
        "authority-spine",
        "evidence-store",
        "eval-runtime-governance",
        "tool-action-harness",
    ),
    "native-hive-runtime-heartbeat": (
        "native-hive-runtime",
        "growth-engine",
        "native-runtime-growth-governance",
    ),
    "assimilation-growth-expert-path": (
        "continuous-assimilation",
        "global-growth",
        "expert-routing",
    ),
    "federation-runtime-path": ("federation-runtime", "shadow-learning"),
    "eval-runtime-governance": ("eval-runtime-governance", "EvalsAO"),
    "ao-runtime-governance": ("canonical-ao-runtime", "AO-governance"),
    "domain-ao-teacher-eval-path": ("domain-ao-runtime", "teacher-eval-governance"),
    "sandboxed-self-repair-governance": ("autonomous-updates", "sandboxed-self-repair"),
    "native-runtime-growth-governance": (
        "native-runtime-growth-governance",
        "growth-engine",
    ),
    NATIVE_PROJECT_HEARTBEAT_RECOVERY_GATE_ID: (
        "native-hive-runtime",
        "native-project-heartbeat",
        "native-project-heartbeat-failure-recovery-governance",
        "release-health-heartbeat-supervisor",
        "autonomous-updates",
        "sandboxed-self-repair",
    ),
    "context-cache-truth-boundary": ("context-cache-truth-boundary",),
    "production-spine-release-manifest": ("production-spine", "release-manifest"),
    "visualizer-control-panel-surface": ("visualizer-control-panel",),
}


def sanitize_release_health_heartbeat_whole_system_contract(
    whole_system_boot_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    contract = whole_system_boot_contract if isinstance(whole_system_boot_contract, dict) else {}
    gates = contract.get("subsystem_gates") if isinstance(contract.get("subsystem_gates"), list) else []
    sanitized_gates: list[dict[str, Any]] = []
    for gate in gates[:32]:
        if not isinstance(gate, dict):
            continue
        gate_id = str(gate.get("gate_id") or "").strip()
        if not gate_id:
            continue
        sanitized_gates.append(
            {
                "gate_id": gate_id,
                "status": str(gate.get("status") or "unknown"),
                "blocking_check_ids": _bounded_strings(gate.get("blocking_check_ids"), limit=16),
                "missing_check_ids": _bounded_strings(gate.get("missing_check_ids"), limit=16),
                "nonblocking_check_ids": _bounded_strings(gate.get("nonblocking_check_ids"), limit=16),
                "evidence_refs": _bounded_strings(gate.get("evidence_refs"), limit=16),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
        )
    return {
        "surface_id": str(contract.get("surface_id") or "whole-system-release-boot-contract"),
        "status": str(contract.get("status") or "not-run"),
        "product_scope": str(contract.get("product_scope") or "whole-system"),
        "passed_count": _safe_int(contract.get("passed_count")),
        "blocked_count": _safe_int(contract.get("blocked_count")),
        "subsystem_gates": sanitized_gates,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def build_release_health_heartbeat_subsystem_repair_candidates(
    whole_system_boot_contract: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    contract = sanitize_release_health_heartbeat_whole_system_contract(whole_system_boot_contract)
    candidates: list[dict[str, Any]] = []
    for gate in contract["subsystem_gates"]:
        if gate.get("status") == "pass":
            continue
        gate_id = str(gate.get("gate_id") or "").strip()
        if not gate_id:
            continue
        candidates.append(
            {
                "candidate_id": f"whole-system-gate::{gate_id}",
                "gate_id": gate_id,
                "status": str(gate.get("status") or "blocked"),
                "target_surfaces": list(
                    WHOLE_SYSTEM_GATE_TARGET_SURFACES.get(gate_id, (gate_id,))
                ),
                "blocking_check_ids": list(gate.get("blocking_check_ids") or []),
                "missing_check_ids": list(gate.get("missing_check_ids") or []),
                "nonblocking_check_ids": list(gate.get("nonblocking_check_ids") or []),
                "evidence_refs": list(gate.get("evidence_refs") or [])[:8],
                "repair_lane": "admin-approved-shadow-eval-sandbox-safe-file-apply-rollback",
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
        )
    return candidates


def release_health_heartbeat_repair_candidates_from_cycles(
    cycles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates_by_gate: dict[str, dict[str, Any]] = {}
    for cycle in cycles:
        if not isinstance(cycle, dict):
            continue
        cycle_candidates = cycle.get("whole_system_repair_candidates")
        if isinstance(cycle_candidates, list):
            for candidate in cycle_candidates:
                if not isinstance(candidate, dict):
                    continue
                gate_id = str(candidate.get("gate_id") or "").strip()
                if gate_id and gate_id not in candidates_by_gate:
                    candidates_by_gate[gate_id] = _sanitize_repair_candidate(candidate)
        native_recovery_candidate = build_native_project_heartbeat_recovery_candidate(
            cycle.get("project_heartbeat") if isinstance(cycle.get("project_heartbeat"), dict) else None
        )
        if native_recovery_candidate:
            gate_id = str(native_recovery_candidate.get("gate_id") or "").strip()
            if gate_id and gate_id not in candidates_by_gate:
                candidates_by_gate[gate_id] = native_recovery_candidate
        contract = cycle.get("whole_system_boot_contract")
        for candidate in build_release_health_heartbeat_subsystem_repair_candidates(
            contract if isinstance(contract, dict) else None
        ):
            gate_id = str(candidate.get("gate_id") or "").strip()
            if gate_id and gate_id not in candidates_by_gate:
                candidates_by_gate[gate_id] = candidate
    return list(candidates_by_gate.values())


def release_health_heartbeat_target_surfaces(
    candidates: list[dict[str, Any]],
    *,
    fallback: list[str] | None = None,
) -> list[str]:
    values: list[str] = []
    if fallback:
        values.extend(fallback)
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        values.extend(str(surface) for surface in candidate.get("target_surfaces") or [])
    return _dedupe_strings(values, limit=64)


def release_health_heartbeat_candidate_gate_ids(candidates: list[dict[str, Any]]) -> list[str]:
    return _dedupe_strings(
        [
            str(candidate.get("gate_id") or "")
            for candidate in candidates
            if isinstance(candidate, dict)
        ],
        limit=64,
    )


def build_native_project_heartbeat_recovery_candidate(
    project_heartbeat: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(project_heartbeat, dict):
        return None
    governance = compact_failure_recovery_governance(
        project_heartbeat.get("failure_recovery_governance")
    )
    heartbeat_status = str(project_heartbeat.get("status") or "unknown")
    runtime_state = str(project_heartbeat.get("runtime_state") or "unknown")
    governance_status = str(governance.get("status") or "unknown")
    blocked_forward_pass = bool(governance.get("blocked_forward_pass"))
    degraded = (
        blocked_forward_pass
        or heartbeat_status == "degraded"
        or runtime_state == "degraded"
        or governance_status.startswith("degraded")
    )
    if not degraded:
        return None
    heartbeat_id = str(project_heartbeat.get("heartbeat_id") or "unknown")
    evidence_refs = _bounded_strings(
        [
            *governance.get("evidence_refs", []),
            *project_heartbeat.get("evidence_refs", []),
            project_heartbeat.get("native_replay_ref"),
            project_heartbeat.get("native_replay_record_id"),
            project_heartbeat.get("wrapper_replay_ref"),
            project_heartbeat.get("wrapper_replay_record_id"),
            project_heartbeat.get("source_run_id"),
        ],
        limit=16,
    )
    missing_check_ids = []
    if not governance.get("self_healing_route_available"):
        missing_check_ids.append("self-healing-route-around")
    return {
        "candidate_id": f"native-project-heartbeat-recovery::{heartbeat_id}",
        "gate_id": NATIVE_PROJECT_HEARTBEAT_RECOVERY_GATE_ID,
        "status": governance_status if governance_status != "not-emitted" else heartbeat_status,
        "target_surfaces": list(WHOLE_SYSTEM_GATE_TARGET_SURFACES[NATIVE_PROJECT_HEARTBEAT_RECOVERY_GATE_ID]),
        "blocking_check_ids": ["native-project-heartbeat-failure-recovery-governance"],
        "missing_check_ids": missing_check_ids,
        "nonblocking_check_ids": [],
        "evidence_refs": evidence_refs,
        "repair_lane": "admin-approved-shadow-eval-sandbox-safe-file-apply-rollback",
        "recovery_governance": governance,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def build_release_health_heartbeat_loop_record(
    *,
    schema_version: str,
    surface_id: str,
    artifact_ref: str,
    heartbeat_artifact_ref: str,
    loop_id: str,
    generated_at: str,
    next_due_at: str,
    trigger: str,
    session_ref_digest: str | None,
    bounded_cycles: int,
    bounded_interval: int,
    bounded_retry_attempts: int,
    cycles: list[dict[str, Any]],
    blocked_cycles: list[dict[str, Any]],
    backoff_seconds: list[int],
    repair_queue: dict[str, Any],
    failure_learning_signal: dict[str, Any],
) -> dict[str, Any]:
    status = "healthy" if not blocked_cycles else "blocked"
    latest_cycle = cycles[-1] if cycles else {}
    latest_heartbeat_id = latest_cycle.get("heartbeat_id")
    whole_system_repair_candidates = release_health_heartbeat_repair_candidates_from_cycles(cycles)
    repair_queue = _repair_queue_with_whole_system_targets(
        repair_queue,
        whole_system_repair_candidates,
    )
    record = {
        "schema_version": schema_version,
        "surface_id": surface_id,
        "loop_id": loop_id,
        "generated_at": generated_at,
        "authority": "NexusBrain",
        "status_label": "LOCKED CANON",
        "status": status,
        "runtime_state": "live-evidence",
        "trigger": trigger,
        "product_surface": "wrapper",
        "session_ref_digest": session_ref_digest,
        "max_cycles": bounded_cycles,
        "cycle_count": len(cycles),
        "latest_heartbeat_id": latest_heartbeat_id,
        "cycles": cycles,
        "timer": {
            "interval_seconds": bounded_interval,
            "started_at": generated_at,
            "next_due_at": next_due_at,
            "sleep_performed": False,
            "background_thread_started": False,
            "scheduler_mode": "bounded-sync-supervisor-run",
        },
        "bounded_retry": {
            "bounded": True,
            "max_retry_attempts": bounded_retry_attempts,
            "attempt_count": len(blocked_cycles),
            "backoff_seconds": backoff_seconds,
            "policy": "exponential-backoff-recorded-no-sleep-no-active-production-mutation",
        },
        "product_scope": "whole-system",
        "whole_system_repair_candidates": whole_system_repair_candidates,
        "whole_system_target_surfaces": release_health_heartbeat_target_surfaces(
            whole_system_repair_candidates
        ),
        "repair_queue": repair_queue,
        "failure_learning_signal": failure_learning_signal,
        "evidence_refs": [
            "/ops/wrapper/release-runtime",
            "/ops/wrapper/release-readiness",
            "/ops/wrapper/release-health-heartbeat/run",
            heartbeat_artifact_ref,
            failure_learning_signal.get("signal_id") if isinstance(failure_learning_signal, dict) else None,
        ],
        "artifact_ref": artifact_ref,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": "sanitized-release-health-loop-status-counts-timers-and-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        "mutation_boundary": "bounded-supervisor-loop-proposal-only-no-active-production-mutation",
    }
    record["evidence_refs"] = [str(ref) for ref in record["evidence_refs"] if str(ref or "")]
    return record


def _repair_queue_with_whole_system_targets(
    repair_queue: dict[str, Any],
    whole_system_repair_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    queue = dict(repair_queue) if isinstance(repair_queue, dict) else {}
    target_surfaces = release_health_heartbeat_target_surfaces(
        whole_system_repair_candidates,
        fallback=[
            str(surface)
            for surface in queue.get("target_surfaces", [])
            if str(surface or "")
        ]
        if isinstance(queue.get("target_surfaces"), list)
        else None,
    )
    if whole_system_repair_candidates:
        queue["target_surfaces"] = target_surfaces
        queue["whole_system_candidate_count"] = len(whole_system_repair_candidates)
        queue["whole_system_candidate_gate_ids"] = release_health_heartbeat_candidate_gate_ids(
            whole_system_repair_candidates
        )
        queue["repair_scope"] = "whole-system-subsystem-governed-safe-artifact"
    queue["raw_content_included"] = False
    queue["active_production_mutation_allowed"] = False
    return queue


def _sanitize_repair_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    gate_id = str(candidate.get("gate_id") or "").strip()
    target_surfaces = _dedupe_strings(
        [
            str(surface)
            for surface in candidate.get("target_surfaces", [])
            if str(surface or "")
        ],
        limit=16,
    )
    sanitized = {
        "candidate_id": str(candidate.get("candidate_id") or f"whole-system-gate::{gate_id}"),
        "gate_id": gate_id,
        "status": str(candidate.get("status") or "blocked"),
        "target_surfaces": target_surfaces or list(WHOLE_SYSTEM_GATE_TARGET_SURFACES.get(gate_id, (gate_id,))),
        "blocking_check_ids": _bounded_strings(candidate.get("blocking_check_ids"), limit=16),
        "missing_check_ids": _bounded_strings(candidate.get("missing_check_ids"), limit=16),
        "nonblocking_check_ids": _bounded_strings(candidate.get("nonblocking_check_ids"), limit=16),
        "evidence_refs": _bounded_strings(candidate.get("evidence_refs"), limit=8),
        "repair_lane": "admin-approved-shadow-eval-sandbox-safe-file-apply-rollback",
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }
    if isinstance(candidate.get("recovery_governance"), dict):
        sanitized["recovery_governance"] = compact_failure_recovery_governance(
            candidate.get("recovery_governance")
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


def _safe_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0
