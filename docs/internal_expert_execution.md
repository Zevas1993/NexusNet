# Internal Expert Execution

## Purpose
Internal expert execution is now a bounded runtime and harness layer inside the real brain path, not just passive expert definitions.

## Contracts
- capability gating per internal expert
- selected internal expert set from the fusion scaffold and execution policy
- bounded output capture for each participating expert
- disagreement capture across enabled experts
- explicit challenger-versus-teacher comparison when required
- explicit teacher-comparison verdicts and recommended bounded execution mode
- bounded native response outlines for prompt shaping and traceability
- bounded native candidate drafts with activation mode, confidence, and teacher-verification requirements
- explicit safe fallback to the teacher-attached model path
- guarded-live checks that can be blocked by disagreement or low confidence

## Current Runtime Shape
- `InternalExpertExecutionService` is the brain-facing entry point
- `InternalExpertRuntimeService` carries the bounded host-execution contract
- `InternalExpertHarnessService` builds capability contracts, emits bounded summaries, and records disagreement artifacts for the current trace
- the harness records both policy-time clamp reasons and runtime-only fallback triggers so post-execution rollback is distinguishable from conservative planning
- the harness now records teacher-comparison verdicts, alignment-hold runtime triggers, recommended execution mode, bounded native candidate drafts, and bounded response outlines

## Current Limits
- heavy-weight native expert inference and training are still out of scope on this host
- the strongest bounded live lane is `native_live_guarded`, not unbounded native replacement
- Critique Expert and teacher fallback remain the arbiter path
- governed action can suppress native guidance or downgrade live-native consideration even when the scaffold and runtime could technically do more
- alignment-hold behavior can now keep native execution in shadow even when evidence would otherwise justify deeper escalation

## Files
- `nexusnet/experts/execution/service.py`
- `nexusnet/experts/runtime/service.py`
- `nexusnet/experts/harness/service.py`
