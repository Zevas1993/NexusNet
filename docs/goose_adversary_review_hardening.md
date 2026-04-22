# Goose Adversary Review Hardening

## Scope
- Goose-inspired adversary review is expanded only as a bounded NexusNet review lane.
- High-risk failure semantics remain fail-closed or escalate.

## Covered Risk Families
- file-mutation risk
- shell/exec risk
- network-egress risk
- credential/secrets risk
- provider-bridge risk
- ambiguous-tool-binding risk
- multi-step escalation risk
- chained approval-bypass risk
- recipe/subagent privilege-confusion risk
- extension/ACP privilege-inheritance confusion risk

## Inspection
- `POST /ops/brain/security/adversary-review`
- `GET /ops/brain/security/adversary-reviews`
- `GET /ops/brain/security/adversary-reviews/compare`
- `GET /ops/brain/security/adversary-reviews/{review_id}`
- `GET /ops/brain/security/adversary-reviews/{review_id}/audit-export`
- gateway resolutions surface policy path, fallback reason, permission review, and adversary report linkage

## Audit Exports
- each adversary review now emits an operator-facing audit export artifact alongside the standard review report
- exports preserve decision provenance, policy path, requested versus allowed tools/extensions, and failure-policy context
- audit exports stay read-only and do not introduce a second operator workflow
- review compare output stays read-only and highlights risk-family deltas, tool/extension drift, decision changes, and audit-export linkage differences across two reviews

## Boundaries
- No fail-open behavior is allowed on high-risk paths.
- Reviews remain subordinate to SafetyAO, CritiqueAO, EvalsAO, approvals, and rollback discipline.
- ACP or extension inheritance confusion escalates or denies through the same bounded review lane and never silently widens privileges.
