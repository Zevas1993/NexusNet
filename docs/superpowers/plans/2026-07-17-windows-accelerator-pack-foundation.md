# Windows Accelerator Pack Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the vendor-neutral accelerator-pack foundation: normalized multi-vendor device contracts, strict pack manifests, compatibility evaluation, restart-safe lifecycle state, a bounded JSON-lines worker protocol, process supervision, and an unregistered worker-backed `RuntimeAdapter`.

**Architecture:** Extract the existing evolutionary-inference hardware graph into one dependency-free shared module and re-export the same classes from the current schema path, avoiding both model duplication and the evolutionary package's eager Torch import. Add a focused `nexusnet.runtime.accelerator_packs` package for pack policy and worker mechanics, then add a `nexus.runtimes.worker` adapter that preserves the existing synchronous runtime contract without registering it in live selection. Vendor libraries stay outside core, and every production behavior is proven through injected or fixture workers.

**Tech Stack:** Python 3.10+, Pydantic v2, standard-library JSON/path/threading/queue/subprocess APIs, pytest, GitNexus.

## Global Constraints

- Initial platform is Windows 11 x64 desktop; Linux, mobile, edge, ARM64, and NPU deployment remain separate Canon phases.
- NexusNet core must not import Torch CUDA, Torch XPU, ROCm, OpenVINO, DirectML, Windows ML, ONNX Runtime, or vendor DLLs.
- Managed native and Python packs execute out of process; this plan installs no vendor packages and changes no global Python or Torch environment.
- Preserve the exact public semantics: `Auto` selects among verified routes, `CPU` forces CPU, `GPU` forces an accelerator, and `Both` maps internally to `hybrid` only when declared and proven.
- `detected`, `compatible`, `verified`, and `supported` are distinct evidence levels. This foundation may establish only detection and manifest compatibility.
- No lifecycle or protocol error may include raw prompts, model outputs, secrets, environment variables, absolute private paths, or unbounded worker output.
- The pack foundation must not change `RuntimeRegistry.adapters`, `RuntimeRegistry.choose`, QES selection, Inference Economy routing, provider selection, model weights, or training behavior.
- Work in an isolated worktree created at execution time through `superpowers:using-git-worktrees`; preserve every unrelated dirty file in the integration checkout.
- Use test-driven development: add one focused red test, run it and record the expected failure, add the minimum production behavior, and rerun green.
- Before editing any existing class, method, or function, run upstream GitNexus impact analysis. `HardwareNode`, `AcceleratorAdapterObservation`, and `HardwareCapabilityGraph` have a HIGH depth-three transitive blast radius (142 dependents) and require an explicit warning and broad regression proof before proceeding.
- Before every commit, stage only the task's named files, run `git diff --cached --check`, and run `gitnexus_detect_changes` with `scope: "staged"`.

## Delivery-Series Boundary

This plan is the first independently testable sub-project. The approved design is partitioned into these subsequent plan boundaries:

1. This plan: contracts, compatibility, registry, worker protocol, supervisor, and inactive adapter.
2. Windows discovery and private-runtime installer foundation.
3. Verified CPU plus current NVIDIA vertical slice with `CPU`, `GPU`, `Both`, and `Auto` controls.
4. Windows ML ONNX execution-provider integration and DirectML/CPU fallback.
5. AMD HIP/Vulkan and Intel XPU/SYCL/OpenVINO packs with real-device gates.
6. QES calibration-driven live selection, update/rollback hardening, repair/uninstall, and the full Windows certification matrix.

No task in this plan may pull work forward from boundaries 2-6.

## File Responsibility Map

- `nexusnet/runtime/hardware_contracts.py`: single dependency-free normalized hardware-graph contract used by evolutionary inference and future pack matching.
- `nexusnet/runtime/evolutionary_inference/schemas.py`: compatibility re-export of the shared hardware classes plus the existing evolutionary-inference-only schemas.
- `nexusnet/runtime/accelerator_packs/contracts.py`: strict runtime-pack, artifact, launch, probe, execution-mode, and lifecycle contracts.
- `nexusnet/runtime/accelerator_packs/compatibility.py`: pure vendor-neutral manifest-to-device eligibility checks; no installation or selection.
- `nexusnet/runtime/accelerator_packs/registry.py`: atomic local lifecycle state and active/previous version pointers; no worker execution.
- `nexusnet/runtime/accelerator_packs/protocol.py`: bounded JSON-lines request/frame schemas and sanitized parse failures.
- `nexusnet/runtime/accelerator_packs/supervisor.py`: one-worker subprocess lifecycle, timeouts, frame correlation, and termination.
- `nexus/runtimes/worker.py`: inactive adapter translating the existing `RuntimeAdapter` interface into worker exchanges.
- `tests/runtime/accelerator_packs/`: one test module per responsibility.
- `tests/fixtures/accelerator_pack_worker.py`: dependency-free deterministic worker used only by supervisor and adapter tests.

---

### Task 1: Extend the existing hardware graph for multi-vendor devices

**Files:**

- Modify: `nexusnet/runtime/evolutionary_inference/schemas.py:6-58`
- Create: `nexusnet/runtime/hardware_contracts.py`
- Create: `tests/runtime/accelerator_packs/test_device_schema.py`

**Interfaces:**

- Consumes: Existing `HardwareNode`, `AcceleratorAdapterObservation`, `HardwareLink`, and `HardwareCapabilityGraph` construction sites.
- Produces: one dependency-free `AcceleratorBackend`, `VerificationState`, normalized device graph, and compatibility re-exports for Task 3 and existing evolutionary inference.

- [ ] **Step 1: Reconfirm and report the blast radius before the existing schema edit**

Run through GitNexus MCP:

```json
{"repo":"NexusNet","target":"HardwareNode","file_path":"nexusnet/runtime/evolutionary_inference/schemas.py","kind":"Class","direction":"upstream","maxDepth":3,"minConfidence":0.8,"includeTests":true}
```

Expected: HIGH risk at depth three. Report the direct dependents and stop for user direction if the result is broader than the recorded 142 transitive dependents or names new critical execution flows.

- [ ] **Step 2: Write the failing device-contract test**

Create `tests/runtime/accelerator_packs/test_device_schema.py`:

