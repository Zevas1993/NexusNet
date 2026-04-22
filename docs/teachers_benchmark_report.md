# NexusNet Teacher Benchmark Report

Status: `LOCKED CANON`

Date: `2026-04-12`

## Scope
This report covers the benchmark-scored hardening of the accepted teacher-system baseline and its evolution into trend-aware and cohort-aware governance. It does not replace the historical/live registry split. It operationalizes the live teacher layer with machine-readable benchmark families, versioned threshold sets, scorecards, disagreement artifacts, evidence bundles, takeover-linked scoring, repeated-run trend gates, benchmark fleets, and cohort scorecards.

## Canon-Preserved Baseline
- historical teacher canon remains preserved in `nexusnet/teachers/teacher_registry_historical.yaml`
- live `v2026` teacher routing remains preserved in `nexusnet/teachers/teacher_registry_v2026_live.yaml`
- Critique Expert remains the arbitration layer
- bounded LFM2 lanes remain bounded
- Curriculum Architect remains auxiliary and does not renumber the core 19

## First-Class Benchmark Artifacts

### Benchmark Family Catalog
- Path: `nexusnet/teachers/teacher_benchmark_families.yaml`
- Status: `LOCKED CANON`
- Purpose: bind each expert capsule to concrete benchmark families aligned with its regimen stages

### Threshold Set Catalog
- Path: `nexusnet/teachers/teacher_benchmark_thresholds.yaml`
- Status: `LOCKED CANON`
- Purpose: versioned threshold rules referenceable from curriculum, promotions, foundry, and EvalsAO

### Runtime Access Layers
- `nexusnet/teachers/benchmarks.py`
- `nexusnet/teachers/thresholds.py`
- `nexusnet/teachers/scorecards.py`
- `nexusnet/teachers/disagreement.py`
- `nexusnet/teachers/evidence_bundle.py`
- `nexusnet/teachers/trend_thresholds.py`
- `nexusnet/teachers/trend_scorecards.py`
- `nexusnet/teachers/trends.py`
- `nexusnet/teachers/fleet_registry.py`
- `nexusnet/teachers/fleet_windows.py`
- `nexusnet/teachers/fleets.py`
- `nexusnet/teachers/cohort_thresholds.py`
- `nexusnet/teachers/cohort_scorecards.py`
- `nexusnet/teachers/cohorts.py`

### Schema Discipline
- `runtime/config/schema_versions.yaml`
- `nexusnet/teachers/schema_versions.py`
- `nexusnet/teachers/migrations.py`
- `runtime/state/teacher-schema-manifest.json`

## Scoring Dimensions
The current teacher threshold set `teacher-v2026-r1` evaluates a subset of the following dimensions depending on subject and benchmark family:

- correctness
- groundedness / provenance
- safety
- tool-discipline
- structured-output conformance
- efficiency / latency budget
- disagreement severity
- dream contamination sensitivity
- native-vs-teacher delta
- rollbackability

## Thresholding Model
- Default threshold set: `teacher-v2026-r1`
- Current threshold version: `1`
- Thresholds are resolved by:
  - subject
  - benchmark family
  - threshold set id
- Subject and family overrides can strengthen or relax dimension-specific thresholds while preserving a shared threshold-set identity for promotion and foundry references.

## Trend-Aware Gating
- Teacher benchmark gating is no longer single-run only.
- Repeated runs now feed `teacher-trend-scorecard` artifacts.
- Trend gates can require:
  - minimum valid runs
  - acceptable variance
  - no recent regression spike
  - acceptable disagreement trend
  - stable weighted-score behavior over time

Current trend threshold set:
- `teacher-trend-v2026-r1`
- version: `1`
- minimum valid runs: `3`

## Fleet And Cohort Governance
- Benchmark fleets are now first-class machine-readable teacher artifacts.
- Cohort scorecards now aggregate repeated evidence across fleet windows instead of relying on one subject’s local history alone.
- Promotions and native takeover flows can now reject candidates when:
  - fleet coverage is insufficient
  - cohort stability is weak
  - cohort variance is too high
  - hardware sensitivity is too large
  - dream/live contamination risk is too unstable

Current cohort threshold set:
- `teacher-cohort-v2026-r1`
- version: `1`
- default minimum valid runs: `5`

## Operational Flow

### Curriculum
- Curriculum stages now score teacher-backed flows directly.
- Stage 2 persists primary-vs-secondary disagreement artifacts.
- Stage 3 persists Critique arbitration-backed scorecards.
- Stage 4 carries dream-derived lineage into the teacher evidence bundle.

### Promotions
- Promotion candidates can now carry:
  - `teacher_evidence_bundle_id`
  - `threshold_set_id`
  - takeover scorecard references where applicable
- Promotion evaluation consumes teacher-aware scorecards instead of provenance-only teacher metadata.
- Promotion evaluation now also emits and enforces trend reports when teacher evidence is involved.
- Promotion evaluation now also emits and enforces `cohort_report.json` artifacts when teacher evidence is involved.

### Foundry / Native Growth
- Foundry now computes a takeover scorecard using teacher deltas and threshold gates.
- Foundry now also computes repeated-run takeover trend reports.
- Foundry now also computes fleet summaries, cohort scorecards, and replacement readiness reports.
- Teacher evidence bundles, takeover scorecards, takeover trend reports, fleet summaries, and cohort scorecards are linked into native-takeover candidate traceability.

### EvalsAO
- EvalsAO now emits richer teacher-aware artifacts:
- `scorecard.json`
- `disagreement_metrics.json`
- `takeover_readiness.json`
- `trend_report.json`
- `cohort_report.json`
- `teacher_eval_report.md`

## Repo Audit: Remaining Passive-Only Teacher Metadata
The following teacher-adjacent areas still remain lighter than the new hardening path and should be considered next-step work rather than completed benchmark governance:

- `nexusnet/teachers/capability_cards.py`
  Capability descriptions exist, but they are not yet benchmark-scored selection inputs.
- `nexusnet/teachers/ensemble.py`
  Ensemble helpers preserve canon and support best-ensemble semantics, but do not yet score ensemble selection against benchmark deltas directly.
- `nexusnet/teachers/catalog.py`
  This remains a compatibility shim and not the promotion-grade source of truth.
- wrapper UI controls
  Wrapper and ops surfaces now expose fleet/cohort fields and read-only compare controls, but they are still operational inspection tools rather than full governance consoles.
- benchmark fleets across broader distributed history
  Fleet/cohort governance now exists, but it still uses local persisted evidence rather than a federated benchmark warehouse.

## Validation
- `tests/test_teacher_registry.py`
- `tests/test_teacher_routing.py`
- `tests/test_teacher_provenance.py`
- `tests/test_teacher_arbitration.py`
- `tests/test_teacher_retirement_shadow.py`
- `tests/test_teacher_operationalization.py`
- `tests/test_teacher_hardening.py`
- `tests/test_teacher_trends.py`
- `tests/test_teacher_cohorts.py`

Result after trend-governance extension:
- teacher-focused suite: see validation report for the current combined count

## Migration Notes
- Historical canon remains immutable and separate.
- Live v2026 operations now use benchmark/threshold references without rewriting the historical layer.
- Scorecards, trend scorecards, and evidence bundles upgrade the teacher system from metadata-only to thresholded, trend-aware, promotion-grade evidence without collapsing NexusNet into its teachers.
