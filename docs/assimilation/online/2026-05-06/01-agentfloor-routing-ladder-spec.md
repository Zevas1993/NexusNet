# AgentFloor Routing Ladder Spec

Status: P0 online assimilation target. Research-only until mapped to NexusNet runtime routing and model certification code.

## Source Evidence

- AgentFloor paper: https://arxiv.org/abs/2605.00334
- Source status: primary paper page. Submitted 2026-05-01.

## Finding

AgentFloor is a deterministic 30-task benchmark organized as a six-tier tool-use capability ladder. Its core claim is practical rather than academic: production agents make many short, structured calls, and smaller open-weight models can cover a large share of those calls while larger models should be reserved for long-horizon planning and constraint tracking.

## NexusNet Assimilation Target

Create a model-routing ladder that scores tasks by routine structure, tool risk, horizon length, constraint persistence, and expected rollback cost. The ladder should route broad-base work to small/open models first, then escalate to larger frontier or premium models only when the task crosses verified difficulty gates.

## Proposed NexusNet Components

- `ModelRouteLadder`: classifies a step as routine tool call, structured extraction, multi-step coordination, or long-horizon planning.
- `RoutingScorecard`: records selected model, rejected alternatives, cost/latency estimate, and capability floor.
- `EscalationPolicy`: promotes to a larger model when the task has unresolved constraints, ambiguity, or repeated failed verification.
- `Control Panel`: shows model tier, reason for selection, cost saved, and escalation triggers.

## Promotion Gates

- Reproduce at least a small local harness slice with NexusNet models or model stubs.
- Add no automatic downgrade for safety-critical or irreversible tool calls.
- Keep operator override visible and logged.
- Treat "small model passed one benchmark" as insufficient for production routing.

## Risks

- Cheap-routing can become false economy if it causes retry storms.
- The benchmark is new; verify harness availability before making hard product claims.
- Long-horizon planning boundaries need NexusNet-specific calibration, not only paper tiers.
