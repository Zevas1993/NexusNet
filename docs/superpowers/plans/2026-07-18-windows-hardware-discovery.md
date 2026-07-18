# Windows Multi-Device Hardware Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to execute this plan task-by-task, with `superpowers:test-driven-development` for every production change.

**Goal:** Replace Windows' CUDA-only accelerator scan with sanitized, dependency-free multi-device discovery that independently represents NVIDIA, AMD, and Intel GPUs, preserves CPU discovery when probes fail, and never promotes detected hardware to a verified runtime route.

**Architecture:** Keep `HardwareCapabilityDiscoverer` platform-neutral and delegate Windows accelerator enumeration to a new `windows_hardware` adapter. The adapter uses Windows CIM for device identity and optional `nvidia-smi` evidence to augment NVIDIA devices without duplicating them. A new vendor-neutral graph observation records probe success or failure without mislabeling CIM as a runtime backend. Linux and macOS keep their existing probes unchanged.

**Tech stack:** Python 3.10+, Pydantic v2, standard-library JSON/hash/subprocess APIs, Windows PowerShell/CIM, pytest, GitNexus.

## Global Constraints

- Target Windows 11 x64 desktop only. Linux porting, Windows ARM64, mobile, edge, NPU, runtime-pack installation, and live routing are separate slices.
- NexusNet core must not import Torch CUDA, Torch XPU, ROCm, OpenVINO, DirectML, Windows ML, ONNX Runtime, WMI Python packages, or vendor DLLs.
- Preserve CPU, RAM, and storage nodes even if every accelerator probe fails.
- Represent each physical Windows video controller independently; mixed Intel integrated and NVIDIA discrete GPUs must not collapse into one node.
- Store no raw PNP device path, hostname, username, environment variable, private filesystem path, or unbounded command output. Stable device references are hashes of sanitized local identity material.
- A CIM observation establishes only `detected`. It must not populate `accelerator_apis` or claim CUDA, HIP, XPU, SYCL, OpenVINO, Vulkan, DirectML, or Windows ML availability.
- A successful `nvidia-smi` probe establishes only detected CUDA-driver evidence. It may populate the CUDA API and observed memory/driver fields, but never `compatible`, `verified`, or `supported`.
- One failed probe must not erase devices found by another probe. Every probe emits a sanitized success/failure observation.
- Do not change `RuntimeRegistry.adapters`, `RuntimeRegistry.choose`, QES, Inference Economy routing, provider selection, installer scripts, global Python/Torch, model weights, or training behavior.
- Work only in `F:\NexusNet\NexusNet\.worktrees\windows-hardware-discovery` on `codex/windows-hardware-discovery`.
- Use TDD: write one focused test, run it red for the expected missing behavior, add the minimum implementation, and rerun green.
- Before editing an existing function, method, or class, run upstream GitNexus impact analysis and report HIGH/CRITICAL risk. Before every commit, stage only named files, run `git diff --cached --check`, and run `gitnexus_detect_changes` with `scope: "staged"`.

## File Responsibility Map

- `nexusnet/runtime/hardware_contracts.py`: add a vendor-neutral probe observation and an additive graph field.
- `nexusnet/runtime/evolutionary_inference/schemas.py`: preserve compatibility re-exports for the shared hardware contracts.
- `nexusnet/runtime/evolutionary_inference/windows_hardware.py`: Windows-only command construction, bounded parsing, normalization, deduplication, and NVIDIA augmentation.
- `nexusnet/runtime/evolutionary_inference/hardware.py`: delegate Windows accelerator discovery while preserving portable nodes and non-Windows probes.
- `tests/runtime/test_windows_hardware_discovery.py`: contract, parser, failure, mixed-device, deduplication, and integration evidence.

---

### Task 1: Add an honest platform-probe observation contract

**Files:**

- Modify: `nexusnet/runtime/hardware_contracts.py`
- Modify: `nexusnet/runtime/evolutionary_inference/schemas.py`
- Create: `tests/runtime/test_windows_hardware_discovery.py`

