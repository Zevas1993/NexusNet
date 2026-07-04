from __future__ import annotations

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from .event_schema import ImprovementEvent


TrustLevel = Literal["unsupported", "partial", "reviewable"]


def provenance_id() -> str:
    return f"improveprov::{uuid4()}"


class ProvenanceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provenance_id: str = Field(default_factory=provenance_id)
    event_id: str
    source_count: int
    evidence_count: int
    verifier_count: int
    unsupported_source_ids: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    verifier_refs: list[str] = Field(default_factory=list)
    trust_level: TrustLevel


class ProvenanceTracker:
    def record(self, event: ImprovementEvent, *, verifier_refs: list[str] | None = None) -> ProvenanceRecord:
        unsupported = [
            source.source_id or "<missing-source-id>"
            for source in event.context_sources
            if not source.source_id or not source.provenance
        ]
        verifier_refs = verifier_refs or []
        evidence_count = len(event.context_sources) - len(unsupported)
        if unsupported or evidence_count == 0:
            trust_level: TrustLevel = "unsupported"
        elif verifier_refs:
            trust_level = "reviewable"
        else:
            trust_level = "partial"
        return ProvenanceRecord(
            event_id=event.event_id,
            source_count=len(event.context_sources),
            evidence_count=evidence_count,
            verifier_count=len(verifier_refs),
            unsupported_source_ids=unsupported,
            evidence_refs=list(event.evidence_refs),
            verifier_refs=verifier_refs,
            trust_level=trust_level,
        )
