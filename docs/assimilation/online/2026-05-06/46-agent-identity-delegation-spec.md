# Agent Identity Delegation Spec

Status: P1 online assimilation target. Research-only until mapped against NexusNet agent, skill, connector, and MCP boundaries.

## Source Evidence

- SPIFFE documentation: https://spiffe.io/docs/latest/spiffe-about/overview/
- SPIRE documentation: https://spiffe.io/docs/latest/spire-about/spire-concepts/
- OAuth 2.0 Token Exchange RFC 8693: https://www.rfc-editor.org/rfc/rfc8693
- OAuth 2.0 Demonstrating Proof of Possession RFC 9449: https://www.rfc-editor.org/rfc/rfc9449
- OAuth 2.0 Rich Authorization Requests RFC 9396: https://www.rfc-editor.org/rfc/rfc9396
- Source status: official project documentation and IETF RFCs.

## Finding

Agent systems need workload identity and scoped delegation, not ambient credentials. SPIFFE/SPIRE model workload identities and mTLS trust domains, while OAuth token exchange, DPoP, and rich authorization requests provide useful patterns for constrained delegation and proof-of-possession tokens.

## NexusNet Assimilation Target

Give every high-authority NexusNet agent, skill, connector, and protocol bridge a verifiable identity and short-lived delegated authority. A child agent or tool should never inherit broad parent privileges by default.

## Proposed NexusNet Components

- `AgentPrincipal`: stable agent identity, owner, trust domain, role, and revocation status.
- `DelegatedCapabilityToken`: short-lived grant with audience, action, resource, data class, and proof binding.
- `TrustDomainRegistry`: local, workspace, connector, MCP, and remote-agent trust boundaries.
- `DelegationTrace`: who delegated what, to whom, for how long, and under which approval.
- `RevocationGate`: blocks stale, revoked, overbroad, or audience-mismatched grants.

## Promotion Gates

- Require explicit delegation for child agents and third-party tools.
- Scope every grant by time, task, action, resource, and audience.
- Record identity and grant ID in every side-effect trace.
- Prefer local offline identity where product requirements do not need networked trust.

## Risks

- OAuth-style machinery can become complex if introduced before authority surfaces are mapped.
- Identity alone does not prove a workflow is safe.
- Overbroad grants recreate ambient authority under a more formal name.
