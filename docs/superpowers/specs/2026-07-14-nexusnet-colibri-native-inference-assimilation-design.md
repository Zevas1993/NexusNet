# NexusNet Colibrì Native Inference Assimilation Design

**Date:** 2026-07-14

**Status:** Approved architecture; implementation not yet started

**Authority:** NexusBrain

**NexusNet baseline:** `ea22b256af4d0821e3e723ed637a8a94be42790b`

**Reviewed Colibrì source:** `JustVugg/colibri@748787c3afa8ab336bb51bf616f212a04f209bba`

**License boundary:** Hybrid assimilation. NexusNet owns the interfaces and execution architecture. Small, isolated Apache-2.0 algorithms may be ported only with source-level attribution, provenance, and focused tests.

## 1. Decision

NexusNet will assimilate the transferable inference mechanisms demonstrated by Colibrì into its own native runtime. NexusNet will not add Colibrì as a provider, server, CLI, subprocess, runtime dependency, or alternate authority.

The assimilation target is a generic, model-aware sparse-MoE inference layer that can place expert tensors across GPU memory, system RAM, and local storage; learn which experts should remain hot; overlap expert movement with computation; prefetch likely future experts; and enable verified speculative acceleration only where local evidence shows a net benefit.

The work extends the actual `NexusNetLM` and `MoECapsuleLayer` inference lineage while preserving:

- NexusBrain authority;
- exact existing routing and output semantics in the lossless path;
- the resident in-memory path as the reference and rollback implementation;
- current training behavior until an independently designed training-tiering phase is approved;
- evidence-gated promotion per hardware, model, workload, context, and quality tier.

## 2. Why This Is Assimilation, Not Integration

Colibrì is an external implementation specialized around GLM-5.2 execution. NexusNet needs the reusable traits, not another product boundary.

Assimilation means:

- extracting testable runtime traits;
- translating them into NexusNet genome units and contracts;
- reproducing their benefit on NexusNet models and hardware;
- retaining only traits that survive correctness, quality, performance, provenance, and rollback gates;
- making the result evolvable by NexusNet rather than coupled to the source project's lifecycle.

It explicitly does not mean:

- routing requests to a Colibrì OpenAI-compatible endpoint;
- shelling out to `coli`;
- importing Colibrì's server or queue;
- treating video demonstrations or upstream benchmarks as NexusNet evidence;
- cloning GLM-specific tensor assumptions into NexusNet's generic core;
- enabling quality-altering expert skipping by default.

This matches the universal evolution canon: inference methods are assimilation inputs, and a successful trait promotes only after profile-specific evidence.

## 3. Evidence Reviewed

The review used two independent evidence levels.

### 3.1 Demonstration evidence

The two requested videos demonstrated and explained:

- a dense core kept resident while sparse experts are fetched from storage;
- large differences between cold and warmed expert-cache behavior;
- a multi-tier GPU/RAM/storage model;
- expert usage locality and hot-expert pinning;
- speculative and prefetch mechanisms intended to hide storage latency.

The videos are discovery evidence only. Their throughput and hit-rate displays are not accepted as NexusNet performance claims.

### 3.2 Primary source evidence

The reviewed Colibrì revision contains:

- dense-versus-expert resource planning in `c/resource_plan.py`;
- hysteretic frequency/recency tier selection and heat decay in `c/tier.h`;
- buffered/direct storage and prefetch mechanics in `c/st.h`;
- asynchronous expert load/matmul overlap, router-guided prefetch, usage persistence, and request-boundary repinning in `c/glm.c`;
- target-verified grammar drafts in `docs/grammar-draft.md`;
- adaptive speculative shutoff and experimental evidence that MTP can regress fully resident execution;
- an Apache-2.0 repository license.

The primary source therefore supports the mechanisms, but it also confirms that several optimizations are workload- and residency-dependent. NexusNet must autotune them rather than canonize them as universal wins.

## 4. Current NexusNet Foundations

NexusNet already has important native foundations:

