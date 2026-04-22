# Task Scope: 2026 Supported Host Execution And UX Hardening

## Accepted Baseline
- Retrieval-policy rerank evidence bundles are accepted baseline infrastructure.
- The rerank promotion bridge and current review/reporting baseline are accepted baseline infrastructure.
- AITune supported-lane readiness is accepted baseline infrastructure.
- The TriAttention comparative harness baseline is accepted baseline infrastructure.
- Wrapper, ops, and visualizer read-only inspection surfaces for these artifacts are accepted baseline infrastructure.
- Existing 2026 docs, playbooks, task scopes, and run logs are accepted baseline infrastructure.

## Highest-Value Gaps
- AITune needs a more reproducible supported-host execution story with explicit plan artifacts, runner visibility, and operator-facing instructions.
- Retrieval-policy promotion reviews are readable, but still need better human summary, stable detail access, and evaluator-linked inspection.
- TriAttention comparative evidence still leans too heavily on heuristic anchors when runtime-profile-backed anchors are available.
- Wrapper, ops, and visualizer surfaces still need more compact report-level usability for these artifacts.

## This Run Will Touch
- `nexusnet/runtime/qes/*`
- `nexusnet/retrieval/rerank/*`
- `nexusnet/promotions/*`
- `nexusnet/evals/*`
- `research/attention_providers/*`
- `nexus/api/app.py`
- `nexusnet/ui_surface/surface.py`
- `nexusnet/visuals/layout.py`
- `ui/visualizer/app.js`
- `runtime/config/aitune.yaml`
- targeted supported-host docs under `docs/`
- targeted tests under `tests/`

## Boundaries
- No redesign of accepted retrieval, AITune, TriAttention, teacher-governance, or visualizer baselines.
- No replacement of canonical runtime backends with AITune.
- No promotion of TriAttention out of research-track default-off status.
- No second control plane and no second visualizer.
- Unsupported environments must remain graceful and skip-safe.
- The visualizer remains read-only.

## Dirty-Tree Risk
- The repo already contains substantial unrelated tracked and untracked drift outside this task.
- Temporary pytest/cache directories may emit permission noise during status scans and broader validation.
