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

REFERENCE_SCHEMES = frozenset(
    {
        "artifact",
        "benchmark",
        "brain",
        "candidate",
        "capability",
        "checkpoint",
        "dependency",
        "endpoint",
        "eval",
        "evidence",
        "experiment",
        "external",
        "federation",
        "foundation",
        "genome",
        "governance",
        "hardware",
        "health",
        "implementation",
        "invariant",
        "model",
        "pathway",
        "policy",
        "pressure",
        "prompt",
        "release",
        "resource",
        "runtime",
        "schema",
        "service",
        "skill",
        "snapshot",
        "strategy",
        "tool",
        "unit",
        "workload",
    }
)
REFERENCE_PATTERN = re.compile(
    r"^(?P<scheme>[a-z][a-z0-9-]*):"
    r"[A-Za-z0-9][A-Za-z0-9._-]*(?::[A-Za-z0-9][A-Za-z0-9._-]*)*$"
)
SHA256_REFERENCE_PATTERN = re.compile(r"^sha256:[0-9a-fA-F]{64}$")
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9-]*$")
SECRET_REFERENCE_PATTERN = re.compile(
    r"(?i)\b(?:sk-[A-Za-z0-9_-]+|bearer\s+\S+|begin private key)\b"
)


def sanitize_reference(value: str) -> str:
    normalized = value.strip()
    if len(normalized) > 512:
        raise ValueError("unsafe reference: maximum length is 512 characters")
    if SECRET_REFERENCE_PATTERN.search(normalized):
        raise ValueError("unsafe reference: secret material is forbidden")
    match = REFERENCE_PATTERN.fullmatch(normalized)
    if SHA256_REFERENCE_PATTERN.fullmatch(normalized):
        return normalized
    if match is None or match.group("scheme") not in REFERENCE_SCHEMES:
        raise ValueError(
            "unsafe reference: use an allowlisted scheme and opaque identifier tokens"
        )
    return normalized


class _FrozenSanitizedModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


def _validate_identifier(value: str) -> str:
    if not IDENTIFIER_PATTERN.fullmatch(value):
        raise ValueError("unsafe identifier: expected an opaque identifier token")
    return value


def _sanitize_optional_reference(value: str | None) -> str | None:
    return sanitize_reference(value) if value is not None else None


def _sanitize_reference_list(values: list[str]) -> list[str]:
    return [sanitize_reference(value) for value in values]


def _validate_identifier_or_reference_list(values: list[str]) -> list[str]:
    return [
        sanitize_reference(value) if ":" in value else _validate_identifier(value)
        for value in values
    ]


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

    @field_validator("unit_id")
    @classmethod
    def validate_unit_id(cls, value: str) -> str:
        return sanitize_reference(value)

    @field_validator("owner_brain_ref")
    @classmethod
    def validate_owner_brain_ref(cls, value: str) -> str:
        sanitized = sanitize_reference(value)
        if sanitized != "brain:NexusBrain":
            raise ValueError("owner_brain_ref must be brain:NexusBrain")
        return sanitized

    @field_validator("current_release_ref", "registration_schema_ref")
    @classmethod
    def validate_optional_refs(cls, value: str | None) -> str | None:
        return _sanitize_optional_reference(value)

    @field_validator(
        "parent_unit_refs",
        "child_unit_refs",
        "capability_refs",
        "genome_refs",
        "implementation_refs",
        "dependency_refs",
        "pathway_refs",
        "checkpoint_refs",
        "health_refs",
        "workload_refs",
        "eval_suite_refs",
        "invariant_refs",
        "growth_pressure_refs",
        "candidate_refs",
        "rollback_refs",
        "improvement_strategy_refs",
    )
    @classmethod
    def validate_reference_lists(cls, values: list[str]) -> list[str]:
        return _sanitize_reference_list(values)

    @field_validator(
        "unit_kind",
        "authority_class",
        "privacy_class",
        "license_state",
        "trust_state",
        "federation_policy",
    )
    @classmethod
    def validate_identifiers(cls, value: str) -> str:
        return _validate_identifier(value)

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

    @field_validator("genome_id", "content_ref")
    @classmethod
    def validate_refs(cls, value: str) -> str:
        return sanitize_reference(value)

    @field_validator("invariant_refs")
    @classmethod
    def validate_reference_lists(cls, values: list[str]) -> list[str]:
        return _sanitize_reference_list(values)


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

    @field_validator("pressure_id")
    @classmethod
    def validate_pressure_id(cls, value: str) -> str:
        return sanitize_reference(value)

    @field_validator(
        "target_unit_refs", "source_evidence_refs", "affected_workloads"
    )
    @classmethod
    def validate_reference_lists(cls, values: list[str]) -> list[str]:
        return _sanitize_reference_list(values)

    @field_validator("affected_hardware_classes")
    @classmethod
    def validate_hardware_classes(cls, values: list[str]) -> list[str]:
        return _validate_identifier_or_reference_list(values)

    @field_validator("problem_class", "status")
    @classmethod
    def validate_identifiers(cls, value: str) -> str:
        return _validate_identifier(value)


class FoundationCheck(_FrozenSanitizedModel):
    schema_version: Literal["nexusnet-evolution-v1"] = EVOLUTION_SCHEMA_VERSION
    foundation_id: str
    status: Literal["verified", "missing", "unverified"]
    evidence_ref: str | None = None
    claim_boundary: Literal["reference-presence-is-not-semantic-proof"]

    @field_validator("foundation_id")
    @classmethod
    def validate_foundation_id(cls, value: str) -> str:
        return sanitize_reference(value)

    @field_validator("evidence_ref")
    @classmethod
    def validate_evidence_ref(cls, value: str | None) -> str | None:
        return _sanitize_optional_reference(value)


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

    @field_validator("snapshot_id")
    @classmethod
    def validate_snapshot_id(cls, value: str) -> str:
        return sanitize_reference(value)

    @field_validator(
        "registered_unit_refs",
        "implementation_refs",
        "dependency_refs",
        "pathway_refs",
        "capability_refs",
        "health_refs",
        "workload_refs",
        "resource_refs",
        "benchmark_refs",
        "candidate_refs",
        "governance_refs",
        "external_alternative_refs",
        "unresolved_refs",
    )
    @classmethod
    def validate_reference_lists(cls, values: list[str]) -> list[str]:
        return _sanitize_reference_list(values)