- `nexusnet/hive/net/model.py::MoECapsuleLayer` implements a learned sparse top-k router and real expert computation.
- `nexusnet/hive/net/lm.py::NexusNetLM` implements the native causal language-model path.
- `nexusnet/hive/net/inference_runtime.py` contains correctness-preserving greedy speculative decoding, prefix caching, continuous batching, and KV accounting.
- `nexusnet/runtime/inference_architecture.py` records runtime acceleration plans.
- `nexusnet/runtime/cache_ledger.py` records KV and prefix-cache evidence.
- `nexusnet/runtime/workload_scorecards.py` gates runtime claims on latency, throughput, memory, cache, evaluation, trace, and hardware evidence.
- `nexusnet/models/runtime_planner.py` provides a model/runtime planning seam, although its current memory model is not MoE-residency aware.
- `nexusnet/growth/production_spine.py::RuntimeQuantizationBenchmarkRunner` provides a benchmark-and-promotion pattern.
- `nexusnet/core/native_execution.py::NativeExecutionPlanner` preserves NexusBrain authority, bounded execution, evidence linkage, fallback, and rollback.

The missing layer is not sparse routing itself. It is physical expert-tensor residency and evidence-driven execution beneath that routing.

## 5. Goals

### 5.1 Primary goals

1. Run native sparse-MoE models whose total expert weights exceed available accelerator memory when the dense core and minimum working set fit the admitted hardware profile.
2. Reduce expert-load stalls by learning workload-local expert demand and keeping valuable experts in faster tiers.
3. Overlap storage, host transfer, accelerator transfer, and expert computation where the platform permits it.
4. Prefetch without changing router decisions or model outputs.
5. Expand speculative decoding into an adaptive, measured acceleration policy with target verification and automatic disablement.
6. Make cold, warm, degraded, and fallback states operator-visible and replayable.
7. Preserve exact provenance for every externally derived algorithm.

### 5.2 Secondary goals

- Make the runtime generic enough for future NexusNet-native MoE generations and attached compatible MoE models.
- Allow the Everything State and Runtime Genome to evolve residency, prefetch, speculation, quantization, and scheduling policies independently.
- Create evidence that can later justify native kernels or model-specific compiler work.

## 6. Non-Goals

This design does not:

- add or vendor the Colibrì server/runtime;
- make GLM-5.2 a NexusNet core-brain replacement;
- implement training-time expert swapping;
- promise useful speed when every token requires cold storage reads;
- treat direct I/O, MTP, low-bit expert storage, or prefetch as universally beneficial;
- relax model rights, artifact trust, checkpoint, governance, or promotion requirements;
- silently substitute a different model, expert, precision, or provider when the requested route cannot run.

## 7. Architecture

```text
NexusBrain runtime decision
  -> MoE residency admission and plan
  -> dense-core and expert-manifest attachment
  -> NexusNetLM forward/decode
       -> exact sparse router decision
       -> demand acquisition for selected experts
       -> optional cancelable prefetch for future experts
       -> tiered expert execution
       -> exact aggregation of selected expert outputs
  -> verified token output
  -> expert-residency and speculation evidence
  -> workload scorecard and runtime-genome candidate
  -> shadow/canary/promotion/rollback lifecycle
```

### 7.1 Runtime package boundary

The proposed native package is:

```text
nexusnet/runtime/moe_residency/
  schemas.py
  manifest.py
  planner.py
  store.py
  heat.py
  prefetch.py
  execution.py
  speculation.py
  evidence.py
  provenance.py
```

Names are design-level and may be adjusted during implementation planning, but responsibilities must remain separated. Planning, movement, routing, computation, speculation, and evidence must not collapse into one engine class.

### 7.2 Reference path and optimized path

The existing fully resident execution remains the reference backend. A new expert-execution boundary will allow two implementations:

- `ResidentExpertExecutionBackend`: reproduces the current direct `ModuleList` behavior.
- `TieredExpertExecutionBackend`: resolves selected experts through the tiered store before executing them.

The routing function remains logically prior to the execution backend. The backend receives selected expert IDs and gate weights; it cannot change them in the lossless profile.

Training uses the resident backend in the first implementation generation. Exported or inference-attached models may use tiered manifests. This avoids unloading live optimizer parameters or changing autograd semantics.

## 8. Core Data Contracts

### 8.1 `ExpertTensorManifest`

One immutable manifest identifies the physical expert representation:

