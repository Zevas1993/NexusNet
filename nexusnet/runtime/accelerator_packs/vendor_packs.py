from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictStr

from nexusnet.runtime.hardware_contracts import AcceleratorBackend, HardwareCapabilityGraph, HardwareNode

from .contracts import RuntimePackManifest


class VendorSupportRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    family: Literal["amd-radeon-ryzen", "intel-gpu"]
    vendor_id: StrictStr
    backend: AcceleratorBackend
    supported_os: tuple[Literal["windows"], ...] = ("windows",)
    supported_architectures: tuple[StrictStr, ...]
    runtime_version: StrictStr
    python_abi: StrictStr | None = None
    inference_supported: bool = True
    training_supported: bool = False
    source_url: StrictStr


class VendorPackCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    manifest: RuntimePackManifest
    device_node_id: StrictStr
    verification_state: Literal["unverified"] = "unverified"
    reason_codes: tuple[StrictStr, ...]


_SUPPORT_MATRIX = (
    VendorSupportRecord(
        family="amd-radeon-ryzen",
        vendor_id="1002",
        backend="hip",
        supported_architectures=("gfx1201", "gfx1200", "gfx1100", "gfx1101", "gfx1150", "gfx1151"),
        runtime_version="7.2.1",
        python_abi="cp312",
        source_url=(
            "https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibility/"
            "compatibilityrad/windows/windows_compatibility.html"
        ),
    ),
    VendorSupportRecord(
        family="amd-radeon-ryzen",
        vendor_id="1002",
        backend="vulkan",
        supported_architectures=("*",),
        runtime_version="llama.cpp-release",
        source_url="https://github.com/ggml-org/llama.cpp/releases",
    ),
    VendorSupportRecord(
        family="intel-gpu",
        vendor_id="8086",
        backend="sycl",
        supported_architectures=("gen9", "gen11", "gen12", "xe", "xe-lp", "xe-hpg", "xe-hpc", "arc"),
        runtime_version="oneapi-2026.1",
        source_url="https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-toolkit/2026.html",
    ),
    VendorSupportRecord(
        family="intel-gpu",
        vendor_id="8086",
        backend="openvino",
        supported_architectures=("gen9", "gen11", "gen12", "xe", "xe-lp", "xe-hpg", "xe-hpc", "arc"),
        runtime_version="openvino-2026",
        source_url="https://docs.openvino.ai/2026/about-openvino/release-notes-openvino/system-requirements.html",
    ),
)


def _probe(operation: str, timeout_ms: int) -> dict[str, object]:
    return {"operation": operation, "timeout_ms": timeout_ms}


def _manifest(record: VendorSupportRecord) -> RuntimePackManifest:
    suffix = {
        "hip": "amd-hip",
        "vulkan": "amd-vulkan",
        "sycl": "intel-sycl",
        "openvino": "intel-openvino",
    }[record.backend]
    return RuntimePackManifest.model_validate(
        {
            "pack_id": f"org.nexusnet.native.{suffix}",
            "version": "1.0.0",
            "pack_type": "native-worker",
            "publisher": "NexusNet",
            "license_id": "MIT",
            "supported_os": ["windows"],
            "architectures": ["amd64"],
            "workload_kinds": ["llm-generate"],
            "model_formats": ["gguf"],
            "accelerator_apis": [record.backend],
            "device_matches": [
                {
                    "vendor_ids": [record.vendor_id],
                    "architectures": [] if record.supported_architectures == ("*",) else list(record.supported_architectures),
                    "accelerator_apis": [record.backend],
                }
            ],
            "launch": {
                "command": ["python", "-m", "nexusnet.runtime.accelerator_packs.workers.native_worker"],
                "environment_allowlist": [
                    "NEXUSNET_NATIVE_BACKEND",
                    "NEXUSNET_NATIVE_CAPABILITIES",
                    "NEXUSNET_NATIVE_DEVICE_NODE_ID",
                    "NEXUSNET_NATIVE_EXECUTABLE",
                    "NEXUSNET_NATIVE_MODEL_FORMATS",
                    "NEXUSNET_NATIVE_ROOT",
                ],
            },
            "execution_modes": ["gpu"],
            "health_probe": _probe("health", 15_000),
            "self_test_probe": _probe("self_test", 60_000),
            "benchmark_probe": _probe("benchmark", 120_000),
            "artifacts": [],
            "capabilities": ["llm-generate", "bounded-native-connector"],
            "known_limitations": ["representative-hardware-certification-required"],
        }
    )


class VendorPackCatalog:
    @staticmethod
    def support_matrix() -> tuple[VendorSupportRecord, ...]:
        return _SUPPORT_MATRIX

    def candidates(self, graph: HardwareCapabilityGraph) -> tuple[VendorPackCandidate, ...]:
        candidates: list[VendorPackCandidate] = []
        for node in graph.nodes:
            if node.kind != "gpu" or node.verification_state != "detected" or not node.vendor_id:
                continue
            for record in _SUPPORT_MATRIX:
                if not self._matches(record, node):
                    continue
                candidates.append(
                    VendorPackCandidate(
                        manifest=_manifest(record),
                        device_node_id=node.node_id,
                        reason_codes=(
                            f"{record.backend}-capability-detected",
                            "representative-hardware-unverified",
                            "runtime-pack-unverified",
                        ),
                    )
                )
        return tuple(candidates)

    @staticmethod
    def _matches(record: VendorSupportRecord, node: HardwareNode) -> bool:
        if node.vendor_id.casefold().removeprefix("0x") != record.vendor_id:
            return False
        if record.backend not in node.accelerator_apis:
            return False
        architectures = {value.casefold() for value in record.supported_architectures}
        return "*" in architectures or bool(node.architecture and node.architecture.casefold() in architectures)
