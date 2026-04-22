# Task Scope: 2026 Research Assimilation

## Accepted Baselines
- Teacher historical/live split is accepted canon.
- Teacher benchmark/cohort/trend governance is accepted canon.
- Visual subsystem baseline and production-grade expansion are accepted canon.
- Existing AITune adapter/provider baseline is accepted canon.
- Existing promotion/foundry/evals wiring stays in place unless a new lane needs additive extension.

## This Task Touches
- Retrieval hardening and rerank provenance.
- Runtime gateway, policy, skills, and approval pattern assimilation.
- Edge vision lane scaffolding with explicit LFM2.5-VL-450M provider metadata.
- Bounded AITune extensions only where visibility or artifact discipline is still missing.
- Prototype scaffolds for skill evolution and MiniMax M2.7.
- Research-track attention-provider scaffolding for TriAttention.
- Source-backed assimilation playbook and run log.

## Major Path Families Touched
- `nexus/retrieval/service.py`, `nexus/operator/kernel.py`, `nexus/services.py`, `nexus/api/app.py`
- `nexusnet/retrieval/rerank/*`, `nexusnet/retrieval/evals/*`
- `nexusnet/runtime/gateway/*`, `nexusnet/tools/skills/*`, `nexusnet/tools/policy/*`, `nexusnet/tools/approvals/*`
- `nexusnet/vision/edge_vlm/*`, `nexusnet/vision/grounding/*`, `nexusnet/vision/function_calling/*`, `nexusnet/vision/latency_profiles/*`
- `nexusnet/runtime/qes/aitune_*`
- `nexusnet/federation/skills/*`, `nexusnet/tools/skill_evolution/*`, `nexusnet/curriculum/skill_refinement/*`
- `nexusnet/benchmarks/agent_harness/*`, `nexusnet/agents/teams/*`, `nexusnet/teachers/minimax_m27_profile.yaml`
- `research/attention_providers/*`
- `runtime/config/features.yaml`, `runtime/config/retrieval.yaml`, `runtime/config/vision_edge.yaml`, `runtime/config/aitune.yaml`
- `tests/test_research_assimilation.py`
- assimilation docs under `docs/` and `docs/research/`

## Repo Insertion Points Confirmed
- Retrieval seam: `nexus/retrieval/service.py`
- Trace and promotion seam: `nexus/operator/kernel.py`
- Wrapper inspection seam: `nexusnet/ui_surface/surface.py`
- Runtime/QES seam: `nexusnet/runtime/registry.py`, `nexusnet/runtime/qes/*`
- Teacher metadata seam: `nexusnet/teachers/registry.py`
- Services/app seams: `nexus/services.py`, `nexus/api/app.py`

## Ship/Prototype/Research Split
- Ship now: cross-encoder reranking, OpenClaw-style gateway patterns, explicit LFM2.5-VL-450M edge lane, bounded AITune extensions.
- Prototype next: governed skill evolution, MiniMax M2.7 teacher and harness lane.
- Research only: TriAttention provider registry and benchmark harness.

## Boundary Conditions
- No second visualizer.
- No second control plane above NexusNet.
- No replacement of canonical runtimes with AITune.
- No replacement of the current teacher/governance baseline.
- No mutation path that bypasses EvalsAO, promotion, or rollback.

## Known Dirty-Tree Risk
- The repo already contains substantial tracked and untracked drift outside this task.
- This run will scope its own docs, configs, code, and tests and avoid reverting unrelated changes.
- `git status --short` also shows broad pre-existing tracked/untracked churn outside this work and several permission-denied pytest temp/cache directories.