```text
manifest_id
model_ref
model_digest
architecture_family
format
dense_tensor_refs[]
expert_records[]
  layer_id
  expert_id
  tensor_names[]
  byte_ranges[]
  dtype_or_quantization
  uncompressed_bytes
  stored_bytes
  content_digests[]
tokenizer_ref
rights_ref
license_ref
source_provenance_refs[]
converter_ref
converter_digest
created_at
```

An expert cannot execute when its bytes do not match the manifest. Tensor layout changes require a new manifest rather than an in-place mutation.

### 8.2 `MoEResidencyPlan`

The planner produces an immutable plan scoped to a model and hardware snapshot:

```text
plan_id
model_ref
hardware_profile_ref
dense_core_bytes
kv_budget_bytes
runtime_buffer_bytes
os_headroom_bytes
gpu_expert_slot_count
ram_expert_slot_count
cold_store_required
direct_io_candidate
prefetch_budget_bytes
max_inflight_loads
expected_bottleneck
admission_state
blockers[]
fallback_plan_ref
```

Admission is rejected when the dense core, minimum KV budget, runtime buffers, and safety headroom cannot coexist. The planner must never infer that storage capacity compensates for insufficient working memory.

### 8.3 `ExpertResidencyRecord`

Each `(model, layer, expert)` has runtime state:

```text
tier: gpu | ram | storage | loading | unavailable
generation
last_verified_digest
heat
frequency
last_used_sequence
load_count
resident_hit_count
prefetch_hit_count
prefetch_miss_count
bytes_moved
last_load_latency_ms
pin_reason
lease_count
```

Generation and lease fields prevent eviction or reuse while an in-flight operation still references the expert.

### 8.4 `ExpertHeatProfile`

Heat is persisted only as sanitized numeric routing evidence, scoped by:

```text
model digest x model generation x hardware class x workload family x context profile
```

Raw prompts, outputs, user identifiers, private file names, and raw route context are excluded. Incompatible profiles are ignored rather than coerced.

## 9. Residency Planning

The planner separates memory into:

1. Dense, always-required model tensors.
2. KV/cache budget for the admitted context and batch profile.
3. Runtime and transfer buffers.
4. Safety headroom for the OS, driver, allocator fragmentation, and concurrent work.
5. GPU hot expert slots.
6. RAM warm expert slots.
7. Storage-backed cold experts.

Planning uses currently available memory rather than installed capacity alone. It records the snapshot used for the decision and refuses optimistic admission when reliable telemetry is missing.

The first portable planner will use conservative buffered-I/O assumptions. Direct I/O is a separate candidate because alignment requirements and Windows/POSIX behavior differ materially.

## 10. Tiered Expert Store

### 10.1 Storage tier

The cold tier stores immutable expert shards with content digests and bounded reads. Initial packaging should prefer a safe tensor representation with explicit offsets rather than pickle-backed serialization.

The store supports:

- bounded, digest-verified reads;
- memory mapping where it is actually beneficial;
- a buffered path on every supported platform;
- an optional aligned direct-I/O path only after platform certification;
- cancellation of speculative prefetches;
- deterministic fault injection for tests.

### 10.2 RAM tier

The warm tier holds decoded or dequantized expert tensors suitable for transfer or CPU execution. Where supported and measured beneficial, pages may be pinned for asynchronous accelerator copies. Pinned memory receives an explicit budget because excessive pinning can degrade the host.

### 10.3 GPU tier

The hot tier holds executable expert tensors. Transfers use a dedicated stream or backend-equivalent mechanism where available. A ready event must complete before compute consumes a newly transferred expert.

### 10.4 Concurrency and safety

Each expert acquisition returns a lease. Eviction waits for all leases and backend events. Duplicate concurrent loads coalesce into one operation. Load errors are shared with waiters and recorded once per operation.

The store never silently returns a stale, mismatched, differently quantized, or semantically substitute expert.

## 11. Heat, Pinning, and Eviction

The default policy combines frequency with recency and adds hysteresis before a hot candidate displaces an incumbent. This is intended to avoid cache churn when router demand is noisy.

Required behavior:

