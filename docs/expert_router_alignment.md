# Expert Router Alignment

## Purpose
Expert–Router Alignment is the prerequisite seam between the Mixtral router lineage and non-identical expert families. The current implementation is scaffold-first: it validates compatibility, records required projections, and keeps plug-and-play expert swapping possible without pretending all expert shapes already match.

## Current Scaffold
- `AdapterRegistry` holds stable component specs for backbone, router, Devstral, Mini-NexusNet experts, and Cortex.
- `ExpertAdapterService` computes shape signatures and projection plans.
- `ExpertRouterAlignmentService` produces harness-ready compatibility snapshots for router-to-expert pairings.

## Alignment Checks
- Hidden-size compatibility
- Router-dimension compatibility
- Context-window bridge requirement
- LoRA-style bridge recommendation when projection is required
- Shadow-fusion readiness summary across a selected expert set
- Explicit alignment blockers and safe-mode ceilings for native execution
- `max_safe_native_mode` and `alignment_hold_required` reporting for policy-time use
- Runtime-ready expert inventories that can feed the bounded internal-expert harness

## Why It Matters
- Mixtral remains the active MoE backbone lineage.
- Devstral remains an integrated expert instead of an external wrapper.
- Mini-NexusNet per expert stays in scope.
- Future expert-family swaps can be additive instead of requiring a hard reset of the router path.
- The evidence-driven execution policy can now distinguish "needs more evidence" from "evidence is strong enough but alignment still holds native behavior below the proposed mode."
- Alignment ceilings can cap live or challenger intent at bounded shadow execution without introducing a second control plane.

## Files
- `nexusnet/moe/adapter_registry/registry.py`
- `nexusnet/moe/expert_adapter/service.py`
- `nexusnet/moe/router_alignment/service.py`
