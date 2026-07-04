# NexusNet Production Spine Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the remaining NexusNet finish backlog into one production-spine implementation surface that proves the real training, child runtime, MoE, tensor kernel, teacher council, eval, registry, federation, dreaming, runtime foundry, replay, and productization contracts are executable and gated.

**Architecture:** Add a focused `nexusnet.growth.production_spine` module instead of expanding the already-large substrate file. The module composes small services: sandbox training runner, callable child runtime, native hive-MoE router, tensor kernel, teacher council automator, sealed eval gauntlet, durable node registry, federated influence loop, dream candidate generator, runtime foundry, deep replay builder, and productization readiness checker.

**Tech Stack:** Python, Pydantic-style dictionaries, JSON/JSONL repo-local artifacts, pytest, SHA-256 signing, pure-Python tensor math for v0.

---

### Task 1: Failing Production Spine Test

**Files:**
- Create: `tests/test_nexusnet_production_spine.py`

- [ ] **Step 1: Write the failing test**

The test must import `NexusNetProductionSpine`, call `run_completion_cycle()`, and assert that all twelve finish surfaces are returned with gated evidence.

- [ ] **Step 2: Verify red**

Run: `pytest tests/test_nexusnet_production_spine.py -q`

Expected: FAIL because `nexusnet.growth.production_spine` does not exist.

### Task 2: Production Spine Module

**Files:**
- Create: `nexusnet/growth/production_spine.py`
- Modify: `nexusnet/growth/__init__.py`

- [ ] **Step 1: Implement the small services**

Implement the v0 concrete contracts for:

```text
SandboxTrainingRunner
ChildNodeRuntime
NativeHiveMoERuntime
HiveTensorRuntimeKernel
TeacherCouncilAutomation
SealedEvalGauntlet
DurableNodeRegistry
FederatedInfluenceLoop
RecursiveDreamExecution
RuntimeQuantizationFoundry
DeepReplayBuilder
ProductizationReadinessGate
```

- [ ] **Step 2: Run targeted tests**

Run: `pytest tests/test_nexusnet_production_spine.py -q`

Expected: PASS.

### Task 3: Regression Verification

**Files:**
- Modify only files from this plan.

- [ ] **Step 1: Run growth and production spine tests**

Run: `pytest tests/test_hive_model_growth_engine.py tests/test_nexusnet_production_spine.py -q`

Expected: PASS.

- [ ] **Step 2: Run whitespace check**

Run: `git diff --check -- nexusnet/growth tests/test_nexusnet_production_spine.py docs/superpowers/plans/2026-05-04-nexusnet-production-spine-completion.md`

Expected: no whitespace errors.
