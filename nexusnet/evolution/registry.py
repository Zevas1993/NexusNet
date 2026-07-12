from __future__ import annotations

from typing import Any, Callable

from nexusnet.evolution.contracts import EvolvableUnit, GenomeRef
from nexusnet.evolution.store import EvolutionEventStore


LEGACY_UNIT_PREFIX = "unit:self-improvement:"
LEGACY_CLAIM_BOUNDARY = (
    "legacy-lane-coverage-is-not-universal-organism-coverage"
)


class EvolvableUnitRegistry:
    def __init__(self, store: EvolutionEventStore):
        self._store = store
        self._units: dict[str, EvolvableUnit] = {}
        self._genomes: dict[str, GenomeRef] = {}
        self._legacy_aspect_total = 0
        self._legacy_taxonomy_fully_covered = False
        self._replay()

    def _replay(self) -> None:
        for event in self._store.replay():
            if event["event_type"] == "unit.registered":
                self._remember_unit(EvolvableUnit.model_validate(event["payload"]))
            elif event["event_type"] == "genome.registered":
                self._remember_genome(GenomeRef.model_validate(event["payload"]))

        legacy_units = [unit for unit in self._units.values() if self._is_legacy(unit)]
        self._legacy_aspect_total = len(legacy_units)
        self._legacy_taxonomy_fully_covered = bool(legacy_units) and all(
            self._is_covered(unit) for unit in legacy_units
        )

    @staticmethod
    def _remember(
        records: dict[str, Any], identity: str, record: Any
    ) -> bool:
        existing = records.get(identity)
        if existing is None:
            records[identity] = record
            return True
        if existing.model_dump(mode="json") != record.model_dump(mode="json"):
            raise ValueError("conflicting evolution identity")
        return False

    def _remember_unit(self, unit: EvolvableUnit) -> bool:
        return self._remember(self._units, unit.unit_id, unit)

    def _remember_genome(self, genome: GenomeRef) -> bool:
        return self._remember(self._genomes, genome.genome_id, genome)

    def register_unit(self, unit: EvolvableUnit) -> EvolvableUnit:
        if self._remember_unit(unit):
            self._store.append("unit.registered", unit.model_dump(mode="json"))
        return unit

    def register_genome(self, genome: GenomeRef) -> GenomeRef:
        if self._remember_genome(genome):
            self._store.append("genome.registered", genome.model_dump(mode="json"))
        return genome

    def list_units(self) -> list[EvolvableUnit]:
        return [self._units[unit_id] for unit_id in sorted(self._units)]

    def list_genomes(self) -> list[GenomeRef]:
        return [self._genomes[genome_id] for genome_id in sorted(self._genomes)]

    @staticmethod
    def _is_legacy(unit: EvolvableUnit) -> bool:
        return unit.unit_id.startswith(LEGACY_UNIT_PREFIX)

    @staticmethod
    def _is_covered(unit: EvolvableUnit) -> bool:
        return all(
            (
                unit.improvement_strategy_refs,
                unit.eval_suite_refs,
                unit.invariant_refs,
                unit.rollback_refs,
            )
        )

    def coverage(self) -> dict[str, Any]:
        covered_units = [unit for unit in self._units.values() if self._is_covered(unit)]
        uncovered_unit_refs = sorted(
            unit.unit_id
            for unit in self._units.values()
            if not self._is_covered(unit)
        )
        legacy_aspect_covered = sum(
            self._is_legacy(unit) and self._is_covered(unit)
            for unit in self._units.values()
        )
        non_legacy_units = [
            unit for unit in self._units.values() if not self._is_legacy(unit)
        ]
        return {
            "registered_unit_total": len(self._units),
            "covered_unit_total": len(covered_units),
            "uncovered_unit_refs": uncovered_unit_refs,
            "legacy_aspect_total": self._legacy_aspect_total,
            "legacy_aspect_covered": legacy_aspect_covered,
            "legacy_taxonomy_fully_covered": (
                self._legacy_taxonomy_fully_covered
                and legacy_aspect_covered == self._legacy_aspect_total
            ),
            "universal_coverage_complete": bool(non_legacy_units)
            and not uncovered_unit_refs,
            "claim_boundary": LEGACY_CLAIM_BOUNDARY,
        }

    def adapt_self_improvement_engine(self, engine: Any) -> None:
        lanes: dict[str, Callable] = engine.lanes
        legacy_coverage = engine.coverage()
        self._legacy_aspect_total = legacy_coverage["total_aspects"]
        self._legacy_taxonomy_fully_covered = bool(
            legacy_coverage["fully_covered"]
        )
        for aspect in lanes:
            self.register_unit(
                EvolvableUnit(
                    unit_id=f"unit:self-improvement:{aspect}",
                    unit_kind="improvement-service",
                    owner_brain_ref="brain:NexusBrain",
                    capability_refs=[f"capability:self-improvement:{aspect}"],
                    implementation_refs=[
                        f"implementation:self-improvement-lane:{aspect}"
                    ],
                    authority_class="mother-brain-governed",
                    privacy_class="sanitized-metadata",
                    license_state="repository-governed",
                    trust_state="existing-compatibility-lane",
                    eval_suite_refs=["eval:self-improvement-coverage-v1"],
                    invariant_refs=[
                        "policy:north-star-v1",
                        "policy:governed-autonomy-v1",
                    ],
                    checkpoint_refs=[
                        "checkpoint:production-before-self-improvement-v1"
                    ],
                    rollback_refs=[
                        "checkpoint:production-before-self-improvement-v1"
                    ],
                    improvement_strategy_refs=[f"strategy:legacy-lane:{aspect}"],
                    federation_policy="sanitized-evidence-only",
                    lifecycle_state="active",
                )
            )
