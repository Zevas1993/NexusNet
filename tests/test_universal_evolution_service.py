from pathlib import Path

import pytest

from nexusnet.evolution.contracts import EvolvableUnit, GenomeRef
from nexusnet.evolution.registry import EvolvableUnitRegistry
from nexusnet.evolution.store import EvolutionEventStore
from nexusnet.hive.self_improvement_engine import IMPROVABLE_ASPECTS, default_engine


class _PartialEngine:
    def __init__(self, covered: str, uncovered: str):
        self.lanes = {covered: lambda _: {"improved": False}}
        self._covered = covered
        self._uncovered = uncovered

    def coverage(self):
        return {
            "total_aspects": 2,
            "covered": [self._covered],
            "covered_count": 1,
            "uncovered": [self._uncovered],
            "coverage_ratio": 0.5,
            "fully_covered": False,
        }


class _FailsOnceStore(EvolutionEventStore):
    def __init__(self, root: Path, failed_event_type: str):
        super().__init__(root)
        self.failed_event_type = failed_event_type
        self.failed = False

    def append(self, event_type: str, payload: dict):
        if event_type == self.failed_event_type and not self.failed:
            self.failed = True
            raise OSError("simulated append failure")
        return super().append(event_type, payload)


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


def _organism_unit() -> EvolvableUnit:
    return EvolvableUnit(
        unit_id="unit:organism:nexus",
        unit_kind="organism",
        owner_brain_ref="brain:NexusBrain",
        authority_class="mother-brain-governed",
        privacy_class="sanitized-metadata",
        license_state="repository-governed",
        trust_state="observed",
        federation_policy="sanitized-evidence-only",
        lifecycle_state="observed",
        registration_schema_ref="schema:evolvable-organism-v1",
        eval_suite_refs=["eval:organism-v1"],
        invariant_refs=["policy:north-star-v1"],
        rollback_refs=["checkpoint:organism-baseline-v1"],
        improvement_strategy_refs=["strategy:organism-evolution-v1"],
    )


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


def test_covered_non_organism_unit_does_not_complete_universal_coverage(
    tmp_path: Path,
):
    registry = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    registry.register_unit(
        _runtime_unit(improvement_strategy_refs=["strategy:runtime-v1"])
    )
    assert registry.coverage()["universal_coverage_complete"] is False


def test_covered_organism_unit_can_complete_universal_coverage(tmp_path: Path):
    registry = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    registry.register_unit(_organism_unit())
    assert registry.coverage()["universal_coverage_complete"] is True


def test_registry_replays_units_after_restart(tmp_path: Path):
    store = EvolutionEventStore(tmp_path)
    first = EvolvableUnitRegistry(store)
    first.adapt_self_improvement_engine(default_engine())
    restarted = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    assert len(restarted.list_units()) == len(IMPROVABLE_ASPECTS)
    assert restarted.coverage() == first.coverage()


def test_partial_legacy_taxonomy_coverage_is_replay_stable(tmp_path: Path):
    registry = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    registry.adapt_self_improvement_engine(
        _PartialEngine(covered="tokenizer", uncovered="federation")
    )
    before_restart = registry.coverage()

    restarted = EvolvableUnitRegistry(EvolutionEventStore(tmp_path))
    assert restarted.coverage() == before_restart
    assert before_restart["legacy_aspect_total"] == 2
    assert before_restart["legacy_aspect_covered"] == 1
    assert before_restart["legacy_taxonomy_fully_covered"] is False


def test_legacy_taxonomy_observation_is_idempotent_and_conflicts_fail(
    tmp_path: Path,
):
    store = EvolutionEventStore(tmp_path)
    registry = EvolvableUnitRegistry(store)
    engine = _PartialEngine(covered="tokenizer", uncovered="federation")
    registry.adapt_self_improvement_engine(engine)
    registry.adapt_self_improvement_engine(engine)
    events = store.replay()
    assert [event["event_type"] for event in events] == [
        "unit.registered",
        "legacy-taxonomy.observed",
    ]
    assert events[-1]["payload"] == {
        "legacy_taxonomy_id": "schema:legacy-self-improvement-taxonomy-v1",
        "legacy_aspect_total": 2,
        "legacy_taxonomy_fully_covered": False,
        "aspect_refs": [
            "capability:self-improvement:federation",
            "capability:self-improvement:tokenizer",
        ],
        "covered_refs": ["capability:self-improvement:tokenizer"],
        "uncovered_refs": ["capability:self-improvement:federation"],
    }

    before_conflict = registry.list_units()
    with pytest.raises(ValueError, match="conflicting evolution identity"):
        registry.adapt_self_improvement_engine(
            _PartialEngine(covered="federation", uncovered="tokenizer")
        )
    assert registry.list_units() == before_conflict
    assert len(store.replay()) == 2


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


def test_failed_unit_append_does_not_mutate_registry_and_retry_persists(
    tmp_path: Path,
):
    store = _FailsOnceStore(tmp_path, "unit.registered")
    registry = EvolvableUnitRegistry(store)
    unit = _runtime_unit(improvement_strategy_refs=["strategy:runtime-v1"])

    with pytest.raises(OSError, match="simulated append failure"):
        registry.register_unit(unit)
    assert registry.list_units() == []

    registry.register_unit(unit)
    assert EvolvableUnitRegistry(EvolutionEventStore(tmp_path)).list_units() == [unit]


def test_failed_genome_append_does_not_mutate_registry_and_retry_persists(
    tmp_path: Path,
):
    store = _FailsOnceStore(tmp_path, "genome.registered")
    registry = EvolvableUnitRegistry(store)
    genome = GenomeRef(
        genome_id="genome:runtime:retry-v1",
        family="runtime",
        content_ref="sha256:" + "c" * 64,
    )

    with pytest.raises(OSError, match="simulated append failure"):
        registry.register_genome(genome)
    assert registry.list_genomes() == []

    registry.register_genome(genome)
    assert EvolvableUnitRegistry(EvolutionEventStore(tmp_path)).list_genomes() == [
        genome
    ]
