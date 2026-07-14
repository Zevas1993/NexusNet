from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .evolution_memory import EvolutionMemory
from .schemas import PlanEvidence, RuntimeObservation


class PlanPromotionController:
    def __init__(self, path: str | Path, memory: EvolutionMemory) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.memory = memory
        self._state = self._load()

    @property
    def active_plan_id(self) -> str:
        return str(self._state["active_plan_id"])

    def promote(self, candidate: PlanEvidence, champion: PlanEvidence | None) -> str:
        if candidate.plan.approval_required or not candidate.plan.reversible:
            self._state["history"].append(
                {
                    "event": "approval-required",
                    "plan_id": candidate.plan.plan_id,
                    "evidence_id": candidate.evidence_id,
                    "reason": "native-dependency-remote-or-quality-altering-candidate",
                }
            )
            self._write()
            self.memory.record(feature_key=candidate.plan.feature_key, plan_id=candidate.plan.plan_id, outcome="approval-required", evidence_id=candidate.evidence_id)
            return "approval-required"
        if candidate.status != "completed" or candidate.repeat_count < 3 or not candidate.quality_equivalent or not candidate.stable:
            self.memory.record(feature_key=candidate.plan.feature_key, plan_id=candidate.plan.plan_id, outcome="rejected", evidence_id=candidate.evidence_id)
            return "rejected"
        if champion is not None and not self._improves(candidate, champion):
            self.memory.record(feature_key=candidate.plan.feature_key, plan_id=candidate.plan.plan_id, outcome="rejected", evidence_id=candidate.evidence_id)
            return "rejected"
        previous = self.active_plan_id
        self._state["previous_plan_id"] = previous
        self._state["active_plan_id"] = candidate.plan.plan_id
        self._state["monitor"] = {"baseline_latency_ms": candidate.warm_latency_ms, "feature_key": candidate.plan.feature_key}
        self._state["history"].append({"event": "promoted", "plan_id": candidate.plan.plan_id, "previous_plan_id": previous, "evidence_id": candidate.evidence_id})
        self._write()
        self.memory.record(feature_key=candidate.plan.feature_key, plan_id=candidate.plan.plan_id, outcome="promoted", evidence_id=candidate.evidence_id)
        return "promoted"

    def observe(self, observation: RuntimeObservation) -> str:
        if observation.plan_id != self.active_plan_id:
            return "ignored-non-active"
        baseline = self._state.get("monitor", {}).get("baseline_latency_ms")
        drift = not observation.quality_equivalent or not observation.stable
        if baseline is not None and observation.latency_ms > float(baseline) * 1.5:
            drift = True
        if not drift:
            feature_key = str(self._state.get("monitor", {}).get("feature_key", "unknown"))
            self.memory.record(feature_key=feature_key, plan_id=observation.plan_id, outcome="successful")
            return "healthy"
        return self.rollback("runtime-drift")

    def rollback(self, reason: str) -> str:
        previous = str(self._state.get("previous_plan_id") or "plan::portable-reference")
        failed = self.active_plan_id
        self._state["active_plan_id"] = previous
        self._state["previous_plan_id"] = "plan::portable-reference"
        feature_key = str(self._state.get("monitor", {}).get("feature_key", "unknown"))
        self._state["history"].append({"event": "rolled-back", "plan_id": failed, "restored_plan_id": previous, "reason": reason})
        self._state["monitor"] = {}
        self._write()
        self.memory.record(feature_key=feature_key, plan_id=failed, outcome="rolled-back")
        return "rolled-back"

    def summary(self) -> dict:
        approval_queue = [item for item in self._state["history"] if item.get("event") == "approval-required"]
        return {
            "active_plan_id": self.active_plan_id,
            "previous_plan_id": self._state.get("previous_plan_id"),
            "history": list(self._state["history"]),
            "approval_queue": approval_queue,
        }

    @staticmethod
    def _improves(candidate: PlanEvidence, champion: PlanEvidence) -> bool:
        candidate_latency = candidate.warm_latency_ms or float("inf")
        champion_latency = champion.warm_latency_ms or float("inf")
        return candidate_latency < champion_latency or candidate.peak_ram_bytes < champion.peak_ram_bytes or candidate.peak_vram_bytes < champion.peak_vram_bytes

    def _load(self) -> dict:
        if self.path.exists():
            try:
                payload = json.loads(self.path.read_text(encoding="utf-8"))
                if "active_plan_id" in payload and isinstance(payload.get("history"), list):
                    return payload
            except (OSError, json.JSONDecodeError):
                return self._default_state()
        return self._default_state()

    @staticmethod
    def _default_state() -> dict:
        return {"schema_version": "1.0", "active_plan_id": "plan::portable-reference", "previous_plan_id": None, "monitor": {}, "history": []}

    def _write(self) -> None:
        descriptor, name = tempfile.mkstemp(prefix=self.path.name, suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(self._state, handle, sort_keys=True, separators=(",", ":"))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(name, self.path)
        finally:
            Path(name).unlink(missing_ok=True)
