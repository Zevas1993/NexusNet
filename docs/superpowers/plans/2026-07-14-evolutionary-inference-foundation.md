# Evolutionary Inference Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a portable, restart-safe inference foundation that discovers the current host, performs bounded calibration, fingerprints model execution needs, registers available inference primitives, and emits a read-only feasibility artifact through the existing inference-architecture scorecard.

**Architecture:** Add a self-contained `nexusnet.runtime.evolutionary_inference` package. Its orchestrator composes hardware discovery, bounded calibration, model fingerprinting, primitive registration, feasibility evaluation, and atomic JSON evidence persistence. The existing `InferenceArchitectureRegistry` owns one orchestrator and exposes its status without changing live routing or promotion policy.

**Tech Stack:** Python 3.11, Pydantic v2, standard-library platform/process/filesystem APIs, pytest, FastAPI TestClient through the existing scorecard endpoint.

## Global Constraints

- Preserve the parent checkout's unrelated dirty files; work only in the isolated feature worktree.
- Follow red-green-refactor for every production behavior.
- Keep discovery optional and fail-soft: absent CUDA, ROCm, or Metal tooling produces explicit unavailable adapter evidence, never startup failure.
- Never persist hostnames, usernames, environment variables, command output beyond the allowlisted adapter fields, model paths, prompt text, or model content.
- Calibration must be bounded by explicit byte/iteration/time limits and must not allocate GPU memory.
- The first slice is observation and shadow feasibility only. It must not mutate runtime routing, promotion state, model weights, or provider selection.
- Before editing existing methods, honor recorded GitNexus impact: class-level HIGH due to imports; target methods LOW. Keep the patch limited to `InferenceArchitectureRegistry.__init__` and `scorecard`.
- Verification must include focused tests, existing inference/cache/MoE/status tests, `git diff --check`, and GitNexus change detection.

---

### Task 1: Define sanitized contracts and deterministic model fingerprints

**Files:**

- Create: `nexusnet/runtime/evolutionary_inference/schemas.py`
- Create: `nexusnet/runtime/evolutionary_inference/fingerprints.py`
- Create: `nexusnet/runtime/evolutionary_inference/__init__.py`
- Test: `tests/runtime/test_evolutionary_inference_foundation.py`

- [ ] Add failing tests that validate strict schemas, deterministic synthetic fingerprints, rejected unknown fields, and absence of raw model paths/content.
- [ ] Run `python -m pytest tests/runtime/test_evolutionary_inference_foundation.py -q` and confirm import/behavior failures.
- [ ] Implement Pydantic contracts with `extra="forbid"`:

```python
class HardwareCapabilityGraph(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    host_fingerprint: str
    collected_at: datetime
    nodes: list[HardwareNode]
    links: list[HardwareLink]
    calibration: list[CalibrationMetric]

class ModelExecutionFingerprint(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    fingerprint_id: str
    architecture_family: str
    parameter_count: int
    tensor_bytes: int
    quantization: str
    context_length: int
    layer_count: int
    expert_count: int = 0
    experts_per_token: int = 0
    modalities: list[str]
    source_kind: Literal["trusted-synthetic", "metadata"]
```

- [ ] Implement `synthetic_model_fingerprint()` from a fixed allowlisted fixture and `fingerprint_from_metadata()` from normalized execution metadata only.
- [ ] Run the focused test and confirm green.

### Task 2: Discover portable hardware and optional accelerators

**Files:**

- Create: `nexusnet/runtime/evolutionary_inference/hardware.py`
- Modify: `tests/runtime/test_evolutionary_inference_foundation.py`

- [ ] Add failing tests using injected command runners for:
  - CPU, total RAM, and storage nodes on every platform.
  - CUDA adapter parsing of allowlisted `nvidia-smi` CSV fields.
  - ROCm and Metal adapters degrading to explicit unavailable observations.
  - Stable sanitized host fingerprints that contain no hostname or username.
- [ ] Run the focused test and confirm failures.
- [ ] Implement `HardwareCapabilityDiscoverer` with injected platform, disk, memory, and subprocess dependencies.
- [ ] Use standard-library fallbacks for memory capacity and `shutil.disk_usage()` for storage.
- [ ] Bound adapter commands with short timeouts and normalize failures to reason codes such as `tool-not-found`, `timeout`, or `unsupported-platform`.
- [ ] Run the focused test and confirm green.

### Task 3: Add bounded host calibration

**Files:**

- Create: `nexusnet/runtime/evolutionary_inference/calibration.py`
- Modify: `tests/runtime/test_evolutionary_inference_foundation.py`

- [ ] Add failing tests asserting memory-copy and representative-compute metrics, positive finite values, byte/iteration bounds, and no GPU allocation path.
- [ ] Run the focused test and confirm failures.
- [ ] Implement `BoundedHostCalibrator` with explicit limits:

```python
class CalibrationLimits(BaseModel):
    memory_bytes: int = Field(default=4 * 1024 * 1024, le=16 * 1024 * 1024)
    memory_rounds: int = Field(default=3, le=8)
    compute_iterations: int = Field(default=20_000, le=100_000)
```

- [ ] Measure `memory_copy_gib_s` with preallocated byte arrays and `cpu_scalar_mops` with deterministic arithmetic; include duration and sample count.
- [ ] Run the focused test and confirm green.

### Task 4: Register reusable inference primitives and evaluate feasibility

**Files:**

