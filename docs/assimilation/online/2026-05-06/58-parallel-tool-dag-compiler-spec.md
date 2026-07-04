# Parallel Tool DAG Compiler Spec

Status: P1 online assimilation target. Research-only until mapped against NexusNet tool execution, policy, and trace infrastructure.

## Source Evidence

- LLMCompiler paper: https://arxiv.org/abs/2312.04511
- LLMCompiler repository: https://github.com/SqueezeAILab/LLMCompiler
- LLM-Tool Compiler paper: https://arxiv.org/abs/2405.17438
- AsyncLM paper: https://arxiv.org/abs/2412.07017
- Source status: primary paper pages and public repository.

## Finding

Sequential ReAct-style tool loops waste time and create unnecessary reasoning steps when independent tool calls can be planned as a dependency graph. LLMCompiler shows a planner, task-fetching unit, and executor pattern for parallel function calling, with reported speed and cost gains over sequential loops.

## NexusNet Assimilation Target

Add a tool DAG compiler that turns approved plans into dependency-aware execution graphs. NexusNet should run independent read-only calls in parallel, serialize risky mutations, and preserve replayable dependencies.

## Proposed NexusNet Components

- `ToolDagPlan`: nodes, dependencies, required approvals, data classes, idempotency keys, and merge steps.
- `ToolDagCompiler`: transforms a natural-language or structured plan into a validated DAG.
- `ParallelToolExecutor`: executes eligible nodes concurrently under policy and sandbox gates.
- `ToolResultJoiner`: merges outputs, detects conflicts, and marks missing dependencies.
- `DagReplayTrace`: records graph version, node status, retries, skipped nodes, and final synthesis.

## Promotion Gates

- Only parallelize nodes proven independent and read-only or idempotent.
- Mutating nodes require transaction boundaries and compensation plans.
- Tool DAGs must pass policy and schema validation before execution.
- Fallback to sequential execution when dependency confidence is low.

## Risks

- Incorrect dependency inference can create race conditions or inconsistent state.
- Parallel failures are harder to explain without strong tracing.
- Batch tools can hide individual authority checks if implemented carelessly.
