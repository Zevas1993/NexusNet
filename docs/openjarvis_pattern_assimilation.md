# OpenJarvis Pattern Assimilation

## Purpose
This lane assimilates OpenJarvis-style productization patterns into NexusNet without replacing the brain-first runtime, wrapper, or gateway baseline.

Primary source checked on 2026-04-13:
- https://github.com/open-jarvis/OpenJarvis

## What NexusNet Steals
- Hardware-aware `init` and `doctor` style first-run guidance.
- Preset bundles for `deep-research`, `code-assistant`, `scheduled-monitor`, and `simple-chat`.
- A local-first skills catalog with sync-plan, benchmark, and optimization summaries.
- Persistent scheduled-operative patterns with memory, traceability, and governed approvals.
- Evaluator dimensions that include energy, FLOPs, latency, and dollar cost next to correctness-oriented metrics.

## What NexusNet Refuses
- Replacing the NexusNet-owned gateway/control plane with an outside shell.
- Treating presets as a new canonical runtime hierarchy.
- Cloud-first defaults.
- Ungoverned skill imports or hidden execution surfaces.

## Implementation Notes
- `runtime/config/openjarvis_lane.yaml` defines preset bundles, scheduled workflows, skills import sources, and cost/energy defaults.
- `/ops/brain/runtime/init` exposes first-run recommendations and preset catalog state.
- `/ops/brain/runtime/doctor` exposes hardware-aware recommendations and runtime-fit findings.
- `/ops/brain/skills/catalog` exposes read-only catalog, sync plans, local-trace benchmarking, and optimization hints.
- `/ops/brain/agents/scheduled` exposes persistent scheduled-operative workflow summaries.
- `/ops/brain/evals/cost-energy` exposes evaluator-ready energy/FLOPs/latency/cost dimensions.

## Governance
- Local-first remains the default.
- Cloud fallback is advisory and only recommended when local fit is insufficient.
- Scheduled workflows remain subordinate to NexusNet AOs and wrapper surfaces.
- Skills sync remains read-only planning and allowlist-aware.
