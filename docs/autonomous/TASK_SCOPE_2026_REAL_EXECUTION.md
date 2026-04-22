# Task Scope: 2026 Real Execution And Evidence Hardening

## Accepted Baseline
- Retrieval-policy rerank evidence bundles are accepted baseline infrastructure.
- The rerank promotion bridge and retrieval review/reporting baseline are accepted baseline infrastructure.
- AITune supported-lane readiness and simulated validation baseline are accepted baseline infrastructure.
- The TriAttention comparative harness and current comparative-summary baseline are accepted baseline infrastructure.
- Wrapper, ops, and visualizer read-only inspection surfaces for these artifacts are accepted baseline infrastructure.
- Existing 2026 assimilation docs, playbooks, task scopes, and run logs are accepted baseline infrastructure.

## Highest-Value Gaps
- AITune validation still lacks benchmark-grade validation artifacts in the live-validation path when running in simulated or future live mode.
- Retrieval-policy promotion review is readable, but ops-level summaries and stable review/report discovery can still be stronger.
- TriAttention comparative baselines carry in-repo provenance, but the evidence does not yet use runtime-profile-aware baseline manifests or richer head-to-head operator summaries.
- Wrapper, ops, and visualizer surfaces still need more explicit artifact discovery for execution plans, review bundles, comparative summaries, and threshold/report identifiers.

## This Run Will Touch
- `nexusnet/runtime/qes/*`
- `nexusnet/retrieval/rerank/*`
- `nexusnet/promotions/*`
- `nexusnet/evals/*`
- `research/attention_providers/*`
- `nexus/api/app.py`
- `nexus/services.py`
- `nexusnet/ui_surface/surface.py`
- `nexusnet/visuals/layout.py`
- `ui/visualizer/app.js`
- `runtime/config/aitune.yaml`
- targeted real-execution docs under `docs/`
- targeted tests under `tests/`

## Boundaries
- No redesign of accepted retrieval reranking, gateway, edge vision, AITune, MiniMax, TriAttention, teacher governance, or visual subsystem baselines.
- No replacement of canonical runtime backends with AITune.
- No promotion of TriAttention out of research-track default-off status.
- No second control plane and no second visualizer.
- Unsupported environments must remain graceful and skip-safe.
- The visualizer remains read-only.

## Dirty-Tree Risk
- The repo already contains substantial unrelated tracked and untracked drift outside this task.
- Temporary pytest/cache directories may emit permission noise during status scans and broader validation.
