# Task Scope: 2026 Core NexusNet Pivot

## Accepted Baseline
- Goose closeout work is accepted as complete and bounded baseline infrastructure
- governance, evals, teacher routing, visualizer, and read-only operator surfaces remain accepted
- bounded Goose/OpenClaw/AITune/TriAttention lanes remain subordinate and are not being redone here

## Current State At Start
- `NexusBrain` already exists and handles retrieval, compression, generation, critique, and trace storage.
- `attach_base_model()` exists only as a method on the brain and is not yet a first-class canonical ingestion seam.
- runtime/QES profiling exists, but it still behaves more like side infrastructure than an explicit brain-execution input.
- multi-plane memory already exists through `MemoryPlaneRegistry`, but root-level `config/planes.yaml` is missing and the MemoryNode abstraction is not operationalized.
- there is no `nexusnet/moe` package yet, so Mixtral/Devstral/NexusNet fusion and Expert-Router Alignment are still missing as executable scaffolding.

## This Task Touches
- canonical brain-first execution seam and model-ingestion path
- attach-base-model traceability and execution metadata
- hardware-aware runtime/QES planning in the actual core path
- config-driven MemoryNode operation and plane-path resolution
- initial MoE fusion, neural bus, cortex-peer, and Expert-Router Alignment scaffolding
- focused docs, tests, and core run logging

## Highest-Value Core Gaps At Start
- the brain path does not yet have a canonical attach seam shared across startup, execution, and traceability
- startup profiling happens, but hardware/QES planning is not first-class execution metadata
- the repo has strong periphery scaffolding but no executable `nexusnet/moe` implementation branch
- MemoryNode remains implicit rather than an operational service with root-config ownership and compatibility views
- core operator inspection can show runtime summaries, but not a unified brain-first execution summary

## Canon Preserved
- NexusNet remains brain-first and starts before attached models
- Dream Training / Recursive Neural Dreaming remains mandatory
- Federated Continuous Learning remains mandatory
- AOs remain open-ended Assistant Orchestrators
- historical/live teacher split remains intact
- Critique Expert remains arbiter
- Mixtral + Devstral remains a serious implementation lineage
- Mini-NexusNet per expert, Cortex, and Neural Bus remain in-scope
- Multi-Plane MemoryNode remains config-driven and not hardcoded
- the visualizer remains read-only
- Goose remains closed except for real ACP-provider-triggered work

## Known Unrelated Dirty-Tree Risk
- The repo still has substantial pre-existing tracked and untracked drift outside this run.
- Long-path and permission-denied noise remains visible under runtime test fixtures and temp directories.

## Planned High-Leverage Iterations
1. Make `attach_base_model()` a real canonical seam and thread execution-trace metadata through the brain path.
2. Feed the brain path with hardware-aware QES planning and MemoryNode context instead of leaving those systems as side summaries.
3. Create an executable `nexusnet/moe` scaffold for router alignment, expert adapters, fusion harnesses, Cortex, and Neural Bus.
4. Add focused docs/tests and validate the updated core path without reopening Goose.

## Implemented In This Run
- Canonical attach seam extracted into `nexusnet/core/attach_base_model.py` and `ModelIngestionService`.
- Brain-first lifecycle tracing and persisted core execution artifacts added to the real generation path.
- HardwareScanner and adaptive system profiling now feed the core execution plan used by the brain.
- Root-owned `config/planes.yaml` and `MemoryNode` operationalization landed with no frozen plane count.
- Mixtral + Devstral + Router + Cortex + Neural Bus + Expert–Router Alignment scaffolding now exists as executable bounded harness code.
- Read-only operator surfaces now expose the latest core execution artifact through `/ops/brain/core`, `/ops/traces/{trace_id}`, and `/ops/brain/wrapper-surface`.
- Core evidence feeds now connect teacher bundles, dream episodes, distillation lineage, and native-takeover candidate refs back into the canonical brain summary and core execution trace.

## Remaining Highest-Value Core Gaps
- Heavy fusion training and live expert swapping remain scaffold-bounded on this host.
- Dream/foundry evidence now reaches the core summary and trace, but native expert execution still needs to use that evidence for deeper internal expert selection and promotion behavior.
- The next major core step is deeper native expert execution beyond scaffold planning, not more Goose-style infrastructure.
