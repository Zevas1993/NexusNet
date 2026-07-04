# Reversible Patch Transaction Log Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet state, memory, policy, and config writes.

## Source Evidence

- JSON Patch RFC 6902: https://www.rfc-editor.org/rfc/rfc6902.html
- JSON Merge Patch RFC 7386: https://www.rfc-editor.org/rfc/rfc7386
- SQLite session extension docs: https://www.sqlite.org/sessionintro.html
- SQLite changeset apply/invert docs: https://www.sqlite.org/session/c_changesetapply_invert.html
- Immer patches docs: https://immerjs.github.io/immer/patches/
- Source status: official RFCs and project docs.

## Finding

Structured patch formats and changesets make state mutations inspectable, testable, and sometimes reversible. JSON Patch includes explicit operations and precondition-like `test`; SQLite sessions can package changesets and invert them; Immer can emit forward and inverse patches for application state.

## NexusNet Assimilation Target

Represent NexusNet state changes as transactions with forward patches, inverse patches, preconditions, evidence links, and rollback plans. This applies to memory writes, policy edits, feature flags, tool manifests, route tables, and UI state snapshots.

## Proposed NexusNet Components

- `StatePatch`: structured forward patch with target, operation set, and schema version.
- `InversePatch`: rollback operation or verified compensation plan.
- `PatchPrecondition`: expected current value, version, digest, or permission check.
- `PatchTransaction`: batch of patches with author, reason, evidence, approval, and run id.
- `RollbackPlan`: executable or reviewable path to undo a failed or rejected change.

## Promotion Gates

- Require preconditions for every state-changing patch.
- Store inverse patches or compensating actions before applying the forward patch.
- Apply changes atomically where the backing store supports transactions.
- Link patches to source evidence and run traces.
- Test concurrent edit, stale precondition, partial failure, and rollback paths.

## Risks

- Not every side effect can be reversed by a patch.
- Inverse patches can be wrong if generated against stale state.
- Patch logs can capture sensitive values unless redacted or encrypted.
