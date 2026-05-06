from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .contracts import SimulationRecord


class DreamingSimulator:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.simulations_dir = self.artifacts_dir / "developmental" / "simulations" if self.artifacts_dir else None
        if self.simulations_dir is not None:
            self.simulations_dir.mkdir(parents=True, exist_ok=True)
        self._simulations: list[dict[str, Any]] = []

    def record_simulation(
        self,
        *,
        simulation_id: str,
        seed_trace_ref: str,
        scenario: dict[str, object],
        expected_outcomes: list[str],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = []
        if not evidence_refs:
            findings.append("simulation_requires_evidence_refs")
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
            "runtime_state": "degraded"
            if any(simulation.get("status") == "blocked" for simulation in self._simulations)
            else ("live-bound" if self._simulations else "static-canon"),
            "simulation_count": len(self._simulations),
            "latest_simulation": self._simulations[0] if self._simulations else None,
            "world_model_boundary": "deterministic-shadow-simulation-no-learned-world-model-claim",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        if self.simulations_dir is None:
            self._simulations.insert(0, record)
            return
        path = self._artifact_path_for_simulation_id(record["simulation_id"])
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        self._simulations.insert(0, record)

    def _artifact_path_for_simulation_id(self, simulation_id: str) -> Path:
        if self.simulations_dir is None:
            raise ValueError("simulations_dir is required for persisted simulations")
        digest = hashlib.sha256(simulation_id.encode("utf-8")).hexdigest()
        path = self.simulations_dir / f"{digest}.json"
        simulations_root = self.simulations_dir.resolve()
        resolved_path = path.resolve()
        if resolved_path.parent != simulations_root:
            raise ValueError("simulation artifact path escaped simulations directory")
        return path
