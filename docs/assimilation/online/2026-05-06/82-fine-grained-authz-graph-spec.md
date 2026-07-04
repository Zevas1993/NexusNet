# Fine Grained Authz Graph Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet principals, resources, and capability grants.

## Source Evidence

- OpenFGA project site: https://openfga.dev/
- OpenFGA introduction docs: https://openfga.dev/docs/fga
- OpenFGA authorization concepts: https://openfga.dev/docs/authorization-concepts
- OpenFGA GitHub repository: https://github.com/openfga/openfga
- Zanzibar paper: https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/
- Source status: official OpenFGA docs/source and primary Google paper page.

## Finding

Relationship-based authorization expresses permissions as relationships between users, groups, services, resources, and parent containers. OpenFGA and Zanzibar-style systems are a stronger fit for agent authority than broad role strings because the permission check can include object-specific relationships.

## NexusNet Assimilation Target

Create a fine-grained authorization graph for NexusNet operators, agents, tools, workspaces, memories, model packs, connectors, and release artifacts. The graph should answer whether a specific agent principal may perform a specific action on a specific object at a specific version.

## Proposed NexusNet Components

- `AuthzTuple`: subject, relation, object, condition, source, and version.
- `ResourceGraph`: workspaces, files, memories, tools, models, connectors, policies, and release artifacts.
- `PermissionCheck`: deny-by-default relation query with traceable explanation.
- `TupleChangeLog`: append-only history of authorization tuple changes.
- `AuthorizationProbeSuite`: regression tests for expected allow/deny cases.

## Promotion Gates

- Default deny when no relationship grants access.
- Version tuple snapshots so historical run traces can be explained.
- Separate human operator rights from agent delegated rights.
- Test privilege escalation, stale membership, deleted resources, and cross-workspace leakage.
- Record permission-check inputs and decisions in high-authority traces.

## Risks

- Relationship graphs can become hard to reason about without visualization and tests.
- Tuple synchronization bugs can deny legitimate work or allow stale access.
- Fine-grained checks add latency unless cached carefully with invalidation.
