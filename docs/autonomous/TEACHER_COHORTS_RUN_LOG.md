# Teacher Cohorts Run Log

Status: `LOCKED CANON`

## 2026-04-12

### Start
- Accepted the current teacher trend-governance phase as the baseline.
- Scoped this pass to benchmark fleets, cohort-level evidence, stronger native replacement readiness, richer EvalsAO artifacts, and read-only operator inspection.
- Recorded task boundaries and visible unrelated dirty-tree risk in `TASK_SCOPE_TEACHER_COHORTS.md`.

### Starting Gap
- teacher governance is still mostly subject-local across repeated runs
- promotions and native takeover do not yet require fleet/cohort evidence
- wrapper and ops surfaces expose trend artifacts but not fleet/cohort-level inspection
- EvalsAO is trend-aware but not yet fleet/cohort-aware

### Intended Outputs
- benchmark fleet registry and governance windows
- cohort scorecards and threshold gating
- replacement readiness reports using subject, fleet, and cohort evidence together
- EvalsAO cohort reports
- wrapper and ops visibility for fleet/cohort artifacts, IDs, threshold versions, and references

### Validation Plan
- run a new teacher cohort test suite first
- rerun teacher-focused suites
- rerun broader promotion/wrapper regression slices
- rerun the full suite before close-out

### Implementation
- Added benchmark fleet catalog and governance windows:
  - `nexusnet/teachers/teacher_benchmark_fleets.yaml`
  - `nexusnet/teachers/fleet_registry.py`
  - `nexusnet/teachers/fleet_windows.py`
  - `nexusnet/teachers/fleets.py`
- Added cohort governance and thresholds:
  - `nexusnet/teachers/cohort_thresholds.py`
  - `nexusnet/teachers/cohort_scorecards.py`
  - `nexusnet/teachers/cohorts.py`
- Added promotion and foundry cohort integration:
  - `nexusnet/promotions/cohort_gating.py`
  - `nexusnet/foundry/cohort_takeover.py`
  - `nexusnet/foundry/replacement_cohorts.py`
  - `nexusnet/foundry/replacement_readiness.py`
  - `nexusnet/foundry/replacement_governance.py`
- Extended schema, persistence, services, API, and wrapper surfaces to carry fleet summaries, cohort scorecards, and replacement readiness reports.

### Failures Fixed
- Adjusted the seeded disagreement test fixtures so stable histories no longer trigger max-severity disagreement artifacts by construction.
- Corrected cohort contamination handling so the cohort gate interprets high contamination-sensitivity scores as lower risk rather than higher risk.
- Extended wrapper visibility tests to create a real replacement-readiness artifact before asserting it is visible.

### Validation
- New cohort suite:
  - `python -m pytest tests\test_teacher_cohorts.py -q`
  - result: `5 passed`
- Teacher/promotion/wrapper regression slice:
  - `python -m pytest tests\test_teacher_registry.py tests\test_teacher_routing.py tests\test_teacher_provenance.py tests\test_teacher_arbitration.py tests\test_teacher_retirement_shadow.py tests\test_teacher_operationalization.py tests\test_teacher_hardening.py tests\test_teacher_trends.py tests\test_teacher_cohorts.py tests\test_nexusnet_promotion_loop.py tests\test_nexusnet_wrapper_surface.py -q`
  - result: `31 passed`
- Full suite:
  - `python -m pytest -q`
  - result: `64 passed, 1 skipped`

### Close-Out Status
- Benchmark fleets and cohort governance are now first-class persisted teacher artifacts.
- Promotions, foundry/native takeover, EvalsAO, and wrapper/ops inspection now consume fleet/cohort evidence instead of subject-local trend history alone.
- Historical/live teacher canon remains unchanged.
