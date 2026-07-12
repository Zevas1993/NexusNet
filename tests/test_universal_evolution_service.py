from pathlib import Path

import pytest

from nexusnet.evolution.contracts import (
    EvolvableUnit,
    FoundationCheck,
    GenomeRef,
    GrowthPressure,
)
from nexusnet.evolution.foundation import FoundationVerifier
from nexusnet.evolution.pressure import GrowthPressureMap
from nexusnet.evolution.registry import EvolvableUnitRegistry
from nexusnet.evolution.service import UniversalEvolutionService
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


def test_service_projects_sanitized_restart_replayable_everything_state(
    tmp_path: Path,
):
    service = UniversalEvolutionService(
        artifacts_dir=tmp_path,
        owner_brain_ref="brain:NexusBrain",
        prerequisite_evidence={
            "mother_brain_authority": "evidence:brain:identity"
        },
        legacy_engine=default_engine(),
    )
    first = service.everything_state()

    restarted = UniversalEvolutionService(
        artifacts_dir=tmp_path,
        owner_brain_ref="brain:NexusBrain",
        prerequisite_evidence={
            "mother_brain_authority": "evidence:brain:identity"
        },
        legacy_engine=default_engine(),
    )
    second = restarted.everything_state()

    assert first["content_sha256"] == second["content_sha256"]
    assert second["authority"] == "NexusBrain"
    assert second["coverage"]["universal_coverage_complete"] is False
    assert "ChrisBoyd" not in str(second)


def test_service_exposes_compact_claim_bounded_projections(tmp_path: Path):
    service = UniversalEvolutionService(
        artifacts_dir=tmp_path,
        owner_brain_ref="brain:NexusBrain",
        prerequisite_evidence={"canon": None},
        legacy_engine=default_engine(),
    )
    unit = _runtime_unit(improvement_strategy_refs=["strategy:runtime-v1"])
    pressure = GrowthPressure(
        pressure_id="pressure:service:latency",
        target_unit_refs=[unit.unit_id],
        source_evidence_refs=["evidence:bench:service-latency"],
        problem_class="latency",
        severity=0.8,
        recurrence=4,
        quality_risk=0.1,
        safety_risk=0.0,
        opportunity_score=0.9,
        expected_value=0.9,
        research_budget_request=0.3,
        affected_workloads=["workload:interactive"],
        status="open",
    )

    assert service.register_unit(unit) == unit
    assert service.record_pressure(pressure) == pressure

    state = service.everything_state()
    units = service.evolvable_units()
    pressures = service.growth_pressure()
    status = service.status()

    assert state["claim_boundary"] == (
        "registry-and-evidence-state-only; no candidate, experiment, promotion, "
        "native-model-birth, or frontier-superiority claim"
    )
    assert next(
        item for item in state["units"] if item["unit_id"] == unit.unit_id
    ) == unit.model_dump(mode="json")
    assert state["open_pressures"][0]["pressure_id"] == pressure.pressure_id
    assert next(
        item for item in units["items"] if item["unit_id"] == unit.unit_id
    ) == unit.model_dump(mode="json")
    assert pressures["items"][0]["pressure_id"] == pressure.pressure_id
    assert status["unit_count"] == len(units["items"])
    assert status["open_pressure_count"] == 1
    assert status["missing_or_unverified_prerequisites"] == [
        "canon",
        "checkpoint",
        "evidence",
        "governance",
        "hive_blackboard",
        "isolation",
        "mother_brain_authority",
        "neural_bus",
        "replay",
        "rollback",
    ]
    assert status["mutation_boundary"] == "read-only-no-protected-state-mutation"
    assert set(status["endpoint_refs"]) == {
        "everything_state",
        "evolvable_units",
        "growth_pressure",
        "status",
    }
    assert "payload" not in status


