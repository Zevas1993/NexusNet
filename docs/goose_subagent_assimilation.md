# Goose Subagent Assimilation

## Scope
- Goose-inspired subagents are assimilated as temporary bounded workers inside NexusNet.
- They support sequential and parallel planning with restricted tool/extension inheritance.

## What Landed
- Delegation planner keyed off recipe/runbook steps.
- Temporary subagent execution records with parent task, subagent IDs, allowed tools, allowed extensions, and result summaries.
- Read-only API, wrapper, and visualizer visibility for recent subagent runs.

## Operationalization
- Recipe and runbook execution history now records linked subagent IDs so delegated work stays visible in operator review.
- Scheduled recipe artifacts can point back to bounded subagent activity without granting governance mutation rights.
- Bounded subagent planning now resolves against recipe-approved tool inheritance and can surface privilege-confusion review artifacts when a step asks for more privilege than the recipe is allowed to carry.
- Schedule-aware subagent planning now carries explicit trigger source, linked traces, gateway resolution, and approval/fallback context into stored worker artifacts before operator review reads them.
- Goose gateway-only execution history now lives on the same artifact lineage as subagent-linked recipe history, which keeps operator drill-down on one trace surface.
- Delegation plans and stored worker artifacts now also carry requested extension policy-set IDs and bundle-family metadata so governed inheritance is inspectable instead of inferred.
- Governed extension provenance carried through subagent-linked flows now includes policy lifecycle and bundle certification linkage for bounded operator audit.
- Subagent-linked execution history now contributes explicit `subagent-delegation` flow-family classification to the same read-only history and compare surfaces used for other Goose-derived flows.
- Subagent-adjacent Goose compare views now let operators inspect delegated-flow lineage beside gateway, policy, certification, adversary, and ACP comparison without introducing a second review UI.
- When governed extensions participate in delegated flows, the same compare/export path now carries deeper certification lineage and restoration context instead of exposing only the latest certification artifact.
- Large delegated-flow comparisons now benefit from the same grouped filter and collapse controls used by other Goose compare views, which keeps operator review readable without mutating subagent or governance state.

## Boundaries
- Subagents do not mutate global governance state directly.
- They remain subordinate to NexusNet routing, approvals, and review lanes.
- No second agent identity is introduced.

## Sources
- Goose docs: https://goose-docs.ai/
- Goose repository: https://github.com/aaif-goose/goose
