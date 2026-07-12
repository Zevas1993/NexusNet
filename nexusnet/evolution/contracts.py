from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


EVOLUTION_SCHEMA_VERSION = "nexusnet-evolution-v1"

KNOWN_UNIT_KINDS = frozenset(
    {
        "model",
        "expert",
        "router",
        "O",
        "AO",
        "memory-plane",
        "retriever",
        "harness",
        "prompt",
        "execution-contract",
        "workflow",
        "tool",
        "skill",
        "runtime",
        "inference-backend",
        "kernel",
        "compiler",
        "quantization-method",
        "cache-method",
        "scheduler",
        "evaluator",
        "policy",
        "federation-method",
        "improvement-service",
    }
)

UNSAFE_REFERENCE_PATTERNS = (
    re.compile(r"^[A-Za-z]:[\\/]"),
    re.compile(r"(?i)\b(?:sk-[A-Za-z0-9_-]+|bearer\s+\S+|begin private key)\b"),
    re.compile(r"[\r\n\x00]"),
)


def sanitize_reference(value: str) -> str:
    normalized = value.strip()
    if not normalized or any(
        pattern.search(normalized) for pattern in UNSAFE_REFERENCE_PATTERNS
    ):
        raise ValueError(
            "unsafe reference: raw, local, secret, or multiline material is forbidden"
        )
    if len(normalized) > 512:
        raise ValueError("unsafe reference: maximum length is 512 characters")
    return normalized


class _FrozenSanitizedModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def sanitize_string_fields(cls, value):
        if isinstance(value, str):
            return sanitize_reference(value)
        if isinstance(value, (list, tuple)):
            return [
                sanitize_reference(item) if isinstance(item, str) else item
                for item in value
            ]
        return value


class EvolvableUnit(_FrozenSanitizedModel):
    schema_version: Literal["nexusnet-evolution-v1"] = EVOLUTION_SCHEMA_VERSION
    unit_id: str
    unit_kind: str
    owner_brain_ref: str
    parent_unit_refs: list[str] = Field(default_factory=list)
    child_unit_refs: list[str] = Field(default_factory=list)
    capability_refs: list[str] = Field(default_factory=list)
    genome_refs: list[str] = Field(default_factory=list)
    implementation_refs: list[str] = Field(default_factory=list)
    dependency_refs: list[str] = Field(default_factory=list)
    pathway_refs: list[str] = Field(default_factory=list)
    authority_class: str
    privacy_class: str
    license_state: str
    trust_state: str
    current_release_ref: str | None = None
    checkpoint_refs: list[str] = Field(default_factory=list)
    health_refs: list[str] = Field(default_factory=list)
    workload_refs: list[str] = Field(default_factory=list)
    eval_suite_refs: list[str] = Field(default_factory=list)
    invariant_refs: list[str] = Field(default_factory=list)
    growth_pressure_refs: list[str] = Field(default_factory=list)
    candidate_refs: list[str] = Field(default_factory=list)
    federation_policy: str
    lifecycle_state: Literal[
        "observed",
        "researched",
        "quarantined",
        "hypothesized",
        "dreamed",
        "synthesized",
        "build-passed",
        "sandboxed",
        "eval-passed",
        "shadow",
        "canary",
        "promotion-ready",
        "active",
        "side-barred",
        "rejected",
        "rolled-back",
        "retired",
        "superseded",
    ]
    registration_schema_ref: str | None = None
    rollback_refs: list[str] = Field(default_factory=list)
    improvement_strategy_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unknown_kind_contract(self) -> "EvolvableUnit":
        if self.unit_kind not in KNOWN_UNIT_KINDS:
            required = {
                "registration_schema_ref": self.registration_schema_ref,
                "eval_suite_refs": self.eval_suite_refs,
                "invariant_refs": self.invariant_refs,
                "rollback_refs": self.rollback_refs,
                "authority_class": self.authority_class,
                "privacy_class": self.privacy_class,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise ValueError(
                    "unknown unit kind requires governed registration fields: "
                    f"{', '.join(missing)}"
                )
        return self


class GenomeRef(_FrozenSanitizedModel):
    schema_version: Literal["nexusnet-evolution-v1"] = EVOLUTION_SCHEMA_VERSION
    genome_id: str
    family: Literal["model", "harness", "runtime", "organism"]
    content_ref: str
    invariant_refs: list[str] = Field(default_factory=list)


class GrowthPressure(_FrozenSanitizedModel):
    schema_version: Literal["nexusnet-evolution-v1"] = EVOLUTION_SCHEMA_VERSION
    pressure_id: str
    target_unit_refs: list[str] = Field(default_factory=list)
    source_evidence_refs: list[str] = Field(default_factory=list)
    problem_class: str
    severity: float = Field(ge=0.0, le=1.0)
    recurrence: int = Field(ge=0)
    affected_workloads: list[str] = Field(default_factory=list)
    affected_hardware_classes: list[str] = Field(default_factory=list)
    quality_risk: float = Field(ge=0.0, le=1.0)
    safety_risk: float = Field(ge=0.0, le=1.0)
    opportunity_score: float = Field(ge=0.0, le=1.0)
    expected_value: float = Field(ge=0.0, le=1.0)
    research_budget_request: float = Field(ge=0.0, le=1.0)
    status: str


class FoundationCheck(_FrozenSanitizedModel):
    schema_version: Literal["nexusnet-evolution-v1"] = EVOLUTION_SCHEMA_VERSION
    foundation_id: str
    status: Literal["verified", "missing", "unverified"]
    evidence_ref: str | None = None
    claim_boundary: str


class EverythingStateSnapshot(_FrozenSanitizedModel):
    schema_version: Literal["nexusnet-evolution-v1"] = EVOLUTION_SCHEMA_VERSION
    snapshot_id: str
    registered_unit_refs: list[str] = Field(default_factory=list)
    implementation_refs: list[str] = Field(default_factory=list)
    dependency_refs: list[str] = Field(default_factory=list)
    pathway_refs: list[str] = Field(default_factory=list)
    capability_refs: list[str] = Field(default_factory=list)
    health_refs: list[str] = Field(default_factory=list)
    workload_refs: list[str] = Field(default_factory=list)
    resource_refs: list[str] = Field(default_factory=list)
    benchmark_refs: list[str] = Field(default_factory=list)
    candidate_refs: list[str] = Field(default_factory=list)
    governance_refs: list[str] = Field(default_factory=list)
    external_alternative_refs: list[str] = Field(default_factory=list)
    unresolved_refs: list[str] = Field(default_factory=list)
