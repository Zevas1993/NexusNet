# NexusNet Teacher Schema Versions

Status: `LOCKED CANON`

Date: `2026-04-12`

## Purpose
This document makes teacher hardening persistence explicit and inspectable. The accepted teacher-system baseline now uses manifest-backed schema families so scorecards, disagreement artifacts, evidence bundles, takeover scorecards, trend records, and retirement shadow records no longer depend on implicit JSON shape alone.

## Canon Rule
- startup auto-create remains enabled
- additive JSON compatibility remains the migration policy
- schema discipline strengthens persistence; it does not replace local-first safe startup

## Canonical Files
- config manifest: `runtime/config/schema_versions.yaml`
- loader: `nexusnet/teachers/schema_versions.py`
- lightweight manifest helper: `nexusnet/teachers/migrations.py`
- generated state manifest: `runtime/state/teacher-schema-manifest.json`

## Schema Families

### Teacher Scorecard
- family: `teacher-scorecard`
- version: `1`
- purpose: single-run weighted benchmark record for a benchmark family

### Teacher Disagreement Artifact
- family: `teacher-disagreement-artifact`
- version: `1`
- purpose: structured primary/secondary disagreement plus Critique arbitration and bounded LFM2 metadata

### Teacher Evidence Bundle
- family: `teacher-evidence-bundle`
- version: `1`
- purpose: aggregate bundle linking scorecards, disagreements, lineage, and takeover linkage

### Takeover Scorecard
- family: `takeover-scorecard`
- version: `1`
- purpose: single-run native takeover scoring snapshot

### Retirement Shadow Record
- family: `retirement-shadow-record`
- version: `1`
- purpose: inspectable shadow retirement governance state

### Teacher Trend Scorecard
- family: `teacher-trend-scorecard`
- version: `1`
- purpose: repeated-run benchmark stability and drift summary for a subject/family

### Takeover Trend Report
- family: `takeover-trend-report`
- version: `1`
- purpose: repeated-run native takeover trend gating summary

### Teacher Benchmark Fleet Summary
- family: `teacher-benchmark-fleet-summary`
- version: `1`
- purpose: fleet-level governance summary across benchmark families, routing dimensions, and governance windows

### Teacher Cohort Scorecard
- family: `teacher-cohort-scorecard`
- version: `1`
- purpose: cohort-level readiness record across fleet windows, teacher/native comparisons, and hardware or lineage slices

### Replacement Readiness Report
- family: `replacement-readiness-report`
- version: `1`
- purpose: native replacement governance record combining subject trend, fleet, cohort, rollback, and signoff gates

## Compatibility Policy
- migration policy: `additive-json`
- current reader minimum: `1`
- current writer version: `1`
- compatible readers: `1`
- implication: older records remain readable as long as the additive fields are optional or defaultable

## Persistence Discipline
The following persisted records now carry explicit schema metadata:
- teacher scorecards
- disagreement artifacts
- teacher evidence bundles
- takeover scorecards
- retirement shadow records
- teacher trend scorecards
- takeover trend reports
- teacher benchmark fleet summaries
- teacher cohort scorecards
- replacement readiness reports

Each record now includes:
- `schema_family`
- `schema_version`
- `schema_compatibility`

## Managed Tables
The current manifest-backed helper tracks these persistence tables:
- `teacher_scorecards`
- `teacher_disagreement_artifacts`
- `teacher_evidence_bundles`
- `takeover_scorecards`
- `retirement_shadow_log`
- `teacher_trend_scorecards`
- `takeover_trend_reports`
- `teacher_benchmark_fleet_summaries`
- `teacher_cohort_scorecards`
- `replacement_readiness_reports`

## Migration Notes
- This phase intentionally avoids destructive migrations.
- Existing auto-create startup behavior remains intact.
- The schema manifest adds inspection and compatibility discipline without requiring remote infrastructure or manual migration steps.