```python
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from nexusnet.runtime.evolutionary_inference.schemas import (
    AcceleratorAdapterObservation,
    HardwareCapabilityGraph,
    HardwareLink,
    HardwareNode,
)
from nexusnet.runtime.hardware_contracts import HardwareCapabilityGraph as SharedHardwareCapabilityGraph
from nexusnet.runtime.hardware_contracts import HardwareNode as SharedHardwareNode


def test_hardware_graph_represents_mixed_vendor_windows_devices_without_claiming_support():
    graph = HardwareCapabilityGraph(
        host_fingerprint="a" * 32,
        collected_at=datetime.now(timezone.utc),
        nodes=[
            HardwareNode(
                node_id="cpu:0",
                kind="cpu",
                name="Windows CPU",
                backend="cpu",
                accelerator_apis=["cpu"],
                verification_state="detected",
                probe_source="windows-cim",
            ),
            HardwareNode(
                node_id="gpu:pci:0001",
                kind="gpu",
                name="Discrete GPU",
                backend="cuda",
                vendor_id="10de",
                device_id="2c05",
                driver_version="test-driver",
                dedicated_memory_bytes=16 * 1024**3,
                shared_memory_bytes=32 * 1024**3,
                accelerator_apis=["cuda", "vulkan", "directml", "windows-ml"],
                verification_state="detected",
                probe_source="dxgi",
            ),
            HardwareNode(
                node_id="gpu:pci:0002",
                kind="gpu",
                name="Integrated GPU",
                backend="xpu",
                vendor_id="8086",
                accelerator_apis=["xpu", "sycl", "openvino", "directml", "windows-ml"],
                verification_state="unverified",
                probe_source="dxgi",
                reason_codes=["pack-evidence-missing"],
            ),
        ],
        links=[
            HardwareLink(source_node_id="cpu:0", target_node_id="gpu:pci:0001", kind="accelerator-transfer"),
            HardwareLink(source_node_id="cpu:0", target_node_id="gpu:pci:0002", kind="accelerator-transfer"),
        ],
        adapters=[
            AcceleratorAdapterObservation(
                backend="windows-ml",
                available=True,
                reason_code="provider-enumeration-available",
                device_count=2,
                verification_state="detected",
                probe_source="windows-ml",
            )
        ],
    )

    assert [node.node_id for node in graph.nodes if node.kind == "gpu"] == ["gpu:pci:0001", "gpu:pci:0002"]
    assert graph.nodes[1].vendor_id == "10de"
    assert graph.nodes[2].verification_state == "unverified"
    assert all(node.verification_state != "supported" for node in graph.nodes)
    assert HardwareNode is SharedHardwareNode
    assert HardwareCapabilityGraph is SharedHardwareCapabilityGraph


def test_hardware_graph_rejects_duplicate_or_dangling_device_references():
    common = dict(node_id="cpu:0", kind="cpu", name="CPU", backend="cpu", accelerator_apis=["cpu"])
    with pytest.raises(ValidationError, match="node_id values must be unique"):
        HardwareCapabilityGraph(
            host_fingerprint="b" * 32,
            collected_at=datetime.now(timezone.utc),
            nodes=[HardwareNode(**common), HardwareNode(**common)],
            links=[],
            adapters=[],
        )

    with pytest.raises(ValidationError, match="unknown node"):
        HardwareCapabilityGraph(
            host_fingerprint="c" * 32,
            collected_at=datetime.now(timezone.utc),
            nodes=[HardwareNode(**common)],
            links=[HardwareLink(source_node_id="cpu:0", target_node_id="gpu:missing", kind="accelerator-transfer")],
            adapters=[],
        )
```

- [ ] **Step 3: Run the new test and verify the expected red state**

Run: `python -m pytest tests/runtime/accelerator_packs/test_device_schema.py -q`

Expected: FAIL because the existing backend literals reject `cpu`, `xpu`, and `windows-ml`, and the new normalized fields do not exist.

- [ ] **Step 4: Replace the hardware contract declarations with the normalized additive contract**

Create `nexusnet/runtime/hardware_contracts.py` with the complete shared contract below:

```python
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
```

Do not remove `memory_bytes`, `logical_units`, `capabilities`, or the existing backend spellings; existing construction sites must remain valid.

Then remove the old contiguous declaration block from `HardwareNode` through `HardwareCapabilityGraph` in `nexusnet/runtime/evolutionary_inference/schemas.py` and add this import after the existing Pydantic import:

```python
from nexusnet.runtime.hardware_contracts import (
    AcceleratorAdapterObservation,
    AcceleratorBackend,
    CalibrationMetric,
    HardwareCapabilityGraph,
    HardwareLink,
    HardwareNode,
    VerificationState,
)
```

Keep every schema beginning with `TensorGroupMetadata` unchanged. Do not add eager exports to `nexusnet/runtime/__init__.py`.

- [ ] **Step 5: Run focused and blast-radius regression tests**

Run:

```powershell
python -m pytest tests/runtime/accelerator_packs/test_device_schema.py tests/runtime/test_evolutionary_inference_foundation.py tests/runtime/test_evolutionary_inference_system.py -q
python -m pytest -q
```

Expected: both commands exit 0 with no failures. If the broad suite has an existing unrelated failure, record the exact baseline comparison and stop before Task 2 until the result is reviewed.

- [ ] **Step 6: Scope-check and commit Task 1**

Run:

```powershell
git add nexusnet/runtime/hardware_contracts.py nexusnet/runtime/evolutionary_inference/schemas.py tests/runtime/accelerator_packs/test_device_schema.py
git diff --cached --check
```

Run `gitnexus_detect_changes` with `{"repo":"NexusNet","scope":"staged"}` and verify only the hardware schema and its expected evolutionary-inference dependents appear. Then commit:

```powershell
git commit -m "feat: normalize accelerator device contracts"
```

---

### Task 2: Define strict runtime-pack manifests and lifecycle vocabulary

**Files:**

- Create: `nexusnet/runtime/accelerator_packs/__init__.py`
- Create: `nexusnet/runtime/accelerator_packs/contracts.py`
- Create: `tests/runtime/accelerator_packs/conftest.py`
- Create: `tests/runtime/accelerator_packs/test_pack_contracts.py`

**Interfaces:**

- Consumes: `AcceleratorBackend` from Task 1.
- Produces: `RuntimePackManifest`, `ExecutionMode`, `PackLifecycleState`, `PackType`, `WorkloadKind`, `ModelFormat`, and reusable manifest fixtures for Tasks 3-7.

- [ ] **Step 1: Write the failing strict-manifest tests and fixture**

Create `tests/runtime/accelerator_packs/conftest.py`:

```python
import pytest

from nexusnet.runtime.accelerator_packs.contracts import RuntimePackManifest


@pytest.fixture
def manifest_factory():
    def build(**overrides):
        payload = {
            "pack_id": "org.nexusnet.test.cuda",
            "version": "1.0.0",
            "pack_type": "native-worker",
            "publisher": "NexusNet",
            "license_id": "MIT",
            "supported_os": ["windows"],
            "architectures": ["amd64"],
            "workload_kinds": ["llm-generate"],
            "model_formats": ["gguf"],
            "accelerator_apis": ["cuda"],
            "device_matches": [{"vendor_ids": ["10de"], "accelerator_apis": ["cuda"]}],
            "minimum_os_build": 26100,
            "dependency_constraints": {},
            "launch": {"command": ["worker.exe"], "environment_allowlist": ["TEMP", "TMP"]},
            "execution_modes": ["gpu"],
            "health_probe": {"operation": "health", "timeout_ms": 5000},
            "self_test_probe": {"operation": "self_test", "timeout_ms": 30000},
            "benchmark_probe": {"operation": "benchmark", "timeout_ms": 60000},
            "artifacts": [
                {
                    "url": "https://example.invalid/worker.zip",
                    "size_bytes": 1024,
                    "sha256": "a" * 64,
                }
            ],
            "capabilities": ["streaming"],
            "known_limitations": [],
            "rollback_compatible_from": ["0.9.0"],
            "data_migration_policy": "none",
        }
        payload.update(overrides)
        return RuntimePackManifest.model_validate(payload)

    return build
```

Create `tests/runtime/accelerator_packs/test_pack_contracts.py`:

```python
import pytest
from pydantic import ValidationError


def test_manifest_is_strict_versioned_and_serializes_declared_capabilities(manifest_factory):
    manifest = manifest_factory()

    assert manifest.schema_version == "1.0"
    assert manifest.pack_id == "org.nexusnet.test.cuda"
    assert manifest.execution_modes[0].value == "gpu"
    assert manifest.artifacts[0].sha256 == "a" * 64

    with pytest.raises(ValidationError):
        manifest.__class__.model_validate({**manifest.model_dump(mode="json"), "undeclared_field": True})


def test_hybrid_mode_requires_an_explicit_hybrid_offload_capability(manifest_factory):
    with pytest.raises(ValidationError, match="hybrid-offload"):
        manifest_factory(execution_modes=["hybrid"])

    manifest = manifest_factory(execution_modes=["gpu", "hybrid"], capabilities=["streaming", "hybrid-offload"])
    assert [mode.value for mode in manifest.execution_modes] == ["gpu", "hybrid"]
```

- [ ] **Step 2: Run the tests and verify the import failure**

Run: `python -m pytest tests/runtime/accelerator_packs/test_pack_contracts.py -q`

Expected: FAIL with `ModuleNotFoundError` for `nexusnet.runtime.accelerator_packs`.

- [ ] **Step 3: Create the package and exact strict contracts**

Create `nexusnet/runtime/accelerator_packs/__init__.py`:

