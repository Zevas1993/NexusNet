# Visualizer Production Run Log

Status: `LOCKED CANON`

## 2026-04-12

### Start
- Accepted the current NexusNet visual subsystem as the production baseline.
- Scoped this run to additive work only: stronger telemetry provenance, richer in-scene diffing, deeper replay/timeline inspection, better internal structure readability, stronger performance fallback behavior, and test/doc hardening.
- Recorded task boundaries and dirty-tree risk in `TASK_SCOPE_VISUALIZER_PRODUCTION_RUN.md`.

### Starting Gap Map
- provider provenance exists but is still too shallow for operator-grade health inspection
- in-scene diffing is still strongest for node/link classes, not for annotations or cohort-style comparisons
- replay lacks richer temporal history views and more explicit compare-now-vs-then workflows
- capsule/core interiors still need clearer mesh and port cues
- low-power / hidden-tab / reduced-fidelity behavior can be stronger
- docs/tests do not yet describe a more production-grade compare/timeline/inspection surface

### Intended Outputs
- stronger telemetry provider health and provenance
- richer in-scene diff annotations and cohort/fleet comparison support
- replay history/timeline inspection with stable metadata
- deeper capsule/core inspection fidelity
- stronger performance/fallback handling
- updated docs and stronger tests

### Iteration 1: Telemetry Provenance And Scene Delta Hardening
- Extended telemetry provider state so each provider reports inspectable provenance such as provider kind, signal count, latest trace reference, registry context, and source-specific metadata.
- Added provider health summary aggregation in the visualizer telemetry catalog.
- Strengthened evidence scene deltas so teacher/evidence comparisons can light up actual scene links, not only subjects.
- Added cohort/fleet scene-delta support for read-only cohort window comparison.

### Iteration 2: Visualizer In-Scene Diffing, Timeline, And Low-Power Controls
- Added read-only `Low Power Clamp` control to the canonical visualizer.
- Added visualizer-side fleet/cohort comparison controls using the existing teacher cohort comparison surface.
- Added replay timeline browsing with focus and anchor workflows inside the same visualizer.
- Added in-scene annotation layers for hot subjects, hot links, and physiology posture summaries.
- Added richer node mesh and port-anchor rendering so core/capsule interiors read more like neural structures.

### Iteration 3: Performance / Fallback And Inspection Hardening
- Added hidden-tab handling that pauses the heavy animation loop and keeps the visualizer in safe posture until visible again.
- Reduced ambient-field cost in safe/low-power tiers while keeping engineering readability.
- Deepened bounded depth inspection with mesh-link projection and port-anchor cues.
- Expanded operator inspection with provider health summary, source counts, replay metadata, and low-power state.

### Validation
- `node --check ui\\visualizer\\app.js`
- `python -m py_compile nexusnet\\visuals\\telemetry.py nexus\\api\\app.py`
- `python -m pytest tests\\test_nexusnet_visualizer.py -q`
- `python -m pytest tests\\test_nexusnet_visualizer.py tests\\test_nexusnet_wrapper_surface.py tests\\test_nexusnet_promotion_loop.py -q`
- `python -m pytest -q` -> `71 passed, 1 skipped`

### Failures Fixed During The Run
- One visualizer smoke test initially failed because the new replay timeline label only appeared after JavaScript render; fixed by making the static HTML first-load state include the timeline label.
- The first full-suite validation timed out at the shell boundary while tests were still progressing; reran with a longer timeout and completed green.

### Remaining Gaps After This Run
- Real on-device thermal / VRAM / RAM telemetry is still partly degraded and should bind to stronger runtime sources when those channels exist.
- Optional true depth enhancement remains bounded to canvas-depth inspection; repo-local Three.js is still an enhancement path, not a present requirement.
- In-scene diffing is materially stronger now but can still become more visual-first for multi-artifact bundle comparisons.
