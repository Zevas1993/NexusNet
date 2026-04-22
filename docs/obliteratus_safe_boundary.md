# OBLITERATUS Safe Boundary

## Purpose
This lane studies a strictly safe subset of OBLITERATUS-inspired ideas for interpretability and red-team review. It does not assimilate refusal removal, liberation presets, guardrail ablation, or production model surgery.

Primary source checked on 2026-04-13:
- https://github.com/elder-plinius/OBLITERATUS

## Allowed Assimilation
- Structured circuit-localization style analysis.
- Before/after comparison artifacts.
- Compensation and rebound detection after bounded model changes.
- Robustness and stress-test evidence as research artifacts.

## Explicitly Refused
- Refusal removal.
- Guardrail ablation presets.
- Production weight surgery.
- Default-on activation.
- Any path that bypasses SafetyAO, EvalsAO, rollback, or external audit.

## Implementation Notes
- `research/interpretability/guardrail_analysis/` provides quarantined analysis artifacts.
- `research/red_team/refusal_circuit_review/` provides review artifacts that remain non-promotable by default.
- `/ops/brain/research/guardrail-analysis` exposes research-only summaries and bounded analysis runs.
- `/ops/brain/research/refusal-circuit-review` exposes quarantined review reports and evaluator-facing status.

## Governance
- Research-only.
- Quarantine flag required.
- EvalsAO, SafetyAO, and external audit remain required.
- Rollback readiness remains mandatory.
- Promotion is blocked by default.
