# NexusNet Evolutionary Inference Fabric Design

**Date:** 2026-07-14

**Last amended:** 2026-07-18

**Status:** Approved umbrella architecture; universal assimilation, execution-fit, runtime-control, and Pareto amendment approved

**Authority:** NexusBrain

**Baseline:** `fadac0d9`

**Amendment baseline:** `9b3a6a65`

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

The 2026-07-18 amendment makes three decisions explicit:

1. fit/admission, complete runtime control, live execution, and measured reconciliation are one cumulative A-C loop rather than alternative implementation choices;
2. inference assimilation is dual-path: whole external engines remain executable baselines and fallbacks while their transferable mechanisms may also become typed primitives for Nexus-native composition;
3. a Nexus-native inference method is an executable graph owned, compiled, admitted, controlled, and measured by NexusNet, not merely a route to the currently fastest external engine.

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

### 3.6 External engines are participants, not the architecture

llama.cpp, vLLM, SGLang, TensorRT-LLM, Transformers, ONNX Runtime, OpenVINO, MLC, MLX, ExLlama, Ollama, vendor runtimes, remote OpenAI-compatible runtimes, and future engines may enter through capability-discovered adapters. No adapter defines the universal control plane. Engines provide immediate execution, comparison baselines, fallbacks, and technique sources.

The registry is open-ended. Supporting future methods must require a versioned method record and adapter or primitive implementation, not edits to a closed list of privileged runtimes.

### 3.7 Fit, admission, control, execution, and reconciliation are inseparable

Every external-engine plan and Nexus-native graph passes the same cumulative loop:

```text
model and workload fingerprint
  -> hardware and runtime capability snapshot
  -> model-aware fit calculation
  -> admitted execution-fit receipt
  -> complete supported-control binding
  -> governed live execution
  -> measured reconciliation
  -> Pareto evidence and evolution-memory update
```

Prediction without live binding, runtime controls without fit admission, and execution without reconciliation are incomplete states. Unsupported controls must be rejected or surfaced as degraded; they cannot disappear silently.

### 3.8 Superiority is scoped Pareto evidence

NexusNet never claims one method is universally best. A candidate may be called superior only for the tested model fingerprint, quantization, hardware and topology snapshot, runtime and driver versions, workload, context range, SLO, and benchmark policy.

Quality, correctness, safety, rights, reproducibility, and stability are hard gates. Among candidates that pass them, a promoted challenger must materially improve at least one governed objective such as latency, throughput, memory, energy, thermal behavior, capacity, stability, or cost while every other protected objective stays within its declared regression tolerance. Without a compatible locally measured baseline, the candidate remains experimental or promising and cannot be labeled superior.

## 4. Scope And Decomposition

This is an umbrella architecture spanning multiple implementation projects. It must not be collapsed into one engine class or one implementation plan.

The implementation sequence is decomposed into:

1. **Capability and calibration foundation** — hardware graph, model execution fingerprint, portable microbenchmarks, and sanitized evidence.
2. **Dual-path method assimilation** — provenance-bound whole-engine records, reusable primitive extraction, adapter conformance, rights gates, and external-baseline execution.
3. **Inference primitive registry and universal IR** — capability predicates, compatibility rules, fallbacks, evidence contracts, executable graph semantics, and backend-independent plan identity.
4. **Cumulative A-C execution control** — model-aware RAM/VRAM/KV/MoE fit, pre-dispatch admission, complete capability-gated controls, live binding, and measured reconciliation.
5. **Heterogeneous residency and transfer fabric** — weights, experts, KV pages, adapters, draft state, and multimodal tensors across accelerator memory, pinned RAM, pageable RAM, and storage.
6. **Nexus-native graph compiler** — lowering, scheduling, placement, memory lifetime, synchronization, portable execution, and approved hardware-specific implementations.
7. **SLO and Pareto controller** — candidate composition, feasibility, equivalent-condition comparison, selection, drift detection, and rollback.
8. **Downtime dream laboratory** — hypothesis generation, experiment planning, sandbox execution, champion/challenger evaluation, and transferable evolution memory.
9. **Advanced kernel, decoding, distributed, and research assimilation** — specialized primitives promoted incrementally through the same contracts.

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

