from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    kind: str
    subject_ref: str
    payload: dict[str, Any] = Field(default_factory=dict)
    source_refs: list[str] = Field(default_factory=list)
    previous_hash: str = ""
    content_hash: str
    artifact_path: str | None = None
