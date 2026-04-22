# Goose Flow Families and Live-Probe Readiness Run Log

## Baseline
- Goose gateway breadth and policy-versioning work are accepted as correct baseline infrastructure.
- The prior lifecycle/certification run is also accepted as baseline and will be extended, not redone.
- This run is additive and focuses on broader flow families, compare/export readiness, policy-family maturity, ACP probe readiness, and operator-facing read-only usability.

## Planned Work
1. Persist explicit Goose flow-family classification in gateway-linked execution artifacts and summaries.
2. Add read-only compare/export endpoints for gateway history, policy history, certification artifacts, and adversary reviews.
3. Expand ACP diagnostics to distinguish simulated posture from live-probe-capable readiness while preserving graceful absence handling.
4. Surface family counts, compare refs, and export-ready summaries through wrapper and visualizer inspection paths.
5. Validate with focused Goose regressions, then broader suites.

## Implementation Notes
- Audit complete. The highest-leverage missing seam is broader flow-family classification and operator compare/export workflows on top of the accepted lifecycle/certification baseline.
- Current ACP config still exposes no real enabled provider endpoint in repo config, so this run should improve live-probe readiness shape and simulated diagnostics rather than making ACP mandatory.
- Added explicit `flow_families` classification to stored recipe, runbook, and gateway execution artifacts in `nexusnet/recipes/execution_store.py`, then exposed flow-family counts and latest-by-family summaries through recipe history, runbook history, gateway history, reports, wrapper state, and visualizer runtime posture.
- Added read-only compare endpoints for recipe history, runbook history, gateway history, policy history, extension certifications, and adversary reviews through `nexus/api/app.py`, plus comparison helpers in the corresponding gateway, extension-catalog, adversary-review, and execution-history services.
- Expanded ACP diagnostics and capability reporting so provider health now distinguishes simulated versus live-probe-capable posture, exposes probe-mode and probe-status counts, and publishes bounded live-probe examples without making ACP required.
- Updated wrapper and visualizer read-only compare refs and runtime posture text so operators can see flow-family breadth, compare entry points, and ACP probe readiness from existing surfaces only.
- Updated Goose docs, assimilation docs, and the research pattern registry to reflect flow-family classification, compare workflows, and ACP live-probe readiness semantics.

## Validation
- `python -m py_compile nexusnet/recipes/execution_store.py nexusnet/recipes/history/service.py nexusnet/recipes/reports.py nexusnet/runtime/gateway/service.py nexusnet/tools/extensions/catalog.py nexusnet/tools/adversary_review/service.py nexusnet/providers/acp/diagnostics.py nexusnet/runtime/acp/capabilities.py nexusnet/runtime/acp/health.py nexusnet/runtime/acp/service.py nexus/api/app.py nexusnet/ui_surface/surface.py nexusnet/visuals/layout.py`
- `node --check ui/visualizer/app.js`
- `python -m pytest tests\\test_goose_policy_versioning.py -q` -> `5 passed`
- `python -m pytest tests\\test_goose_gateway_coverage.py -q` -> `4 passed`
- `python -m pytest tests\\test_goose_operationalization.py -q` -> `5 passed`
- `python -m pytest tests\\test_goose_policy_versioning.py tests\\test_goose_gateway_coverage.py tests\\test_goose_operationalization.py tests\\test_goose_assimilation.py tests\\test_goose_real_flow_expansion.py tests\\test_nexusnet_wrapper_surface.py tests\\test_nexusnet_visualizer.py -q` -> `30 passed`
- `python -m pytest -q` -> `123 passed, 1 skipped`

## Failures Fixed
- Initial operator comparison validation assumed `approval-heavy` would always distinguish the ACP review path from the baseline gateway path. Actual bounded governance behavior correctly marked both paths as approval-heavy, so the comparison validation was tightened to the truly distinguishing `acp-bridged` family instead.

## Blockers
- None.
