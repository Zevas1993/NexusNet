# Goose Scheduled Recipe Artifacts

## Scope
- Schedule-compatible Goose recipes now produce persisted scheduled artifacts instead of summary-only state.
- The lane remains local-first and safe-fallback by default.

## Recorded Fields
- `schedule_id`
- `last_run`
- `next_run`
- `last_status`
- `success_failure_trend`
- `output_artifact_refs`
- `escalation_path`
- `retry_path`
- `linked_trace_ids`
- `linked_report_ids`
- `linked_execution_ids`
- `gateway_resolution_ids`
- `adversary_review_report_ids`
- report payload and markdown refs

## Inspection
- `GET /ops/brain/agents/scheduled`
- `GET /ops/brain/agents/scheduled/history`
- `GET /ops/brain/agents/scheduled/history/{artifact_id}`

## Operational Notes
- History capture is idempotent against the current workflow snapshot so repeated inspection does not churn duplicate artifacts.
- Explicit schedule-triggered recipe, runbook, and bounded subagent executions now persist first-class `scheduled-execution` artifacts instead of waiting for summary-time reconstruction.
- Scheduled history summaries now expose per-workflow latest artifacts so `scheduled-monitor` drill-down does not get hidden by other workflow snapshots.
- Scheduled artifacts stay visible in wrapper and visualizer overlays as read-only operational evidence.
