# Core Evidence-Driven Execution

## Goal
Teacher, dream, distillation, evaluator, and native-takeover evidence now influences bounded core execution decisions in the real brain path instead of living only in summaries and operator reports.

## Decision Inputs
- teacher evidence bundle count, selected teachers, and benchmark families
- latest dream episode for the active session or trace
- distillation lineage artifacts and source kinds
- native-takeover candidate refs, replacement-readiness report IDs, and governed promotion summaries
- runtime/QES posture, safe-mode state, and long-context cap
- MemoryNode active planes and foundry-evidence planes
- Mixtral + Devstral + NexusNet fusion scaffold readiness

## Execution Modes
- `teacher_fallback`: teacher-backed attached model stays primary because alignment, teacher evidence, runtime posture, or bounded-native evidence is not ready enough
- `native_shadow`: internal experts run in shadow and emit bounded advisory guidance while the teacher-attached path remains primary
- `native_challenger_shadow`: internal experts run as challenger shadow participants and explicitly compare against the teacher path
- `native_planner_live`: internal experts emit live planner guidance into the prompt, but teacher-attached generation remains the final fallback and arbiter path
- `native_live_guarded`: guarded live-native consideration is allowed only while disagreement, confidence, rollback, evaluator, and governance checks remain bounded and explicit

## Governed Behavioralization
- the execution policy now records a `proposed_execution_mode` and an effective `execution_mode`
- foundry-native behavior summaries can clamp the proposed posture through governed actions before attachment and prompt shaping
- Expert–Router Alignment can hold native behavior below the proposed posture even when foundry and evaluator evidence are otherwise stronger
- governed action can suppress native guidance entirely, downgrade live-native consideration to shadow, or keep the system in teacher fallback
- runtime-only fallback triggers remain separate from policy-time clamp reasons so the repo can distinguish conservative planning from actual post-execution rollback
- post-runtime promotion linkage can become more conservative than policy-time allowance, but it cannot silently escalate past the earlier governed clamp
- bounded native execution can now produce an explicit native candidate draft plus activation metadata when the current effective behavior allows it

## Evidence Influence
- teacher evidence anchors expert weighting and can force fallback if the teacher anchor is missing
- dream episodes can enable challenger-shadow consideration
- distillation lineage can strengthen native-shadow or planner-live consideration
- foundry replacement readiness, decision lineage, and evaluator artifacts can open guarded-live or challenger-shadow consideration, but never silent live takeover
- alignment blockers can force a `hold_for_alignment` posture that keeps native behavior bounded to shadow or teacher fallback until bridge work is ready
- disagreement and low-confidence signals can force a bounded return to the teacher path even when foundry evidence is strong

## Bounded Behavior
- evidence never mutates behavior silently; a policy ID, governed action, reasons, evidence refs, and rollback guard are recorded
- native behavior remains teacher-fallback-safe on this host
- direct full native takeover is still deferred; this lane only plans, challenges, or guarded-lives bounded native execution
- execution policy, native execution, and promotion linkage are persisted into the core execution artifact and wrapper surface
- bounded native execution now emits teacher-comparison verdicts, alignment-aware recommendations, native response outlines, native candidate artifacts, and behavior-loop next steps instead of only emitting planner summaries

## Files
- `nexusnet/core/evidence_feeds.py`
- `nexusnet/core/execution_policy.py`
- `nexusnet/core/native_execution.py`
- `nexusnet/core/brain.py`
- `docs/core_promotion_replacement_linkage.md`
