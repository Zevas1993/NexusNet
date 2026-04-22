# Core Native Execution + Alignment Run Log

## Baseline
- Goose remains closed and unchanged in this run.
- The evidence bridge, attach seam, and bounded internal expert execution baseline are accepted and preserved.

## Planned Work
1. Upgrade the core policy engine to richer bounded native execution modes.
2. Thread promotion/replacement evidence into native execution planning and teacher fallback behavior.
3. Enrich attach/model-ingestion, traces, and read-only surfaces with policy and promotion linkage refs.
4. Update docs and validate the revised core execution path.

## Audit Notes
- Audit confirmed that the prior execution-fusion baseline is present: brain-first wake, canonical attach seam, MemoryNode, runtime/QES planning, evidence feeds, internal expert execution, and read-only wrapper/core inspection.
- The highest-leverage remaining gap is no longer visibility. It is bounded native decision quality and promotion/replacement linkage in the actual brain path.

## Implementation Notes
- Updated `CoreExecutionPolicyEngine` so teacher, dream, distillation, and foundry signals now select bounded `teacher_fallback`, `native_shadow`, `native_challenger_shadow`, `native_planner_live`, or `native_live_guarded` modes with explicit fallback triggers and guarded-live blockers.
- Enriched `CoreEvidenceBridge` so foundry evidence now carries takeover trend, fleet/cohort, replacement, rollback, and guarded-live readiness refs into the real core path.
- Strengthened `NativeExecutionPlanner` so the planner emits richer prompt-guidance modes, guarded-live budgets, promotion candidate state, and a promotion-linkage artifact derived from foundry evidence and bounded runtime outcomes.
- Strengthened the internal expert harness/runtime so challenger-vs-teacher comparison, guarded-live fallback, disagreement capture, and fallback-trigger reporting are explicit runtime outputs instead of implicit side effects.
- Updated `NexusBrain` so promotion linkage is recorded before model attachment, included in prompt shaping, attached-model records, saved trace metrics, and read-only summary/surface views.
- Enriched the canonical attach seam so attachment records preserve execution policy IDs, legacy execution modes, promotion action, and promotion decision IDs.
- Added `docs/core_promotion_replacement_linkage.md` and refreshed core execution/evidence docs to reflect the new bounded native execution contract.

## Validation
- `python -m py_compile nexusnet\core\execution_policy.py nexusnet\core\evidence_feeds.py nexusnet\core\native_execution.py nexusnet\core\brain.py nexusnet\core\attach_base_model.py nexusnet\core\model_ingestion.py nexusnet\core\execution_trace.py nexusnet\experts\harness\service.py nexusnet\experts\runtime\service.py nexusnet\ui_surface\surface.py tests\test_nexusnet_core_execution_fusion.py` passed.
- `node --check ui\visualizer\app.js` passed.
- `python -m pytest tests\test_nexusnet_core_execution_fusion.py -q` -> `4 passed`
- `python -m pytest tests\test_nexusnet_core_pivot.py tests\test_nexusnet_core_execution_fusion.py tests\test_nexus_phase1_foundation.py tests\test_nexusnet_brain.py tests\test_nexusnet_wrapper_surface.py tests\test_nexusnet_visualizer.py -q` -> `30 passed`
- `python -m pytest -q` -> `134 passed, 1 skipped`

## Failures Fixed
- Fixed a circular import path through `nexusnet.foundry.__init__` by converting foundry exports to lazy imports, which lets the core depend on `NativePromotionGate` without forcing the whole foundry/refinery stack to initialize during import.
- Fixed the new guarded-live test to use registered expert IDs from the adapter registry instead of an unregistered placeholder expert name.

## Blockers
- None.

## Goose Status
- Goose remains closed and unchanged in this run. No provider-triggered Goose work is introduced here.