- every demanded expert increments heat;
- heat decays deterministically at bounded intervals;
- recency breaks ties between similarly frequent experts;
- a replacement candidate must exceed the incumbent by a configured hysteresis margin;
- repinning occurs at request or batch boundaries by default, not in the middle of an executing token;
- operator-forced pins are explicit, bounded, and visible;
- profile resets and model-generation changes are replayable events.

The precise LFRU score, decay, and hysteresis constants are runtime-genome candidates, not permanent magic numbers. Colibrì's compact policy is eligible for a small attributed port, followed by NexusNet-specific ablation.

## 12. Router-Aware Acquisition and Prefetch

### 12.1 Exact demand acquisition

After `MoECapsuleLayer` computes top-k expert IDs, the executor acquires exactly those experts. This path is mandatory and correctness-preserving.

### 12.2 Overlap

Selected experts should be grouped by current tier. Already resident experts can compute while colder experts are loading when aggregation ordering and backend synchronization preserve exact results.

The executor records separately:

- demand wait time;
- transfer time;
- compute time;
- measured overlap;
- residual unhidden I/O time.

### 12.3 Future-expert prefetch

Exact next-layer routing generally depends on the current layer's output, so future prefetch is predictive rather than authoritative. Candidate predictors include:

- persisted layer-to-layer route transitions;
- current workload heat;
- a lightweight pilot router using the available hidden-state approximation;
- repeated-prefix route reuse.

Prefetch is cancelable and budgeted. It can affect residency only, never selected experts or gate weights. Promotion requires measuring precision, recall, wasted bytes, demand-stall reduction, and total throughput—not just prefetch hit rate.

## 13. Adaptive Speculative Acceleration

The existing greedy `speculative_decode` establishes a target-verified correctness baseline. The new controller generalizes policy and evidence without weakening target authority.

Candidate methods include:

- smaller draft model;
- prompt n-gram or suffix drafts;
- MTP head when the model has a compatible, trusted head;
- grammar-forced spans for structured output, always target-verified.

The controller tracks:

- proposals and accepted tokens;
- accepted length distribution;
- target forward count;
- draft time;
- verification time;
- additional memory;
- end-to-end tokens per second and latency;
- structured-output and tool-call correctness;
- quality/equivalence evidence.

Acceptance rate alone is insufficient. A method automatically returns to target-only decoding when a bounded warmup shows non-positive end-to-end benefit, memory pressure violates the plan, or structured-output correctness fails.

Speculation and expert streaming are evaluated both independently and together. MTP may help a storage-bound lane but regress a fully resident lane, so the controller's profile key includes residency state.

## 14. Evidence and Operator Truth

The runtime emits an `ExpertResidencyEvidence` record per run or bounded aggregation window:

```text
plan_ref
manifest_ref
heat_profile_ref
hardware_snapshot_ref
cold_or_warm_state
expert_demand_count
gpu_hits
ram_hits
storage_misses
bytes_read
bytes_transferred
load_wait_ms
overlap_ms
evictions
prefetches
prefetch_hits
prefetch_wasted_bytes
tier_occupancy
speculation_method
speculation_acceptance
baseline_latency_and_throughput
candidate_latency_and_throughput
quality_and_equivalence_refs
degraded_reasons[]
fallback_events[]
```

This evidence extends, rather than replaces, the cache ledger and runtime workload scorecards. Expert-cache hit rate must not be mixed with KV or prefix-cache hit rate.

Operator-visible states are:

- `resident-reference`;
- `tiered-cold`;
- `tiered-warming`;
- `tiered-warm`;
- `tiered-degraded`;
- `fallback-resident`;
- `blocked-insufficient-working-set`;
- `blocked-artifact-or-rights`.

No state may be presented as warm, accelerated, or promoted without fresh measured evidence.

## 15. Failure and Fallback Semantics

Failures are explicit and do not change model identity.

| Failure | Required behavior |
| --- | --- |
| Manifest or digest mismatch | Block the expert and route; emit artifact-integrity evidence. |
| Dense core or minimum working set does not fit | Reject tiered admission; do not pretend storage makes the route viable. |
| Expert load timeout | Complete from the verified resident reference only if available and admitted; otherwise fail visibly. |
| Accelerator OOM | Stop new transfers, release safe candidates, record the plan violation, and use the predeclared fallback. |
| Prefetch error | Cancel the prefetch; demand loading remains authoritative. |
| Heat-profile corruption or incompatibility | Ignore the profile and start cold with a recorded reason. |
| Speculative regression | Disable speculation for the profile and continue target-only. |
| Direct-I/O incompatibility | Use the certified buffered path and record the downgrade. |
| Quality-altering candidate fails eval | Side-bar or reject it; never silently activate it. |

