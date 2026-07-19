# Windows Accelerator Completion Train Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This train is intentionally sequential; do not dispatch parallel implementers.

**Goal:** Complete the seven remaining Windows 11 accelerator-pack slices from private installation through evidence-driven live selection, with a real CPU/NVIDIA proof on the current machine and honest unverified gates for unavailable AMD/Intel hardware.

**Architecture:** Keep vendor dependencies outside NexusNet core in versioned worker packs. A dependency-free pack manager acquires and verifies artifacts, builds isolated environments, and activates only packs whose worker health and correctness evidence passes. The live runtime registry consumes verified route decisions from a calibration-aware selector; it never infers usability from hardware detection alone.

**Tech Stack:** Python 3.10+, Pydantic v2, standard-library `hashlib`, `urllib`, `venv`, `subprocess`, and atomic filesystem APIs; PowerShell 7/Windows PowerShell; existing NexusNet worker JSON protocol; pytest; GitNexus; optional isolated Torch/ONNX/llama.cpp workers.

## Global Constraints

- Target Windows 11 x64 desktop only. Linux, Windows ARM64, mobile, edge, and NPU work remain later adapters.
- Do not modify global Python, global Torch, machine-wide `PATH`, or unrelated environments.
- Core must not import Torch CUDA, Torch XPU, ROCm, OpenVINO, DirectML, Windows ML, ONNX Runtime, or vendor DLLs.
- Every pack artifact must have an allowlisted HTTPS origin, exact byte size ceiling, SHA-256 digest, license/provenance metadata, and a signature reference when the publisher supplies one.
- No pack becomes live from detection or compatibility alone. Activation requires artifact verification, device compatibility, worker health, correctness, and policy admission.
- `CPU` forces a verified CPU route; `GPU` forces a verified accelerator route; `Both` maps to `hybrid` only for proven hybrid offload; `Auto` ranks only verified routes.
- No forced mode silently falls back. `Auto` may select CPU and must emit sanitized reasons.
- AMD and Intel implementations remain `unverified` on this NVIDIA-only machine until the full representative real-device release gate is supplied.
- Tests must use bounded local fixtures. Network downloads occur only in explicit live-smoke commands after catalog and digest review.
- Use TDD for every production behavior. Before editing an existing symbol, run upstream GitNexus impact and warn on HIGH/CRITICAL. Before each commit run focused tests, `git diff --cached --check`, and staged GitNexus change detection.

## File Responsibility Map

- `nexusnet/runtime/accelerator_packs/acquisition.py`: bounded artifact download/copy, origin policy, digest verification, and atomic staging.
- `nexusnet/runtime/accelerator_packs/installer.py`: private venv/native-directory construction, health/correctness gates, activation, repair, rollback, and uninstall.
- `nexusnet/runtime/accelerator_packs/catalog.py`: dependency-free built-in CPU/NVIDIA/Windows ML/AMD/Intel pack candidates and isolated environment locks.
- `nexusnet/runtime/accelerator_packs/workers/`: out-of-process reference, Torch, ONNX/Windows ML, and native connector worker entry points.
- `nexusnet/runtime/accelerator_packs/route_selection.py`: verified route evidence, calibration keys, invalidation, forced-mode semantics, and `Auto` ranking.
- `nexusnet/runtime/accelerator_packs/lifecycle.py`: crash counters, circuit breaker, quarantine, repair, update, rollback, retention, provenance, and SBOM receipts.
- `nexus/runtimes/registry.py`: register only active verified worker adapters and honor explicit execution mode.
- `nexusnet/runtime/registry.py`: project selected pack/evidence into the brain runtime plan without installing packs.
- `nexus/api/app.py` and `ui/control-panel/app.js`: sanitized runtime-pack status and `Auto`/`CPU`/`GPU`/`Both` operator control.
- `install/windows/bootstrap.ps1` and `nexusnet/cli/runtime_packs.py`: private core setup and explicit plan/install/repair/uninstall commands.

---

### Task 1: Private Windows environment and adaptive pack acquisition

**Files:**
- Create: `nexusnet/runtime/accelerator_packs/acquisition.py`
- Create: `nexusnet/runtime/accelerator_packs/installer.py`
- Create: `nexusnet/cli/runtime_packs.py`
- Modify: `nexusnet/runtime/accelerator_packs/__init__.py`
- Modify: `pyproject.toml`
- Modify: `install/windows/bootstrap.ps1`
- Test: `tests/runtime/accelerator_packs/test_acquisition.py`
- Test: `tests/runtime/accelerator_packs/test_installer.py`
- Test: `tests/runtime/accelerator_packs/test_windows_bootstrap.py`

