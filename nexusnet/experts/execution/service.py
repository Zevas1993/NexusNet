from __future__ import annotations

from typing import Any

from ..runtime import InternalExpertRuntimeService


class InternalExpertExecutionService:
    def __init__(self, *, runtime: InternalExpertRuntimeService | None = None):
        self.runtime = runtime or InternalExpertRuntimeService()

    def preview(
        self,
        *,
        native_execution_plan: dict[str, Any],
        selected_expert: str | None,
    ) -> dict[str, Any]:
        return self.runtime.preview(
            native_execution_plan=native_execution_plan,
            selected_expert=selected_expert,
        )

    def execute(
        self,
        *,
        prompt: str,
        selected_expert: str | None,
        native_execution_plan: dict[str, Any],
        execution_policy: dict[str, Any],
        evidence_feeds: dict[str, Any],
    ) -> dict[str, Any]:
        return self.runtime.execute(
            prompt=prompt,
            selected_expert=selected_expert,
            native_execution_plan=native_execution_plan,
            execution_policy=execution_policy,
            evidence_feeds=evidence_feeds,
        )
