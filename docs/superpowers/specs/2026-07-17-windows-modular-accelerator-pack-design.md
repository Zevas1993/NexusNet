# NexusNet Windows Modular Accelerator Pack Design

**Status:** Approved design, awaiting written-spec review
**Date:** 2026-07-17
**Initial platform:** Windows 11 x64 desktop
**Later Canon phase:** Linux, mobile, edge, ARM64, and NPU-specific deployment

## 1. Decision

NexusNet will use a hybrid, capability-driven runtime-pack architecture. The NexusNet control plane will remain free of vendor-specific compute libraries. Accelerator support will be supplied through independently discoverable, installable, testable, updatable, disableable, and rollback-capable runtime packs.

A pack is a logical isolation and lifecycle boundary, not necessarily a Python virtual environment. A pack may be:

- a Windows-managed ONNX execution provider;
- a versioned native worker directory;
- an isolated Python worker environment;
- or an external-runtime connector.

The first implementation targets Windows 11 x64 systems with NVIDIA, AMD, or Intel processors and GPUs. Every supported installation retains a CPU-capable route, including systems whose installed accelerator has no verified NexusNet pack. This defines broad system compatibility; it does not promise acceleration on every legacy, unlisted, or otherwise unsupported GPU. Hardware acceleration is selected by compatibility, correctness, and measured performance, not by vendor identity alone.

The public execution modes are:

- `Auto`: select the best verified route for the exact device, model, and workload profile;
- `CPU`: force a verified CPU route;
- `GPU`: force a verified accelerator route and fail honestly if none is available;
- `Both`: request a verified hybrid CPU/GPU route. Internally this mode is named `hybrid`; it is exposed only when a backend declares and proves hybrid offload support.

## 2. Scope

### 2.1 In scope

- A bundled private Python runtime for NexusNet core.
- An adaptive online Windows installer that leaves system Python and system Torch unchanged.
- Windows 11 x64 hardware discovery for NVIDIA, AMD, Intel, and CPU resources.
- Isolated runtime-pack discovery, acquisition, validation, activation, health checking, updating, and rollback.
- Windows ML execution-provider integration for compatible ONNX workloads.
- Versioned llama.cpp native packs for GGUF inference.
- Isolated vendor-specific PyTorch workers for native NexusNet MoE, expert inference, assimilation, and training workloads that require PyTorch.
- Cross-vendor Vulkan or DirectML/Windows ML fallback where compatible with the workload.
- Universal CPU fallback.
- Multi-device and mixed-vendor discovery and routing.
- Evidence-based `Auto`, `CPU`, `GPU`, and `Both` selection.
- Sanitized receipts for discovery, pack lifecycle, calibration, selection, fallback, and failures.
- Platform-neutral contracts so Linux can add a new platform adapter later.

### 2.2 Out of scope

- Linux implementation in the first delivery.
- Windows on ARM64.
- Mobile and edge deployment.
- NPU-specific execution.
- Combining unrelated GPUs into one distributed inference job.
- Assuming every model format can run on every backend.
- Installing every vendor stack on every machine.
- Mutating, upgrading, or relying on a user's global Python environment.
- Treating presence of a GPU, driver, package, endpoint, or model file as proof that inference is live or performant.

### 2.3 Support terminology

NexusNet uses these terms as evidence levels, not synonyms:

- `detected`: hardware or software was observed by a probe;
- `compatible`: the observed tuple satisfies a pack's declared prerequisites;
- `verified`: a specific device, driver, pack, model, and workload tuple passed required health, correctness, execution, and policy checks;
- `supported`: the declared hardware class passed the full real-device release evidence gate and is covered by the published support matrix.

Detection or compatibility alone never makes a route eligible for `Auto` and never justifies a product support claim. An unverified or unsupported accelerator does not make the Windows system unusable when a verified CPU route remains available.

## 3. Research conclusions

The design follows these current ecosystem constraints:

