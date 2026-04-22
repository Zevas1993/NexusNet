# Task Scope: 2026 Live Validation And Productionization

## Accepted Baseline
- Retrieval-policy rerank evidence bundles are accepted baseline infrastructure.
- The rerank promotion bridge is accepted baseline infrastructure.
- AITune supported-lane readiness is accepted baseline infrastructure.
- The TriAttention comparative harness is accepted baseline infrastructure.
- Wrapper, ops, and visualizer read-only inspection surfaces for these artifacts are accepted baseline infrastructure.
- Existing 2026 assimilation docs, playbooks, task scopes, and run logs are accepted baseline infrastructure.

## Highest-Value Gaps
- AITune supported-lane execution is readiness-only and needs a real runner contract, richer health reporting, and better mock/live validation artifacts.
- Retrieval-policy rerank evidence is persisted, but operator review and evaluator-facing reports remain too raw and artifact-centric.
- TriAttention comparative baselines exist, but the evidence is still too synthetic and needs stronger comparative summaries and in-repo path provenance.
- Wrapper, ops, and visualizer surfaces should expose report IDs, threshold versions, skip reasons, readiness state, and comparative evidence more directly.

## This Run Will Touch
- `nexusnet/runtime/qes/*`
- `nexusnet/retrieval/rerank/*`
- `nexusnet/promotions/*`
- `nexusnet/evals/*`
- `research/attention_providers/*`
- `nexus/api/app.py`
- `nexus/services.py`
- `nexus/operator/kernel.py`
- `nexusnet/ui_surface/surface.py`
- `nexusnet/visuals/layout.py`
- `ui/visualizer/app.js`
- `runtime/config/aitune.yaml`
- targeted live-validation docs under `docs/`
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
