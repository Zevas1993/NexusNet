from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from nexusnet.runtime.hardware_contracts import AcceleratorBackend


class PackType(str, Enum):
    WINDOWS_MANAGED_EP = "windows-managed-ep"
    NATIVE_WORKER = "native-worker"
    PYTHON_WORKER = "python-worker"
    EXTERNAL_CONNECTOR = "external-connector"


class PackLifecycleState(str, Enum):
    AVAILABLE = "available"
    DOWNLOADING = "downloading"
    STAGED = "staged"
    VERIFYING = "verifying"
    ACTIVE = "active"
    DEGRADED = "degraded"
    QUARANTINED = "quarantined"
    ROLLBACK_AVAILABLE = "rollback-available"
    REMOVED = "removed"


class ExecutionMode(str, Enum):
    AUTO = "auto"
    CPU = "cpu"
    GPU = "gpu"
    HYBRID = "hybrid"


class WorkloadKind(str, Enum):
    LLM_GENERATE = "llm-generate"
    EMBEDDING = "embedding"
    RERANK = "rerank"
    VISION = "vision"
    NATIVE_MOE = "native-moe"
    TRAINING = "training"


class ModelFormat(str, Enum):
    GGUF = "gguf"
    ONNX = "onnx"
    ORT = "ort"
    SAFETENSORS = "safetensors"
    TORCH = "torch"


class ArtifactDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    url: str = Field(min_length=1)
    size_bytes: int = Field(gt=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    signature: str | None = None
    signature_kind: str | None = None


class DeviceMatch(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    vendor_ids: list[str] = Field(default_factory=list)
    device_ids: list[str] = Field(default_factory=list)
    architectures: list[str] = Field(default_factory=list)
    accelerator_apis: list[AcceleratorBackend] = Field(default_factory=list)
    minimum_memory_bytes: int | None = Field(default=None, ge=0)


class WorkerLaunchContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    command: list[str] = Field(min_length=1)
    working_directory_ref: str | None = None
    environment_allowlist: list[str] = Field(default_factory=list)


class WorkerProbeContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    operation: Literal["health", "self_test", "benchmark"]
    timeout_ms: int = Field(gt=0, le=300_000)


class RuntimePackManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    pack_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    version: str = Field(min_length=1)
    pack_type: PackType
    publisher: str = Field(min_length=1)
    license_id: str = Field(min_length=1)
    supported_os: list[Literal["windows", "linux"]] = Field(min_length=1)
    architectures: list[str] = Field(min_length=1)
    workload_kinds: list[WorkloadKind] = Field(min_length=1)
    model_formats: list[ModelFormat] = Field(min_length=1)
    accelerator_apis: list[AcceleratorBackend] = Field(min_length=1)
    device_matches: list[DeviceMatch] = Field(default_factory=list)
    minimum_os_build: int | None = Field(default=None, ge=0)
    minimum_driver_version: str | None = None
    python_abi: str | None = None
    dependency_constraints: dict[str, str] = Field(default_factory=dict)
    launch: WorkerLaunchContract
    execution_modes: list[ExecutionMode] = Field(min_length=1)
    health_probe: WorkerProbeContract
    self_test_probe: WorkerProbeContract
    benchmark_probe: WorkerProbeContract
    artifacts: list[ArtifactDescriptor] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    known_limitations: list[str] = Field(default_factory=list)
    rollback_compatible_from: list[str] = Field(default_factory=list)
    data_migration_policy: Literal["none", "backward-compatible", "explicit"] = "none"

    @model_validator(mode="after")
    def validate_execution_capabilities(self) -> "RuntimePackManifest":
        if ExecutionMode.HYBRID in self.execution_modes and "hybrid-offload" not in self.capabilities:
            raise ValueError("hybrid execution requires the hybrid-offload capability")
        return self