1. PyTorch CPU, CUDA, XPU, and ROCm distributions are mutually exclusive variants of the `torch` package. They must not be combined in one environment.
2. ONNX Runtime GenAI directs users to install only one CPU, DirectML, or CUDA package set in a given environment.
3. Windows ML can dynamically acquire Windows-certified execution providers for supported hardware on Windows 11 24H2 or newer. Current provider families include NVIDIA NvTensorRtRtx, AMD MIGraphX and VitisAI, and Intel OpenVINO, while DirectML and the ORT CPU provider remain broad fallbacks.
4. Windows ML does not cover every NexusNet workload. It requires compatible ONNX models, and the current AMD MIGraphX Windows ML provider does not support GenAI scenarios.
5. llama.cpp publishes separate Windows x64 CPU, CUDA, HIP, Vulkan, OpenVINO, and SYCL builds. Those artifacts naturally fit versioned native packs.
6. AMD's native Windows ROCm and PyTorch support is limited to an explicit hardware and software matrix. Unsupported AMD devices require another verified path rather than an optimistic ROCm claim.
7. Intel PyTorch XPU supports a defined set of Intel client GPUs on Windows. Older or unlisted Intel devices must use a verified SYCL, OpenVINO, Vulkan, DirectML, or CPU route.
8. Python virtual environments are disposable and non-portable. NexusNet will recreate environments from locked manifests on the target machine rather than copying a development venv.

### 3.1 Local evidence

The research environment demonstrated that isolation works without changing the global environment:

- global Python: PyTorch `2.6.0+cpu`, CUDA unavailable;
- test environment: PyTorch `2.11.0+cu128`, CUDA available;
- detected accelerator: NVIDIA GeForce RTX 5070 Ti;
- focused native-inference verification: 70 passed, 1 skipped.

The test environment was created with `--system-site-packages`. It proved mutation isolation but is not the production template. Production base and worker environments must be created without system-site packages.

A resident-tensor SwiGLU microbenchmark also showed why `Auto` must calibrate exact workload profiles. One-row work was faster on CPU, while larger row counts favored the GPU by up to roughly eight times in that synthetic test. These numbers are evidence for crossover behavior, not product performance claims.

## 4. Architectural principles

### 4.1 Vendor-neutral core

NexusNet core will not import Torch CUDA, Torch XPU, ROCm, OpenVINO, DirectML, or vendor DLLs. Core owns policy, orchestration, evidence, and lifecycle. Packs own vendor libraries and device execution.

### 4.2 Capability-based identity

The router will reason about capabilities such as:

- workload kinds: `llm-generate`, `embedding`, `rerank`, `vision`, `native-moe`, `training`;
- model formats: `gguf`, `onnx`, `ort`, `safetensors`, `torch`;
- accelerator APIs: `cuda`, `hip`, `xpu`, `sycl`, `openvino`, `vulkan`, `directml`, `windows-ml`, `cpu`;
- execution features: streaming, structured output, tools, quantization, partial offload, hybrid offload, training, and deterministic mode.

Vendor names may appear in manifests and observations, but core selection rules must not be hardcoded as `if NVIDIA`, `if AMD`, or `if Intel` dispatch branches.

### 4.3 Process isolation

Managed native and Python packs run out of process. A dependency crash, DLL conflict, import failure, memory fault, or incompatible runtime must not take down the NexusNet control plane.

### 4.4 Honest degradation

A route is usable only after compatibility checks, a live health probe, a correctness smoke test, and any policy-required calibration. Forced `GPU` or `Both` requests do not silently become CPU requests. `Auto` may choose CPU and must record why.

### 4.5 Independent lifecycle

Core and packs have separate versions. A pack update can be installed, evaluated, activated, quarantined, or rolled back without upgrading NexusNet core or another pack.

## 5. System components

### 5.1 NexusNet Core Environment

The Windows installer creates a clean, private base environment from the bundled Python runtime. It contains NexusNet, its control-plane dependencies, the installer/pack manager, and no vendor-specific Torch or ONNX Runtime variant.

`pyproject.toml` is the packaging authority. Legacy `setup.py` and hand-maintained requirements files must not define conflicting dependency or command contracts. Platform and pack locks are generated from the authoritative project metadata and committed as reproducible inputs.

