from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .event_schema import FailureMode, ImprovementEvent


TriageLabel = Literal[
    "store_as_project_memory",
    "create_eval_case",
    "create_preference_pair",
    "create_training_candidate",
    "discard",
    "human_review_required",
]

SafeOptimizationMode = Literal[
    "memory_rag_update",
    "prompt_policy_candidate",
    "routing_policy_candidate",
    "eval_case_expansion",
    "human_reviewed_training_candidate",
]

RISKY_FAILURE_MODES: set[FailureMode] = {
    "hallucination",
    "missing_context",
    "tool_error",
    "stale_info",
    "bad_reasoning",
    "policy_blocked",
    "privacy_risk",
}


class TriageDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    labels: list[TriageLabel] = Field(default_factory=list)
    queue_required: bool
    review_required: bool
    reasons: list[str] = Field(default_factory=list)
    blocked_reason: str | None = None
    safe_optimization_modes: list[SafeOptimizationMode] = Field(default_factory=list)
    model_update_boundary: str = "no-weight-update-without-human-review-external-verification-and-regression-gates"


def triage_improvement_event(event: ImprovementEvent) -> TriageDecision:
    labels: list[TriageLabel] = []
    reasons: list[str] = []
    modes: list[SafeOptimizationMode] = []
    review_required = bool(event.learning_signal.review_required)

    if event.safety.contains_secrets:
        return TriageDecision(
            event_id=event.event_id,
            labels=["discard", "human_review_required"],
            queue_required=False,
            review_required=True,
            reasons=["Secrets are never converted into memory, eval, preference, or training material."],
            blocked_reason="contains-secrets",
            safe_optimization_modes=[],
        )

    if event.safety.contains_private_data:
        review_required = True
        reasons.append("Private data requires human review and redaction before any durable improvement.")
        if event.safety.retention_policy == "long_term":
            reasons.append("Long-term private retention is blocked until explicitly approved.")

    if event.learning_signal.should_store_memory and not event.safety.contains_private_data:
        labels.append("store_as_project_memory")
        modes.append("memory_rag_update")
        reasons.append("Learning signal allows project memory because no private or secret data is marked.")

    if event.learning_signal.should_create_eval or event.outcome.status in {"partial", "failed", "blocked", "needs_review"}:
        labels.append("create_eval_case")
        modes.append("eval_case_expansion")
        reasons.append("Outcome or learning signal supports a regression/eval case.")

    if event.outcome.failure_modes and set(event.outcome.failure_modes).intersection(RISKY_FAILURE_MODES):
        if "create_eval_case" not in labels:
            labels.append("create_eval_case")
            modes.append("eval_case_expansion")
        review_required = True
        reasons.append("Failure modes require external verification before behavior changes.")

    if event.learning_signal.should_create_training_example:
        labels.append("create_training_candidate")
        labels.append("human_review_required")
        modes.append("human_reviewed_training_candidate")
        review_required = True
        reasons.append("Training examples remain candidates only; no automatic weight update is allowed.")

    if event.learning_signal.confidence < 0.8:
        review_required = True
        reasons.append("Confidence below 0.80 requires review before promotion.")

    if event.agent_task_type in {"coding", "debugging", "tool_orchestration", "architecture"}:
        modes.append("prompt_policy_candidate")
        modes.append("routing_policy_candidate")

    labels = _dedupe(labels)
    modes = _dedupe(modes)
    if review_required and "human_review_required" not in labels:
        labels.append("human_review_required")

    if not labels:
        labels = ["discard"]
        reasons.append("No safe learning signal was present.")

    queue_required = labels != ["discard"] and not event.safety.contains_secrets
    return TriageDecision(
        event_id=event.event_id,
        labels=labels,
        queue_required=queue_required,
        review_required=review_required,
        reasons=reasons,
        blocked_reason=None if queue_required else "no-safe-learning-signal",
        safe_optimization_modes=modes,
    )


def _dedupe(items: list) -> list:
    return list(dict.fromkeys(items))
