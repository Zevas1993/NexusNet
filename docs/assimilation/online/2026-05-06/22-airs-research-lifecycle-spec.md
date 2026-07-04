# AIRS Research Lifecycle Spec

Status: P2 online assimilation target. Research-only until task format, license, and compute cost are inspected.

## Source Evidence

- AIRS-Bench paper: https://arxiv.org/abs/2602.06855
- AIRS-Bench repository: https://github.com/facebookresearch/airs-bench
- Source status: primary paper page and public benchmark repository.

## Finding

AIRS-Bench evaluates autonomous AI research agents across 20 tasks sourced from machine-learning papers. Tasks cover idea generation, experiment analysis, iterative refinement, and submissions evaluated against metrics and human SOTA values, with no baseline code provided.

## NexusNet Assimilation Target

Use AIRS-Bench as the pattern for bounded research/dreaming lanes. NexusNet should only attempt autonomous research loops when a task has a dataset, metric, baseline/SOTA target, reproducible environment, and cost budget.

## Proposed NexusNet Components

- `ResearchTaskPassport`: paper source, dataset, metric, SOTA reference, compute budget, and allowed methods.
- `ExperimentLedger`: hypothesis, code changes, metric result, seed, artifact path, and failed attempts.
- `ResearchHarnessAdapter`: isolates dataset downloads, scripts, and submissions from the main repo.
- `TeacherCouncilReview`: reviews novelty and regression risk before a result becomes a recommendation.

## Promotion Gates

- Require objective metrics before automated research search.
- Sandbox datasets and generated code.
- Record failed experiments, not just the best result.
- Keep results as recommendations until reviewed by the operator.

## Risks

- Research tasks can consume substantial compute.
- Benchmark overfitting is easy if the agent sees public solutions.
- Metric wins may not translate into useful NexusNet behavior.
