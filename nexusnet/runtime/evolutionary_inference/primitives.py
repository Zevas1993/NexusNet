from __future__ import annotations

import importlib.util
import hashlib
import inspect

from . import transfer as transfer_module

from .schemas import InferencePrimitive


class InferencePrimitiveRegistry:
    def __init__(self, primitives: list[InferencePrimitive]) -> None:
        self._primitives = {primitive.primitive_id: primitive for primitive in primitives}

    @classmethod
    def default(cls) -> "InferencePrimitiveRegistry":
        moe_path = "nexusnet.runtime.moe_residency"
        moe_available = importlib.util.find_spec(moe_path) is not None
        transfer_digest = hashlib.sha256(inspect.getsource(transfer_module).encode()).hexdigest()
        primitives = [
                InferencePrimitive(
                    primitive_id="portable.cpu-reference",
                    description="Portable CPU and system-memory reference execution fallback.",
                    compatible_model_families=["all"],
                    required_resources=["cpu", "system-ram"],
                    effects=["portable-execution", "baseline-correctness"],
                    implementation_state="available",
                    evidence_state="portable-reference",
                    adapter_path=None,
                    required_capabilities=["portable-compute", "pageable-host-memory"],
                    implementation_digest=transfer_digest,
                    evidence_requirements=["repeated-measurement", "checksum-equivalence"],
                ),
                InferencePrimitive(
                    primitive_id="transfer.pageable",
                    description="Bounded chunked pageable host-memory transfer.",
                    compatible_model_families=["all"],
                    required_resources=["system-ram"],
                    effects=["bounded-host-transfer"],
                    implementation_state="available",
                    evidence_state="existing-implementation",
                    adapter_path="nexusnet.runtime.evolutionary_inference.transfer.TransferExecutor",
                    required_capabilities=["pageable-host-memory"],
                    conflicts=["transfer.accelerator-resident", "transfer.unified-memory"],
                    fallback_primitive_id="portable.cpu-reference",
                    implementation_digest=transfer_digest,
                    reversible_parameters=["chunk_bytes"],
                    evidence_requirements=["repeated-measurement", "checksum-equivalence"],
                ),
                InferencePrimitive(
                    primitive_id="transfer.storage-staging",
                    description="Bounded temporary-file staging with durable write and measured readback.",
                    compatible_model_families=["all"],
                    required_resources=["storage", "system-ram"],
                    effects=["storage-roundtrip"],
                    implementation_state="available",
                    evidence_state="existing-implementation",
                    adapter_path="nexusnet.runtime.evolutionary_inference.transfer.TransferExecutor",
                    required_capabilities=["persistent-artifact-storage"],
                    fallback_primitive_id="transfer.pageable",
                    implementation_digest=transfer_digest,
                    reversible_parameters=["chunk_bytes"],
                    evidence_requirements=["durable-write", "checksum-equivalence"],
                ),
                InferencePrimitive(
                    primitive_id="transfer.double-buffered",
                    description="Measured copy/compute pipelining with bounded buffers.",
                    compatible_model_families=["all"],
                    required_resources=["cpu", "system-ram"],
                    effects=["copy-compute-overlap", "limited-vram-staging"],
                    implementation_state="available",
                    evidence_state="existing-implementation",
                    adapter_path="nexusnet.runtime.evolutionary_inference.transfer.TransferExecutor",
                    required_capabilities=["portable-compute", "pageable-host-memory"],
                    conflicts=["transfer.accelerator-resident", "transfer.unified-memory"],
                    fallback_primitive_id="transfer.pageable",
                    implementation_digest=transfer_digest,
                    reversible_parameters=["chunk_bytes", "buffer_depth", "prefetch_depth"],
                    evidence_requirements=["overlap-measurement", "checksum-equivalence"],
                ),
                InferencePrimitive(
                    primitive_id="transfer.accelerator-resident",
                    description="Pinned asynchronous host/device transfer on a verified CUDA or ROCm backend.",
                    compatible_model_families=["all"],
                    required_resources=["gpu", "system-ram"],
                    effects=["pinned-transfer", "asynchronous-device-copy"],
                    implementation_state="available",
                    evidence_state="unverified",
                    adapter_path="nexusnet.runtime.evolutionary_inference.transfer.TransferExecutor",
                    required_capabilities=["device-memory"],
                    conflicts=["transfer.pageable", "transfer.double-buffered", "transfer.unified-memory"],
                    fallback_primitive_id="transfer.pageable",
                    implementation_digest=transfer_digest,
                    reversible_parameters=["chunk_bytes"],
                    evidence_requirements=["backend-availability", "event-timing", "checksum-equivalence"],
                ),
                InferencePrimitive(
                    primitive_id="transfer.unified-memory",
                    description="Direct bounded execution staging on verified unified-memory hardware.",
                    compatible_model_families=["all"],
                    required_resources=["gpu", "system-ram"],
                    effects=["unified-memory-staging"],
                    implementation_state="available",
                    evidence_state="unverified",
                    adapter_path="nexusnet.runtime.evolutionary_inference.transfer.TransferExecutor",
                    required_capabilities=["unified-memory"],
                    conflicts=["transfer.pageable", "transfer.double-buffered", "transfer.accelerator-resident"],
                    fallback_primitive_id="transfer.pageable",
                    implementation_digest=transfer_digest,
                    reversible_parameters=["chunk_bytes"],
                    evidence_requirements=["hardware-capability", "checksum-equivalence"],
                ),
                InferencePrimitive(
                    primitive_id="moe.selective-residency",
                    description="Existing tiered expert residency and selective MoE execution path.",
                    compatible_model_families=["moe"],
                    required_resources=["cpu", "system-ram", "gpu"],
                    effects=["tiered-expert-residency", "limited-vram-execution", "expert-prefetch"],
                    implementation_state="available" if moe_available else "unavailable",
                    evidence_state="existing-implementation" if moe_available else "unverified",
                    adapter_path=moe_path,
                    required_capabilities=["device-memory"],
                    compatible_operator_families=["moe-router", "expert-ffn"],
                    fallback_primitive_id="portable.cpu-reference",
                    implementation_digest=hashlib.sha256(moe_path.encode()).hexdigest() if moe_available else "",
                    reversible_parameters=["resident_experts", "prefetch_depth"],
                    evidence_requirements=["expert-routing-equivalence", "residency-telemetry"],
                ),
            ]
        return cls(primitives)

    def get(self, primitive_id: str) -> InferencePrimitive:
        return self._primitives[primitive_id]

    def list(self) -> list[InferencePrimitive]:
        return [self._primitives[key] for key in sorted(self._primitives)]

    def list_ids(self) -> list[str]:
        return sorted(self._primitives)

    def validate_composition(self, primitive_ids: list[str]) -> list[str]:
        selected = set(primitive_ids)
        if any(primitive_id not in self._primitives for primitive_id in selected):
            return ["unknown-primitive"]
        if any(self._primitives[primitive_id].implementation_state != "available" for primitive_id in selected):
            return ["unavailable-primitive"]
        if any(
            conflict in selected
            for primitive_id in selected
            for conflict in self._primitives[primitive_id].conflicts
        ):
            return ["primitive-conflict"]
        return []
