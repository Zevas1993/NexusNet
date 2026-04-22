# Task Scope: 2026 Goose Refinement and Certification Depth

## Accepted Baseline
- goose lane config and service registration
- recipe and runbook schema plus baseline examples
- bounded subagent, delegation, and parallel lanes
- extension catalog and extension governance baseline
- versioned policy-set baseline
- flow-family classification baseline
- compare endpoint baseline
- visualizer compare control baseline
- lifecycle fixture baseline
- certification lineage baseline
- ACP compare/export readiness baseline
- permission, sandbox, persistent-instruction, and adversary-review baselines
- wrapper, ops, and visualizer read-only Goose inspection baseline
- current Goose docs, playbook, and task-scope artifacts

## Current State At Start
- Goose compare views already exist for gateway, policy history, certification, adversary review, and ACP provider readiness.
- The visualizer already exposes first-class Goose compare selectors and a read-only diff card.
- Policy lifecycle history already includes explicit `superseded`, `rolled_back`, and `held` fixtures.
- Certification artifacts already expose lineage IDs, restoration detection, permission deltas, and compare/export reports.
- ACP compare/export already exists in read-only form and gracefully degrades because repo config still ships disabled/null-endpoint ACP providers.

## This Task Touches
- grouped and collapsible visualizer diff rendering for large compare payloads
- deeper stored certification lineage fixtures and related provenance/history drill-down
- stronger compare/export markdown quality for operators
- richer ACP simulated/live readiness summaries and bounded live-probe report shape
- focused Goose docs, tests, and task-scoped validation

## Highest-Value Gaps At Start
- large compare payloads still flatten into a single diff card rather than grouped sections by policy, certification, permission, ACP, adversary, and gateway categories
- certification lineage is still strongest on the current artifact; historical stored certification chains are shallower than policy history
- compare/export markdown remains readable but still light on grouped operator sections and lineage context
- ACP readiness still lacks richer blocked/live-probe readiness guidance when no real provider is available

## Canon Preserved
- NexusNet remains brain-first and the neural-network upgrade path
- Nexus remains the shell, platform, and runtime surface
- Goose-derived patterns stay subordinate to Nexus and NexusNet
- ACP remains optional and provider-gated
- high-risk review remains fail-closed or escalate, never fail open
- wrapper and visualizer remain read-only inspection surfaces
- no second control plane or second UI system is introduced

## Known Unrelated Dirty-Tree Risk
- The repo still has substantial pre-existing tracked and untracked drift outside this task.
- Temp/cache permission-denied noise remains visible in `git status` and is unrelated to this run.

## Planned High-Leverage Iterations
1. Add grouped/collapsible Goose diff presentation and expose grouping metadata through existing read-only surfaces.
2. Seed deeper stored certification history so revoked, restored, rolled-back, and held lineage is represented by multiple historical certification artifacts.
3. Improve ACP readiness/probe reporting for simulated posture and bounded live-probe readiness without making ACP mandatory.
4. Tighten operator compare/export markdown and validate targeted Goose, wrapper, visualizer, and ACP surfaces.

## Outcome Snapshot
- Visualizer Goose compare cards now group large diff payloads into canonical read-only sections aligned with the backend compare-group catalog.
- Extension certification now persists deeper stored lineage across historical artifacts, restoration targets, lineage depth, and transition summaries.
- Provenance, compare payloads, and compare/export markdown now surface certification lineage context instead of flattening everything to current-state status.
- ACP diagnostics now expose probe-readiness state, bounded probe budgets, execution policy, and live-probe blockers while preserving graceful degradation when no real provider exists.