The source checkout does not live inside the environment. Development uses an editable installation in a clean project `.venv`; end-user installation uses built, versioned artifacts.

### 5.2 Hardware Capability Discoverer

The discoverer produces a sanitized graph of compute and memory resources without importing optional pack dependencies. On Windows it may use stable OS APIs, CIM/WMI, DXGI, vendor command-line probes when present, and Windows ML provider enumeration.

Each device observation includes:

- stable local device reference;
- device class and vendor ID;
- architecture and accelerator APIs;
- dedicated and shared memory where available;
- driver version;
- relevant runtime availability;
- sanitized capabilities and reason codes;
- probe source and collection timestamp.

Discovery must represent multiple devices independently. A machine with an Intel integrated GPU and NVIDIA discrete GPU yields two accelerator nodes and separate candidate sets.

Failure to run one probe does not erase CPU capability or other devices. Probe failures are recorded as unavailable or unverified observations.

### 5.3 Runtime Pack Manifest

Every NexusNet-managed pack has a signed, versioned manifest. Windows-managed execution providers are projected into the same normalized manifest shape at discovery time.

Required manifest fields are:

- schema version;
- pack ID, version, and pack type;
- publisher and license metadata;
- supported operating systems and architectures;
- workload kinds and model formats;
- accelerator APIs and device-match predicates;
- driver, OS-build, Python, ABI, and dependency constraints;
- worker launch contract;
- supported execution modes;
- health, correctness, and benchmark contracts;
- artifact URLs, sizes, hashes, and signatures;
- capability declarations and known limitations;
- rollback compatibility and data migration policy.

Unknown manifest fields are rejected unless a later schema version explicitly allows them. A manifest cannot grant capabilities that the worker does not report and prove at runtime.

### 5.4 Pack Registry

The registry stores installed, available, active, quarantined, and previous pack versions. It is the only source of activated pack identity for the router.

Registry responsibilities are:

- validate manifests;
- enumerate pack candidates;
- map packs to detected devices and workloads;
- track installation and activation state;
- expose health and evidence summaries;
- maintain current and previous version pointers;
- prevent duplicate or conflicting activation;
- quarantine packs that fail startup, correctness, stability, or policy checks.

The registry does not execute inference or select models.

### 5.5 Pack Manager

The pack manager performs acquisition and lifecycle operations:

- resolve compatible candidates;
- show the chosen artifact and download size during installation;
- download to a staging directory;
- verify origin, digest, signature, license posture, and disk budget;
- construct native directories or clean worker venvs;
- run health and correctness checks before activation;
- atomically activate a passing version;
- retain the last known-good version;
- rollback or quarantine a failing version;
- garbage-collect inactive versions under an explicit retention policy.

Initial pack downloads are covered by installer consent. NexusNet does not perform hidden post-install downloads. Later optional packs and materially large updates require explicit user or administrator approval under product policy.

### 5.6 Runtime Worker Protocol

NexusNet-managed workers use versioned JSON messages over standard input and standard output. This protocol is cross-platform, avoids fixed local ports, and keeps vendor dependencies outside core. Existing external HTTP providers remain HTTP connectors but are projected behind the same logical runtime contract.

Required worker operations are:

- `describe`;
- `health`;
- `self_test`;
- `benchmark`;
- `load_model`;
- `infer`;
- `unload_model`;
- `cancel`;
- `shutdown`.

Each request contains a protocol version, request ID, deadlines, sanitized model reference, workload profile, requested execution mode, and policy receipt reference. Streaming responses use ordered event frames with terminal success or failure frames.

Workers never write raw prompts, model outputs, secrets, or user content to lifecycle and benchmark receipts. Content logging is controlled by the higher-level governed evidence policy.

Core enforces startup, request, cancellation, and shutdown timeouts. Malformed frames, protocol-version mismatch, unexpected process exit, or deadline violation degrade the worker and may quarantine the active pack.

### 5.7 Windows ML Pack

The Windows ML pack is the preferred ONNX path on compatible Windows systems. It:

