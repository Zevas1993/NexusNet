from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import SimulationRecord


class DreamingSimulator:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "developmental" / "simulations" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def record_simulation(
        self,
        *,
        simulation_id: str,
        seed_trace_ref: str,
        scenario: dict[str, object],
        expected_outcomes: list[str],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = [] if evidence_refs else ["simulation_requires_evidence_refs"]
        record = SimulationRecord(
            simulation_id=simulation_id,
            seed_trace_ref=seed_trace_ref,
            scenario=scenario,
            expected_outcomes=expected_outcomes,
            evidence_refs=evidence_refs,
            status="blocked" if findings else "shadow-recorded",
            findings=findings,
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "dreaming-simulator",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(item.get("status") == "blocked" for item in self._records) else ("live-bound" if self._records else "static-canon"),
            "simulation_count": len(self._records),
            "latest_simulation": self._records[0] if self._records else None,
            "world_model_boundary": "deterministic-shadow-simulation-no-learned-world-model-claim",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._records.insert(0, record)
        if self.root is None:
            return
        path = self.root / f"{_safe_id(record['simulation_id'])}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")


def _safe_id(value: str) -> str:
    return value.replace(":", "_").replace("/", "_")[:160] or "simulation"
