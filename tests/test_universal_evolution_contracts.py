from __future__ import annotations

import pytest
from pydantic import ValidationError

from nexusnet.evolution.contracts import (
    EVOLUTION_SCHEMA_VERSION,
    EvolvableUnit,
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