- enumerates compatible execution providers;
- records provider readiness and version;
- acquires Windows-certified providers when installer or user policy allows;
- registers ready providers with ONNX Runtime;
- exposes device and provider capabilities to NexusNet;
- validates each model/provider pairing;
- benchmarks explicit providers instead of trusting provider order;
- preserves DirectML and CPU fallbacks.

On Windows 11 builds older than 26100, vendor-provider acquisition through the Windows ML catalog is not assumed. DirectML, CPU, or NexusNet-managed packs remain eligible.

Windows-managed providers may update independently. Provider-version changes invalidate affected correctness and performance evidence before the provider can win `Auto` selection again.

For offline, managed, or strict-version deployments, the same logical pack may register a bring-your-own execution-provider library. The manifest identifies whether the provider is Windows-managed or NexusNet-managed.

### 5.8 llama.cpp Native Packs

GGUF inference uses separate native packs for available llama.cpp backends:

- CUDA;
- HIP;
- SYCL;
- OpenVINO;
- Vulkan;
- CPU.

The installer resolves only compatible candidates. Vulkan is a portable GPU fallback, not an automatic winner over a vendor-native backend. CPU remains the terminal compatibility route.

Each pack runs as a local worker or managed llama.cpp server controlled by NexusNet. It must report the actual compiled backend, visible devices, model format support, offload controls, and hybrid capabilities.

### 5.9 PyTorch Worker Packs

PyTorch-dependent work uses separate clean environments for:

- CUDA;
- Intel XPU;
- AMD Windows ROCm where officially supported;
- CPU.

Each environment contains exactly one Torch distribution family. Dependencies are locked by Python version, platform, architecture, pack version, and artifact hash. No pack uses `--system-site-packages`.

PyTorch workers support only the workload kinds declared by their manifests. Inference support does not imply training support. Training support does not imply that a model fits in memory.

The current native MoE CUDA implementation must move behind a device-execution abstraction before non-CUDA workers can participate. Device-specific tensor operations remain inside the worker or device adapter rather than leaking into control-plane routing.

### 5.10 External Runtime Connectors

Ollama, LM Studio, and other externally managed runtimes remain optional connectors. NexusNet does not claim responsibility for their internal dependencies. A connector is eligible only after endpoint liveness, model availability, contract compatibility, and policy admission are verified.

External connectors use the same capability, health, benchmark, and receipt vocabulary as managed packs so QES can compare them without special-casing provider names.

## 6. Installation and acquisition flow

The adaptive online Windows installation flow is:

1. Validate supported Windows architecture and minimum core requirements.
2. Install the bundled private Python runtime and NexusNet base environment.
3. Run dependency-free hardware and OS discovery.
4. Build candidate packs for every detected device and required workload family.
5. Select a small initial set: a universal CPU-capable route and the highest-confidence compatible accelerator route for this machine.
6. Display planned downloads, disk use, license notices, and fallback posture.
7. Download and verify artifacts.
8. Construct isolated worker environments or native pack directories.
9. Run health and correctness checks.
10. Activate only passing packs.
11. Run bounded calibration for eligible `Auto` routes.
12. Persist sanitized installation and activation receipts.
13. Launch NexusNet through a stable Windows entry point that always invokes the private base environment.

If accelerator acquisition or activation fails, installation can finish with a verified CPU route. The installer reports the accelerator as degraded or unavailable and preserves a repair action; it does not report full accelerator readiness.

Uninstall removes NexusNet-owned environments, packs, caches, and launchers according to retention settings. It does not uninstall shared Windows ML execution providers or change global Python packages.

## 7. Selection and calibration

### 7.1 Eligibility gates

A route enters calibration only when all of these are true:

- manifest and artifact verification passed;
- device match passed;
- OS, driver, ABI, and dependency constraints passed;
- worker health passed;
- model format and workload contract match;
- correctness self-test passed;
- policy and privacy admission passed;
- resource feasibility passed.

### 7.2 Calibration key

Performance and stability evidence is keyed by:

- host fingerprint;
- device reference;
- OS build;
- driver version;
- pack and worker version;
- execution-provider version where applicable;
- model digest and model format;
- quantization;
- input, output, context, and batch buckets;
- execution mode;
- relevant runtime parameters.

