from __future__ import annotations

from typing import Any


PROVENANCE_FIELDS = (
    "compatibility_plan_id",
    "compatibility_status",
    "attachment_mode",
    "product_evidence",
)


def normalize_compatibility_provenance(*sources: Any) -> dict[str, Any]:
    """Extract canonical attach compatibility provenance from nested trace payloads."""

    provenance: dict[str, Any] = {}
    for source in sources:
        _merge_source(provenance, _as_dict(source))
    return provenance


def trace_is_non_product_evidence(trace: dict[str, Any], provenance: dict[str, Any] | None = None) -> bool:
    runtime_selection = _as_dict(trace.get("runtime_selection")) or _as_dict((trace.get("metrics") or {}).get("runtime_selection"))
    selected_provenance = provenance or normalize_compatibility_provenance(trace, runtime_selection)
    served_runtime = runtime_selection.get("served_runtime_name") or trace.get("runtime_name")
    attachment_mode = selected_provenance.get("attachment_mode")
    if served_runtime == "mock":
        return True
    if attachment_mode in {"mock", "dev"}:
        return True
    return selected_provenance.get("product_evidence") is not True


def _merge_source(provenance: dict[str, Any], source: dict[str, Any]) -> None:
    if not source:
        return
    for nested_key in (
        "compatibility_provenance",
        "runtime_selection",
        "core_attachment",
        "model_attachment",
    ):
        nested = _as_dict(source.get(nested_key))
        if nested:
            _merge_source(provenance, nested)

    plan = _as_dict(source.get("compatibility_plan"))
    if plan:
        provenance.setdefault("compatibility_plan", plan)
        if plan.get("compatibility_plan_id") is not None:
            provenance["compatibility_plan_id"] = plan.get("compatibility_plan_id")
        if plan.get("status") is not None:
            provenance["compatibility_status"] = str(plan.get("status"))

    for field in PROVENANCE_FIELDS:
        if field in source and source.get(field) is not None:
            provenance[field] = source.get(field)

    mode = source.get("mode")
    if "attachment_mode" not in provenance and mode in {"mock", "dev", "product"}:
        provenance["attachment_mode"] = mode

    if "product_evidence" not in provenance and provenance.get("attachment_mode") in {"mock", "dev"}:
        provenance["product_evidence"] = False


def _as_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "model_dump"):
        return dict(value.model_dump(mode="json"))
    return {}
