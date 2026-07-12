from __future__ import annotations

import pytest
from pydantic import ValidationError

from nexusnet.evolution.contracts import (
    EVOLUTION_SCHEMA_VERSION,
    EvolvableUnit,
    FoundationCheck,
    GenomeRef,
    GrowthPressure,
    sanitize_reference,
)


def _unit(**overrides):
    payload = {
        "unit_id": "unit:runtime:vulkan-pilot",
        "unit_kind": "runtime",
        "owner_brain_ref": "brain:NexusBrain",
        "authority_class": "mother-brain-governed",
        "privacy_class": "sanitized-metadata",
        "license_state": "reviewed",
        "trust_state": "quarantined",
        "federation_policy": "local-only",
        "lifecycle_state": "observed",
        "eval_suite_refs": ["eval:runtime-portability-v1"],
        "invariant_refs": ["policy:north-star-v1"],
        "checkpoint_refs": ["checkpoint:runtime-baseline-v1"],
        "rollback_refs": ["checkpoint:runtime-baseline-v1"],
    }
    payload.update(overrides)
    return EvolvableUnit(**payload)


def test_known_unit_round_trips_with_versioned_contract():
    unit = _unit()
    payload = unit.model_dump(mode="json")
    assert payload["schema_version"] == EVOLUTION_SCHEMA_VERSION
    assert payload["owner_brain_ref"] == "brain:NexusBrain"
    assert EvolvableUnit.model_validate(payload) == unit


def test_unknown_kind_requires_schema_eval_privacy_authority_and_rollback():
    with pytest.raises(ValidationError, match="unknown unit kind"):
        _unit(unit_kind="invented-neural-organ")
    unit = _unit(
        unit_kind="invented-neural-organ",
        registration_schema_ref="schema:invented-neural-organ-v1",
    )
    assert unit.unit_kind == "invented-neural-organ"


@pytest.mark.parametrize(
    "unsafe",
    [
        "C:/Users/ChrisBoyd/private.txt",
        "F:\\NexusNet\\secret.bin",
        "sk-secret-token",
        "Bearer abcdef",
        "-----BEGIN PRIVATE KEY-----",
        "evidence:line-one\nline-two",
        "\\\\server\\share\\private.txt",
        "/home/chris/private.txt",
        "ChrisBoyd",
        "user:ChrisBoyd",
        "raw private prompt output",
        "evidence:sk-secret-token",
    ],
)
def test_reference_sanitizer_rejects_private_or_secret_material(unsafe: str):
    with pytest.raises(ValueError, match="unsafe reference"):
        sanitize_reference(unsafe)


def test_genome_and_pressure_use_refs_not_raw_content():
    genome = GenomeRef(
        genome_id="genome:runtime:v1",
        family="runtime",
        content_ref="sha256:" + "a" * 64,
        invariant_refs=["policy:north-star-v1"],
    )
    pressure = GrowthPressure(
        pressure_id="pressure:runtime:latency-1",
        target_unit_refs=["unit:runtime:vulkan-pilot"],
        source_evidence_refs=["evidence:benchmark:run-1"],
        problem_class="latency",
        severity=0.8,
        recurrence=3,
        quality_risk=0.1,
        safety_risk=0.0,
        opportunity_score=0.9,
        expected_value=0.85,
        research_budget_request=0.2,
        status="open",
    )
    assert genome.family == "runtime"
    assert pressure.recurrence == 3


def test_owner_brain_is_always_nexus_brain():
    with pytest.raises(ValidationError, match="brain:NexusBrain"):
        _unit(owner_brain_ref="brain:OtherBrain")


@pytest.mark.parametrize(
    "field_name",
    [
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
    ],
)
def test_evolvable_unit_reference_collections_reject_raw_content(field_name: str):
    with pytest.raises(ValidationError, match="unsafe reference"):
        _unit(**{field_name: ["raw private prompt output"]})


def test_narrative_fields_are_not_normalized_as_references():
    claim_boundary = "  reference presence is not semantic proof  "
    check = FoundationCheck(
        foundation_id="foundation:canon",
        status="verified",
        evidence_ref="evidence:canon:book-v1",
        claim_boundary=claim_boundary,
    )
    assert check.claim_boundary == claim_boundary