```python
"""Vendor-neutral accelerator-pack contracts and process isolation."""
```

Create `nexusnet/runtime/accelerator_packs/contracts.py`:

```python
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
```

- [ ] **Step 4: Run the focused tests and verify green**

Run: `python -m pytest tests/runtime/accelerator_packs/test_pack_contracts.py -q`

Expected: 2 passed.

- [ ] **Step 5: Scope-check and commit Task 2**

Run:

```powershell
git add nexusnet/runtime/accelerator_packs/__init__.py nexusnet/runtime/accelerator_packs/contracts.py tests/runtime/accelerator_packs/conftest.py tests/runtime/accelerator_packs/test_pack_contracts.py
git diff --cached --check
```

Run `gitnexus_detect_changes` with `{"repo":"NexusNet","scope":"staged"}` and verify the change is isolated to new contracts and tests. Then commit:

```powershell
git commit -m "feat: define accelerator pack manifests"
```

---

### Task 3: Evaluate manifest compatibility without vendor branches

**Files:**

- Create: `nexusnet/runtime/accelerator_packs/compatibility.py`
- Create: `tests/runtime/accelerator_packs/test_compatibility.py`

**Interfaces:**

- Consumes: `HardwareNode`, `RuntimePackManifest`, `ExecutionMode`, `WorkloadKind`, and `ModelFormat`.
- Produces: `PackCompatibilityEvaluator.evaluate(...) -> CompatibilityDecision`; later installer and QES plans consume this pure decision.

- [ ] **Step 1: Write the failing compatibility tests**

Create `tests/runtime/accelerator_packs/test_compatibility.py`:

```python
from nexusnet.runtime.accelerator_packs.compatibility import PackCompatibilityEvaluator
from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode, ModelFormat, WorkloadKind
from nexusnet.runtime.hardware_contracts import HardwareNode


def test_compatibility_matches_capabilities_instead_of_vendor_dispatch(manifest_factory):
    manifest = manifest_factory(
        pack_id="org.nexusnet.test.vulkan",
        accelerator_apis=["vulkan"],
        device_matches=[{"accelerator_apis": ["vulkan"]}],
    )
    amd = HardwareNode(
        node_id="gpu:amd:0",
        kind="gpu",
        name="AMD GPU",
        backend="vulkan",
        vendor_id="1002",
        accelerator_apis=["vulkan", "directml"],
    )
    intel = HardwareNode(
        node_id="gpu:intel:0",
        kind="gpu",
        name="Intel GPU",
        backend="vulkan",
        vendor_id="8086",
        accelerator_apis=["vulkan", "directml"],
    )

    evaluator = PackCompatibilityEvaluator()
    for device in (amd, intel):
        decision = evaluator.evaluate(
            manifest=manifest,
            device=device,
            host_os="windows",
            architecture="amd64",
            os_build=26100,
            workload=WorkloadKind.LLM_GENERATE,
            model_format=ModelFormat.GGUF,
            requested_mode=ExecutionMode.GPU,
        )
        assert decision.compatible is True
        assert decision.reason_codes == ["manifest-compatible"]


def test_forced_modes_fail_honestly_when_device_class_or_pack_mode_conflicts(manifest_factory):
    cpu = HardwareNode(
        node_id="cpu:0",
        kind="cpu",
        name="CPU",
        backend="cpu",
        accelerator_apis=["cpu"],
    )
    decision = PackCompatibilityEvaluator().evaluate(
        manifest=manifest_factory(),
        device=cpu,
        host_os="windows",
        architecture="amd64",
        os_build=26100,
        workload=WorkloadKind.LLM_GENERATE,
        model_format=ModelFormat.GGUF,
        requested_mode=ExecutionMode.GPU,
    )

    assert decision.compatible is False
    assert "gpu-mode-requires-accelerator" in decision.reason_codes
    assert "device-api-mismatch" in decision.reason_codes
```

- [ ] **Step 2: Run the test and verify the expected red state**

Run: `python -m pytest tests/runtime/accelerator_packs/test_compatibility.py -q`

Expected: FAIL with `ModuleNotFoundError` for `compatibility`.

- [ ] **Step 3: Implement the pure compatibility evaluator**

Create `nexusnet/runtime/accelerator_packs/compatibility.py`:

```python
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
```

- [ ] **Step 4: Run the focused contract matrix**

Run:

```powershell
python -m pytest tests/runtime/accelerator_packs/test_pack_contracts.py tests/runtime/accelerator_packs/test_compatibility.py -q
```

Expected: 4 passed.

- [ ] **Step 5: Scope-check and commit Task 3**

Run:

```powershell
git add nexusnet/runtime/accelerator_packs/compatibility.py tests/runtime/accelerator_packs/test_compatibility.py
git diff --cached --check
```

Run `gitnexus_detect_changes` with `{"repo":"NexusNet","scope":"staged"}` and verify only the pure evaluator and tests appear. Then commit:

```powershell
git commit -m "feat: evaluate accelerator pack compatibility"
```

---

### Task 4: Persist pack lifecycle, activation, quarantine, and rollback atomically

**Files:**

- Create: `nexusnet/runtime/accelerator_packs/registry.py`
- Create: `tests/runtime/accelerator_packs/test_pack_registry.py`

**Interfaces:**

- Consumes: `RuntimePackManifest` and `PackLifecycleState`.
- Produces: `RuntimePackRegistry`, `RuntimePackRecord`, `RegistrySnapshot`, and `RegistryError`; later pack-manager and router plans read this state but do not bypass it.

- [ ] **Step 1: Write failing restart, transition, activation, and rollback tests**

Create `tests/runtime/accelerator_packs/test_pack_registry.py`:

```python
import pytest

from nexusnet.runtime.accelerator_packs.contracts import PackLifecycleState
from nexusnet.runtime.accelerator_packs.registry import RegistryError, RuntimePackRegistry


def _advance_to_verifying(registry, pack_id: str, version: str) -> None:
    registry.transition(pack_id, version, PackLifecycleState.DOWNLOADING)
    registry.transition(pack_id, version, PackLifecycleState.STAGED, install_ref=f"packs/{pack_id}/{version}")
    registry.transition(pack_id, version, PackLifecycleState.VERIFYING)


def test_registry_restores_atomic_active_and_previous_versions_then_rolls_back(tmp_path, manifest_factory):
    path = tmp_path / "runtime" / "accelerator-packs" / "registry-v1.json"
    registry = RuntimePackRegistry(path)
    first = manifest_factory(version="1.0.0")
    second = manifest_factory(version="1.1.0")

    registry.register_manifest(first)
    _advance_to_verifying(registry, first.pack_id, first.version)
    registry.activate(first.pack_id, first.version)
    registry.register_manifest(second)
    _advance_to_verifying(registry, second.pack_id, second.version)
    registry.activate(second.pack_id, second.version)

    restored = RuntimePackRegistry(path)
    assert restored.active(first.pack_id).manifest.version == "1.1.0"
    assert restored.get(first.pack_id, "1.0.0").state == PackLifecycleState.ROLLBACK_AVAILABLE
    assert restored.snapshot().previous_versions[first.pack_id] == "1.0.0"

    restored.rollback(first.pack_id, reason_code="new-version-crashed")
    assert restored.active(first.pack_id).manifest.version == "1.0.0"
    assert restored.get(first.pack_id, "1.1.0").state == PackLifecycleState.QUARANTINED
    assert not path.with_suffix(".tmp").exists()


def test_registry_rejects_invalid_transitions_and_corrupt_state_without_private_detail(tmp_path, manifest_factory):
    path = tmp_path / "registry-v1.json"
    registry = RuntimePackRegistry(path)
    manifest = manifest_factory()
    registry.register_manifest(manifest)

    with pytest.raises(RegistryError, match="lifecycle-transition-invalid") as invalid:
        registry.activate(manifest.pack_id, manifest.version)
    assert str(tmp_path) not in str(invalid.value)

    path.write_text('{"secret":"C:/Users/Private/model.gguf"}', encoding="utf-8")
    with pytest.raises(RegistryError, match="registry-invalid") as corrupt:
        RuntimePackRegistry(path)
    assert "Private" not in str(corrupt.value)
```

