from __future__ import annotations

from typing import Any

from ..core.compatibility_provenance import normalize_compatibility_provenance
from .provenance_gate import evaluate_native_takeover_provenance_gate

HARD_BLOCK_REASONS = {
    "NON_PRODUCT_EVIDENCE",
    "MOCK_OR_DEV_ATTACHMENT",
    "COMPATIBILITY_UNSUPPORTED",
}
UNVERIFIED_REASONS = {
    "MISSING_PROVENANCE",
    "MISSING_COMPATIBILITY_PLAN",
    "COMPATIBILITY_UNVERIFIED",
    "INCOMPLETE_LINEAGE",
}
BLOCKING_DECISIONS = {"rejected"}
PENDING_DECISIONS = {"shadow", "review"}
BLOCKING_GOVERNED_ACTIONS = {"rollback_to_teacher", "keep_teacher_fallback"}
PENDING_GOVERNED_ACTIONS = {
    "require_more_evidence",
    "hold_for_alignment",
    "allow_native_shadow",
    "allow_native_challenger_shadow",
}


def readiness_summary(*sources: Any, candidate_kind: str | None = None) -> dict[str, Any]:
    merged = _merge_sources(*sources)
    normalized_candidate_kind = candidate_kind or merged.get("candidate_kind") or "native-takeover"
    compatibility_provenance = normalize_compatibility_provenance(
        merged,
        merged.get("compatibility_provenance"),
        merged.get("benchmark"),
        merged.get("benchmark_summary"),
    )

    gate = dict(merged.get("promotion_provenance_gate") or {})
    if normalized_candidate_kind == "native-takeover":
        gate = gate or evaluate_native_takeover_provenance_gate(
            traceability=merged,
            compatibility_provenance=compatibility_provenance,
            candidate_kind="native-takeover",
        )
    else:
        gate = gate or {
            "eligible": bool(merged.get("takeover_eligible")),
            "status": "not-applicable",
            "reason_codes": [],
            "summary": "Takeover readiness is not applicable to this candidate kind.",
            "compatibility_provenance": compatibility_provenance,
        }

    compatibility_provenance = dict(gate.get("compatibility_provenance") or compatibility_provenance)
    compatibility_plan_id = (
        merged.get("compatibility_plan_id")
        or compatibility_provenance.get("compatibility_plan_id")
        or gate.get("compatibility_plan_id")
    )
    compatibility_status = (
        merged.get("compatibility_status")
        or compatibility_provenance.get("compatibility_status")
        or gate.get("compatibility_status")
    )
    attachment_mode = (
        merged.get("attachment_mode")
        or compatibility_provenance.get("attachment_mode")
        or gate.get("attachment_mode")
    )
    product_evidence = _resolve_product_evidence(
        merged.get("product_evidence"),
        compatibility_provenance.get("product_evidence"),
        gate.get("product_evidence"),
    )

    gate_reasons = list(
        dict.fromkeys(
            list(merged.get("takeover_gate_reasons") or [])
            + list(gate.get("reason_codes") or [])
        )
    )
    takeover_eligible = bool(merged.get("takeover_eligible", gate.get("eligible", False)))
    review_status = merged.get("review_status") or merged.get("candidate_review_status")
    decision = merged.get("decision")
    governance_decision = merged.get("governance_decision")
    evaluator_decision = merged.get("evaluator_decision") or merged.get("evaluation_decision")
    governed_action = merged.get("governed_action")

    readiness_reasons: list[str] = list(gate_reasons)
    if decision in BLOCKING_DECISIONS:
        readiness_reasons.append("DECISION_REJECTED")
    if governance_decision in BLOCKING_DECISIONS:
        readiness_reasons.append("GOVERNANCE_REJECTED")
    if evaluator_decision in BLOCKING_DECISIONS:
        readiness_reasons.append("EVALUATION_REJECTED")
    if review_status in BLOCKING_DECISIONS:
        readiness_reasons.append("REVIEW_REJECTED")
    if governed_action in BLOCKING_GOVERNED_ACTIONS:
        readiness_reasons.append("GOVERNED_FALLBACK")
    if review_status in PENDING_DECISIONS:
        readiness_reasons.append("REVIEW_PENDING")
    if decision in PENDING_DECISIONS:
        readiness_reasons.append("DECISION_PENDING")
    if governance_decision in PENDING_DECISIONS:
        readiness_reasons.append("GOVERNANCE_PENDING")
    if evaluator_decision in PENDING_DECISIONS:
        readiness_reasons.append("EVALUATION_PENDING")
    if governed_action in PENDING_GOVERNED_ACTIONS:
        readiness_reasons.append("GOVERNED_MORE_EVIDENCE")
    readiness_reasons = list(dict.fromkeys(readiness_reasons))

    hard_blocked = any(reason in HARD_BLOCK_REASONS for reason in readiness_reasons)
    unverified = any(reason in UNVERIFIED_REASONS for reason in readiness_reasons)
    governance_blocked = any(
        reason in {"DECISION_REJECTED", "GOVERNANCE_REJECTED", "EVALUATION_REJECTED", "REVIEW_REJECTED", "GOVERNED_FALLBACK"}
        for reason in readiness_reasons
    )
    pending_review = any(
        reason in {"REVIEW_PENDING", "DECISION_PENDING", "GOVERNANCE_PENDING", "EVALUATION_PENDING", "GOVERNED_MORE_EVIDENCE"}
        for reason in readiness_reasons
    )

    if hard_blocked or governance_blocked:
        readiness_status = "blocked"
    elif not takeover_eligible:
        if unverified:
            readiness_status = "unverified"
        elif pending_review:
            readiness_status = "shadow"
        else:
            readiness_status = "needs_more_evidence"
    elif pending_review:
        readiness_status = "shadow"
    else:
        readiness_status = "eligible"

    return {
        "candidate_kind": normalized_candidate_kind,
        "takeover_eligible": takeover_eligible,
        "takeover_ready": readiness_status == "eligible",
        "readiness_status": readiness_status,
        "readiness_reasons": readiness_reasons,
        "summary": _summary(readiness_status=readiness_status, gate=gate, readiness_reasons=readiness_reasons),
        "compatibility_provenance": compatibility_provenance,
        "compatibility_plan_id": compatibility_plan_id,
        "compatibility_status": compatibility_status,
        "attachment_mode": attachment_mode,
        "product_evidence": product_evidence,
        "promotion_provenance_gate": gate,
        "takeover_gate_reasons": gate_reasons,
    }