def test_service_rejects_non_nexusbrain_ownership(tmp_path: Path):
    with pytest.raises(ValueError, match="owner_brain_ref must be brain:NexusBrain"):
        UniversalEvolutionService(
            artifacts_dir=tmp_path,
            owner_brain_ref="brain:OtherBrain",
            prerequisite_evidence={},
            legacy_engine=default_engine(),
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


def test_pressure_ranking_respects_value_priority_and_health_limits(tmp_path: Path):
    pressure_map = GrowthPressureMap(EvolutionEventStore(tmp_path))
    pressure_map.record(
        GrowthPressure(
            pressure_id="pressure:latency:1",
            target_unit_refs=["unit:runtime:a"],
            source_evidence_refs=["evidence:bench:1"],
            problem_class="latency",
            severity=0.8,
            recurrence=4,
            quality_risk=0.1,
            safety_risk=0.0,
            opportunity_score=0.9,
            expected_value=0.9,
            research_budget_request=0.3,
            affected_workloads=["workload:interactive"],
            status="open",
        )
    )
    pressure_map.record(
        GrowthPressure(
            pressure_id="pressure:safety:1",
            target_unit_refs=["unit:model:a"],
            source_evidence_refs=["evidence:eval:2"],
            problem_class="safety",
            severity=1.0,
            recurrence=1,
            quality_risk=0.8,
            safety_risk=1.0,
            opportunity_score=1.0,
            expected_value=1.0,
            research_budget_request=1.0,
            affected_workloads=["workload:protected"],
            status="open",
        )
    )

    ranked = pressure_map.ranked(
        workload_priority={
            "workload:interactive": 1.0,
            "workload:protected": 1.0,
        },
        system_health_limit=0.5,
    )

    assert ranked[0]["pressure_id"] == "pressure:latency:1"
    assert ranked[0]["priority_score"] == 0.82
    assert ranked[0]["executable_research_budget"] == 0.3
    assert ranked[1]["blocked_reason"] == (
        "safety-or-quality-risk-exceeds-system-health-limit"
    )
    assert ranked[1]["executable_research_budget"] == 0.0


def test_pressure_map_replays_open_pressure_and_summarizes_budget(tmp_path: Path):
    pressure = GrowthPressure(
        pressure_id="pressure:memory:1",
        target_unit_refs=["unit:runtime:a"],
        source_evidence_refs=["evidence:bench:memory-1"],
        problem_class="memory",
        severity=0.7,
        recurrence=2,
        quality_risk=0.1,
        safety_risk=0.0,
        opportunity_score=0.8,
        expected_value=0.7,
        research_budget_request=0.25,
        affected_workloads=["workload:interactive"],
        status="open",
    )
    GrowthPressureMap(EvolutionEventStore(tmp_path)).record(pressure)

    restarted = GrowthPressureMap(EvolutionEventStore(tmp_path))
    summary = restarted.summary(
        workload_priority={"workload:interactive": 1.0},
        system_health_limit=0.5,
    )

    assert summary["open_pressure_count"] == 1
    assert summary["blocked_pressure_count"] == 0
    assert summary["executable_research_budget_total"] == 0.25
    assert summary["pressures"][0]["pressure_id"] == pressure.pressure_id


def test_foundation_verifier_labels_unknowns_instead_of_inventing_proof():
    checks = FoundationVerifier(
        {
            "mother_brain_authority": "evidence:brain:identity",
            "governance": "evidence:governance:service",
        }
    ).verify()
    by_name = {check.prerequisite: check for check in checks}

    assert len(checks) == 10
    assert by_name["mother_brain_authority"].status == "verified"
    assert by_name["neural_bus"].status == "unverified"
    assert by_name["hive_blackboard"].status == "unverified"
    assert all(
        check.claim_boundary == "reference-presence-is-not-semantic-proof"
        for check in checks
    )


def test_foundation_verifier_distinguishes_explicit_missing_from_absent():
    checks = FoundationVerifier(
        {
            "canon": None,
            "mother_brain_authority": "  evidence:brain:identity  ",
        }
    ).verify()
    by_name = {check.prerequisite: check for check in checks}

    assert by_name["canon"].status == "missing"
    assert by_name["canon"].evidence_ref is None
    assert by_name["mother_brain_authority"].status == "verified"
    assert by_name["mother_brain_authority"].evidence_ref == (
        "evidence:brain:identity"
    )
    assert by_name["isolation"].status == "unverified"


def test_foundation_check_preserves_durable_id_serialization_contract():
    check = FoundationCheck(
        foundation_id="foundation:canon",
        status="verified",
        evidence_ref="evidence:canon:1",
        claim_boundary="reference-presence-is-not-semantic-proof",
    )

    assert check.prerequisite == "canon"
    assert check.model_dump() == {
        "schema_version": "nexusnet-evolution-v1",
        "foundation_id": "foundation:canon",
        "status": "verified",
        "evidence_ref": "evidence:canon:1",
        "claim_boundary": "reference-presence-is-not-semantic-proof",
    }
    with pytest.raises(ValueError, match="foundation_id must use foundation scheme"):
        FoundationCheck(
            foundation_id="evidence:not-foundation",
            status="unverified",
            claim_boundary="reference-presence-is-not-semantic-proof",
        )


def test_identical_pressure_retry_preserves_event_count_and_last_hash(tmp_path: Path):
    store = EvolutionEventStore(tmp_path)
    pressure_map = GrowthPressureMap(store)
    pressure = GrowthPressure(
        pressure_id="pressure:retry:1",
        target_unit_refs=["unit:runtime:a"],
        source_evidence_refs=["evidence:bench:retry-1"],
        problem_class="latency",
        severity=0.6,
        recurrence=2,
        quality_risk=0.1,
        safety_risk=0.0,
        opportunity_score=0.7,
        expected_value=0.8,
        research_budget_request=0.2,
        affected_workloads=["workload:interactive"],
        status="open",
    )
    pressure_map.record(pressure)
    events_before_retry = store.replay()

    returned = pressure_map.record(pressure)
    events_after_retry = store.replay()

    assert returned == pressure
    assert len(events_before_retry) == len(events_after_retry) == 1
    assert events_after_retry[-1]["event_sha256"] == events_before_retry[-1][
        "event_sha256"
    ]


def test_changed_pressure_appends_once_and_replay_uses_latest_state(tmp_path: Path):
    store = EvolutionEventStore(tmp_path)
    pressure_map = GrowthPressureMap(store)
    pressure = GrowthPressure(
        pressure_id="pressure:lifecycle:1",
        target_unit_refs=["unit:runtime:a"],
        source_evidence_refs=["evidence:bench:lifecycle-1"],
        problem_class="latency",
        severity=0.4,
        recurrence=1,
        quality_risk=0.1,
        safety_risk=0.0,
        opportunity_score=0.6,
        expected_value=0.6,
        research_budget_request=0.2,
        affected_workloads=["workload:interactive"],
        status="open",
    )
    changed = pressure.model_copy(update={"severity": 0.9, "recurrence": 5})

    pressure_map.record(pressure)
    pressure_map.record(changed)

    assert len(store.replay()) == 2
    replayed = GrowthPressureMap(EvolutionEventStore(tmp_path)).ranked(
        workload_priority={"workload:interactive": 1.0},
        system_health_limit=0.5,
    )
    assert len(replayed) == 1
    assert replayed[0]["pressure_id"] == pressure.pressure_id
    assert replayed[0]["severity"] == 0.9
    assert replayed[0]["recurrence"] == 5


def test_pressure_ranking_uses_pressure_id_as_final_tie_break(tmp_path: Path):
    pressure_map = GrowthPressureMap(EvolutionEventStore(tmp_path))
    pressure = GrowthPressure(
        pressure_id="pressure:tie:b",
        target_unit_refs=["unit:runtime:a"],
        source_evidence_refs=["evidence:bench:tie"],
        problem_class="latency",
        severity=0.5,
        recurrence=2,
        quality_risk=0.1,
        safety_risk=0.0,
        opportunity_score=0.5,
        expected_value=0.5,
        research_budget_request=0.2,
        affected_workloads=["workload:interactive"],
        status="open",
    )
    pressure_map.record(pressure)
    pressure_map.record(
        pressure.model_copy(update={"pressure_id": "pressure:tie:a"})
    )

    ranked = pressure_map.ranked(
        workload_priority={"workload:interactive": 1.0},
        system_health_limit=0.5,
    )

    assert [item["pressure_id"] for item in ranked] == [
        "pressure:tie:a",
        "pressure:tie:b",
    ]


def test_pressure_ranking_excludes_non_open_pressures(tmp_path: Path):
    pressure_map = GrowthPressureMap(EvolutionEventStore(tmp_path))
    open_pressure = GrowthPressure(
        pressure_id="pressure:status:open",
        target_unit_refs=["unit:runtime:a"],
        source_evidence_refs=["evidence:bench:status"],
        problem_class="latency",
        severity=0.5,
        recurrence=2,
        quality_risk=0.1,
        safety_risk=0.0,
        opportunity_score=0.5,
        expected_value=0.5,
        research_budget_request=0.2,
        affected_workloads=["workload:interactive"],
        status="open",
    )
    pressure_map.record(open_pressure)
    pressure_map.record(
        open_pressure.model_copy(
            update={"pressure_id": "pressure:status:closed", "status": "closed"}
        )
    )

    ranked = pressure_map.ranked(
        workload_priority={"workload:interactive": 1.0},
        system_health_limit=0.5,
    )

    assert [item["pressure_id"] for item in ranked] == ["pressure:status:open"]
