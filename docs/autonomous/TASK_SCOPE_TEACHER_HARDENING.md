# Task Scope: Teacher Hardening

Status: `LOCKED CANON`

Date: `2026-04-12`

## Task Goal
Harden the accepted NexusNet teacher baseline into a benchmark-scored, promotion-grade subsystem for:

- promotion gates
- native takeover readiness
- retirement shadow governance
- EvalsAO scoring
- wrapper and ops traceability

## Baseline Assumptions
- historical/live teacher registry split is accepted
- 19-core live pair map is accepted
- Critique Expert arbitration is accepted
- bounded LFM2 lanes are accepted
- Curriculum Architect remains auxiliary

## Task-Scoped Files Relevant To This Work

### Teacher Core
- `nexusnet/teachers/registry.py`
- `nexusnet/teachers/routing.py`
- `nexusnet/teachers/provenance.py`
- `nexusnet/teachers/retirement.py`
- `nexusnet/teachers/evidence.py`
- `nexusnet/teachers/teacher_registry_historical.yaml`
- `nexusnet/teachers/teacher_registry_v2026_live.yaml`
- `nexusnet/teachers/expert_training_regimens.yaml`
- `nexusnet/teachers/teacher_routing_policy.yaml`

### New Hardening Targets
- `nexusnet/teachers/benchmarks.py`
- `nexusnet/teachers/scorecards.py`
- `nexusnet/teachers/thresholds.py`
- `nexusnet/teachers/disagreement.py`
- `nexusnet/teachers/evidence_bundle.py`
- `nexusnet/teachers/retirement_governance.py`
- `nexusnet/teachers/retirement_shadow_log.py`
- `nexusnet/teachers/teacher_benchmark_families.yaml`
- `nexusnet/teachers/teacher_benchmark_thresholds.yaml`
- `nexusnet/promotions/teacher_evidence.py`
- `nexusnet/foundry/takeover_scorecard.py`
- `nexusnet/foundry/takeover_thresholds.py`
- `nexusnet/foundry/teacher_replacement.py`
- `nexusnet/foundry/teacher_delta.py`

### Integration Surfaces
- `nexusnet/curriculum/engine.py`
- `nexusnet/distillation/refinery.py`
- `nexusnet/evals/service.py`
- `nexusnet/foundry/benchmarks.py`
- `nexusnet/foundry/promotion.py`
- `nexusnet/foundry/provenance.py`
- `nexusnet/foundry/refinery.py`
- `nexusnet/foundry/retirement.py`
- `nexusnet/promotions/service.py`
- `nexusnet/ui_surface/surface.py`
- `nexus/api/app.py`
- `nexus/services.py`
- `nexusnet/schemas.py`

### Tests and Docs
- `tests/test_teacher_registry.py`
- `tests/test_teacher_routing.py`
- `tests/test_teacher_provenance.py`
- `tests/test_teacher_arbitration.py`
- `tests/test_teacher_retirement_shadow.py`
- `tests/test_teacher_operationalization.py`
- `tests/test_nexusnet_promotion_loop.py`
- `tests/test_nexusnet_wrapper_surface.py`
- `tests/test_nexusnet_assimilation.py`
- `docs/teachers_validation_report.md`
- `docs/teachers_operational_flow.md`
- `docs/teachers_benchmark_report.md`
- `docs/teachers_takeover_hardening.md`

## Visible Pre-Existing Unrelated Dirty Paths
These paths were already dirty or broadly outside this task’s direct scope at task start:

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
This repo has substantial pre-existing tracked and untracked drift. This task will keep a task-scoped run log and final change summary so teacher hardening output stays auditable.
