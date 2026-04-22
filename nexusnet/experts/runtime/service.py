from __future__ import annotations

from typing import Any

from ..harness import InternalExpertHarnessService


class InternalExpertRuntimeService:
    def __init__(self, *, harness: InternalExpertHarnessService | None = None):
        self.harness = harness or InternalExpertHarnessService()

    def preview(
        self,
        *,
        native_execution_plan: dict[str, Any],
        selected_expert: str | None,
    ) -> dict[str, Any]:
        preview = self.harness.preview(
            native_execution_plan=native_execution_plan,
            selected_expert=selected_expert,
        )
        return {
            **preview,
            "runtime_contract": {
                "bounded_host_execution": True,
                "teacher_fallback_path": native_execution_plan.get("teacher_fallback_path"),
                "prompt_guidance_mode": native_execution_plan.get("prompt_guidance_mode"),
                "fallback_triggers": native_execution_plan.get("fallback_triggers", []),
                "challenger_compare_required": native_execution_plan.get("challenger_compare_required", False),
            },
        }

    def execute(
        self,
        *,
        prompt: str,
        selected_expert: str | None,
        native_execution_plan: dict[str, Any],
        execution_policy: dict[str, Any],
        evidence_feeds: dict[str, Any],
    ) -> dict[str, Any]:
        executed = self.harness.execute(
            prompt=prompt,
            selected_expert=selected_expert,
            native_execution_plan=native_execution_plan,
            execution_policy=execution_policy,
            evidence_feeds=evidence_feeds,
        )
        return {
            **executed,
            "runtime_contract": {
                "bounded_host_execution": True,
                "teacher_fallback_path": native_execution_plan.get("teacher_fallback_path"),
                "prompt_guidance_mode": native_execution_plan.get("prompt_guidance_mode"),
                "execution_mode": native_execution_plan.get("execution_mode"),
                "fallback_triggers": executed.get("fallback_triggers", []),
                "guarded_live_allowed": executed.get("guarded_live_allowed", False),
            },
        }