- [ ] **Step 2: Run the tests and verify the expected red state**

Run: `python -m pytest tests/runtime/accelerator_packs/test_pack_registry.py -q`

Expected: FAIL with `ModuleNotFoundError` for `registry`.

- [ ] **Step 3: Implement the atomic lifecycle registry**

Create `nexusnet/runtime/accelerator_packs/registry.py`:

```python
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from threading import RLock
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .contracts import PackLifecycleState, RuntimePackManifest


class RegistryError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


class RuntimePackRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    manifest: RuntimePackManifest
    state: PackLifecycleState = PackLifecycleState.AVAILABLE
    install_ref: str | None = None
    reason_codes: list[str] = Field(default_factory=list)
    updated_at: datetime

    @field_validator("install_ref")
    @classmethod
    def validate_install_ref(cls, value: str | None) -> str | None:
        if value is None:
            return None
        ref = PurePosixPath(value.replace("\\", "/"))
        if ref.is_absolute() or ".." in ref.parts:
            raise ValueError("install_ref must be a relative private-pack reference")
        return ref.as_posix()


class RegistrySnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    records: dict[str, RuntimePackRecord] = Field(default_factory=dict)
    active_versions: dict[str, str] = Field(default_factory=dict)
    previous_versions: dict[str, str] = Field(default_factory=dict)


_ALLOWED_TRANSITIONS = {
    PackLifecycleState.AVAILABLE: {PackLifecycleState.DOWNLOADING, PackLifecycleState.REMOVED},
    PackLifecycleState.DOWNLOADING: {PackLifecycleState.STAGED, PackLifecycleState.QUARANTINED},
    PackLifecycleState.STAGED: {PackLifecycleState.VERIFYING, PackLifecycleState.QUARANTINED},
    PackLifecycleState.VERIFYING: {PackLifecycleState.ACTIVE, PackLifecycleState.QUARANTINED},
    PackLifecycleState.ACTIVE: {
        PackLifecycleState.DEGRADED,
        PackLifecycleState.QUARANTINED,
        PackLifecycleState.ROLLBACK_AVAILABLE,
    },
    PackLifecycleState.DEGRADED: {
        PackLifecycleState.ACTIVE,
        PackLifecycleState.QUARANTINED,
        PackLifecycleState.ROLLBACK_AVAILABLE,
    },
    PackLifecycleState.QUARANTINED: {PackLifecycleState.STAGED, PackLifecycleState.REMOVED},
    PackLifecycleState.ROLLBACK_AVAILABLE: {PackLifecycleState.ACTIVE, PackLifecycleState.REMOVED},
    PackLifecycleState.REMOVED: {PackLifecycleState.AVAILABLE},
}


class RuntimePackRegistry:
    def __init__(self, registry_path: str | Path):
        self._path = Path(registry_path)
        self._lock = RLock()
        self._snapshot = self._load()

    @staticmethod
    def _key(pack_id: str, version: str) -> str:
        return f"{pack_id}@{version}"

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _updated_record(record: RuntimePackRecord, **updates) -> RuntimePackRecord:
        payload = record.model_dump(mode="json")
        payload.update(updates)
        return RuntimePackRecord.model_validate(payload)

    def _load(self) -> RegistrySnapshot:
        if not self._path.exists():
            return RegistrySnapshot()
        try:
            return RegistrySnapshot.model_validate_json(self._path.read_text(encoding="utf-8"))
        except (OSError, ValidationError, ValueError):
            raise RegistryError("registry-invalid") from None

    def _persist(self, snapshot: RegistrySnapshot) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(".tmp")
        temporary.write_text(snapshot.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(self._path)
        self._snapshot = snapshot

    def snapshot(self) -> RegistrySnapshot:
        return self._snapshot.model_copy(deep=True)

    def register_manifest(self, manifest: RuntimePackManifest) -> RuntimePackRecord:
        with self._lock:
            key = self._key(manifest.pack_id, manifest.version)
            existing = self._snapshot.records.get(key)
            if existing is not None:
                if existing.manifest != manifest:
                    raise RegistryError("manifest-version-conflict")
                return existing
            record = RuntimePackRecord(manifest=manifest, updated_at=self._now())
            records = {**self._snapshot.records, key: record}
            self._persist(self._snapshot.model_copy(update={"records": records}))
            return record

    def get(self, pack_id: str, version: str) -> RuntimePackRecord:
        try:
            return self._snapshot.records[self._key(pack_id, version)]
        except KeyError:
            raise RegistryError("pack-version-not-registered") from None

    def active(self, pack_id: str) -> RuntimePackRecord:
        version = self._snapshot.active_versions.get(pack_id)
        if version is None:
            raise RegistryError("active-pack-unavailable")
        return self.get(pack_id, version)

    def transition(
        self,
        pack_id: str,
        version: str,
        target: PackLifecycleState,
        *,
        install_ref: str | None = None,
        reason_code: str | None = None,
    ) -> RuntimePackRecord:
        with self._lock:
            current = self.get(pack_id, version)
            if target not in _ALLOWED_TRANSITIONS[current.state]:
                raise RegistryError("lifecycle-transition-invalid")
            updated = self._updated_record(
                current,
                state=target,
                install_ref=install_ref if install_ref is not None else current.install_ref,
                reason_codes=[*current.reason_codes, reason_code] if reason_code else current.reason_codes,
                updated_at=self._now(),
            )
            records = {**self._snapshot.records, self._key(pack_id, version): updated}
            self._persist(self._snapshot.model_copy(update={"records": records}))
            return updated

    def activate(self, pack_id: str, version: str) -> RuntimePackRecord:
        with self._lock:
            candidate = self.get(pack_id, version)
            if candidate.state != PackLifecycleState.VERIFYING:
                raise RegistryError("lifecycle-transition-invalid")
            records = dict(self._snapshot.records)
            active_versions = dict(self._snapshot.active_versions)
            previous_versions = dict(self._snapshot.previous_versions)
            previous = active_versions.get(pack_id)
            if previous and previous != version:
                old_key = self._key(pack_id, previous)
                records[old_key] = self._updated_record(
                    records[old_key],
                    state=PackLifecycleState.ROLLBACK_AVAILABLE,
                    updated_at=self._now(),
                )
                previous_versions[pack_id] = previous
            activated = self._updated_record(
                candidate,
                state=PackLifecycleState.ACTIVE,
                updated_at=self._now(),
            )
            records[self._key(pack_id, version)] = activated
            active_versions[pack_id] = version
            self._persist(
                self._snapshot.model_copy(
                    update={
                        "records": records,
                        "active_versions": active_versions,
                        "previous_versions": previous_versions,
                    }
                )
            )
            return activated

    def rollback(self, pack_id: str, *, reason_code: str) -> RuntimePackRecord:
        with self._lock:
            current_version = self._snapshot.active_versions.get(pack_id)
            target_version = self._snapshot.previous_versions.get(pack_id)
            if current_version is None or target_version is None:
                raise RegistryError("rollback-unavailable")
            current = self.get(pack_id, current_version)
            target = self.get(pack_id, target_version)
            if target.state != PackLifecycleState.ROLLBACK_AVAILABLE:
                raise RegistryError("rollback-unavailable")
            records = dict(self._snapshot.records)
            records[self._key(pack_id, current_version)] = self._updated_record(
                current,
                state=PackLifecycleState.QUARANTINED,
                reason_codes=[*current.reason_codes, reason_code],
                updated_at=self._now(),
            )
            restored = self._updated_record(
                target,
                state=PackLifecycleState.ACTIVE,
                updated_at=self._now(),
            )
            records[self._key(pack_id, target_version)] = restored
            active_versions = {**self._snapshot.active_versions, pack_id: target_version}
            previous_versions = dict(self._snapshot.previous_versions)
            previous_versions.pop(pack_id, None)
            self._persist(
                self._snapshot.model_copy(
                    update={
                        "records": records,
                        "active_versions": active_versions,
                        "previous_versions": previous_versions,
                    }
                )
            )
            return restored
```

