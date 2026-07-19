# Windows Accelerator Release Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the seven approved Windows accelerator release-closure items with literal verification, private current-machine certification, honest unavailable-hardware gates, clean repository state, and a non-force publication to `main`.

**Architecture:** Execute from the isolated `codex/windows-accelerator-release-closure` worktree. Reuse the existing accelerator-pack contracts, environment locks, workers, registry, and lifecycle manager; add only the missing operator lifecycle seam and durable release evidence needed to exercise them outside test fixtures.

**Tech Stack:** Python 3.11, pytest, Pydantic v2, PowerShell 7, private `venv`, locked PyTorch 2.11.0 CPU/CUDA wheels, ONNX Runtime provider probes, Git, and GitNexus.

## Global Constraints

- Never alter global Python, global Torch, machine `PATH`, drivers, or vendor SDKs.
- Never label detection, catalog eligibility, or fixture behavior as live certification.
- Keep AMD and Intel routes unverified without representative hardware.
- Keep `Both` unavailable without measured hybrid-offload evidence.
- Use a failing test before any production-code behavior change.
- Run GitNexus upstream impact before editing a function, method, or class and staged change detection before every commit.
- Preserve the parent checkout's generated artifacts and its existing stash.

---

### Task 1: Produce a definitive repository verification baseline

**Files:**
- Generate: `.release-evidence/pytest-full.xml`
- Generate: `.release-evidence/pytest-full.log`

**Interfaces:**
- Consumes: the committed repository at `37604dce` plus the release-closure documentation commit.
- Produces: one literal pytest exit code, counts, duration, and failing node IDs if any.

- [x] Confirm no stale pytest process exists and identify unrelated CPU-heavy processes without terminating them.
- [x] Wait for the active video-watcher inference process to finish so it does not distort the baseline.
- [x] Run `python -m pytest -ra --junitxml=.release-evidence/pytest-full.xml` with a three-hour command timeout and capture the complete terminal result.
- [x] If the suite fails, rerun each failing node ID directly. For a code defect, apply systematic debugging and TDD; for an environment gate, record exact evidence and keep the gate explicit.
- [x] Run `python -m compileall -q core nexus nexusnet recursive_dreamer tests` and `git diff --check`.

### Task 2: Reconcile plan and release evidence

**Files:**
- Modify: `docs/superpowers/plans/2026-07-18-windows-accelerator-completion-train.md`
- Modify: `docs/runtime/WINDOWS_ACCELERATOR_RELEASE_EVIDENCE_2026-07-18.md`

**Interfaces:**
- Consumes: the seven implementation commits, eleven repair commits, Task 1 results, and current GitNexus state.
- Produces: checked implementation tasks and a chronological post-repair verification section with no stale failure claims.

- [x] Mark only demonstrably completed implementation-plan steps as checked; leave external hardware certification gates unchecked and named.
- [x] Add the post-Task-7 repair commits and fresh verification output to the release report.
- [x] Preserve the distinction among `verified`, `unavailable`, and `unverified` routes.
- [x] Run Markdown placeholder/conflict-marker scans and `git diff --check`.
- [x] Stage only the two evidence documents, run staged GitNexus detection, and commit `docs(runtime): reconcile accelerator release evidence` (`c9d4c61`).

### Task 3: Materialize and certify the production NVIDIA pack

**Files:**
- Modify: `nexusnet/cli/runtime_packs.py`
- Test: `tests/runtime/accelerator_packs/test_windows_bootstrap.py`
- Generate: `.release-evidence/cuda-pack/`
- Modify: `docs/runtime/WINDOWS_ACCELERATOR_RELEASE_EVIDENCE_2026-07-18.md`

**Interfaces:**
- Consumes: `BuiltInPackCatalog`, `PrivateEnvironmentBuilder`, `WorkerEnvironmentLock`, `PackInstaller`, `RuntimePackRegistry`, and `WorkerAdapterFactory`.
- Produces: `plan`, `status`, `install`, `repair`, `rollback`, and `uninstall` CLI operations with sanitized JSON results plus a private CUDA worker environment.

- [x] Add failing CLI tests proving explicit consent, exact pack/version selection, private-root confinement, sanitized errors, lifecycle operations, and no silent fallback.
- [x] Run the new CLI tests and observe the missing-command failures.
- [x] Run GitNexus impact on `_parser`, `main`, and any existing lifecycle symbol that must change; report HIGH/CRITICAL before editing.
- [x] Implement the minimal CLI composition layer around existing catalog/installer/lifecycle interfaces; keep vendor imports in workers.
- [x] Run the focused CLI/bootstrap/installer/lifecycle tests.
- [x] Materialize `torch-cuda-2.11.0-cu128-cp311-win-amd64` beneath `.release-evidence/cuda-pack/` using `PrivateEnvironmentBuilder`; verify `include-system-site-packages = false`.
- [x] Run worker `describe`, `health`, `self_test`, deterministic load/infer/unload, forced CPU/GPU mode, and calibration-key probes; capture sanitized JSON and hashes.
- [x] Update the release report with the exact isolated-environment result and any remaining production-model limitation.
- [x] Stage source, tests, and report only; run focused tests, cached diff check, GitNexus detection, and commit the governed lifecycle CLI (`f058f4b`).

