from pathlib import Path

import pytest

from nexusnet.evolution.contracts import EvolvableUnit, GenomeRef
from nexusnet.evolution.registry import EvolvableUnitRegistry
from nexusnet.evolution.store import EvolutionEventStore
from nexusnet.hive.self_improvement_engine import IMPROVABLE_ASPECTS, default_engine


def _runtime_unit(**overrides) -> EvolvableUnit:
    values = {
        "unit_id": "unit:runtime:new-backend",
        "unit_kind": "runtime",
        "owner_brain_ref": "brain:NexusBrain",
        "authority_class": "mother-brain-governed",
        "privacy_class": "sanitized-metadata",
        "license_state": "reviewed",
        "trust_state": "quarantined",
        "federation_policy": "local-only",
        "lifecycle_state": "observed",
        "eval_suite_refs": ["eval:runtime-v1"],
        "invariant_refs": ["policy:north-star-v1"],
        "checkpoint_refs": ["checkpoint:baseline-v1"],
        "rollback_refs": ["checkpoint:baseline-v1"],
    }
    values.update(overrides)
    return EvolvableUnit(**values)


def test_legacy_lanes_become_registry_units_without_claiming_universal_completion(
    tmp_path: Path,
):
    registry = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    registry.adapt_self_improvement_engine(default_engine())
    coverage = registry.coverage()
    assert coverage["legacy_aspect_total"] == len(IMPROVABLE_ASPECTS)
    assert coverage["legacy_aspect_covered"] == len(IMPROVABLE_ASPECTS)
    assert coverage["legacy_taxonomy_fully_covered"] is True
    assert coverage["universal_coverage_complete"] is False
    assert (
        coverage["claim_boundary"]
        == "legacy-lane-coverage-is-not-universal-organism-coverage"
    )


def test_registered_uncovered_unit_is_reported_honestly(tmp_path: Path):
    registry = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    registry.register_unit(
        _runtime_unit(improvement_strategy_refs=[])
    )
    coverage = registry.coverage()
    assert coverage["uncovered_unit_refs"] == ["unit:runtime:new-backend"]


def test_registry_replays_units_after_restart(tmp_path: Path):
    store = EvolutionEventStore(tmp_path)
    first = EvolvableUnitRegistry(store)
    first.adapt_self_improvement_engine(default_engine())
    restarted = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    assert len(restarted.list_units()) == len(IMPROVABLE_ASPECTS)


def test_registration_is_idempotent_only_for_identical_records(tmp_path: Path):
    registry = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    unit = _runtime_unit(improvement_strategy_refs=["strategy:runtime-v1"])
    registry.register_unit(unit)
    registry.register_unit(unit)
    assert len(registry.list_units()) == 1
    assert len(EvolutionEventStore(tmp_path).replay()) == 1

    with pytest.raises(ValueError, match="conflicting evolution identity"):
        registry.register_unit(unit.model_copy(update={"trust_state": "reviewed"}))


def test_registry_registers_and_replays_genomes(tmp_path: Path):
    registry = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    genome = GenomeRef(
        genome_id="genome:runtime:v1",
        family="runtime",
        content_ref="sha256:" + "a" * 64,
        invariant_refs=["policy:north-star-v1"],
    )
    registry.register_genome(genome)
    registry.register_genome(genome)

    restarted = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    assert restarted.list_genomes() == [genome]

    with pytest.raises(ValueError, match="conflicting evolution identity"):
        restarted.register_genome(
            genome.model_copy(update={"content_ref": "sha256:" + "b" * 64})
        )
