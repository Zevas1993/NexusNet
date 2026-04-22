# Teacher Hardening Run Log

Status: `LOCKED CANON`

## 2026-04-12

### Start
- Accepted the current teacher-system split and operational flow as the baseline.
- Scoped the task to benchmark hardening, teacher evidence persistence, native takeover scoring, retirement shadow governance, EvalsAO scoring, and wrapper/ops traceability.
- Recorded task boundaries and visible unrelated dirty-tree risk in `TASK_SCOPE_TEACHER_HARDENING.md`.

### Validation Baseline
- Confirmed teacher-focused validation baseline before new hardening edits:
  - `tests/test_teacher_registry.py`
  - `tests/test_teacher_routing.py`
  - `tests/test_teacher_provenance.py`
  - `tests/test_teacher_arbitration.py`
  - `tests/test_teacher_retirement_shadow.py`
- Result at start of hardening pass: `7 passed`

### Operationalization Baseline Already Present
- Curriculum teacher regimens are wired.
- Foundry/native-takeover flow carries basic teacher evidence.
- Promotion candidates can carry teacher evidence in traceability.
- Wrapper/ops surfaces expose teacher evidence fields.

### Remaining Hardening Gap At Start
- benchmark families are not yet first-class teacher artifacts
- threshold sets are not yet versioned and referenced through promotions/foundry/evals
- disagreement artifacts are not yet formalized as first-class bundles
- native takeover is not yet fully scorecard- and threshold-driven
- retirement shadow governance is still lighter than requested
- EvalsAO score outputs are richer than before but still not benchmark-scorecard grade

### Hardening Implementation
- Added first-class benchmark family and threshold catalogs:
  - `nexusnet/teachers/teacher_benchmark_families.yaml`
  - `nexusnet/teachers/teacher_benchmark_thresholds.yaml`
- Added scored teacher runtime helpers:
  - `nexusnet/teachers/benchmarks.py`
  - `nexusnet/teachers/thresholds.py`
  - `nexusnet/teachers/scorecards.py`
- Added disagreement and evidence persistence:
  - `nexusnet/teachers/disagreement.py`
  - `nexusnet/teachers/evidence_bundle.py`
  - `nexusnet/promotions/teacher_evidence.py`
- Added native-takeover hardening:
  - `nexusnet/foundry/takeover_scorecard.py`
  - `nexusnet/foundry/takeover_thresholds.py`
  - `nexusnet/foundry/teacher_replacement.py`
  - `nexusnet/foundry/teacher_delta.py`
- Added retirement shadow governance:
  - `nexusnet/teachers/retirement_governance.py`
  - `nexusnet/teachers/retirement_shadow_log.py`
- Upgraded curriculum, foundry, promotions, EvalsAO, wrapper/ops surfaces, and store persistence to carry thresholded teacher evidence.

### Failures Fixed
- Fixed a circular import between `nexusnet/teachers/disagreement.py` and `nexusnet/teachers/evidence.py`.
- Fixed benchmark-family subject resolution for distillation/native flows whose aggregate subject name is not itself a benchmark-catalog subject.
- Fixed a test mismatch where retirement shadow visibility was being asserted before the foundry/native path had run.

### Validation During This Run
- Teacher hardening suite:
  - `python -m pytest tests\test_teacher_registry.py tests\test_teacher_routing.py tests\test_teacher_provenance.py tests\test_teacher_arbitration.py tests\test_teacher_retirement_shadow.py tests\test_teacher_operationalization.py tests\test_teacher_hardening.py -q`
  - result: `16 passed`

### Remaining Work Before Close-Out
- run broader regression validation
- run full suite
- record any additional regressions or blockers from full-suite validation

### Final Validation
- Broader regression slice:
  - `python -m pytest tests\test_nexusnet_promotion_loop.py tests\test_nexusnet_wrapper_surface.py tests\test_nexusnet_assimilation.py tests\test_nexusnet_brain.py -q`
  - result: `13 passed`
- Full suite:
  - `python -m pytest -q`
  - result: `54 passed, 1 skipped`

### Close-Out Status
- Teacher hardening is now benchmark-scored, threshold-referenced, promotion-linkable, takeover-scorecard-backed, and wrapper-visible.
- No new blocker was encountered in the final regression sweep.

### Trend Governance Extension
- Added schema/version discipline for teacher hardening records:
  - `runtime/config/schema_versions.yaml`
  - `nexusnet/teachers/schema_versions.py`
  - `nexusnet/teachers/migrations.py`
- Added repeated-run trend governance:
  - `nexusnet/teachers/trend_thresholds.py`
  - `nexusnet/teachers/trend_scorecards.py`
  - `nexusnet/teachers/trends.py`
  - `nexusnet/foundry/takeover_trends.py`
  - `nexusnet/promotions/trend_gating.py`
- Upgraded EvalsAO, foundry, promotions, and wrapper/ops surfaces to use and expose trend artifacts.
- Trend-governance validation:
  - `python -m pytest tests\test_teacher_registry.py tests\test_teacher_routing.py tests\test_teacher_provenance.py tests\test_teacher_arbitration.py tests\test_teacher_retirement_shadow.py tests\test_teacher_operationalization.py tests\test_teacher_hardening.py tests\test_teacher_trends.py -q`
  - result: `21 passed`
- Broader regression slice after trend governance:
  - `python -m pytest tests\test_nexusnet_promotion_loop.py tests\test_nexusnet_wrapper_surface.py tests\test_nexusnet_assimilation.py tests\test_nexusnet_brain.py -q`
  - result: `13 passed`
- Full suite after trend governance:
  - `python -m pytest -q`
  - result: `59 passed, 1 skipped`