- [ ] **Step 4: Run the registry and contract tests**

Run:

```powershell
python -m pytest tests/runtime/accelerator_packs/test_pack_contracts.py tests/runtime/accelerator_packs/test_pack_registry.py -q
```

Expected: 4 passed, the registry artifact is restored after restart, and no `.tmp` file remains.

- [ ] **Step 5: Scope-check and commit Task 4**

Run:

```powershell
git add nexusnet/runtime/accelerator_packs/registry.py tests/runtime/accelerator_packs/test_pack_registry.py
git diff --cached --check
```

Run `gitnexus_detect_changes` with `{"repo":"NexusNet","scope":"staged"}` and verify only the lifecycle registry and tests appear. Then commit:

```powershell
git commit -m "feat: persist accelerator pack lifecycle"
```

---

### Task 5: Define a bounded and sanitized JSON-lines worker protocol

**Files:**

- Create: `nexusnet/runtime/accelerator_packs/protocol.py`
- Create: `tests/runtime/accelerator_packs/test_worker_protocol.py`

**Interfaces:**

- Consumes: `ExecutionMode`.
- Produces: `WorkerOperation`, `WorkerRequest`, `WorkerFrame`, `JsonLineCodec`, and `ProtocolError` for Task 6.

- [ ] **Step 1: Write failing codec, terminal-frame, and sanitation tests**

Create `tests/runtime/accelerator_packs/test_worker_protocol.py`:

```python
import pytest
from pydantic import ValidationError

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode
from nexusnet.runtime.accelerator_packs.protocol import (
    JsonLineCodec,
    ProtocolError,
    WorkerFrame,
    WorkerOperation,
    WorkerRequest,
)


def test_protocol_round_trips_a_versioned_request_and_terminal_result():
    codec = JsonLineCodec(max_frame_bytes=4096)
    request = WorkerRequest(
        request_id="request-1",
        operation=WorkerOperation.HEALTH,
        deadline_unix_ms=4_000_000_000_000,
        sanitized_model_ref="model::none",
        workload_profile={"batch_size": 1},
        execution_mode=ExecutionMode.AUTO,
        policy_receipt_ref="receipt::test",
        payload={},
    )
    decoded = codec.decode_request(codec.encode(request))
    assert decoded == request

    frame = WorkerFrame(request_id=request.request_id, event="result", sequence=0, terminal=True, payload={"available": True})
    assert codec.decode_frame(codec.encode(frame)) == frame


def test_protocol_rejects_invalid_or_oversized_frames_without_echoing_content():
    codec = JsonLineCodec(max_frame_bytes=32)
    secret = b'{"prompt":"private prompt that must not escape"}\n'
    with pytest.raises(ProtocolError, match="worker-frame-too-large") as oversized:
        codec.decode_frame(secret)
    assert "private prompt" not in str(oversized.value)

    with pytest.raises(ProtocolError, match="worker-frame-invalid") as malformed:
        JsonLineCodec().decode_frame(b"not-json-and-private\n")
    assert "private" not in str(malformed.value)

    with pytest.raises(ValidationError, match="terminal"):
        WorkerFrame(request_id="request-1", event="result", sequence=0, terminal=False, payload={})
```

- [ ] **Step 2: Run the tests and verify the expected red state**

Run: `python -m pytest tests/runtime/accelerator_packs/test_worker_protocol.py -q`

Expected: FAIL with `ModuleNotFoundError` for `protocol`.

- [ ] **Step 3: Implement the exact bounded protocol and codec**

Create `nexusnet/runtime/accelerator_packs/protocol.py`:

```python
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .contracts import ExecutionMode


class ProtocolError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


class WorkerOperation(str, Enum):
    DESCRIBE = "describe"
    HEALTH = "health"
    SELF_TEST = "self_test"
    BENCHMARK = "benchmark"
    LOAD_MODEL = "load_model"
    INFER = "infer"
    UNLOAD_MODEL = "unload_model"
    CANCEL = "cancel"
    SHUTDOWN = "shutdown"


class WorkerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    protocol_version: Literal["1.0"] = "1.0"
    request_id: str = Field(min_length=1, max_length=128)
    operation: WorkerOperation
    deadline_unix_ms: int = Field(gt=0)
    sanitized_model_ref: str = Field(min_length=1, max_length=256)
    workload_profile: dict[str, int | float | str | bool] = Field(default_factory=dict)
    execution_mode: ExecutionMode
    policy_receipt_ref: str = Field(min_length=1, max_length=256)
    payload: dict[str, Any] = Field(default_factory=dict)


class WorkerFrame(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    protocol_version: Literal["1.0"] = "1.0"
    request_id: str = Field(min_length=1, max_length=128)
    event: Literal["accepted", "chunk", "result", "error"]
    sequence: int = Field(ge=0)
    terminal: bool = False
    payload: dict[str, Any] = Field(default_factory=dict)
    reason_code: str | None = None

    @model_validator(mode="after")
    def validate_terminal_semantics(self) -> "WorkerFrame":
        if self.event in {"result", "error"} and not self.terminal:
            raise ValueError("result and error frames must be terminal")
        if self.event in {"accepted", "chunk"} and self.terminal:
            raise ValueError("accepted and chunk frames cannot be terminal")
        if self.event == "error" and not self.reason_code:
            raise ValueError("error frames require a reason_code")
        return self


class JsonLineCodec:
    def __init__(self, *, max_frame_bytes: int = 4 * 1024 * 1024):
        if max_frame_bytes <= 0:
            raise ValueError("max_frame_bytes must be positive")
        self.max_frame_bytes = max_frame_bytes

    def encode(self, message: BaseModel) -> bytes:
        encoded = (message.model_dump_json() + "\n").encode("utf-8")
        if len(encoded) > self.max_frame_bytes:
            raise ProtocolError("worker-frame-too-large")
        return encoded

    def decode_request(self, raw: bytes) -> WorkerRequest:
        return self._decode(raw, WorkerRequest)

    def decode_frame(self, raw: bytes) -> WorkerFrame:
        return self._decode(raw, WorkerFrame)

    def _decode(self, raw: bytes, model_type):
        if len(raw) > self.max_frame_bytes:
            raise ProtocolError("worker-frame-too-large")
        try:
            text = raw.decode("utf-8")
            if not text.endswith("\n"):
                raise ValueError("unterminated")
            return model_type.model_validate_json(text)
        except (UnicodeDecodeError, ValueError, ValidationError):
            raise ProtocolError("worker-frame-invalid") from None
```

- [ ] **Step 4: Run the focused protocol tests**

Run: `python -m pytest tests/runtime/accelerator_packs/test_worker_protocol.py -q`

Expected: 2 passed.

- [ ] **Step 5: Scope-check and commit Task 5**

Run:

```powershell
git add nexusnet/runtime/accelerator_packs/protocol.py tests/runtime/accelerator_packs/test_worker_protocol.py
git diff --cached --check
```

Run `gitnexus_detect_changes` with `{"repo":"NexusNet","scope":"staged"}` and verify only the protocol and tests appear. Then commit:

```powershell
git commit -m "feat: define accelerator worker protocol"
```

---

### Task 6: Supervise an isolated worker with bounded requests and honest failures

**Files:**

- Create: `nexusnet/runtime/accelerator_packs/supervisor.py`
- Create: `tests/fixtures/accelerator_pack_worker.py`
- Create: `tests/runtime/accelerator_packs/test_worker_supervisor.py`

**Interfaces:**

