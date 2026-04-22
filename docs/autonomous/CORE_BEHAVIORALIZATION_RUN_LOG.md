# Core Behavioralization + Fusion Run Log

## Baseline
- Goose remains closed and unchanged in this run.
- The evidence bridge, attach seam, bounded internal expert execution, and `promotion_linkage` artifact baseline are accepted and preserved.

## Planned Work
1. Turn promotion linkage into a governance-visible behavior clamp and rollback signal.
2. Thread governed native behavior state from promotion records into the real core policy path.
3. Preserve bounded challenger/live execution while allowing post-runtime rollback to the teacher path.
4. Update docs/tests and validate the revised core execution path.

## Audit Notes
- Audit confirmed that the prior native-execution baseline is present: brain-first wake, canonical attach seam, MemoryNode, runtime/QES planning, evidence feeds, internal expert execution, promotion linkage, and read-only wrapper/core inspection.
- The highest-leverage remaining gap is no longer visibility. It is behavioralization: governance needs to actively clamp or allow bounded native behavior instead of only describing it afterwards.

## Implementation Notes
- Added governed native behavior states to the schema and foundry promotion gate so promotion linkage now emits both legacy execution actions and the canonical governed action contract.
- Derived a native behavior summary from promotion and evaluation records and surfaced it through the evidence bridge for real policy-time use.
- Updated `CoreExecutionPolicyEngine` so it records both `proposed_execution_mode` and effective `execution_mode`, then clamps the effective mode by governed action before prompt shaping and model attachment.
- Updated `NativeExecutionPlanner` and `promotion_linkage()` so post-runtime linkage can become more conservative than policy-time allowance without silently escalating past the earlier governed clamp.
- Split policy-time fallback reasons from runtime-only fallback triggers inside the internal expert harness so real rollback remains explicit and traceable.
- Threaded governed action plus proposed versus effective execution posture into attach records, execution traces, and read-only operator surfaces.
- Strengthened targeted tests around governed clamps, guarded-live rollback, and proposed-versus-effective execution continuity.

## Validation
- `python -m py_compile nexusnet\\schemas.py nexusnet\\foundry\\promotion.py nexusnet\\promotions\\service.py nexusnet\\core\\evidence_feeds.py nexusnet\\core\\execution_policy.py nexusnet\\core\\native_execution.py nexusnet\\experts\\harness\\service.py nexusnet\\core\\brain.py nexusnet\\core\\attach_base_model.py nexusnet\\core\\model_ingestion.py nexusnet\\core\\execution_trace.py nexusnet\\ui_surface\\surface.py tests\\test_nexusnet_core_execution_fusion.py` -> passed
- `node --check ui\\visualizer\\app.js` -> passed
- `python -m pytest tests\\test_nexusnet_core_execution_fusion.py -q` -> `5 passed`
- `python -m pytest tests\\test_nexusnet_core_pivot.py tests\\test_nexusnet_core_execution_fusion.py tests\\test_nexus_phase1_foundation.py tests\\test_nexusnet_brain.py tests\\test_nexusnet_wrapper_surface.py tests\\test_nexusnet_visualizer.py -q` -> `31 passed`
- `python -m pytest -q` -> `135 passed, 1 skipped`

## Failures Fixed
- Updated targeted tests to assert the new governed-action and proposed-versus-effective execution contract instead of the earlier trace-only semantics.
- Fixed a semantic bug where policy-time conservative reasons were being treated as runtime fallback triggers, which incorrectly forced rollback behavior even when no runtime fallback had occurred.
- Fixed post-runtime promotion linkage so it can become more conservative than the earlier policy clamp, but cannot silently escalate past that governed allowance.

## Blockers
- None.

## Goose Status
- Goose remains closed and unchanged in this run. No provider-triggered Goose work is introduced here.

## Remaining Unrelated Dirty-Tree Risk
- The repo still has substantial pre-existing tracked and untracked drift outside this run.
- `git status` still reports permission-denied and cache noise under `.pytest-tmp`, `pytest-cache-files-*`, and `runtime/test-tmp-run`.