A change to any identity-bearing field invalidates the prior winning claim for that key.

### 7.3 Measurements

Calibration records at least:

- startup and model-load latency;
- time to first token where applicable;
- steady-state latency or throughput;
- peak host memory and device memory;
- correctness result;
- timeout and error counts;
- thermal or power observations when available and trustworthy;
- sample count, warmup policy, and duration.

Calibration is bounded. It does not run an unbounded benchmark suite during installation. Longer certification can run later under explicit policy.

### 7.4 Auto selection

`Auto` ranks only eligible, verified routes. The objective may prioritize latency, throughput, memory, power, privacy, or a balanced score. A GPU is not selected merely because it exists. CPU may win small or latency-sensitive work.

When evidence is missing or stale, `Auto` uses a conservative verified fallback and records `calibration-required` or another specific reason code. It does not promote an unverified route based on estimated capability alone.

### 7.5 Forced modes

- `CPU` selects a verified CPU route or returns an explicit CPU-route-unavailable error.
- `GPU` selects a verified accelerator route for the requested workload or returns an explicit accelerator-route-unavailable error.
- `Both` selects a route whose manifest and calibration prove hybrid offload. It never means running duplicate inference on CPU and GPU, and it does not combine unrelated vendor devices by default.
- `Auto` may choose CPU, GPU, or hybrid and explains the choice through sanitized reason codes.

## 8. Failure handling and rollback

Pack states are:

- `available`;
- `downloading`;
- `staged`;
- `verifying`;
- `active`;
- `degraded`;
- `quarantined`;
- `rollback-available`;
- `removed`.

Required behavior includes:

- Partial downloads remain in staging and are never executable.
- Digest or signature mismatch deletes or quarantines the staged artifact and blocks activation.
- Worker startup or self-test failure preserves the previous active version.
- Repeated runtime crashes open a circuit breaker and remove the pack from `Auto` eligibility.
- Out-of-memory failures update feasibility evidence for that model/profile instead of globally condemning the device.
- Correctness mismatch quarantines the exact pack/device/model combination and may quarantine the pack according to severity.
- Driver or Windows ML provider changes invalidate evidence and trigger revalidation.
- Rollback activation is atomic and recorded.
- No fallback is silent. Every fallback includes the rejected route, reason code, selected route, and evidence references without raw user content.

## 9. Security and supply-chain requirements

- Artifacts come only from allowlisted publishers and repositories.
- Every NexusNet-managed artifact is verified by cryptographic digest; signatures are required where the publisher provides a verifiable signing mechanism.
- Platform locks include artifact hashes and exact versions.
- Pack manifests include license and provenance metadata.
- Native and Python workers run with least privilege and constrained environment variables.
- Core does not add pack DLL directories to the machine-wide `PATH`.
- Pack libraries remain in versioned private directories.
- Worker protocol frames are size-bounded and schema-validated.
- Secrets are provided only to a worker that requires them and are never included in receipts.
- Download, activation, update, rollback, and quarantine actions are auditable.
- A software bill of materials can be produced for core and each pack independently.

## 10. Integration with the current NexusNet repository

The implementation should extend existing seams instead of creating a parallel runtime control plane.

### 10.1 Reuse

- `nexus/runtimes/base.py`: preserve the logical `health`, `generate`, and profile contract while adding a worker-backed adapter.
- `nexus/runtimes/registry.py`: evolve from eager in-process adapters and static choice into pack-backed discovery and verified adapter registration.
- `nexusnet/runtime/registry.py`: retain capability-card, QES, model-catalog, and benchmark coordination.
- `nexusnet/runtime/evolutionary_inference`: retain hardware graph, feasibility, calibration, synthesis, and promotion concepts.
- `nexusnet/runtime/inference_economy_router.py`: consume a verified execution-plan decision; do not absorb pack installation mechanics.
- governed evidence and authority services: retain admission, sanitized receipts, and fail-closed behavior.

### 10.2 Correct

