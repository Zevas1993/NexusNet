from __future__ import annotations

import hashlib
from typing import Any


def project_heartbeat_payload(
    *,
    run_id: str,
    session_id: str,
    created_at: str,
    blocked: bool,
    nodes: list[Any],
    selected_nodes: list[Any],
    activation: dict[str, Any],
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    plane_trace: dict[str, Any],
    neural_pathway_map: dict[str, Any],
    synaptic_transmission_ledger: dict[str, Any],
    forward_propagation_ledger: dict[str, Any],
    runtime_growth_receipt: dict[str, Any],
    runtime_growth_packet: dict[str, Any],
    federated_learning_packet: dict[str, Any],
    federated_prior_update: dict[str, Any],
    federated_influence_ledger: dict[str, Any],
    executable_dream_cycle_ledger: dict[str, Any],
    checkpoint: dict[str, Any],
    checkpoint_coverage_ledger: dict[str, Any],
    runtime_decision_ledger: dict[str, Any],
    backend_quantization_execution_ledger: dict[str, Any],
    durable_storage_ledger: dict[str, Any],
    deep_replay_drilldown_ledger: dict[str, Any],
    health_event: dict[str, Any],
    self_healing_route_around: dict[str, Any] | None,
    policy_scan: dict[str, Any],
    immune_findings: list[dict[str, Any]],
    source_brain_generate_status: str | None = None,
) -> dict[str, Any]:
    policy_summary = policy_scan.get("summary") if isinstance(policy_scan.get("summary"), dict) else {}
    normalized_brain_generate_status = _normalized_brain_generate_status(source_brain_generate_status)
    source_runtime_degraded = normalized_brain_generate_status in {
        "blocked",
        "error",
        "failed",
        "runtime-unavailable",
    }
    nexus_brain_present = any(_node_type(node) == "NexusBrain" for node in nodes)
    selected_node_ids = [_node_id(node) for node in selected_nodes if _node_id(node)]
    self_healing_refs = heartbeat_payload_refs(
        ("health-event", health_event, "health_event_id"),
        ("route-around", self_healing_route_around, "route_around_id"),
    )
    lanes = [
        project_heartbeat_lane(
            lane_id="model-serving-runtime",
            label="NexusBrain model-serving runtime result for this forward pass",
            status_if_alive=not source_runtime_degraded,
            artifact_refs=[f"brain-generate-status::{normalized_brain_generate_status}"],
            blockers=(
                [f"model-serving-runtime-{normalized_brain_generate_status}"]
                if source_runtime_degraded
                else []
            ),
        ),
        project_heartbeat_lane(
            lane_id="nexus-brain",
            label="NexusBrain authority and selected brain-bearing nodes",
            status_if_alive=nexus_brain_present and bool(selected_node_ids) and not blocked,
            artifact_refs=[
                "authority::NexusBrain",
                *[f"node::{node_id}" for node_id in selected_node_ids[:8]],
            ],
            blockers=[] if nexus_brain_present and selected_node_ids and not blocked else ["nexus_brain_route_missing_or_blocked"],
        ),
        project_heartbeat_lane(
            lane_id="native-hive-substrate",
            label="Native hive substrate activation, bus, blackboard, and plane trace",
            status_if_alive=all(
                [
                    activation.get("activation_id"),
                    neural_bus.get("bus_id"),
                    hive_blackboard.get("residual_state_id"),
                    plane_trace.get("trace_ledger_id"),
                    not blocked,
                ]
            ),
            artifact_refs=heartbeat_payload_refs(
                ("activation", activation, "activation_id"),
                ("neural-bus", neural_bus, "bus_id"),
                ("blackboard", hive_blackboard, "residual_state_id"),
                ("plane-trace", plane_trace, "trace_ledger_id"),
            ),
            blockers=[] if not blocked else ["native_hive_forward_pass_blocked"],
        ),
        project_heartbeat_lane(
            lane_id="neural-signal-path",
            label="Neural pathway, synaptic transmission, and forward propagation",
            status_if_alive=all(
                [
                    neural_pathway_map.get("pathway_id"),
                    synaptic_transmission_ledger.get("transmission_id"),
                    forward_propagation_ledger.get("propagation_id"),
                    not blocked,
                ]
            ),
            artifact_refs=heartbeat_payload_refs(
                ("pathway", neural_pathway_map, "pathway_id"),
                ("synaptic-transmission", synaptic_transmission_ledger, "transmission_id"),
                ("forward-propagation", forward_propagation_ledger, "propagation_id"),
            ),
            blockers=[] if not blocked else ["neural_signal_path_blocked"],
        ),
        project_heartbeat_lane(
            lane_id="growth-engine",
            label="Runtime growth receipt and growth federated packet",
            status_if_alive=bool(runtime_growth_receipt.get("receipt_id")) and not blocked,
            artifact_refs=heartbeat_payload_refs(
                ("runtime-growth", runtime_growth_receipt, "receipt_id"),
                ("runtime-growth-packet", runtime_growth_packet, "packet_id"),
            ),
            blockers=[] if runtime_growth_receipt.get("receipt_id") and not blocked else ["runtime_growth_receipt_missing"],
        ),
        project_heartbeat_lane(
            lane_id="federation-runtime",
            label="Sanitized federation packet, prior update, and influence loop",
            status_if_alive=all(
                [
                    federated_learning_packet.get("packet_id"),
                    federated_prior_update.get("prior_update_id"),
                    federated_influence_ledger.get("federated_influence_id"),
                    not blocked,
                ]
            ),
            artifact_refs=heartbeat_payload_refs(
                ("federated-packet", federated_learning_packet, "packet_id"),
                ("federated-prior", federated_prior_update, "prior_update_id"),
                ("federated-influence", federated_influence_ledger, "federated_influence_id"),
            ),
            blockers=[] if not blocked else ["federation_runtime_blocked"],
        ),
        project_heartbeat_lane(
            lane_id="dream-runtime",
            label="Executable recursive dream cycle",
            status_if_alive=bool(executable_dream_cycle_ledger.get("dream_cycle_id")) and not blocked,
            artifact_refs=heartbeat_payload_refs(
                ("dream-cycle", executable_dream_cycle_ledger, "dream_cycle_id"),
            ),
            blockers=[] if executable_dream_cycle_ledger.get("dream_cycle_id") and not blocked else ["dream_cycle_missing"],
        ),
        project_heartbeat_lane(
            lane_id="checkpoint-rewind",
            label="Checkpoint and checkpoint coverage",
            status_if_alive=all(
                [
                    checkpoint.get("checkpoint_id"),
                    checkpoint_coverage_ledger.get("coverage_ledger_id"),
                ]
            ),
            artifact_refs=heartbeat_payload_refs(
                ("checkpoint", checkpoint, "checkpoint_id"),
                ("checkpoint-coverage", checkpoint_coverage_ledger, "coverage_ledger_id"),
            ),
            blockers=[] if checkpoint.get("checkpoint_id") else ["checkpoint_missing"],
        ),
        project_heartbeat_lane(
            lane_id="runtime-decision",
            label="Artifact-bound runtime decision and backend quantization execution",
            status_if_alive=all(
                [
                    runtime_decision_ledger.get("runtime_decision_id"),
                    backend_quantization_execution_ledger.get("backend_execution_id"),
                    not blocked,
                ]
            ),
            artifact_refs=heartbeat_payload_refs(
                ("runtime-decision", runtime_decision_ledger, "runtime_decision_id"),
                ("backend-execution", backend_quantization_execution_ledger, "backend_execution_id"),
            ),
            blockers=[] if not blocked else ["runtime_decision_blocked"],
        ),
        project_heartbeat_lane(
            lane_id="storage-replay",
            label="Durable storage and deep replay drilldown",
            status_if_alive=all(
                [
                    durable_storage_ledger.get("storage_ledger_id"),
                    deep_replay_drilldown_ledger.get("replay_drilldown_id"),
                ]
            ),
            artifact_refs=heartbeat_payload_refs(
                ("durable-storage", durable_storage_ledger, "storage_ledger_id"),
                ("deep-replay", deep_replay_drilldown_ledger, "replay_drilldown_id"),
            ),
            blockers=[] if durable_storage_ledger.get("storage_ledger_id") else ["durable_storage_missing"],
        ),
        project_heartbeat_lane(
            lane_id="policy-immune",
            label="Policy kernel, immune scan, health event, and route-around boundary",
            status_if_alive=(
                policy_summary.get("allow_merge") is True
                and not immune_findings
                and bool(health_event.get("health_event_id"))
            ),
            artifact_refs=[
                "policy-scan::allow_merge",
                "immune-findings::clear" if not immune_findings else "immune-findings::blocked",
                *self_healing_refs,
            ],
            blockers=[] if policy_summary.get("allow_merge") is True and not immune_findings else ["policy_or_immune_blocked"],
        ),
    ]
    alive_lanes = [lane for lane in lanes if lane["status"] == "alive"]
    degraded_lanes = [lane for lane in lanes if lane["status"] != "alive"]
    status = "alive" if not degraded_lanes else "degraded"
    failure_recovery_governance = project_heartbeat_failure_recovery_governance(
        blocked=blocked or source_runtime_degraded,
        health_event=health_event,
        self_healing_route_around=self_healing_route_around,
        checkpoint=checkpoint,
        runtime_growth_receipt=runtime_growth_receipt,
        federated_learning_packet=federated_learning_packet,
        executable_dream_cycle_ledger=executable_dream_cycle_ledger,
        policy_summary=policy_summary,
        immune_findings=immune_findings,
    )
    return {
        "schema_version": "nexusnet-project-heartbeat-v1",
        "surface_id": "nexusnet-project-heartbeat",
        "authority": "NexusBrain",
        "status_label": "LOCKED CANON",
        "status": status,
        "honest_status_label": (
            "core-substrate-heartbeat-alive"
            if status == "alive"
            else "core-substrate-heartbeat-degraded"
        ),
        "trigger": "hive-forward-pass",
        "heartbeat_id": f"project-heartbeat::{privacy_digest(run_id)}",
        "generated_at": created_at,
        "source_run_id": run_id,
        "source_trace_ref": f"trace::{run_id}",
        "source_brain_generate_status": normalized_brain_generate_status,
        "source_runtime_degraded": source_runtime_degraded,
        "session_ref_digest": privacy_digest(session_id),
        "lane_count": len(lanes),
        "alive_lane_count": len(alive_lanes),
        "degraded_lane_count": len(degraded_lanes),
        "degraded_lane_ids": [lane["lane_id"] for lane in degraded_lanes],
        "lanes": lanes,
        "failure_recovery_governance": failure_recovery_governance,
        "evidence_refs": dedupe_strings([ref for lane in lanes for ref in lane.get("artifact_refs", [])])[:48],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": "sanitized-core-organ-status-counts-and-artifact-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        "mutation_boundary": "heartbeat-status-and-artifact-refs-only-no-active-production-mutation",
    }


