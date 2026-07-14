# NexusNet Evolutionary Inference Fabric Design

**Date:** 2026-07-14

**Status:** Approved umbrella architecture; implementation planning pending user review

**Authority:** NexusBrain

**Baseline:** `fadac0d9`

**Supersedes:** The narrow assumption that inference assimilation should be organized per model or around one external runtime. The existing Colibri-native MoE work remains a valid primitive and evidence source inside this broader fabric.

**Related design:** `docs/superpowers/specs/2026-07-14-nexusnet-colibri-native-inference-assimilation-design.md`

## 1. Decision

NexusNet will build a model-agnostic, hardware-adaptive, continuously evolving inference fabric. It will assimilate the strongest transferable mechanisms from current inference systems, runtimes, kernels, and research papers into NexusNet-owned primitives. It will not canonize one model, one hardware vendor, one runtime, one optimization, or one fixed policy as universally best.

The fabric will:

1. inspect the executable structure and resource behavior of an incoming model without requiring model-specific code;
2. discover and benchmark the actual capabilities of the system on which NexusNet is running;
3. compose compatible inference primitives into multiple candidate execution plans;
4. select a Pareto-optimal plan for the active service-level objective;
5. continuously measure quality, latency, throughput, memory, energy, thermals, stability, and cost;
6. use downtime to dream up, sandbox, benchmark, and validate better inference methods;
7. transfer successful learning into global policies so later models and systems begin with stronger priors;
8. promote only evidence-backed improvements and retain a verified rollback path.

The governing rule is:

> Avoid unnecessary work and movement; compress and overlap unavoidable work and movement; place each operation where total measured cost is lowest; learn from every verified outcome.

## 2. Meaning Of "Best From The Start"

"Best from the start" does not mean enabling every published technique simultaneously. Many methods are mutually exclusive, hardware-specific, architecture-specific, workload-specific, quality-altering, or beneficial only under particular residency states.

It means NexusNet ships with:

- a broad initial registry of proven inference primitives;
- portable correctness-first fallbacks;
- accelerator-specific implementations behind capability gates;
- runtime hardware calibration rather than vendor-name assumptions;
- model-structure discovery rather than model-ID recipes;
- an evidence-aware composition engine that chooses compatible traits;
- an ongoing research-intake and dream process that prevents the initial catalog from becoming a permanent ceiling.

An optimization is eligible at startup only when its capability predicate, compatibility rules, failure behavior, evidence contract, and rollback path are known. Unknown combinations remain candidates, not active production behavior.

## 3. Architectural Invariants

### 3.1 No per-model implementation paths

NexusNet may retain sanitized observations produced by a model, but it must not grow hard-coded execution branches keyed to a model name or repository ID.

Policies are keyed by transferable features such as:

- operator graph and dependency structure;
- dense, sparse-MoE, state-space, recurrent, convolutional, diffusion, or multimodal topology;
- tensor dimensions, layouts, dtypes, quantization metadata, and sparsity;
- attention, KV, routing, and state-retention behavior;
- required custom operators and kernel capabilities;
- hardware capability graph;
- workload phase, batch, context, modality, and SLO;
- observed bottleneck class and residency state.

A model ID may appear in provenance and integrity evidence. It cannot be the reason a policy is selected.

### 3.2 Hardware-neutral control, hardware-specialized execution

The control plane uses capability contracts rather than CUDA-, ROCm-, Metal-, Intel-, NPU-, CPU-, or vendor-specific assumptions. Execution primitives may be specialized, but each specialization declares the exact capabilities it requires and the portable fallback it preserves.

### 3.3 Pareto optimization, not one hidden scalar

Latency, throughput, memory, energy, thermals, quality, stability, and cost can conflict. NexusNet will maintain a Pareto frontier of verified plans rather than collapsing every objective into one permanent weighted score.

The active SLO chooses a point from that frontier. When no intent is available, NexusNet uses a balanced policy and records that default explicitly.

### 3.4 Reference behavior remains authoritative

Every optimized lane has a correctness-first reference path. A candidate cannot redefine model identity, routing semantics, requested precision, structured-output rules, privacy, or provider authority merely to improve a benchmark.

### 3.5 Dreaming produces candidates, not facts

