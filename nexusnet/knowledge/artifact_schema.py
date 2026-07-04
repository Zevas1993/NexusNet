from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


KnowledgeStatus = Literal["candidate", "code_backed_candidate", "live_control_plane", "promoted", "blocked"]


class KnowledgeSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_ref: str
    title: str = ""
    text: str = ""
    source_url: str = ""
    permission_state: Literal["allowed", "restricted", "blocked"] = "allowed"
    privacy_class: str = "public"
    license_state: str = "pending_review"
    rbac_scope: list[str] = Field(default_factory=list)
    claims: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeCompileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_family: str
    sources: list[KnowledgeSource] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    scope: dict[str, Any] = Field(default_factory=dict)
    artifact_shape: dict[str, Any] = Field(default_factory=dict)
    freshness_policy: dict[str, Any] = Field(default_factory=dict)
    governance: dict[str, Any] = Field(default_factory=dict)


class KnowledgeRequestContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str
    contexts: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    output_shape: dict[str, Any] = Field(default_factory=dict)
    budget: dict[str, Any] = Field(default_factory=dict)


class KnowledgeArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    artifact_type: str = "task_context"
    task_family: str
    scope: dict[str, Any] = Field(default_factory=dict)
    content: dict[str, Any] = Field(default_factory=dict)
    field_citations: dict[str, list[str]] = Field(default_factory=dict)
    source_digests: list[dict[str, Any]] = Field(default_factory=list)
    confidence: dict[str, Any] = Field(default_factory=dict)
    conflict_objects: list[dict[str, Any]] = Field(default_factory=list)
    governance: dict[str, Any] = Field(default_factory=dict)
    freshness: dict[str, Any] = Field(default_factory=dict)
    status: KnowledgeStatus = "candidate"
    artifact_hash: str
    excluded_sources: list[dict[str, Any]] = Field(default_factory=list)
    blocked_source_refs: list[dict[str, Any]] = Field(default_factory=list)
    source_ref_security_gate: dict[str, Any] = Field(default_factory=dict)
    artifact_trust_preview: dict[str, Any] = Field(default_factory=dict)
    control_panel_replay: dict[str, Any] = Field(default_factory=dict)
    fallback_policy: dict[str, Any] = Field(default_factory=dict)
    validation: dict[str, Any] = Field(default_factory=dict)

    def validation_report(self) -> dict[str, Any]:
        required_fields = ["content.summary"]
        facts = self.content.get("facts") or []
        required_fields.extend(f"content.facts.{index}" for index, _ in enumerate(facts))
        relationships = self.content.get("relationships") or []
        required_fields.extend(f"content.relationships.{index}" for index, _ in enumerate(relationships))
        missing = [field for field in required_fields if not self.field_citations.get(field)]
        return {
            "valid": not missing,
            "required_citation_fields": required_fields,
            "missing_citation_fields": missing,
            "source_digest_count": len(self.source_digests),
            "conflict_count": len(self.conflict_objects),
        }
