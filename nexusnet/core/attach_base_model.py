from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..adapters import BaseModelAdapter, make_registry_adapter


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_base_model(
    *,
    model_hint: str | None,
    role: str,
    runtime_name: str | None,
    model_registry: Any,
    runtime_registry: Any,
    adapter_cache: dict[str, BaseModelAdapter],
    attachment_cache: dict[str, dict[str, Any]],
    telemetry: Any | None = None,
    hardware_profile: dict[str, Any] | None = None,
    runtime_decision: dict[str, Any] | None = None,
    teacher_registry_layer: str | None = None,
    teacher_id: str | None = None,
    lineage_tags: list[str] | None = None,
    evidence_refs: dict[str, Any] | None = None,
    execution_mode: str | None = None,
    proposed_execution_mode: str | None = None,
    execution_policy_id: str | None = None,
    legacy_execution_mode: str | None = None,
    governed_action: str | None = None,
    native_execution_verdict: str | None = None,
    alignment_hold_required: bool | None = None,
    native_candidate_id: str | None = None,
    native_activation_mode: str | None = None,
    native_candidate_confidence: float | None = None,
    promotion_action: str | None = None,
    promotion_decision_id: str | None = None,
    startup_log_path: str | None = None,
) -> tuple[BaseModelAdapter, dict[str, Any]]:
    registration = model_registry.resolve_model(model_hint)
    selected_runtime_name = runtime_name or registration.runtime_name
    adapter_role = "specialist" if role == "specialist" else "teacher"
    adapter_key = f"{role}:{registration.model_id}@{selected_runtime_name}"
    cached_adapter = adapter_cache.get(adapter_key)
    if cached_adapter is not None:
        cached_record = attachment_cache.get(adapter_key)
        if cached_record is not None:
            merged_record = {
                **cached_record,
                "last_attached_at": _utcnow_iso(),
                "teacher_id": teacher_id or cached_record.get("teacher_id"),
                "teacher_registry_layer": teacher_registry_layer or cached_record.get("teacher_registry_layer"),
                "lineage_tags": sorted(set((cached_record.get("lineage_tags") or []) + list(lineage_tags or []))),
                "hardware_profile": hardware_profile or cached_record.get("hardware_profile", {}),
                "runtime_decision": runtime_decision or cached_record.get("runtime_decision", {}),
                "startup_log_path": startup_log_path or cached_record.get("startup_log_path"),
                "evidence_refs": {
                    **dict(cached_record.get("evidence_refs") or {}),
                    **dict(evidence_refs or {}),
                },
                "execution_mode": execution_mode or cached_record.get("execution_mode"),
                "proposed_execution_mode": proposed_execution_mode or cached_record.get("proposed_execution_mode"),
                "execution_policy_id": execution_policy_id or cached_record.get("execution_policy_id"),
                "legacy_execution_mode": legacy_execution_mode or cached_record.get("legacy_execution_mode"),
                "governed_action": governed_action or cached_record.get("governed_action"),
                "native_execution_verdict": native_execution_verdict or cached_record.get("native_execution_verdict"),
                "alignment_hold_required": (
                    alignment_hold_required
                    if alignment_hold_required is not None
                    else cached_record.get("alignment_hold_required")
                ),
                "native_candidate_id": native_candidate_id or cached_record.get("native_candidate_id"),
                "native_activation_mode": native_activation_mode or cached_record.get("native_activation_mode"),
                "native_candidate_confidence": (
                    native_candidate_confidence
                    if native_candidate_confidence is not None
                    else cached_record.get("native_candidate_confidence")
                ),
                "promotion_action": promotion_action or cached_record.get("promotion_action"),
                "promotion_decision_id": promotion_decision_id or cached_record.get("promotion_decision_id"),
            }
            attachment_cache[adapter_key] = merged_record
            return cached_adapter, dict(merged_record)
    runtime_backend = runtime_registry.get_adapter(selected_runtime_name)
    adapter = make_registry_adapter(registration, runtime_backend, adapter_role=adapter_role)
    adapter_cache[adapter_key] = adapter
    capability_profile = adapter.capability_profile().model_dump(mode="json")
    record = {
        "attachment_id": f"attach::{adapter_key}",
        "adapter_key": adapter_key,
        "adapter_id": adapter.adapter_id,
        "attached_at": _utcnow_iso(),
        "model_id": registration.model_id,
        "display_name": registration.display_name,
        "model_family": registration.capability_card.model_family,
        "runtime_name": selected_runtime_name,
        "requested_role": role,
        "adapter_role": adapter.adapter_role,
        "teacher_id": teacher_id,
        "teacher_registry_layer": teacher_registry_layer,
        "lineage_tags": list(lineage_tags or []),
        "evidence_refs": dict(evidence_refs or {}),
        "execution_mode": execution_mode,
        "proposed_execution_mode": proposed_execution_mode,
        "execution_policy_id": execution_policy_id,
        "legacy_execution_mode": legacy_execution_mode,
        "governed_action": governed_action,
        "native_execution_verdict": native_execution_verdict,
        "alignment_hold_required": alignment_hold_required,
        "native_candidate_id": native_candidate_id,
        "native_activation_mode": native_activation_mode,
        "native_candidate_confidence": native_candidate_confidence,
        "promotion_action": promotion_action,
        "promotion_decision_id": promotion_decision_id,
        "startup_log_path": startup_log_path,
        "hardware_profile": hardware_profile or {},
        "runtime_decision": runtime_decision or {},
        "attached_model_identity": {
            "model_id": registration.model_id,
            "display_name": registration.display_name,
            "runtime_name": selected_runtime_name,
            "model_family": registration.capability_card.model_family,
            "available": registration.available,
        },
        "capability_profile": capability_profile,
    }
    attachment_cache[adapter_key] = record
    if telemetry is not None:
        telemetry.log_model_attach(
            {
                "event": "nexusnet.attach_model",
                "model_id": registration.model_id,
                "runtime_name": selected_runtime_name,
                "adapter_role": role,
                "teacher_registry_layer": teacher_registry_layer,
                "teacher_id": teacher_id,
                "lineage_tags": list(lineage_tags or []),
                "evidence_refs": dict(evidence_refs or {}),
                "execution_mode": execution_mode,
                "proposed_execution_mode": proposed_execution_mode,
                "execution_policy_id": execution_policy_id,
                "legacy_execution_mode": legacy_execution_mode,
                "governed_action": governed_action,
                "native_execution_verdict": native_execution_verdict,
                "alignment_hold_required": alignment_hold_required,
                "native_candidate_id": native_candidate_id,
                "native_activation_mode": native_activation_mode,
                "native_candidate_confidence": native_candidate_confidence,
                "promotion_action": promotion_action,
                "promotion_decision_id": promotion_decision_id,
                "startup_log_path": startup_log_path,
                "capability_profile": capability_profile,
            }
        )
    return adapter, dict(record)
