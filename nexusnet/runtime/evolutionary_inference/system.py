from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

from .benchmark import PlanBenchmark
from .calibration import BoundedHostCalibrator, CalibrationLimits
from .dream_lab import InferenceDreamLab
from .evolution_memory import EvolutionMemory
from .feasibility import ExecutionFitEstimator, ExecutionFitReconciler
from .fingerprints import fingerprint_from_runtime_metadata
from .foundation import EvolutionaryInferenceFoundation
from .hardware import HardwareCapabilityDiscoverer
from .pareto import ParetoController
from .promotion import PlanPromotionController
from .schemas import (
    CapacityGate,
    DreamCycleEvidence,
    ExecutionFitReconciliation,
    ExecutionFitReceipt,
    ExecutionFitRequest,
    ExecutionPlan,
    HardwareCapabilityGraph,
    ModelExecutionFingerprint,
    PlanEvidence,
    RuntimeCapabilityProfile,
    RuntimeModelMetadata,
    RuntimeObservation,
    SLOProfile,
    WorkloadProfile,
)
from .synthesis import ExecutionPlanSynthesizer
from .transfer import HardwareCalibrationLab, TransferExecutor
from nexusnet.runtime.moe_residency.architecture import MoEResidencyTelemetry


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
        self.fit_estimator = ExecutionFitEstimator()
        self.fit_reconciler = ExecutionFitReconciler()
        self._plans: dict[str, ExecutionPlan] = {}
        self._evidence: dict[str, PlanEvidence] = {}
        self._fit_receipts: dict[str, ExecutionFitReceipt] = {}
        self._fit_reconciliations: dict[str, ExecutionFitReconciliation] = {}
        self._evidence_dir = self.artifacts_dir / "runtime" / "evolutionary-inference" / "plan-evidence"
        self._evidence_dir.mkdir(parents=True, exist_ok=True)
        self._load_plan_evidence()
        self._last_workload = WorkloadProfile(prompt_tokens=0, max_new_tokens=64, batch_size=1)
        self._last_slo = SLOProfile()
        self._last_dream: DreamCycleEvidence | None = None
        self._residency_evidence: dict[str, MoEResidencyTelemetry] = {}

    def attach_model(self, metadata: RuntimeModelMetadata | dict[str, Any]) -> ModelExecutionFingerprint:
        self.fingerprint = fingerprint_from_runtime_metadata(metadata)
        self.foundation.establish_baseline(model_fingerprint=self.fingerprint)
        self._plans.clear()
        self._evidence.clear()
        self._fit_receipts.clear()
        self._fit_reconciliations.clear()
        self._residency_evidence.clear()
        return self.fingerprint

    def select_plan(self, workload: WorkloadProfile, slo: SLOProfile) -> ExecutionPlan:
        if self.fingerprint is None:
            return self._portable_reference(workload)
        status = self.foundation.status()
        graph = status["hardware"]
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

    def fit_plan(
        self,
        plan: ExecutionPlan,
        workload: WorkloadProfile,
        runtime_capabilities: RuntimeCapabilityProfile,
        *,
        required_controls: list[str] | None = None,
    ) -> ExecutionFitReceipt:
        if self.fingerprint is None:
            raise ValueError("execution fit requires an attached model fingerprint")
        hardware = HardwareCapabilityGraph.model_validate(self.foundation.status()["hardware"])
        planner_only_parameters = {
            "buffer_depth",
            "chunk_bytes",
            "compute_iterations",
            "pareto_max_regression_ratio",
            "pareto_min_improvement_ratio",
            "prefetch_depth",
        }
        requested_controls = {
            key: value
            for key, value in plan.parameters.items()
            if key not in planner_only_parameters
        }
        normalized_required = sorted({str(control) for control in required_controls or [] if str(control)})
        context_tokens = max(
            1,
            int(
                requested_controls.get(
                    "context_tokens",
                    workload.prompt_tokens + workload.max_new_tokens,
                )
            ),
        )
        max_new_tokens = max(
            1,
            int(requested_controls.get("max_new_tokens", workload.max_new_tokens)),
        )
        runtime_buffer_bytes = max(
            0,
            int(plan.parameters.get("chunk_bytes", 0)) * int(plan.parameters.get("buffer_depth", 1)),
        )
        identity = {
            "plan_id": plan.plan_id,
            "model_fingerprint_id": self.fingerprint.fingerprint_id,
            "hardware_fingerprint": hardware.host_fingerprint,
            "runtime_digest": runtime_capabilities.implementation_digest,
            "workload": workload.model_dump(mode="json"),
            "requested_controls": requested_controls,
            "required_controls": normalized_required,
        }
        request_digest = hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:24]
        receipt = self.fit_estimator.evaluate(
            ExecutionFitRequest(
                request_id=f"fit-request::{request_digest}",
                plan_id=plan.plan_id,
                model_fingerprint=self.fingerprint,
                hardware=hardware,
                runtime_capabilities=runtime_capabilities,
                requested_context_tokens=context_tokens,
                max_new_tokens=max_new_tokens,
                batch_size=workload.batch_size,
                concurrent_requests=workload.concurrent_requests,
                runtime_buffer_bytes=runtime_buffer_bytes,
                requested_controls=requested_controls,
                required_controls=normalized_required,
            )
        )
        self._fit_receipts[runtime_capabilities.runtime_name] = receipt
        return receipt

    def reconcile_fit(
        self,
        observation: RuntimeObservation,
        *,
        runtime_name: str,
    ) -> ExecutionFitReconciliation:
        receipt = self._fit_receipts.get(runtime_name)
        if receipt is None:
            raise ValueError(f"execution fit receipt is unavailable for runtime: {runtime_name}")
        reconciliation = self.fit_reconciler.reconcile(receipt, observation)
        self._fit_reconciliations[runtime_name] = reconciliation
        return reconciliation

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

    def observe(self, observation: RuntimeObservation, *, runtime_name: str | None = None) -> str:
        if runtime_name is not None:
            reconciliation = self.reconcile_fit(observation, runtime_name=runtime_name)
            if reconciliation.status == "rejected":
                return "rejected-fit-observation"
            if reconciliation.status == "rollback-required":
                if observation.plan_id != self.promotion.active_plan_id:
                    return "ignored-non-active"
                return self.promotion.rollback("execution-fit-reconciliation")
        return self.promotion.observe(observation)

    def record_residency_evidence(
        self,
        telemetry: MoEResidencyTelemetry,
        *,
        quality_equivalent: bool,
        stable: bool,
    ) -> PlanEvidence:
        if not quality_equivalent:
            raise ValueError("residency evidence requires confirmed quality equivalence")
        if self.fingerprint is None:
            raise ValueError("residency evidence requires an attached model fingerprint")
        if telemetry.model_fingerprint_id != self.fingerprint.fingerprint_id:
            raise ValueError("residency evidence model fingerprint does not match the attached model")
        plan = self._plans.get(telemetry.execution_plan_id)
        if plan is None:
            raise ValueError("residency evidence requires an existing execution plan")
        checksum = hashlib.sha256(
            json.dumps(telemetry.as_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        evidence = PlanEvidence(
            evidence_id=f"residency-evidence::{checksum[:24]}",
            plan=plan,
            status="completed",
            repeat_count=telemetry.sample_count,
            cold_latency_ms=telemetry.cold_latency_ms,
            warm_latency_ms=telemetry.warm_latency_ms,
            throughput_tokens_s=telemetry.throughput_tokens_s,
            peak_ram_bytes=plan.estimated_peak_ram_bytes,
            peak_vram_bytes=plan.estimated_peak_vram_bytes,
            bytes_moved=telemetry.bytes_read,
            quality_equivalent=True,
            stable=stable,
            uncertainty=0.0 if telemetry.sample_count >= 3 else 1.0,
            measurements_ms=list(telemetry.measurements_ms),
            checksum=checksum,
            reason_codes=list(telemetry.reason_codes),
        )
        self._evidence[plan.plan_id] = evidence
        self._residency_evidence[plan.plan_id] = telemetry
        self._persist_plan_evidence(evidence)
        return evidence

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
            "execution_fit_receipts": {
                runtime_name: receipt.model_dump(mode="json")
                for runtime_name, receipt in sorted(self._fit_receipts.items())
            },
            "execution_fit_reconciliations": {
                runtime_name: reconciliation.model_dump(mode="json")
                for runtime_name, reconciliation in sorted(self._fit_reconciliations.items())
            },
            "residency_evidence": {
                plan_id: telemetry.as_dict()
                for plan_id, telemetry in sorted(self._residency_evidence.items())
            },
            "moe_architecture_intake": {
                "implementation_state": "available",
                "supported_dense_residency_tiers": ["gpu", "ram"],
                "gpu_acceleration_modes": ["off", "on", "auto"],
                "required_controls": [
                    "explicit_architecture_descriptor",
                    "header_only_tier_plan",
                    "cpu_or_gpu_dense_placement",
                    "bounded_expert_cache",
                    "per_inference_gpu_toggle",
                    "exact_profile_gpu_benefit_gate",
                    "sanitized_live_residency_telemetry",
                    "equivalence_gated_evolution_evidence",
                ],
                "policy_mutation_allowed": False,
                "integration_boundary": "architecture-planning-and-evidence-only; model-loading-and-policy-promotion-remain-governed",
            },
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
