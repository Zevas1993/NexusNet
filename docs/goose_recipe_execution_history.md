# Goose Recipe Execution History

## Scope
- Recipe and runbook executions are now persisted as first-class artifacts.
- This lane stays subordinate to NexusNet tracing, approvals, and AO routing.

## Artifact Shape
- `recipe_id` / `execution_kind`
- `ao_association`
- `trigger_source`
- `parameter_set`
- `started_at` / `ended_at`
- `status`
- `linked_trace_ids`
- `linked_subagent_ids`
- `policy_path`
- `approval_path`
- `artifacts_produced`
- `report` payload and markdown refs

## Inspection
- `GET /ops/brain/recipes/history`
- `GET /ops/brain/recipes/history/{execution_id}`
- `POST /ops/brain/recipes/execute`
- `GET /ops/brain/runbooks/history`
- `GET /ops/brain/runbooks/history/{execution_id}`
- `POST /ops/brain/runbooks/execute`
- `POST /ops/brain/subagents/plan` now records bounded execution history automatically for the referenced recipe or runbook

## Boundaries
- Execution history does not bypass governance or evaluator gates.
- Recipes remain AO/runbook definitions inside Nexus/NexusNet, not a second workflow engine.

## Operator Notes
- History endpoints support filtered inspection by `recipe_id` and `status`.
- Summary payloads expose stable report IDs for wrapper/ops/visualizer drill-down.
