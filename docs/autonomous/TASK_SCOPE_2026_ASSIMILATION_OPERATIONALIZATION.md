# Task Scope: 2026 Assimilation Operationalization

## Accepted Baselines
- Two-stage retrieval reranking is accepted baseline infrastructure.
- NexusNet-owned OpenClaw-style local gateway / skills / approvals is accepted baseline infrastructure.
- The explicit LFM2.5-VL-450M edge vision lane is accepted baseline infrastructure.
- The additive AITune baseline/extensions are accepted baseline infrastructure.
- Governed prototype/research scaffolds for SkillClaw, MiniMax M2.7, and TriAttention are accepted baseline infrastructure.
- Current docs/playbook/task-scope artifacts are accepted baseline infrastructure.

## Highest-Value Gaps
- Retrieval reranking needs richer corpora, thresholds, scorecards, and promotion-grade inspection.
- Gateway/skills/approvals needs stronger provenance, persistence through traces, and clearer operator visibility.
- Edge vision needs measurable benchmark coverage rather than metadata only.
- AITune needs a bounded validation matrix and future-ready supported-lane harness.
- Skill evolution, MiniMax, and TriAttention need more operational evidence paths and inspection visibility.

## This Task Will Touch
- Retrieval rerank operationalization modules, configs, EvalsAO linkage, and inspection surfaces.
- Gateway/skills/approvals provenance and read-only wrapper/visualizer visibility.
- Edge vision benchmarking, latency-profile visibility, and safe-mode suitability inspection.
- Bounded AITune validation infrastructure and validation-matrix docs.
- Governed skill-evolution artifact flow and stronger MiniMax/TriAttention operational docs or harness support.
- Task-scoped run log and operationalization docs.

## Major Path Families Touched
- `nexus/retrieval/service.py`, `nexus/operator/kernel.py`, `nexus/services.py`, `nexus/api/app.py`
- `nexusnet/retrieval/rerank/*`, `nexusnet/retrieval/evals/*`
- `nexusnet/runtime/gateway/*`, `nexusnet/tools/policy/*`, `nexusnet/ui_surface/*`, `nexusnet/visuals/layout.py`
- `nexusnet/vision/edge_vlm/*`, `nexusnet/vision/grounding/*`, `nexusnet/vision/function_calling/*`, `nexusnet/vision/latency_profiles/*`
- `nexusnet/runtime/qes/aitune_*`
- `nexusnet/federation/skills/*`, `nexusnet/tools/skill_evolution/*`, `nexusnet/curriculum/skill_refinement/*`
- `nexusnet/benchmarks/agent_harness/*`, `nexusnet/teachers/minimax_m27_profile.yaml`
- `research/attention_providers/*`
- `runtime/config/retrieval.yaml`, `runtime/config/vision_edge.yaml`, `runtime/config/aitune.yaml`
- operationalization docs under `docs/`
- `tests/test_assimilation_operationalization.py`

## Boundary Conditions
- No second control plane above NexusNet.
- No second canonical visualizer.
- No replacement of dedicated runtime backends with AITune.
- No replacement of broader multimodal teachers with the edge lane.
- No bypass of EvalsAO / promotion / rollback discipline.
- Unsupported environments must remain graceful and local-safe.

## Known Dirty-Tree Risk
- The repo already contains substantial tracked and untracked drift outside this task.
- Pytest temp/cache directories in the workspace may produce permission-denied warnings during broad status scans.
