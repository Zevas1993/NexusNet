# NexusNet Teacher Takeover Hardening

Status: `LOCKED CANON`

Date: `2026-04-12`

## Purpose
This document records the teacher-evidence hardening applied to native takeover readiness and retirement shadow governance. The goal is to keep wrapper-to-native-growth visible while preventing native takeover from outrunning teacher evidence, repeated-run proof, external evaluation, or rollback discipline.

## Core Rules
- no native takeover is promotable without outperforming the relevant live teacher pair on the relevant benchmark families
- no native takeover is promotable from single-run evidence alone
- no native takeover is promotable from subject-local trend evidence alone
- teacher replacement remains shadow by default
- historical teachers are immutable and cannot enter retirement flow
- non-shadow takeover still requires external evaluation and governance signoff

## New Evidence Path

### Teacher Disagreement
- Primary vs secondary disagreement is now persisted as a first-class artifact.
- Critique arbitration and rationale are stored alongside the disagreement record.
- LFM2 participation records bounded lane and bounded-compliance status.

### Teacher Evidence Bundle
- Curriculum, distillation, and promotion flows can now reference a shared teacher evidence bundle.
- Bundles carry:
  - selected teachers
  - disagreement artifact references
  - scorecard references
  - benchmark family
  - threshold set
  - dream/live lineage
  - teacher confidence

### Takeover Scorecard
- Path: `nexusnet/foundry/takeover_scorecard.py`
- Status: `LOCKED CANON`
- Captures:
  - `dependency_ratio`
  - `native_generation`
  - `takeover_readiness`
  - `teacher_disagreement_delta`
  - `native_vs_primary_delta`
  - `native_vs_secondary_delta`
  - `takeover_rollbackability`
- Scorecards are thresholded through `nexusnet/foundry/takeover_thresholds.py`

### Takeover Trend Report
- Path: `nexusnet/foundry/takeover_trends.py`
- Status: `LOCKED CANON`
- Adds repeated-run governance over:
  - weighted score stability
  - dependency ratio trend
  - native generation trend
  - disagreement delta trend
  - native-vs-primary trend
  - native-vs-secondary trend
  - rollback risk trend
- Current trend threshold set: `takeover-trend-v2026-r1`

### Fleet And Cohort Governance
- Benchmark fleets now give takeover review a broader governance window than one subject’s repeated history.
- Cohort scorecards now measure:
  - stability across fleets
  - outperformance consistency
  - dream/live contamination risk
  - hardware sensitivity
  - rollback risk
- Replacement readiness reports now combine:
  - subject trend
  - fleet gates
  - cohort gates
  - rollback readiness
  - governance and evaluator signoff state

## Retirement Shadow Governance

### Governance Gate
- Path: `nexusnet/teachers/retirement_governance.py`
- Status: `LOCKED CANON`

Retirement shadow decisions require:
- benchmark surpass evidence
- repeated-run trend evidence
- external evaluation pass
- rollback path
- governance signoff

### Inspectable State
- Path: `nexusnet/teachers/retirement_shadow_log.py`
- Status: `LOCKED CANON`

Retirement shadow status is now persisted and surfaced through wrapper/ops payloads and foundry status payloads. This creates an inspectable shadow review trail without deleting live or historical teachers.

## Foundry Integration
- `nexusnet/foundry/benchmarks.py` now produces takeover scorecards
- `nexusnet/foundry/benchmarks.py` now also produces takeover trend reports
- `nexusnet/foundry/promotion.py` gates on takeover scorecards plus repeated-run takeover trend readiness
- `nexusnet/foundry/promotion.py` now also respects fleet/cohort governance and replacement readiness
- `nexusnet/foundry/retirement.py` now routes through teacher replacement advice, replacement readiness, and retirement shadow governance
- `nexusnet/foundry/provenance.py` includes:
  - `teacher_evidence_bundle_id`
  - `threshold_set_id`
  - `takeover_scorecard_id`
  - `takeover_trend_report_id`
  - `fleet_summary_ids`
  - `cohort_scorecard_ids`
  - `replacement_readiness_report_id`

## EvalsAO Integration
Teacher-aware evaluation now checks:
- disagreement resolution quality
- Critique arbitration quality
- LFM2 bounded-lane compliance
- native-takeover vs teacher fallback
- dream-derived contamination

Artifacts emitted for takeover-related evaluations now include:
- `scorecard.json`
- `disagreement_metrics.json`
- `takeover_readiness.json`
- `trend_report.json`
- `cohort_report.json`
- `teacher_eval_report.md`

## Remaining Next-Step Gaps
- score weighting is stronger than provenance-only gating and now trend-, fleet-, and cohort-aware, but it is still based on local persisted evidence rather than large distributed benchmark populations
- wrapper/ops inspection is currently read-only and API-driven
- broader population and cross-project cohort analysis is still a next-step area rather than a fully mature subsystem

## Validation
- teacher hardening suite: `16 passed`
- broader suite and full-suite validation should remain the final acceptance gate for this hardening phase
