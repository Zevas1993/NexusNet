# Object Capability Delegation Spec

Status: P1 online assimilation target. Research-only until compared with NexusNet's identity, policy, and tool-manifest design.

## Source Evidence

- UCAN specification repository: https://github.com/ucan-wg/spec
- UCAN delegation spec: https://ucan.xyz/delegation/
- Web3.Storage UCAN docs: https://docs-beta.web3.storage/concepts/ucan/
- Macaroons paper: https://research.google.com/pubs/archive/41892.pdf
- Source status: public specifications, official docs, and primary paper.

## Finding

Object-capability systems focus on authority, not broad identity. UCAN and macaroons show how capabilities can be delegated, attenuated, chained, time-limited, caveated, and validated locally. This is a sharper primitive for agents than role-based permission alone.

## NexusNet Assimilation Target

Represent high-authority NexusNet actions as attenuable capabilities. Agents, skills, and tools should receive the narrowest capability required for a task, with delegation chains and revocation evidence.

## Proposed NexusNet Components

- `CapabilityGrant`: subject, resource URI, action, caveats, audience, expiry, issuer, and proof chain.
- `CapabilityInvocation`: signed or locally bound request that exercises one grant once.
- `DelegationChainVerifier`: confirms every child grant is narrower than its parent.
- `ReplayProtectionStore`: tracks invocation identifiers until expiry.
- `CapabilityDiffViewer`: shows exactly what authority changed between grants.

## Promotion Gates

- Default to narrow resource URIs and short expiry.
- Require proof chains for delegated agent authority.
- Block broad wildcard grants unless explicitly approved and time-limited.
- Record capability ID in every side-effect trace.

## Risks

- Capability systems can be hard to reason about without good visualization.
- Bearer-style credentials require careful storage and replay protection.
- Object-capability patterns must integrate with existing OS, connector, and MCP permissions.