Fallback cannot silently switch to an external provider or different model. Any broader route change remains a NexusBrain decision under existing authority and receipt rules.

## 16. Provenance and Apache-2.0 Boundary

Before any direct port, implementation must record:

- upstream repository and exact commit;
- upstream file and relevant symbol or line region;
- Apache-2.0 license text and required notices;
- whether the result is copied, adapted, or independently implemented;
- NexusNet destination file and symbol;
- reviewer and test references;
- source and resulting code digests.

Expected treatment by source area:

| Colibrì area | NexusNet treatment |
| --- | --- |
| `c/tier.h` heat/LFRU/hysteresis | Eligible for a small attributed algorithm port after isolated review. |
| `c/resource_plan.py` resource formulas | Eligible for attributed adaptation into NexusNet schemas and conservative platform logic. |
| `c/st.h` direct-I/O implementation | Conceptual input; reimplement per platform rather than copying POSIX-specific storage code. |
| `c/glm.c` async pipeline and prefetch | Conceptual input; implement against NexusNet's model/runtime contracts. |
| `c/glm.c` GLM tensor/router/MLA logic | Architecture-specific research candidate, not generic core code. |
| `c/openai_server.py` | Explicitly excluded. |
| Adaptive expert top-p | Quality-altering research candidate only. |
| MTP and grammar drafts | Independently integrate with NexusNet target verification and evidence policies. |

Directly derived files receive header attribution. Repository-level third-party notices identify the upstream revision. Provenance failure blocks promotion.

## 17. Verification Strategy

### 17.1 Correctness

- Resident backend reproduces the current `MoECapsuleLayer` output exactly for deterministic CPU tests.
- Tiered backend matches the resident backend for the same weights, routes, precision, and inputs.
- Router IDs, top-k choices, and gate weights are identical between reference and lossless optimized runs.
- Concurrent acquisition cannot return stale or cross-model expert tensors.
- Eviction cannot invalidate an active lease.
- Target-verified speculation produces the reference token sequence for deterministic decoding.

### 17.2 Planner and storage safety

- Boundary tests cover zero slots, one slot, fragmentation headroom, insufficient dense-core memory, and unreliable telemetry.
- Corrupt, truncated, oversized, misaligned, and digest-mismatched shards fail closed.
- Duplicate loads coalesce.
- Cancelled prefetches release buffers and leases.
- Direct-I/O tests are platform-tagged and never required for the portable buffered baseline.

### 17.3 Policy behavior

- Deterministic tests cover heat increment, decay, tie-breaking, hysteresis, repinning, and profile invalidation.
- Adversarial alternating routes demonstrate that hysteresis reduces thrashing.
- Prefetch cannot alter route selection or output.
- Speculation disables itself when wall-clock benefit is non-positive despite a seemingly acceptable acceptance rate.

### 17.4 Performance evidence

Every candidate is compared across:

- resident reference;
- tiered cold start;
- tiered warmed profile;
- prefetch off/on;
- speculation off/on;
- combined prefetch and speculation;
- supported storage and hardware classes;
- representative chat, coding, agent-loop, batch, and long-context workloads.

Required metrics include TTFT, inter-token latency, decode throughput, storage bytes per token, expert hit rates by tier, memory peaks, prefetch waste, speculation acceptance, quality delta, thermal posture where available, and failure rate.

### 17.5 Promotion

Lossless optimizations require equivalence plus a statistically credible positive end-to-end benefit for the exact profile. Quality-altering candidates additionally require hidden evaluation, explicit quality budgets, governance approval, and rollback proof.

No optimization promotes from a synthetic hit-rate improvement alone.

## 18. Rollout Slices

### Slice 0: Provenance and contracts

- Add schemas, provenance records, and an in-memory fake tier store.
- Add no production execution behavior.
- Prove manifest validation, planning, leases, and evidence shape.