- Replace CUDA-only hardware scanning with the normalized multi-device discovery contract.
- Expand accelerator observations beyond fixed CUDA, ROCm, and Metal literals.
- Make Windows ROCm discovery follow the current official support matrix rather than rejecting Windows categorically.
- Replace static runtime fallback order with eligibility and evidence-driven selection.
- Turn the benchmark matrix into versioned lookup and invalidation evidence used by QES.
- Move native MoE CUDA checks behind a device-execution interface.
- Remove vendor-specific imports from core execution paths.
- Replace placeholder Windows bootstrap behavior with the private-runtime and pack-manager installation flow.
- Consolidate packaging authority under `pyproject.toml` and eliminate dependency/entry-point drift from legacy packaging files.

### 10.3 Keep separate

- Hardware discovery observes resources.
- Pack registry tracks lifecycle and capability.
- Pack manager mutates pack installation state.
- Workers execute vendor code.
- QES selects among verified routes.
- Inference Economy Router applies task, privacy, cost, and governance policy.
- Evidence services record sanitized outcomes.

No component should take over another component's responsibility.

## 11. Linux portability

Linux support will replace Windows-specific discovery and acquisition adapters while preserving:

- the manifest schema;
- pack registry and lifecycle states;
- worker protocol;
- capability vocabulary;
- selection and calibration keys;
- execution modes;
- evidence and rollback contracts.

Windows ML is represented as a Windows platform pack, not embedded into core abstractions. Linux can later provide CUDA, ROCm, SYCL/OpenVINO, Vulkan, and CPU packs without changing QES or the public runtime controls.

Mobile and edge remain later Canon phases and may use different worker transports or embedded runtimes while projecting the same higher-level capability and evidence contracts.

## 12. Testing strategy

### 12.1 Contract tests

- Manifest validation, schema-version rejection, and capability normalization.
- Worker protocol framing, deadlines, cancellation, streaming order, and malformed-message handling.
- Registry lifecycle transitions and atomic activation.
- Calibration-key construction and invalidation.
- Execution-mode semantics.
- Sanitization of all lifecycle and routing receipts.

### 12.2 Installer tests

- Clean Windows 11 x64 VM with no Python installed.
- Existing unrelated system Python and Torch remain unchanged.
- Interrupted downloads and low-disk conditions.
- No compatible GPU.
- Supported and unsupported driver versions.
- Upgrade, repair, rollback, and uninstall.
- Installation paths containing spaces and non-ASCII characters.
- Offline behavior after successful installation.

### 12.3 Hardware matrix

The release evidence matrix must include real Windows hardware for:

- NVIDIA CUDA-capable GPU;
- supported AMD GPU;
- supported Intel GPU;
- CPU-only system;
- mixed-vendor or integrated-plus-discrete system where available.

Mocked discovery covers additional device and failure combinations but does not replace real-device proof.

### 12.4 Runtime tests

- Correctness equivalence against the CPU reference within declared tolerance.
- Model load, infer, unload, cancel, and process restart.
- CPU/GPU crossover calibration.
- GPU out-of-memory and host-memory pressure.
- Forced `CPU`, `GPU`, and `Both` behavior.
- `Auto` selection with fresh, stale, missing, and contradictory evidence.
- External provider liveness loss.
- Pack crash, timeout, malformed output, and circuit breaker.
- Windows ML provider update and evidence invalidation.

### 12.5 Release gates

A vendor route is not described as working or supported until its declared hardware class has:

- installation proof;
- discovery proof;
- health proof;
- correctness proof;
- execution proof;
- fallback proof;
- update or rollback proof;
- and exact test output recorded in the release evidence.

## 13. Implementation sequence

The design is implemented in bounded slices:

1. Define pack manifest, normalized device schema, worker protocol, lifecycle states, and red contract tests.
2. Add pack registry and worker supervisor without changing live inference selection.
3. Add Windows multi-device discovery and capability projection.
4. Replace the placeholder Windows installer with the clean private core environment and adaptive pack acquisition foundation.
5. Deliver a CPU pack and NVIDIA CUDA vertical slice on the current machine, including explicit modes and rollback.
6. Add Windows ML ONNX integration with DirectML and CPU fallback.
7. Add AMD HIP/Vulkan and Intel SYCL/OpenVINO paths with real-device evidence gates.
8. Add isolated PyTorch XPU, supported Windows ROCm, and CPU workers where native NexusNet workloads require them.
9. Connect QES calibration evidence to live selection and retire static availability-order claims.
10. Harden updates, circuit breakers, repair, uninstall, provenance, and full Windows hardware certification.