def annotate_takeover_readiness(payload: dict[str, Any] | None, *sources: Any, candidate_kind: str | None = None) -> dict[str, Any]:
    annotated = dict(payload or {})
    readiness = readiness_summary(annotated, *sources, candidate_kind=candidate_kind)
    annotated.update(
        {
            "compatibility_provenance": readiness["compatibility_provenance"],
            "compatibility_plan_id": readiness["compatibility_plan_id"],
            "compatibility_status": readiness["compatibility_status"],
            "attachment_mode": readiness["attachment_mode"],
            "product_evidence": readiness["product_evidence"],
            "promotion_provenance_gate": readiness["promotion_provenance_gate"],
            "takeover_eligible": readiness["takeover_eligible"],
            "takeover_gate_reasons": readiness["takeover_gate_reasons"],
            "takeover_ready": readiness["takeover_ready"],
            "readiness_status": readiness["readiness_status"],
            "readiness_reasons": readiness["readiness_reasons"],
            "readiness_summary": readiness["summary"],
        }
    )
    return annotated


def annotate_diagnostic_readiness(
    payload: dict[str, Any] | None,
    *sources: Any,
    candidate_kind: str | None = None,
    readiness_context: str = "diagnostic-artifact",
) -> dict[str, Any]:
    annotated = annotate_takeover_readiness(payload, *sources, candidate_kind=candidate_kind)
    annotated.update(
        {
            "diagnostic_only": True,
            "authoritative_readiness": False,
            "readiness_authority": "promotion-provenance-gate",
            "readiness_context": readiness_context,
        }
    )
    return annotated


def _merge_sources(*sources: Any) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for source in sources:
        payload = _as_dict(source)
        for key, value in payload.items():
            if value is None:
                continue
            merged[key] = value
    return merged


def _as_dict(source: Any) -> dict[str, Any]:
    if source is None:
        return {}
    if isinstance(source, dict):
        return dict(source)
    if hasattr(source, "model_dump"):
        return dict(source.model_dump(mode="json"))
    return {}


def _resolve_product_evidence(*values: Any) -> bool | None:
    for value in values:
        if value is None:
            continue
        return bool(value)
    return None


def _summary(*, readiness_status: str, gate: dict[str, Any], readiness_reasons: list[str]) -> str:
    if readiness_status == "eligible":
        return "Explicit gate truth is present and no downstream governance state contradicts takeover readiness."
    if gate.get("summary"):
        return str(gate["summary"])
    if not readiness_reasons:
        return "Takeover readiness remains unavailable because explicit gate truth is missing."
    return f"Takeover readiness remains {readiness_status} because {', '.join(reason.lower() for reason in readiness_reasons)}."
