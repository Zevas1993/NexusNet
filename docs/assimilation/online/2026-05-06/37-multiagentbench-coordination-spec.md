# MultiAgentBench Coordination Spec

Status: P2 online assimilation target. Research-only until MARBLE code/data licenses and runnable scenarios are inspected.

## Source Evidence

- MultiAgentBench paper: https://arxiv.org/abs/2503.01935
- MARBLE repository: https://github.com/MultiagentBench/MARBLE
- Source status: primary paper page and public code/data repository reference.

## Finding

MultiAgentBench evaluates collaboration and competition across multi-agent scenarios and compares coordination topologies such as star, chain, tree, and graph. Its useful lesson for NexusNet is that multi-agent architecture should be evaluated by coordination quality and milestone progress, not only final task completion.

## NexusNet Assimilation Target

Add a Hive Mind coordination scorecard that measures delegation quality, role clarity, message efficiency, conflict resolution, milestone progress, and failure isolation across agent teams.

## Proposed NexusNet Components

- `CoordinationTopologySpec`: star, chain, tree, graph, supervisor-worker, and debate layouts.
- `AgentRolePassport`: role, authority, data access, allowed tools, escalation path, and termination condition.
- `MilestoneKPITrace`: tracks progress by intermediate commitments rather than final answer only.
- `ConflictResolutionLedger`: records disagreements, evidence used, decision owner, and unresolved risk.
- `TeamRunScorecard`: compares single-agent, multi-agent, and human-in-loop variants.

## Promotion Gates

- Do not assume more agents means better performance.
- Require explicit role and authority boundaries for every spawned agent.
- Compare topology variants on the same task set before promotion.
- Preserve parent-child trace links so failures can be attributed.

## Risks

- Multi-agent benchmarks can reward chatter instead of useful work.
- Competition/deception tasks may not map cleanly to commercial NexusNet workflows.
- Without strict trace discipline, multi-agent runs become harder to debug than single-agent runs.
