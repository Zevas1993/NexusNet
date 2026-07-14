from __future__ import annotations

import hashlib
import json
from typing import Callable

from .benchmark import PlanBenchmark
from .pareto import ParetoController
from .promotion import PlanPromotionController
from .schemas import CapacityGate, DreamCycleEvidence, ExecutionPlan, PlanEvidence, WorkloadProfile


class InferenceDreamLab:
    def __init__(
        self,
        benchmark: PlanBenchmark,
        pareto: ParetoController,
        promotion: PlanPromotionController,
    ) -> None:
        self.benchmark = benchmark
        self.pareto = pareto
        self.promotion = promotion

    def run(
        self,
        gate: CapacityGate,
        champion: PlanEvidence,
        workload: WorkloadProfile,
        cancel_check: Callable[[], bool] | None = None,
        priors: dict[str, float] | None = None,
    ) -> DreamCycleEvidence:
        closed = [
            name
            for name, open_state in (
                ("serving-busy", gate.serving_idle),
                ("thermal-gate-closed", gate.thermal_ok),
                ("memory-gate-closed", gate.memory_ok),
                ("power-gate-closed", gate.power_ok),
                ("budget-exhausted", gate.budget_remaining > 0),
            )
            if not open_state
        ]
        cycle_id = self._cycle_id(gate, champion.plan.plan_id)
        if closed:
            return DreamCycleEvidence(cycle_id=cycle_id, status="gated", trials_completed=0, reason_codes=closed)
        candidates = sorted(
            self._mutations(champion.plan),
            key=lambda plan: (-(priors or {}).get(plan.plan_id, 0.5), plan.plan_id),
        )[: gate.budget_remaining]
        evidence: list[PlanEvidence] = [champion]
        completed: list[str] = []
        for candidate in candidates:
            if cancel_check is not None and cancel_check():
                return DreamCycleEvidence(
                    cycle_id=cycle_id,
                    status="preempted-safe-checkpoint",
                    trials_completed=len(completed),
                    candidate_plan_ids=completed,
                    reason_codes=["serving-preempted"],
                    trial_evidence=evidence[1:],
                )
            trial = self.benchmark.run(candidate, workload, repeat_count=3, cancel_check=cancel_check)
            completed.append(candidate.plan_id)
            evidence.append(trial)
        frontier = self.pareto.frontier(evidence)
        challenger = next((item for item in frontier if item.plan.plan_id != champion.plan.plan_id), None)
        frontier_ids = {item.plan.plan_id for item in frontier}
        for trial in evidence[1:]:
            if trial.plan.plan_id not in frontier_ids:
                self.promotion.memory.record(
                    feature_key=trial.plan.feature_key,
                    plan_id=trial.plan.plan_id,
                    outcome="rejected",
                    evidence_id=trial.evidence_id,
                )
        if challenger is None:
            return DreamCycleEvidence(
                cycle_id=cycle_id,
                status="rejected",
                trials_completed=len(completed),
                candidate_plan_ids=completed,
                reason_codes=["no-nondominated-challenger"],
                trial_evidence=evidence[1:],
            )
        result = self.promotion.promote(challenger, champion)
        return DreamCycleEvidence(
            cycle_id=cycle_id,
            status="promoted" if result == "promoted" else "rejected",
            trials_completed=len(completed),
            candidate_plan_ids=completed,
            promoted_plan_id=challenger.plan.plan_id if result == "promoted" else None,
            reason_codes=[] if result == "promoted" else [result],
            trial_evidence=evidence[1:],
        )

    @staticmethod
    def _mutations(champion: ExecutionPlan) -> list[ExecutionPlan]:
        mutations: list[ExecutionPlan] = []
        base_chunk = int(champion.parameters.get("chunk_bytes", 512 * 1024))
        for chunk, depth in ((max(64 * 1024, base_chunk // 2), 1), (base_chunk, 2), (min(4 * 1024 * 1024, base_chunk * 2), 2)):
            parameters = dict(champion.parameters)
            parameters.update({"chunk_bytes": chunk, "buffer_depth": depth, "compute_iterations": 64})
            primitives = list(champion.primitive_ids)
            primitives = [item for item in primitives if not item.startswith("transfer.")]
            primitives.append("transfer.double-buffered" if depth == 2 else "transfer.pageable")
            digest = hashlib.sha256(json.dumps({"base": champion.plan_id, "p": parameters}, sort_keys=True).encode()).hexdigest()[:20]
            mutations.append(
                champion.model_copy(
                    update={
                        "plan_id": f"plan::dream-{digest}",
                        "primitive_ids": primitives,
                        "parameters": parameters,
                        "fallback_plan_id": champion.plan_id,
                        "estimated_peak_ram_bytes": chunk * depth,
                    }
                )
            )
        return mutations

    @staticmethod
    def _cycle_id(gate: CapacityGate, champion_id: str) -> str:
        payload = json.dumps({"gate": gate.model_dump(mode="json"), "champion": champion_id}, sort_keys=True)
        return f"dream::{hashlib.sha256(payload.encode()).hexdigest()[:24]}"
