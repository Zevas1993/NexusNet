from __future__ import annotations

from typing import Any


AUTHORITY = "promotion-provenance-gate"


def resolve_readiness_authority(evidence_refs: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize the fail-closed authority contract for replacement readiness."""

    evidence_refs = evidence_refs or {}
    raw_authority = evidence_refs.get("readiness_authority")
    explicit_authority = raw_authority.get("readiness_authority") if isinstance(raw_authority, dict) else raw_authority
    takeover_eligible = bool(evidence_refs.get("takeover_eligible"))
    readiness_status = str(evidence_refs.get("readiness_status") or "")
    authoritative_readiness = bool(evidence_refs.get("authoritative_readiness"))
    missing: list[str] = []
    if not takeover_eligible:
        missing.append("takeover_eligible")
    if readiness_status != "eligible":
        missing.append("readiness_status")
    if explicit_authority != AUTHORITY:
        missing.append("readiness_authority")
    if not authoritative_readiness:
        missing.append("authoritative_readiness")

    return {
        "readiness_authority": AUTHORITY,
        "source_readiness_authority": explicit_authority,
        "takeover_eligible": takeover_eligible,
        "readiness_status": readiness_status or "not_eligible",
        "authoritative_readiness": not missing,
        "diagnostic_only": bool(missing),
        "missing_authority": missing,
    }


def annotate_evidence_refs(evidence_refs: dict[str, Any] | None) -> dict[str, Any]:
    annotated = dict(evidence_refs or {})
    annotated["readiness_authority"] = resolve_readiness_authority(annotated)
    return annotated


def authority_allows_replacement(evidence_refs: dict[str, Any] | None) -> bool:
    return bool(resolve_readiness_authority(evidence_refs).get("authoritative_readiness"))
