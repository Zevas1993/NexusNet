# Core Brain Execution

## Canon
- `NexusBrain` starts before any attached model work.
- `nexusnet.core.attach_base_model.attach_base_model()` is the canonical ingestion seam.
- Wrapped generation flows through NexusNet planning, memory, critique, and traceability instead of bypassing the brain.

## Execution Order
1. `NexusBrain.wake()` captures startup telemetry and the hardware profile before model attachment.
2. `BrainRuntimeRegistry.core_execution_plan()` selects the runtime/QES posture for the requested model.
3. `MemoryNode.execution_context()` loads the config-driven plane view for the task.
4. `MoEFusionScaffoldService.execution_plan()` builds the Mixtral + Devstral + Router + Cortex + Neural Bus scaffold view.
5. `CoreExecutionPolicyEngine.decide()` turns teacher, dream, distillation, native-takeover evidence, and Expert–Router Alignment ceilings into a bounded proposed posture plus an effective governed execution mode.
6. `NativeExecutionPlanner` and the internal-expert harness decide whether the task stays teacher fallback, adds native-shadow guidance, runs challenger shadow, or attempts guarded live while preserving teacher fallback and emitting teacher-comparison verdicts plus bounded native candidate drafts.
7. Promotion and replacement linkage converts foundry evidence plus bounded runtime outcomes into explicit governed actions, alignment-hold signals, rollbackable refs, behavior-loop next steps, and effective-mode continuity.
8. `_attach_base_model()` routes through `ModelIngestionService` and the canonical attach seam.
9. Attached-model generation runs only after the brain has recorded the plan and any bounded native-expert guidance.
10. Critique runs after generation and the resulting inference trace is persisted.

## Captured Core Metadata
- hardware profile
- selected runtime and QES plan
- quantization and safe-mode posture
- attached model identity and adapter capability profile
- teacher registry layer and teacher ID when present
- dream/live lineage tags
- memory-plane context
- fusion scaffold snapshot
- teacher-evidence bundle summary
- latest dream-episode linkage for the active trace or session when present
- foundry lineage and native-takeover candidate references when present
- evidence-driven execution policy ID, proposed mode, effective mode, governed action, alignment summary, reasons, and rollback guard
- native execution preview and result, selected internal experts, disagreement capture, teacher-comparison verdicts, bounded native response outline, native candidate metadata, policy fallback triggers, and runtime fallback triggers
- promotion linkage governed action, alignment-hold state, decision ID, rollback reference, evaluator linkage, governance checks, and behavior-loop next step
- ordered execution stages
- attach-record evidence refs, execution-mode continuity, policy IDs, promotion continuity, governed-action continuity, native runtime verdict continuity, and native candidate continuity

## Artifacts And Inspection
- core execution stage data is embedded under `trace.metrics.core_execution`
- a dedicated core execution artifact is written to `runtime/artifacts/core/execution/`
- core evidence feeds summarize the latest teacher, dream, and foundry-native lineage visible to the requested session or trace
- `core_summary()` exposes both the execution-policy preview and the native-execution preview for read-only operator inspection
- read-only inspection:
  - `GET /ops/brain/core`
  - `GET /ops/traces/{trace_id}`
  - `GET /ops/brain/wrapper-surface`

## Traceability Contract
- `brain-execution-start` must appear before `attach-base-model`
- `evidence-driven-policy` must appear before `attach-base-model`
- `native-candidate-activation` must appear before `attach-base-model`
- `native-promotion-linkage` must appear before `attach-base-model`
- `attach-base-model` must appear before `runtime-generate`
- `core_execution.artifact_id` and `core_execution.artifact_path` must be stable within a saved trace
- rollback analysis uses the persisted trace plus the generic `execution_traces` store record; no second control plane is introduced

## Files
- `nexusnet/core/brain.py`
- `nexusnet/core/attach_base_model.py`
- `nexusnet/core/execution_policy.py`
- `nexusnet/core/native_execution.py`
- `nexusnet/core/model_ingestion.py`
- `nexusnet/core/execution_trace.py`