- Consumes: `JsonLineCodec`, `WorkerOperation`, `WorkerRequest`, `WorkerFrame`, and `ExecutionMode`.
- Produces: `WorkerSupervisor.request(...) -> list[WorkerFrame]`, `WorkerSupervisor.stop()`, and `WorkerSupervisorError` for Task 7.

- [ ] **Step 1: Create the dependency-free fixture worker**

Create `tests/fixtures/accelerator_pack_worker.py`:

```python
import json
import subprocess
import sys
import time


def emit(request_id, event, sequence, terminal, payload=None, reason_code=None):
    frame = {
        "protocol_version": "1.0",
        "request_id": request_id,
        "event": event,
        "sequence": sequence,
        "terminal": terminal,
        "payload": payload or {},
        "reason_code": reason_code,
    }
    sys.stdout.write(json.dumps(frame, separators=(",", ":")) + "\n")
    sys.stdout.flush()


for line in sys.stdin:
    request = json.loads(line)
    request_id = request["request_id"]
    operation = request["operation"]
    payload = request.get("payload", {})
    if operation == "health":
        emit(request_id, "result", 0, True, {"available": True, "capabilities": {"streaming": True}})
    elif operation == "describe":
        emit(request_id, "result", 0, True, {"worker": "fixture", "protocol_version": "1.0"})
    elif operation == "infer":
        emit(request_id, "accepted", 0, False)
        emit(request_id, "chunk", 1, False, {"text": "worker:"})
        emit(request_id, "result", 2, True, {"text": "worker:" + payload.get("prompt", "")})
    elif operation == "benchmark" and payload.get("hang"):
        time.sleep(5)
    elif operation == "self_test" and payload.get("malformed"):
        sys.stdout.write("not-json-private-output\n")
        sys.stdout.flush()
    elif operation == "shutdown":
        emit(request_id, "result", 0, True, {"stopped": True})
        break
    else:
        emit(request_id, "error", 0, True, reason_code="operation-unsupported")
```

- [ ] **Step 2: Write failing process, timeout, malformed-frame, and sanitation tests**

Create `tests/runtime/accelerator_packs/test_worker_supervisor.py`:

```python
import sys
from pathlib import Path

import pytest

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode
from nexusnet.runtime.accelerator_packs.protocol import WorkerOperation
from nexusnet.runtime.accelerator_packs.supervisor import WorkerSupervisor, WorkerSupervisorError


def _command() -> list[str]:
    fixture = Path(__file__).parents[2] / "fixtures" / "accelerator_pack_worker.py"
    return [sys.executable, "-I", str(fixture)]


def test_supervisor_correlates_streaming_frames_and_stops_the_worker():
    supervisor = WorkerSupervisor(command=_command(), request_timeout_s=2)
    health = supervisor.request(
        WorkerOperation.HEALTH,
        sanitized_model_ref="model::none",
        execution_mode=ExecutionMode.AUTO,
        policy_receipt_ref="receipt::health",
    )
    inference = supervisor.request(
        WorkerOperation.INFER,
        sanitized_model_ref="model::fixture",
        execution_mode=ExecutionMode.CPU,
        policy_receipt_ref="receipt::infer",
        payload={"prompt": "hello"},
    )

    assert health[-1].payload["available"] is True
    assert [frame.event for frame in inference] == ["accepted", "chunk", "result"]
    assert inference[-1].payload["text"] == "worker:hello"
    supervisor.stop()
    assert supervisor.running is False


def test_supervisor_terminates_timeout_and_malformed_workers_without_echoing_payload():
    timeout_supervisor = WorkerSupervisor(command=_command(), request_timeout_s=0.1)
    with pytest.raises(WorkerSupervisorError, match="worker-timeout") as timeout:
        timeout_supervisor.request(
            WorkerOperation.BENCHMARK,
            sanitized_model_ref="model::secret",
            execution_mode=ExecutionMode.GPU,
            policy_receipt_ref="receipt::timeout",
            payload={"hang": True, "prompt": "private timeout prompt"},
        )
    assert "private timeout prompt" not in str(timeout.value)
    assert timeout_supervisor.running is False

    malformed_supervisor = WorkerSupervisor(command=_command(), request_timeout_s=2)
    with pytest.raises(WorkerSupervisorError, match="worker-frame-invalid") as malformed:
        malformed_supervisor.request(
            WorkerOperation.SELF_TEST,
            sanitized_model_ref="model::none",
            execution_mode=ExecutionMode.CPU,
            policy_receipt_ref="receipt::malformed",
            payload={"malformed": True},
        )
    assert "private-output" not in str(malformed.value)
    assert malformed_supervisor.running is False
```

- [ ] **Step 3: Run the tests and verify the expected red state**

Run: `python -m pytest tests/runtime/accelerator_packs/test_worker_supervisor.py -q`

Expected: FAIL with `ModuleNotFoundError` for `supervisor`.

- [ ] **Step 4: Implement the bounded subprocess supervisor**

Create `nexusnet/runtime/accelerator_packs/supervisor.py`:

```python
from __future__ import annotations

import os
import queue
import subprocess
import threading
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from .contracts import ExecutionMode
from .protocol import JsonLineCodec, ProtocolError, WorkerFrame, WorkerOperation, WorkerRequest


class WorkerSupervisorError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


class WorkerSupervisor:
    _BASE_ENVIRONMENT = ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "PATHEXT", "TEMP", "TMP")

    def __init__(
        self,
        *,
        command: list[str],
        working_directory: str | Path | None = None,
        environment: dict[str, str] | None = None,
        request_timeout_s: float = 30.0,
        codec: JsonLineCodec | None = None,
    ) -> None:
        if not command:
            raise ValueError("worker command must not be empty")
        if request_timeout_s <= 0:
            raise ValueError("request_timeout_s must be positive")
        self._command = list(command)
        self._working_directory = str(working_directory) if working_directory is not None else None
        self._environment = dict(environment or {})
        self._request_timeout_s = request_timeout_s
        self._codec = codec or JsonLineCodec()
        self._process: subprocess.Popen[bytes] | None = None
        self._frames: queue.Queue[bytes | None] = queue.Queue()
        self._request_lock = threading.RLock()
        self._reader: threading.Thread | None = None

    @property
    def running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def _worker_environment(self) -> dict[str, str]:
        environment = {key: os.environ[key] for key in self._BASE_ENVIRONMENT if key in os.environ}
        environment.update(self._environment)
        environment["PYTHONNOUSERSITE"] = "1"
        environment["PYTHONUNBUFFERED"] = "1"
        return environment

    def start(self) -> None:
        with self._request_lock:
            if self.running:
                return
            self._frames = queue.Queue()
            try:
                self._process = subprocess.Popen(
                    self._command,
                    cwd=self._working_directory,
                    env=self._worker_environment(),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    bufsize=0,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except OSError:
                self._process = None
                raise WorkerSupervisorError("worker-start-failed") from None
            self._reader = threading.Thread(target=self._read_stdout, name="nexusnet-pack-worker-reader", daemon=True)
            self._reader.start()

    def _read_stdout(self) -> None:
        process = self._process
        if process is None or process.stdout is None:
            self._frames.put(None)
            return
        try:
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                self._frames.put(line)
        finally:
            self._frames.put(None)

    def request(
        self,
        operation: WorkerOperation,
        *,
        sanitized_model_ref: str,
        execution_mode: ExecutionMode,
        policy_receipt_ref: str,
        workload_profile: dict[str, int | float | str | bool] | None = None,
        payload: dict[str, Any] | None = None,
        timeout_s: float | None = None,
    ) -> list[WorkerFrame]:
        with self._request_lock:
            self.start()
            process = self._process
            if process is None or process.stdin is None:
                raise WorkerSupervisorError("worker-start-failed")
            timeout = timeout_s if timeout_s is not None else self._request_timeout_s
            request_id = f"request-{uuid4().hex}"
            request = WorkerRequest(
                request_id=request_id,
                operation=operation,
                deadline_unix_ms=int((time.time() + timeout) * 1000),
                sanitized_model_ref=sanitized_model_ref,
                workload_profile=workload_profile or {},
                execution_mode=execution_mode,
                policy_receipt_ref=policy_receipt_ref,
                payload=payload or {},
            )
            try:
                process.stdin.write(self._codec.encode(request))
                process.stdin.flush()
            except (BrokenPipeError, OSError, ProtocolError) as error:
                self._terminate()
                reason = error.reason_code if isinstance(error, ProtocolError) else "worker-write-failed"
                raise WorkerSupervisorError(reason) from None

            deadline = time.monotonic() + timeout
            frames: list[WorkerFrame] = []
            while len(frames) < 4096:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self._terminate()
                    raise WorkerSupervisorError("worker-timeout")
                try:
                    raw = self._frames.get(timeout=remaining)
                except queue.Empty:
                    self._terminate()
                    raise WorkerSupervisorError("worker-timeout") from None
                if raw is None:
                    self._terminate()
                    raise WorkerSupervisorError("worker-exited")
                try:
                    frame = self._codec.decode_frame(raw)
                except ProtocolError as error:
                    self._terminate()
                    raise WorkerSupervisorError(error.reason_code) from None
                if frame.request_id != request_id:
                    self._terminate()
                    raise WorkerSupervisorError("worker-request-mismatch")
                frames.append(frame)
                if frame.terminal:
                    return frames
            self._terminate()
            raise WorkerSupervisorError("worker-frame-limit-exceeded")

    def stop(self) -> None:
        with self._request_lock:
            if not self.running:
                self._terminate()
                return
            try:
                self.request(
                    WorkerOperation.SHUTDOWN,
                    sanitized_model_ref="model::none",
                    execution_mode=ExecutionMode.AUTO,
                    policy_receipt_ref="receipt::shutdown",
                    timeout_s=min(2.0, self._request_timeout_s),
                )
            except WorkerSupervisorError:
                pass
            finally:
                self._terminate()

    def _terminate(self) -> None:
        process = self._process
        self._process = None
        if process is None:
            return
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        if process.stdin is not None:
            process.stdin.close()
        if process.stdout is not None:
            process.stdout.close()
```

