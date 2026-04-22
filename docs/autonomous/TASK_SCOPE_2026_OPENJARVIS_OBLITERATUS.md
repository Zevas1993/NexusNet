# Task Scope: 2026 OpenJarvis + OBLITERATUS Bounded Assimilation

## Accepted Baseline
- The 2026 convergence/live-validation baseline remains accepted infrastructure.
- Retrieval rerank evidence, AITune readiness, TriAttention comparative harnessing, and read-only inspection surfaces remain accepted infrastructure.
- Existing wrapper, visualizer, gateway, skill-evolution, MiniMax, and research-track scaffolds remain accepted infrastructure unless validation proves a mismatch.

## Highest-Value Gaps
- NexusNet lacked a productized local-first runtime init/doctor/preset lane inspired by OpenJarvis.
- Skills cataloging, sync planning, benchmarking, and optimization were still thinner than the existing gateway baseline deserved.
- Scheduled-monitor style persistent workflows were not yet explicit first-class summaries.
- Evaluator dimensions did not yet expose energy, FLOPs, and dollar-cost estimates alongside latency.
- There was no quarantined interpretability/red-team lane for safe OBLITERATUS-derived analysis and rebound detection.

## This Run Touches
- `runtime/config/openjarvis_lane.yaml`
- `nexusnet/runtime/init/*`
- `nexusnet/runtime/doctor/*`
- `nexusnet/tools/skills/*`
- `nexusnet/runtime/gateway/*`
- `nexusnet/agents/scheduled/*`
- `nexusnet/evals/cost_energy/*`
- `research/interpretability/guardrail_analysis/*`
- `research/red_team/refusal_circuit_review/*`
- `nexusnet/evals/red_team/*`
- wrapper/ops/visualizer read-only inspection surfaces
- docs and tests for these bounded assimilations

## Boundaries
- No second control plane.
- No replacement of NexusNet with OpenJarvis or OBLITERATUS.
- OBLITERATUS main purpose is not assimilated.
- No safety-removal features, no liberation presets, no mainline weight surgery, and no default-on red-team lane.
- Local-first operation remains preferred and the visualizer remains read-only.

## Dirty-Tree Risk
- The repo already contains substantial unrelated tracked and untracked drift outside this task.
- Temp/cache directories may still emit permission noise during status scans and broad test passes.
