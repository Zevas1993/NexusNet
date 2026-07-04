# AgentProcessBench Step Verifier Spec

Status: P1 online assimilation target. Research-only until dataset/code are inspected.

## Source Evidence

- AgentProcessBench paper: https://arxiv.org/abs/2603.14465
- Source status: primary paper page with linked code/data.

## Finding

AgentProcessBench focuses on step-level process quality in tool-using trajectories. It labels individual steps as correct, neutral, or erroneous, and highlights that outcome-only scoring misses important process failures, especially when tool calls have side effects.

## NexusNet Assimilation Target

Add process-level verification to NexusNet action traces. Before a plan reaches an irreversible step, NexusNet should be able to classify recent actions as useful, exploratory, neutral, or harmful, then require repair or operator approval if the trace is drifting.

## Proposed NexusNet Components

- `StepQualityLabel`: `correct`, `neutral`, `erroneous`, `blocked`, `needs_operator`.
- `TraceProcessScorer`: scores each tool/action step with rationale and source references.
- `IrreversibleStepGate`: blocks high-impact actions when recent process quality is low.
- `Verifier Replay`: replays the trace against policy without re-executing side effects.

## Promotion Gates

- Use local labels and deterministic validators before relying on model judgments.
- Require a side-effect taxonomy for shell, file, browser, GitHub, MCP, payment-like, and desktop actions.
- Keep process scoring separate from success scoring; both matter.

## Risks

- Step labels can become subjective without clear local policy.
- Too much neutral-step blocking can make agents brittle.
- Process scoring must be cheap enough to run continuously.