Downtime research may generate hypotheses, configurations, policies, schedules, formats, compiler graphs, or kernel candidates. Nothing becomes active because it was dreamed. Promotion requires artifact trust, sandbox evidence, quality/equivalence evidence, performance evidence, monitoring, and rollback.

## 4. Scope And Decomposition

This is an umbrella architecture spanning multiple implementation projects. It must not be collapsed into one engine class or one implementation plan.

The implementation sequence is decomposed into:

1. **Capability and calibration foundation** — hardware graph, model execution fingerprint, portable microbenchmarks, and sanitized evidence.
2. **Inference primitive registry** — capability predicates, compatibility rules, fallbacks, and evidence contracts for current methods.
3. **Heterogeneous residency and transfer fabric** — weights, experts, KV pages, adapters, draft state, and multimodal tensors across accelerator memory, pinned RAM, pageable RAM, and storage.
4. **SLO and Pareto controller** — candidate composition, feasibility, shadow comparison, selection, drift detection, and rollback.
5. **Downtime dream laboratory** — hypothesis generation, experiment planning, sandbox execution, champion/challenger evaluation, and transferable evolution memory.
6. **Advanced kernel, decoding, distributed, and research assimilation** — specialized primitives promoted incrementally through the same contracts.

Each project receives its own implementation plan and evidence gates. This umbrella spec controls their shared boundaries and ordering.

### 4.1 Canon alignment and classification

This design is a cross-cutting umbrella architecture, not a claim that every described behavior is currently live.

- **Classification:** NexusNet-native architectural pattern, inference primitive portfolio, research-intake target, eval target, and governed autonomous-evolution target.
- **Earliest build layer:** Layer 11 for model attach and inference-harness integration.
- **Dream-loop dependency:** Layer 10 eval/sandbox/governance and Layer 12 recursive dreaming/self-repair must be verified before candidate invention can affect active runtime policy.
- **Research-radar dependency:** Continuous external discovery belongs to Layer 14 and cannot grant promotion authority.
- **Prerequisites:** authority, isolation, Neural Bus/HiveBlackboard, substrate ledgers, evidence/artifact trust, provenance/privacy, memory, operator visibility, and eval/sandbox/governance from earlier canon layers.
- **Current anchors:** the existing MoE residency runtime, inference architecture registry, cache and decision ledgers, workload scorecards, runtime router, dream queue, downtime scheduler, and autonomous update controller.
- **Blocked claims:** universal optimality, complete hardware coverage, production readiness of every listed method, automatic native-code promotion, and performance superiority without current controlled evidence.
- **Minimum evidence:** capability and calibration refs, model execution fingerprint, primitive digests, cold/warm performance, quality/equivalence, resource and thermal posture, failure/fallback evidence, monitoring, and rollback.
- **Visibility:** active plans, uncertainty, dream state, promotions, rejections, and rollback history must be visible through release Harness/control-panel surfaces before the behavior is considered live.
- **Rollback/sidebar rule:** every retired, rejected, failed, superseded, or hardware-incompatible candidate remains in historical evidence and cannot be silently rewritten as success.

## 5. Initial Assimilation Portfolio

NexusNet will assimilate mechanisms, not import external authority. The initial registry should cover the following families.

### 5.1 Memory, residency, and context reuse

| Source family | Transferable traits |
| --- | --- |
| PagedAttention and vLLM | Paged KV allocation, continuous batching, chunked prefill, prefix caching, phase-aware scheduling. |
| SGLang and RadixAttention | Radix-based reusable-prefix indexing, request-aware scheduling, hierarchical cache integration. |
| LMCache and HiCache | GPU/RAM/storage KV tiers, cache transfer contracts, reusable context beyond one process. |
| Mooncake and KV-centric serving | KV-aware scheduling and disaggregated cache movement. |
| KVTuner and adaptive KV quantization | Sensitivity-aware mixed precision for KV state. |
| DuoAttention, MInference, and SPIN-like research | Head- and pattern-aware long-context execution under quality gates. |
| HeadInfer and CLO | Head/page-granular KV offload, persistent hot state, prefetch, reduced CPU synchronization. |
| SparseX and quantized KV handoff research | Experimental segment reuse and agent-to-agent cache transfer behind strict provenance and correctness gates. |

### 5.2 Constrained-VRAM transfer and heterogeneous execution