- Create: `nexusnet/runtime/evolutionary_inference/primitives.py`
- Create: `nexusnet/runtime/evolutionary_inference/feasibility.py`
- Modify: `tests/runtime/test_evolutionary_inference_foundation.py`

- [ ] Add failing tests proving the default registry contains:
  - `portable.cpu-reference` as an always-available fallback.
  - `moe.selective-residency` bound to the existing `nexusnet.runtime.moe_residency` implementation.
  - Explicit requirements, compatible model families, evidence state, and no per-model policy mutation.
- [ ] Add failing feasibility tests for dense CPU fallback, MoE selective residency on RAM-constrained accelerator hosts, and infeasible capacity with human-readable reason codes.
- [ ] Run the focused test and confirm failures.
- [ ] Implement `InferencePrimitiveRegistry.default()` and deterministic lookup/list APIs.
- [ ] Implement `CandidateFeasibilityEvaluator.evaluate(graph, fingerprint, registry)` returning a shadow-only candidate set, selected candidate ID, blockers, and confidence.
- [ ] Keep selection conservative: availability and capacity are mandatory; benchmark evidence can raise confidence but cannot promote a primitive.
- [ ] Run the focused test and confirm green.

### Task 5: Persist atomic, restart-safe foundation evidence

**Files:**

- Create: `nexusnet/runtime/evolutionary_inference/foundation.py`
- Modify: `nexusnet/runtime/evolutionary_inference/__init__.py`
- Modify: `tests/runtime/test_evolutionary_inference_foundation.py`

- [ ] Add failing tests that establish a baseline into a temporary artifact directory, inspect JSON sanitation, instantiate a second orchestrator, and prove the same artifact is restored after restart.
- [ ] Add a failing corruption test proving malformed persisted JSON yields an honest degraded state rather than an exception or fabricated success.
- [ ] Run the focused test and confirm failures.
- [ ] Implement `EvolutionaryInferenceFoundation.establish_baseline()` to compose discovery, calibration, synthetic fingerprinting, primitive registration, and feasibility.
- [ ] Persist `artifacts/runtime/evolutionary-inference/foundation-v1.json` via write-to-temp plus `Path.replace()`.
- [ ] Implement `status(ensure_baseline: bool = False)` with states `uninitialized`, `live-evidence`, and `degraded-evidence`; never silently regenerate corrupted evidence unless explicitly asked to establish a baseline.
- [ ] Run the focused test and confirm green.

### Task 6: Expose read-only status through the existing runtime surface

**Files:**

- Modify: `nexusnet/runtime/inference_architecture.py`
- Modify: `tests/test_inference_architecture_registry.py`

- [ ] Add a failing registry test asserting `scorecard()["evolutionary_inference_foundation"]` contains live evidence, primitive IDs, feasibility, artifact reference, and `policy_mutation_allowed is False`.
- [ ] Extend the existing FastAPI black-box test to assert the same field is visible from `/ops/brain/canon/inference-architecture` and survives a second app construction against the same project root.
- [ ] Run `python -m pytest tests/test_inference_architecture_registry.py -q` and confirm failures.
- [ ] In `InferenceArchitectureRegistry.__init__`, construct `EvolutionaryInferenceFoundation(artifacts_dir=self.artifacts_dir)`.
- [ ] In `scorecard`, add:

```python
"evolutionary_inference_foundation": self.evolutionary_foundation.status(
    ensure_baseline=self.artifacts_dir is not None
),
```

- [ ] Do not change the plan endpoint, live runtime selectors, or promotion gates.
- [ ] Run focused registry and foundation tests and confirm green.

### Task 7: Verify scope and integrate

**Files:**

- Verify all files above.

- [ ] Run:

```powershell
python -m pytest tests/runtime/test_evolutionary_inference_foundation.py tests/test_inference_architecture_registry.py -q
python -m pytest tests/test_cache_ledger.py tests/runtime/test_moe_residency.py tests/e2e/test_status_api.py -q
git diff --check
```

- [ ] Review persisted fixture evidence to confirm it contains no hostname, username, paths outside the artifact reference, prompt text, or model content.
- [ ] Run GitNexus change detection for all changes and inspect affected processes/symbols.
- [ ] Commit the focused feature branch with an evidence-backed message.
- [ ] Merge into `codex/all-worktrees-integration` while preserving the parent checkout's unrelated tracked and untracked changes.
- [ ] Rerun the focused matrix from the integration checkout after merge.

## Plan Self-Review

- The plan implements the spec's first independent project, not the full six-project evolutionary loop.
- It assimilates existing MoE residency through a shared primitive contract rather than duplicating or wrapping its execution code.
- It improves system-wide decision inputs, not per-model tuning: fingerprints are portable workload descriptors and the primitive registry is global.
- It handles limited VRAM indirectly in this slice by modeling RAM/accelerator capacity and exposing selective residency feasibility; transfer scheduling, pinned staging, and overlap remain a later measured primitive project.
- It provides real runtime-visible, restart-safe evidence while keeping live policy mutation explicitly disabled.

## Execution Status

- [x] Task 1: strict contracts and deterministic model fingerprints.
- [x] Task 2: portable hardware discovery and fail-soft accelerator adapters.
- [x] Task 3: bounded CPU and memory calibration.
- [x] Task 4: shared primitive registry and shadow feasibility.
- [x] Task 5: atomic, restart-safe evidence.
- [x] Task 6: additive runtime scorecard integration.
- [x] Task 7: final verification, commit, and local integration merge.
