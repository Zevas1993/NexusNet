# Mixtral Devstral Fusion

## Canonical Branch
- Mixtral is preserved as the MoE backbone.
- The router remains explicit.
- Devstral is preserved as an integrated expert.
- Cortex is modeled as a peer to the router.
- Neural Bus is the communication substrate.
- Mini-NexusNet experts remain part of the implementation direction.

## Current Executable Scaffold
`MoEFusionScaffoldService` builds the bounded fusion plan used by the brain summary and generation trace:
- backbone selection
- router identity
- selected expert inventory for the current task
- Devstral integration flag
- Mini-NexusNet expert inventory
- Cortex peer snapshot
- Neural Bus snapshot
- Expert–Router Alignment snapshot
- native execution ceiling derived from alignment
- hardware-note gating for safe-mode hosts

## Harnesses
- `MixtralDevstralHarness` produces the branch-lineage definition and bounded selected-expert set.
- The selected-expert set now feeds the evidence-driven execution policy and bounded internal-expert runtime.
- The fusion scaffold now exposes a native execution ceiling and alignment-hold flag so the brain can cap behavior before model attachment.
- The active expert set also feeds bounded native candidate drafting and teacher-comparison behavior inside the real brain path.
- The harness is intentionally executable on this host without claiming full heavy-weight training support.
- Safe-mode hardware keeps the lane scaffold-only rather than silently pretending full fusion execution is available.

## Files
- `nexusnet/moe/fusion/service.py`
- `nexusnet/moe/mixtral_devstral/harness.py`
- `nexusnet/moe/cortex/service.py`
- `nexusnet/moe/neural_bus/bus.py`