**Interface:**

```python
class HardwareProbeObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    probe_id: str
    available: bool
    reason_code: str
    device_count: int = Field(default=0, ge=0)
    verification_state: VerificationState = "detected"
    probe_source: str


class HardwareCapabilityGraph(BaseModel):
    # existing fields remain unchanged
    discovery_observations: list[HardwareProbeObservation] = Field(default_factory=list)
```

- [ ] Write a test that constructs a graph with a failed `windows-cim-video-controller` observation and asserts exact JSON projection plus `extra="forbid"` behavior.
- [ ] Run `python -m pytest tests/runtime/test_windows_hardware_discovery.py -q` and confirm RED because `HardwareProbeObservation` is absent.
- [ ] Add the shared contract and re-export it from `evolutionary_inference.schemas`; do not change any existing field defaults or validation.
- [ ] Rerun the new test GREEN, then run `tests/runtime/accelerator_packs/test_device_schema.py` and `tests/runtime/test_evolutionary_inference_foundation.py`.
- [ ] Stage only the three named files, run cached diff checks and staged GitNexus change detection, then commit.

---

### Task 2: Implement dependency-free Windows CIM enumeration and CUDA augmentation

**Files:**

- Create: `nexusnet/runtime/evolutionary_inference/windows_hardware.py`
- Modify: `tests/runtime/test_windows_hardware_discovery.py`

**Public module interface:**

```python
@dataclass(frozen=True)
class WindowsAcceleratorDiscovery:
    nodes: tuple[HardwareNode, ...]
    adapters: tuple[AcceleratorAdapterObservation, ...]
    observations: tuple[HardwareProbeObservation, ...]


def discover_windows_accelerators(command_runner: CommandRunner) -> WindowsAcceleratorDiscovery:
    ...
```

**CIM command:** invoke `powershell.exe` with `-NoLogo`, `-NoProfile`, `-NonInteractive`, `-ExecutionPolicy Bypass`, and a fixed script that selects only `Name`, `PNPDeviceID`, `DriverVersion`, `AdapterRAM`, `VideoProcessor`, `AdapterCompatibility`, `Status`, and `ConfigManagerErrorCode`, then emits compressed JSON. Use a 3-second runner timeout and cap accepted stdout at 1 MiB before parsing.

**Normalization rules:**

```python
vendor_id = VEN_([0-9A-Fa-f]{4}) from PNPDeviceID, lower-cased
device_id = DEV_([0-9A-Fa-f]{4}) from PNPDeviceID, lower-cased
node_id = "gpu:windows:" + sha256(canonical_identity.encode()).hexdigest()[:16]
backend = "portable" for CIM-only devices
verification_state = "detected"
probe_source = "windows-cim"
reason_codes = ["windows-cim-detected", "runtime-unverified"]
```

Use the raw PNP identifier only as hash input; never retain or serialize it. Use `AdapterRAM` as both `memory_bytes` and `dedicated_memory_bytes` only when it parses as a positive integer, with `memory-os-reported` in reason codes. Sanitize labels to 120 characters. Deduplicate identical stable node IDs.

**NVIDIA augmentation:** retain the existing three-column `nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits` contract. Match results to unmatched CIM NVIDIA nodes by normalized name, then by stable NVIDIA ordinal. Preserve the CIM node ID, vendor/device identity, and architecture; replace memory/driver evidence with the CLI values, set `backend="cuda"`, `accelerator_apis=["cuda"]`, `probe_source="windows-cim+nvidia-smi"`, and reason codes `windows-cim-detected`, `cuda-driver-detected`, `runtime-pack-unverified`. If CIM is unavailable, create sanitized `gpu:windows:nvidia-smi:<index>` fallback nodes. Never create a duplicate GPU for one matched device.

