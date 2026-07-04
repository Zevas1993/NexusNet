# Inspect AI Evaluation Spine Spec

Status: P1 online assimilation target. Research-only until adapter scope, license, and overlap with NexusNet's existing test infrastructure are inspected.

## Source Evidence

- Inspect documentation: https://inspect.aisi.org.uk/
- Inspect repository: https://github.com/UKGovernmentBEIS/inspect_ai
- Source status: official documentation and public open-source repository from the UK AI Security Institute.

## Finding

Inspect provides an evaluation framework built around tasks, datasets, solvers, scorers, logs, model providers, agents, tools, MCP integration, sandboxing, approval policies, and trace analysis. Its strongest value for NexusNet is the shape of an evaluation spine, not necessarily wholesale adoption.

## NexusNet Assimilation Target

Define a NexusNet eval spine that can run internal scorecards and optionally adapt external Inspect-style evaluations. The goal is one evidence model for agent runs, tool approval, sandbox results, scoring, replay, and longitudinal regression tracking.

## Proposed NexusNet Components

- `EvalTaskSpec`: dataset, input, target, solver route, tool policy, sandbox policy, scorer, and metadata.
- `SolverTrace`: model route, prompts, tool calls, approvals, retries, compaction, and final output.
- `ScorerRegistry`: deterministic scorers first, model-graded scorers with provenance where needed.
- `EvalLogStore`: immutable run logs, sample-level events, artifacts, and aggregate metrics.
- `InspectAdapter`: optional bridge for importing or exporting compatible benchmark tasks.

## Promotion Gates

- Keep deterministic checks ahead of model-graded judgments when both exist.
- Store eval logs locally by default and redact secrets before export.
- Require cost, timeout, and concurrency limits for every eval run.
- External eval imports remain refs-only until their license and data boundaries are confirmed.

## Risks

- Full framework adoption could duplicate or fight NexusNet's existing runtime/test surfaces.
- Model-graded scoring can create false confidence without calibration.
- Eval infrastructure can become shelfware unless tied to real release gates.
