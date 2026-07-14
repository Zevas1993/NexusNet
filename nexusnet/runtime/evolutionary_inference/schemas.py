from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HardwareNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    node_id: str
    kind: Literal["cpu", "system-ram", "storage", "gpu"]
    name: str
    backend: Literal["portable", "cuda", "rocm", "metal"] = "portable"
    memory_bytes: int | None = Field(default=None, ge=0)
    logical_units: int | None = Field(default=None, ge=1)
    capabilities: list[str] = Field(default_factory=list)


class HardwareLink(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_node_id: str
    target_node_id: str
    kind: Literal["memory-access", "storage-transfer", "accelerator-transfer"]
    measured_bandwidth_gib_s: float | None = Field(default=None, ge=0)


class AcceleratorAdapterObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    backend: Literal["cuda", "rocm", "metal"]
    available: bool
    reason_code: str
    device_count: int = Field(default=0, ge=0)


class CalibrationMetric(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metric_id: str
    value: float = Field(gt=0)
    unit: str
    sample_count: int = Field(gt=0)
    duration_ms: float = Field(gt=0)
    target_node_ids: list[str] = Field(min_length=1)


class HardwareCapabilityGraph(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    host_fingerprint: str
    collected_at: datetime
    nodes: list[HardwareNode]
    links: list[HardwareLink]
    adapters: list[AcceleratorAdapterObservation]
    calibration: list[CalibrationMetric] = Field(default_factory=list)


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
    model_fingerprint: ModelExecutionFingerprint
    primitives: list[InferencePrimitive]
    feasibility: CandidateFeasibility
    artifact_ref: str | None = None
    policy_mutation_allowed: Literal[False] = False
