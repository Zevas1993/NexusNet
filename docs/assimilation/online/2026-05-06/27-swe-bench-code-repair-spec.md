# SWE Bench Code Repair Spec

Status: P1 online assimilation target. Research-only until local runner cost, license terms, and benchmark contamination controls are inspected.

## Source Evidence

- SWE-bench repository: https://github.com/SWE-bench/SWE-bench
- SWE-bench project docs: https://www.swebench.com/
- SWE-bench paper: https://arxiv.org/abs/2310.06770
- SWE-bench Multimodal paper: https://arxiv.org/abs/2410.03859
- Source status: public repository, docs, datasets, and primary paper pages.

## Finding

SWE-bench turns real GitHub issues into repository-level patch tasks with Docker-backed evaluation. The Verified subset and Multimodal extension are especially relevant because they add human-solvability filtering and visual software domains.

## NexusNet Assimilation Target

Use SWE-bench-style issue-to-patch certification for NexusNet coding lanes. A coding agent should produce a diff, run tests, preserve logs, explain failures, and survive review gates before being considered useful for commercial code work.

## Proposed NexusNet Components

- `CodeIssuePassport`: repository snapshot, issue statement, allowed files, dependency setup, and evaluator script.
- `PatchTrace`: plan, touched files, test commands, failure iterations, final diff digest, and reviewer notes.
- `RepoSandboxRunner`: disposable checkout, dependency cache boundary, test runner, and network policy.
- `RegressionOracle`: records pass/fail tests, skipped tests, changed tests, and suspected verifier sabotage.
- `CodeLaneScorecard`: separates compilation, tests, style, reviewability, and user-acceptance dimensions.

## Promotion Gates

- Tests and diff review must both pass; agent-reported completion is not enough.
- Protect benchmark tests, lockfiles, CI, and verifier scripts from weakening edits.
- Track benchmark contamination and do not train or tune on held-out solutions.
- Keep benchmark runs separate from real customer repositories.

## Risks

- Real user tasks are often less formal than benchmark issue statements.
- Docker setup, dependency caches, and language-specific environments can dominate runtime cost.
- A high SWE-bench score can still miss product judgment, architecture fit, and support handoff quality.