### 6.4.1 `InferenceMethodRecord` And Assimilation Gateway

Every assimilated method receives one provenance-bound record before it can affect planning:

```text
method_id and version
source_kind: external-engine | primitive-family | nexus-native-graph
source and artifact digests
license, inference, evaluation, derivative, and redistribution rights
claimed capabilities and upstream evidence
locally reproduced capabilities and evidence
supported models, operators, formats, precisions, and hardware
tunable controls and control semantics
known conflicts, fallbacks, and failure classes
assimilation maturity: researched | adapted | reproduced | primitive-extracted | native | certified
```

The gateway may retain a complete engine, extract reusable semantic primitives, or do both. External claims remain discovery evidence until reproduced. Incompatible rights block code or artifact assimilation while still allowing an appropriately bounded research note when policy permits.

### 6.4.2 `BackendFederation` And `RuntimeCapabilityProfile`

Each runtime adapter publishes a versioned capability profile discovered from the installed implementation rather than copied from generic upstream documentation. The profile covers model and format support, controllable parameters, quantization and KV formats, scheduling and batching, placement and offload, observability, cancellation, failure semantics, and reference-output behavior.

For each requested control, the adapter must report exactly one binding outcome: `applied`, `degraded`, `unsupported`, or `rejected`. A successful API call is not proof that the requested execution method was used.

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

### 6.5.1 `UniversalInferenceIR`

The universal IR is a typed executable graph independent of any one runtime. It represents:

- operator semantics, shapes, layouts, precision, and quantization;
- weights, experts, KV pages, activations, adapters, and temporary memory lifetimes;
- device and tier placement, transfers, prefetch, eviction, and reuse;
- prefill, decode, batching, speculation, routing, and distributed schedules;
- synchronization, cancellation, failure, and fallback boundaries;
- quality semantics, required evidence, and reversible parameters.

An external adapter may execute an entire plan, a primitive implementation may satisfy one IR node family, and NexusNet may compile a mixed graph from both. Plan identity binds the graph, primitive and implementation digests, model fingerprint, hardware snapshot, runtime capabilities, and control parameters.

### 6.5.2 `NexusNativeGraphCompiler`

The compiler validates and lowers universal graphs into a portable correctness-first executor or approved hardware-specific implementations. Its first responsibility is semantic preservation and observable control binding, not novel kernel generation. Native kernel generation becomes an additional lowering path only after artifact trust, sandbox, equivalence, benchmark, approval, monitoring, and rollback gates exist.

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

### 6.6.1 `ExecutionFitRequest` And `ExecutionFitReceipt`

The fit estimator is deterministic and side-effect free. Its request binds the model execution fingerprint, requested prompt/output/context and concurrency, quantization, hardware snapshot, runtime capability profile, candidate plan, and admission policy.

The immutable sanitized receipt records:

```text
receipt, plan, model, hardware, runtime, and benchmark-policy identities
decision: admitted | degraded | rejected
machine-readable reason codes
requested, selected, and safe context
dense weights, expert weights, KV-per-token, total KV, buffers, and headroom
GPU/accelerator, unified-memory, RAM, and storage placement
predicted bottleneck and performance range with uncertainty
every requested control, its evidence source, support state, and binding outcome
declared fallback and rollback trigger
```

Dense and MoE calculations distinguish total resident parameters from active per-token parameters. KV-cache cost is derived from model structure, precision, batch, and context instead of static RAM/VRAM thresholds. The pre-dispatch gate consumes the receipt before model load or provider/kernel execution.

The cumulative control surface includes, when a runtime supports them, context, output limit, weight and KV quantization, K/V cache types, generation and batch threads, batch and micro-batch sizes, GPU/accelerator layers, split mode, tensor split or override, expert placement and CPU/RAM offload, memory mapping/locking, scheduling, speculation, cache/reuse, distributed placement, and runtime-specific equivalents. Capability discovery, not a hard-coded llama.cpp vocabulary, determines binding.

### 6.6.2 `ExecutionFitObservation` And Reconciler