| Source family | Transferable traits |
| --- | --- |
| CUDA and HIP best practices | Bounded pinned host pools, batched transfers, non-default copy streams, events, and copy/compute overlap. |
| FlexGen and ZeRO-Inference | Layer/tensor streaming, memory aggregation, transfer pipelining, and throughput-oriented placement. |
| PowerInfer | Hot/cold activation locality and CPU execution when movement would cost more than computation. |
| Endor | Compressed transfer representation and low-overhead accelerator-side reconstruction. |
| HOBBIT | Mixed-precision cache-miss fallback, layer-aware prefetch, and sequence-aware expert caching. |
| MoE-Lightning | CPU/GPU/I/O pipelines, paged weight movement, and bottleneck-aware scheduling. |
| APEX | Profile-informed overlap of CPU and GPU work during constrained-memory decode. |
| ATSInfer | Tensor-granular static placement plus load-aware dynamic transfer. |
| GPUDirect Storage and equivalent backends | Optional storage-to-accelerator paths that avoid CPU bounce buffers when certified. |

### 5.3 Quantization and compressed execution

The registry should support capability-described weight, activation, KV, and expert formats including:

- FP32, BF16, FP16, FP8, and supported FP4 families;
- INT8 and INT4 weight/activation combinations;
- GPTQ, AWQ, GGUF, compressed-tensors, TorchAO, and backend-native formats where rights and compatibility allow;
- rotation- or outlier-aware candidates such as QuaRot/SpinQuant-style methods;
- mixed-precision layer, head, expert, token, and tensor-group profiles;
- lossless or quality-altering compression with explicit distinction.

The fabric prefers the smallest quality-approved representation that has an efficient consuming kernel. A smaller format is not a win when conversion or dequantization costs outweigh saved movement and compute.

### 5.4 Kernels, compilation, and graph execution

Candidate backends include:

- eager portable reference execution;
- PyTorch compile/Inductor and AOT artifacts;
- CUDA/HIP graphs where shapes and lifetimes are safe;
- FlashAttention, FlashInfer, Triton, CUTLASS, and equivalent attention/GEMM kernels;
- fused normalization, RoPE, activation, sampling, and dequantization paths;
- grouped GEMM and fused MoE execution;
- DeepEP-like expert-parallel communication where supported;
- CPU vector, AMX, OpenVINO, IPEX, llama.cpp/GGML-style, Metal, and NPU backends under the same capability contract.

Compilation is measured after warmup and graph-break inspection. Cold compilation cost, cache reuse, shape specialization, correctness, and artifact portability are part of the scorecard.

### 5.5 Decoding and generation

The registry should initially understand:

- target-only autoregressive decoding;
- n-gram and suffix drafting;
- small draft-model speculation;
- EAGLE-family candidates where a compatible trusted drafter exists;
- LayerSkip/self-speculation where training and architecture requirements are satisfied;
- grammar-forced or structured-output drafts with target verification;
- adaptive draft length and automatic disablement on non-positive end-to-end benefit.

Acceptance rate alone is not sufficient. Promotion depends on end-to-end latency, throughput, additional memory, target work, output equivalence, structured-output behavior, and interaction with residency state.

### 5.6 Scheduling, batching, and distributed execution

The initial portfolio should include:

- continuous batching;
- chunked prefill;
- decode-priority and SLO-priority scheduling;
- adaptive batch and token budgets;
- prefill/decode disaggregation;
- data, tensor, pipeline, expert, and context parallelism;
- topology-aware communication over PCIe, NVLink, C2C, shared memory, network, or storage fabrics;
- multi-device placement that measures communication cost rather than assuming more devices are faster.

Distributed and disaggregated plans remain inactive on single-device systems. Their presence in the registry must impose no idle overhead.

## 6. Core Components

### 6.1 `HardwareCapabilityGraph`

This component discovers resources and relationships:

```text
device nodes
  CPU cores and vector features
  accelerator/NPU type and compute features
  VRAM, unified memory, RAM, storage, and cache capacities
  supported dtypes and kernel families
  copy engines and concurrent-execution capabilities
  power, temperature, and energy telemetry

link edges
  topology and locality
  measured latency and bandwidth by direction
  peer access and zero-copy support
  NUMA affinity
  storage and network paths
```

Discovery records both advertised and measured capabilities. Measured values win for planning. Missing telemetry produces uncertainty and conservative admission rather than invented precision.

### 6.2 `HardwareCalibrationLab`

