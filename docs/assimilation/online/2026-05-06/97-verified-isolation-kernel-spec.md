# Verified Isolation Kernel Spec

Status: P2 online assimilation target. Research-only until mapped to NexusNet sandbox, appliance, or embedded deployment needs.

## Source Evidence

- seL4 project site: https://sel4.systems/
- seL4 manual docs: https://docs.sel4.systems/projects/sel4/manual.html
- seL4 capability tutorial docs: https://docs.sel4.systems/Tutorials/capabilities
- seL4 Microkit docs: https://docs.sel4.systems/projects/microkit/
- Source status: official seL4 project and documentation pages.

## Finding

seL4 is the rare software artifact whose security boundary is backed by formal proof. The useful NexusNet lesson is not "run everything on seL4"; it is the discipline of small trusted kernels, explicit capabilities, static system structure, and proof-maintained isolation boundaries.

## NexusNet Assimilation Target

Define a verified-isolation profile for future NexusNet appliance, enterprise, or embedded deployments. High-authority components should be decomposed into minimal compartments with explicit communication, capability transfer, and measurable trusted computing base size.

## Proposed NexusNet Components

- `IsolationKernelProfile`: deployment tier, trusted computing base, compartment list, and communication graph.
- `CapabilityDistributionMap`: which component holds which authority and why.
- `CompartmentInterfaceSpec`: typed IPC, allowed data classes, and failure behavior.
- `TcbBudgetReport`: tracks which code is trusted for each high-authority lane.
- `IsolationProofStatus`: records whether isolation is by proof, platform policy, container boundary, or convention.

## Promotion Gates

- Start with architecture mapping; do not require seL4 for normal desktop development.
- Keep every compartment authority explicit and reviewable.
- Measure trusted computing base for release and buyer-facing deployments.
- Test compromised non-critical compartments against critical lane boundaries.
- Treat proof-backed isolation as strongest evidence, not as a replacement for app-level policy.

## Risks

- seL4 integration is specialized and expensive.
- A verified kernel does not prove NexusNet application logic is correct.
- Static partitioning can slow iteration if introduced too early.
