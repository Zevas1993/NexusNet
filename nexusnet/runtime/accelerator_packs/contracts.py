from __future__ import annotations

from enum import Enum
from pathlib import PurePosixPath, PureWindowsPath
import re
from types import MappingProxyType
from typing import Annotated, Literal, Mapping
from urllib.parse import unquote, urlsplit

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    StrictInt,
    StrictStr,
    field_validator,
    model_validator,
)

from nexusnet.runtime.hardware_contracts import AcceleratorBackend


_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")
_ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _freeze_string_mapping(value: Mapping[str, str]) -> Mapping[str, str]:
    return MappingProxyType(dict(value))


FrozenStringMapping = Annotated[
    Mapping[StrictStr, StrictStr],
    AfterValidator(_freeze_string_mapping),
    PlainSerializer(lambda value: dict(value), return_type=dict),
]


def _validate_safe_text(value: str, *, label: str) -> str:
    if not value or value != value.strip() or _CONTROL_CHARACTERS.search(value):
        raise ValueError(f"{label} must be non-empty and contain no surrounding whitespace or control characters")
    return value


def _validate_package_relative_ref(value: str, *, label: str) -> str:
    _validate_safe_text(value, label=label)
    posix_path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    if ("\\" in value or posix_path.is_absolute() or windows_path.is_absolute() or windows_path.drive
            or any(part in {".", ".."} for part in posix_path.parts) or str(posix_path) != value):
        raise ValueError(f"{label} must be a normalized package-relative reference")
    return value


def _fully_decode_url_path(value: str) -> str:
    decoded = value
    for _ in range(5):
        next_value = unquote(decoded)
        if next_value == decoded:
            return decoded
        decoded = next_value
    raise ValueError("artifact URL path uses excessive nested encoding")


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

    url: StrictStr = Field(min_length=1)
    size_bytes: StrictInt = Field(gt=0)
    sha256: StrictStr = Field(pattern=r"^[0-9a-f]{64}$")
    signature: StrictStr | None = None
    signature_kind: StrictStr | None = None

    @field_validator("url")
    @classmethod
    def validate_artifact_url(cls, value: str) -> str:
        try:
            _validate_safe_text(value, label="artifact URL")
            parsed = urlsplit(value)
            _ = parsed.port
            decoded_path = _fully_decode_url_path(parsed.path)
            decoded_netloc = _fully_decode_url_path(parsed.netloc)
            decoded_query = _fully_decode_url_path(parsed.query)
            _validate_safe_text(decoded_path, label="artifact URL path")
            path_parts = PurePosixPath(decoded_path).parts
            decoded_components = (decoded_netloc, decoded_path, decoded_query)
            if (parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username is not None
                    or parsed.password is not None or parsed.fragment or ".." in path_parts
                    or "\\" in value or any(
                        "\\" in component or _CONTROL_CHARACTERS.search(component)
                        or any(character.isspace() for character in component)
                        for component in decoded_components
                    )):
                raise ValueError("artifact URL must use sanitized HTTPS transport")
        except ValueError as exc:
            raise ValueError("artifact URL must use sanitized HTTPS transport") from exc
        return value


class DeviceMatch(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    vendor_ids: tuple[StrictStr, ...] = ()
    device_ids: tuple[StrictStr, ...] = ()
    architectures: tuple[StrictStr, ...] = ()
    accelerator_apis: tuple[AcceleratorBackend, ...] = ()
    minimum_memory_bytes: StrictInt | None = Field(default=None, ge=0)


class WorkerLaunchContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    command: tuple[StrictStr, ...] = Field(min_length=1)
    working_directory_ref: StrictStr | None = None
    environment_allowlist: tuple[StrictStr, ...] = ()

    @field_validator("command")
    @classmethod
    def validate_command(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        _validate_package_relative_ref(value[0], label="worker executable")
        for argument in value[1:]:
            _validate_safe_text(argument, label="worker argument")
            if ".." in re.split(r"[\\/]", argument):
                raise ValueError("worker arguments must not contain path traversal segments")
        return value

    @field_validator("working_directory_ref")
    @classmethod
    def validate_working_directory_ref(cls, value: str | None) -> str | None:
        if value is not None:
            _validate_package_relative_ref(value, label="worker working directory")
        return value

    @field_validator("environment_allowlist")
    @classmethod
    def validate_environment_allowlist(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized_names = [item.casefold() for item in value]
        if len(value) != len(set(normalized_names)) or any(not _ENVIRONMENT_NAME.fullmatch(item) for item in value):
            raise ValueError("environment allowlist entries must be unique environment variable names")
        return value


class WorkerProbeContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    operation: Literal["health", "self_test", "benchmark"]
    timeout_ms: StrictInt = Field(gt=0, le=300_000)


class RuntimePackManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    pack_id: StrictStr = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    version: StrictStr = Field(min_length=1)
    pack_type: PackType
    publisher: StrictStr = Field(min_length=1)
    license_id: StrictStr = Field(min_length=1)
    supported_os: tuple[Literal["windows", "linux"], ...] = Field(min_length=1)
    architectures: tuple[StrictStr, ...] = Field(min_length=1)
    workload_kinds: tuple[WorkloadKind, ...] = Field(min_length=1)
    model_formats: tuple[ModelFormat, ...] = Field(min_length=1)
    accelerator_apis: tuple[AcceleratorBackend, ...] = Field(min_length=1)
    device_matches: tuple[DeviceMatch, ...] = ()
    minimum_os_build: StrictInt | None = Field(default=None, ge=0)
    minimum_driver_version: StrictStr | None = None
    python_abi: StrictStr | None = None
    dependency_constraints: FrozenStringMapping = Field(default_factory=dict, validate_default=True)
    launch: WorkerLaunchContract
    execution_modes: tuple[ExecutionMode, ...] = Field(min_length=1)
    health_probe: WorkerProbeContract
    self_test_probe: WorkerProbeContract
    benchmark_probe: WorkerProbeContract
    artifacts: tuple[ArtifactDescriptor, ...] = ()
    capabilities: tuple[StrictStr, ...] = ()
    known_limitations: tuple[StrictStr, ...] = ()
    rollback_compatible_from: tuple[StrictStr, ...] = ()
    data_migration_policy: Literal["none", "backward-compatible", "explicit"] = "none"

    @model_validator(mode="after")
    def validate_execution_capabilities(self) -> "RuntimePackManifest":
        if ExecutionMode.HYBRID in self.execution_modes and "hybrid-offload" not in self.capabilities:
            raise ValueError("hybrid execution requires the hybrid-offload capability")
        expected_probes = {
            "health_probe": "health",
            "self_test_probe": "self_test",
            "benchmark_probe": "benchmark",
        }
        for field_name, operation in expected_probes.items():
            if getattr(self, field_name).operation != operation:
                raise ValueError(f"{field_name} probe operation must be {operation}")
        return self
