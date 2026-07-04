from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .event_schema import ImprovementEvent
from .provenance import ProvenanceRecord
from .triage import TriageDecision


TrainingCandidateStatus = Literal["blocked", "review_required", "ready_for_review"]


class TrainingCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    provenance_id: str
    allowed: bool
    status: TrainingCandidateStatus
    export_ready: bool
    prompt: str
    response_summary: str
    negative_signals: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)


class TrainingCandidateBuilder:
    def build_candidate(
        self,
        event: ImprovementEvent,
        decision: TriageDecision,
        provenance: ProvenanceRecord,
    ) -> TrainingCandidate:
        blocked: list[str] = []
        if "create_training_candidate" not in decision.labels:
            blocked.append("triage-did-not-request-training-candidate")
        if event.safety.contains_secrets:
            blocked.append("contains-secrets")
        if event.safety.contains_private_data:
            blocked.append("private-data-review-required")
        if provenance.unsupported_source_ids:
            blocked.append("unsupported-provenance")

        allowed = not blocked
        if not allowed:
            status: TrainingCandidateStatus = "blocked"
        elif decision.review_required:
            status = "review_required"
        else:
            status = "ready_for_review"
        return TrainingCandidate(
            event_id=event.event_id,
            provenance_id=provenance.provenance_id,
            allowed=allowed,
            status=status,
            export_ready=allowed and status == "ready_for_review",
            prompt=event.user_goal,
            response_summary=event.final_output_summary,
            negative_signals=[str(mode) for mode in event.outcome.failure_modes],
            evidence_refs=list(event.evidence_refs),
            blocked_reasons=blocked,
        )
