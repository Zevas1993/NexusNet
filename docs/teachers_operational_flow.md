# NexusNet Teacher Operational Flow

Status: `LOCKED CANON`

## Purpose
This document explains how the accepted teacher-system baseline now participates in live NexusNet improvement loops instead of remaining passive metadata.

## Flow

### 1. Registry Layer Selection
- `historical`
  Preserves the original best-ensemble-per-role canon.
- `v2026_live`
  Provides operational primary/secondary routing with Critique Expert arbitration and bounded LFM2 support.

The split is preserved in:

- [runtime/config/teachers.yaml](../runtime/config/teachers.yaml)
- [nexusnet/teachers/teacher_registry_historical.yaml](../nexusnet/teachers/teacher_registry_historical.yaml)
- [nexusnet/teachers/teacher_registry_v2026_live.yaml](../nexusnet/teachers/teacher_registry_v2026_live.yaml)

### 2. Curriculum Execution
- [nexusnet/curriculum/engine.py](../nexusnet/curriculum/engine.py) now consumes the teacher regimens directly.
- If a subject has a teacher regimen, curriculum assessment executes:
  - Stage 1 Domain Professor Distillation
  - Stage 2 Dual-Teacher Contrast
  - Stage 3 Skeptical Examination
  - Stage 4 Dream / Self-Evolution
- Stage records now persist:
  - selected teacher roles
  - disagreement artifacts
  - benchmark family
  - dream/eval lineage

### 3. Foundry and Native Growth
- [nexusnet/distillation/refinery.py](../nexusnet/distillation/refinery.py) aggregates teacher evidence from traces and curriculum records.
- [nexusnet/foundry/benchmarks.py](../nexusnet/foundry/benchmarks.py) now scores:
  - `dependency_ratio`
  - `native_generation`
  - `teacher_disagreement_delta`
  - `takeover_readiness`
  - `takeover_rollbackability`
  - `native_vs_wrapper_slices`
- Native-takeover candidates carry teacher evidence into promotion traceability.

### 4. Promotion Evidence
- [nexusnet/promotions/service.py](../nexusnet/promotions/service.py) now passes candidate traceability into EvalsAO.
- Native-takeover candidates can reference:
  - selected teachers
  - arbitration path
  - benchmark family
  - dream-derived involvement
  - teacher replacement evidence

### 5. EvalsAO
- [nexusnet/evals/service.py](../nexusnet/evals/service.py) now runs teacher-aware scenario checks in addition to recent-trace review.
- Current teacher-aware scenarios:
  - `primary-vs-secondary-disagreement`
  - `critique-arbitration-validation`
  - `lfm2-bounded-lane-enforcement`
  - `native-takeover-vs-teacher-fallback`
  - `dream-derived-trace-contamination`

### 6. Wrapper and Ops Visibility
- [nexusnet/ui_surface/surface.py](../nexusnet/ui_surface/surface.py) exposes:
  - teacher registry layer visibility
  - selected teacher roles
  - arbitration visibility
  - disagreement trace visibility
  - benchmark family visibility
  - promotion/foundry teacher evidence visibility

## Canon Boundaries
- Historical teacher canon is not rewritten by live routing.
- LFM2 remains bounded and non-primary.
- Critique Expert remains the skeptical arbiter.
- Teacher retirement and native takeover remain shadow-gated until evaluator, rollback, and governance evidence all exist.
