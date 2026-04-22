# Goose Policy Lifecycle

## Scope
- Goose-derived policy sets now behave as lifecycle-managed governance artifacts inside NexusNet.
- This extends the existing policy-set baseline without creating a second control plane.

## Lifecycle Fields
- `policy_set_id`
- `version`
- `created_from`
- `supersedes`
- `bundle_family`
- `author`
- `origin`
- `effective_scope`
- `status`
- `created_at`
- `activated_at`
- `retired_at`
- `rollback_reference`
- `linked_evidence_ids`
- `linked_report_ids`
- `status_history`

## Status Model
- `draft`: defined but not yet approved for bounded use.
- `shadow`: bounded rollout state where the policy set is governed and inspectable but not treated as fully active.
- `approved`: accepted for rollout but not yet the active family version.
- `active`: live family policy set used for bounded gateway resolution.
- `rolled_back`: explicitly returned to an older lineage target.
- `superseded`: retained in lineage history but no longer current.

## Read-Only Surfaces
- `GET /ops/brain/extensions/policy-sets`
- `GET /ops/brain/extensions/policy-sets/{policy_set_id}`
- `GET /ops/brain/extensions/policy-history`
- `GET /ops/brain/extensions/policy-history/compare`
- `GET /ops/brain/extensions/policy-history/{policy_set_id}`
- `GET /ops/brain/extensions/policy-rollouts`
- wrapper surface Goose inspection
- visualizer runtime posture

## Rollout and Rollback
- Rollout state is grouped by bundle family so one surface can show active, shadow, approved, rolled-back, and superseded lineage together.
- Rollback references are preserved on the lifecycle artifact rather than inferred from current bundle state.
- ACP-facing policy sets stay provider-gated and can remain in `shadow` even when the governance artifact exists.
- Policy-history compare output is read-only and highlights status deltas, family changes, risk-flag changes, linked evidence/report drift, and rollback-reference changes between two lifecycle artifacts.

## Explicit Multi-Version Fixtures
- Filesystem bridge lineage now explicitly exercises `superseded -> rolled_back -> active` across `goose-mcp-readonly` versions `2026.02`, `2026.03`, and `2026.04`.
- Retrieval-pack lineage now explicitly exercises `draft -> shadow -> approved -> active`, plus retained `rolled_back` (`2026.02`) and `superseded` (`2026.03`) historical versions before the active `2026.04` version.
- ACP provider lineage now explicitly exercises `superseded -> held -> shadow` across `goose-acp-coding-provider` versions `2026.02`, `2026.03`, and `2026.04`.
- These fixtures are now meant to prove historical lineage depth in operator surfaces, not just status-schema support.

## Compare and Export Workflow
- `GET /ops/brain/extensions/policy-history/compare` now emits a stable compare report with:
  - `report_id`
  - `payload_path`
  - `markdown_path`
  - `human_summary`
- Visualizer Goose compare controls can compare policy version A vs B without falling back to raw JSON-only operator work.
- Policy compare exports now group lifecycle delta, risk/evidence delta, and transition context so rolled-back and superseded versions stay readable during operator review.

## Boundaries
- Policy lifecycle is subordinate to NexusNet governance, not a replacement for it.
- Lifecycle state does not grant new privileges by itself.
- Visualizer and wrapper exposure remain read-only.
- ACP lifecycle artifacts remain provider-gated: the governance lane is production-grade, but real ACP probe execution only advances if a non-null ACP provider endpoint enters repo config.
