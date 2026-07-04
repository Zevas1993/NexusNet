from __future__ import annotations

from typing import Any

from ..core.compatibility_provenance import normalize_compatibility_provenance

ELIGIBLE_COMPATIBILITY_STATUSES = {"COMPATIBLE", "ADAPTER_REQUIRED"}


def evaluate_native_takeover_provenance_gate(
    *,
    traceability: dict[str, Any] | None = None,
    compatibility_provenance: dict[str, Any] | None = None,
    candidate_kind: str | None = None,
) -> dict[str, Any]:
    if candidate_kind not in {None, "native-takeover"}:
        return {
            "eligible": True,
            "status": "not-applicable",
            "reason_codes": [],
            "summary": "Native takeover provenance gate does not apply to this candidate kind.",
            "recommended_governed_action": None,
            "compatibility_provenance": normalize_compatibility_provenance(
                compatibility_provenance or {},
                traceability or {},
            ),
        }

    traceability = dict(traceability or {})
    explicit_provenance = dict(compatibility_provenance or {})
    distillation_artifact = dict(traceability.get("distillation_artifact") or {})
    artifact_metadata = dict(distillation_artifact.get("metadata") or {})
    takeover = dict(traceability.get("takeover") or {})
    takeover_evidence = dict(takeover.get("evidence") or {})

    normalized = normalize_compatibility_provenance(
        explicit_provenance,
        traceability,
        artifact_metadata,
        takeover_evidence,
    )
    plan_ids = _collect_list(
        traceability,
        artifact_metadata,
        explicit_provenance,
        key="compatibility_plan_ids",
    )
    status_counts = _collect_counts(
        traceability,
        artifact_metadata,
        explicit_provenance,
        key="compatibility_status_counts",
    )
    attachment_mode_counts = _collect_counts(
        traceability,
        artifact_metadata,
        explicit_provenance,
        key="attachment_mode_counts",
    )
    product_evidence_counts = _collect_counts(
        traceability,
        artifact_metadata,
        explicit_provenance,
        key="product_evidence_counts",
    )
    included_non_product_trace_count = _first_int(
        traceability,
        artifact_metadata,
        explicit_provenance,
        key="included_non_product_trace_count",
    )

    if plan_ids and not normalized.get("compatibility_plan_id") and len(set(plan_ids)) == 1:
        normalized["compatibility_plan_id"] = plan_ids[0]
    if status_counts and not normalized.get("compatibility_status") and len(status_counts) == 1:
        normalized["compatibility_status"] = next(iter(status_counts))
    if attachment_mode_counts and not normalized.get("attachment_mode") and len(attachment_mode_counts) == 1:
        normalized["attachment_mode"] = next(iter(attachment_mode_counts))
    if product_evidence_counts and "product_evidence" not in normalized and len(product_evidence_counts) == 1:
        normalized["product_evidence"] = next(iter(product_evidence_counts))
    if included_non_product_trace_count and "product_evidence" not in normalized:
        normalized["product_evidence"] = False

    normalized["compatibility_plan_ids"] = plan_ids
    normalized["compatibility_status_counts"] = status_counts
    normalized["attachment_mode_counts"] = attachment_mode_counts
    normalized["product_evidence_counts"] = product_evidence_counts
    if included_non_product_trace_count:
        normalized["included_non_product_trace_count"] = included_non_product_trace_count

    reason_codes: list[str] = []
    if not _has_any_provenance(normalized, plan_ids, status_counts, attachment_mode_counts, product_evidence_counts):
        reason_codes.append("MISSING_PROVENANCE")
    if len(set(plan_ids)) > 1:
        reason_codes.append("INCOMPLETE_LINEAGE")
    if len(status_counts) > 1:
        reason_codes.append("INCOMPLETE_LINEAGE")
    if len(attachment_mode_counts) > 1:
        reason_codes.append("INCOMPLETE_LINEAGE")
    if len(product_evidence_counts) > 1:
        reason_codes.append("INCOMPLETE_LINEAGE")
    if included_non_product_trace_count:
        reason_codes.append("INCOMPLETE_LINEAGE")
        reason_codes.append("NON_PRODUCT_EVIDENCE")

    compatibility_plan_id = normalized.get("compatibility_plan_id")
    compatibility_status = normalized.get("compatibility_status")
    attachment_mode = normalized.get("attachment_mode")
    product_evidence = normalized.get("product_evidence")

    if not compatibility_plan_id:
        reason_codes.append("MISSING_COMPATIBILITY_PLAN")
    if attachment_mode in {"mock", "dev"}:
        reason_codes.append("MOCK_OR_DEV_ATTACHMENT")
    elif attachment_mode != "product":
        reason_codes.append("MISSING_PROVENANCE")

    if product_evidence is False:
        reason_codes.append("NON_PRODUCT_EVIDENCE")
    elif product_evidence is not True:
        reason_codes.append("MISSING_PROVENANCE")

    if compatibility_status == "UNVERIFIED":
        reason_codes.append("COMPATIBILITY_UNVERIFIED")
    elif compatibility_status == "UNSUPPORTED":
        reason_codes.append("COMPATIBILITY_UNSUPPORTED")
    elif compatibility_status not in ELIGIBLE_COMPATIBILITY_STATUSES:
        reason_codes.append("MISSING_PROVENANCE")

    reason_codes = list(dict.fromkeys(reason_codes))
    eligible = len(reason_codes) == 0
    status = "eligible" if eligible else "blocked"
    recommended_governed_action = _recommended_governed_action(reason_codes)

    return {
        "eligible": eligible,
        "status": status,
        "reason_codes": reason_codes,
        "summary": _summary(reason_codes),
        "recommended_governed_action": recommended_governed_action,
        "compatibility_provenance": normalized,
        "compatibility_plan_id": normalized.get("compatibility_plan_id"),
        "compatibility_status": normalized.get("compatibility_status"),
        "attachment_mode": normalized.get("attachment_mode"),
        "product_evidence": normalized.get("product_evidence"),
    }


