# Core Promotion + Replacement Linkage

## Purpose
Dream, foundry, teacher, evaluator, and native-takeover evidence now produces a governance-visible `promotion_linkage` artifact that affects bounded core behavior inside the real NexusNet brain path instead of remaining only planning or trace metadata.

## Governed Actions
- `keep_teacher_fallback`
- `allow_native_shadow`
- `allow_native_challenger_shadow`
- `allow_native_live_guarded`
- `require_more_evidence`
- `hold_for_alignment`
- `rollback_to_teacher`

## Current Contract
- `promotion_linkage` is derived from foundry evidence, the core execution policy, evaluator and decision artifacts when present, and bounded internal expert runtime output.
- The brain records both a proposed execution posture and an effective execution posture. Governance can clamp the proposed posture before native guidance is attached to the request.
- Expert–Router Alignment can now produce an explicit `hold_for_alignment` outcome instead of collapsing everything into generic evidence insufficiency.
- Runtime disagreement or low-confidence guarded-live checks can still force a second-stage rollback to teacher fallback after policy-time allowance.
- `promotion_linkage` carries stable lineage and provenance fields including governed action, decision and evaluation refs, rollback reference, proposed mode, effective mode, alignment hold state, teacher-comparison verdicts, native candidate refs, behavior-loop next step, and fallback triggers.
- Legacy `execution_action` remains available for compatibility, but governed action is now the canonical behavior contract.
- Direct unbounded native takeover is still deferred on this host.

## Bounded Outcomes
- `keep_teacher_fallback`: teacher-backed attached execution remains primary.
- `allow_native_shadow`: native experts may contribute bounded shadow guidance only.
- `allow_native_challenger_shadow`: challenger behavior is allowed and compared against the teacher path.
- `allow_native_live_guarded`: guarded live-native participation is allowed, but only while disagreement, confidence, rollback, and evaluator checks stay bounded.
- `require_more_evidence`: the core path must stay conservative until teacher, dream, foundry, or evaluator evidence improves.
- `hold_for_alignment`: evidence may justify deeper native behavior, but Expert–Router Alignment still limits the current safe mode.
- `rollback_to_teacher`: the runtime has triggered a bounded return to the teacher path and the fallback reason is persisted.

## Behavior Loop
- `promotion_linkage.behavior_loop.next_step` now records the next bounded operator-facing behavior step such as expanding shadow execution, resolving alignment blockers, teacher-verifying a native candidate, or rolling back and rebuilding evidence.
- Native runtime now contributes a bounded native candidate artifact so deeper behavior loops can carry explicit candidate IDs and confidence without claiming unbounded native takeover.

## Inspection
- `trace.metrics.core_execution.promotion_linkage`
- `trace.metrics.core_execution.execution_policy`
- `GET /ops/brain/core`
- `GET /ops/brain/wrapper-surface`

## Files
- `nexusnet/core/native_execution.py`
- `nexusnet/core/execution_policy.py`
- `nexusnet/core/brain.py`
- `nexusnet/foundry/promotion.py`
- `nexusnet/promotions/service.py`
