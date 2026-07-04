# Five Eyes Agentic Security Spec

Status: P0 online assimilation target. Research-only until NexusNet authority surfaces are mapped against the guidance.

## Source Evidence

- Cyber.gov.au guidance page: https://www.cyber.gov.au/business-government/secure-design/artificial-intelligence/careful-adoption-of-agentic-ai-services
- NSA press release: https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4475134/nsa-joins-the-asds-acsc-and-others-to-release-guidance-on-agentic-artificial-in/
- Joint guidance PDF mirror: https://media.defense.gov/2026/Apr/30/2003922823/-1/-1/0/CAREFUL%20ADOPTION%20OF%20AGENTIC%20AI%20SERVICES_FINAL.PDF
- NIST AI RMF page: https://www.nist.gov/itl/ai-risk-management-framework
- Source status: official government guidance and NIST risk-management reference.

## Finding

The late April and early May 2026 joint guidance treats agentic AI as a cybersecurity deployment problem. Its strongest NexusNet implications are distinct agent identity, least privilege, mutual authentication, trusted registries, defense in depth, policy decision points, auditability, resilience, reversibility, and risk containment over raw productivity.

## NexusNet Assimilation Target

Promote an Agentic Security Baseline before any new high-authority NexusNet lane. Browser, shell, MCP, file, connector, memory-export, enterprise, and multi-agent behaviors should all require identity, scoped privileges, approval policy, traceability, revocation, and containment.

## Proposed NexusNet Components

- `AgentIdentityRegistry`: unique agent principal, key or certificate binding, owner, role, allowed tools, and revocation status.
- `ActionPolicyDecisionPoint`: central approval decision for each high-authority action.
- `AgentLeastPrivilegeGrant`: time-bound, task-bound, data-bound, and tool-bound authority record.
- `ContainmentProfile`: sandbox, network, filesystem, credential, and rollback controls per lane.
- `SecurityBaselineChecklist`: maps each NexusNet lane to identity, auth, least privilege, monitoring, reversal, and incident response.

## Promotion Gates

- Deny access for unregistered agents, stale keys, or tools outside an approved grant.
- Require explicit approval for sensitive data, external send, shell, file mutation, connector mutation, and inter-agent delegation.
- Preserve audit traces and support post-incident revocation.
- Prefer lower-risk automation or read-only mode when agentic autonomy is not necessary.

## Risks

- Government guidance is broad; NexusNet still needs concrete implementation mapping.
- Identity and policy systems can become bypassable if high-authority shortcuts remain.
- Overly broad grants recreate the same risk under a more formal label.
