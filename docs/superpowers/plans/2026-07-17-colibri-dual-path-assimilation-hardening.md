# Colibri Dual-Path Assimilation Hardening Implementation Plan

> **For NexusNet:** Execute this plan with the `superpowers:test-driven-development`, `superpowers:systematic-debugging`, and `superpowers:verification-before-completion` skills.

**Goal:** Make the Colibri-derived tiered MoE architecture intake executable on CPU/RAM while adding an honest per-inference GPU `off`/`on`/`auto` control whose decision is identity-bound and evidence-gated.

**Architecture:** Extend the metadata-only architecture plan into an immutable executable residency plan. `off` forces CPU/RAM, `on` requires an executable GPU runtime and fails closed when unavailable, and `auto` selects GPU only after an exact-profile benefit has been verified. The tiered expert backend may execute hot experts on a selected device while returning results to the caller device. Residency telemetry is bound to the architecture plan, execution plan, model fingerprint, model digest, hardware profile, and GPU decision so evidence cannot be relabeled across models or plans.

**Tech stack:** Python 3.12, PyTorch, pytest, GitNexus, dataclasses, SHA-256 identity payloads.

---

## Task 1: Lock policy and plan identity with failing tests

**Files:**

- Modify: `tests/runtime/test_moe_architecture_intake.py`
- Modify: `nexusnet/runtime/moe_residency/architecture.py`
- Modify: `nexusnet/runtime/moe_residency/schemas.py`

- [ ] Add tests proving storage bandwidth and hardware/profile facts change `plan_id`.
- [ ] Add tests for `GPUAccelerationPolicy(mode="off" | "on" | "auto")`.
- [ ] Prove `off` produces no GPU slots, `on` blocks without an executable GPU runtime, and `auto` stays CPU until exact-profile benefit is verified.
- [ ] Prove admitted architecture plans convert to `MoEResidencyPlan` without changing `plan_id`, while blocked or identity-less plans refuse conversion.
- [ ] Run the focused test file and confirm the new assertions fail for missing behavior:

```powershell
pytest tests/runtime/test_moe_architecture_intake.py -q
```

- [ ] Implement only the policy, full hardware-profile hash, plan fields, and executable conversion needed to pass.
- [ ] Rerun the focused test file and require green.

## Task 2: Execute through CPU/RAM or selected GPU without silent fallback

**Files:**

- Modify: `tests/runtime/test_moe_residency.py`
- Modify: `nexusnet/runtime/moe_residency/execution.py`
- Modify: `nexusnet/runtime/moe_residency/schemas.py`

- [ ] Add a CPU-only end-to-end test that converts an architecture plan, attaches it to a native MoE layer, and matches resident inference output.
- [ ] Add a test that GPU `on` fails before model mutation when CUDA execution is unavailable.
- [ ] Add a CUDA-only equivalence test guarded by `torch.cuda.is_available()`; it must compare GPU-hot-tier output with the resident reference.
- [ ] Run the focused runtime tests and confirm the new behavior is red:

```powershell
pytest tests/runtime/test_moe_residency.py -q
```

- [ ] Add an optional expert execution device to `TieredSwiGLUExecutionBackend` and its factories.
- [ ] Move only selected expert inputs/weights to that device and return expert output to the caller device.
- [ ] Validate the plan/device contract in `attach_tiered_moe_runtime`; never turn GPU `on` into a silent CPU fallback.
- [ ] Rerun the focused runtime tests and require green, allowing only the explicit CUDA capability skip on this CPU-only Torch build.

## Task 3: Prevent cross-plan evidence and stale model evidence

**Files:**

- Modify: `tests/runtime/test_moe_architecture_intake.py`
- Modify: `tests/runtime/test_evolutionary_inference_system.py`
- Modify: `nexusnet/runtime/moe_residency/architecture.py`
- Modify: `nexusnet/runtime/evolutionary_inference/system.py`

- [ ] Add tests proving telemetry cannot be relabeled and must match architecture plan, execution plan, model fingerprint, model digest, hardware profile, and GPU decision.
- [ ] Add a regression test proving attaching a new model clears prior residency evidence.
- [ ] Add a regression test proving cross-model/cross-execution-plan telemetry is rejected.
- [ ] Run both focused files and confirm the regressions fail for the expected causes:

```powershell
pytest tests/runtime/test_moe_architecture_intake.py tests/runtime/test_evolutionary_inference_system.py -q
```

- [ ] Remove the telemetry relabel path, enforce identity checks, and clear residency evidence on model attachment.
- [ ] Expose the active GPU mode/decision through sanitized residency evidence and status.
- [ ] Rerun the focused tests and require green.

## Task 4: Verify the bounded assimilation slice

**Files:**

- Verify only the files listed above plus `nexusnet/runtime/moe_residency/__init__.py` if exports change.

- [ ] Run syntax compilation:

```powershell
python -m compileall nexusnet/runtime/moe_residency nexusnet/runtime/evolutionary_inference
```

- [ ] Run the focused assimilation matrix:

```powershell
pytest tests/runtime/test_moe_residency.py tests/runtime/test_moe_architecture_intake.py tests/runtime/test_evolutionary_inference_system.py tests/test_video_assimilation_targets.py -q
```

- [ ] Record runtime capability evidence:

```powershell
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.device_count())"
nvidia-smi --query-gpu=name,memory.total,memory.free,compute_cap --format=csv,noheader
```

- [ ] Run whitespace and patch checks:

```powershell
git diff --check
git diff -- nexusnet/runtime/moe_residency nexusnet/runtime/evolutionary_inference/system.py tests/runtime/test_moe_residency.py tests/runtime/test_moe_architecture_intake.py tests/runtime/test_evolutionary_inference_system.py docs/superpowers/plans/2026-07-17-colibri-dual-path-assimilation-hardening.md
```

- [ ] Run `gitnexus_detect_changes()` and attribute any repository-wide risk separately from this bounded slice.
- [ ] Do not claim GPU speedup unless a CUDA-enabled runtime executes the CUDA equivalence/benchmark path on the exact hardware profile.