- [ ] **Step 5: Run supervisor and protocol tests**

Run:

```powershell
python -m pytest tests/runtime/accelerator_packs/test_worker_protocol.py tests/runtime/accelerator_packs/test_worker_supervisor.py -q
```

Expected: 4 passed; both faulting workers are terminated and no private fixture payload appears in exception text.

- [ ] **Step 6: Scope-check and commit Task 6**

Run:

```powershell
git add nexusnet/runtime/accelerator_packs/supervisor.py tests/fixtures/accelerator_pack_worker.py tests/runtime/accelerator_packs/test_worker_supervisor.py
git diff --cached --check
```

Run `gitnexus_detect_changes` with `{"repo":"NexusNet","scope":"staged"}` and verify only supervisor/fixture/test symbols appear. Then commit:

```powershell
git commit -m "feat: supervise isolated accelerator workers"
```

---

### Task 7: Add an inactive worker-backed RuntimeAdapter and close the foundation gate

**Files:**

- Create: `nexus/runtimes/worker.py`
- Modify: `nexusnet/runtime/accelerator_packs/__init__.py`
- Create: `tests/runtime/accelerator_packs/test_worker_runtime_adapter.py`
- Verify unchanged: `nexus/runtimes/registry.py`

**Interfaces:**

- Consumes: Existing `RuntimeAdapter.generate(...)`, `RuntimeAdapter.health()`, `prompt_from_messages`, `RuntimePackManifest`, and `WorkerSupervisor`.
- Produces: `WorkerRuntimeAdapter` and `RuntimeExecutionError`. It is importable for tests but intentionally absent from `RuntimeRegistry.adapters` and `RuntimeRegistry.choose`.

- [ ] **Step 1: Write the failing adapter and core-import isolation tests**

Create `tests/runtime/accelerator_packs/test_worker_runtime_adapter.py`:

```python
import sys
from pathlib import Path

from nexus.schemas import Message
from nexus.runtimes.worker import WorkerRuntimeAdapter
from nexusnet.runtime.accelerator_packs.supervisor import WorkerSupervisor


def _command() -> list[str]:
    fixture = Path(__file__).parents[2] / "fixtures" / "accelerator_pack_worker.py"
    return [sys.executable, "-I", str(fixture)]


def test_worker_adapter_preserves_health_profile_and_generate_contract(manifest_factory):
    supervisor = WorkerSupervisor(command=_command(), request_timeout_s=2)
    adapter = WorkerRuntimeAdapter(manifest=manifest_factory(), supervisor=supervisor)

    health = adapter.health()
    generated = adapter.generate(
        prompt=None,
        messages=[Message(role="user", content="hello")],
        model_id="fixture-model",
        metadata={"execution_mode": "gpu", "policy_receipt_ref": "receipt::adapter"},
    )

    assert health["available"] is True
    assert health["pack_id"] == "org.nexusnet.test.cuda"
    assert adapter.profile().backend_type == "managed-worker"
    assert generated == "worker:USER: hello"
    supervisor.stop()


def test_accelerator_pack_core_imports_no_vendor_runtime_modules():
    repository_root = Path(__file__).parents[3]
    script = (
        "import sys; import nexusnet.runtime.accelerator_packs; "
        "banned=('torch','onnxruntime','openvino','intel_extension_for_pytorch'); "
        "assert not any(n == b or n.startswith(b + '.') for n in sys.modules for b in banned)"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=repository_root,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
```

- [ ] **Step 2: Run the test and verify the expected red state**

Run: `python -m pytest tests/runtime/accelerator_packs/test_worker_runtime_adapter.py -q`

Expected: FAIL with `ModuleNotFoundError` for `nexus.runtimes.worker`.

- [ ] **Step 3: Implement the inactive adapter**

Create `nexus/runtimes/worker.py`:

```python
from __future__ import annotations

import hashlib
from typing import Any

from nexusnet.runtime.accelerator_packs.contracts import ExecutionMode, RuntimePackManifest
from nexusnet.runtime.accelerator_packs.protocol import WorkerOperation
from nexusnet.runtime.accelerator_packs.supervisor import WorkerSupervisor, WorkerSupervisorError

from ..schemas import Message
from .base import RuntimeAdapter, prompt_from_messages


class RuntimeExecutionError(RuntimeError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


class WorkerRuntimeAdapter(RuntimeAdapter):
    runtime_name = "accelerator-pack"
    backend_type = "managed-worker"

    def __init__(self, *, manifest: RuntimePackManifest, supervisor: WorkerSupervisor):
        super().__init__({"pack_id": manifest.pack_id, "pack_version": manifest.version})
        self.manifest = manifest
        self.supervisor = supervisor

    @staticmethod
    def _sanitized_model_ref(model_id: str) -> str:
        digest = hashlib.sha256(model_id.encode("utf-8")).hexdigest()[:24]
        return f"model::{digest}"

    @staticmethod
    def _execution_mode(metadata: dict[str, Any] | None) -> ExecutionMode:
        value = str((metadata or {}).get("execution_mode", "auto")).lower()
        if value == "both":
            value = "hybrid"
        try:
            return ExecutionMode(value)
        except ValueError:
            raise RuntimeExecutionError("execution-mode-invalid") from None

    def health(self) -> dict[str, Any]:
        try:
            frames = self.supervisor.request(
                WorkerOperation.HEALTH,
                sanitized_model_ref="model::none",
                execution_mode=ExecutionMode.AUTO,
                policy_receipt_ref="receipt::runtime-health",
            )
        except WorkerSupervisorError as error:
            return {
                "available": False,
                "pack_id": self.manifest.pack_id,
                "pack_version": self.manifest.version,
                "reason_codes": [error.reason_code],
                "capabilities": {},
            }
        result = frames[-1]
        if result.event == "error":
            return {
                "available": False,
                "pack_id": self.manifest.pack_id,
                "pack_version": self.manifest.version,
                "reason_codes": [result.reason_code or "worker-health-failed"],
                "capabilities": {},
            }
        return {
            "available": bool(result.payload.get("available", False)),
            "pack_id": self.manifest.pack_id,
            "pack_version": self.manifest.version,
            "capabilities": {
                "declared": list(self.manifest.capabilities),
                "reported": result.payload.get("capabilities", {}),
            },
            "metrics": {},
        }

    def generate(
        self,
        *,
        prompt: str | None,
        messages: list[Message],
        model_id: str,
        expert: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        mode = self._execution_mode(metadata)
        policy_receipt_ref = str((metadata or {}).get("policy_receipt_ref", "receipt::runtime-generate"))
        try:
            frames = self.supervisor.request(
                WorkerOperation.INFER,
                sanitized_model_ref=self._sanitized_model_ref(model_id),
                execution_mode=mode,
                policy_receipt_ref=policy_receipt_ref,
                payload={
                    "prompt": prompt_from_messages(messages, prompt),
                    "model_id": model_id,
                    "expert": expert,
                },
            )
        except WorkerSupervisorError as error:
            raise RuntimeExecutionError(error.reason_code) from None
        result = frames[-1]
        if result.event == "error":
            raise RuntimeExecutionError(result.reason_code or "worker-inference-failed")
        text = result.payload.get("text")
        if not isinstance(text, str):
            raise RuntimeExecutionError("worker-result-invalid")
        return text
```

