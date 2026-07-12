from __future__ import annotations

import json
from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path
from typing import Any

from nexusnet.evolution.contracts import (
    EvolvableUnit,
    GrowthPressure,
    sanitize_reference,
)
from nexusnet.evolution.foundation import FoundationVerifier
from nexusnet.evolution.pressure import GrowthPressureMap
from nexusnet.evolution.registry import EvolvableUnitRegistry
from nexusnet.evolution.store import EvolutionEventStore


CLAIM_BOUNDARY = (
    "registry-and-evidence-state-only; no candidate, experiment, promotion, "
    "native-model-birth, or frontier-superiority claim"
)
MUTATION_BOUNDARY = "read-only-no-protected-state-mutation"
ENDPOINT_REFS = {
    "everything_state": "/ops/brain/evolution/everything-state",
    "evolvable_units": "/ops/brain/evolution/evolvable-units",
    "growth_pressure": "/ops/brain/evolution/growth-pressure",
    "status": "/ops/brain/evolution/status",
}


def _content_sha256(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


class UniversalEvolutionService:
    def __init__(
        self,
        *,
        artifacts_dir: Path,
        owner_brain_ref: str,
        prerequisite_evidence: Mapping[str, str | None],
        legacy_engine: Any,
    ):
        owner = sanitize_reference(owner_brain_ref)
        if owner != "brain:NexusBrain":
            raise ValueError("owner_brain_ref must be brain:NexusBrain")
        self._owner_brain_ref = owner
        self._store = EvolutionEventStore(artifacts_dir)
        self._registry = EvolvableUnitRegistry(self._store)
        self._pressure_map = GrowthPressureMap(self._store)
        self._foundation_verifier = FoundationVerifier(prerequisite_evidence)
        self._registry.adapt_self_improvement_engine(legacy_engine)

    def register_unit(self, unit: EvolvableUnit) -> EvolvableUnit:
        if unit.owner_brain_ref != self._owner_brain_ref:
            raise ValueError("unit owner must match the NexusBrain service owner")
        return self._registry.register_unit(unit)

    def record_pressure(self, pressure: GrowthPressure) -> GrowthPressure:
        return self._pressure_map.record(pressure)

    def _ranked_pressures(self) -> list[dict[str, Any]]:
        return self._pressure_map.ranked(
            workload_priority={},
            system_health_limit=0.5,
        )

    def everything_state(self) -> dict[str, Any]:
        events = self._store.replay()
        payload = {
            "authority": "NexusBrain",
            "units": [
                unit.model_dump(mode="json") for unit in self._registry.list_units()
            ],
            "genomes": [
                genome.model_dump(mode="json")
                for genome in self._registry.list_genomes()
            ],
            "open_pressures": self._ranked_pressures(),
            "prerequisite_checks": [
                check.model_dump(mode="json")
                for check in self._foundation_verifier.verify()
            ],
            "coverage": self._registry.coverage(),
            "event_count": len(events),
            "last_event_sha256": events[-1]["event_sha256"] if events else None,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        return {**payload, "content_sha256": _content_sha256(payload)}

    def evolvable_units(self) -> dict[str, Any]:
        return {
            "authority": "NexusBrain",
            "items": [
                unit.model_dump(mode="json") for unit in self._registry.list_units()
            ],
            "genomes": [
                genome.model_dump(mode="json")
                for genome in self._registry.list_genomes()
            ],
            "coverage": self._registry.coverage(),
            "claim_boundary": CLAIM_BOUNDARY,
        }

    def growth_pressure(self) -> dict[str, Any]:
        items = self._ranked_pressures()
        return {
            "authority": "NexusBrain",
            "items": items,
            "open_pressure_count": len(items),
            "blocked_pressure_count": sum(
                item["blocked_reason"] is not None for item in items
            ),
            "executable_research_budget_total": round(
                sum(item["executable_research_budget"] for item in items), 6
            ),
            "claim_boundary": CLAIM_BOUNDARY,
        }

    def status(self) -> dict[str, Any]:
        events = self._store.replay()
        coverage = self._registry.coverage()
        pressures = self._ranked_pressures()
        checks = self._foundation_verifier.verify()
        return {
            "authority": "NexusBrain",
            "unit_count": len(self._registry.list_units()),
            "genome_count": len(self._registry.list_genomes()),
            "open_pressure_count": len(pressures),
            "coverage": coverage,
            "top_pressures": pressures[:5],
            "missing_or_unverified_prerequisites": sorted(
                check.prerequisite
                for check in checks
                if check.status in {"missing", "unverified"}
            ),
            "last_event_sha256": (
                events[-1]["event_sha256"] if events else None
            ),
            "endpoint_refs": dict(ENDPOINT_REFS),
            "claim_boundary": CLAIM_BOUNDARY,
            "mutation_boundary": MUTATION_BOUNDARY,
        }
