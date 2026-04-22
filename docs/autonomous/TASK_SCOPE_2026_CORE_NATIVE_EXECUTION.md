# Task Scope: 2026 Core Native Execution + Alignment Run

## Accepted Baseline
- Goose remains closed and is not being reopened here.
- Teacher historical/live split, teacher benchmark/cohort/trend governance, the visual subsystem baseline, and bounded OpenClaw/AITune/TriAttention lanes are accepted.
- The current evidence-feed bridge in `nexusnet/core/brain.py`, the canonical `attach_base_model()` seam, and the bounded internal expert execution baseline are accepted starting points.

## Current State At Start
- The repo already has a brain-first execution seam, canonical model ingestion, QES/runtime planning, MemoryNode context, and MoE scaffold visibility.
- Teacher, dream, distillation, and native-takeover evidence are already visible in the core summary and persisted traces.
- Internal experts already execute in bounded preview/live-planner form, but native execution decisions are still too coarse and promotion/replacement linkage is not yet driving enough of the real core path.

## This Task Touches
- bounded evidence-driven native execution policy and richer execution modes
- canonical attach/model-ingestion trace enrichment for policy, mode, and promotion refs
- internal expert challenger/live-guarded behavior and disagreement-triggered fallback
- promotion and replacement linkage between foundry evidence and actual core execution
- focused docs, tests, and run logging for the core native execution line

## Highest-Value Core Gaps At Start
- evidence feeds are visible, but not yet strong enough in direct native expert execution and promotion-action selection
- execution modes remain too coarse for challenger shadow, guarded live, and explicit teacher fallback triggers
- promotion/replacement evidence is not yet threaded deeply enough into actual bounded core execution behavior
- read-only surfaces do not yet expose the new promotion linkage and fallback posture clearly enough

## Canon Preserved
- NexusNet remains brain-first and starts before attached models
- Dream Training and Federated Continuous Learning remain mandatory implementation lines
- Mixtral + Devstral + Router + Cortex + Neural Bus remain the active scaffold branch
- Expert–Router Alignment remains a prerequisite, not an assumption
- Multi-Plane MemoryNode remains config-driven and unfrozen
- the visualizer remains read-only
- Goose remains closed unless real ACP-provider-triggered work appears

## Planned High-Leverage Iterations
1. Replace coarse execution modes with bounded native fallback/shadow/challenger/live-guarded modes.
2. Feed promotion/replacement evidence into actual core execution and attach-trace artifacts.
3. Strengthen bounded internal expert challenger behavior and disagreement-triggered teacher fallback.
4. Validate the updated core path without reopening Goose or adding a second control plane.

## Implemented In This Run
- Replaced the older coarse execution labels with bounded `teacher_fallback`, `native_shadow`, `native_challenger_shadow`, `native_planner_live`, and `native_live_guarded` policy modes, while preserving legacy labels for traceability.
- Threaded foundry promotion and replacement evidence into actual core execution behavior through explicit promotion linkage, execution actions, rollback refs, and attach-seam continuity.
- Strengthened the internal expert harness so guarded-live paths can be blocked by disagreement or low-confidence signals and can fall back explicitly to the teacher-attached model path.
- Extended persisted core artifacts and wrapper-surface inspection with promotion action, decision IDs, and fallback-trigger visibility.
- Added targeted validation for guarded-live bounded behavior and promotion linkage without reopening Goose.

## Remaining Highest-Value Core Gaps
- The repo still uses bounded native planning/challenger behavior, not heavyweight internal native inference or full replacement.
- Promotion and replacement linkage now influences core execution decisions, but future work should push deeper into real expert execution and governed takeover loops.
- Fusion remains scaffold-bounded on this host; deeper expert-family execution should stay gated behind alignment and evidence.

## Known Unrelated Dirty-Tree Risk
- The repo still has substantial pre-existing tracked and untracked drift outside this run.
- Permission-denied temp and pytest cache noise remains visible under `.pytest-tmp`, `pytest-cache-files-*`, and `runtime/test-tmp-run`.
