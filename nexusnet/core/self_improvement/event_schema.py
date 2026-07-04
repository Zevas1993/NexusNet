from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


PROJECT_NAME = "NexusNet Neural Core AI Brain"
SOURCE_DOCUMENT_REFS = [
    "arXiv:2510.02665",
    "arXiv:2411.17760",
    "docs/SELF_IMPROVEMENT_LAYER.md",
]

InputModality = Literal["text", "file", "image", "audio", "tool_output", "environment_state", "video"]
AgentTaskType = Literal[
    "architecture",
    "coding",
    "research",
    "debugging",
    "planning",
    "documentation",
    "multimodal",
    "tool_orchestration",
    "error_recovery",
]
SourceType = Literal["uploaded_file", "project_memory", "web", "tool", "user_message", "runtime_trace", "artifact"]
OutcomeStatus = Literal["success", "partial", "failed", "blocked", "needs_review"]
UserFeedback = Literal["positive", "negative", "neutral", "none"]
FailureMode = Literal["hallucination", "missing_context", "tool_error", "stale_info", "bad_reasoning", "policy_blocked", "privacy_risk"]
RetentionPolicy = Literal["discard", "session", "project", "long_term"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def improvement_event_id() -> str:
    return f"improve::{uuid4()}"


class ContextSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: SourceType
    source_id: str
    provenance: str
    evidence_ref: str | None = None


class Outcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: OutcomeStatus
    user_feedback: UserFeedback = "none"
    failure_modes: list[FailureMode] = Field(default_factory=list)


class LearningSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    should_store_memory: bool = False
    should_create_eval: bool = False
    should_create_training_example: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    review_required: bool = True


class SafetyClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contains_private_data: bool = False
    contains_secrets: bool = False
    retention_policy: RetentionPolicy = "session"


class ImprovementEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=improvement_event_id)
    timestamp: datetime = Field(default_factory=utc_now)
    project: str = PROJECT_NAME
    session_id: str
    input_modalities: list[InputModality] = Field(default_factory=list)
    user_goal: str
    agent_task_type: AgentTaskType
    context_sources: list[ContextSource] = Field(default_factory=list)
    agent_plan: str = ""
    actions_taken: list[str] = Field(default_factory=list)
    final_output_summary: str = ""
    outcome: Outcome
    learning_signal: LearningSignal = Field(default_factory=LearningSignal)
    safety: SafetyClassification = Field(default_factory=SafetyClassification)
    metrics: dict[str, float | int | str | bool] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    source_document_refs: list[str] = Field(default_factory=lambda: list(SOURCE_DOCUMENT_REFS))
    metadata: dict[str, Any] = Field(default_factory=dict)
