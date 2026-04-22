# NexusNet Canon Matrix

This file preserves the current constitutional split and migration posture for the runnable codebase.

## Core Split

- `NexusNet` = **LOCKED CANON**
  Brain-first neural wrapper/core, teacher-ingestion layer, memory/dreaming/curriculum substrate, and native-growth path.
- `AOs` = **LOCKED CANON**
  Executive assistant-orchestrator layer coordinating domain workflows, memory, critique, dreaming, safety, runtime, and training flows.
- `Nexus` = **STRONG ACCEPTED DIRECTION**
  Host shell/platform body exposing API, UI, governance, ops, and compatibility surfaces for the NexusNet brain.

## Current Runnable Ownership

- `nexusnet/core` = **LOCKED CANON**
  Canonical wrapped inference path through `NexusBrain.generate()`.
- `nexusnet/teachers` = **LOCKED CANON**
  Teacher registry, assignment routing, attachment state, provenance.
- `nexusnet/aos` = **LOCKED CANON**
  Canonical AO registry and routing plans.
- `nexusnet/memory/planes.py` = **UNRESOLVED CONFLICT**
  Preserves 8-plane canon, 11-plane operational MemoryNode, and 3-plane compatibility projections together.
- `nexusnet/runtime_optimizer` = **LOCKED CANON**
  Device profile, token-budget profile, quantization decision, QES-style candidate surfaces.
- `nexusnet/ui_surface` = **LOCKED CANON**
  Wrapper-surface state used by the UI/API to keep the user-facing shell brain-first.
- `nexusnet/evals` = **STRONG ACCEPTED DIRECTION**
  Placeholder external evaluator workflow and artifact convention.
- `nexus/` = **IMPLEMENTATION BRANCH**
  Host shell carrying API delivery, UI mounting, governance, ops, and compatibility layers without taking ownership away from the brain.

## Migration Notes

- All user-facing task execution must keep flowing through `NexusBrain`.
- `nexus/` may expose routes and shells, but it must not become the intelligence center.
- Teacher selection and AO selection are now visible in traces and wrapper responses.
- Existing legacy memory planes are preserved through alias mapping rather than destructive rewrites.
- Dream, curriculum, and distillation outputs remain shadow/governed paths.
- External evaluator artifacts are intentionally advisory until a fuller black-box suite is implemented.

## Deferred But Preserved

- Federated continuous learning
- BrainGraph / graph intelligence
- Mixtral / Devstral branch-specific scaffolds
- Foundry independence metrics and teacher replacement gates
- Native student checkpoint promotion beyond dataset export