Calibration runs bounded, portable probes for:

- pageable and pinned H2D/D2H transfer by chunk size;
- bidirectional and concurrent copy/compute behavior;
- allocator and synchronization overhead;
- representative GEMM, GEMV, attention, dequantization, sampling, and CPU kernels;
- storage read and optional direct-transfer behavior;
- compilation and warmup cost;
- energy and thermal response when telemetry exists.

Calibration is versioned by hardware, driver, runtime, operating system, power state, and significant configuration. Drift triggers selective remeasurement, not an unconditional full benchmark.

### 6.3 `ModelExecutionFingerprint`

The fingerprint describes executable characteristics without becoming a model recipe:

```text
graph_digest
operator_families[]
tensor_groups[]
state_and_kv_contract
sparsity_and_router_contract
precision_and_quantization_contract
dynamic_shape_contract
custom_operator_requirements[]
multimodal_contract
rights_and_artifact_refs[]
unknown_or_unsupported_features[]
```

The fingerprint is derived from trusted metadata, graph inspection, bounded probes, and artifact digests. Unknown custom code is not executed merely to complete discovery.

### 6.4 `InferencePrimitiveRegistry`

Every primitive declares:

```text
primitive_id and implementation_digest
capability_predicate
model_feature_predicate
workload_predicate
compatible_and_conflicting_primitives[]
resource_model
quality_semantics
warmup_and_calibration_contract
evidence_schema
failure_and_fallback_contract
rights_and_provenance_refs[]
promotion_state
```

The registry separates algorithm identity from backend implementation. For example, paged KV allocation can have CUDA, ROCm, Metal, CPU, and portable implementations while retaining one semantic contract.

### 6.5 `ExecutionPlanSynthesizer`

The synthesizer combines compatible primitives into feasible plans. It uses constraint solving and learned priors to prune invalid or clearly dominated combinations before benchmarking.

It must account for interactions. Examples:

- speculation can regress when its draft state displaces valuable KV or resident weights;
- aggressive KV caching can reduce batch capacity;
- low-bit transfer can lose its benefit when dequantization is not fused;
- CPU offload can help memory fit but harm every-token latency;
- compilation can help stable shapes and regress dynamic workloads;
- prefetch can improve hit rate while wasting bandwidth and energy.

No candidate is promoted from isolated component scores alone.

### 6.6 `HeterogeneousResidencyFabric`

The fabric generalizes the proven MoE tiering pattern across:

- dense weight groups;
- sparse experts;
- KV and reusable context pages;
- adapters and LoRA weights;
- draft-model and speculative state;
- multimodal encoder outputs and features;
- compiled kernels and graph artifacts.

Tiers include accelerator memory, unified memory, bounded pinned RAM, pageable RAM, local storage, and approved remote stores. Each asset type owns its placement semantics while sharing integrity, leases, coalescing, eviction, prefetch, telemetry, and rollback contracts.

The transfer engine supports batched contiguous movement, persistent pinned slabs, double/triple buffering, copy streams, events, adaptive prefetch depth, and compressed transit. Pinned memory is bounded because excessive pinning can degrade the host.

### 6.7 `DynamicSLOController`

The controller infers or receives objectives such as:

- interactive latency;
- throughput;
- context capacity;
- memory conservation;
- battery/energy;
- thermal stability;
- cost;
- deterministic or high-assurance execution.

Hard constraints are applied first. The controller then selects among nondominated verified plans. It records whether the SLO was explicit, inferred, or balanced-default.

### 6.8 `InferenceEvidencePlane`

Every plan records comparable evidence:

```text
hardware capability and calibration refs
model execution fingerprint ref
primitive and implementation digests
SLO and workload profile
TTFT, ITL, end-to-end latency, and throughput
VRAM, RAM, storage, and cache occupancy
bytes moved and effective bandwidth
copy/compute overlap and synchronization stalls
kernel utilization and compilation state
cache, residency, and prefetch outcomes
energy, power, and thermal metrics when available
quality, equivalence, determinism, and safety refs
failure, degradation, fallback, and rollback events
```

Raw prompts, outputs, secrets, personal data, and private paths are excluded from global learning artifacts. Workload features are sanitized and minimized.

### 6.9 `EvolutionMemory`

Evolution memory retains transferable relationships between capability features, model-graph features, workload features, chosen primitives, and verified outcomes.

It stores:

