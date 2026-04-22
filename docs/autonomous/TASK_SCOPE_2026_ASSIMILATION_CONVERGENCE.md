# Task Scope: 2026 Assimilation Convergence

## Accepted Baseline
- Two-stage retrieval reranking is accepted baseline infrastructure.
- Retrieval rerank corpora, thresholds, and scorecards are accepted baseline infrastructure.
- NexusNet-owned gateway, skills, and approvals are accepted baseline infrastructure.
- Edge vision operationalization is accepted baseline infrastructure.
- Bounded AITune validation is accepted baseline infrastructure.
- Governed skill evolution, MiniMax M2.7 reference/benchmark, and TriAttention research harness scaffolds are accepted baseline infrastructure.
- Current playbook, task-scope, and run-log docs are accepted baseline infrastructure.

## Highest-Value Gaps
- Retrieval rerank scorecards are operational but not yet promotion-evidence first-class artifacts.
- EvalsAO reports retrieval rerank artifacts, but does not yet consume a dedicated rerank evidence bundle contract.
- AITune is gracefully skip-safe, but the supported Linux plus NVIDIA validation lane still needs a real runner, matrix, and readiness reporting path.
- TriAttention benchmarks exist, but comparative evidence against accepted long-context baselines is still weak.
- Wrapper, ops, and visualizer inspection should expose convergence artifacts more explicitly, not only baseline summaries.

## This Run Will Touch
- `nexusnet/promotions/*`
- `nexusnet/retrieval/rerank/*`
- `nexusnet/evals/*`
- `nexusnet/runtime/qes/*`
- `research/attention_providers/*`
- `nexus/api/app.py`
- `nexus/services.py`
- `nexus/operator/kernel.py`
- `nexusnet/ui_surface/surface.py`
- `nexusnet/visuals/layout.py`
- `runtime/config/aitune.yaml`
- `docs/autonomous/*`
- targeted convergence docs under `docs/`
- targeted tests under `tests/`

## Boundaries
- No redesign of the current teacher historical/live split, teacher benchmark/cohort governance, or visual subsystem.
- No replacement of canonical runtime backends with AITune.
- No promotion of TriAttention to default-on.
- No second control plane and no second visualizer.
- Unsupported environments must remain graceful and skip-safe.

## Dirty-Tree Risk
- The repo already contains substantial unrelated tracked and untracked drift outside this task.
- Temporary pytest/cache permission noise exists in some generated directories and should be ignored unless it blocks validation.
