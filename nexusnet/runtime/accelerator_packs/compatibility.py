from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from nexusnet.runtime.hardware_contracts import HardwareNode

from .contracts import ExecutionMode, ModelFormat, RuntimePackManifest, WorkloadKind


class CompatibilityDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    compatible: bool
    reason_codes: list[str] = Field(default_factory=list)


class PackCompatibilityEvaluator:
    def evaluate(
        self,
        *,
        manifest: RuntimePackManifest,
        device: HardwareNode,
        host_os: str,
        architecture: str,
        os_build: int | None,
        workload: WorkloadKind,
        model_format: ModelFormat,
        requested_mode: ExecutionMode,
    ) -> CompatibilityDecision:
        reasons: list[str] = []
        if host_os.lower() not in manifest.supported_os:
            reasons.append("os-mismatch")
        if architecture.lower() not in {item.lower() for item in manifest.architectures}:
            reasons.append("architecture-mismatch")
        if manifest.minimum_os_build is not None and (os_build is None or os_build < manifest.minimum_os_build):
            reasons.append("os-build-too-old")
        if workload not in manifest.workload_kinds:
            reasons.append("workload-mismatch")
        if model_format not in manifest.model_formats:
            reasons.append("model-format-mismatch")

        concrete_modes = set(manifest.execution_modes)
        if requested_mode == ExecutionMode.CPU and device.kind != "cpu":
            reasons.append("cpu-mode-requires-cpu")
        if requested_mode == ExecutionMode.GPU and device.kind != "gpu":
            reasons.append("gpu-mode-requires-accelerator")
        if requested_mode == ExecutionMode.HYBRID and "hybrid-offload" not in manifest.capabilities:
            reasons.append("hybrid-offload-unavailable")
        if requested_mode != ExecutionMode.AUTO and requested_mode not in concrete_modes:
            reasons.append("execution-mode-mismatch")
        if requested_mode == ExecutionMode.AUTO:
            device_mode = ExecutionMode.CPU if device.kind == "cpu" else ExecutionMode.GPU
            if device_mode not in concrete_modes and ExecutionMode.HYBRID not in concrete_modes:
                reasons.append("auto-has-no-concrete-mode")

        device_apis = set(device.accelerator_apis or [device.backend])
        if not device_apis.intersection(manifest.accelerator_apis):
            reasons.append("device-api-mismatch")
        if manifest.device_matches and not any(self._matches(rule, device, device_apis) for rule in manifest.device_matches):
            reasons.append("device-predicate-mismatch")

        return CompatibilityDecision(
            compatible=not reasons,
            reason_codes=reasons or ["manifest-compatible"],
        )

    @staticmethod
    def _matches(rule, device: HardwareNode, device_apis: set[str]) -> bool:
        if rule.vendor_ids and (device.vendor_id or "").lower() not in {item.lower() for item in rule.vendor_ids}:
            return False
        if rule.device_ids and (device.device_id or "").lower() not in {item.lower() for item in rule.device_ids}:
            return False
        if rule.architectures and (device.architecture or "").lower() not in {
            item.lower() for item in rule.architectures
        }:
            return False
        if rule.accelerator_apis and not device_apis.intersection(rule.accelerator_apis):
            return False
        memory = device.dedicated_memory_bytes if device.kind == "gpu" else device.memory_bytes
        if rule.minimum_memory_bytes is not None and (memory is None or memory < rule.minimum_memory_bytes):
            return False
        return True
