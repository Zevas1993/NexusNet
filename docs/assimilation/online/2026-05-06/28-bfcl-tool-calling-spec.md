# BFCL Tool Calling Spec

Status: P1 online assimilation target. Research-only until BFCL categories, license, and local/open-model runner requirements are inspected.

## Source Evidence

- BFCL leaderboard: https://gorilla.cs.berkeley.edu/leaderboard
- BFCL repository: https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard
- BFCL paper: https://openreview.net/pdf?id=2GmDdhBdDk
- Source status: primary leaderboard, public code/data directory, and ICML 2025 paper.

## Finding

BFCL has grown from simple function-call matching into a broader tool-use evaluation surface. The current V4 framing includes agentic web search, memory management, and format sensitivity, which maps directly to failures that matter in a tool-rich NexusNet environment.

## NexusNet Assimilation Target

Create a first-class tool-call certification lane. Every model route should be scored for schema conformance, no-tool decisions, multi-turn argument carryover, parallel calls, tool-error recovery, and format stability before it can drive MCP, browser, file, or shell tools.

## Proposed NexusNet Components

- `ToolCallPassport`: tool schema, authority level, required arguments, optional arguments, examples, and no-call conditions.
- `SchemaConformanceScorer`: exact JSON/schema validation before any side effect can execute.
- `NoToolDecisionGate`: verifies the model can refuse to call tools when a tool is not needed or not permitted.
- `ToolErrorRecoveryTrace`: records invalid arguments, tool errors, repair attempts, and final outcome.
- `ModelToolUseProfile`: per-model scorecard for single-call, parallel-call, multi-turn, memory, search, and format-sensitivity cases.

## Promotion Gates

- Invalid or partial tool calls must be blocked before execution.
- High-authority tools require separate policy approval even when the schema is valid.
- Tool-use scores must be measured per model, per route, and per tool family.
- Local/open models need the same tool-call gates as frontier API models.

## Risks

- BFCL leaderboard scores may not transfer to NexusNet-specific tool schemas.
- Format sensitivity can regress after prompt or model changes.
- Tool-call accuracy is necessary but not sufficient for safe authority delegation.