The observation binds to the receipt and records sanitized actual allocation, context achieved, TTFT, inter-token latency, throughput, utilization, transfers, cache/residency behavior, energy/thermals when available, control-binding proof, degradation, and failure. The reconciler classifies prediction error, invalidates stale assumptions, updates bounded transferable evidence, and triggers fallback or rollback when live behavior violates the receipt.

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
  -> runtime capability profiles and method registry
  -> external-engine and Nexus-native candidate frontier
  -> execution-fit request and pre-dispatch admission
  -> selected plan, complete control bindings, and declared fallback
  -> governed external-adapter or Nexus-native-graph execution
  -> fit observation, reconciliation, and drift detection
  -> evolution memory update
  -> retain, degrade, or roll back plan
```

The live loop selects verified behavior. It does not generate and execute untrusted native code during a request.

### 7.2 Downtime dream loop

```text
idle-capacity, thermal, power, memory, and budget gate
  -> external-method intake and bottleneck/opportunity mining
  -> whole-engine baseline adaptation and primitive extraction
  -> Nexus-native graph hypothesis and candidate generation
  -> feasibility and artifact-trust screening
  -> execution-fit admission and isolated sandbox build/calibration
  -> equivalent-condition reference/champion/challenger benchmark
  -> hard-gate validation and scoped Pareto evaluation
  -> candidate dossier and rollback plan
  -> shadow/canary promotion gate
  -> monitored activation or rejection
  -> transferable evolution-memory update
