# AgentProof Workflow Verification Spec

Status: P1 online assimilation target. Research-only until code/license are inspected.

## Source Evidence

- AgentProof paper: https://arxiv.org/abs/2603.20356
- Source status: primary paper page.

## Finding

AgentProof statically extracts abstract workflow graphs from agent frameworks and checks topology and temporal policies before deployment. It treats dead ends, unreachable exits, and missing human-gate paths as graph defects rather than only runtime failures.

## NexusNet Assimilation Target

Add static verification to NexusNet graph-like agent plans, skill pipelines, retrieval workflows, and code-change flows before they are executed. Runtime guardrails are still needed, but some defects should be caught before the first tool call.

## Proposed NexusNet Components

- `WorkflowGraphExport`: serializes NexusNet plans into nodes, edges, tools, authorities, and terminal states.
- `StaticPlanChecks`: unreachable exit, dead-end action, missing cancellation, missing human gate, unbounded loop, and forbidden authority path.
- `WitnessTrace`: minimal path showing why a plan violates policy.
- `RuntimeTraceMonitor`: confirms actual execution does not violate the checked plan.

## Promotion Gates

- Start with NexusNet-native plan graphs; do not introduce another framework dependency first.
- Warn on high-risk policy violations before execution.
- Require witness traces in Control Panel, not opaque "failed verification" labels.

## Risks

- Static verification can miss data-dependent risks.
- Overly strict graph policies can block legitimate exploratory work.
- Existing NexusNet workflows may need adapters before graph checks are useful.
