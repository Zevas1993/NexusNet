# Biscuit Datalog Capability Token Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet delegated authority and offline tool grants.

## Source Evidence

- Biscuit specifications: https://doc.biscuitsec.org/reference/specifications
- Biscuit Datalog reference: https://doc.biscuitsec.org/reference/datalog.html
- Biscuit project site: https://www.biscuitsec.org/
- Source status: official Biscuit documentation and specification pages.

## Finding

Biscuit tokens combine bearer-token portability with offline attenuation and Datalog authorization logic. A token holder can add blocks that restrict a token further without needing the issuer online. This is a sharp fit for agent delegation because agents often need narrower, temporary, locally verifiable authority.

## NexusNet Assimilation Target

Use Biscuit-like attenuation for NexusNet agent grants. Instead of broad session roles, each delegated tool run can carry a token that states the subject, resource, action, constraints, expiry, and additional caveats added by intermediate supervisors.

## Proposed NexusNet Components

- `DelegationToken`: signed attenuable token with root authority and caveat chain.
- `DatalogGrantPolicy`: facts and rules for workspace, resource, action, model lane, and risk class.
- `AttenuationBlock`: additional restrictions added by router, policy gate, or human reviewer.
- `OfflineGrantVerifier`: verifies a token without calling a central service.
- `GrantDecisionTrace`: records facts, rules, caveats, and final allow/deny result.

## Promotion Gates

- Token attenuation can only remove authority, never add it.
- Require expiry, audience, resource scope, and action scope on every agent grant.
- Log the exact facts and caveats used for high-authority decisions.
- Reject grants when policy schema versions mismatch.
- Test confused-deputy, replay, and cross-workspace token reuse cases.

## Risks

- Bearer tokens still need careful storage and revocation strategy.
- Datalog policies can become hard to understand without explanation tooling.
- Offline verification must not become offline permission sprawl.
