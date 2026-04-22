# Task Scope: Visualizer Expansion

Status: `LOCKED CANON`

Date: `2026-04-12`

## Task Goal
Advance the accepted NexusNet visual subsystem baseline into a richer canonical inspection surface with:

- live route telemetry bound to link and loop animation
- visualizer-side filtering and diff workflows
- replayable recent-state inspection
- stronger safe-mode / thermal / VRAM physiology
- performance-aware rendering and graceful fallback behavior
- deeper inspectability for the core and expert capsules

## Accepted Baseline Preserved
- one canonical visualizer under `/ui/visualizer/`
- the current visual manifest / schema / layout compiler
- the read-only visual-state API projection
- the wrapper link into the visualizer
- the `/ui/3d/` legacy redirect shim
- the authoritative default 19-core expert roster
- the visualizer’s read-only role relative to wrapper / ops control surfaces

## Current Known Visualizer Baseline
- static compiled geometry lives under `ui/visualizer/data/`
- the visualizer is served as repo-local HTML/CSS/JS with layered SVG + Canvas
- route emphasis is still mostly driven by selection and `active_subjects`
- the visualizer surface currently exposes:
  - session input
  - mode toggle pills
  - dream / critique / consequence loop toggles
  - basic selection / evidence / governance cards
- evidence bundle diff and cohort window compare endpoints already exist and should be reused

## Task Boundaries
This task may extend the following areas but should not rework the accepted visualizer baseline:

### Visualizer State / Layout / Overlay Logic
- `nexusnet/visuals/schema.py`
- `nexusnet/visuals/layout.py`
- `nexusnet/visuals/visual_manifest.yaml`
- `nexusnet/visuals/expert_topologies.yaml`
- `nexusnet/visuals/modes.yaml`

### UI Surface / API Integration
- `nexusnet/ui_surface/surface.py`
- `nexus/services.py`
- `nexus/api/app.py`
- `ui/visualizer/index.html`
- `ui/visualizer/app.js`
- `ui/visualizer/styles.css`
- `ui/visualizer/data/*`

### Visualizer Docs / Run Artifacts
- `docs/visuals/nexusnet_visual_spec.md`
- `docs/autonomous/VISUALIZER_EXPANSION_RUN_LOG.md`
- additional visualizer docs if needed

### Tests
- `tests/test_nexusnet_visualizer.py`
- relevant wrapper / promotion regression slices if visualizer state contracts change

## Visible Pre-Existing Unrelated Dirty Paths
These were already dirty or broadly outside this task’s direct scope when the visualizer expansion pass began:

- `README.md`
- `app/core/rag.py`
- `app/main.py`
- `apps/api/main.py`
- `core/orchestrator.py`
- `core/rag/retriever.py`
- `nexusnet/__init__.py`
- `nexusnet/temporal/retriever.py`
- `pyproject.toml`
- `requirements.txt`
- `runtime/config/inference.yaml`
- `runtime/config/planes.yaml`
- `runtime/config/teachers.yaml`
- `temporal/entity_resolution.py`
- `ui/index.html` already had baseline visualizer-link changes
- large untracked subsystem trees already present under `nexus/`, `nexusnet/`, `runtime/`, `tests/`, and `docs/`

## Risk Note
This repo still has substantial unrelated drift. This task keeps a separate run log and end-of-task summary so visualizer telemetry, replay, physiology, and performance changes remain auditable.
