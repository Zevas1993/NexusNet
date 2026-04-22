# NexusNet Teacher Cohort Governance

Status: `LOCKED CANON`

Date: `2026-04-12`

## Purpose
Cohort governance lifts teacher/native evidence from subject-local trend scores to cohort-level readiness. A native candidate now has to look reliable across benchmark fleets and governance windows, not just across one repeated benchmark thread.

## Canonical Files
- cohort analyzer: `nexusnet/teachers/cohorts.py`
- cohort scorecards: `nexusnet/teachers/cohort_scorecards.py`
- cohort thresholds: `nexusnet/teachers/cohort_thresholds.py`
- promotion gate: `nexusnet/promotions/cohort_gating.py`
- foundry cohort bridge: `nexusnet/foundry/cohort_takeover.py`
- replacement readiness: `nexusnet/foundry/replacement_readiness.py`
- replacement cohorts: `nexusnet/foundry/replacement_cohorts.py`

## What A Cohort Can Represent
- all runs for one expert across a fleet
- all runs for one teacher pair across multiple subjects
- all runs under one hardware class
- all runs under one budget class
- dream-derived vs live-derived runs
- native-vs-teacher comparisons for one takeover candidate

## Cohort Signals
Current cohort scorecards track:
- stability score
- variance
- disagreement trend
- outperformance consistency
- regression spikes
- rollback risk
- dream contamination risk
- hardware sensitivity

## Governance Rule
Teacher replacement remains shadow by default. A candidate cannot move beyond shadow replacement until:
- subject-level trend gates pass
- fleet-level gates pass
- cohort-level gates pass
- external evaluation passes
- rollback path exists
- governance/promotion signoff exists

## Surface Visibility
Wrapper and ops surfaces now expose:
- fleet summaries
- cohort scorecards
- replacement readiness reports
- evidence diff controls
- window comparison controls

## Canon Rule
Cohort governance strengthens promotion-grade teacher evidence. It does not rewrite the accepted registry split or renumber the 19-core roster.