Each slice requires focused red tests, implementation, targeted verification, GitNexus impact analysis before symbol edits, `gitnexus_detect_changes` before commit, and honest reporting of unsupported or unverified hardware.

## 14. Acceptance criteria

The Windows modular accelerator foundation is accepted only when all of the following are demonstrated:

1. NexusNet installs on a clean Windows 11 x64 machine without a preinstalled Python runtime.
2. Installation does not modify global Python, global Torch, or unrelated environments.
3. Core starts with no vendor-specific Python package imported.
4. NVIDIA, AMD, Intel, and CPU resources can be represented by the normalized device contract.
5. The first foundation vertical slice has full install-to-inference evidence for CPU and the current NVIDIA machine. A Windows product release described as supporting NVIDIA, AMD, and Intel acceleration is not accepted until representative supported hardware from all three vendor families passes the complete real-device release gate. Before that proof exists, AMD and Intel routes remain explicitly `unverified` in product state and documentation.
6. Windows ML, llama.cpp, PyTorch workers, and external connectors project the same logical capability and health vocabulary.
7. Mutually exclusive Torch and ONNX package variants are isolated.
8. `CPU`, `GPU`, `Both`, and `Auto` have the exact semantics defined in this specification.
9. `Auto` selects only a correctness-verified route and uses exact-profile performance evidence when claiming a performance winner.
10. A failed pack cannot crash core, silently replace a forced mode, or remain eligible after quarantine.
11. Pack update and rollback work without upgrading NexusNet core.
12. Installer repair and uninstall preserve shared Windows components and remove NexusNet-owned artifacts according to policy.
13. Linux can add a platform discovery/acquisition adapter without changing the manifest, worker, QES, or public execution-mode contracts.

## 15. Rejected alternatives

### 15.1 One monolithic venv

Rejected because vendor Torch builds and ONNX Runtime variants conflict, native DLLs can collide, mixed-vendor systems cannot be represented cleanly, and one dependency failure can break core.

### 15.2 Windows ML only

Rejected because it is limited to compatible ONNX workloads and does not cover GGUF, every GenAI path, native NexusNet MoE, or PyTorch training.

### 15.3 NexusNet bundles every vendor SDK

Rejected because it duplicates Windows-certified provider distribution, inflates the installer, increases licensing and update burden, and weakens compatibility. Bring-your-own providers remain an explicit fallback for offline or strict-version deployments.

### 15.4 Separate NVIDIA, AMD, and Intel products

Rejected because it fragments NexusNet, complicates mixed-device systems, multiplies update and support paths, and moves hardware decisions onto end users.

### 15.5 One cross-vendor GPU API

Rejected as the only path because Vulkan or DirectML can provide broad compatibility but cannot be assumed to match vendor-native performance or support every workload and model format.

## 16. Primary research sources

- Python virtual environments: https://docs.python.org/3/library/venv.html
- PyTorch previous-version and accelerator wheel installation: https://docs.pytorch.org/get-started/previous-versions/
- PyTorch Intel XPU on Windows: https://docs.pytorch.org/docs/stable/notes/get_start_xpu.html
- AMD Windows ROCm support matrix: https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibility/compatibilityrad/windows/windows_compatibility.html
- ONNX Runtime GenAI package isolation: https://onnxruntime.ai/docs/genai/howto/install.html
- ONNX Runtime execution providers: https://onnxruntime.ai/docs/execution-providers/
- Windows ML overview: https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/overview
- Windows ML execution providers: https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/supported-execution-providers
- Windows ML provider acquisition: https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/initialize-execution-providers
- Windows ML versus bring-your-own providers: https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/windows-ml-eps-vs-bring-your-own
- llama.cpp Windows backend releases: https://github.com/ggml-org/llama.cpp/releases
