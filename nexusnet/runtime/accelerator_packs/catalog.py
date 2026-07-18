from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from nexusnet.runtime.hardware_contracts import HardwareCapabilityGraph, HardwareNode

from .contracts import RuntimePackManifest


@dataclass(frozen=True)
class PackCandidate:
    manifest: RuntimePackManifest
    device_node_id: str
    verification_state: Literal["unverified"] = "unverified"
    reason_codes: tuple[str, ...] = ("runtime-pack-unverified",)


def _probe(operation: str, timeout_ms: int) -> dict[str, object]:
    return {"operation": operation, "timeout_ms": timeout_ms}


def _cpu_manifest() -> RuntimePackManifest:
    return RuntimePackManifest.model_validate(
        {
            "pack_id": "org.nexusnet.cpu.reference",
            "version": "1.0.0",
            "pack_type": "python-worker",
            "publisher": "NexusNet",
            "license_id": "MIT",
            "supported_os": ["windows", "linux"],
            "architectures": ["amd64"],
            "workload_kinds": ["native-moe"],
            "model_formats": ["torch"],
            "accelerator_apis": ["cpu"],
            "device_matches": [{"accelerator_apis": ["cpu"]}],
            "launch": {
                "command": ["python", "-m", "nexusnet.runtime.accelerator_packs.workers.reference_worker"],
                "environment_allowlist": ["NEXUSNET_TORCH_BACKEND"],
            },
            "execution_modes": ["cpu"],
            "health_probe": _probe("health", 5_000),
            "self_test_probe": _probe("self_test", 30_000),
            "benchmark_probe": _probe("benchmark", 60_000),
            "artifacts": [],
            "capabilities": ["numeric-model", "deterministic"],
            "known_limitations": ["reference-numeric-model-only"],
        }
    )


def _cuda_manifest() -> RuntimePackManifest:
    return RuntimePackManifest.model_validate(
        {
            "pack_id": "org.nexusnet.torch.cuda",
            "version": "1.0.0",
            "pack_type": "python-worker",
            "publisher": "NexusNet",
            "license_id": "MIT",
            "supported_os": ["windows", "linux"],
            "architectures": ["amd64"],
            "workload_kinds": ["native-moe"],
            "model_formats": ["torch"],
            "accelerator_apis": ["cuda"],
            "device_matches": [{"vendor_ids": ["10de"], "accelerator_apis": ["cuda"]}],
            "launch": {
                "command": ["python", "-m", "nexusnet.runtime.accelerator_packs.workers.torch_worker"],
                "environment_allowlist": ["NEXUSNET_TORCH_BACKEND"],
            },
            "execution_modes": ["gpu"],
            "health_probe": _probe("health", 15_000),
            "self_test_probe": _probe("self_test", 30_000),
            "benchmark_probe": _probe("benchmark", 60_000),
            "artifacts": [],
            "capabilities": ["numeric-model", "cuda-tensor-execution"],
            "known_limitations": ["current-machine-proof-model-only"],
        }
    )


class BuiltInPackCatalog:
    def candidates(self, graph: HardwareCapabilityGraph) -> tuple[PackCandidate, ...]:
        cpu = next((node for node in graph.nodes if node.kind == "cpu"), None)
        candidates: list[PackCandidate] = []
        if cpu is not None:
            candidates.append(PackCandidate(manifest=_cpu_manifest(), device_node_id=cpu.node_id))

        cuda_observed = any(
            item.backend == "cuda" and item.available and item.verification_state == "detected"
            for item in graph.adapters
        )
        if cuda_observed:
            for node in graph.nodes:
                if self._is_cuda_node(node):
                    candidates.append(
                        PackCandidate(
                            manifest=_cuda_manifest(),
                            device_node_id=node.node_id,
                            reason_codes=("cuda-driver-detected", "runtime-pack-unverified"),
                        )
                    )
        return tuple(candidates)

    @staticmethod
    def _is_cuda_node(node: HardwareNode) -> bool:
        return (
            node.kind == "gpu"
            and node.backend == "cuda"
            and "cuda" in node.accelerator_apis
            and node.verification_state == "detected"
        )
