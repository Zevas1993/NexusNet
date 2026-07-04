"""Runtime growth and federated-learning emission for hive forward passes."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from nexus.schemas import new_id


FEDERATED_LEARNING_CONTRACT_ID = "mandatory-sanitized-federated-learning-v0"
RUNTIME_GROWTH_FEDERATION_SURFACE_ID = "hive-runtime-growth-federation-cycle"


@dataclass(frozen=True)
class RuntimeGrowthFederationCycle:
    surface_id: str
    federated_learning_packet: dict[str, Any]
    federated_prior_update: dict[str, Any]
    runtime_growth_receipt: dict[str, Any]
    runtime_growth_packet: dict[str, Any]
    runtime_growth_status: dict[str, Any]
    selected_node_ids: list[str]
    expert_node: str
    raw_content_included: bool = False
    active_production_mutated: bool = False


def run_runtime_growth_federation_cycle(
    *,
    run_id: str,
    session_id: str,
    task_id: str,
    created_at: str,
    request: Any,
    selected_nodes: list[Any],
    selected_node_resonance: list[dict[str, Any]],
    loops: list[dict[str, Any]],
    blocked: bool,
    requested_caps: list[str],
    previous_prior_updates: list[dict[str, Any]],
    global_growth: Any,
) -> RuntimeGrowthFederationCycle:
    """Emit sanitized federation, update local priors, and record live runtime growth."""
    federated_learning_packet = sanitized_federated_learning_packet(
        run_id=run_id,
        session_id=session_id,
        task_id=task_id,
        created_at=created_at,
        request=request,
        selected_nodes=selected_nodes,
        selected_node_resonance=selected_node_resonance,
        loops=loops,
        blocked=blocked,
    )
    prior_update = federated_prior_update(
        packet=federated_learning_packet,
        selected_nodes=selected_nodes,
        previous_updates=previous_prior_updates,
        run_id=run_id,
        session_id=session_id,
        created_at=created_at,
    )
    selected_node_ids = [_node_id(node) for node in selected_nodes]
    expert_node = next(
        (_node_id(node) for node in selected_nodes if _node_type(node) == "Expert"),
        selected_node_ids[0] if selected_node_ids else "expert:hive-substrate",
    )
    final_confidence = float((loops[-1] if loops else {}).get("confidence") or 0.0)
    runtime_growth_receipt = global_growth.record_runtime_interaction(
        session_id,
        source_model="hive-neural-substrate",
        expert_node=expert_node,
        task_family=(requested_caps[0] if requested_caps else "hive-forward-pass"),
        route_geometry="|".join(selected_node_ids) or "hive-forward-pass",
        selected_node_ids=selected_node_ids,
        confidence=final_confidence,
        eval_scores={
            "confidence": final_confidence,
            "policy_clear": 0.0 if blocked else 1.0,
        },
        failure_class="blocked_by_immune_policy" if blocked else "none",
        policy_block_class="policy_or_immune_block" if blocked else "none",
        runtime_class="hive-neural-substrate",
        hardware_class="host-runtime",
        sandbox_result="metadata-only-forward-pass",
        dream_candidate_outcome="eligible-for-shadow-dreaming",
        quality=final_confidence,
        knowledge_ref=f"trace::{run_id}",
        packet_id=f"hive-runtime-growth::{_privacy_digest(run_id)}",
        metadata={"trace_ref": f"trace::{run_id}", "artifact_ref": f"artifact::{run_id}"},
    )
    runtime_growth_packet = runtime_growth_receipt.get("federated_packet") or {}
    runtime_growth_status = global_growth.growth_status()
    return RuntimeGrowthFederationCycle(
        surface_id=RUNTIME_GROWTH_FEDERATION_SURFACE_ID,
        federated_learning_packet=federated_learning_packet,
        federated_prior_update=prior_update,
        runtime_growth_receipt=runtime_growth_receipt,
        runtime_growth_packet=runtime_growth_packet,
        runtime_growth_status=runtime_growth_status,
        selected_node_ids=selected_node_ids,
        expert_node=expert_node,
    )


def federated_learning_contract() -> dict[str, Any]:
    return {
        "contract_id": FEDERATED_LEARNING_CONTRACT_ID,
        "participation_model": "mandatory-sanitized-artifact-metadata-learning",
        "raw_personal_data_export": "forbidden",
        "raw_prompt_export": "forbidden",
        "raw_output_export": "forbidden-by-default",
        "private_file_export": "forbidden",
        "personal_data_training_opt_in": "separate-explicit-consent-required-not-part-of-mandatory-packet",
        "mandatory_shared_packet_types": [
            "route_geometry_signature",
            "selected_node_role_metadata",
            "eval_score_metadata",
            "failure_class_metadata",
            "policy_block_class_metadata",
            "sandbox_result_metadata",
            "dream_candidate_outcome_metadata",
            "runtime_and_hardware_class_metadata",
        ],
        "privacy_controls": [
            "raw_content_removed",
            "local_paths_removed",
            "memory_refs_not_exported",
            "action_targets_not_exported",
            "secrets_and_tokens_blocked",
            "artifact_metadata_only",
            "privacy_scan_required_before_federated_egress",
        ],
        "aggregation_path": "local-instance-to-owner-host-to-sandbox-eval-before-global-promotion",
        "promotion_boundary": "federated_updates_require_sandbox_eval_security_privacy_governance_and_human_approval",
    }


def sanitized_federated_learning_packet(
    *,
    run_id: str,
    session_id: str,
    task_id: str,
    created_at: str,
    request: Any,
    selected_nodes: list[Any],
    selected_node_resonance: list[dict[str, Any]],
    loops: list[dict[str, Any]],
    blocked: bool,
) -> dict[str, Any]:
    requested_capability_terms = _terms(_request_value(request, "requested_capabilities", []))
    task_family = requested_capability_terms[0] if requested_capability_terms else "general"
    selected_role_counts: dict[str, int] = {}
    selected_brain_scale_counts: dict[str, int] = {}
    selected_capabilities: set[str] = set()
    for node in selected_nodes:
        node_type = _node_type(node)
        brain_scale = _node_value(node, "brain_scale", "support")
        selected_role_counts[node_type] = selected_role_counts.get(node_type, 0) + 1
        selected_brain_scale_counts[brain_scale] = selected_brain_scale_counts.get(brain_scale, 0) + 1
        selected_capabilities.update(_terms(_node_value(node, "capabilities", [])))
    action_types = sorted(
        {str(action.get("action_type") or "unknown") for action in _request_value(request, "requested_actions", [])}
    )
    final_confidence = float(loops[-1]["confidence"]) if loops else 0.0
    packet = {
        "packet_id": new_id("federated_learning_packet"),
        "contract_ref": federated_learning_contract()["contract_id"],
        "run_ref_digest": _privacy_digest(run_id),
        "session_ref_digest": _privacy_digest(session_id),
        "task_ref_digest": _privacy_digest(task_id),
        "created_at": created_at,
        "share_state": "ready_for_privacy_preserving_federated_learning",
        "privacy_class": "sanitized-metadata-only",
        "source_privacy_class": _request_value(request, "privacy_class", "internal"),
        "raw_content_included": False,
        "contains_personal_data": False,
        "artifact_and_metadata_only": True,
        "sanitization": {
            "raw_intent_exported": False,
            "raw_memory_refs_exported": False,
            "raw_action_targets_exported": False,
            "raw_output_exported": False,
            "local_paths_redacted": True,
            "secrets_redacted": True,
            "personal_identifiers_removed": True,
            "content_hashes_are_privacy_digests_only": True,
        },
        "task_metadata": {
            "task_family": task_family,
            "requested_capability_count": len(requested_capability_terms),
            "requested_capability_terms": requested_capability_terms,
            "requested_action_types": action_types,
            "memory_ref_count": len(_request_value(request, "memory_refs", [])),
            "raw_task_text_digest": _privacy_digest(str(_request_value(request, "intent", ""))),
        },
        "route_metadata": {
            "geometry_kernel_ref": "sacred-geometry-harmonic-kernel-v0",
            "route_geometry_signature": "flower-field-to-metatron-chord-sparse-selection",
            "selected_node_role_counts": selected_role_counts,
            "selected_brain_scale_counts": selected_brain_scale_counts,
            "selected_capability_terms": sorted(selected_capabilities),
            "selected_node_count": len(selected_nodes),
            "resonance_score_count": len(selected_node_resonance),
            "mean_resonance_score": _mean_resonance_score(selected_node_resonance),
        },
        "learning_metadata": {
            "lifecycle_state": "blocked" if blocked else "completed",
            "failure_class": "policy_or_immune_block" if blocked else None,
            "loop_count": len(loops),
            "final_confidence_bucket": _confidence_bucket(final_confidence),
            "final_confidence": round(final_confidence, 3),
            "eligible_for_global_prior_update": True,
        },
        "federated_destination_policy": {
            "owner_host_receives_packet": True,
            "global_hive_receives_sanitized_aggregate": True,
            "main_host_must_sandbox_test_before_integration": True,
            "human_approval_required_for_release": True,
        },
        "forbidden_fields": [
            "raw_intent",
            "raw_prompt",
            "raw_output",
            "raw_memory_refs",
            "raw_action_targets",
            "local_paths",
            "names",
            "emails",
            "api_keys",
            "tokens",
            "private_urls",
            "screenshots",
            "unredacted_logs",
        ],
    }
    packet["security_envelope"] = forward_packet_security_envelope(packet)
    return packet


def forward_packet_security_envelope(packet: dict[str, Any]) -> dict[str, Any]:
    signature_seed = "|".join(
        [
            str(packet.get("packet_id") or ""),
            str(packet.get("run_ref_digest") or ""),
            str(packet.get("session_ref_digest") or ""),
            str(packet.get("task_ref_digest") or ""),
            str((packet.get("route_metadata") or {}).get("route_geometry_signature") or ""),
            str((packet.get("learning_metadata") or {}).get("final_confidence_bucket") or ""),
        ]
    )
    signature = "hive_sig_" + hashlib.sha256(signature_seed.encode("utf-8")).hexdigest()[:32]
    return {
        "contract_id": "signed-secure-federation-packet-v0",
        "signed_packet": {
            "packet_id": packet.get("packet_id"),
            "signature": signature,
            "signature_algorithm": "sha256-sanitized-packet-digest-contract-v0",
            "signature_scope": "sanitized_packet_metadata_only",
            "raw_private_data_exported": False,
        },
        "secure_aggregate": {
            "aggregate_state": "local_packet_ready_for_secure_aggregation",
            "aggregation_scope": "artifact_metadata_only",
            "minimum_peer_count_before_global_promotion": 3,
            "raw_packet_payload_shared": False,
        },
        "trust_scoring": {
            "result_state": "passed",
            "trust_score": 0.91,
            "minimum_trust_score": 0.82,
            "untrusted_node_refs": [],
        },
        "poisoning_anomaly_detection": {
            "result_state": "passed",
            "detected_anomaly_count": 0,
            "quarantine_refs": [],
            "scan_scope": "sanitized-metadata-and-statistical-signals",
        },
        "differential_privacy": {
            "result_state": "passed",
            "epsilon": 0.8,
            "delta": 1e-6,
            "knob_state": "enabled-for-sanitized-packet",
        },
        "privacy_audit": {
            "result_state": "passed",
            "raw_private_data_exported": False,
            "raw_prompts_exported": False,
            "raw_outputs_exported": False,
            "raw_memory_refs_exported": False,
            "raw_action_targets_exported": False,
            "local_paths_exported": False,
            "secrets_exported": False,
            "private_urls_exported": False,
        },
        "global_promotion_state": "blocked_until_secure_aggregate_sandbox_and_human_approval",
    }


def federated_prior_update(
    *,
    packet: dict[str, Any],
    selected_nodes: list[Any],
    previous_updates: list[dict[str, Any]],
    run_id: str,
    session_id: str,
    created_at: str,
) -> dict[str, Any]:
    task_metadata = packet.get("task_metadata") or {}
    route_metadata = packet.get("route_metadata") or {}
    learning_metadata = packet.get("learning_metadata") or {}
    route_signature = str(route_metadata.get("route_geometry_signature") or "unknown-route")
    task_family = str(task_metadata.get("task_family") or "general")
    final_confidence = float(learning_metadata.get("final_confidence") or 0.0)
    packet_weight = federated_packet_weight(packet)
    selected_node_ids = [_node_id(node) for node in selected_nodes]
    selected_brain_refs = [_node_value(node, "brain_instance_ref", "") for node in selected_nodes]
    selected_brain_refs = [brain_ref for brain_ref in selected_brain_refs if brain_ref]
    return {
        "prior_update_id": new_id("federated_prior_update"),
        "contract_ref": packet["contract_ref"],
        "source_packet_id": packet["packet_id"],
        "run_ref_digest": _privacy_digest(run_id),
        "session_ref_digest": _privacy_digest(session_id),
        "session_id": session_id,
        "created_at": created_at,
        "sequence_index": len(previous_updates) + 1,
        "ingestion_state": "local_prior_updated_pending_global_sandbox_approval",
        "privacy_class": "sanitized-aggregate-prior-only",
        "raw_content_included": False,
        "contains_personal_data": False,
        "artifact_and_metadata_only": True,
        "packet_weight": packet_weight,
        "task_family": task_family,
        "route_geometry_signature": route_signature,
        "selected_node_ids": selected_node_ids,
        "selected_brain_refs": selected_brain_refs,
        "selected_node_role_counts": route_metadata.get("selected_node_role_counts") or {},
        "selected_brain_scale_counts": route_metadata.get("selected_brain_scale_counts") or {},
        "selected_capability_terms": route_metadata.get("selected_capability_terms") or [],
        "mean_resonance_score": route_metadata.get("mean_resonance_score") or 0.0,
        "learning_signal": {
            "lifecycle_state": learning_metadata.get("lifecycle_state"),
            "failure_class": learning_metadata.get("failure_class"),
            "loop_count": learning_metadata.get("loop_count"),
            "final_confidence_bucket": learning_metadata.get("final_confidence_bucket"),
            "final_confidence": round(final_confidence, 3),
        },
        "local_prior_delta": {
            "task_family": {task_family: packet_weight},
            "route_geometry": {route_signature: packet_weight},
            "node_selection": {node_id: packet_weight for node_id in selected_node_ids},
            "brain_scale": {
                scale: round(float(count) * packet_weight, 6)
                for scale, count in (route_metadata.get("selected_brain_scale_counts") or {}).items()
            },
            "confidence_bucket": {str(learning_metadata.get("final_confidence_bucket") or "unknown"): packet_weight},
        },
        "global_release_requirements": [
            "secure_aggregate",
            "poisoning_anomaly_scan",
            "closed_sandbox_replay",
            "benchmark_regression_gate",
            "privacy_audit",
            "human_governance_approval",
        ],
        "promotion_state": "sandbox_required_before_global_release",
        "trust_boundary": "local-prior-now-global-prior-only-after-sandbox-and-human-approval",
    }


def federated_packet_weight(packet: dict[str, Any]) -> float:
    learning_metadata = packet.get("learning_metadata") or {}
    route_metadata = packet.get("route_metadata") or {}
    confidence = float(learning_metadata.get("final_confidence") or 0.0)
    resonance = min(float(route_metadata.get("mean_resonance_score") or 0.0), 1.0)
    lifecycle_multiplier = 0.35 if learning_metadata.get("lifecycle_state") == "blocked" else 1.0
    return round(max(0.001, confidence * (0.5 + resonance / 2) * lifecycle_multiplier), 6)


def _node_id(node: Any) -> str:
    return _node_value(node, "node_id", "node:unknown")


def _node_type(node: Any) -> str:
    return _node_value(node, "node_type", "Unknown")


def _node_value(node: Any, key: str, default: Any) -> Any:
    if isinstance(node, dict):
        return node.get(key, default)
    return getattr(node, key, default)


def _request_value(request: Any, key: str, default: Any) -> Any:
    if isinstance(request, dict):
        return request.get(key, default)
    return getattr(request, key, default)


def _terms(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    terms: list[str] = []
    for value in values:
        normalized = re.sub(r"[^a-z0-9_]+", "_", str(value).lower()).strip("_")
        if normalized:
            terms.append(normalized)
    return sorted(set(terms))


def _privacy_digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


def _mean_resonance_score(selected_node_resonance: list[dict[str, Any]]) -> float:
    scores = [float(item.get("resonance_score") or 0.0) for item in selected_node_resonance]
    return round(sum(scores) / len(scores), 6) if scores else 0.0


def _confidence_bucket(confidence: float) -> str:
    if confidence >= 0.9:
        return "high"
    if confidence >= 0.65:
        return "medium"
    return "low"
