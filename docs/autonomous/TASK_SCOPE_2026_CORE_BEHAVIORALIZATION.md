# Task Scope: 2026 Core Behavioralization + Fusion Run

## Accepted Baseline
- Goose remains closed and is not being reopened here.
- Teacher historical/live split, benchmark/cohort/trend governance, the visual subsystem baseline, and bounded OpenClaw/AITune/TriAttention lanes are accepted.
- The current evidence bridge, canonical `attach_base_model()` seam, bounded internal expert execution, and `promotion_linkage` artifact baseline are accepted starting points.

## Current State At Start
- The repo already has a brain-first execution seam, canonical model ingestion, QES/runtime planning, MemoryNode context, MoE scaffold visibility, and bounded native modes.
- `promotion_linkage` already exists as a first-class artifact, but it still acts more like planning and trace metadata than a true governed behavior clamp.
- Internal experts already execute in bounded planner/challenger form, but governance should more directly decide whether shadow, challenger, guarded live, or teacher fallback behavior is actually allowed.

## This Task Touches
- promotion and replacement linkage behavioralization
- core execution policy and native execution gating
- attach/model-ingestion continuity for governed behavior metadata
- read-only operator visibility for governed behavior outcomes
- focused docs, tests, and run logging for the behavioralized core path

## Highest-Value Core Gaps At Start
- `promotion_linkage` does not yet clamp or allow actual bounded behavior strongly enough
- governance-visible native behavior state is not yet surfaced from promotion records into the real core path
- core traces and attachments do not yet distinguish proposed vs effective execution posture
- prompt shaping still needs clearer suppression of native guidance when governed fallback or rollback is required

## Canon Preserved
- NexusNet remains brain-first and starts before attached models
- Dream Training and Federated Continuous Learning remain mandatory implementation lines
- Mixtral + Devstral + Router + Cortex + Neural Bus remain the active scaffold branch
- Expert–Router Alignment remains a prerequisite, not an assumption
- Multi-Plane MemoryNode remains config-driven and unfrozen
- the visualizer remains read-only
- Goose remains closed unless real ACP-provider-triggered work appears

## Planned High-Leverage Iterations
1. Derive a governance-visible native behavior posture from promotion records and foundry evidence.
2. Clamp proposed native execution modes with governed action before prompt shaping and attachment.
3. Preserve a second-stage bounded rollback path after challenger/guarded-live execution checks.
4. Extend traceability, surfaces, docs, and tests around proposed vs effective execution posture.

## Implemented In This Run
- Added a governed-action contract for native behavior: `keep_teacher_fallback`, `allow_native_shadow`, `allow_native_challenger_shadow`, `allow_native_live_guarded`, `require_more_evidence`, and `rollback_to_teacher`.
- Derived governance-visible native behavior summaries from promotion and evaluation records, then fed them back into the core evidence bridge.
- Updated the execution policy to preserve both proposed and effective execution posture and to clamp native participation before prompt shaping and attachment.
- Preserved a second-stage runtime rollback path through separate runtime fallback triggers so guarded-live disagreement still rolls back explicitly without being confused with policy-time conservatism.
- Extended `promotion_linkage`, attach records, execution traces, and read-only surfaces with governed action plus proposed versus effective execution metadata.
- Strengthened targeted tests and full-suite validation around behavioralized promotion linkage and bounded guarded-live fallback.

## Remaining Gaps After This Run
- Promotion linkage now affects bounded behavior, but deeper governed promotion and replacement loops can still use the new artifact more directly.
- Internal experts remain scaffold-bounded on this host; heavier native execution remains alignment-gated.
- Fusion depth can grow further only where host runtime support is strong enough to preserve rollback and evaluator discipline.

## Known Unrelated Dirty-Tree Risk
- The repo still has substantial pre-existing tracked and untracked drift outside this run.
- Permission-denied temp and pytest cache noise remains visible under `.pytest-tmp`, `pytest-cache-files-*`, and `runtime/test-tmp-run`.
