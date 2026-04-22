# Task Scope: Visualizer Production Run

Status: `LOCKED CANON`

Date: `2026-04-12`

## Task Goal
Advance the accepted NexusNet visualizer baseline into a more production-grade read-only inspection surface with:

- stronger real-source telemetry integration and provider health
- richer in-scene diffing and compare workflows
- deeper replay and time inspection
- clearer capsule/core inspection fidelity
- stronger performance and fallback behavior
- richer operator inspection panels
- updated docs, tests, and scoped run artifacts

## Accepted Baseline Preserved
- one canonical visualizer under `/ui/visualizer/`
- current visual manifest / schema / layout compiler structure
- current telemetry / performance adapter baseline
- read-only visual-state API projection
- wrapper link into the visualizer
- replay endpoint
- current filter / diff controls
- current safe-mode / thermal / VRAM physiology baseline
- authoritative default 19-core expert roster
- visualizer remains read-only and does not become a control plane

## Current Production Baseline
- the visualizer already has:
  - telemetry adapters
  - render-tier guidance
  - filter controls
  - compare helpers
  - replay scrubber
  - bounded depth inspection
  - safe-mode physiology overlays
- compare payloads already support scene delta hints for some artifact types
- operator panels already expose provider state at a coarse level

## Remaining Gaps At Start
- in-scene diffing is still not rich enough for cohort/fleet/time comparisons
- provider provenance is present but still too shallow for operator-grade source health inspection
- replay lacks stronger timeline/history views and compare-now-vs-then readability
- capsule/core interiors still need more legible structural mesh and port/cluster cues
- low-power / hidden-tab / render-fallback behavior can be stronger
- docs and tests do not yet reflect a more production-grade compare/timeline/inspection surface

## Files This Task May Touch

### Visualizer Backend / Telemetry / Performance
- `nexusnet/visuals/telemetry.py`
- `nexusnet/visuals/performance.py`
- `nexusnet/visuals/layout.py`
- `nexusnet/visuals/schema.py`
- `nexusnet/visuals/__init__.py`

### API / Wrapper Integration
- `nexus/api/app.py`
- `nexusnet/ui_surface/surface.py`

### Canonical Visualizer UI
- `ui/visualizer/index.html`
- `ui/visualizer/app.js`
- `ui/visualizer/styles.css`

### Tests / Docs / Run Artifacts
- `tests/test_nexusnet_visualizer.py`
- `docs/visuals/nexusnet_visual_spec.md`
- `docs/autonomous/VISUALIZER_PRODUCTION_RUN_LOG.md`

## Files Touched In This Run
- `nexusnet/visuals/telemetry.py`
- `nexus/api/app.py`
- `ui/visualizer/index.html`
- `ui/visualizer/app.js`
- `ui/visualizer/styles.css`
- `tests/test_nexusnet_visualizer.py`
- `docs/visuals/nexusnet_visual_spec.md`
- `docs/autonomous/VISUALIZER_PRODUCTION_RUN_LOG.md`

## Visible Unrelated Dirty-Tree Risk
This repo already contains substantial unrelated tracked and untracked drift outside this task, including:

- broad pre-existing changes to runtime, docs, tests, and application surfaces
- large untracked subsystem trees under `nexus/`, `nexusnet/`, `runtime/`, `docs/`, `tests/`, and `ui/`
- wrapper-facing files already touched by prior accepted work

This task keeps a dedicated run log and scoped summary so the production visualizer work remains auditable despite broader repo drift.
