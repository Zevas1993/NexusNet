# Core NexusNet Pivot Run Log

## Baseline
- Goose is accepted as closed baseline infrastructure and is not being reopened in this run.
- This run is focused on the unfinished center of the project: the actual brain-first NexusNet core path.

## Planned Work
1. Build a canonical model-ingestion seam around `attach_base_model()`.
2. Feed the real brain path with hardware-aware runtime/QES planning and MemoryNode context.
3. Add executable MoE fusion and Expert-Router Alignment scaffolding.
4. Document and validate the updated core path.

## Audit Notes
- Audit complete. The largest core gap is not missing wrappers or governance; it is the missing canonical seam between the brain, model attachment, runtime/QES planning, and future MoE fusion.
- `nexusnet/moe` does not currently exist, so the Mixtral + Devstral + NexusNet branch needs real executable scaffolding rather than more doc-only intent.
- `config/planes.yaml` is missing even though multi-plane memory is already present conceptually and in runtime config.

## Implementation Notes
- Added `nexusnet.core.attach_base_model.attach_base_model()` as the canonical model-ingestion seam and wrapped it in `ModelIngestionService`.
- Updated `NexusBrain` so wakeup, runtime/QES planning, MemoryNode context, fusion scaffold planning, model attachment, generation, and critique all flow through a single brain-first path.
- Added persisted core execution artifacts under `runtime/artifacts/core/execution/` and surfaced the latest artifact IDs through `/ops/brain/core`, `/ops/traces/{trace_id}`, and `/ops/brain/wrapper-surface`.
- Operationalized `MemoryNode` with root-level `config/planes.yaml`, compatibility views, and a migration script that proves plane count is config-driven.
- Added executable `nexusnet.moe` scaffolding for adapter registry, Expert–Router Alignment, Mixtral + Devstral harnessing, Cortex peer, and Neural Bus coordination.
- Wrote core operator docs for the brain seam, router alignment, fusion branch, MemoryNode, and hardware-aware core execution.
- Added a core evidence bridge so teacher evidence bundles, dream episodes, distillation lineage, and native-takeover candidate refs show up in the canonical brain summary and wrapped operator inspection path.

## Validation
- `python -m py_compile` passed for touched core/runtime/operator/ui-surface files.
- `node --check ui/visualizer/app.js` passed.
- `pytest tests/test_nexusnet_core_pivot.py -q` -> `5 passed`
- `pytest tests/test_nexus_phase1_foundation.py tests/test_nexusnet_brain.py tests/test_nexusnet_wrapper_surface.py -q` -> `12 passed`
- `pytest tests/test_nexusnet_core_pivot.py tests/test_nexus_phase1_foundation.py tests/test_nexusnet_brain.py tests/test_nexusnet_wrapper_surface.py -q` -> `17 passed`
- `pytest tests/test_nexusnet_visualizer.py -q` -> `8 passed`
- `pytest tests/test_nexusnet_promotion_loop.py tests/test_nexusnet_assimilation.py tests/test_nexusnet_wrapper_surface.py -q` -> `8 passed`
- `pytest tests/test_nexusnet_visualizer.py -q` -> `8 passed`
- `pytest -q` -> `130 passed, 1 skipped`

## Failures Fixed
- Wrapper-surface core traceability initially showed `None` because the operator trace did not carry the brain-level `core_execution` payload forward.
- Fixed by propagating `brain_trace_id` and `core_execution` into the operator trace metrics instead of weakening the wrapper-surface assertion.
- No new functional failures were introduced during the evidence-feed iteration.

## Blockers
- None currently.

## Goose Status
- Goose remains closed and unchanged in this run except for baseline validation discipline. No Goose reopen work was introduced.
