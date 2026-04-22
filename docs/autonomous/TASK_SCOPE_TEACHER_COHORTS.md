# Task Scope: Teacher Cohorts And Benchmark Fleets

Status: `LOCKED CANON`

Date: `2026-04-12`

## Task Goal
Advance the accepted teacher trend-governance baseline into fleet- and cohort-aware governance for:

- benchmark fleet governance
- cohort-level replacement evidence
- cross-run population analysis
- stronger teacher/native comparison confidence
- richer wrapper and ops inspection

## Accepted Baseline Preserved
- historical/live teacher registry split remains intact
- the 19-core live pair map remains intact
- Critique Expert arbitration remains intact
- bounded LFM2 lane logic remains intact
- schema/version tracking remains intact
- trend scorecards remain intact
- takeover trend gating remains intact
- retirement shadow governance remains intact
- existing wrapper and ops inspection baseline remains intact

## Task Boundaries
This task may extend the following areas but should not rework the accepted baseline:

### Teacher Governance Extensions
- `nexusnet/teachers/fleets.py`
- `nexusnet/teachers/fleet_registry.py`
- `nexusnet/teachers/fleet_windows.py`
- `nexusnet/teachers/cohorts.py`
- `nexusnet/teachers/cohort_scorecards.py`
- `nexusnet/teachers/cohort_thresholds.py`
- `nexusnet/teachers/teacher_benchmark_fleets.yaml`

### Foundry / Promotion / Eval Integration
- `nexusnet/foundry/cohort_takeover.py`
- `nexusnet/foundry/replacement_governance.py`
- `nexusnet/foundry/replacement_cohorts.py`
- `nexusnet/foundry/replacement_readiness.py`
- `nexusnet/promotions/cohort_gating.py`
- `nexusnet/evals/service.py`
- `nexusnet/promotions/service.py`
- `nexusnet/foundry/retirement.py`
- `nexusnet/foundry/teacher_replacement.py`
- `nexusnet/foundry/benchmarks.py`

### Shared Contracts / Persistence / Surfaces
- `nexusnet/schemas.py`
- `nexus/storage.py`
- `nexus/services.py`
- `nexus/api/app.py`
- `nexusnet/ui_surface/surface.py`
- `runtime/config/schema_versions.yaml`
- `docs/teachers_benchmark_report.md`
- `docs/teachers_takeover_hardening.md`
- `docs/teachers_schema_versions.md`
- `docs/teachers_cohort_governance.md`
- `docs/teachers_benchmark_fleets.md`

### Tests
- `tests/test_teacher_trends.py`
- `tests/test_teacher_cohorts.py`
- `tests/test_nexusnet_wrapper_surface.py`
- `tests/test_nexusnet_promotion_loop.py`

## Visible Pre-Existing Unrelated Dirty Paths
These were already dirty or broadly outside this task’s direct scope when the cohort-governance pass began:

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
- `ui/index.html`
- large untracked subsystem trees already present under `nexus/`, `nexusnet/`, `runtime/`, and `tests/`

## Risk Note
This repo still has substantial unrelated drift. This task keeps a separate run log and end-of-task summary so benchmark fleet and cohort governance changes remain auditable.
