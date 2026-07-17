from __future__ import annotations

from collections.abc import Mapping
import re

from pydantic import BaseModel, ConfigDict

from nexusnet.runtime.hardware_contracts import HardwareNode

from .contracts import ExecutionMode, ModelFormat, RuntimePackManifest, WorkloadKind


_VERSION = re.compile(r"^\d+(?:\.\d+)*$")
_CONSTRAINT = re.compile(r"^(==|!=|>=|<=|>|<)?(\d+(?:\.\d+)*)$")
_DEPENDENCY_SEPARATOR = re.compile(r"[-_.]+")
_MAX_VERSION_LENGTH = 128
_MAX_VERSION_COMPONENTS = 16
_MAX_VERSION_COMPONENT_DIGITS = 18
_MAX_CONSTRAINT_LENGTH = 512
_MAX_CONSTRAINT_CLAUSES = 16


def _numeric_version(value: object) -> tuple[int, ...] | None:
    if not isinstance(value, str) or len(value) > _MAX_VERSION_LENGTH or not _VERSION.fullmatch(value):
        return None
    component_text = value.split(".")
    if (
        len(component_text) > _MAX_VERSION_COMPONENTS
        or any(len(part) > _MAX_VERSION_COMPONENT_DIGITS for part in component_text)
    ):
        return None
    try:
        parts = [int(part) for part in component_text]
    except ValueError:
        return None
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def _compare_versions(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    width = max(len(left), len(right))
    normalized_left = left + (0,) * (width - len(left))
    normalized_right = right + (0,) * (width - len(right))
    return (normalized_left > normalized_right) - (normalized_left < normalized_right)


def _satisfies_constraint(version: object, constraint: object) -> bool | None:
    actual = _numeric_version(version)
    if (
        actual is None
        or not isinstance(constraint, str)
        or len(constraint) > _MAX_CONSTRAINT_LENGTH
    ):
        return None
    clauses = constraint.split(",")
    if (
        not clauses
        or len(clauses) > _MAX_CONSTRAINT_CLAUSES
        or any(not clause for clause in clauses)
    ):
        return None
    for clause in clauses:
        match = _CONSTRAINT.fullmatch(clause)
        if match is None:
            return None
        operator, expected_text = match.groups()
        expected = _numeric_version(expected_text)
        if expected is None:
            return None
        comparison = _compare_versions(actual, expected)
        accepted = {
            None: comparison == 0,
            "==": comparison == 0,
            "!=": comparison != 0,
            ">=": comparison >= 0,
            "<=": comparison <= 0,
            ">": comparison > 0,
            "<": comparison < 0,
        }[operator]
        if not accepted:
            return False
    return True


def _dependency_name(value: str) -> str:
    return _DEPENDENCY_SEPARATOR.sub("-", value).casefold()


class CompatibilityDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    compatible: bool
    reason_codes: tuple[str, ...] = ()


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
        host_python_abi: str | None = None,
        dependency_versions: Mapping[str, str] | None = None,
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

        if manifest.minimum_driver_version is not None:
            required_driver = _numeric_version(manifest.minimum_driver_version)
            observed_driver = _numeric_version(device.driver_version)
            if required_driver is None:
                reasons.append("driver-version-constraint-invalid")
            elif observed_driver is None:
                reasons.append("driver-version-unverified")
            elif _compare_versions(observed_driver, required_driver) < 0:
                reasons.append("driver-version-too-old")

        if manifest.python_abi is not None:
            if not isinstance(host_python_abi, str):
                reasons.append("python-abi-unverified")
            elif host_python_abi.casefold() != manifest.python_abi.casefold():
                reasons.append("python-abi-mismatch")

        if manifest.dependency_constraints:
            if dependency_versions is None:
                reasons.append("dependency-constraints-unverified")
            else:
                observed_dependencies = {
                    _dependency_name(name): version
                    for name, version in dependency_versions.items()
                    if isinstance(name, str)
                }
                dependency_unavailable = False
                dependency_unverified = False
                dependency_mismatch = False
                for name, constraint in manifest.dependency_constraints.items():
                    version = observed_dependencies.get(_dependency_name(name))
                    if version is None:
                        dependency_unavailable = True
                        continue
                    satisfies = _satisfies_constraint(version, constraint)
                    if satisfies is None:
                        dependency_unverified = True
                    elif not satisfies:
                        dependency_mismatch = True
                if dependency_unavailable:
                    reasons.append("dependency-unavailable")
                if dependency_unverified:
                    reasons.append("dependency-constraint-unverified")
                if dependency_mismatch:
                    reasons.append("dependency-version-mismatch")

        concrete_modes = set(manifest.execution_modes)
        if device.kind not in {"cpu", "gpu"}:
            reasons.append("device-not-compute-capable")
        if requested_mode == ExecutionMode.CPU and device.kind != "cpu":
            reasons.append("cpu-mode-requires-cpu")
        if requested_mode == ExecutionMode.GPU and device.kind != "gpu":
            reasons.append("gpu-mode-requires-accelerator")
        if requested_mode == ExecutionMode.HYBRID and device.kind != "gpu":
            reasons.append("hybrid-mode-requires-accelerator")
        if requested_mode == ExecutionMode.HYBRID and "hybrid-offload" not in manifest.capabilities:
            reasons.append("hybrid-offload-unavailable")
        if requested_mode != ExecutionMode.AUTO and requested_mode not in concrete_modes:
            reasons.append("execution-mode-mismatch")
        if requested_mode == ExecutionMode.AUTO:
            device_mode = {
                "cpu": ExecutionMode.CPU,
                "gpu": ExecutionMode.GPU,
            }.get(device.kind)
            hybrid_available = device.kind == "gpu" and ExecutionMode.HYBRID in concrete_modes
            if device_mode is None or (device_mode not in concrete_modes and not hybrid_available):
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