- [ ] **Step 4: Export only the pack-foundation contracts, not a live adapter registration**

Replace `nexusnet/runtime/accelerator_packs/__init__.py` with:

```python
"""Vendor-neutral accelerator-pack contracts and process isolation."""

from .compatibility import CompatibilityDecision, PackCompatibilityEvaluator
from .contracts import (
    ExecutionMode,
    ModelFormat,
    PackLifecycleState,
    PackType,
    RuntimePackManifest,
    WorkloadKind,
)
from .protocol import JsonLineCodec, ProtocolError, WorkerFrame, WorkerOperation, WorkerRequest
from .registry import RegistryError, RuntimePackRecord, RuntimePackRegistry
from .supervisor import WorkerSupervisor, WorkerSupervisorError

__all__ = [
    "CompatibilityDecision",
    "ExecutionMode",
    "JsonLineCodec",
    "ModelFormat",
    "PackCompatibilityEvaluator",
    "PackLifecycleState",
    "PackType",
    "ProtocolError",
    "RegistryError",
    "RuntimePackManifest",
    "RuntimePackRecord",
    "RuntimePackRegistry",
    "WorkerFrame",
    "WorkerOperation",
    "WorkerRequest",
    "WorkerSupervisor",
    "WorkerSupervisorError",
    "WorkloadKind",
]
```

Do not edit `nexus/runtimes/registry.py` or `nexus/runtimes/__init__.py` in this task.

- [ ] **Step 5: Run the complete foundation and existing runtime regression matrices**

Run:

```powershell
python -m pytest tests/runtime/accelerator_packs -q
python -m pytest tests/runtime/test_evolutionary_inference_foundation.py tests/runtime/test_evolutionary_inference_system.py tests/test_corpus_assimilation_runtime.py -q
python -m pytest -q
python -c "import sys; import nexusnet.runtime.accelerator_packs; banned=('torch','onnxruntime','openvino','intel_extension_for_pytorch'); assert not any(n == b or n.startswith(b + '.') for n in sys.modules for b in banned)"
git diff --check
```

Expected: every command exits 0. The focused foundation matrix should report 14 passed, the existing runtime regression matrix should have zero failures, the full suite should have zero failures, and the import guard should produce no output.

- [ ] **Step 6: Prove live runtime selection is unchanged**

Run:

```powershell
git diff HEAD~6 -- nexus/runtimes/registry.py nexus/runtimes/__init__.py
$hits = rg -n 'accelerator-pack|WorkerRuntimeAdapter' nexus/runtimes/registry.py nexus/runtimes/__init__.py
if ($LASTEXITCODE -eq 0) { $hits; throw 'live runtime registry changed' }
if ($LASTEXITCODE -ne 1) { throw 'runtime registry scan failed' }
```

Expected: both commands produce no output. If the execution branch contains unrelated prior edits to these files, compare against the isolated worktree base commit instead of `HEAD~6` and record the exact base SHA.

- [ ] **Step 7: Scope-check and commit Task 7**

Run:

```powershell
git add nexus/runtimes/worker.py nexusnet/runtime/accelerator_packs/__init__.py tests/runtime/accelerator_packs/test_worker_runtime_adapter.py
git diff --cached --check
```

Run `gitnexus_detect_changes` with `{"repo":"NexusNet","scope":"staged"}`. Expected: the new worker adapter and package exports only; no existing live selection flow is affected. Then commit:

```powershell
git commit -m "feat: add inactive worker runtime adapter"
```

- [ ] **Step 8: Record exact evidence and stop at the approved boundary**

Record:

- the isolated worktree and branch;
- all seven commit SHAs;
- focused and full test pass/fail counts;
- GitNexus changed symbols, affected flows, and risk for every commit;
- confirmation that global Python and global Torch were not modified;
- confirmation that no vendor runtime module was imported by the core package;
- confirmation that `RuntimeRegistry.adapters` and `RuntimeRegistry.choose` are unchanged;
- the remaining boundary: Windows discovery and installer work has not started.

Do not merge into the integration branch until the task-by-task review and final code review are both approved.

## Plan Self-Review

### Specification coverage

- Vendor-neutral core: Tasks 2-7 use only Pydantic and standard-library process APIs; the final import guard rejects vendor runtime imports.
- One hardware graph: Task 1 extracts the existing models into a dependency-free shared module, re-exports the identical classes from the old schema path, and preserves old fields.
- Capability identity: Tasks 1-3 model APIs, formats, workloads, modes, and device predicates without vendor dispatch branches.
- Process isolation: Tasks 5-7 provide bounded framing, subprocess supervision, timeouts, termination, and an adapter boundary.
- Honest degradation: compatibility and execution failures return stable reason codes; forced modes never silently become CPU.
- Independent lifecycle: Task 4 persists pack versions, active/previous pointers, quarantine, and atomic rollback.
- Sanitization: registry, codec, supervisor, and adapter tests prove errors do not echo private raw content.
- Current runtime safety: Task 7 explicitly proves the live registry and selector remain unchanged.

### Type and name consistency

- Public `Both` is represented only as `ExecutionMode.HYBRID`; `WorkerRuntimeAdapter._execution_mode` performs the single `both` to `hybrid` translation.
- `HardwareNode.accelerator_apis`, `DeviceMatch.accelerator_apis`, and `RuntimePackManifest.accelerator_apis` all consume the same `AcceleratorBackend` literal.
- Registry methods consistently address a pack version with `(pack_id, version)` and persist keys as `pack_id@version`.
- Supervisor requests and protocol frames use the same `request_id`, `WorkerOperation`, `ExecutionMode`, and terminal-frame semantics.
- The worker adapter is deliberately named `WorkerRuntimeAdapter` and is never added to `RuntimeRegistry.adapters` in this plan.

### Scope omissions by design

- Hardware probes, Windows ML acquisition, pack downloads, signature verification, venv construction, and private Python installation belong to the next installer/discovery plan.
- CPU, CUDA, HIP, XPU, SYCL, OpenVINO, Vulkan, DirectML, Windows ML, and llama.cpp execution binaries are not installed or invoked here.
- Correctness self-tests and calibration evidence are protocol operations only in this slice; their vendor implementations and QES eligibility effects belong to later plans.
- Live routing, training, assimilation execution, and model-weight behavior remain unchanged.

## Execution Handoff

Plan execution begins only after choosing one of the Superpowers execution workflows. The recommended path is subagent-driven development because each task has an independent red-green-review-commit gate and Task 1 has a high transitive blast radius.
