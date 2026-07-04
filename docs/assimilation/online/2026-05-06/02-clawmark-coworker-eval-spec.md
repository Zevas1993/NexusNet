# ClawMark Coworker Eval Spec

Status: P0 online assimilation target. Research-only until benchmark assets and license are verified.

## Source Evidence

- ClawMark paper page: https://huggingface.co/papers/2604.23781
- Source status: primary paper index with abstract, metrics, and linked arXiv/GitHub.

## Finding

ClawMark targets persistent coworker agents across multi-turn, multi-day, multimodal workflows. It uses evolving environment state across filesystem, email, calendar, knowledge base, and spreadsheet services, with deterministic Python checkers over post-execution state rather than LLM-as-judge scoring.

## NexusNet Assimilation Target

Use ClawMark as the pattern for "living workspace" certification: NexusNet should not be considered a reliable persistent coworker unless it can survive changing files, calendar-like state, new evidence, delayed updates, and multimodal artifacts without overwriting earlier provenance.

## Proposed NexusNet Components

- `WorkspaceStateScenario`: deterministic workspace fixture with staged updates.
- `PostStateChecker`: executable verifier for workspace end state and intermediate invariants.
- `CoworkerTrace`: multi-day action/evidence log that ties each decision to current state and source status.
- `KAC Intake Gate`: blocks memory promotion when the scenario has unresolved dynamic updates.

## Promotion Gates

- Import only benchmark structure first; do not ingest private user workspace data.
- Require deterministic checks for pass/fail, partial credit, and unsafe side effects.
- Keep evolving-state tests in sandbox fixtures, never live email/calendar accounts by default.

## Risks

- Multi-service benchmarks can become heavy to run locally.
- Partial progress can hide serious state-management failure.
- Multimodal evidence needs separate parser/certification gates before memory promotion.
