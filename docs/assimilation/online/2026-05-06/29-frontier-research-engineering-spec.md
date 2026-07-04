# Frontier Research Engineering Spec

Status: P2 online assimilation target. Research-only until cost, GPU requirements, datasets, and license constraints are inspected.

## Source Evidence

- MLE-bench repository: https://github.com/openai/mle-bench
- MLE-bench paper: https://arxiv.org/abs/2410.07095
- PaperBench paper: https://arxiv.org/abs/2504.01848
- PaperBench repository: https://github.com/openai/frontier-evals/tree/main/project/paperbench
- RE-Bench paper: https://arxiv.org/abs/2411.15114
- Source status: primary papers plus public benchmark repositories where available.

## Finding

MLE-bench, PaperBench, and RE-Bench evaluate agents on research-engineering work that spans experiment setup, code writing, execution, reproduction, grading, and long-horizon iteration. These benchmarks are expensive but useful because they force objective artifacts rather than only natural-language research plans.

## NexusNet Assimilation Target

Constrain NexusNet research, dreaming, and self-improvement lanes around measurable experiment artifacts. Research agents should propose, run, reproduce, score, and explain experiments in shadow mode before any output influences production behavior.

## Proposed NexusNet Components

- `ResearchTaskPassport`: objective, dataset, baseline, compute budget, allowed libraries, expected artifacts, and grading rubric.
- `ExperimentTrace`: commands, notebooks, configs, seeds, metrics, artifacts, failures, and rerun notes.
- `ReproductionSandbox`: fresh environment for replaying submitted code before grading.
- `RubricGrader`: hierarchical scoring that separates setup, implementation, result quality, and explanation.
- `ResearchLineageLedger`: links ideas, experiments, failures, wins, and promoted changes without permitting autonomous production mutation.

## Promotion Gates

- Keep research outputs advisory until reviewed by a human or explicit governance lane.
- Cap compute, wall-clock time, network, and dataset access.
- Require independent reproduction before any result is treated as evidence.
- Preserve failed experiments; do not let summary-only memory erase negative results.

## Risks

- These benchmarks can require substantial GPU, storage, and wall-clock budget.
- Research scores may reward benchmark-specific scaffolding more than product value.
- Poorly governed research agents can create confusing artifacts, hidden costs, or unsafe self-modification pressure.