- global priors;
- hardware-family priors;
- graph-feature priors;
- primitive interaction effects;
- failure and incompatibility evidence;
- calibration drift;
- champion/challenger history;
- retired or superseded policies.

It does not store a lookup table of model ID to magic configuration. A new model starts from nearest feature-space evidence and remains uncertain until measured.

### 6.10 `InferenceDreamLab`

The dream lab runs only when capacity gates allow. It consumes sanitized evidence and produces candidates through:

- parameter search and Bayesian/multi-objective optimization;
- primitive recombination;
- schedule and placement mutation;
- transfer chunking and prefetch-depth experiments;
- precision and compression allocation experiments;
- compiler and fusion candidates;
- speculative-decoding policies;
- research-derived primitive proposals;
- counterfactual replay of bottleneck traces;
- adversarial workloads designed to expose regressions.

The lab compares current champion, portable reference, and challengers under identical conditions. It may update priors from failed experiments; it may not rewrite production truth from a failed or incomplete run.

## 7. Dual-Loop Data Flow

### 7.1 Live inference loop

```text
request and explicit/inferred SLO
  -> hardware capability and current-state snapshot
  -> model execution fingerprint
  -> feasible verified-plan frontier
  -> selected plan and declared fallback
  -> governed execution
  -> sanitized evidence and drift detection
  -> evolution memory update
  -> retain, degrade, or roll back plan
```

The live loop selects verified behavior. It does not generate and execute untrusted native code during a request.

### 7.2 Downtime dream loop

```text
idle-capacity, thermal, power, memory, and budget gate
  -> bottleneck and opportunity mining
  -> hypothesis and candidate generation
  -> feasibility and artifact-trust screening
  -> isolated sandbox build/calibration
  -> reference/champion/challenger benchmark
  -> quality, safety, and Pareto evaluation
  -> candidate dossier and rollback plan
  -> shadow/canary promotion gate
  -> monitored activation or rejection
  -> transferable evolution-memory update
```

Serving demand preempts dream work. The scheduler must cancel or checkpoint safely without leaving partial production artifacts.

## 8. Promotion And Autonomy Boundary

### 8.1 Automatically promotable

Reversible runtime policies may promote automatically after all gates pass, including:

- cache sizing within admitted bounds;
- prefetch depth and scheduling;
- selection among already trusted kernel implementations;
- batching and chunking parameters;
- residency placement and eviction policies;
- selection among already certified precision profiles;
- speculation enablement and draft length;
- SLO selection and Pareto-frontier choice.

Automatic promotion still requires shadow evidence, a declared rollback, post-promotion monitoring, and immediate regression response.

### 8.2 Approval required

The following require explicit approval after sandbox and eval evidence:

- new native executable code or kernels;
- new privileged plugins or runtime dependencies;
- changes to model weights or training artifacts;
- quality-altering transformations outside previously approved bounds;
- new remote execution, storage, or data-sharing boundaries;
- relaxation of privacy, artifact-trust, authority, or rollback controls;
- irreversible or schema-breaking production mutations.

### 8.3 Never permitted

The dream lab cannot:

- use raw private prompts or outputs as unrestricted optimization material;
- silently substitute a different model or provider;
- falsify benchmark evidence or omit cold-start costs;
- promote an unverified method because a paper or upstream benchmark reports a gain;
- disable monitoring, rollback, or policy gates;
- treat failure to measure as evidence of safety or performance.

## 9. Current NexusNet Integration Seams

The design extends current surfaces rather than creating another authority plane:

- `nexusnet/runtime/moe_residency/` is the first working residency primitive and should become a consumer of shared transfer/capability contracts rather than remain the universal abstraction.
- `nexusnet/runtime/inference_architecture.py` is the plan and strategy surface to evolve from shadow descriptions toward evidence-linked candidate composition.
- `nexusnet/runtime/cache_ledger.py` and runtime workload scorecards provide existing evidence and promotion patterns.
- `nexusnet/runtime/decision_ledger.py` already combines route, cache, quantization, and eval state.
- `nexusnet/runtime/inference_economy_router.py` is the live request/SLO and route-admission seam.
- `nexusnet/research/forward_radar.py::schedule_downtime_benchmark` already gates downtime work on serving, temperature, free VRAM, release state, and budget, but its current packet is a model-candidate dry run with benchmark execution prohibited.
- `nexusnet/core/autonomous_updates.py::AutonomousUpdateController` already provides proposal, eval replay, sandbox, approval, monitoring, safe apply, and rollback controls.
- `nexusnet/release_wrapper.py::_queue_dream_research_improvement` already converts sanitized runtime evidence into governed dream-research proposals.

