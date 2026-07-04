# Workflow Engine Substrate Spec

Status: P2 online assimilation target. Research-only until compared with NexusNet's current behavior loop and orchestration code.

## Source Evidence

- Temporal docs: https://docs.temporal.io/
- Restate docs: https://docs.restate.dev/
- Inngest docs: https://www.inngest.com/docs
- Hatchet docs: https://docs.hatchet.run/
- Source status: official durable workflow and task engine documentation.

## Finding

Durable workflow engines provide production patterns for retries, activities, queues, timers, idempotency, event history, cancellation, scheduling, and long-running state. These are lower-level execution substrates than agent frameworks and can inform how NexusNet handles side effects.

## NexusNet Assimilation Target

Evaluate whether NexusNet needs an internal workflow substrate or adapters to existing durable engines. The immediate target is a design pattern: side effects are activities with durable IDs, retry policy, cancellation, and replay-safe state.

## Proposed NexusNet Components

- `DurableActivity`: side-effect unit with ID, inputs, outputs, retry policy, timeout, and compensation behavior.
- `RunEventHistory`: append-only log of decisions, activities, signals, timers, cancellations, and completions.
- `IdempotencyKeyPolicy`: prevents duplicate writes, sends, purchases, shell commands, or connector mutations.
- `WorkflowAdapter`: optional adapter to Temporal, Restate, Inngest, Hatchet, or local-only scheduler.
- `CompensationPlan`: rollback, cleanup, or human escalation when a workflow fails after partial side effects.

## Promotion Gates

- Do not adopt a workflow engine before proving where the current NexusNet loop fails.
- Require idempotency keys for every mutating activity.
- Ensure local-only mode remains viable for commercial packaging.
- Test cancellation, resume, retry, and duplicate-delivery cases.

## Risks

- A full workflow engine can add operational weight and hosting requirements.
- Agent reasoning is non-deterministic; workflow replay must separate decisions from side effects.
- Poor compensation design can leave external systems in inconsistent states.
