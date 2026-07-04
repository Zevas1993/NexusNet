# SABER Mutating Action Guard Spec

Status: P0 online assimilation target. Research-only until mapped to NexusNet action policy and trace code.

## Source Evidence

- SABER paper: https://arxiv.org/abs/2512.07850
- Source status: primary paper page.

## Finding

SABER analyzes agent trajectories and distinguishes mutating environment-changing steps from non-mutating steps. It finds that deviations in mutating actions are much more likely to flip success to failure, then proposes mutation-gated verification, targeted reflection before mutating steps, and block-based context cleaning.

## NexusNet Assimilation Target

Add a mutating-action guard across shell, file, browser, MCP, GitHub, database, memory, and model-routing authority. NexusNet should treat a read/search step differently from a write/delete/send/execute/publish step, and it should verify high-risk mutations immediately before they happen.

## Proposed NexusNet Components

- `ActionMutationClass`: read-only, reversible mutation, irreversible mutation, external side effect, and privileged mutation.
- `PreMutationVerifier`: checks target, current context, stale constraints, policy, and rollback path.
- `TargetedReflectionPrompt`: concise pre-flight review focused only on the pending mutation and constraints.
- `ContextCleaningCheckpoint`: removes stale or conflicting context before high-impact actions.

## Promotion Gates

- Every mutating action must carry a mutation class and target.
- Irreversible actions require operator consent unless explicitly whitelisted.
- Verification must run immediately before the mutation, not only at plan creation.
- Store the pre-mutation trace for audit and replay.

## Risks

- Reflection can become performative if not tied to deterministic checks.
- Over-gating low-risk writes can slow development.
- Mutation classification must be conservative when target authority is ambiguous.