**Interfaces:**
- Consumes: `RuntimePackManifest`, `ArtifactDescriptor`, `RuntimePackRegistry`, `PackCompatibilityEvaluator`, and `WorkerSupervisor`.
- Produces: `AcquisitionPolicy`, `AcquiredArtifact`, `ArtifactAcquirer.acquire()`, `PrivateEnvironmentBuilder.build()`, and `PackInstaller.install()/repair()/uninstall()`.

- [x] Write failing tests proving allowlisted HTTPS/local-fixture acquisition, byte ceilings, SHA-256 enforcement, partial-download isolation, disk-budget rejection, no `--system-site-packages`, atomic activation, previous-version preservation, and sanitized receipts.
- [x] Run `python -m pytest tests/runtime/accelerator_packs/test_acquisition.py tests/runtime/accelerator_packs/test_installer.py tests/runtime/accelerator_packs/test_windows_bootstrap.py -q`; confirm failures are missing interfaces/placeholder bootstrap behavior.
- [x] Run GitNexus impact before changing the pack exports, project scripts, or bootstrap entry points; stop and report HIGH/CRITICAL results.
- [x] Implement bounded acquisition with a `.partial` staging file, incremental SHA-256, exact maximum bytes, allowlisted origins, `os.replace` promotion, and cleanup on every failure.
- [x] Implement private environment construction with `python -m venv` without system-site packages, locked commands, constrained environment variables, and install roots restricted beneath a NexusNet-owned directory.
- [x] Implement installer orchestration: register manifest, acquire, transition through lifecycle states, build, start worker, run `health` and `self_test`, activate only on pass, and quarantine/rollback on failure.
- [x] Replace the placeholder PowerShell bootstrap with architecture checks, bundled/private Python selection, clean core venv creation, editable developer versus built end-user install, and explicit pack-plan output; add the `nexusnet-runtime-packs` CLI entry point.
- [x] Rerun the focused tests, the existing accelerator-pack suite, and guards proving global interpreter/package state and machine `PATH` are unchanged.
- [x] Stage only Task 1 files, run cached diff/GitNexus checks, and commit `feat(runtime): add private pack acquisition and installer` (`cadc9cde`).

### Task 2: CPU reference and NVIDIA CUDA vertical slice

**Files:**
- Create: `nexusnet/runtime/accelerator_packs/catalog.py`
- Create: `nexusnet/runtime/accelerator_packs/workers/__init__.py`
- Create: `nexusnet/runtime/accelerator_packs/workers/reference_worker.py`
- Create: `nexusnet/runtime/accelerator_packs/workers/torch_worker.py`
- Create: `nexusnet/runtime/accelerator_packs/worker_factory.py`
- Test: `tests/runtime/accelerator_packs/test_builtin_catalog.py`
- Test: `tests/runtime/accelerator_packs/test_reference_worker.py`
- Test: `tests/runtime/accelerator_packs/test_torch_worker.py`
- Test: `tests/runtime/accelerator_packs/test_cpu_nvidia_vertical.py`

**Interfaces:**
- Consumes: Task 1 installer, existing worker protocol/supervisor, normalized hardware graph, and `WorkerRuntimeAdapter`.
- Produces: `BuiltInPackCatalog.candidates(graph)`, `WorkerAdapterFactory.from_record()`, a dependency-free CPU reference worker, and an isolated Torch worker whose device code never enters core.

- [x] Write failing catalog tests for one universal CPU candidate plus NVIDIA CUDA only when CUDA-driver evidence exists; detection alone must leave candidates inactive/unverified.
- [x] Write failing protocol tests for `describe`, `health`, `self_test`, `benchmark`, `load_model`, `infer`, `unload_model`, `cancel`, and `shutdown`, including bounded frames and sanitized failures.
- [x] Run the focused tests red and confirm missing catalog/workers/factory are the causes.
- [x] Implement the CPU reference worker with a deterministic numeric model artifact and correctness vector so it performs real load/infer/unload work without importing a vendor runtime.
- [x] Implement the Torch worker with all Torch imports inside the worker process, explicit `cpu` or `cuda` device binding, CUDA availability/device-index checks, memory/correctness receipts, and no raw prompt/model-path logging.
- [x] Implement built-in locked manifests and the worker adapter factory; reject a manifest whose reported backend/device/capabilities exceed its declarations.
- [x] Install and exercise the CPU pack locally. Exercise the NVIDIA pack through the isolated CUDA interpreter on this machine, record exact device/backend evidence, compare its correctness vector with CPU, and prove rollback by activating a deliberately failing successor fixture.
- [x] Run focused tests, the full accelerator-pack suite, and a live CPU/NVIDIA smoke. Do not call the NVIDIA route supported unless install, health, correctness, execution, fallback, and rollback evidence all pass.
- [x] Stage only Task 2 files and evidence, run cached diff/GitNexus checks, and commit `feat(runtime): add CPU and NVIDIA worker packs` (`d8434b75`).

