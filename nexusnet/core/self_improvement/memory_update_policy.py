from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .event_schema import ImprovementEvent, RetentionPolicy
from .provenance import ProvenanceRecord
from .triage import TriageDecision


class MemoryUpdateCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    allowed: bool
    requires_review: bool
    retention_policy: RetentionPolicy
    claims: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)


class MemoryUpdatePolicy:
    def build_candidate(
        self,
        event: ImprovementEvent,
        decision: TriageDecision,
        provenance: ProvenanceRecord,
    ) -> MemoryUpdateCandidate:
        blocked: list[str] = []
        if "store_as_project_memory" not in decision.labels:
            blocked.append("triage-did-not-allow-memory")
        if event.safety.contains_secrets:
            blocked.append("contains-secrets")
        if event.safety.contains_private_data:
            blocked.append("private-data-review-required")
        if provenance.unsupported_source_ids:
            blocked.append("unsupported-provenance")

        return MemoryUpdateCandidate(
            event_id=event.event_id,
            allowed=not blocked,
            requires_review=decision.review_required,
            retention_policy=event.safety.retention_policy,
            claims=[event.final_output_summary] if event.final_output_summary else [],
            evidence_refs=list(event.evidence_refs),
            blocked_reasons=blocked,
        )
