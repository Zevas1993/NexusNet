# Complete Evolutionary Inference System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Turn the existing evolutionary inference foundation into a complete, executable dual-loop system that fingerprints real model metadata, measures heterogeneous transfer behavior, synthesizes and benchmarks plans, selects a Pareto-optimal champion per SLO, promotes and rolls back reversible policies, and evolves those policies during governed downtime.

**Architecture:** Keep hardware-neutral control in `nexusnet.runtime.evolutionary_inference` and place executable behavior behind capability-gated primitives. A single `EvolutionaryInferenceSystem` owns the live selection loop and downtime dream loop, persists evidence and champion history atomically, and is injected into the existing inference architecture and economy router rather than creating another authority plane.

**Tech Stack:** Python 3.11, Pydantic v2, standard library timing/hash/storage APIs, optional PyTorch CUDA/ROCm/MPS execution behind runtime capability checks, pytest, FastAPI TestClient.

## Global Constraints

- No `pass`, `NotImplementedError`, TODO, FIXME, placeholder return, fabricated measurement, or production-default synthetic model.
- No plan selection keyed by model name, repository ID, model path, prompt, output, username, hostname, or private content.
- Every automatic promotion is limited to reversible runtime parameters and requires reference equivalence, repeated measurements, a rollback target, and post-promotion monitoring.
- Native executable, dependency, remote-boundary, model-weight, and quality-altering candidates remain approval-required and cannot become active automatically.
- Missing CUDA, ROCm, Metal, energy, or thermal telemetry removes the affected primitive or objective; it never fabricates support.
- Dream work starts only when serving, thermal, memory, power, and budget gates permit it and must honor preemption between trials.
- Existing dirty parent-checkout changes remain untouched; implementation stays in the isolated worktree.
- Follow red-green-refactor for every production behavior and run GitNexus impact before editing existing symbols.

---

### Task 1: Replace synthetic-default evidence with real runtime contracts

**Files:**
- Modify: `nexusnet/runtime/evolutionary_inference/schemas.py`
- Modify: `nexusnet/runtime/evolutionary_inference/fingerprints.py`
- Modify: `nexusnet/runtime/evolutionary_inference/foundation.py`
- Test: `tests/runtime/test_evolutionary_inference_system.py`

**Interfaces:**
- Produces: `RuntimeModelMetadata`, `WorkloadProfile`, `SLOProfile`, `RuntimeObservation`, and `fingerprint_from_runtime_metadata(metadata) -> ModelExecutionFingerprint`.
- Produces: hardware-only foundation evidence when no model has been attached.

- [x] Write failing tests proving graph/operator/tensor features determine the fingerprint, model ID/path fields are ignored, unknown custom operators fail closed, and hardware startup no longer creates a synthetic model fingerprint.
- [x] Run `python -m pytest tests/runtime/test_evolutionary_inference_system.py -q` and confirm missing-contract failures.
- [x] Extend `ModelExecutionFingerprint` with `graph_digest`, `operator_families`, `tensor_groups`, state/KV, sparsity/router, dynamic-shape, custom-operator, rights, and unsupported-feature contracts.
- [x] Implement:

```python
def fingerprint_from_runtime_metadata(metadata: RuntimeModelMetadata | dict[str, Any]) -> ModelExecutionFingerprint:
    normalized = RuntimeModelMetadata.model_validate(metadata)
    if normalized.unknown_or_unsupported_features:
        raise UnsupportedModelFeatureError(normalized.unknown_or_unsupported_features)
    canonical = normalized.model_dump(mode="json", exclude={"provenance_ref"})
    return ModelExecutionFingerprint(
        fingerprint_id=f"model-fingerprint::{sha256_json(canonical)[:24]}",
        graph_digest=sha256_json({"operators": canonical["operator_families"], "tensors": canonical["tensor_groups"]}),
        source_kind="metadata",
        **canonical,
    )
```

- [x] Make `EvolutionaryInferenceFoundation.establish_baseline()` persist hardware/calibration evidence without model feasibility unless an actual fingerprint is supplied.
- [x] Run the focused tests and confirm green.

### Task 2: Implement real heterogeneous transfer calibration and execution

**Files:**
- Create: `nexusnet/runtime/evolutionary_inference/transfer.py`
- Modify: `nexusnet/runtime/evolutionary_inference/calibration.py`
- Modify: `nexusnet/runtime/evolutionary_inference/schemas.py`
- Test: `tests/runtime/test_evolutionary_inference_system.py`

**Interfaces:**
- Produces: `TransferExecutor.execute(request: TransferRequest) -> TransferEvidence`.
- Produces: `HardwareCalibrationLab.calibrate(graph) -> HardwareCapabilityGraph`.