### Task 3: Live `Auto`/`CPU`/`GPU`/`Both` routing and operator toggle

**Files:**
- Create: `nexusnet/runtime/accelerator_packs/route_selection.py`
- Modify: `nexus/runtimes/registry.py`
- Modify: `nexusnet/runtime/registry.py`
- Create: `nexusnet/cli/runtime_mode.py`
- Modify: `pyproject.toml`
- Modify: `nexus/api/app.py`
- Modify: `ui/control-panel/app.js`
- Test: `tests/runtime/accelerator_packs/test_route_selection.py`
- Test: `tests/runtime/accelerator_packs/test_live_registry.py`
- Test: `tests/test_runtime_mode_api.py`

**Interfaces:**
- Consumes: active registry records, worker factory, hardware graph, compatibility decisions, health/correctness evidence, and public `ExecutionMode`.
- Produces: `RouteEvidence`, `RouteRequest`, `RouteDecision`, `VerifiedRouteSelector.select()`, live pack-backed adapters, `/api/runtime-packs/status`, and `/api/runtime-packs/mode`.

- [x] Write failing tests for exact forced-mode behavior, `both` to `hybrid`, no silent fallback, inactive/unhealthy/quarantined exclusion, and `Auto` CPU fallback with sanitized reasons.
- [x] Write failing API/control-surface guards for status projection and four toggle choices without raw install paths or device identities.
- [x] Run all Task 3 tests red for missing selector/live registration/routes.
- [x] Run GitNexus upstream impact for `RuntimeRegistry`, `RuntimeRegistry.choose`, `BrainRuntimeRegistry.core_execution_plan`, the API handlers, and touched control-panel render functions; warn before any HIGH/CRITICAL edit.
- [x] Implement verified route selection as a separate dependency-free component; explicit modes filter before ranking and return stable unavailable errors rather than substituting another mode.
- [x] Extend `RuntimeRegistry` by injection with active verified `WorkerRuntimeAdapter` instances while retaining existing external adapters. Existing static selection remains the fallback only when pack routing was not requested.
- [x] Project sanitized decisions through `BrainRuntimeRegistry`, CLI, API, and control panel. Persist the operator preference under NexusNet-owned configuration with atomic writes.
- [x] Run focused tests plus release-wrapper/runtime/API regression matrices and live CPU/GPU toggle smoke; verify `Both` remains unavailable unless a pack proves hybrid offload.
- [x] Stage only Task 3 files, run cached diff/GitNexus checks, and commit `feat(runtime): connect verified accelerator mode routing` (`1bb32617`).

### Task 4: Windows ML with DirectML and CPU fallback

**Files:**
- Create: `nexusnet/runtime/accelerator_packs/windows_ml.py`
- Create: `nexusnet/runtime/accelerator_packs/workers/onnx_worker.py`
- Modify: `nexusnet/runtime/accelerator_packs/catalog.py`
- Test: `tests/runtime/accelerator_packs/test_windows_ml.py`
- Test: `tests/runtime/accelerator_packs/test_onnx_worker.py`

**Interfaces:**
- Consumes: Windows build/device observations, Task 1 acquisition policy, worker protocol, and route evidence.
- Produces: `WindowsMlProviderObservation`, `WindowsMlCatalog.discover()`, provider-version evidence, and ONNX worker provider validation.

