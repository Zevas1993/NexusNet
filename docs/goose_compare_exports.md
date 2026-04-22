# Goose Compare Exports

## Scope
- Goose compare workflows now emit stable read-only report artifacts for operator export and audit.

## Exported Compare Artifacts
- policy lifecycle compare reports
- extension certification compare reports
- gateway execution compare reports
- adversary audit compare exports
- ACP provider compare reports

## Common Fields
- stable report or export ID
- JSON payload path
- markdown path
- human-readable summary
- evidence and report links when the compared artifacts already carry them
- left/right artifact payloads
- structured diff payload

## Operator Readability
- exported markdown now groups compare output by state, lineage, permissions, risk/remediation, and trace/report context where applicable.
- certification compare exports now surface lineage depth, restored-from artifacts, and restoration state instead of only flat status changes.
- ACP compare exports now surface probe-readiness state, execution policy, blockers, and remediation drift without requiring raw JSON inspection.
- gateway compare exports keep grouped policy, approval/fallback, and trace/artifact sections so large flow comparisons stay readable under one report contract.
- policy and certification compare exports preserve stable report IDs while making superseded, rolled-back, held, and restored lineage transitions readable for operators.

## Notes
- Export artifacts improve operator readability without removing machine-readable payloads.
- Export generation stays read-only and does not mutate gateway, policy, ACP, or adversary governance state.
- ACP compare exports remain valid even with no real ACP provider because the provider-gated/simulated posture shares the same report shape as future bounded live probes.
