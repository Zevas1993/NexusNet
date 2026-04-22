# Goose Recipe Assimilation

## Scope
- Goose-inspired recipes are assimilated as portable YAML AO playbooks and runbooks.
- They remain subordinate to Nexus/NexusNet and do not create a second workflow system.

## What Landed
- Portable YAML recipe schema with parameters, approved tool sets, gateway-policy hints, and schedule compatibility.
- Repo-local recipe roots under `nexusnet/aos/recipes/` and `nexusnet/runbooks/`.
- Read-only API and wrapper/visualizer visibility for recipe/runbook counts and IDs.

## Operationalization
- Recipe/runbook execution history now persists as first-class artifacts with trace IDs, subagent IDs, policy paths, approval paths, and report IDs.
- Scheduled recipe-compatible workflows now expose persisted artifact history and detail views.
- Operator endpoints now support bounded recipe/runbook execution recording for reviewable evidence.
- Bounded subagent planning now auto-records recipe/runbook execution history instead of relying only on manual operator posting.
- Recipe and runbook execution endpoints now derive gateway decisions, approval/fallback chains, and adversary report linkage automatically when real Goose-derived flows are recorded.
- Schedule-aware recipe and runbook execution now persists first-class scheduled artifacts immediately instead of relying only on summary-time scheduled snapshots.
- History endpoints now support bounded filtering by `schedule_id` and `trigger_source` so operator review can isolate specific recurring Goose procedures.
- Direct gateway-only Goose flows now persist execution-history artifacts on the same read-only lineage surface as recipe and runbook flows.
- Recipe and runbook execution artifacts now also store linked gateway execution IDs/reports plus extension policy-set and bundle-family provenance when governed extension lanes are involved.
- Gateway-linked recipe and runbook artifacts now also carry policy lifecycle artifact IDs and bundle certification lineage inside stored extension provenance.
- Recipe and runbook execution history now records explicit Goose flow-family classification so operators can compare recipe-driven, approval-heavy, scheduled, extension-only, delegated, and ACP-bridged paths without inferring them manually.
- Recipe-linked Goose compare flows now surface through first-class visualizer/operator compare controls instead of only endpoint-level inspection.
- Gateway and recipe compare exports now group flow, policy, and trace deltas so large operator comparisons stay readable when multiple governed bundles participate in one execution artifact.
- Large recipe and runbook compare payloads now also inherit explicit Goose diff filter and collapse controls, so operator review can focus on policy, approval, trace, or certification deltas without leaving the read-only compare surface.

## Boundaries
- Recipes do not bypass EvalsAO, SafetyAO, approvals, or rollback discipline.
- Recipes only describe bounded AO/gateway/skill/tool patterns already owned by NexusNet.

## Sources
- Goose docs: https://goose-docs.ai/docs/guides/recipes/
- Goose recipe reference: https://goose-docs.ai/docs/guides/recipes/recipe-reference
- Goose subrecipes: https://goose-docs.ai/docs/guides/recipes/subrecipes
- Goose repository: https://github.com/aaif-goose/goose
