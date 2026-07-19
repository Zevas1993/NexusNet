# Windows Accelerator Train Release Evidence — 2026-07-18

## Claim boundary

This report separates current-machine execution proof from catalog eligibility.
Detection, a matching support-matrix tuple, and fixture tests do not activate a
route. NexusNet requires a verified install, worker health, correctness,
policy admission, and exact calibration evidence before `Auto` ranks an
accelerator. Without exact calibration, `Auto` conservatively selects a
verified CPU route and reports `calibration-required`. Forced GPU and Both do
not silently fall back.

## Current machine

- Windows x64 build 26200.
- 13th Gen Intel Core i7-13700K, 16 physical cores / 24 logical processors.
- 34,028,507,136 bytes system memory.
- NVIDIA GeForce RTX 5070 Ti, driver 32.0.15.9636.
- CUDA worker observation: Torch 2.11.0+cu128, CUDA runtime 12.8, one device,
  17,094,475,776 bytes reported device memory.
- The core/system ONNX Runtime 1.27.0 environment exposes
  AzureExecutionProvider and CPUExecutionProvider. No Windows ML dynamic GPU
  provider was observed there.
- A separate no-system-site-packages evidence venv exposes ONNX Runtime
  DirectML 1.24.4 with DmlExecutionProvider and CPUExecutionProvider. A
  CPU-fallback-disabled profile attributed the deterministic proof kernels
  only to DmlExecutionProvider.
- No AMD GPU or Intel GPU was detected. The Intel CPU is not XPU proof.

Raw PNP identities are intentionally excluded. Runtime status projects a
one-way `device::` reference instead.

## Evidence matrix

| Route family | Current state | Evidence | Remaining gate |
| --- | --- | --- | --- |
| Reference CPU | Verified on this machine | Real load, self-test, numeric inference, unload, governed fallback/rollback test | Model-family-specific certification beyond the deterministic proof model |
| Torch CPU | Verified on this machine | Fresh CPython 3.11 private venv, no system site packages, 15 exact hashed wheels, Torch 2.11.0+cpu, health/self-test, `[3,5,7]` inference | Production model/workload calibration records |
| NVIDIA CUDA | Verified on this machine for the worker/device proof | Exact 15-wheel CUDA lock in a no-system-site-packages CPython 3.11 venv; Torch 2.11.0+cu128, CUDA 12.8, RTX 5070 Ti; describe, health, self-test, load, `[3,5,7]` inference, and unload passed | Production-model/workload calibration records plus cancellation, timeout, OOM, crash, reboot, and sustained-load soak |
| Windows ML dynamic providers | Unavailable and unverified | Windows build gate passes and missing-runtime/provider discovery remains truthful | Install and enumerate the supported Windows ML runtime/provider packages, then model correctness and recovery proof |
| DirectML | Verified on this NVIDIA machine for the deterministic provider/worker proof; product route unactivated | Private ONNX Runtime DirectML 1.24.4 venv, explicit DmlExecutionProvider, CPU EP fallback disabled, profiler attributed kernels only to DirectML, and NexusNet health/self-test/load/`[3,5,7]` inference/unload passed | Add a reviewed exact environment lock and catalog acquisition path, then certify release models and representative AMD/Intel hardware separately |
| AMD ROCm Windows | Unavailable, unverified, and install-not-ready | Exact cp312 ROCm 7.2.1 Torch wheel lock and official support tuples are encoded, but the required ROCm SDK prerequisite packages are not yet fully locked | Complete the private SDK prerequisite lock, then use representative supported Radeon/Ryzen hardware for driver/SDK install, health, correctness, OOM, rollback, and soak |
| AMD Vulkan | Unavailable and unverified | Capability-driven native candidate and bounded connector tests | Representative AMD hardware and reviewed native binary certification |
| Intel Torch XPU | Unavailable and unverified | Exact official XPU lock and family-rejection tests | Representative Intel GPU, driver install, real XPU health/correctness/OOM/rollback/soak |
| Intel SYCL/OpenVINO | Unavailable and unverified | Capability-driven native candidates and connector tests | Representative Intel GPU and reviewed binary/provider certification |
| Both / hybrid | Unavailable | Selector requires explicit `hybrid-offload` proof | A pack that demonstrates real cross-device hybrid offload and calibration |

## Supply-chain and isolation evidence

- CPU lock requirements SHA-256:
  `67e38f978ce337d493dfc634e04cf13d2ae953e49e5c740b54753911ee81f025`.
- CUDA lock requirements SHA-256:
  `31786cbd665c82ff38cc52ae4c1daa3fb8d028c59aa9a7435062154bde0eb46f`.
- The environment builder recorded `include-system-site-packages = false`.
- Torch families are mutually exclusive: CPU, CUDA, XPU, and Windows ROCm.
- Every locked wheel has a reviewed HTTPS host, exact byte size, and SHA-256.
- Pack acquisition uses bounded streaming, disk reserve checks, partial-file
  isolation, digest enforcement, and atomic promotion.
- Lifecycle receipts expose manifest/SBOM digests, publisher, license, counts,
  actions, and sanitized reason codes without URLs, install paths, prompts,
  model paths, PNP identities, secrets, or worker stderr.
- The DirectML evidence venv used exact top-level package versions, but it is
  not represented as a release lock: transitive wheel hashes still require
  review before the product catalog may acquire or activate that route.

## Governed selection and recovery evidence

- Calibration identity includes route, pack/version, worker version, device
  fingerprint, driver, model hash, workload, and workload-profile hash.
- Stale or changed driver/model/profile evidence does not match.
- OOM and crash state is scoped to the exact calibration key.
- `Auto` ranks only exact passed calibration records; missing evidence produces
  conservative CPU plus `calibration-required`.
