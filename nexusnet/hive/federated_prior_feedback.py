"""Federated prior feedback into shadow routing and recursive dreaming."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nexus.schemas import new_id
from nexusnet.hive.runtime_growth_federation import FEDERATED_LEARNING_CONTRACT_ID


FEDERATED_PRIOR_FEEDBACK_SURFACE_ID = "hive-federated-prior-feedback-cycle"
FEDERATED_PRIOR_FEEDBACK_REF = "federated-prior-feedback-cycle-v0"


@dataclass(frozen=True)
class FederatedPriorFeedbackCycle:
    surface_id: str
    status: str
    prior_ledger: dict[str, Any]
    shadow_routing: dict[str, Any]
    dream_context: dict[str, Any]
    control_panel_status: dict[str, Any]
    raw_content_included: bool = False
    active_production_mutated: bool = False


def run_federated_prior_feedback_cycle(
    *,
    prior_updates: list[dict[str, Any]],
    selected_nodes: list[Any] | None = None,
    selected_node_resonance: list[dict[str, Any]] | None = None,
    dream_request: Any | None = None,
    health_events: list[dict[str, Any]] | None = None,
    candidates: list[dict[str, Any]] | None = None,
) -> FederatedPriorFeedbackCycle:
    prior_ledger = federated_prior_ledger(prior_updates)
    shadow_routing = shadow_routing_payload(
        selected_nodes=selected_nodes or [],
        selected_node_resonance=selected_node_resonance or [],
        prior_ledger=prior_ledger,
    )
    dream_context = dream_context_payload(
        request=dream_request,
        health_events=health_events or [],
        candidates=candidates or [],
        prior_ledger=prior_ledger,
        shadow_routing=shadow_routing,
    )
    control_panel_status = federated_prior_feedback_status(
        prior_ledger=prior_ledger,
        shadow_routing=shadow_routing,
        dream_context=dream_context,
    )
    return FederatedPriorFeedbackCycle(
        surface_id=FEDERATED_PRIOR_FEEDBACK_SURFACE_ID,
        status=control_panel_status["status"],
        prior_ledger=prior_ledger,
        shadow_routing=shadow_routing,
        dream_context=dream_context,
        control_panel_status=control_panel_status,
    )


def federated_prior_ledger(prior_updates: list[dict[str, Any]]) -> dict[str, Any]:
    sorted_updates = sorted(prior_updates, key=lambda item: str(item.get("created_at") or ""))
    task_family_priors = _sum_prior_deltas(sorted_updates, "task_family")
    route_geometry_priors = _route_geometry_priors(sorted_updates)
    node_selection_priors = _sum_prior_deltas(sorted_updates, "node_selection")
    brain_scale_priors = _sum_prior_deltas(sorted_updates, "brain_scale")
    confidence_bucket_priors = _sum_prior_deltas(sorted_updates, "confidence_bucket")
    sanitized_count = sum(
        1
        for update in sorted_updates
        if update.get("raw_content_included") is False and update.get("contains_personal_data") is False
    )
    return {
        "ledger_id": "federated-prior-ledger-v0",
        "contract_ref": FEDERATED_LEARNING_CONTRACT_ID,
        "packet_count": len(sorted_updates),
        "sanitized_packet_count": sanitized_count,
        "prior_update_count": len(sorted_updates),
        "privacy_boundary": {
            "raw_personal_data_export": "forbidden",
            "raw_content_included": False,
            "contains_personal_data": False,
            "aggregate_class": "sanitized-artifact-and-metadata-priors-only",
        },
        "task_family_priors": task_family_priors,
        "route_geometry_priors": route_geometry_priors,
        "node_selection_priors": node_selection_priors,
        "brain_scale_priors": brain_scale_priors,
        "confidence_bucket_priors": confidence_bucket_priors,
        "routing_prior_suggestions": _routing_prior_suggestions(route_geometry_priors),
        "promotion_boundary": "local_prior_can_update_immediately_global_update_requires_sandbox_security_privacy_and_human_approval",
        "poisoning_defense_required": True,
        "latest_prior_update_id": sorted_updates[-1].get("prior_update_id") if sorted_updates else None,
    }


def shadow_routing_payload(
    *,
    selected_nodes: list[Any],
    selected_node_resonance: list[dict[str, Any]],
    prior_ledger: dict[str, Any],
) -> dict[str, Any]:
    node_priors = prior_ledger.get("node_selection_priors") or {}
    candidates = []
    resonance_by_node = {
        item.get("node_id"): float(item.get("resonance_score") or 0.0)
        for item in selected_node_resonance
    }
    for node in selected_nodes:
        node_id = _node_id(node)
        prior_weight = float(node_priors.get(node_id) or 0.0)
        resonance = resonance_by_node.get(node_id, 0.0)
        candidates.append(
            {
                "node_id": node_id,
                "node_type": _node_value(node, "node_type", "Unknown"),
                "baseline_resonance_score": resonance,
                "sanitized_prior_weight": round(prior_weight, 6),
                "shadow_weight": round(resonance + prior_weight * 0.1, 6),
                "promotion_state": "eval_required_before_active_routing_change",
            }
        )
    candidates.sort(key=lambda item: (-item["shadow_weight"], item["node_id"]))
    baseline_quality = round(
        sum(resonance_by_node.get(_node_id(node), 0.0) for node in selected_nodes) / max(len(selected_nodes), 1),
        6,
    )
    shadow_quality = round(
        sum(item["shadow_weight"] for item in candidates[: max(len(selected_nodes), 1)]) / max(len(selected_nodes), 1),
        6,
    )
    quality_delta = round(shadow_quality - baseline_quality, 6)
    return {
        "shadow_routing_id": new_id("shadow_routing"),
        "shadow_state": "evaluating" if prior_ledger.get("prior_update_count") else "awaiting_priors",
        "prior_source": "FederatedPriorLedger",
        "baseline_selected_node_ids": [_node_id(node) for node in selected_nodes],
        "prior_ledger_ref": prior_ledger.get("ledger_id"),
        "prior_update_count": prior_ledger.get("prior_update_count", 0),
        "prior_weighted_candidates": candidates,
        "quality_comparison": {
            "comparison_state": "shadow_computed_no_active_mutation",
            "baseline_route_quality": baseline_quality,
            "shadow_route_quality": shadow_quality,
            "quality_delta": quality_delta,
            "baseline_order": [_node_id(node) for node in selected_nodes],
            "shadow_order": [item["node_id"] for item in candidates],
        },
        "promotion_state": "shadow_only_pending_eval_sandbox_governance",
        "promotion_gate": {
            "gate_state": "blocked_until_eval_sandbox_governance",
            "active_route_mutated": False,
            "minimum_delta_required": 0.01,
            "quality_delta": quality_delta,
            "required_approvals": [
                "shadow_route_eval_delta",
                "closed_sandbox_replay",
                "policy_scan",
                "human_governance_approval",
            ],
        },
        "active_route_mutated": False,
        "required_evidence_before_promotion": [
            "shadow_route_eval_delta",
            "closed_sandbox_replay",
            "policy_scan",
            "human_governance_approval",
        ],
    }


def dream_context_payload(
    *,
    request: Any | None,
    health_events: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    prior_ledger: dict[str, Any],
    shadow_routing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    degraded_health_events = [
        event
        for event in health_events
        if event.get("event_state") == "degraded_observed"
        or event.get("policy_block_count")
        or event.get("immune_response_count")
    ]
    failed_candidates = [
        candidate
        for candidate in candidates
        if candidate.get("lifecycle_state") == "blocked"
        or "closed_sandbox_eval_failed" in (candidate.get("blocked_reasons") or [])
        or (
            (
                (candidate.get("closed_sandbox_evaluation") or {}).get("promotion_decision")
                or {}
            ).get("decision_state")
            == "failed_blocks_promotion"
        )
    ]
    failure_terms = set()
    for candidate in failed_candidates:
        failure_terms.update(str(reason) for reason in (candidate.get("blocked_reasons") or []) if reason)
    for event in degraded_health_events:
        if event.get("event_state"):
            failure_terms.add(str(event.get("event_state")))
        if event.get("policy_block_count"):
            failure_terms.add("policy_block")
        if event.get("immune_response_count"):
            failure_terms.add("immune_response")
    status = federated_prior_feedback_status(
        prior_ledger=prior_ledger,
        shadow_routing=shadow_routing,
    )
    return {
        "context_contract": "failure-prior-research-conditioned-dreaming-v0",
        "consumed_health_event_refs": [
            str(event.get("health_event_id"))
            for event in degraded_health_events
            if event.get("health_event_id")
        ],
        "consumed_failed_candidate_refs": [
            str(candidate.get("candidate_run_id"))
            for candidate in failed_candidates
            if candidate.get("candidate_run_id")
        ],
        "consumed_prior_ledger": {
            "ledger_id": prior_ledger.get("ledger_id"),
            "prior_update_count": prior_ledger.get("prior_update_count", 0),
            "task_family_priors": prior_ledger.get("task_family_priors") or {},
            "brain_scale_priors": prior_ledger.get("brain_scale_priors") or {},
        },
        "federated_prior_feedback": {
            "surface_id": FEDERATED_PRIOR_FEEDBACK_SURFACE_ID,
            "status": status["status"],
            "honest_status_label": status["honest_status_label"],
            "prior_update_count": status["prior_update_count"],
            "shadow_routing_ref": status.get("shadow_routing_ref"),
            "active_route_mutated": False,
            "active_production_mutated": False,
            "raw_content_included": False,
        },
        "research_source_refs": _request_value(request, "source_refs", []),
        "memory_ref_count": len(_request_value(request, "memory_refs", [])),
        "failure_terms": sorted(failure_terms),
        "privacy_boundary": {
            "raw_problem_statement_exported": False,
            "raw_failed_outputs_exported": False,
            "local_paths_exported": False,
        },
    }


def federated_prior_feedback_status(
    *,
    prior_ledger: dict[str, Any],
    shadow_routing: dict[str, Any] | None = None,
    dream_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prior_count = int(prior_ledger.get("prior_update_count") or 0)
    has_dream_context = bool(dream_context)
    status = "live-bound" if prior_count else "degraded"
    return {
        "surface_id": FEDERATED_PRIOR_FEEDBACK_SURFACE_ID,
        "latest_ref": FEDERATED_PRIOR_FEEDBACK_REF,
        "status": status,
        "honest_status_label": (
            "prior-feedback-live-shadow-only" if prior_count else "prior-feedback-awaiting-sanitized-priors"
        ),
        "prior_ledger_ref": prior_ledger.get("ledger_id"),
        "prior_update_count": prior_count,
        "shadow_routing_ref": (shadow_routing or {}).get("shadow_routing_id"),
        "dream_context_bound": has_dream_context,
        "active_route_mutated": False,
        "active_production_mutated": False,
        "raw_content_included": False,
        "mutation_boundary": "sanitized-prior-feedback-shadow-only-no-active-route-or-production-mutation",
    }


def _sum_prior_deltas(prior_updates: list[dict[str, Any]], key: str) -> dict[str, float]:
    totals: dict[str, float] = {}
    for update in prior_updates:
        delta = (update.get("local_prior_delta") or {}).get(key) or {}
        if not isinstance(delta, dict):
            continue
        for item_key, value in delta.items():
            try:
                totals[str(item_key)] = round(totals.get(str(item_key), 0.0) + float(value), 6)
            except (TypeError, ValueError):
                continue
    return dict(sorted(totals.items(), key=lambda item: (-item[1], item[0])))


def _route_geometry_priors(prior_updates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    priors: dict[str, dict[str, Any]] = {}
    for update in prior_updates:
        signature = str(update.get("route_geometry_signature") or "unknown-route")
        packet_weight = float(update.get("packet_weight") or 0.0)
        prior = priors.setdefault(
            signature,
            {
                "packet_count": 0,
                "total_weight": 0.0,
                "mean_resonance_score": 0.0,
                "promotion_state": "sandbox_required_before_global_release",
            },
        )
        prior["packet_count"] += 1
        prior["total_weight"] = round(float(prior["total_weight"]) + packet_weight, 6)
        prior["mean_resonance_score"] = round(
            (
                float(prior["mean_resonance_score"]) * (prior["packet_count"] - 1)
                + float(update.get("mean_resonance_score") or 0.0)
            )
            / prior["packet_count"],
            6,
        )
    return dict(sorted(priors.items(), key=lambda item: (-item[1]["total_weight"], item[0])))


def _routing_prior_suggestions(route_geometry_priors: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    suggestions = []
    for signature, prior in route_geometry_priors.items():
        suggestions.append(
            {
                "route_geometry_signature": signature,
                "packet_count": prior["packet_count"],
                "total_weight": prior["total_weight"],
                "mean_resonance_score": prior["mean_resonance_score"],
                "suggestion": "increase_shadow_weight_for_repeated_successful_route",
                "promotion_state": prior["promotion_state"],
            }
        )
    return suggestions


def _node_id(node: Any) -> str:
    return str(_node_value(node, "node_id", "node:unknown"))


def _node_value(node: Any, key: str, default: Any) -> Any:
    if isinstance(node, dict):
        return node.get(key, default)
    return getattr(node, key, default)


def _request_value(request: Any | None, key: str, default: Any) -> Any:
    if request is None:
        return default
    if isinstance(request, dict):
        return request.get(key, default)
    return getattr(request, key, default)