The inference dream lab should bind these seams. It must not create an ungoverned second self-improvement pipeline.

## 10. Failure And Degradation Semantics

| Condition | Required behavior |
| --- | --- |
| Unknown model structure | Use the portable reference for supported operators; quarantine unsupported custom operations; collect bounded discovery evidence. |
| Missing optimized backend | Remove that primitive implementation from feasible plans; retain semantic fallback. |
| Calibration failure | Mark affected measurements uncertain; use conservative advertised bounds and reference execution. |
| Driver, runtime, or hardware drift | Invalidate only affected calibrations and compiled artifacts; remeasure selectively. |
| Accelerator OOM | Stop new allocations/transfers, release safe candidates, record plan violation, and activate the declared fallback. |
| Thermal, energy, or battery limit | Preempt dream work first; then choose a verified constrained policy or degrade visibly. |
| Quality or equivalence regression | Reject or roll back the candidate regardless of speed. |
| Performance regression | Return to the previous champion and retain the failed evidence as a negative prior. |
| Corrupt evolution memory | Ignore incompatible records, rebuild from signed evidence, and continue from portable priors. |
| Dream sandbox failure | Quarantine outputs; no production mutation; persist sanitized failure evidence. |
| New native kernel fails trust or review | Keep it sandbox-only and continue with trusted implementations. |

## 11. Testing Strategy

### 11.1 Contract tests

- Capability discovery is deterministic for a supplied hardware fixture.
- Model fingerprints depend on graph/tensor features, not model names.
- Primitive predicates accept and reject the intended capability combinations.
- Conflicting primitives cannot compose into one plan.
- Every optimized primitive declares and exercises a fallback.

### 11.2 Correctness and quality tests

- Reference and optimized paths meet declared equivalence tolerances.
- Structured output, tool calling, stop behavior, and determinism contracts survive optimization.
- Quantized, sparse, speculative, and offloaded lanes cannot hide quality deltas.
- Unknown/custom operators fail closed.

### 11.3 Performance tests

- Cold start, warm start, steady state, and drift are measured separately.
- Transfer, conversion, compilation, synchronization, and prefetch waste are included.
- Candidate comparisons use the same workload and hardware state.
- Reported improvements include uncertainty and repeat counts.
- Multi-objective results preserve the Pareto frontier rather than only a single score.

### 11.4 Hardware simulation and fixture tests

- CPU-only, unified-memory, low-VRAM discrete GPU, high-VRAM GPU, multi-GPU, and constrained edge profiles.
- Slow/fast PCIe or equivalent links, NUMA penalties, limited RAM, and storage-backed cases.
- Missing telemetry and unsupported-dtype cases.
- Thermal throttling, memory pressure, and serving preemption.

### 11.5 Dream and promotion tests

- Dream work never starts while capacity gates are closed.
- Serving demand checkpoints or cancels dream work safely.
- Failed candidates cannot promote.
- Automatically promotable policies still require evidence and rollback.
- Native code and irreversible changes cannot bypass approval.
- Restart replay preserves champion, challenger, rejected, and rollback history without raw-content leakage.

## 12. Observability And Operator Truth

The release Harness and control panel should expose:

- current hardware capability and calibration state;
- current model execution fingerprint summary;
- selected SLO and whether it was explicit, inferred, or defaulted;
- active primitives and fallback plan;
- live Pareto frontier and selected point;
- current bottleneck classification;
- cold/warm residency state;
- transfer, cache, kernel, quality, energy, and thermal evidence;
- dream capacity gate and current experiment;
- champion/challenger history;
- promotions, rejections, degradations, and rollbacks;
- stale or uncertain evidence.

NexusNet must not claim it is optimal. It may claim that a plan is the best currently verified nondominated option for a declared hardware snapshot, workload, SLO, and evidence set.

## 13. Research Intake And Freshness

The initial portfolio will age. The forward radar therefore needs an inference-method lane that:

