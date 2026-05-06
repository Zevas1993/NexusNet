from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AssimilationSourceLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    packet_id: str
    online_spec_count: int
    video_spec_count: int
    total_spec_count: int
    status: Literal["refs_only_until_code_backed"] = "refs_only_until_code_backed"
    source_docs: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)

    @classmethod
    def full_2026_05_06_packet(cls) -> "AssimilationSourceLedger":
        return cls(
            packet_id="assimilation-2026-05-06-full-chat",
            online_spec_count=134,
            video_spec_count=10,
            total_spec_count=144,
            source_docs=[
                "docs/assimilation/online/2026-05-06/README.md",
                "docs/assimilation/online/2026-05-06/FINAL_MISSING_PIECE_SYNTHESIS.md",
                "docs/assimilation/videos/2026-05-06/README.md",
                "docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md",
            ],
            boundaries=[
                "refs_only_until_code_backed",
                "production_self_mutation_blocked",
                "consciousness_upload_claims_blocked",
                "operator_approval_required_for_active_promotion",
                "artifact_trust_required_for_promoted_artifacts",
            ],
        )


class NexusBodySchemaSnapshot(BaseModel):
    model_config = ConfigDict(extra="allow")

    surface_id: str = "nexus-body-schema"
    authority: str = "NexusBrain"
    runtime_state: Literal["static-canon", "live-bound", "degraded"] = "static-canon"
    capability_counts: dict[str, int] = Field(default_factory=dict)
    degraded_surfaces: list[str] = Field(default_factory=list)
    blocked_surfaces: list[str] = Field(default_factory=list)
    production_mutation_allowed: bool = False
    source_ledger: AssimilationSourceLedger = Field(default_factory=AssimilationSourceLedger.full_2026_05_06_packet)


FrameType = Literal["project", "task", "artifact", "tool", "model", "user_goal", "memory", "runtime", "policy"]


class ReferenceFrameRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frame_id: str
    frame_type: FrameType
    subject_ref: str
    facts: list[dict[str, str]] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    uncertainty: float = 0.0
    findings: list[str] = Field(default_factory=list)
    runtime_state: Literal["live-bound", "degraded"] = "live-bound"
    mutation_allowed: bool = False
    artifact_path: str | None = None
