# Goose Real-Flow Expansion Run Log

## Baseline
- Goose hardening baseline accepted as correct infrastructure.
- This run is additive and focuses on broader real-flow linkage, scheduled persistence, ACP diagnostics, adversary hardening, and inspection depth.

## Planned Work
1. Expand Goose execution trace linkage into more real runtime and scheduled flows.
2. Persist scheduled-monitor and scheduled-recipe artifacts with linked trace and report references.
3. Deepen ACP provider health and compatibility diagnostics without making ACP mandatory.
4. Expand adversary-review coverage for more high-risk gateway, extension, and ACP inheritance paths.
5. Surface the new artifacts through wrapper, ops, and visualizer reads.
6. Validate with targeted and broader regression tests.

## Implementation Notes
- Audit complete. The highest-value initial gap is that scheduled artifacts still rely too much on summary-time capture instead of execution-linked persistence.
- Added schedule-aware execution-linked persistence for recipe, runbook, and bounded subagent flows so scheduled artifacts can carry linked execution IDs, trace IDs, report IDs, and gateway resolution IDs.
- Expanded recipe/runbook history summaries with `schedule_id` and `trigger_source` filtering plus richer latest-artifact linkage fields.
- Extended ACP diagnostics with readiness summaries, recommended actions, extension compatibility, feature incompatibility counts, and richer provider detail drill-down.
- Expanded adversary review with an explicit `extension-acp-privilege-inheritance-confusion-risk` family and kept fail-closed or escalate behavior intact.
- Deepened visualizer runtime posture with schedule-specific artifact drill-down, richer ACP readiness counts, and adversary trigger visibility.

## Validation
- `python -m py_compile nexus\api\app.py nexus\services.py nexusnet\agents\subagents\service.py nexusnet\agents\scheduled\artifacts.py nexusnet\agents\scheduled\history.py nexusnet\agents\scheduled\reports.py nexusnet\agents\scheduled\service.py nexusnet\recipes\execution_store.py nexusnet\recipes\history\service.py nexusnet\recipes\reports.py nexusnet\runbooks\history\service.py nexusnet\runtime\acp\capabilities.py nexusnet\runtime\acp\health.py nexusnet\runtime\acp\service.py nexusnet\providers\acp\diagnostics.py nexusnet\tools\adversary_review\policies.py nexusnet\tools\adversary_review\service.py nexusnet\tools\adversary_review\reports.py nexusnet\evals\red_team\gateway_scenarios.py nexusnet\visuals\layout.py tests\test_goose_real_flow_expansion.py tests\test_goose_operationalization.py`
- `node --check ui\visualizer\app.js`
- `python -m pytest tests\test_goose_real_flow_expansion.py -q` -> `4 passed`
- `python -m pytest tests\test_goose_real_flow_expansion.py tests\test_goose_operationalization.py tests\test_goose_assimilation.py tests\test_supported_host_execution.py tests\test_nexusnet_visualizer.py tests\test_nexusnet_wrapper_surface.py tests\test_nexusnet_promotion_loop.py -q` -> `27 passed`
- `python -m pytest -q` -> `114 passed, 1 skipped`

## Failures Fixed
- Scheduled summary inspection initially assumed the globally latest artifact was always the one the operator wanted. Added per-workflow latest scheduled artifact visibility and aligned tests to the workflow-specific surface.
- Visualizer scheduled posture initially surfaced the global latest scheduled artifact instead of the `scheduled-monitor` artifact. Switched the runtime posture drill-down to prefer the workflow-specific artifact.

## Blockers
- None.
