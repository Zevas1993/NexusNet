# Visualizer Expansion Run Log

Status: `LOCKED CANON`

## 2026-04-12

### Start
- Accepted the current NexusNet visual subsystem as the baseline.
- Scoped this pass to telemetry binding, filtering/diff workflows, replay inspection, stronger physiology, and performance-aware rendering.
- Recorded task boundaries and unrelated dirty-tree risk in `TASK_SCOPE_VISUALIZER_EXPANSION.md`.

### Starting Gap
- route emphasis is still mostly selection-driven rather than telemetry-driven
- the visualizer endpoint exposes only a narrow overlay contract
- the visualizer has no internal filter/diff workflow
- there is no replay/scrubber path
- physiology handling is still minimal and VRAM is unbound
- there are no performance tiers or reduced-fidelity safeguards yet

### Intended Outputs
- structured link / loop / evidence / physiology activity in the visualizer state
- visualizer-side filter and diff controls
- bounded replay and route-history inspection
- stronger safe-mode / thermal / VRAM / retry presentation
- render tiers and graceful fallback behavior
- updated docs and stronger visualizer tests

### Iteration 1 — Backend Telemetry Projection
- Extended the visualizer backend projection to emit structured:
  - `link_activity`
  - `loop_activity`
  - `evidence_activity`
  - `physiology_activity`
  - `telemetry_window`
  - `filter_catalog`
  - `diff_catalog`
  - `replay_catalog`
  - `performance_profile`
- Added read-only endpoints for:
  - bounded replay
  - disagreement artifact compare
  - replacement-readiness compare
  - route-window compare
- Reused existing teacher evidence diff and cohort compare paths rather than creating overlapping mutation surfaces.

### Iteration 2 — Visualizer UI Expansion
- Expanded the canonical visualizer UI with:
  - render-tier control
  - visualizer-side filter controls
  - replay scrubber and replay playback toggle
  - read-only compare actions for bundle, disagreement, readiness, and route windows
- Rebound node/link/loop styling to the richer overlay contract so emphasis now follows telemetry intensity instead of selection alone.
- Deepened selection inspection with cluster motif and evidence-reference visibility.
- Strengthened physiology rendering so safe mode, thermal posture, retry posture, and degraded channels remain explicit.

### Iteration 3 — Validation
- Focused validation:
  - `tests/test_nexusnet_visualizer.py`
  - wrapper / promotion visualizer regressions
- Added regression coverage for:
  - richer overlay state contract
  - replay endpoint shape
  - route-window compare endpoint
  - disagreement compare endpoint
  - replacement-readiness compare endpoint
  - UI availability of replay and render-tier controls
- Results:
  - `tests/test_nexusnet_visualizer.py` → `6 passed`
  - `tests/test_nexusnet_wrapper_surface.py tests/test_nexusnet_promotion_loop.py` → `5 passed`
  - combined visualizer + wrapper + promotion slice → `11 passed`
  - full suite → `70 passed, 1 skipped`
- One broader-suite run timed out at the shell timeout boundary before completion; rerunning with a longer timeout completed green with no test failures.
