from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


NodeType = Literal["NexusBrain", "O", "AO", "Expert", "MiniNexusNet", "Memory", "Evaluator", "Dream", "Runtime", "Other"]
PrivacyClass = Literal[
    "public",
    "licensed",
    "internal",
    "private_local",
    "private_redacted",
    "federated_sanitized",
    "blocked_private_raw",
]
LicenseState = Literal[
    "approved_train",
    "approved_eval_only",
    "research_only",
    "pending_review",
    "blocked_unclear",
    "blocked_anti_distillation",
    "blocked_private",
    "blocked_no_output_training",
]
GovernanceState = Literal[
    "draft",
    "blocked",
    "approved_for_dataset",
    "student_born",
    "training_planned",
    "training_running",
    "trained",
    "eval_failed",
    "eval_passed",
    "shadow_only",
    "canary_candidate",
    "promotable",
    "promoted",
    "teacher_ejection_candidate",
    "teacher_retired",
    "rejected",
    "side_barred",
    "rolled_back",
]
GrowthDecision = Literal["shadow_specialist", "promotable", "blocked", "side_barred", "rejected"]


class GrowthCycleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cycle_id: str = "cycle:cyc_demo_001"
    requested_by_node_ref: str = "node:operator"
    request_type: str = "failure_gap"
    operator_approved: bool = False
    target_node_id: str
    target_node_type: NodeType
    target_capabilities: list[str] = Field(default_factory=list)
    student_kind: str = "child_expert"
    birth_reason: str
    expected_artifact_type: str = "adapter"
    privacy_policy_ref: str = "policy:privacy_local_v0"
    license_policy_ref: str = "policy:teacher_license_v0"
    federation_policy_ref: str = "policy:federation_sanitized_v0"
    failure_refs: list[str] = Field(default_factory=list)
    dream_refs: list[str] = Field(default_factory=list)
    federated_prior_refs: list[str] = Field(default_factory=list)
    canon_refs: list[str] = Field(default_factory=list)
    teacher_pairing_refs: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    knowledge_artifact_refs: list[str] = Field(default_factory=list)
    knowledge_artifact_runtime_contexts: list[dict[str, Any]] = Field(default_factory=list)
    material_request_ref: str | None = None
    adapter_training_plan_ref: str | None = None
    adapter_training_plan_status: str = "unknown"
    adapter_training_gate: dict[str, Any] = Field(default_factory=dict)
    adapter_training_findings: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactHeader(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "artifact_header.v0.1"
    artifact_id: str
    artifact_type: str
    cycle_id: str
    student_id: str | None = None
    parent_refs: list[str] = Field(default_factory=list)
    teacher_refs: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    privacy_class: PrivacyClass = "internal"
    license_state: LicenseState = "approved_train"
    federation_policy: str = "non_federating"
    hash: str = ""
    signature_state: str = "unsigned_v0"
    storage_path: str = ""
    checkpoint_ref: str | None = None
    replay_refs: list[str] = Field(default_factory=list)
    governance_state: GovernanceState = "draft"
    created_at: datetime = Field(default_factory=utcnow)


class GrowthCycleRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "growth_cycle.v0.1"
    header: ArtifactHeader
    cycle_id: str
    status: str = "shadow_specialist"
    requested_by: dict[str, Any]
    target: dict[str, Any]
    birth_intent: dict[str, Any]
    policies: dict[str, str]
    refs: dict[str, list[str]]
    state_refs: dict[str, Any]
    governance: dict[str, Any]
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class DatasetManifestRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "dataset_manifest.v0.1"
    header: ArtifactHeader
    dataset_manifest_id: str
    cycle_id: str
    target_node_ref: str
    splits: dict[str, Any]
    license_summary: dict[str, int]
    privacy_summary: dict[str, int]


class TrainingRunRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "training_run.v0.1"
    header: ArtifactHeader
    train_id: str
    cycle_id: str
    student_id: str
    support_state: Literal["declared_supported", "planned", "dry_run_supported", "sandbox_supported", "production_supported"]
    actual_weight_mutation_allowed: bool = False
    declared_methods: list[str] = Field(default_factory=list)
    loss_contract: dict[str, Any] = Field(default_factory=dict)
    dataset_radar_training_prerequisites: dict[str, Any] = Field(default_factory=dict)
    output_artifacts: list[str] = Field(default_factory=list)


class ReviewerDecisionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "reviewer_decision.v0.1"
    header: ArtifactHeader
    monitor_id: str
    cycle_id: str
    student_id: str
    windows: dict[str, str]
    parent_comparison: dict[str, Any]
    teacher_comparison: dict[str, Any]
    hard_gates: dict[str, bool]
    decision: GrowthDecision
    teacher_ejection_eligible: bool = False
    reason: str
