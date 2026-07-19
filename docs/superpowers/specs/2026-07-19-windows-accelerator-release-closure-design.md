# Windows Accelerator Release Closure Design

## Goal

Close the Windows 11 modular accelerator implementation as a release-quality,
evidence-gated deliverable without weakening its hardware truthfulness or
mixing generated video artifacts into source history.

## Approved Scope

The closure covers seven ordered outcomes:

1. obtain a definitive full-repository verification result;
2. reconcile the implementation plan and release-evidence report with the
   merged code and post-implementation repairs;
3. materialize and exercise the NVIDIA CUDA worker in a private production
   environment and record real-model calibration evidence where local assets
   permit it;
4. exercise the packaged Windows bootstrap and lifecycle operations through
   install, restart-equivalent reload, repair, update/rollback, and uninstall;
5. probe Windows ML/DirectML locally and retain explicit unavailable or
   unverified gates for AMD and Intel hardware that is not physically present;
6. remove repository-state noise by ignoring generated watcher and temporary
   tool artifacts while preserving user evidence outside Git history; and
7. merge the verified closure into the integration branch and fast-forward
   `main` locally and remotely without force-pushing.

## Approaches Considered

### Isolated release-closure worktree (selected)

Run verification and environment construction in a clean worktree rooted at
the already-integrated baseline. This preserves the parent checkout's generated
artifacts and makes staged GitNexus evidence correspond only to closure work.

### Modify the integration checkout in place

This avoids a later merge but leaves 8,474 generated files adjacent to release
changes and increases accidental staging risk. It is rejected for this run.

### Treat fixture coverage as cross-vendor certification

This would make the task superficially complete without representative AMD or
Intel hardware. It is rejected because catalog eligibility and fixture tests
do not prove a live route.

## Verification Design

The literal repository suite runs once, without a short artificial timeout,
after competing local inference work is no longer consuming the test CPU. Its
exit code, pass/fail/skip counts, and duration become the release baseline.
Focused accelerator, runtime-mode, wrapper/provider, compilation, import-boundary,
and GitNexus checks run again after any closure edits.

A timeout is evidence of incomplete verification, never a passing result. Any
new code defect is reproduced by a focused failing test before implementation.

## Runtime Certification Design

Vendor libraries remain outside NexusNet core. Production CUDA proof must use
a private environment with `include-system-site-packages = false`, exact locked
requirements, worker health/self-test/inference receipts, and a stable device
fingerprint. Calibration uses a locally available production model when one is
already present; the run will not download an arbitrary large model merely to
manufacture evidence.

Windows ML/DirectML is probed through an isolated provider environment. AMD
ROCm/Vulkan and Intel XPU/SYCL/OpenVINO stay `unverified` when representative
hardware is absent, with fixture matrices proving only gating behavior. `Both`
stays unavailable until measured hybrid execution exists.

## Packaged Windows Soak Design

The bootstrap runs into a disposable NexusNet-owned directory rather than
global Python or machine `PATH`. The smoke records architecture checks, private
environment creation, plan output, worker lifecycle, repair, compatible
rollback, persistence reload, and uninstall. Only paths beneath the disposable
root may be removed during cleanup.

## Repository and Publication Design

Generated `video-watch-output/`, `.superpowers/`, and
`.codex-remote-attachments/` paths are ignored rather than committed or deleted;
this preserves local evidence while producing a clean source status. The
existing stash is inspected and retained unless its contents are proven fully
represented in committed history.

After fresh verification and GitNexus change detection, the closure branch is
merged into `codex/all-worktrees-integration`. Because `origin/main` is already
an ancestor of the integration branch, publication uses a normal fast-forward
push and never force-pushes.

## Acceptance Boundary

Closure is complete only when every locally executable task has exact evidence,
GitNexus is current with risk `none`, tracked Git state is clean, and publication
succeeds. Missing AMD or Intel hardware is reported as an external certification
gate, not as unfinished control-plane implementation and not as a synthetic pass.