- [x] Write failing tests for measured pageable copy, bounded storage transfer, chunked double buffering, byte-for-byte checksum equivalence, accelerator unavailability, and serving preemption.
- [x] Verify the tests fail because transfer execution does not exist.
- [x] Implement portable pageable and storage transfers using real bounded byte buffers and temporary files.
- [x] Implement optional PyTorch accelerator transfer with bounded pinned slabs, a non-default stream, events, `non_blocking=True`, and synchronized evidence when CUDA/ROCm is actually available; return `backend-unavailable` otherwise.
- [x] Record direction, chunk size, repeat count, cold/warm duration, bytes moved, effective bandwidth, overlap ratio, synchronization count, backend, and checksum equivalence.
- [x] Add calibrated transfer links to the hardware graph; measured values override advertised values.
- [x] Run the focused tests and confirm green.

### Task 3: Build an executable primitive registry and plan synthesizer

**Files:**
- Modify: `nexusnet/runtime/evolutionary_inference/primitives.py`
- Create: `nexusnet/runtime/evolutionary_inference/synthesis.py`
- Modify: `nexusnet/runtime/evolutionary_inference/schemas.py`
- Test: `tests/runtime/test_evolutionary_inference_system.py`

**Interfaces:**
- Produces: `ExecutionPlanSynthesizer.synthesize(graph, fingerprint, workload, slo, priors) -> list[ExecutionPlan]`.

- [x] Write failing tests showing CPU-only, limited-VRAM MoE, high-VRAM, and unified-memory fixtures receive different feasible plans without model-name branches.
- [x] Write failing conflict tests proving incompatible primitives cannot compose.
- [x] Register only executable primitives: portable reference, pageable transfer, bounded storage staging, chunked transfer, double-buffered copy/compute, optional pinned asynchronous accelerator transfer, and existing MoE selective residency.
- [x] Give every primitive exact capability/model/workload predicates, conflicts, fallback ID, implementation digest, quality semantics, evidence requirements, and reversible parameters.
- [x] Implement constraint-based candidate composition with deterministic IDs and no unavailable primitive in a candidate.
- [x] Run the focused tests and confirm green.

### Task 4: Implement real shadow benchmarking and Pareto selection

**Files:**
- Create: `nexusnet/runtime/evolutionary_inference/benchmark.py`
- Create: `nexusnet/runtime/evolutionary_inference/pareto.py`
- Modify: `nexusnet/runtime/evolutionary_inference/schemas.py`
- Test: `tests/runtime/test_evolutionary_inference_system.py`

**Interfaces:**
- Produces: `PlanBenchmark.run(plan, workload, repeat_count=3) -> PlanEvidence`.
- Produces: `ParetoController.frontier(evidence) -> list[PlanEvidence]` and `select(frontier, slo) -> PlanEvidence`.

- [x] Write failing tests for cold/warm separation, repeated measurements, equal input/checksum/reference conditions, uncertainty, nondominated-frontier preservation, and different selections for latency versus memory SLOs.
- [x] Implement actual transfer/compute benchmark execution using `TransferExecutor`; derive quality/equivalence solely from deterministic checksum and declared external quality evidence.
- [x] Reject failed, incomplete, non-equivalent, or single-sample evidence from promotion eligibility.
- [x] Implement Pareto dominance across latency, throughput, peak RAM/VRAM, bytes moved, energy when available, quality, and stability.
- [x] Select a frontier point using hard constraints first, then the explicit/inferred/balanced SLO without one permanent hidden scalar.
- [x] Run the focused tests and confirm green.

### Task 5: Implement evolution memory, promotion, monitoring, and rollback

**Files:**
- Create: `nexusnet/runtime/evolutionary_inference/evolution_memory.py`
- Create: `nexusnet/runtime/evolutionary_inference/promotion.py`
- Test: `tests/runtime/test_evolutionary_inference_system.py`

**Interfaces:**
- Produces: `EvolutionMemory.record(outcome)`, `priors(feature_key)`, and restart-safe `summary()`.
- Produces: `PlanPromotionController.promote(candidate, champion, gate)`, `observe(plan_id, observation)`, and `rollback(reason)`.

- [x] Write failing restart tests for champion, challenger, rejection, negative prior, and rollback history with no raw-content leakage.
- [x] Write failing promotion tests requiring equivalence, minimum repeats, improvement/non-domination, monitoring, and rollback.
- [x] Write failing tests proving native-code and quality-altering candidates require approval and performance/quality drift automatically restores the prior champion.
- [x] Persist signed-content digests and atomic JSON records under `runtime/evolutionary-inference/`.
- [x] Implement feature-space priors from hardware/fingerprint/workload traits, never model IDs.
- [x] Implement reversible active-policy files with previous-champion snapshots and immediate drift rollback.
- [x] Run the focused tests and confirm green.

### Task 6: Implement the preemptible downtime dream laboratory

**Files:**
- Create: `nexusnet/runtime/evolutionary_inference/dream_lab.py`
- Test: `tests/runtime/test_evolutionary_inference_system.py`

**Interfaces:**
- Produces: `InferenceDreamLab.run(request, cancel_check=None) -> DreamCycleEvidence`.