- [x] Re-check only official Microsoft and ONNX Runtime documentation for current Windows ML provider acquisition and package constraints; record exact source URLs/date in the plan evidence.
- [x] Write failing tests for build `<26100`, missing Windows ML runtime, provider enumeration, explicit provider selection, DirectML/CPU fallback, and provider-version evidence invalidation.
- [x] Run Task 4 tests red for missing Windows ML projection and worker.
- [x] Implement dependency-free Windows ML discovery/acquisition orchestration in core; keep ONNX Runtime and provider DLL imports inside the worker.
- [x] Implement ONNX worker `describe/health/self_test/load/infer` with explicit provider lists, no provider-order trust, and sanitized unavailable reasons.
- [x] Add Windows ML, DirectML, and CPU candidates to the catalog without promoting any route until provider/model correctness evidence passes.
- [x] Run focused tests and a live Windows probe. If Windows ML/ONNX prerequisites are absent, record an unavailable receipt and keep CPU/NVIDIA routes intact.
- [x] Stage Task 4 files, run cached diff/GitNexus checks, and commit `feat(runtime): add governed Windows ML pack` (`22f4e87c`).

### Task 5: AMD HIP/Vulkan and Intel SYCL/OpenVINO paths

**Files:**
- Create: `nexusnet/runtime/accelerator_packs/vendor_packs.py`
- Create: `nexusnet/runtime/accelerator_packs/workers/native_worker.py`
- Modify: `nexusnet/runtime/accelerator_packs/catalog.py`
- Test: `tests/runtime/accelerator_packs/test_vendor_packs.py`
- Test: `tests/runtime/accelerator_packs/test_native_worker.py`

**Interfaces:**
- Consumes: detected AMD/Intel nodes, allowlisted artifact catalog, native worker protocol, and compatibility evaluator.
- Produces: capability-driven HIP/Vulkan/SYCL/OpenVINO candidates and a bounded native executable connector.

- [x] Re-check official AMD ROCm Windows, Intel XPU/OpenVINO, and llama.cpp release documentation; encode supported matrices as data, not vendor branches in the selector.
- [x] Write failing tests for AMD HIP eligibility only on supported tuples, Vulkan fallback, Intel SYCL/OpenVINO eligibility, unsupported/legacy devices, mixed-device independence, and no cross-device hybrid assumption.
- [x] Run Task 5 tests red for missing vendor catalog/native worker.
- [x] Implement immutable support-matrix records and capability-driven candidate projection. Unknown hardware remains detected/unverified with a CPU fallback.
- [x] Implement the native worker connector with executable-root confinement, backend/device handshake, model-format checks, deadlines, cancellation, bounded output, and truthful capability reconciliation.
- [x] Add AMD/Intel candidates to the common catalog and selection path. Do not mark them verified on this machine; test fixtures prove gates but do not replace hardware certification.
- [x] Run focused and mixed-device matrices plus vendor-import/privacy guards.
- [x] Stage Task 5 files, run cached diff/GitNexus checks, and commit `feat(runtime): add AMD and Intel pack paths` (`33f1bb4c`).

### Task 6: Isolated PyTorch XPU, supported Windows ROCm, and CPU workers

**Files:**
- Create: `nexusnet/runtime/accelerator_packs/environment_locks.py`
- Modify: `nexusnet/runtime/accelerator_packs/workers/torch_worker.py`
- Modify: `nexusnet/runtime/accelerator_packs/catalog.py`
- Test: `tests/runtime/accelerator_packs/test_environment_locks.py`
- Test: `tests/runtime/accelerator_packs/test_torch_worker_families.py`

**Interfaces:**
- Consumes: private environment builder, official support-matrix data, and Torch worker protocol.
- Produces: `WorkerEnvironmentLock`, mutually exclusive `torch-cpu`/`torch-cuda`/`torch-xpu`/`torch-rocm-windows` families, and device-execution handshakes.

- [x] Write failing tests proving every environment has exactly one Torch distribution family, exact indexes/hashes, no system-site packages, and rejection of unavailable XPU/ROCm backends.
- [x] Run Task 6 tests red for missing locks/family handshakes.
- [x] Implement immutable environment locks keyed by Python/platform/architecture/pack version; keep index URLs and hashes allowlisted and explicit.
- [x] Extend the worker handshake for CPU, CUDA, XPU, and supported Windows ROCm while keeping all device-specific calls inside the worker.
- [x] Add catalog candidates only when device/support-matrix prerequisites match. Training remains a separate declared capability from inference.
- [x] Run focused tests and live CPU/CUDA worker checks; report XPU/ROCm as unavailable/unverified without matching hardware.
- [x] Stage Task 6 files, run cached diff/GitNexus checks, and commit `feat(runtime): isolate native Torch worker families` (`a57c69fd`).