1. discovers new papers, kernels, runtimes, formats, and hardware capabilities;
2. records source, license, provenance, claimed gains, assumptions, and reproducibility;
3. extracts transferable traits rather than copying whole systems;
4. maps traits to primitive contracts and missing capability predicates;
5. proposes sandbox experiments against current champions;
6. rejects methods whose gains do not reproduce locally;
7. retires or sidebars superseded primitives without deleting historical evidence.

External benchmarks are discovery evidence. Only NexusNet-controlled measurements can promote a trait.

## 14. First Implementation Project

The first implementation plan after approval should build the smallest foundation that makes later assimilation real:

1. `HardwareCapabilityGraph` schema and portable CPU/RAM/storage discovery.
2. Optional CUDA/ROCm/Metal capability adapters that degrade cleanly when unavailable.
3. Bounded calibration for memory capacity, transfer behavior, and representative compute.
4. `ModelExecutionFingerprint` schema and a trusted synthetic-model fixture path.
5. `InferencePrimitiveRegistry` with the portable reference plus the already implemented MoE residency primitive represented through shared contracts.
6. A candidate feasibility result and evidence artifact; no live policy mutation yet.
7. Runtime-visible status and focused tests proving sanitized restart-safe evidence.

This slice creates the universal language the residency, SLO, Pareto, and dream projects require. It must not start by hard-coding more model-specific optimizations.

## 15. Acceptance Criteria For The Umbrella Architecture

The evolutionary inference fabric is not considered realized until NexusNet can demonstrate all of the following:

1. An unseen supported model is fingerprinted and admitted without model-ID-specific code.
2. The same model receives materially different verified plans on meaningfully different hardware.
3. Different SLOs select different nondominated plans on the same hardware.
4. A constrained-VRAM lane measures and improves transfer/compute overlap without hiding quality or cold-start cost.
5. An optimized primitive fails and NexusNet automatically returns to its declared reference behavior.
6. A downtime dream experiment produces a challenger, sandbox evidence, a Pareto comparison, and either a governed promotion or recorded rejection.
7. A successful outcome improves transferable priors used by a later model or hardware profile.
8. A failed outcome becomes a negative prior rather than being silently discarded.
9. Native executable candidates cannot bypass approval.
10. The control panel exposes current state, uncertainty, evidence, and rollback truth without raw-content leakage.

## 16. Primary Research And Runtime References

- [vLLM documentation](https://docs.vllm.ai/en/stable/)
- [SGLang](https://github.com/sgl-project/sglang)
- [SGLang/RadixAttention paper](https://arxiv.org/abs/2312.07104)
- [LMCache](https://github.com/LMCache/LMCache)
- [FlexGen](https://arxiv.org/abs/2303.06865)
- [PowerInfer](https://arxiv.org/abs/2312.12456)
- [HOBBIT](https://arxiv.org/abs/2411.01433)
- [MoE-Lightning](https://arxiv.org/abs/2411.11217)
- [Endor](https://arxiv.org/abs/2406.11674)
- [APEX](https://arxiv.org/abs/2506.03296)
- [ATSInfer](https://arxiv.org/abs/2607.10183)
- [CLO](https://arxiv.org/abs/2511.14510)
- [HeadInfer](https://arxiv.org/abs/2502.12574)
- [KVTuner](https://arxiv.org/abs/2502.04420)
- [DuoAttention](https://arxiv.org/abs/2410.10819)
- [MInference](https://arxiv.org/abs/2407.02490)
- [EAGLE-3](https://arxiv.org/abs/2503.01840)
- [LayerSkip](https://arxiv.org/abs/2404.16710)
- [DistServe](https://arxiv.org/abs/2401.09670)
- [Mooncake](https://arxiv.org/abs/2407.00079)
- [DeepEP](https://github.com/deepseek-ai/DeepEP)
- [FlashInfer](https://github.com/flashinfer-ai/flashinfer)
- [PyTorch compile documentation](https://docs.pytorch.org/docs/stable/generated/torch.compile.html)
- [NVIDIA CUDA Best Practices](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
- [AMD HIP asynchronous execution](https://rocm.docs.amd.com/projects/HIP/en/docs-7.0.0/how-to/hip_runtime_api/asynchronous.html)
- [NVIDIA GPUDirect Storage](https://docs.nvidia.com/gpudirect-storage/overview-guide/index.html)

These references seed the initial portfolio. They do not exhaust or permanently define the methods NexusNet may assimilate.
