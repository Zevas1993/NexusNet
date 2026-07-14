from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
import json
import os
import tempfile

from .benchmark import PlanBenchmark
from .calibration import BoundedHostCalibrator, CalibrationLimits
from .dream_lab import InferenceDreamLab
from .evolution_memory import EvolutionMemory
from .fingerprints import fingerprint_from_runtime_metadata
from .foundation import EvolutionaryInferenceFoundation
from .hardware import HardwareCapabilityDiscoverer
from .pareto import ParetoController
from .promotion import PlanPromotionController
from .schemas import (
    CapacityGate,
    DreamCycleEvidence,
    ExecutionPlan,
    ModelExecutionFingerprint,
    PlanEvidence,
    RuntimeModelMetadata,
    RuntimeObservation,
    SLOProfile,
    WorkloadProfile,
)
from .synthesis import ExecutionPlanSynthesizer
from .transfer import HardwareCalibrationLab, TransferExecutor


class EvolutionaryInferenceSystem:
    def __init__(
        self,
        *,
        artifacts_dir: str | Path,
        discoverer: HardwareCapabilityDiscoverer | None = None,
        calibration_limits: CalibrationLimits | None = None,
    ) -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.transfer = TransferExecutor(storage_dir=self.artifacts_dir / "runtime" / "evolutionary-inference" / "transfer")
        self.hardware_lab = HardwareCalibrationLab(self.transfer)
        self.foundation = EvolutionaryInferenceFoundation(
            artifacts_dir=self.artifacts_dir,
            discoverer=discoverer,
            calibrator=BoundedHostCalibrator(limits=calibration_limits),
            graph_calibrator=self.hardware_lab.calibrate,
        )
        foundation_status = self.foundation.status(ensure_baseline=True)
        stored = foundation_status.get("model_fingerprint")
        self.fingerprint = ModelExecutionFingerprint.model_validate(stored) if stored else None
        self.synthesizer = ExecutionPlanSynthesizer()
        self.benchmark = PlanBenchmark(self.transfer)
        self.pareto = ParetoController()
        self.memory = EvolutionMemory(self.artifacts_dir / "runtime" / "evolutionary-inference" / "memory-v1.json")
        self.promotion = PlanPromotionController(
            self.artifacts_dir / "runtime" / "evolutionary-inference" / "active-policy-v1.json",
            self.memory,
        )
        self.dream_lab = InferenceDreamLab(self.benchmark, self.pareto, self.promotion)
        self._plans: dict[str, ExecutionPlan] = {}
        self._evidence: dict[str, PlanEvidence] = {}
        self._evidence_dir = self.artifacts_dir / "runtime" / "evolutionary-inference" / "plan-evidence"
        self._evidence_dir.mkdir(parents=True, exist_ok=True)
        self._load_plan_evidence()
        self._last_workload = WorkloadProfile(prompt_tokens=0, max_new_tokens=64, batch_size=1)
        self._last_slo = SLOProfile()
        self._last_dream: DreamCycleEvidence | None = None

    def attach_model(self, metadata: RuntimeModelMetadata | dict[str, Any]) -> ModelExecutionFingerprint:
        self.fingerprint = fingerprint_from_runtime_metadata(metadata)
        self.foundation.establish_baseline(model_fingerprint=self.fingerprint)
        self._plans.clear()
        self._evidence.clear()
        return self.fingerprint

    def select_plan(self, workload: WorkloadProfile, slo: SLOProfile) -> ExecutionPlan:
        if self.fingerprint is None:
            return self._portable_reference(workload)
        status = self.foundation.status()
        graph = status["hardware"]
        from .schemas import HardwareCapabilityGraph

        hardware = HardwareCapabilityGraph.model_validate(graph)
        priors = self.memory.priors(self.synthesizer.feature_key(hardware, self.fingerprint, workload))
        plans = self.synthesizer.synthesize(hardware, self.fingerprint, workload, slo, priors)
        self._plans.update({plan.plan_id: plan for plan in plans})
        for plan in plans:
            if plan.plan_id not in self._evidence:
                self._evidence[plan.plan_id] = self.benchmark.run(plan, workload, repeat_count=3)
                self._persist_plan_evidence(self._evidence[plan.plan_id])
        frontier = self.pareto.frontier(list(self._evidence.values()))
        self._last_workload = workload
        self._last_slo = slo
        if not frontier:
            return next(plan for plan in plans if plan.plan_id == "plan::portable-reference")
        selected = self.pareto.select(frontier, slo)
        return selected.plan

    def run_dream_cycle(
        self,
        capacity_gate: CapacityGate,
        cancel_check: Callable[[], bool] | None = None,
    ) -> DreamCycleEvidence:
        if self.fingerprint is None:
            result = DreamCycleEvidence(cycle_id="dream::no-model", status="no-model", trials_completed=0, reason_codes=["model-not-attached"])
            self._last_dream = result
            return result
        champion = self._evidence.get(self.promotion.active_plan_id)
        if champion is None:
            plan = self.select_plan(self._last_workload, self._last_slo)
            champion = self._evidence.get(plan.plan_id)
        if champion is None:
            reference = self._portable_reference(self._last_workload)
            champion = self.benchmark.run(reference, self._last_workload, repeat_count=3)
            self._plans[reference.plan_id] = reference
            self._evidence[reference.plan_id] = champion
        result = self.dream_lab.run(
            capacity_gate,
            champion,
            self._last_workload,
            cancel_check,
            self.memory.priors(champion.plan.feature_key),
        )
        for trial in result.trial_evidence:
            self._plans[trial.plan.plan_id] = trial.plan
            self._evidence[trial.plan.plan_id] = trial
            self._persist_plan_evidence(trial)
        self._last_dream = result
        return result

    def observe(self, observation: RuntimeObservation) -> str:
        return self.promotion.observe(observation)

    def rollback(self, reason: str = "operator-request") -> str:
        return self.promotion.rollback(reason)

    def status(self) -> dict[str, Any]:
        foundation = self.foundation.status()
        frontier = self.pareto.frontier(list(self._evidence.values()))
        hardware = foundation.get("hardware", {})
        measured_links = [
            {
                "source": link.get("source_node_id"),
                "target": link.get("target_node_id"),
                "kind": link.get("kind"),
                "bandwidth_gib_s": link.get("measured_bandwidth_gib_s"),
            }
            for link in hardware.get("links", [])
        ]
        completed = [item for item in self._evidence.values() if item.status == "completed"]
        transfer_evidence = {
            item.plan.plan_id: {
                "evidence_id": item.evidence_id,
                "cold_latency_ms": item.cold_latency_ms,
                "warm_latency_ms": item.warm_latency_ms,
                "bytes_moved": item.bytes_moved,
                "peak_ram_bytes": item.peak_ram_bytes,
                "peak_vram_bytes": item.peak_vram_bytes,
                "quality_equivalent": item.quality_equivalent,
                "stable": item.stable,
            }
            for item in completed
        }
        bottleneck = None
        if measured_links:
            available = [item for item in measured_links if item["bandwidth_gib_s"] is not None]
            if available:
                bottleneck = min(available, key=lambda item: item["bandwidth_gib_s"])
        return {
            "runtime_state": foundation["runtime_state"],
            "host_fingerprint": foundation.get("host_fingerprint"),
            "model_fingerprint_id": self.fingerprint.fingerprint_id if self.fingerprint else None,
            "active_plan": self.promotion.active_plan_id,
            "fallback_plan": "plan::portable-reference",
            "verified_plan_ids": sorted(self._evidence),
            "pareto_frontier": [item.plan.plan_id for item in frontier],
            "uncertainty": {item.plan.plan_id: item.uncertainty for item in frontier},
            "measured_hardware_links": measured_links,
            "bottleneck": bottleneck,
            "plan_evidence": transfer_evidence,
            "promotion": self.promotion.summary(),
            "evolution_memory": self.memory.summary(),
            "last_dream_cycle": self._last_dream.model_dump(mode="json") if self._last_dream else None,
        }

    @staticmethod
    def _portable_reference(workload: WorkloadProfile) -> ExecutionPlan:
        return ExecutionPlan(
            plan_id="plan::portable-reference",
            primitive_ids=["portable.cpu-reference", "transfer.pageable"],
            parameters={"chunk_bytes": 256 * 1024, "buffer_depth": 1, "compute_iterations": 128},
            fallback_plan_id=None,
            estimated_peak_ram_bytes=max(64 * 1024, workload.batch_size * (workload.prompt_tokens + workload.max_new_tokens) * 512),
            estimated_peak_vram_bytes=0,
            feature_key="unattached-portable-reference",
        )

    def _load_plan_evidence(self) -> None:
        for path in self._evidence_dir.glob("*.json"):
            try:
                evidence = PlanEvidence.model_validate_json(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            self._evidence[evidence.plan.plan_id] = evidence
            self._plans[evidence.plan.plan_id] = evidence.plan

    def _persist_plan_evidence(self, evidence: PlanEvidence) -> None:
        safe_name = evidence.plan.plan_id.replace(":", "_").replace("/", "_") + ".json"
        target = self._evidence_dir / safe_name
        descriptor, name = tempfile.mkstemp(prefix=safe_name, suffix=".tmp", dir=self._evidence_dir)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(evidence.model_dump(mode="json"), handle, sort_keys=True, separators=(",", ":"))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(name, target)
        finally:
            Path(name).unlink(missing_ok=True)
