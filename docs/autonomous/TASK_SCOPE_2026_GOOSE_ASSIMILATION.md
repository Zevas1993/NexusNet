# Task Scope: 2026 Goose Bounded Assimilation

## Accepted Baseline
- The convergence/live-validation baseline remains accepted infrastructure.
- Retrieval-policy rerank evidence bundles, AITune supported-lane readiness, TriAttention comparative harnessing, and existing wrapper/visualizer read-only inspection surfaces remain accepted infrastructure.
- OpenClaw-style runtime patterns, OpenJarvis productization patterns, and the quarantined OBLITERATUS safe-boundary lane remain accepted infrastructure unless validation proves a mismatch.

## Highest-Value Gaps
- NexusNet lacked a portable YAML recipe/runbook lane for AO playbooks, scheduled task packs, and reusable operator procedures.
- The runtime had no bounded Goose-style subagent delegation lane with explicit tool/extension inheritance and provenance.
- The skill/runtime lane lacked a first-class extension catalog with MCP-aware compatibility summaries.
- There was no optional ACP bridge/provider lane that stayed subordinate to NexusNet governance.
- Security patterns like permission-mode catalogs, sandbox summaries, persistent guardrails, and fail-closed adversary review were not yet explicit read-only operator surfaces.

## This Run Touches
- `runtime/config/goose_lane.yaml`
- `nexusnet/recipes/*`
- `nexusnet/runbooks/*`
- `nexusnet/aos/recipes/*`
- `nexusnet/agents/subagents/*`
- `nexusnet/agents/delegation/*`
- `nexusnet/agents/parallel/*`
- `nexusnet/tools/extensions/*`
- `nexusnet/tools/skills/*`
- `nexusnet/runtime/acp/*`
- `nexusnet/providers/acp/*`
- `nexusnet/tools/permissions/*`
- `nexusnet/tools/adversary_review/*`
- `nexusnet/runtime/sandbox/*`
- `nexusnet/guardrails/persistent_instructions/*`
- wrapper/ops/visualizer read-only inspection surfaces
- Goose assimilation docs, playbook updates, and tests

## Boundaries
- Goose is a source of patterns, not a replacement product identity.
- No second control plane and no second agent identity above Nexus/NexusNet.
- ACP remains optional and subordinate.
- High-risk review paths must fail closed or escalate; fail-open reviewer behavior is explicitly not adopted.
- The visualizer remains read-only and governance remains authoritative.

## Dirty-Tree Risk
- The repo already contains substantial unrelated tracked and untracked drift outside this task.
- Cache/temp directories may still emit permission noise during broader scans or test runs.
