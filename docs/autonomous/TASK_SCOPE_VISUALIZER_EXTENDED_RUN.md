# Task Scope: Visualizer Extended Run

Status: `LOCKED CANON`

Date: `2026-04-12`

## Task Goal
Advance the accepted NexusNet visualizer baseline into a stronger read-only inspection surface with:

- real-source telemetry adapters with graceful degraded fallback
- richer visual diff and comparison workflows
- deeper replay and time-scrubbing inspection
- stronger safe-mode / thermal / VRAM physiology
- performance-aware rendering tiers and fallback behavior
- deeper operator inspection panels and bounded depth rendering inside the same canonical visualizer

## Accepted Baseline Preserved
- one canonical visualizer under `/ui/visualizer/`
- current visual manifest / schema / layout compiler structure
- read-only `/ops/brain/visualizer/state` projection
- wrapper link into the visualizer
- `/ui/3d/` redirect shim
- authoritative default 19-core expert roster
- telemetry-driven emphasis, replay endpoint, filter controls, and safe-mode physiology baseline already accepted
- visualizer remains read-only and does not become a control plane

## Current Known Baseline
- compiled geometry is checked in under `ui/visualizer/data/`
- visualizer runs as repo-local HTML/CSS/JS with layered SVG + Canvas
- compare endpoints exist for:
  - evidence bundle diffs
  - disagreement diffs
  - replacement readiness diffs
  - route-window compare
  - teacher cohort compare
- replay endpoint exists, but playback and comparison workflows are still shallow
- telemetry is still built mostly inside `nexusnet/visuals/layout.py`
- current UI controls are useful but still too card/JSON-oriented for operator-grade comparison

## This Run Will Touch

### Visualizer Backend / Overlay Logic
- `nexusnet/visuals/layout.py`
- `nexusnet/visuals/schema.py`
- `nexusnet/visuals/telemetry.py`
- `nexusnet/visuals/performance.py`
- `nexusnet/visuals/__init__.py`

### UI / API / Wrapper Integration
- `nexus/api/app.py`
- `nexusnet/ui_surface/surface.py`
- `ui/visualizer/index.html`
- `ui/visualizer/app.js`
- `ui/visualizer/styles.css`

### Tests / Docs / Run Artifacts
- `tests/test_nexusnet_visualizer.py`
- relevant wrapper / promotion visualizer regression slices if contracts move
- `docs/visuals/nexusnet_visual_spec.md`
- `docs/autonomous/VISUALIZER_EXTENDED_RUN_LOG.md`

## Still Missing At Start
- telemetry adapter architecture instead of layout-local telemetry math
- richer scene-aware diff highlighting instead of mostly JSON diff cards
- stronger replay metadata and compare-now-vs-then workflows
- client-aware render tier adaptation and frame-budget safeguards
- deeper inspection panels for telemetry source status, render posture, and replay provenance
- bounded optional depth inspection inside the same visualizer

## Visible Unrelated Dirty-Tree Risk
This repo already contains substantial unrelated tracked and untracked drift outside this task, including:

- top-level docs and runtime config drift
- broad untracked subsystem trees under `nexus/`, `nexusnet/`, `runtime/`, `tests/`, and `docs/`
- pre-existing modifications to wrapper-facing files such as `ui/index.html`
- pre-existing dirty application/runtime files unrelated to the visualizer task

This run keeps a separate log and end summary so the visualizer changes remain auditable despite broader repo drift.
