# Local First CRDT State Spec

Status: P2 online assimilation target. Research-only until NexusNet Control Panel and memory-state needs are mapped.

## Source Evidence

- Yjs docs: https://docs.yjs.dev/
- Yjs repository: https://github.com/yjs/yjs
- Automerge docs: https://automerge.org/docs/
- ElectricSQL docs: https://legacy.electric-sql.com/docs
- Local-first paper reference: https://www.inkandswitch.com/local-first/
- Source status: official project docs and local-first research reference.

## Finding

CRDT and local-first systems solve a problem agent platforms often ignore: multiple actors can update shared state offline, sync later, and avoid central-server fragility. For NexusNet, this maps to operator notes, task boards, memory review queues, eval annotations, and multi-agent run state.

## NexusNet Assimilation Target

Use local-first state primitives for operator-owned data that should survive offline work and avoid SaaS lock-in. CRDT state should be used for collaborative review surfaces, not raw high-risk authority records until conflict semantics are proven.

## Proposed NexusNet Components

- `LocalFirstStateRecord`: document ID, actor ID, update hash, schema version, privacy class, and sync status.
- `AgentAnnotationCRDT`: collaborative comments, review status, labels, and triage notes for runs and specs.
- `ConflictSemanticsTest`: verifies domain-specific merge behavior for review and task state.
- `OfflineControlPanelStore`: local-first queue for notes, approvals, and low-risk metadata.
- `SyncBoundaryPolicy`: determines which state may leave the local device.

## Promotion Gates

- Do not use generic CRDT merge semantics for irreversible authority decisions.
- Keep private memory and raw traces local unless sync is explicitly enabled.
- Test schema migration, deletion, undo, and conflict cases.
- Preserve append-only evidence separately from editable annotations.

## Risks

- CRDTs guarantee convergence, not domain correctness.
- Deletion and privacy semantics are subtle in replicated systems.
- Sync layers can accidentally expose private local state.
