# Policy As Code Action PDP Spec

Status: P1 online assimilation target. Research-only until NexusNet authority surfaces and existing policy code are mapped.

## Source Evidence

- Open Policy Agent docs: https://www.openpolicyagent.org/docs/latest/
- Open Policy Agent repository: https://github.com/open-policy-agent/opa
- Cedar policy language docs: https://docs.cedarpolicy.com/
- Cedar repository: https://github.com/cedar-policy/cedar
- Source status: official documentation and public repositories.

## Finding

OPA and Cedar show mature patterns for separating policy decisions from application logic. For NexusNet, the key assimilation point is not a specific syntax; it is the policy decision point model where every high-authority action is evaluated against explicit subject, action, resource, context, and evidence.

## NexusNet Assimilation Target

Add a policy-as-code layer around shell, browser, MCP, connector, file, memory export, model routing, and inter-agent delegation. The runtime should ask a central action policy decision point before executing sensitive operations.

## Proposed NexusNet Components

- `ActionPolicyRequest`: subject, action, resource, data class, tool manifest, run ID, and operator grant.
- `PolicyDecisionRecord`: allow, deny, require approval, require sandbox, or require redaction, with policy version and reason.
- `CapabilityPolicyBundle`: versioned rules for each lane and authority class.
- `PolicySimulationRunner`: tests policy changes against saved traces before release.
- `PolicyAuditSurface`: Control Panel view for denied actions, approval prompts, and policy drift.

## Promotion Gates

- No high-authority action should bypass the policy decision point.
- Policy versions must be included in traces and eval reports.
- Policy changes need regression tests over real NexusNet action traces.
- Default-deny unknown tools, unknown agents, and unknown resource classes.

## Risks

- Policy engines can create false confidence if bypass paths remain.
- Rules can become unreadable unless grouped by lane and authority level.
- Policy-as-code must not replace human review for ambiguous or high-stakes actions.
