# Release Wrapper Baseline Repairs Design

## Purpose

Restore the eleven reproduced release-wrapper and provider-growth regression tests without weakening governance, sanitization, or degraded-state reporting. The repair stays confined to the isolated Windows accelerator completion branch and preserves the dirty integration checkout.

## Evidence Baseline

The regressions group into seven root causes:

1. The visualizer exposes sanitized release-wrapper data but uses four stale `Harness` labels instead of the required `Wrapper` labels.
2. Domain teacher-evaluation handoffs are auto-approved during ordinary chat instead of remaining pending for an explicit administrator action.
3. An unknown provider can trigger a federated import readiness lifecycle that overwrites the interaction's latest lifecycle identity.
4. Provider-failure recovery is submitted as a write-like hive action without a checkpoint, which unnecessarily degrades the whole-system heartbeat.
5. Repair-envelope plans execute automatically even when the release supervisor is disabled and has emitted no pulse.
6. The release-supervisor lifecycle dereferences a missing production spine after the forward-pass coverage stage has already classified that subsystem as degraded.
7. Boot readiness runs before the whole-system heartbeat is persisted, creating a circular `boot-smoke-blocked` result.

## Design

### Sanitized visualizer labels

Retain the existing sanitized release-runtime state and metric values. Rename only the four stale visualizer captions to `Wrapper usable providers`, `Wrapper canonical AOs`, `Wrapper packet outbox`, and `Wrapper packet inbox`. No raw prompt, model output, provider error, or peer packet content enters the UI.

### Explicit domain-growth approval

Ordinary chat may create a sanitized teacher-evaluation handoff and pending administrator proposal, but it must not execute promotion approval. The existing administrator-governed replay path remains the only path that changes a candidate to approved.

### Provider-qualified federated import

Automatic federated packet import/readiness runs only after the selected provider has known usable readiness. Unknown or unverified provider identifiers may still record honest interaction and failure evidence, but they cannot advance federated readiness or replace the interaction lifecycle's latest-run identity.

### Read-only degraded recovery observation

Provider failure remains visible in the forward-pass and learning receipts. The subsequent hive recovery observation uses a read-only/inspect action so it can collect governance evidence without requesting a mutation or requiring a checkpoint.

### Supervisor-gated automatic repair

A repair-envelope plan is always persisted when health evidence calls for one. It executes automatically only when the configured release supervisor is enabled and emits the live pulse that requested the repair. Without that pulse, the plan remains pending for the explicit administrator endpoint.

### Missing production-spine boundary

If the production spine is unavailable, the live release-supervisor path returns a sanitized degraded/skipped lifecycle receipt instead of dereferencing `None`. The chat request remains usable, and forward-pass coverage continues to name the unavailable subsystem honestly.

### Heartbeat-before-boot ordering

The chat path builds and persists the whole-system heartbeat before invoking release boot/readiness checks. Boot then evaluates current governed state rather than a missing prior tick. Release history and canon-refresh evidence remain downstream of the boot lifecycle.

## Verification

Use the eleven already-red tests as focused regression gates. Then run the complete provider-growth and release-wrapper test files, the focused Windows accelerator suite, Python compilation, and GitNexus change detection. Do not call the repair complete if a broad test exposes a new failure; report any unrelated baseline failure separately with exact output.

## Non-goals

- No broad port from the dirty integration checkout.
- No changes to raw-content retention policy.
- No test relaxation to accept auto-approval, false heartbeat degradation, or production-spine exceptions.
- No mobile or edge-device runtime work.
