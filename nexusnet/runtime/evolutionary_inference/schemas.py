from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexusnet.runtime.hardware_contracts import (
    AcceleratorAdapterObservation,
    AcceleratorBackend,
    CalibrationMetric,
    HardwareCapabilityGraph,
    HardwareLink,
    HardwareNode,
    VerificationState,
)


class TensorGroupMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    group_id: str
    bytes: int = Field(gt=0)
    dtype: str
    layout: str


class RuntimeModelMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    architecture_family: str
    parameter_count: int = Field(gt=0)
    tensor_bytes: int = Field(gt=0)
    quantization: str
    context_length: int = Field(gt=0)
    layer_count: int = Field(gt=0)
    expert_count: int = Field(default=0, ge=0)
    experts_per_token: int = Field(default=0, ge=0)
    modalities: list[str] = Field(default_factory=lambda: ["text"], min_length=1)
    operator_families: list[str] = Field(min_length=1)
    tensor_groups: list[TensorGroupMetadata] = Field(min_length=1)
    state_and_kv_contract: dict[str, Any] = Field(default_factory=dict)
    sparsity_and_router_contract: dict[str, Any] = Field(default_factory=dict)
    dynamic_shape_contract: dict[str, bool] = Field(default_factory=dict)
    custom_operator_requirements: list[str] = Field(default_factory=list)
    rights_and_artifact_refs: list[str] = Field(default_factory=list)
    unknown_or_unsupported_features: list[str] = Field(default_factory=list)
    provenance_ref: str = ""