def project_heartbeat_failure_recovery_governance(
    *,
    blocked: bool,
    health_event: dict[str, Any],
    self_healing_route_around: dict[str, Any] | None,
    checkpoint: dict[str, Any],
    runtime_growth_receipt: dict[str, Any],
    federated_learning_packet: dict[str, Any],
    executable_dream_cycle_ledger: dict[str, Any],
    policy_summary: dict[str, Any],
    immune_findings: list[dict[str, Any]],
) -> dict[str, Any]:
    route_available = bool(
        isinstance(self_healing_route_around, dict)
        and self_healing_route_around.get("route_around_id")
    )
    status = (
        "degraded-recovery-governed"
        if blocked and route_available
        else "degraded-recovery-missing"
        if blocked
        else "live-bound-idle"
    )
    return {
        "surface_id": "native-project-heartbeat-failure-recovery-governance",
        "authority": "NexusBrain",
        "status": status,
        "runtime_state": "degraded" if blocked else "live-bound",
        "blocked_forward_pass": bool(blocked),
        "self_healing_route_available": route_available,
        "admin_governance_required": bool(blocked),
        "sandbox_eval_required": bool(blocked),
        "rollback_required": bool(blocked),
        "recovery_action": (
            "route-around-and-queue-governed-repair"
            if blocked and route_available
            else "record-healthy-heartbeat"
            if not blocked
            else "queue-governed-repair-without-route-around"
        ),
        "policy_allow_merge": policy_summary.get("allow_merge") is True,
        "immune_finding_count": len(immune_findings),
        "evidence_refs": heartbeat_payload_refs(
            ("health-event", health_event, "health_event_id"),
            ("route-around", self_healing_route_around, "route_around_id"),
            ("checkpoint", checkpoint, "checkpoint_id"),
            ("runtime-growth", runtime_growth_receipt, "receipt_id"),
            ("federated-packet", federated_learning_packet, "packet_id"),
            ("dream-cycle", executable_dream_cycle_ledger, "dream_cycle_id"),
        )[:24],
        "operator_governance_boundary": (
            "heartbeat-record-only-until-admin-approved-sandbox-eval-rollback-path"
        ),
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def project_heartbeat_lane(
    *,
    lane_id: str,
    label: str,
    status_if_alive: bool,
    artifact_refs: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    status = "alive" if status_if_alive else "degraded"
    return {
        "lane_id": lane_id,
        "label": label,
        "status": status,
        "honest_status_label": (
            "core-organ-receipt-present"
            if status == "alive"
            else "core-organ-receipt-missing-or-blocked"
        ),
        "artifact_refs": dedupe_strings(artifact_refs)[:12],
        "blockers": dedupe_strings(blockers if status != "alive" else [])[:12],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def heartbeat_payload_refs(*items: tuple[str, dict[str, Any] | None, str]) -> list[str]:
    refs: list[str] = []
    for prefix, payload, key in items:
        if not isinstance(payload, dict):
            continue
        value = str(payload.get(key) or "").strip()
        if value:
            refs.append(f"{prefix}::{value}")
    return dedupe_strings(refs)


def dedupe_strings(values: Any) -> list[str]:
    if isinstance(values, str):
        candidates = [values]
    elif isinstance(values, list):
        candidates = values
    else:
        candidates = []
    seen: set[str] = set()
    result: list[str] = []
    for value in candidates:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def privacy_digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


def _node_id(node: Any) -> str:
    return str(getattr(node, "node_id", "") or "")


def _node_type(node: Any) -> str:
    return str(getattr(node, "node_type", "") or "")


def _normalized_brain_generate_status(value: Any) -> str:
    status = str(value or "unknown").strip().lower()
    if status not in {
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
        return "unknown"
    return status
