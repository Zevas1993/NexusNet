# Goose Gateway Flow Traceability

## Scope
- Goose-inspired gateway resolutions now persist as first-class NexusNet artifacts instead of living only in transient in-memory logs.
- This remains subordinate to Nexus-owned gateway, approval, sandbox, and adversary-review services.

## Persisted Fields
- `gateway_resolution_id`
- `gateway_execution_id`
- `gateway_report_id`
- `flow_families`
- trigger source
- requested tools
- requested extensions
- effective requested tools after extension governance
- approval and fallback chain
- linked trace IDs
- linked report IDs
- adversary-review report IDs
- extension bundle provenance
- extension policy-set IDs and bundle families
- gateway execution report and markdown summary

## Operator Surfaces
- `GET /ops/brain/gateway`
- `GET /ops/brain/gateway/history`
- `GET /ops/brain/gateway/history/compare`
- `GET /ops/brain/gateway/history/{execution_id}`
- recipe/runbook/subagent execution history endpoints now carry linked gateway execution IDs and reports
- wrapper surface Goose gateway summary
- visualizer runtime posture Goose gateway fields

## Flow Families
- Stored execution artifacts now classify broader Goose-derived flow families such as `gateway-controlled`, `gateway-only`, `recipe-driven`, `runbook-driven`, `subagent-delegation`, `extension-only`, `approval-heavy`, `scheduled`, and `acp-bridged` when those paths are present.
- History summaries expose flow-family counts and latest-by-family records so operators can inspect breadth without mutating governance state.
- Compare views stay read-only and highlight differences in flow families, extension provenance, linked traces/reports, and approval/adversary linkage across two gateway executions.
- Gateway compare responses now also emit stable compare report artifacts with JSON and markdown output for operator export workflows.

## Governance
- gateway-only executions use the shared recipe execution artifact schema with `execution_kind=gateway`
- extension selection remains subordinate to NexusNet gateway and policy logic
- high-risk review remains fail-closed or escalate, never fail-open

## Sources
- Goose docs: https://goose-docs.ai/
- Goose repository: https://github.com/aaif-goose/goose