class ModelExecutionFingerprint(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    fingerprint_id: str
    architecture_family: str
    parameter_count: int = Field(gt=0)
    tensor_bytes: int = Field(gt=0)
    quantization: str
    context_length: int = Field(gt=0)
    layer_count: int = Field(gt=0)
    expert_count: int = Field(default=0, ge=0)
    experts_per_token: int = Field(default=0, ge=0)
    modalities: list[str] = Field(min_length=1)
    source_kind: Literal["trusted-synthetic", "metadata"]
    graph_digest: str = ""
    operator_families: list[str] = Field(default_factory=list)
    tensor_groups: list[TensorGroupMetadata] = Field(default_factory=list)
    state_and_kv_contract: dict[str, Any] = Field(default_factory=dict)
    sparsity_and_router_contract: dict[str, Any] = Field(default_factory=dict)
    dynamic_shape_contract: dict[str, bool] = Field(default_factory=dict)
    custom_operator_requirements: list[str] = Field(default_factory=list)
    rights_and_artifact_refs: list[str] = Field(default_factory=list)
    unknown_or_unsupported_features: list[str] = Field(default_factory=list)


class InferencePrimitive(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    primitive_id: str
    description: str
    compatible_model_families: list[str]
    required_resources: list[str]
    effects: list[str]
    implementation_state: Literal["available", "unavailable"]
    evidence_state: Literal["portable-reference", "existing-implementation", "unverified"]
    adapter_path: str | None = None
    required_capabilities: list[str] = Field(default_factory=list)
    compatible_operator_families: list[str] = Field(default_factory=lambda: ["all"])
    conflicts: list[str] = Field(default_factory=list)
    fallback_primitive_id: str | None = None
    implementation_digest: str = ""
    reversible_parameters: list[str] = Field(default_factory=list)
    quality_semantics: Literal["bit-equivalent", "external-evidence-required"] = "bit-equivalent"
    evidence_requirements: list[str] = Field(default_factory=list)
    approval_required: bool = False


class FeasibilityCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    primitive_id: str
    feasible: bool
    score: float = Field(ge=0, le=1)
    reason_codes: list[str]


class CandidateFeasibility(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    status: Literal["shadow-feasible", "blocked"]
    selected_primitive_id: str | None
    candidates: list[FeasibilityCandidate]
    reason_codes: list[str]
    blockers: list[str]
    confidence: float = Field(ge=0, le=1)
    policy_mutation_allowed: Literal[False] = False


class EvolutionaryInferenceEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    evidence_id: str
    created_at: datetime
    hardware: HardwareCapabilityGraph
    model_fingerprint: ModelExecutionFingerprint | None = None
    primitives: list[InferencePrimitive]
    feasibility: CandidateFeasibility | None = None
    artifact_ref: str | None = None
    policy_mutation_allowed: Literal[False] = False


class WorkloadProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    prompt_tokens: int = Field(ge=0)
    max_new_tokens: int = Field(gt=0)
    batch_size: int = Field(default=1, gt=0)
    concurrent_requests: int = Field(default=1, gt=0)


class SLOProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    objective: Literal["latency", "throughput", "memory", "balanced"] = "balanced"
    max_latency_ms: float | None = Field(default=None, gt=0)
    min_throughput_tokens_s: float | None = Field(default=None, gt=0)
    max_peak_ram_bytes: int | None = Field(default=None, gt=0)
    max_peak_vram_bytes: int | None = Field(default=None, gt=0)
    require_quality_equivalence: bool = True


class TransferRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Literal["pageable", "storage", "double-buffered", "accelerator"]
    bytes: int = Field(gt=0, le=16 * 1024 * 1024)
    chunk_bytes: int = Field(gt=0, le=8 * 1024 * 1024)
    repeat_count: int = Field(default=3, gt=0, le=8)
    compute_iterations: int = Field(default=256, ge=0, le=100_000)
    backend: Literal["portable", "cuda", "rocm", "metal"] = "portable"
    direction: Literal["host-to-host", "storage-roundtrip", "host-to-device"] = "host-to-host"


class TransferEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["completed", "backend-unavailable", "preempted", "failed"]
    kind: str
    backend: str
    direction: str
    bytes_per_repeat: int = Field(ge=0)
    bytes_moved: int = Field(ge=0)
    chunk_bytes: int = Field(gt=0)
    repeat_count: int = Field(ge=0)
    duration_ms: list[float]
    cold_duration_ms: float | None = Field(default=None, ge=0)
    warm_duration_ms: float | None = Field(default=None, ge=0)
    effective_bandwidth_gib_s: float = Field(ge=0)
    overlap_ratio: float = Field(ge=0, le=1)
    synchronization_count: int = Field(ge=0)
    checksum_equivalent: bool
    reason_codes: list[str] = Field(default_factory=list)


class ExecutionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    plan_id: str
    primitive_ids: list[str] = Field(min_length=1)
    parameters: dict[str, int | float | str | bool]
    fallback_plan_id: str | None
    estimated_peak_ram_bytes: int = Field(ge=0)
    estimated_peak_vram_bytes: int = Field(ge=0)
    quality_semantics: Literal["bit-equivalent", "external-evidence-required"] = "bit-equivalent"
    reversible: bool = True
    approval_required: bool = False
    feature_key: str


class PlanEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    plan: ExecutionPlan
    status: Literal["completed", "failed", "preempted", "backend-unavailable"]
    repeat_count: int = Field(ge=0)
    cold_latency_ms: float | None = Field(default=None, ge=0)
    warm_latency_ms: float | None = Field(default=None, ge=0)
    throughput_tokens_s: float = Field(ge=0)
    peak_ram_bytes: int = Field(ge=0)
    peak_vram_bytes: int = Field(ge=0)
    bytes_moved: int = Field(ge=0)
    energy_joules: float | None = Field(default=None, ge=0)
    quality_equivalent: bool
    stable: bool
    uncertainty: float = Field(ge=0)
    measurements_ms: list[float]
    checksum: str
    reason_codes: list[str] = Field(default_factory=list)


class RuntimeObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    plan_id: str
    latency_ms: float = Field(ge=0)
    quality_equivalent: bool
    stable: bool
    peak_ram_bytes: int | None = Field(default=None, ge=0)
    peak_vram_bytes: int | None = Field(default=None, ge=0)


class CapacityGate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    serving_idle: bool
    thermal_ok: bool
    memory_ok: bool
    power_ok: bool
    budget_remaining: int = Field(ge=0, le=64)


class DreamCycleEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    cycle_id: str
    status: Literal["gated", "preempted-safe-checkpoint", "promoted", "rejected", "no-model"]
    trials_completed: int = Field(ge=0)
    candidate_plan_ids: list[str] = Field(default_factory=list)
    promoted_plan_id: str | None = None
    reason_codes: list[str] = Field(default_factory=list)
    trial_evidence: list[PlanEvidence] = Field(default_factory=list)
