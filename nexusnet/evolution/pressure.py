from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from nexusnet.evolution.contracts import GrowthPressure
from nexusnet.evolution.store import EvolutionEventStore


BLOCKED_REASON = "safety-or-quality-risk-exceeds-system-health-limit"


class GrowthPressureMap:
    def __init__(self, store: EvolutionEventStore):
        self._store = store
        self._pressures: dict[str, GrowthPressure] = {}
        for event in self._store.replay():
            if event["event_type"] == "pressure.recorded":
                pressure = GrowthPressure.model_validate(event["payload"])
                self._pressures[pressure.pressure_id] = pressure

    def record(self, pressure: GrowthPressure) -> GrowthPressure:
        payload = pressure.model_dump(mode="json")
        current = self._pressures.get(pressure.pressure_id)
        if current is not None and current.model_dump(mode="json") == payload:
            return current
        self._store.append("pressure.recorded", payload)
        self._pressures[pressure.pressure_id] = pressure
        return pressure

    def ranked(
        self,
        *,
        workload_priority: Mapping[str, float],
        system_health_limit: float,
    ) -> list[dict[str, Any]]:
        ranked = []
        for pressure in self._pressures.values():
            if pressure.status != "open":
                continue
            recurrence_score = min(1.0, pressure.recurrence / 10.0)
            workload_score = max(
                (
                    workload_priority.get(ref, 0.5)
                    for ref in pressure.affected_workloads
                ),
                default=0.5,
            )
            priority_score = round(
                0.25 * pressure.severity
                + 0.15 * recurrence_score
                + 0.20 * pressure.opportunity_score
                + 0.20 * pressure.expected_value
                + 0.20 * workload_score,
                6,
            )
            blocked = (
                max(pressure.quality_risk, pressure.safety_risk)
                > system_health_limit
            )
            ranked.append(
                {
                    **pressure.model_dump(mode="json"),
                    "priority_score": priority_score,
                    "blocked_reason": BLOCKED_REASON if blocked else None,
                    "executable_research_budget": (
                        0.0 if blocked else pressure.research_budget_request
                    ),
                }
            )
        return sorted(
            ranked,
            key=lambda item: (
                item["blocked_reason"] is not None,
                -item["priority_score"],
                item["pressure_id"],
            ),
        )

    def summary(
        self,
        *,
        workload_priority: Mapping[str, float],
        system_health_limit: float,
    ) -> dict[str, Any]:
        pressures = self.ranked(
            workload_priority=workload_priority,
            system_health_limit=system_health_limit,
        )
        return {
            "open_pressure_count": len(pressures),
            "blocked_pressure_count": sum(
                pressure["blocked_reason"] is not None for pressure in pressures
            ),
            "executable_research_budget_total": round(
                sum(
                    pressure["executable_research_budget"]
                    for pressure in pressures
                ),
                6,
            ),
            "pressures": pressures,
        }