- Circuit thresholds are bounded and persisted atomically. Opening a circuit
  quarantines its route and requests rollback to the declared compatible
  predecessor.
- Repair requires fresh verification; update preserves one rollback candidate;
  uninstall removes only NexusNet-owned pack/environment roots.
- The end-to-end governed fixture covers plan, acquire, digest verify, activate,
  exact calibrated select, real reference load/infer, crash threshold,
  quarantine, rollback/fallback, and uninstall.

## Product-support gates still required

1. Record production-model calibration on CPU and RTX 5070 Ti across prompt
   sizes, batch sizes, memory pressure, cancellation, timeout, and OOM profiles.
2. Extend the passing packaged install/repair/update/rollback/uninstall proof
   with repeated worker-crash, process-tree cleanup, reboot persistence, and
   sustained-load soak.
3. Certify AMD ROCm/Vulkan on each claimed support-family tuple using a
   representative device and exact driver/runtime receipts.
4. Certify Intel XPU/SYCL/OpenVINO on representative Intel GPUs.
5. Keep Windows ML unavailable until its dynamic runtime/provider is actually
   enumerated. Convert the passing DirectML proof into a hashed release lock,
   then run release-model correctness and recovery gates.
6. Keep hybrid disabled until measured cross-device offload outperforms the
   best single route without correctness or stability regression.

## Historical verification status at Task 7 commit gate

- Accelerator-pack plus runtime-mode/certification API matrix: 253 passed after
  the final direct-uninstall rollback regression was added.
- Task 7 calibration/lifecycle/end-to-end/route/live-registry/API matrix:
  28 passed.
- Windows discovery, evolutionary inference, model registry, hardware API,
  universal runtime gates, runtime scorecards, and mode API matrix: 68 passed.
- Core endpoint matrix: 5 passed.
- Release heartbeat supervisor plus runtime workload scorecards: 11 passed.
- Provider/wrapper-growth file: 15 passed and 6 failed. The exact six failures
  reproduce at the Task 6 baseline with the same assertions, so they are not
  introduced by this train.
- Release-wrapper runtime was too slow to complete as an 85-test monolith in a
  20-minute bounded run. Split evidence covered tests 1–30: 25 passed and 5
  failed. The exact five failures reproduce at the Task 6 baseline. Remaining
  release-wrapper cases are not represented as passing evidence.

The baseline failures concern pre-existing visualizer label assertions,
heartbeat/repair ordering and state expectations, a deliberately missing
production-spine path, and release boot-smoke state. They are not silently
converted to passes or attributed to the accelerator implementation.

## Post-repair and release-closure verification — 2026-07-19

- The independent repair series through `87596fd4` resolved the historical
  provider-wrapper, release-wrapper, heartbeat, repair-ordering, production
  spine, and boot-smoke failures recorded above.
- A full system-interpreter traversal completed with 2,129 passed, 7 failed,
  and 4 skipped. The seven failures were two missing Canon capture scripts,
  four stale wrapper assertions, and two Windows long-path sandbox failures.
- Closure commit `38ed01b` restored the two Canon capture scripts, corrected
  the wrapper assertions, bounded pytest temporary-path labels for Windows,
  and added a direct regression test for that path policy.
- A second full traversal used the CUDA interpreter and a live Docker Desktop
  daemon: 2,139 passed, 1 failed, and 1 skipped in 6,925.94 seconds. The sole
  failure was a stale visualizer assertion that assumed VRAM telemetry could
  never be bound; live RTX telemetry correctly contradicted it. The closure
  commit makes that assertion capability-aware.
- The sole skip in the CUDA traversal is an intentionally mutually exclusive
  CPU-only test that verifies forced GPU fails before worker attachment when
  CUDA is unavailable. It passed under the system interpreter. The union of
  the CPU-only matrix (2 passed) and live-CUDA matrix (3 passed) exercises both
  environment branches without an unexecuted case.
- The post-fix focused closure matrix passed 10 tests, including both Canon
  capture tools, bounded Windows paths, sandbox isolation, wrapper behavior,
  and telemetry-aware visualizer behavior. Both Node capture scripts also
  passed syntax and help-entrypoint checks, and `compileall` passed for the
  touched Python surfaces.
- Commit `f058f4b` added the consent-gated lifecycle CLI. Its 60-test focused
  matrix passed, including a real clean-venv reference install/uninstall. The
  production CUDA pack then installed its exact 2.576 GiB wheel set in 89.9
  seconds; `pip check` and every deterministic worker operation passed.
- The first clean packaged-core probe exposed an eager import of optional
  Torch. Commit `101b741` made all 41 evolutionary-inference public exports
  lazy without changing their names. The clean core then planned packs without
  Torch, and the HIGH-risk regression matrix passed 79 tests.
- A second fresh packaged-root soak passed install, deliberate quarantine,
  fresh repair, compatible update, rollback, and both uninstalls. No pack or
  environment files remained. The global pip-list hash was identical before
  and after (`BE3F32DE23CD88B74A0A1716BF99B5F52972076D2728B3B2ECFF0D0904F0E368`),
  and process, user, and machine PATH values were unchanged.
- The private DirectML probe passed deterministic ONNX correctness and exposed
  one silent-fallback risk. The worker now disables CPU EP fallback for an
  explicit DmlExecutionProvider session; the provider/vendor/import/privacy
  matrix passed 51 tests. Windows ROCm Torch candidates are now suppressed by
  default until SDK-prerequisite readiness is explicitly verified.

A final full traversal remains required after the production-isolated pack
installation, packaged lifecycle soak, and DirectML/private-provider work in
the release-closure train. Therefore this section does not yet claim the
entire seven-item release closure is complete.
