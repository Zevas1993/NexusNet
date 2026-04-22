# Goose Real-Flow Traceability

## Scope
- Goose-inspired recipe, runbook, and bounded subagent flows now capture richer real-flow traceability instead of relying only on manual history insertion.
- This remains subordinate to NexusNet governance, gateway policy, approvals, and review lanes.

## What Is Linked
- recipe or runbook ID
- AO association
- trigger source
- linked trace IDs
- linked subagent IDs
- policy path
- approval path
- gateway decision path
- approval and fallback chain
- adversary review report IDs
- produced artifacts

## Real-Flow Coverage
- `POST /ops/brain/recipes/execute` derives gateway and review context automatically.
- `POST /ops/brain/runbooks/execute` derives gateway and review context automatically.
- `POST /ops/brain/subagents/plan` now auto-records execution history and links gateway plus privilege-review provenance.
- Schedule-aware recipe, runbook, and subagent flows can now emit execution-linked scheduled artifacts immediately when `schedule_id` or a `schedule:*` trigger source is present.
- Recipe and runbook history endpoints now support bounded filtering by `schedule_id`, `trigger_source`, and status for operator drill-down.

## Boundaries
- Traceability does not create a second workflow engine.
- High-risk review remains fail-closed or escalate.
- Visualizer and wrapper inspection remain read-only.
