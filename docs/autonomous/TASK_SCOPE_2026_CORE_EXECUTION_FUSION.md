# Task Scope: 2026 Core Execution + Fusion Run

## Accepted Baseline
- Goose remains closed and is not being reopened here.
- Teacher historical/live split, teacher governance, the visual subsystem baseline, and bounded external assimilation lanes are accepted.
- The current evidence-feed bridge in `nexusnet/core/brain.py` is accepted as the starting seam, not a target for rework.

## Current State At Start
- The brain-first execution seam, canonical attach path, QES/runtime planning, MemoryNode runtime view, and MoE scaffold already exist.
- Teacher, dream, distillation, and native-takeover evidence are visible in core summaries and traces.
- The largest remaining gap is that those evidence feeds are still mostly observational; they do not yet drive bounded native-shadow or live-planner decisions inside the real brain path.

## This Task Touches
- evidence-driven core execution policy and native execution planning
- canonical attach/model-ingestion trace enrichment
- bounded internal expert runtime and harness behavior
- stronger Expert–Router Alignment and fusion path utilization
- MemoryNode/QES context carried into actual execution-policy decisions
- focused docs, tests, and run logging

## Highest-Value Core Gaps At Start
- teacher/dream/foundry evidence does not yet change expert weighting or native-shadow/live-planner routing
- internal expert execution remains implicit rather than a bounded callable harness
- wrapped generation still lacks an explicit native-expert guidance layer between evidence and the attached model path
- attach records do not yet capture evidence refs or execution-mode continuity

## Canon Preserved
- NexusNet remains brain-first and starts before attached models
- Dream Training and Federated Continuous Learning remain mandatory implementation lines
- Mixtral + Devstral + Router + Cortex + Neural Bus remain the active scaffold branch
- Expert–Router Alignment remains a prerequisite, not an assumption
- Multi-Plane MemoryNode remains config-driven and unfrozen
- the visualizer remains read-only
- Goose remains closed unless real ACP-provider-triggered work appears

## Known Unrelated Dirty-Tree Risk
- The repo still has substantial pre-existing tracked and untracked drift outside this run.
- Permission-denied temp and pytest cache noise remains visible under `.pytest-tmp`, `pytest-cache-files-*`, and `runtime/test-tmp-run`.

## Planned High-Leverage Iterations
1. Add an evidence-driven execution policy and native execution planner to the real brain path.
2. Add bounded internal expert execution and disagreement capture with safe teacher fallback.
3. Thread execution-mode and evidence refs through attach/model-ingestion records and read-only surfaces.
4. Strengthen docs/tests and validate the updated core path without reopening Goose.

## Implemented In This Run
- Added `CoreExecutionPolicyEngine` and `NativeExecutionPlanner` so teacher, dream, distillation, and native-takeover evidence now influence bounded execution mode selection.
- Added bounded internal expert runtime, execution, and harness services under `nexusnet/experts/` with capability gating, output capture, disagreement capture, and explicit teacher fallback.
- Updated `NexusBrain.generate()` and `core_summary()` so execution policy and native execution now feed real prompt construction, trace artifacts, and read-only operator inspection.
- Threaded execution-mode and evidence refs through the canonical attach/model-ingestion seam so cached attachment records preserve continuity instead of losing later evidence.
- Extended wrapper/operator traceability so execution policy and internal-expert runtime summaries remain visible without introducing a second control plane.
- Added focused docs for evidence-driven execution and internal expert execution and validated the new lane with targeted and full-suite tests.

## Remaining Highest-Value Core Gaps
- The current native lane is `native-planner-live`, not direct heavyweight native inference or replacement.
- Fusion remains harness-bounded on this host; deeper real expert execution beyond bounded prompt guidance is still the next native step.
- Dream/foundry evidence now changes execution decisions, but future work should push those signals deeper into promotion and replacement behavior rather than adding more wrapper infrastructure.