- [ ] Add a RED test for mixed Intel + NVIDIA CIM JSON: two distinct nodes, lower-case PCI IDs, stable hashed IDs, no raw PNP path, no inferred accelerator APIs, and detected-only state.
- [ ] Add the minimum CIM parser and rerun that test GREEN.
- [ ] Add a RED test showing `nvidia-smi` augments the matching CIM NVIDIA node without duplicating it while the Intel device stays portable/unverified.
- [ ] Implement minimal NVIDIA augmentation and rerun GREEN.
- [ ] Add RED failure tests for malformed/oversized CIM output, missing PowerShell, timed-out CIM, and `nvidia-smi`-only fallback. Assert sanitized `HardwareProbeObservation` reason codes and preservation of successful evidence from the other probe.
- [ ] Implement bounded, fail-soft command handling and rerun all new tests GREEN.
- [ ] Run vendor-import and sensitive-string guards over the new module.
- [ ] Stage only the two named files, run cached diff checks and staged GitNexus change detection, then commit.

---

### Task 3: Delegate Windows discovery from the platform-neutral graph builder

**Files:**

- Modify: `nexusnet/runtime/evolutionary_inference/hardware.py`
- Modify: `tests/runtime/test_windows_hardware_discovery.py`
- Modify only if an existing expectation requires truthful evidence vocabulary: `tests/runtime/test_evolutionary_inference_foundation.py`

**Integration behavior:**

```python
if self._system_name.casefold() == "windows":
    windows = discover_windows_accelerators(self._command_runner)
    accelerator_results = [(list(windows.nodes), list(windows.adapters))]
    discovery_observations.extend(windows.observations)
    legacy_probes = (self._probe_rocm, self._probe_metal)
else:
    legacy_probes = (self._probe_cuda, self._probe_rocm, self._probe_metal)
```

The exact code may be simplified, but Windows must run CIM plus one CUDA CLI probe, append one RAM-to-GPU transfer link per unique node, retain the existing ROCm and Metal unsupported-platform observations, and attach platform probe observations to the graph. Non-Windows command order and behavior must remain unchanged.

- [ ] Add a RED integration test through `HardwareCapabilityDiscoverer` for mixed Intel/NVIDIA Windows hardware. Assert CPU/RAM/storage plus two GPU nodes, unique links, CIM/CUDA observations, and no state above `detected`.
- [ ] Run upstream GitNexus impact for `HardwareCapabilityDiscoverer.discover` immediately before editing it; stop and warn if the result rises to HIGH/CRITICAL or names live routing flows.
- [ ] Add minimal Windows-only delegation and rerun the integration test GREEN.
- [ ] Add a RED integration test where PowerShell and `nvidia-smi` fail; assert CPU/RAM/storage survive, no fake GPU exists, and both sanitized failures are present.
- [ ] Complete fail-soft integration and rerun GREEN.
- [ ] Run the full affected regression matrix:

```powershell
F:\NexusNet\.venvs\nexusnet-cuda-py311\Scripts\python.exe -m pytest tests/runtime/test_windows_hardware_discovery.py tests/runtime/test_evolutionary_inference_foundation.py tests/runtime/test_evolutionary_inference_system.py tests/runtime/accelerator_packs tests/test_model_registry.py -q
```

- [ ] Run a live discovery smoke test on the current Windows machine. Record observed devices and evidence states; do not call an accelerator verified or supported.
- [ ] Confirm no live registry/selector/installer files changed and no vendor runtime import entered core.
- [ ] Stage only the named files, run `git diff --cached --check`, staged GitNexus change detection, and commit.

---

### Final Review and Verification

- [ ] Generate one full branch review package from base `2952f6ea3f3674a3ee640d1e0d401c20da7ea929` to HEAD and dispatch an independent final reviewer.
- [ ] Resolve every Critical or Important finding with focused TDD and re-review.
- [ ] Rerun the full affected regression matrix fresh after the final change.
- [ ] Run GitNexus compare-scope change detection, `git diff --check`, vendor-import guard, live-registry invariance check, and `git status --short`.
- [ ] Use `superpowers:finishing-a-development-branch`; preserve the worktree until the user chooses merge, PR, keep, or discard.
