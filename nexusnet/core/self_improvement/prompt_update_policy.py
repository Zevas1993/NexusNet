from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .event_schema import ImprovementEvent
from .triage import TriageDecision


class PromptPolicyCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    allowed: bool
    policy_scope: str
    requires_review: bool
    failure_modes: list[str] = Field(default_factory=list)
    proposed_instruction: str
    blocked_reasons: list[str] = Field(default_factory=list)


class PromptUpdatePolicy:
    def build_candidate(self, event: ImprovementEvent, decision: TriageDecision) -> PromptPolicyCandidate:
        allowed = "prompt_policy_candidate" in decision.safe_optimization_modes or bool(event.outcome.failure_modes)
        blocked: list[str] = []
        if event.safety.contains_secrets:
            allowed = False
            blocked.append("contains-secrets")
        scope = _scope_for_task(event.agent_task_type)
        failure_modes = [str(mode) for mode in event.outcome.failure_modes]
        proposed_instruction = (
            f"When handling {scope} work, inspect provenance, uncertainty, and failure signals "
            "before promoting memory, routing, or policy changes."
        )
        return PromptPolicyCandidate(
            event_id=event.event_id,
            allowed=allowed,
            policy_scope=scope,
            requires_review=decision.review_required,
            failure_modes=failure_modes,
            proposed_instruction=proposed_instruction,
            blocked_reasons=blocked,
        )


def _scope_for_task(agent_task_type: str) -> str:
    if agent_task_type in {"architecture", "planning"}:
        return "architecture-routing"
    if agent_task_type in {"coding", "debugging"}:
        return "coding-debugging"
    if agent_task_type in {"research", "documentation"}:
        return "research-documentation"
    return "general-self-improvement"