### Task 4: Exercise the packaged Windows lifecycle

**Files:**
- Test: `tests/runtime/accelerator_packs/test_windows_bootstrap.py`
- Generate: `.release-evidence/windows-soak/`
- Modify: `docs/runtime/WINDOWS_ACCELERATOR_RELEASE_EVIDENCE_2026-07-18.md`

**Interfaces:**
- Consumes: `install/windows/bootstrap.ps1` and the lifecycle CLI from Task 3.
- Produces: disposable packaged-install evidence for plan, status, install, reload, repair, rollback, uninstall, and path isolation.

- [x] Add a failing bootstrap guard only if live execution exposes a missing packaged-install contract.
- [x] Run `install/windows/bootstrap.ps1 -NexusNetHome <disposable-root> -DeveloperEditable` with the current Python 3.11 interpreter.
- [x] Prove the private core `pyvenv.cfg` disables system-site packages and global package/PATH snapshots are unchanged.
- [x] Exercise CPU reference install, status reload in a fresh process, deliberate quarantine/repair, compatible update/rollback fixture, and uninstall.
- [x] Remove only the verified disposable root after recording digests and sanitized outcomes.
- [x] Update the release report and rerun bootstrap/lifecycle tests.

### Task 5: Probe additional hardware lanes honestly

**Files:**
- Generate: `.release-evidence/provider-probes/`
- Modify: `docs/runtime/WINDOWS_ACCELERATOR_RELEASE_EVIDENCE_2026-07-18.md`

**Interfaces:**
- Consumes: `WindowsMlCatalog`, ONNX worker, vendor support matrices, live Windows hardware graph, and existing fixture matrices.
- Produces: current-machine DirectML/Windows ML observations and explicit AMD/Intel certification blockers.

- [x] Re-run live hardware and Windows ML provider discovery in an isolated environment.
- [x] If the reviewed DirectML package can be installed without global mutation, install it privately and run provider enumeration plus ONNX correctness/health probes.
- [x] Run AMD/Intel mixed-device, unsupported-device, import-boundary, and privacy fixture matrices.
- [x] Confirm AMD/Intel remain unverified because no representative GPU is present; do not substitute NVIDIA DirectML proof for AMD/Intel certification.
- [x] Confirm `Both` remains unavailable without `hybrid-offload` calibration evidence.
- [x] Record exact states and remaining external hardware gates in the release report.

### Task 6: Finish repository housekeeping

**Files:**
- Modify: `.gitignore`

**Interfaces:**
- Consumes: the parent checkout's untracked-path inventory and existing stash metadata.
- Produces: ignored watcher/tool-generated paths without deleting local evidence.

- [x] Add `/video-watch-output/`, `/.superpowers/`, `/.codex-remote-attachments/`, and `/.release-evidence/` to `.gitignore` if equivalent rules are absent.
- [ ] Verify the parent checkout retains all generated files but `git status` no longer lists them.
- [x] Inspect `stash@{0}` names and file lists; its only `.gitnexus` addition was already in `HEAD`, so the proven-redundant stash was dropped.
- [x] Run `git check-ignore -v` for each generated root and `git diff --check`.
- [ ] Stage `.gitignore` and the final evidence-report update, run staged GitNexus detection, and commit `chore: isolate generated release evidence`.

### Task 7: Final verification, merge, and publication

**Files:**
- Modify only files required by verified fixes from Tasks 1-6.

**Interfaces:**
- Consumes: all closure commits.
- Produces: clean Git state, current GitNexus graph, local integration merge, and fast-forward `origin/main` publication.

- [x] Run all accelerator-pack tests, Windows discovery tests, runtime-mode/API tests, provider-growth and release-wrapper regression tests, AST vendor-import guards, and compileall.
- [x] Run the literal full suite again if Tasks 2-6 changed executable code (2,147 passed, 1 intentional environment skip, 0 failed in 1:52:15).
- [ ] Run `git diff --check`, `npx gitnexus analyze --skip-agents-md`, and `gitnexus detect-changes --scope all`; require risk `none` after commit.
- [ ] Merge `codex/windows-accelerator-release-closure` into `codex/all-worktrees-integration` without touching parent-generated artifacts.
- [ ] Rerun the focused release matrix in the merged integration checkout.
- [ ] Fast-forward `main` to the verified integration commit and push `main` to `origin` without force.
- [ ] Push the integration branch for durable provenance, then remove only the release-closure worktree and branch after merge and push are verified.