### Slice 1: Resident execution boundary

- Introduce the expert-execution backend seam.
- Keep the resident backend as default.
- Prove exact output and training-test equivalence.

### Slice 2: Portable RAM/storage tiering

- Add expert shard packaging, bounded buffered reads, RAM caching, and demand acquisition.
- Begin on CPU or a deterministic emulated device lane before accelerator transfer.
- Prove cold/warm states and explicit degraded/fallback receipts.

### Slice 3: GPU hot tier and heat policy

- Add asynchronous transfer where supported.
- Add persistent sanitized heat profiles, LFRU/hysteresis, and request-boundary repinning.
- Benchmark against resident and cold-tier baselines.

### Slice 4: Router-aware prefetch

- Add cancelable, budgeted predictors.
- Promote only predictors that reduce demand stalls and improve end-to-end results.

### Slice 5: Adaptive speculation

- Wrap existing verified speculative decoding in profile-aware measurement and automatic shutoff.
- Add n-gram/grammar/MTP candidates separately, with structured-output regressions.

### Slice 6: Specialized formats and kernels

- Evaluate direct I/O, quantized expert storage, fused dequantize/matmul, platform-specific kernels, and selected architecture-specific traits.
- Each remains a separate runtime-genome candidate with independent rollback.

## 19. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Storage latency overwhelms sparse-compute savings | Honest admission estimates, warmed profiles, overlap measurement, and rejection of nonviable routes. |
| Cache thrashing | Hysteresis, request-boundary repinning, bounded profile scopes, and thrash tests. |
| Prefetch wastes bandwidth | Strict budgets, cancellation, precision/waste metrics, and automatic disablement. |
| Tiering changes output | Keep route and gate authority outside the store; verify exact resident/tiered equivalence. |
| Quantization changes quality | Separate lossless residency from lossy format candidates and require hidden evals. |
| MTP or drafts regress speed | Measure wall-clock benefit and automatically disable per profile. |
| Training path destabilizes | Keep tiering inference-only initially and retain resident `ModuleList` semantics. |
| Platform-specific I/O becomes core complexity | Portable buffered baseline; direct I/O remains an optional certified backend. |
| Upstream code contaminates generic architecture | Narrow port allowlist, commit-pinned provenance, per-file attribution, and independent NexusNet interfaces. |
| Evidence surfaces overclaim readiness | Use explicit cold/warm/degraded states and existing promotion gates. |

## 20. Success Criteria

The assimilation is successful when NexusNet can demonstrate, with local evidence:

1. Exact lossless equivalence between resident and tiered execution for a native sparse-MoE fixture.
2. Correct execution when total expert storage exceeds the configured hot tier.
3. Lower warmed end-to-end latency or greater admitted model capacity for at least one real hardware/workload profile without hidden quality regression.
4. Accurate cold/warm/degraded/fallback receipts with replayable manifests and plans.
5. Automatic rejection or disablement of an optimization that does not help its profile.
6. No Colibrì runtime, provider, server, or command in the production dependency graph.
7. Complete attribution and provenance for every directly derived algorithm.

## 21. Implementation Planning Constraints

Before changing any existing function, class, or method, implementation planning and execution must:

- run GitNexus impact analysis for the target symbol;
- report direct callers, affected processes, and risk level;
- warn before any HIGH or CRITICAL edit;
- add a focused red test before the implementation change;
- preserve unrelated dirty-worktree changes;
- run focused equivalence and failure-path tests after each slice;
- run `gitnexus_detect_changes()` before any implementation commit;
- keep each slice independently revertible.

Likely first-impact targets are `MoECapsuleLayer`, `NexusNetLM`, `speculative_decode`, `ModelRuntimePlanner`, `EffectiveContextCacheLedger`, and `RuntimeWorkloadScorecardRegistry`. This document does not authorize editing them without the required impact report.

## 22. Final Design Boundary

Colibrì contributes evidence and narrowly attributable algorithms. NexusNet owns:

- the model/runtime contracts;
- the generic tiering architecture;
- the execution path;
- the adaptive policy;
- the evidence ledger;
- the governance and promotion lifecycle;
- the resulting native inference capability.

This is a native NexusNet evolution slice, not a third-party runtime integration.
