# Durable Agent Orchestration Spec

Status: P1 online assimilation target. Research-only until mapped against NexusNet's existing behavior loop, Control Panel, and native execution code.

## Source Evidence

- LangGraph durable execution docs: https://docs.langchain.com/oss/python/langgraph/durable-execution
- LangGraph persistence docs: https://docs.langchain.com/oss/python/langgraph/persistence
- Microsoft Agent Framework docs: https://learn.microsoft.com/en-us/agent-framework/
- Microsoft Agent Framework repository: https://github.com/microsoft/agent-framework
- AutoGen repository maintenance notice: https://github.com/microsoft/autogen
- Source status: official documentation and public repositories.

## Finding

Modern agent frameworks are converging on durable execution, checkpoints, replay, human interrupts, persistence, graph/workflow edges, and migration away from purely conversational multi-agent loops. AutoGen's maintenance notice and Microsoft Agent Framework's successor position are useful signals: orchestration is moving toward governed workflow runtimes.

## NexusNet Assimilation Target

Make NexusNet long-running behavior explicitly durable. Every multi-step agent run should be resumable, replayable, interruptible, and idempotent around side effects.

## Proposed NexusNet Components

- `RunCheckpoint`: goal, state snapshot, active plan, memory view, tool results, pending approvals, and retry state.
- `SideEffectTaskEnvelope`: wraps file writes, API calls, shell commands, and connector mutations so resumed runs do not repeat side effects blindly.
- `HumanInterruptPoint`: pause, inspect, approve, modify, or cancel a run before authority escalation.
- `ReplayController`: deterministic replay for prior steps and controlled re-execution for non-deterministic steps.
- `WorkflowEdgeRegistry`: explicit edges between planner, router, executor, reviewer, memory, and verifier nodes.

## Promotion Gates

- Side-effecting operations must be idempotent or persisted behind task envelopes.
- A resumed run must show what is replayed versus re-executed.
- Human approval points must survive restart.
- Do not import a framework wholesale until NexusNet-specific boundaries are mapped.

## Risks

- Framework adoption can create dependency lock-in and duplicate existing NexusNet behavior-loop logic.
- Durable execution is only useful if state snapshots are complete and privacy-safe.
- Poor idempotency can repeat writes, sends, purchases, or shell commands after resume.
