from __future__ import annotations

import hashlib
import json

from .primitives import InferencePrimitiveRegistry
from .schemas import ExecutionPlan, HardwareCapabilityGraph, ModelExecutionFingerprint, SLOProfile, WorkloadProfile


INFERENCE_EVOLUTION_ASSIMILATION_TARGET_IDS = (
    "nanochat-constrained-hardware-reference",
)
"""Source-backed target for bounded plan-scale and quality/throughput tradeoff work.

See docs/assimilation/videos/2026-07-14/11-nanochat-constrained-hardware-reference-spec.md.
"""


class ExecutionPlanSynthesizer:
    def __init__(self, registry: InferencePrimitiveRegistry | None = None) -> None:
        self.registry = registry or InferencePrimitiveRegistry.default()

    def synthesize(
        self,
        graph: HardwareCapabilityGraph,
        fingerprint: ModelExecutionFingerprint,
        workload: WorkloadProfile,
        slo: SLOProfile,
        priors: dict[str, float] | None = None,
    ) -> list[ExecutionPlan]:
        feature_key = self.feature_key(graph, fingerprint, workload)
        runtime_threads = self._runtime_threads(graph)
        reference = ExecutionPlan(
            plan_id="plan::portable-reference",
            primitive_ids=["portable.cpu-reference", "transfer.pageable"],
            parameters={
                "chunk_bytes": self._chunk_size(slo),
                "buffer_depth": 1,
                "compute_iterations": 128,
                "gpu_layers": 0,
                "runtime_batch_tokens": self._runtime_batch_tokens(workload, slo),
                "context_tokens": min(fingerprint.context_length, workload.prompt_tokens + workload.max_new_tokens),
                "max_new_tokens": workload.max_new_tokens,
                "threads": runtime_threads,
            },
            fallback_plan_id=None,
            estimated_peak_ram_bytes=min(fingerprint.tensor_bytes, 256 * 1024 * 1024),
            estimated_peak_vram_bytes=0,
            feature_key=feature_key,
        )
        plans = [reference]
        gpu_nodes = [node for node in graph.nodes if node.kind == "gpu"]
        if not gpu_nodes:
            return plans
        gpu = max(gpu_nodes, key=lambda item: item.memory_bytes or 0)
        memory = gpu.memory_bytes or 0
        unified = "unified-memory" in gpu.capabilities
        if unified:
            plans.append(
                self._plan(
                    ["portable.cpu-reference", "transfer.unified-memory"],
                    {
                        "chunk_bytes": self._chunk_size(slo),
                        "buffer_depth": 1,
                        "compute_iterations": 96,
                        "gpu_layers": fingerprint.layer_count,
                        "runtime_batch_tokens": self._runtime_batch_tokens(workload, slo),
                        "context_tokens": min(fingerprint.context_length, workload.prompt_tokens + workload.max_new_tokens),
                        "max_new_tokens": workload.max_new_tokens,
                        "threads": runtime_threads,
                    },
                    fingerprint,
                    feature_key,
                    peak_vram=min(fingerprint.tensor_bytes, memory),
                )
            )
        elif memory >= fingerprint.tensor_bytes:
            plans.append(
                self._plan(
                    ["portable.cpu-reference", "transfer.accelerator-resident"],
                    {
                        "chunk_bytes": min(self._chunk_size(slo) * 2, 8 * 1024 * 1024),
                        "buffer_depth": 1,
                        "compute_iterations": 64,
                        "gpu_layers": fingerprint.layer_count,
                        "runtime_batch_tokens": self._runtime_batch_tokens(workload, slo),
                        "context_tokens": min(fingerprint.context_length, workload.prompt_tokens + workload.max_new_tokens),
                        "max_new_tokens": workload.max_new_tokens,
                        "threads": runtime_threads,
                    },
                    fingerprint,
                    feature_key,
                    peak_vram=fingerprint.tensor_bytes,
                )
            )
        else:
            primitive_ids = ["portable.cpu-reference", "transfer.double-buffered"]
            if fingerprint.expert_count > 0 and fingerprint.experts_per_token > 0:
                primitive_ids.append("moe.selective-residency")
            plans.append(
                self._plan(
                    primitive_ids,
                    {
                        "chunk_bytes": self._chunk_size(slo),
                        "buffer_depth": 2 if slo.objective != "memory" else 1,
                        "prefetch_depth": 2 if slo.objective == "latency" else 1,
                        "compute_iterations": 64,
                        "gpu_layers": max(1, min(fingerprint.layer_count, int(fingerprint.layer_count * memory / fingerprint.tensor_bytes * 0.85))),
                        "runtime_batch_tokens": self._runtime_batch_tokens(workload, slo),
                        "context_tokens": min(fingerprint.context_length, workload.prompt_tokens + workload.max_new_tokens),
                        "max_new_tokens": workload.max_new_tokens,
                        "threads": runtime_threads,
                    },
                    fingerprint,
                    feature_key,
                    peak_vram=min(memory, max(1, fingerprint.tensor_bytes // max(fingerprint.expert_count, 2))),
                )
            )
        return sorted(
            [plan for plan in plans if not self.registry.validate_composition(plan.primitive_ids)],
            key=lambda plan: plan.plan_id,
        )

    @staticmethod
    def feature_key(
        graph: HardwareCapabilityGraph,
        fingerprint: ModelExecutionFingerprint,
        workload: WorkloadProfile,
    ) -> str:
        gpu_memory = max((node.memory_bytes or 0 for node in graph.nodes if node.kind == "gpu"), default=0)
        payload = {
            "cpu_units": max((node.logical_units or 1 for node in graph.nodes if node.kind == "cpu"), default=1),
            "ram_bucket": max((node.memory_bytes or 0 for node in graph.nodes if node.kind == "system-ram"), default=0) // 1024**3,
            "gpu_bucket": gpu_memory // 1024**3,
            "graph": fingerprint.graph_digest,
            "quantization": fingerprint.quantization,
            "experts": fingerprint.expert_count,
            "batch": workload.batch_size,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:24]

    @staticmethod
    def _chunk_size(slo: SLOProfile) -> int:
        return {"latency": 1024 * 1024, "throughput": 2 * 1024 * 1024, "memory": 256 * 1024, "balanced": 512 * 1024}[slo.objective]

    @staticmethod
    def _runtime_batch_tokens(workload: WorkloadProfile, slo: SLOProfile) -> int:
        base = max(32, min(2048, workload.batch_size * workload.max_new_tokens))
        if slo.objective == "throughput":
            return min(2048, base * 2)
        if slo.objective == "memory":
            return max(32, base // 2)
        return base

    @staticmethod
    def _runtime_threads(graph: HardwareCapabilityGraph) -> int:
        logical_units = max(
            (node.logical_units or 1 for node in graph.nodes if node.kind == "cpu"),
            default=1,
        )
        return max(1, min(64, logical_units // 2 or 1))

    @staticmethod
    def _plan(
        primitives: list[str],
        parameters: dict[str, int | float | str | bool],
        fingerprint: ModelExecutionFingerprint,
        feature_key: str,
        *,
        peak_vram: int,
    ) -> ExecutionPlan:
        canonical = json.dumps({"primitives": primitives, "parameters": parameters, "feature": feature_key}, sort_keys=True)
        digest = hashlib.sha256(canonical.encode()).hexdigest()[:20]
        return ExecutionPlan(
            plan_id=f"plan::{digest}",
            primitive_ids=primitives,
            parameters=parameters,
            fallback_plan_id="plan::portable-reference",
            estimated_peak_ram_bytes=min(fingerprint.tensor_bytes, 256 * 1024 * 1024),
            estimated_peak_vram_bytes=peak_vram,
            feature_key=feature_key,
        )
