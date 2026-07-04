# Capability RPC Object Fabric Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet internal service and plugin communication.

## Source Evidence

- Cap'n Proto RPC protocol docs: https://capnproto.org/rpc.html
- Cap'n Proto schema docs: https://capnproto.org/language.html
- Fuchsia component capabilities docs: https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities
- Fuchsia realms docs: https://fuchsia.dev/fuchsia-src/concepts/components/v2/realms
- Source status: official Cap'n Proto and Fuchsia documentation.

## Finding

Cap'n Proto RPC treats object references as capabilities and supports promise pipelining for latency-efficient distributed object calls. Fuchsia's component model routes capabilities through component topology. NexusNet can use the pattern to avoid broad singleton APIs and make each service call carry only the authority it needs.

## NexusNet Assimilation Target

Build an internal object-capability RPC fabric for NexusNet services. Agents, tools, memory stores, model runtimes, and UI plugins should communicate through references that both designate the target and confer limited rights.

## Proposed NexusNet Components

- `CapabilityObjectRef`: reference to a service object with scoped methods and lifetime.
- `PromisePipelinedCall`: dependency-aware call graph that can reduce round trips without broadening authority.
- `CapabilityRouteManifest`: declares which component can receive which capability from whom.
- `DisconnectedCapabilityHandler`: safe behavior when a delegated object reference becomes unavailable.
- `OcapRpcTrace`: records capability issuance, transfer, use, and drop/revocation.

## Promotion Gates

- Avoid global service singletons for high-authority APIs.
- Pass object references rather than path strings or broad resource IDs where possible.
- Record capability transfer paths in traces.
- Define disconnect, expiry, and revocation behavior.
- Test confused-deputy and stale-reference scenarios.

## Risks

- Capability RPC requires careful mental models and tooling.
- Debugging distributed object references can be harder than REST-style calls.
- Transport encryption and authentication still need separate implementation.