### Task 7: QES calibration, circuit breakers, repair, provenance, and certification surface

**Files:**
- Create: `nexusnet/runtime/accelerator_packs/calibration.py`
- Create: `nexusnet/runtime/accelerator_packs/lifecycle.py`
- Modify: `nexusnet/runtime/accelerator_packs/route_selection.py`
- Modify: `nexusnet/runtime/accelerator_packs/installer.py`
- Modify: `nexusnet/runtime/registry.py`
- Modify: `nexus/api/app.py`
- Modify: `ui/control-panel/app.js`
- Test: `tests/runtime/accelerator_packs/test_calibration.py`
- Test: `tests/runtime/accelerator_packs/test_lifecycle_hardening.py`
- Test: `tests/runtime/accelerator_packs/test_end_to_end_windows_runtime.py`

**Interfaces:**
- Consumes: verified pack/worker/device/model/workload evidence and all previous task interfaces.
- Produces: `CalibrationKey`, `CalibrationRecord`, `CalibrationLedger`, `PackCircuitBreaker`, lifecycle receipts, SBOM/provenance summaries, and an end-to-end governed Windows runtime surface.

- [x] Write failing tests for exact calibration-key identity, stale evidence invalidation, CPU/GPU crossover, contradictory/missing evidence, OOM profile scoping, crash threshold/quarantine, rollback, repair, update, uninstall, retention, and sanitized SBOM/provenance receipts.
- [x] Write an end-to-end failing test covering discover → plan → acquire → verify → activate → select → load → infer → fail/quarantine → fallback/rollback → uninstall.
- [x] Run Task 7 tests red for missing calibration/lifecycle behavior.
- [x] Run GitNexus impact on QES/runtime-plan/API/control-panel symbols before edits and warn on HIGH/CRITICAL risk.
- [x] Implement atomic calibration storage and invalidation. `Auto` ranks only exact-key verified records and otherwise selects a conservative verified fallback with `calibration-required`.
- [x] Implement bounded crash tracking, circuit opening, quarantine, rollback, repair, update, retention, uninstall, and independent core/pack SBOM summaries.
- [x] Project sanitized evidence and blockers through QES, runtime status API, and control panel; never expose raw prompts, model paths, PNP identities, secrets, or worker stderr.
- [x] Run the end-to-end test, all accelerator-pack tests, affected runtime/API/control-panel tests, compile/import/privacy guards, and live CPU/NVIDIA discovery/install/infer/mode/rollback smoke.
- [x] Produce a release-evidence report distinguishing verified current-machine routes from unverified AMD/Intel/Windows ML routes and list the representative-hardware gates still required for product support claims.
- [x] Stage Task 7 files and evidence, run cached diff/GitNexus compare checks, and commit `feat(runtime): complete governed Windows accelerator train` (`ff7f8832`).

## Final Sequential Verification

- [x] Run every test under `tests/runtime/accelerator_packs`, Windows discovery tests, evolutionary-inference tests, runtime registry/model registry tests, release-wrapper runtime tests, and new API/control-surface guards.
- [x] Run `python -m compileall -q` for every touched Python package and AST guards proving vendor libraries are imported only by worker modules.
- [ ] Run `git diff --check`, full branch GitNexus compare, and inspect every affected execution flow.
- [ ] Run live Windows hardware discovery and the installed CPU/NVIDIA vertical smoke from the private/worker environments; capture exact output and artifact hashes.
- [ ] Confirm the base integration checkout, global Python, global Torch, system `PATH`, and unrelated files are unchanged.
- [x] Request an independent whole-branch code review, fix every Critical/Important finding with TDD, and rerun the complete verification matrix (repair series through `87596fd4`, plus closure fix `38ed01b`).
- [ ] Use `superpowers:finishing-a-development-branch` and present the verified local-merge/PR/keep/discard choices.

## Self-Review

- The seven tasks cover specification sequence items 4-10 in order.
- Runtime installation, vendor workers, routing, calibration, and lifecycle remain separate components with dependency-neutral interfaces.
- CPU/NVIDIA current-machine proof is required; AMD/Intel/Windows ML absence produces explicit unverified/unavailable evidence rather than synthetic success.
- Every existing live symbol edit is preceded by GitNexus impact analysis and every commit by staged change detection.
- No placeholder implementation or silent fallback is authorized by this plan.
