# NexusNet Worktree Integration Train Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align active NexusNet branches and worktrees into one current integration branch without deleting relevant project work.

**Architecture:** Use a branch-by-branch integration train from `codex/knowledge-artifact-compiler`, preserving dirty work as commits before merging. Merge low-conflict branches first, resolve higher-conflict branches by keeping compatible canonical surfaces, and verify after each checkpoint with focused tests plus GitNexus detect-change/index refresh.

**Tech Stack:** Git worktrees, GitNexus, pytest, Python compile checks, Node syntax checks for UI files.

---

### Task 1: Create Integration Branch And Checkpoint Current Dirt

**Files:**
- Modify: current dirty files already present in the worktree
- Create: `docs/superpowers/plans/2026-07-04-nexusnet-worktree-integration-train.md`

- [ ] Create `codex/all-worktrees-integration` from the current checkout.
- [ ] Run `git status --short` and `mcp__gitnexus.detect_changes(scope="all")`.
- [ ] Commit the current dirty files and this plan as an integration checkpoint.
- [ ] Run focused tests covering the checkpointed files.

### Task 2: Merge Computer Fabric MVP

**Files:**
- Merge branch: `codex/nexusnet-computer-fabric-mvp`
- Expected additions: `nexusnet/computer_fabric/**`, `tests/test_computer_fabric.py`, related docs

- [ ] Run conflict preview before merge.
- [ ] Merge the branch.
- [ ] Run `pytest tests/test_computer_fabric.py -q`.
- [ ] Commit the merge if verification is acceptable.

### Task 3: Preserve And Merge Product Sweep Worktree

**Files:**
- Source worktree: `F:\NexusNet_Worktrees\nexusnet-full-product-sweep`
- Merge branch: `codex/nexusnet-full-product-sweep`

- [ ] Commit dirty files in the product sweep worktree before merging.
- [ ] Merge into integration branch.
- [ ] Resolve conflicts in `nexus/api/app.py`, `nexus/services.py`, `nexusnet/core/brain.py`, `nexusnet/evals/__init__.py`, and protocol/runtime init files.
- [ ] Run product-sweep and existing core tests.

### Task 4: Merge Full Assimilation Implementation

**Files:**
- Merge branch: `codex/full-assimilation-implementation`

- [ ] Merge only after product sweep is stable.
- [ ] Resolve add/add conflicts in authority, developmental, eval, evidence, and tool-action modules by preserving both compatible public APIs.
- [ ] Run authority/developmental/eval/evidence/tool-action focused tests.

### Task 5: Evaluate Universal Runtime Gate

**Files:**
- Merge branch: `codex/universal-runtime-gate`

- [ ] Diff the single old commit against the integrated branch.
- [ ] Cherry-pick only non-superseded runtime gate material if needed.
- [ ] Skip or archive superseded scaffolding rather than forcing stale root docs/API conflicts.

### Task 6: Final Alignment

**Files:**
- All merged branches and worktrees

- [ ] Run a focused suite spanning ontology, teacher, release wrapper, computer fabric, product sweep, assimilation, and core brain tests.
- [ ] Run Python compile checks on touched Python files and Node syntax checks on touched UI files.
- [ ] Run `mcp__gitnexus.detect_changes(scope="compare")`.
- [ ] Run `npx gitnexus analyze` and `npx gitnexus status`.
- [ ] Remove only fully merged, clean worktrees and delete only merged branches.
