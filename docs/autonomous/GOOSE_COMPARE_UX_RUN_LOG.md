# Goose Compare UX and Lifecycle Fixture Run Log

## Baseline
- Goose flow-family expansion work is accepted as correct baseline infrastructure.
- Existing compare endpoints, simulated-vs-live ACP readiness reporting, and read-only wrapper/ops/visualizer Goose inspection are accepted as baseline and will be extended, not redone.
- This run is additive and focuses on compare UX, lifecycle fixtures, lineage drill-down, ACP compare readiness, and operator-facing read-only exports.

## Planned Work
1. Add explicit multi-version policy-family fixtures and richer certification lineage so compare/export workflows have stable historical artifacts.
2. Add ACP readiness/probe compare support and bounded live-probe report shape without making ACP mandatory.
3. Add first-class Goose compare controls and clearer compare summaries to the visualizer and existing operator surfaces.
4. Validate focused Goose compare, policy-history, ACP, wrapper, and visualizer paths, then run broader regression coverage.

## Audit Notes
- Audit complete. The largest remaining gaps are operator compare usability and explicit lifecycle-fixture coverage, not the underlying compare endpoint baseline.
- Current Goose ACP config still exposes no enabled real provider endpoint in repo config, so live-probe work should stay bounded to report shape, compare support, and graceful readiness behavior unless a real provider appears.

## Implementation Notes
- Added explicit multi-version Goose policy fixtures for `superseded`, `rolled_back`, `held`, and active lineage paths.
- Enriched policy-history, certification, provenance, gateway compare, and adversary compare payloads with stable export artifacts and richer lineage/delta metadata.
- Added ACP provider compare endpoint export artifacts and surfaced that compare path through wrapper and visualizer read-only state.
- Added first-class visualizer Goose compare controls and improved diff cards so operator compare work is not reduced to raw JSON.

## Validation
- `python -m py_compile` on touched Python files: passed.
- `node --check ui/visualizer/app.js`: passed.
- `python -m pytest tests\test_goose_policy_versioning.py -q`: passed after aligning rollout payload assertions with the existing read-only record shape.
- `python -m pytest tests\test_goose_policy_versioning.py tests\test_goose_gateway_coverage.py tests\test_goose_operationalization.py tests\test_nexusnet_visualizer.py -q`: passed.
- `python -m pytest tests\test_goose_assimilation.py tests\test_goose_real_flow_expansion.py tests\test_nexusnet_wrapper_surface.py -q`: passed.
- `python -m pytest -q`: passed (`124 passed, 1 skipped`).

## Failures Fixed
- Corrected policy-version test assumptions from `policy::version` to the actual stable artifact ID format `policy@version`.
- Corrected rollout assertions to inspect lifecycle records instead of assuming `held_versions` and similar fields were bare strings.

## Blockers
- None currently.