def _summary(reason_codes: list[str]) -> str:
    if not reason_codes:
        return "Product-grade compatibility-backed provenance is present for native takeover gating."
    labels = {
        "MISSING_PROVENANCE": "required provenance is missing",
        "MISSING_COMPATIBILITY_PLAN": "the compatibility plan is missing",
        "NON_PRODUCT_EVIDENCE": "the evidence is not product-grade",
        "MOCK_OR_DEV_ATTACHMENT": "the attachment came from mock or dev mode",
        "COMPATIBILITY_UNVERIFIED": "compatibility is still unverified",
        "COMPATIBILITY_UNSUPPORTED": "compatibility is unsupported",
        "INCOMPLETE_LINEAGE": "lineage is mixed or incomplete",
    }
    joined = ", ".join(labels.get(code, code.lower()) for code in reason_codes)
    return f"Native takeover remains blocked because {joined}."


def _recommended_governed_action(reason_codes: list[str]) -> str | None:
    if not reason_codes:
        return None
    if any(
        code in {"NON_PRODUCT_EVIDENCE", "MOCK_OR_DEV_ATTACHMENT", "COMPATIBILITY_UNSUPPORTED"}
        for code in reason_codes
    ):
        return "keep_teacher_fallback"
    return "require_more_evidence"


def _has_any_provenance(
    normalized: dict[str, Any],
    plan_ids: list[str],
    status_counts: dict[str, int],
    attachment_mode_counts: dict[str, int],
    product_evidence_counts: dict[bool, int],
) -> bool:
    return bool(
        normalized.get("compatibility_plan_id")
        or normalized.get("compatibility_status")
        or normalized.get("attachment_mode")
        or normalized.get("product_evidence") is not None
        or plan_ids
        or status_counts
        or attachment_mode_counts
        or product_evidence_counts
    )


def _collect_list(*sources: dict[str, Any], key: str) -> list[str]:
    values: list[str] = []
    for source in sources:
        raw = source.get(key)
        if isinstance(raw, list):
            values.extend(str(item) for item in raw if item not in {None, ""})
    return list(dict.fromkeys(values))


def _collect_counts(*sources: dict[str, Any], key: str) -> dict[Any, int]:
    for source in sources:
        raw = source.get(key)
        if not isinstance(raw, dict) or not raw:
            continue
        normalized: dict[Any, int] = {}
        for count_key, count_value in raw.items():
            try:
                count_int = int(count_value)
            except Exception:
                continue
            if count_int <= 0:
                continue
            normalized_key = _normalize_count_key(count_key)
            normalized[normalized_key] = normalized.get(normalized_key, 0) + count_int
        if normalized:
            return normalized
    return {}


def _normalize_count_key(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        return value
    return value


def _first_int(*sources: dict[str, Any], key: str) -> int:
    for source in sources:
        raw = source.get(key)
        if raw in {None, ""}:
            continue
        try:
            return int(raw)
        except Exception:
            continue
    return 0
