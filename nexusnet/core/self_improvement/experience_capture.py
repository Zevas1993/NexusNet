from __future__ import annotations

from typing import Any

from .event_schema import (
    ContextSource,
    ImprovementEvent,
    InputModality,
    LearningSignal,
    Outcome,
    PROJECT_NAME,
    SafetyClassification,
)


class ExperienceCapture:
    def __init__(self, *, project: str = PROJECT_NAME):
        self.project = project

    def capture(
        self,
        *,
        session_id: str,
        user_goal: str,
        input_modalities: list[InputModality],
        agent_task_type: str,
        context_sources: list[ContextSource | dict[str, Any]] | None = None,
        agent_plan: str = "",
        actions_taken: list[str] | None = None,
        final_output_summary: str = "",
        outcome: Outcome | dict[str, Any],
        learning_signal: LearningSignal | dict[str, Any] | None = None,
        safety: SafetyClassification | dict[str, Any] | None = None,
        metrics: dict[str, float | int | str | bool] | None = None,
        evidence_refs: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ImprovementEvent:
        normalized_sources = [
            source if isinstance(source, ContextSource) else ContextSource.model_validate(source)
            for source in (context_sources or [])
        ]
        resolved_metadata = {
            **(metadata or {}),
            "capture_method": "ExperienceCapture.capture",
            "captured_source_count": len(normalized_sources),
        }
        return ImprovementEvent(
            project=self.project,
            session_id=session_id,
            input_modalities=input_modalities,
            user_goal=user_goal,
            agent_task_type=agent_task_type,
            context_sources=normalized_sources,
            agent_plan=agent_plan,
            actions_taken=actions_taken or [],
            final_output_summary=final_output_summary,
            outcome=outcome if isinstance(outcome, Outcome) else Outcome.model_validate(outcome),
            learning_signal=(
                learning_signal
                if isinstance(learning_signal, LearningSignal)
                else LearningSignal.model_validate(learning_signal or {})
            ),
            safety=(
                safety
                if isinstance(safety, SafetyClassification)
                else SafetyClassification.model_validate(safety or {})
            ),
            metrics=metrics or {},
            evidence_refs=evidence_refs or [],
            metadata=resolved_metadata,
        )
