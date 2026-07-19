from __future__ import annotations

import hashlib
from typing import Any

from ..runtime import InternalExpertRuntimeService


class InternalExpertExecutionService:
    def __init__(
        self,
        *,
        runtime: InternalExpertRuntimeService | None = None,
        node_contract_registry: Any | None = None,
    ):
        self.runtime = runtime or InternalExpertRuntimeService()
        self.node_contract_registry = node_contract_registry

    def preview(
        self,
        *,
        native_execution_plan: dict[str, Any],
        selected_expert: str | None,
    ) -> dict[str, Any]:
        route_receipt = self._authorize_route(
            native_execution_plan=native_execution_plan,
            selected_expert=selected_expert,
        )
        if route_receipt is not None and route_receipt.get("route_allowed") is not True:
            return self._blocked_result(
                native_execution_plan=native_execution_plan,
                route_receipt=route_receipt,
                preview_only=True,
            )
        preview = self.runtime.preview(
            native_execution_plan=native_execution_plan,
            selected_expert=selected_expert,
        )
        return self._with_contract_enforcement(preview, route_receipt)

    def execute(
        self,
        *,
        prompt: str,
        selected_expert: str | None,
        native_execution_plan: dict[str, Any],
        execution_policy: dict[str, Any],
        evidence_feeds: dict[str, Any],
    ) -> dict[str, Any]:
        route_receipt = self._authorize_route(
            native_execution_plan=native_execution_plan,
            selected_expert=selected_expert,
            execution_policy=execution_policy,
        )
        if route_receipt is not None and route_receipt.get("route_allowed") is not True:
            return self._blocked_result(
                native_execution_plan=native_execution_plan,
                route_receipt=route_receipt,
                execution_policy=execution_policy,
                preview_only=False,
            )
        executed = self.runtime.execute(
            prompt=prompt,
            selected_expert=selected_expert,
            native_execution_plan=native_execution_plan,
            execution_policy=execution_policy,
            evidence_feeds=evidence_feeds,
        )
        return self._with_contract_enforcement(executed, route_receipt)

    def _authorize_route(
        self,
        *,
        native_execution_plan: dict[str, Any],
        selected_expert: str | None,
        execution_policy: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        registry = self.node_contract_registry
        authorize = getattr(registry, "authorize_route", None)
        if not callable(authorize):
            return None
        execution_policy = dict(execution_policy or {})
        execution_id = str(native_execution_plan.get("execution_id") or execution_policy.get("trace_id") or "native-expert")
        trace_id = str(execution_policy.get("trace_id") or "")
        if not trace_id:
            trace_id = "native-preview::" + hashlib.sha256(execution_id.encode("utf-8")).hexdigest()[:16]
        session_id = str(execution_policy.get("session_id") or execution_id)
        session_ref_digest = "sha256:" + hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:16]
        return authorize(
            selected_ao="RouterAO",
            selected_expert=str(selected_expert or "general"),
            trace_ref=f"trace::{trace_id}",
            session_ref_digest=session_ref_digest,
        )

    def _with_contract_enforcement(
        self,
        payload: dict[str, Any],
        route_receipt: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if route_receipt is None:
            return payload
        return {
            **payload,
            "node_contract_route_receipt": route_receipt,
            "node_contract_enforcement": {
                "status": "enforced",
                "registry_surface_id": route_receipt.get("surface_id"),
                "selected_ao": route_receipt.get("selected_ao"),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            },
        }

    def _blocked_result(
        self,
        *,
        native_execution_plan: dict[str, Any],
        route_receipt: dict[str, Any],
        preview_only: bool,
        execution_policy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        fallback_triggers = list(
            dict.fromkeys([*(native_execution_plan.get("fallback_triggers") or []), "node_contract_route_blocked"])
        )
        blocked = {
            "status_label": "BLOCKED NODE CONTRACT",
            "execution_id": native_execution_plan.get("execution_id"),
            "enabled": False,
            "execution_mode": "teacher_fallback",
            "legacy_execution_mode": "teacher-primary",
            "selected_internal_experts": [],
            "primary_expert_id": None,
            "teacher_fallback_path": native_execution_plan.get("teacher_fallback_path"),
            "contracts": [],
            "enabled_contract_count": 0,
            "preview_only": preview_only,
            "node_contract_route_receipt": route_receipt,
            "node_contract_enforcement": {
                "status": "blocked",
                "registry_surface_id": route_receipt.get("surface_id"),
                "selected_ao": route_receipt.get("selected_ao"),
                "blockers": list(route_receipt.get("blockers") or []),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            },
            "fallback_triggered": True,
            "policy_fallback_triggers": list(native_execution_plan.get("fallback_triggers") or []),
            "runtime_fallback_triggers": ["node_contract_route_blocked"],
            "fallback_triggers": fallback_triggers,
            "guarded_live_allowed": False,
            "alignment_hold_required": bool(native_execution_plan.get("alignment_hold_required")),
            "alignment_blockers": list(native_execution_plan.get("alignment_blockers") or []),
            "recommended_execution_mode": "teacher_fallback",
            "fallback_recommendation": native_execution_plan.get("teacher_fallback_path"),
            "runtime_contract": {
                "bounded_host_execution": True,
                "teacher_fallback_path": native_execution_plan.get("teacher_fallback_path"),
                "execution_mode": "teacher_fallback",
                "fallback_triggers": fallback_triggers,
                "guarded_live_allowed": False,
            },
        }
        if preview_only:
            return blocked
        execution_policy = dict(execution_policy or {})
        return {
            **blocked,
            "outputs": [],
            "output_count": 0,
            "disagreements": [],
            "disagreement_count": 0,
            "prompt_guidance": ["Teacher fallback required because the selected expert route lacks an active node contract."],
            "execution_policy_ref": execution_policy.get("policy_id"),
            "evidence_refs": execution_policy.get("evidence_refs", {}),
            "challenger_vs_teacher": {
                "required": False,
                "teacher_fallback_path": native_execution_plan.get("teacher_fallback_path"),
                "teacher_anchor_present": False,
                "challenger_output_count": 0,
                "disagreement_count": 0,
                "fallback_triggered": True,
            },
            "teacher_comparison": {
                "verdict": "node-contract-route-blocked",
                "summary": "The selected expert route is blocked; the teacher-attached path remains authoritative.",
                "recommended_execution_mode": "teacher_fallback",
            },
            "native_candidate": {
                "candidate_id": None,
                "activation_allowed": False,
                "activation_mode": "teacher-fallback-only",
                "confidence": 0.0,
                "blocked_reason": "node-contract-route-blocked",
            },
            "native_response_outline": [],
        }
