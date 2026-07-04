from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow
from pydantic import ValidationError

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
            created_at=utcnow().isoformat(),
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        simulations = self._list_simulations()
        return {
            "surface_id": "dreaming-simulator",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(simulation.get("status") == "blocked" for simulation in simulations)
            else ("live-bound" if simulations else "static-canon"),
            "simulation_count": len(simulations),
            "latest_simulation": simulations[0] if simulations else None,
            "world_model_boundary": "deterministic-shadow-simulation-no-learned-world-model-claim",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        if self.simulations_dir is None:
            self._simulations.insert(0, record)
            return
        path = self._artifact_path_for_simulation_id(record["simulation_id"])
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, allow_nan=False, indent=2, sort_keys=True), encoding="utf-8")
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

    def _list_simulations(self) -> list[dict[str, Any]]:
        records_by_id: dict[str, dict[str, Any]] = {}
        if self.simulations_dir is not None:
            disk_records: dict[str, tuple[str, str, dict[str, Any]]] = {}
            for path in sorted(self.simulations_dir.glob("*.json"), key=lambda item: item.name):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    if not isinstance(payload, dict):
                        continue
                    record = SimulationRecord(**payload).model_dump(mode="json")
                except (OSError, json.JSONDecodeError, ValidationError):
                    continue
                simulation_id = record.get("simulation_id")
                candidate_key = (record.get("created_at") or "", path.name)
                if simulation_id not in disk_records or candidate_key > disk_records[simulation_id][:2]:
                    disk_records[simulation_id] = (*candidate_key, record)
            for simulation_id, (_, _, record) in disk_records.items():
                records_by_id[simulation_id] = record
        for record in reversed(self._simulations):
            simulation_id = record.get("simulation_id")
            if simulation_id:
                records_by_id[simulation_id] = record
        records = list(records_by_id.values())
        records.sort(key=lambda item: (item.get("created_at") or "", item.get("simulation_id") or ""), reverse=True)
        return records
