# Visualizer Extended Run Log

Status: `LOCKED CANON`

## 2026-04-12

### Start
- Accepted the current NexusNet visual subsystem as the baseline.
- Scoped this run to additive work only: telemetry adapters, stronger diff/replay workflows, performance/fallback hardening, richer operator inspection, and bounded depth enhancement inside the same canonical visualizer.
- Recorded task boundaries and dirty-tree risk in `TASK_SCOPE_VISUALIZER_EXTENDED_RUN.md`.

### Starting Gap Map
- telemetry is still composed directly inside `nexusnet/visuals/layout.py`
- route/link emphasis still relies mostly on recent traces rather than a pluggable telemetry boundary
- diff workflows are still more card/JSON-oriented than scene-oriented
- replay exists but compare-now-vs-then inspection is still shallow
- render tiers exist but are not yet backed by stronger client-aware performance safeguards
- operator panels do not yet expose enough telemetry-source and replay provenance detail
- optional bounded depth inspection does not yet exist inside the canonical visualizer

### Intended Outputs
- pluggable telemetry providers with real-source and simulated fallback behavior
- stronger scene-bound comparison workflows and diff highlights
- deeper replay metadata and temporal inspection
- stronger physiology and performance posture reporting
- richer operator inspection panels
- updated docs and tests

### Iteration 1 - Telemetry Adapter Architecture
- Added `nexusnet/visuals/telemetry.py` and `nexusnet/visuals/performance.py`.
- Split visualizer telemetry into named provider layers:
  - trace-store
  - wrapper-snapshot
  - brain-telemetry-logs
  - simulated-fallback
- Kept the accepted visual-state API intact while extending it with:
  - `telemetry_sources`
  - richer `performance_profile`
  - stronger replay frame provenance
- Preserved graceful degraded behavior when traces, VRAM posture, or hardware signals are sparse.

### Iteration 2 - Scene-Aware Compare And Replay
- Extended compare payloads with `scene_delta` so the visualizer can highlight changed capsules and links directly in the neural scene.
- Added replay anchor comparison and live-vs-frame comparison inside the existing visualizer.
- Upgraded the diff panel from raw JSON-only output into a scene-aware inspection workflow with:
  - left/right artifact identity
  - hot subject deltas
  - hot link deltas
  - raw diff fallback details

### Iteration 3 - Operator Panels And Depth
- Added an operator inspection panel for:
  - telemetry provider status
  - log-channel visibility
  - replay provenance
  - render-tier posture
  - depth-mode status
- Added a bounded depth inspection panel inside the same canonical visualizer.
- Kept SVG + Canvas as the default scene and used a local canvas depth cross-section for selected nodes rather than creating a second renderer surface.

### Iteration 4 - Performance And Physiology Hardening
- Added client-aware frame-time sampling and auto-tier clamping on top of the existing server-side render recommendation.
- Strengthened physiology presentation with visible RAM/VRAM posture slots, reduced-motion handling, and clearer constrained-state render behavior.
- Preserved read-only posture throughout; no mutation or control-plane behavior was introduced.

### Validation
- `python -m py_compile` on updated backend visualizer modules succeeded.
- `node --check ui/visualizer/app.js` succeeded.
- `python -m pytest tests\test_nexusnet_visualizer.py -q` -> `6 passed`
- `python -m pytest tests\test_nexusnet_visualizer.py tests\test_nexusnet_wrapper_surface.py tests\test_nexusnet_promotion_loop.py -q` -> `11 passed`
- `python -m pytest -q` -> `70 passed, 1 skipped`

### Failures Fixed
- Initial patch rollout exceeded the Windows command-length limit, so the implementation was split into smaller patches.
- The first validation attempt tried to syntax-check `app.js` through Python and surfaced non-ASCII separators in new UI strings; switched to `node --check` and converted new separators to ASCII.
- One full-suite run reached the shell timeout while still making progress; rerunning with a longer timeout completed green.
