# Colibrì Architecture-Intake Assimilation Implementation Plan

> **For agentic workers:** Execute this plan test-first. Preserve existing dirty
> worktree changes and do not add Colibrì as a dependency or copy its runtime.

**Goal:** Make NexusNet's native tiered-MoE runtime usable from explicit model
architecture metadata on CPU-only, RAM-limited, and GPU-equipped hosts, then
feed sanitized, live residency measurements into the evolutionary planner.

**Architecture:** Add a NexusNet-owned architecture-intake module beside the
existing residency store. It accepts a precise MoE descriptor and hardware
budgets, calculates dense placement plus GPU/RAM expert-cache capacity and a
storage-limited cold ceiling, and fails closed for incomplete metadata. A
telemetry adapter consumes the existing aggregate `runtime_evidence()` shape,
never prompts, paths, tokens, or weights. `EvolutionaryInferenceSystem` stores
the resulting verified evidence only after an explicit equivalence result.

**Constraints:**

- No Colibrì dependency, source import, CLI, server, subprocess, or model
  weight handling.
- No model-name rules; exact layer/expert/KV metadata is mandatory.
- CPU/RAM-only is a supported placement when its dense working set fits.
- A plan is an admission/readiness result, not permission to load or execute a
  model. Live evidence must remain numeric and sanitized.
- Promotion remains governed by the existing repeated/equivalence/stability
  gates; the new adapter cannot fabricate those outcomes.

## Tasks

### 1. Define the architecture and telemetry contracts

**Files:** Create `nexusnet/runtime/moe_residency/architecture.py`; modify the
residency package exports; test in `tests/runtime/test_moe_architecture_intake.py`.

1. Write red tests for CPU/RAM placement, GPU placement, invalid layout, and
   insufficient dense residency.
2. Add immutable descriptor, hardware-budget, plan, and telemetry objects.
3. Compute total experts, dense/KV working set, cache slots, cold expert bytes
   per token, and storage bandwidth ceiling without model-specific constants.
4. Validate the focused test file.

### 2. Bridge verified runtime evidence into evolution

**Files:** Modify `nexusnet/runtime/evolutionary_inference/system.py`; test in
`tests/runtime/test_evolutionary_inference_system.py`.

1. Write a red system test that turns a sanitized residency snapshot into a
   `PlanEvidence` record and confirms it appears in status.
2. Add a narrow `record_residency_evidence` method that stores only completed,
   equivalence-confirmed, numeric evidence for an existing plan.
3. Persist atomically through the existing evidence path and expose a compact
   residency-evidence status view.
4. Run focused residency and evolution tests.

### 3. Register the clean-room target at its source seam

**Files:** Modify `nexusnet/operations/assimilation_targets.py` and
`tests/test_video_assimilation_targets.py`; create
`nexusnet/runtime/moe_residency/assimilation/colibri-moe-architecture-intake.md`.

1. Register the verified primary source and target with both source-local
   anchor and concrete implementation references.
2. Keep the explicit independent-behavioral boundary and no-dependency rule.
3. Update scorecard coverage expectations and source-anchor validation.

### 4. Verify the completed slice

Run the focused pytest matrix, compile the touched packages, check whitespace,
and run GitNexus change detection. Report exact evidence and any unrelated
dirty-worktree failures rather than claiming broader completion.