```

Serving demand preempts dream work. The scheduler must cancel or checkpoint safely without leaving partial production artifacts.

## 8. Promotion And Autonomy Boundary

### 8.0 Pareto promotion contract

Benchmark policy declares the protected objectives, permitted regression tolerance per objective, minimum material improvement, repetitions, warmup handling, confidence rule, workload corpus, and environmental controls before results are observed. A candidate is eligible for the verified frontier only when all hard gates pass and the comparison is complete.

Promotion requires a material improvement in at least one governed objective with no protected objective outside its declared tolerance. Results that trade advantages without dominating under the active policy may remain nondominated alternatives for a different SLO, but they cannot be described as globally better. Missing, corrupt, interrupted, thermally incomparable, or selectively omitted measurements invalidate the superiority claim.

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

- `nexusnet/runtime/evolutionary_inference/` already provides schemas, primitives, feasibility, synthesis, benchmarking, Pareto selection, dream, promotion, transfer, evidence, and system orchestration. These are the authoritative extension points for this amendment.
- `nexus/runtimes/registry.py` already federates mock, Ollama, OpenAI-compatible, vLLM, LM Studio, Transformers, and llama.cpp adapters. It should evolve toward capability profiles and conformance rather than embedding one preferred engine into the planner.
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
| Unknown or stale runtime capability | Do not bind the affected control; reject or degrade the receipt explicitly and schedule bounded rediscovery. |
| Adapter reports success without binding proof | Mark the control and run unverified, quarantine its performance evidence, and prevent superiority or promotion claims. |
| Adapter disagreement with reference behavior | Quarantine the adapter/version and its evidence; retain other runtimes and the correctness-first path. |
| Calibration failure | Mark affected measurements uncertain; use conservative advertised bounds and reference execution. |
| Driver, runtime, or hardware drift | Invalidate only affected calibrations and compiled artifacts; remeasure selectively. |
| Accelerator OOM | Stop new allocations/transfers, release safe candidates, record plan violation, and activate the declared fallback. |
| Thermal, energy, or battery limit | Preempt dream work first; then choose a verified constrained policy or degrade visibly. |
| Quality or equivalence regression | Reject or roll back the candidate regardless of speed. |
| Performance regression | Return to the previous champion and retain the failed evidence as a negative prior. |
| Corrupt evolution memory | Ignore incompatible records, rebuild from signed evidence, and continue from portable priors. |
| Dream sandbox failure | Quarantine outputs; no production mutation; persist sanitized failure evidence. |
| New native kernel fails trust or review | Keep it sandbox-only and continue with trusted implementations. |
| Incomplete or incomparable benchmark | Persist the run as invalid evidence; do not update the verified frontier or promote. |
| No compatible measured baseline | Keep the candidate experimental; do not claim superiority. |

## 11. Testing Strategy

### 11.1 Contract tests

- Capability discovery is deterministic for a supplied hardware fixture.
- Model fingerprints depend on graph/tensor features, not model names.
- Primitive predicates accept and reject the intended capability combinations.
- Conflicting primitives cannot compose into one plan.
- Every optimized primitive declares and exercises a fallback.
- Method records preserve provenance, rights, version, maturity, and local reproduction state.
- Runtime adapters report `applied`, `degraded`, `unsupported`, or `rejected` for every requested control.
- Universal IR rejects invalid types, shapes, lifetimes, placements, conflicts, and unsupported lowerings.
- Execution-fit receipts are immutable, sanitized, identity-bound, and deterministic for fixed inputs.

### 11.2 Correctness and quality tests

- Reference and optimized paths meet declared equivalence tolerances.
- Structured output, tool calling, stop behavior, and determinism contracts survive optimization.
- Quantized, sparse, speculative, and offloaded lanes cannot hide quality deltas.
- Unknown/custom operators fail closed.
- Portable, whole-engine, and Nexus-native executions meet the same declared output contract.

### 11.3 Performance tests

- Cold start, warm start, steady state, and drift are measured separately.
- Transfer, conversion, compilation, synchronization, and prefetch waste are included.
- Candidate comparisons use the same workload and hardware state.
- Reported improvements include uncertainty and repeat counts.
- Multi-objective results preserve the Pareto frontier rather than only a single score.
- A superiority label requires a compatible baseline, complete measurements, a material improvement, and no protected regression outside policy tolerance.
- Model-aware weight, KV, buffer, headroom, and MoE fit predictions are reconciled against measured allocation.
- Verified receipt parameters reach the real adapter or native graph; silent control loss fails the test.

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
- External method intake can produce both an executable baseline adapter and separately governed reusable primitives.
- At least one Nexus-native graph competes against external baselines and remains a candidate unless its local Pareto evidence passes.

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

## 14. Next Implementation Project

The capability, fingerprint, primitive, feasibility, synthesis, benchmark, Pareto, evidence, and dream foundations now exist in the repository and must be verified rather than recreated. The next implementation plan should deliver one runtime-visible universal-method vertical slice:

1. extend the existing method/primitive contracts with dual-path source, rights, maturity, capability-profile, and binding-evidence fields;
2. add versioned capability and conformance profiles for every adapter currently registered in `nexus/runtimes/registry.py`, with unavailable features degrading honestly;
3. implement deterministic `ExecutionFitRequest`, `ExecutionFitReceipt`, and `ExecutionFitObservation` contracts using model-aware weight, KV, buffer, headroom, quantization, dense/MoE, and heterogeneous-placement calculations;
4. place the fit/admission gate before actual adapter, provider, model-load, or native-kernel execution;
5. bind all supported controls through backend-neutral intent and record each adapter's applied, degraded, unsupported, or rejected outcome;
6. introduce the smallest portable `UniversalInferenceIR` and `NexusNativeGraphCompiler` lane capable of executing one correctness-first candidate graph rather than routing to an external engine;
7. run the Nexus-native graph and at least two available external-engine baselines through the same benchmark policy, output contract, receipt, and observation path;
8. compute a scoped Pareto frontier, refuse superiority claims without complete local evidence, and retain negative results;
9. expose sanitized method, fit, binding, benchmark, frontier, degradation, and rollback receipts through the existing runtime-visible surface;
10. prove restart, failure, fallback, and rollback behavior with focused red/green tests and a live smoke on the hardware actually available.

This slice is intentionally vertical: it must prove assimilation, fit, runtime control, Nexus-native execution, comparison, and reconciliation together. It must not hard-code a preferred runtime, duplicate the evolutionary fabric, or claim coverage for engines and hardware that were not exercised.

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
11. A newly registered external method can enter as a whole-engine baseline, reusable primitives, or both without becoming architectural authority.
12. Every external and Nexus-native plan passes the same model-aware fit, pre-dispatch admission, control-binding, execution, and reconciliation loop.
13. A Nexus-native executable graph competes against compatible external engines under one benchmark policy and output contract.
14. A superiority claim is scoped, locally reproduced, materially better on at least one objective, and within tolerance on every protected objective.
15. Unsupported or silently unbound runtime controls prevent verified-promotion claims and surface an honest degraded or rejected receipt.

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
