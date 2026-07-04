# ToolSandbox Stateful Tool Use Spec

Status: P1 online assimilation target. Research-only until Apple ToolSandbox code, scenarios, and license boundaries are inspected locally.

## Source Evidence

- Apple research page: https://machinelearning.apple.com/research/toolsandbox-stateful-conversational-llm-benchmark
- ToolSandbox paper: https://arxiv.org/abs/2408.04682
- ToolSandbox repository: https://github.com/apple/ToolSandbox
- Source status: official Apple research page, primary paper page, and public repository.

## Finding

ToolSandbox evaluates tool-using agents in stateful, conversational, interactive scenarios. It explicitly targets gaps that simple REST API or one-turn function-calling tests miss: implicit state dependencies, canonicalization, insufficient information, on-policy user simulation, and intermediate plus final milestone checks.

## NexusNet Assimilation Target

Add a stateful tool-use harness between BFCL-style schema checks and high-authority MCP/browser/file actions. NexusNet should prove that a model can ask for missing information, preserve state across turns, use canonical arguments, and avoid unintended side effects before it gets tool execution authority.

## Proposed NexusNet Components

- `StatefulToolScenario`: initial state, user simulator rules, allowed tools, hidden state, milestones, and final verifier.
- `ToolStateDeltaLedger`: records before/after state for every tool call and flags unexpected mutations.
- `MissingInfoGate`: blocks tool execution when required user intent or context is underspecified.
- `CanonicalArgumentScorer`: checks normalized contacts, dates, locations, IDs, and entity references.
- `InteractiveToolEvalRunner`: runs multi-turn tool conversations with replayable traces.

## Promotion Gates

- Do not promote any tool route that only passes single-turn function-calling tests.
- Require no-op/refusal behavior for insufficient-information cases.
- Check intermediate state deltas, not just final natural-language answers.
- Keep synthetic user data separate from real user profiles and live tools.

## Risks

- Benchmark scenarios may not match NexusNet-specific tools without adapter work.
- Stateful evaluation can hide errors if the simulator is too forgiving.
- Good tool use still needs separate policy, identity, and authority gates.
