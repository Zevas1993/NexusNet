from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EffectType = Literal[
    "filesystem_read",
    "filesystem_write",
    "network",
    "browser",
    "desktop",
    "shell",
    "model_update",
    "memory_update",
]


class AuthorityDecisionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str
    actor_ref: str
    effect_type: EffectType
    status: Literal["allowed-shadow", "blocked"]
    blockers: list[str] = Field(default_factory=list)
    capability_refs: list[str] = Field(default_factory=list)
    sandbox_state: str
    operator_approved: bool
    evidence_refs: list[str] = Field(default_factory=list)
    observed_effect_receipt: dict[str, object]
    rollback_record: dict[str, object]
    production_action_allowed: bool = False
    artifact_path: str | None = None
