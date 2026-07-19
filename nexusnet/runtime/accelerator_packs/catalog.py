from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Literal

from nexusnet.runtime.hardware_contracts import HardwareCapabilityGraph, HardwareNode

from .contracts import RuntimePackManifest
from .windows_ml import WindowsMlDiscovery, WindowsMlProviderObservation
from .vendor_packs import VendorPackCatalog


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
            "dependency_constraints": {"environment_lock_id": "torch-cuda-2.11.0-cu128-cp311-win-amd64"},
            "launch": {
                "command": ["python", "-m", "nexusnet.runtime.accelerator_packs.workers.torch_worker"],
                "environment_allowlist": ["NEXUSNET_TORCH_BACKEND", "NEXUSNET_TORCH_FAMILY"],
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


def _torch_family_manifest(*, family: str, backend: str, lock_id: str, vendor_id: str | None = None) -> RuntimePackManifest:
    is_cpu = backend == "cpu"
    device_match: dict[str, object] = {"accelerator_apis": [backend]}
    if vendor_id:
        device_match["vendor_ids"] = [vendor_id]
    return RuntimePackManifest.model_validate(
        {
            "pack_id": f"org.nexusnet.torch.{family}",
            "version": "1.0.0",
            "pack_type": "python-worker",
            "publisher": "NexusNet",
            "license_id": "MIT",
            "supported_os": ["windows"],
            "architectures": ["amd64"],
            "workload_kinds": ["native-moe"],
            "model_formats": ["torch"],
            "accelerator_apis": [backend],
            "device_matches": [device_match],
            "dependency_constraints": {"environment_lock_id": lock_id},
            "launch": {
                "command": ["python", "-m", "nexusnet.runtime.accelerator_packs.workers.torch_worker"],
                "environment_allowlist": ["NEXUSNET_TORCH_BACKEND", "NEXUSNET_TORCH_FAMILY"],
            },
            "execution_modes": ["cpu" if is_cpu else "gpu"],
            "health_probe": _probe("health", 15_000),
            "self_test_probe": _probe("self_test", 30_000),
            "benchmark_probe": _probe("benchmark", 60_000),
            "artifacts": [],
            "capabilities": ["numeric-model", "tensor-inference"],
            "known_limitations": ["inference-only-pack"],
        }
    )


def _windows_ml_manifest(provider: WindowsMlProviderObservation) -> RuntimePackManifest:
    is_cpu = provider.backend == "cpu"
    suffix = "cpu" if is_cpu else "directml"
    return RuntimePackManifest.model_validate(
        {
            "pack_id": f"org.nexusnet.windows-ml.{suffix}",
            "version": "1.0.0",
            "pack_type": "python-worker",
            "publisher": "NexusNet",
            "license_id": "MIT",
            "supported_os": ["windows"],
            "architectures": ["amd64"],
            "workload_kinds": ["native-moe"],
            "model_formats": ["onnx"],
            "accelerator_apis": ["cpu" if is_cpu else "directml"],
            "device_matches": [{"accelerator_apis": ["cpu" if is_cpu else "directml"]}],
            "minimum_os_build": 26100,
            "launch": {
                "command": ["python", "-m", "nexusnet.runtime.accelerator_packs.workers.onnx_worker"],
                "environment_allowlist": ["NEXUSNET_MODEL_ROOT", "NEXUSNET_ONNX_PROVIDER"],
            },
            "execution_modes": ["cpu" if is_cpu else "gpu"],
            "health_probe": _probe("health", 15_000),
            "self_test_probe": _probe("self_test", 30_000),
            "benchmark_probe": _probe("benchmark", 60_000),
            "artifacts": [],
            "capabilities": ["onnx-inference", "explicit-provider-selection"],
            "known_limitations": ["provider-correctness-required-before-activation"],
        }
    )


class BuiltInPackCatalog:
    def candidates(
        self,
        graph: HardwareCapabilityGraph,
        *,
        windows_ml: WindowsMlDiscovery | None = None,
        python_abi: str | None = None,
    ) -> tuple[PackCandidate, ...]:
        cpu = next((node for node in graph.nodes if node.kind == "cpu"), None)
        candidates: list[PackCandidate] = []
        if cpu is not None:
            candidates.append(PackCandidate(manifest=_cpu_manifest(), device_node_id=cpu.node_id))
            candidates.append(
                PackCandidate(
                    manifest=_torch_family_manifest(
                        family="cpu",
                        backend="cpu",
                        lock_id="torch-cpu-2.11.0-cp311-win-amd64",
                    ),
                    device_node_id=cpu.node_id,
                    reason_codes=("cpu-device-detected", "runtime-pack-unverified"),
                )
            )

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
        if windows_ml is not None and windows_ml.available:
            known_nodes = {node.node_id for node in graph.nodes}
            for provider in windows_ml.providers:
                if provider.state != "ready" or not provider.certified or provider.device_node_id not in known_nodes:
                    continue
                candidates.append(
                    PackCandidate(
                        manifest=_windows_ml_manifest(provider),
                        device_node_id=provider.device_node_id,
                        reason_codes=(
                            "windows-ml-provider-enumerated",
                            "provider-correctness-unverified",
                            "runtime-pack-unverified",
                        ),
                    )
                )
        for node in graph.nodes:
            if node.kind != "gpu" or node.verification_state != "detected":
                continue
            if node.vendor_id and node.vendor_id.casefold().removeprefix("0x") == "8086" and "xpu" in node.accelerator_apis:
                candidates.append(
                    PackCandidate(
                        manifest=_torch_family_manifest(
                            family="xpu",
                            backend="xpu",
                            lock_id="torch-xpu-2.10.0-cp311-win-amd64",
                            vendor_id="8086",
                        ),
                        device_node_id=node.node_id,
                        reason_codes=("xpu-device-detected", "runtime-pack-unverified"),
                    )
                )
            effective_python_abi = python_abi or f"cp{sys.version_info.major}{sys.version_info.minor}"
            if (
                effective_python_abi == "cp312"
                and node.vendor_id
                and node.vendor_id.casefold().removeprefix("0x") == "1002"
                and node.architecture in {"gfx1201", "gfx1200", "gfx1100", "gfx1101", "gfx1150", "gfx1151"}
                and "hip" in node.accelerator_apis
            ):
                candidates.append(
                    PackCandidate(
                        manifest=_torch_family_manifest(
                            family="rocm-windows",
                            backend="hip",
                            lock_id="torch-rocm-windows-2.9.1-rocm7.2.1-cp312-win-amd64",
                            vendor_id="1002",
                        ),
                        device_node_id=node.node_id,
                        reason_codes=("windows-rocm-tuple-matched", "runtime-pack-unverified"),
                    )
                )
        candidates.extend(VendorPackCatalog().candidates(graph))
        return tuple(candidates)

    @staticmethod
    def _is_cuda_node(node: HardwareNode) -> bool:
        return (
            node.kind == "gpu"
            and node.backend == "cuda"
            and "cuda" in node.accelerator_apis
            and node.verification_state == "detected"
        )
