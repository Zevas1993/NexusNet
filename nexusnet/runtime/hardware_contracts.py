from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


AcceleratorBackend = Literal[
    "portable",
    "cpu",
    "cuda",
    "hip",
    "rocm",
    "xpu",
    "sycl",
    "openvino",
    "vulkan",
    "directml",
    "windows-ml",
    "metal",
]
VerificationState = Literal["detected", "compatible", "verified", "supported", "unavailable", "unverified"]


class HardwareNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    node_id: str
    kind: Literal["cpu", "system-ram", "storage", "gpu"]
    name: str
    backend: AcceleratorBackend = "portable"
    memory_bytes: int | None = Field(default=None, ge=0)
    logical_units: int | None = Field(default=None, ge=1)
    capabilities: list[str] = Field(default_factory=list)
    vendor_id: str | None = None
    device_id: str | None = None
    architecture: str | None = None
    driver_version: str | None = None
    dedicated_memory_bytes: int | None = Field(default=None, ge=0)
    shared_memory_bytes: int | None = Field(default=None, ge=0)
    accelerator_apis: list[AcceleratorBackend] = Field(default_factory=list)
    verification_state: VerificationState = "detected"
    probe_source: str | None = None
    reason_codes: list[str] = Field(default_factory=list)


class HardwareLink(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_node_id: str
    target_node_id: str
    kind: Literal["memory-access", "storage-transfer", "accelerator-transfer"]
    measured_bandwidth_gib_s: float | None = Field(default=None, ge=0)


class AcceleratorAdapterObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    backend: AcceleratorBackend
    available: bool
    reason_code: str
    device_count: int = Field(default=0, ge=0)
    provider_name: str | None = None
    provider_version: str | None = None
    verification_state: VerificationState = "detected"
    probe_source: str | None = None


class CalibrationMetric(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metric_id: str
    value: float = Field(gt=0)
    unit: str
    sample_count: int = Field(gt=0)
    duration_ms: float = Field(gt=0)
    target_node_ids: list[str] = Field(min_length=1)


class HardwareCapabilityGraph(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    host_fingerprint: str
    collected_at: datetime
    nodes: list[HardwareNode]
    links: list[HardwareLink]
    adapters: list[AcceleratorAdapterObservation]
    calibration: list[CalibrationMetric] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_graph_references(self) -> "HardwareCapabilityGraph":
        node_ids = [node.node_id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("node_id values must be unique")
        known = set(node_ids)
        if any(link.source_node_id not in known or link.target_node_id not in known for link in self.links):
            raise ValueError("hardware link references an unknown node")
        return self
