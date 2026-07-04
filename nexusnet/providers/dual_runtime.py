"""Dual-runtime co-execution: CPU (LM Studio) + GPU (vLLM) models run simultaneously THROUGH NexusNet.

Canon C39: "LM Studio = CPU-only models, vLLM = GPU models, running simultaneously and communicating
THROUGH NexusNet (deeper data gathering)." This coordinator calls a local/CPU provider and a GPU/cloud
provider in parallel, merges their outputs by policy, and yields BOTH so the continuous-assimilation
loop can learn from each. Genuine parallel calls (thread pool); deterministic with offline providers.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .model_providers import ProviderRegistry, Message

_MERGE_POLICIES = ("prefer_gpu", "prefer_local", "longest", "both")


class DualRuntimeCoordinator:
    """Run two providers (e.g. CPU+GPU) concurrently through NexusNet and merge their outputs."""

    def __init__(self, registry: ProviderRegistry, *, cpu_provider: str, gpu_provider: str,
                 merge: str = "prefer_gpu") -> None:
        if merge not in _MERGE_POLICIES:
            raise ValueError(f"unknown merge policy {merge!r}; allowed {_MERGE_POLICIES}")
        self.registry = registry
        self.cpu_provider = cpu_provider
        self.gpu_provider = gpu_provider
        self.merge = merge

    def co_execute(self, messages: list[Message]) -> dict[str, Any]:
        """Call both runtimes simultaneously; return merged output + both raw results + contributors."""
        with ThreadPoolExecutor(max_workers=2) as pool:
            f_cpu = pool.submit(self.registry.complete, self.cpu_provider, messages)
            f_gpu = pool.submit(self.registry.complete, self.gpu_provider, messages)
            cpu, gpu = f_cpu.result(), f_gpu.result()
        merged_text, source, contributors = self._merge(cpu, gpu)
        return {
            "merged_text": merged_text,
            "merged_from": source,
            "contributors": contributors,        # both feed assimilation as distinct source models
            "cpu": cpu,
            "gpu": gpu,
            "ran_simultaneously": True,
            "through_nexusnet": True,
        }

    def _merge(self, cpu: dict, gpu: dict) -> tuple[str, str, list[str]]:
        ok = [r for r in (cpu, gpu) if r.get("ok")]
        contributors = [r["provider_id"] for r in ok if r.get("provider_id")]
        if not ok:
            return "", "none", contributors
        if self.merge == "both":
            return ("\n---\n".join(r["text"] for r in ok), "both", contributors)
        if self.merge == "longest":
            best = max(ok, key=lambda r: len(r.get("text", "")))
            return best["text"], best.get("provider_id", "?"), contributors
        primary = gpu if self.merge == "prefer_gpu" else cpu
        fallback = cpu if self.merge == "prefer_gpu" else gpu
        chosen = primary if primary.get("ok") else fallback
        return chosen.get("text", ""), chosen.get("provider_id", "?"), contributors