- [x] Write failing tests for closed serving/thermal/memory/budget gates, mid-cycle preemption, champion/reference/challenger comparison, governed promotion, recorded rejection, and positive/negative prior updates.
- [x] Generate bounded candidates by recombining trusted primitives and mutating reversible chunk size, buffer depth, prefetch depth, and scheduling parameters.
- [x] Benchmark candidates against the identical reference/champion workload and hardware snapshot.
- [x] Quarantine incomplete or failed trials, update negative priors, and never activate them.
- [x] Promote only reversible candidates satisfying the promotion controller; emit approval-required dossiers for native/dependency/remote/quality-altering proposals.
- [x] Check `cancel_check()` between every trial and persist `preempted-safe-checkpoint` without partial active policy mutation.
- [x] Run the focused tests and confirm green.

### Task 7: Compose the complete live and downtime system

**Files:**
- Create: `nexusnet/runtime/evolutionary_inference/system.py`
- Modify: `nexusnet/runtime/evolutionary_inference/__init__.py`
- Modify: `nexusnet/runtime/evolutionary_inference/foundation.py`
- Test: `tests/runtime/test_evolutionary_inference_system.py`

**Interfaces:**
- Produces: `EvolutionaryInferenceSystem.attach_model`, `observe`, `select_plan`, `run_dream_cycle`, `rollback`, and `status`.

- [x] Write an end-to-end failing test satisfying all ten umbrella acceptance criteria with hardware fixtures and executable portable transfers.
- [x] Build one system object that loads hardware calibration, fingerprints, plans, evidence, frontier, active policies, drift state, dream history, and evolution memory.
- [x] Make live selection use only verified champions/frontier points and fall back to the portable reference when evidence is absent or stale.
- [x] Make observations sanitized, persist performance/quality/resource evidence, and trigger drift rollback.
- [x] Make status expose uncertainty, hardware, fingerprints, active/fallback plan, frontier, bottleneck, transfer evidence, dream gate/cycle, promotions, rejections, and rollbacks.
- [x] Run the focused tests and confirm green.

### Task 8: Bind the complete system to NexusNet runtime surfaces

**Files:**
- Modify: `nexusnet/runtime/inference_architecture.py`
- Modify: `nexusnet/runtime/inference_economy_router.py`
- Modify: `nexus/services.py`
- Modify: `nexus/api/app.py`
- Modify: `tests/test_inference_architecture_registry.py`
- Modify: `tests/runtime/test_inference_economy_router.py`
- Test: `tests/runtime/test_evolutionary_inference_system.py`

**Interfaces:**
- Consumes: `EvolutionaryInferenceSystem` from Task 7.
- Produces: live route decision field `evolutionary_inference` and `/ops/brain/inference-evolution/*` endpoints.

- [x] Add failing API and router tests for real metadata attach, calibration, plan benchmark, distinct SLO selection, downtime dream, promotion/rejection, observation-driven rollback, restart replay, and sanitized status.
- [x] Construct `InferenceArchitectureRegistry` before `InferenceEconomyRouter`, inject `select_plan` into the router, and never pass request messages into the selector.
- [x] Extend architecture planning with evidence-linked plans while preserving all existing policy gates.
- [x] Add GET status plus POST model, observe, benchmark/dream, and rollback endpoints under `/ops/brain/inference-evolution`.
- [x] Keep the forward-radar integration as a concrete callable `run_dream_cycle(capacity_gate, cancel_check)` so the pending scheduler can bind without copying domain logic.
- [x] Run architecture, router, services, API, workload, autonomous-update behavior, cache, MoE, and status regressions.

### Task 9: Final proof, no-stub audit, and integration

**Files:**
- Verify all files above.

- [x] Run `rg -n "TODO|FIXME|NotImplemented|placeholder|pass$|stub" nexusnet/runtime/evolutionary_inference nexusnet/runtime/inference_architecture.py nexusnet/runtime/inference_economy_router.py` and require no implementation placeholders.
- [x] Run the complete focused and dependent pytest matrices with exact pass/fail counts.
- [x] Run `python -m compileall -q nexusnet/runtime/evolutionary_inference nexusnet/runtime/inference_architecture.py nexusnet/runtime/inference_economy_router.py`.
- [x] Run `git diff --check` and GitNexus staged change detection.
- [x] Commit, fast-forward merge into `codex/all-worktrees-integration`, restore all pre-existing dirty work, rerun merged verification, and clean up only after proof.

## Self-Review

- Spec sections 5 through 13 map to executable registry, transfer, synthesis, benchmark, Pareto, memory, promotion, dream, system, and runtime-integration tasks.
- All ten umbrella acceptance criteria are asserted in Task 7 and exercised again through the API/router in Task 8.
- Production startup is hardware-only until real sanitized runtime metadata is attached; the synthetic helper remains test-only compatibility support and is not used by the live system.
- Optional accelerator code has a complete implementation path and an explicit unavailable result; it is not represented as active when the backend cannot execute.
- External algorithms without NexusNet-owned executable implementations are not falsely registered as working primitives. Continuous research intake can propose them as approval-required dossiers, but they cannot enter the active registry or frontier without code, trust, and benchmark evidence.
- The known baseline `test_autonomous_update_api_blackbox_and_control_panel_surface` count mismatch is unrelated and remains unchanged; behavior-specific autonomous-update tests will still be run.
