from __future__ import annotations

from typing import Any

from ..adapters import BaseModelAdapter
from .attach_base_model import attach_base_model


class ModelIngestionService:
    def __init__(
        self,
        *,
        model_registry: Any,
        runtime_registry: Any,
        telemetry: Any | None = None,
        adapter_cache: dict[str, BaseModelAdapter] | None = None,
        attachment_cache: dict[str, dict[str, Any]] | None = None,
    ):
        self.model_registry = model_registry
        self.runtime_registry = runtime_registry
        self.telemetry = telemetry
        self.adapter_cache = adapter_cache if adapter_cache is not None else {}
        self.attachment_cache = attachment_cache if attachment_cache is not None else {}

    def attach(
        self,
        *,
        model_hint: str | None,
        role: str = "teacher",
        runtime_name: str | None = None,
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
        return attach_base_model(
            model_hint=model_hint,
            role=role,
            runtime_name=runtime_name,
            model_registry=self.model_registry,
            runtime_registry=self.runtime_registry,
            adapter_cache=self.adapter_cache,
            attachment_cache=self.attachment_cache,
            telemetry=self.telemetry,
            hardware_profile=hardware_profile,
            runtime_decision=runtime_decision,
            teacher_registry_layer=teacher_registry_layer,
            teacher_id=teacher_id,
            lineage_tags=lineage_tags,
            evidence_refs=evidence_refs,
            execution_mode=execution_mode,
            proposed_execution_mode=proposed_execution_mode,
            execution_policy_id=execution_policy_id,
            legacy_execution_mode=legacy_execution_mode,
            governed_action=governed_action,
            native_execution_verdict=native_execution_verdict,
            alignment_hold_required=alignment_hold_required,
            native_candidate_id=native_candidate_id,
            native_activation_mode=native_activation_mode,
            native_candidate_confidence=native_candidate_confidence,
            promotion_action=promotion_action,
            promotion_decision_id=promotion_decision_id,
            startup_log_path=startup_log_path,
        )

    def attachments(self) -> list[dict[str, Any]]:
        return sorted(self.attachment_cache.values(), key=lambda item: (item.get("attached_at") or "", item.get("adapter_key") or ""))
