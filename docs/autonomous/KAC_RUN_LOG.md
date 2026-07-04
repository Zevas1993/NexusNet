# Knowledge Artifact Compiler Run Log

## 2026-05-06 - Source-Ref Security Gate

Next step completed: KAC now blocks unsafe `source_refs` before read and surfaces the blocked refs as replayable, sanitized metadata.

- Added explicit KAC source-ref gates for missing, out-of-root, absolute, private, and non-UTF8 refs.
- Persisted `source_ref_security_gate`, `blocked_source_refs`, and `control_panel_replay` on compiled knowledge artifacts.
- Added `ArtifactTrustRegistry.scan_knowledge_artifact()` and `/ops/brain/artifact-trust/knowledge-artifacts/scan` so blocked KAC source refs quarantine the artifact in artifact trust.
- Added a non-persistent `ArtifactTrustRegistry.preview_knowledge_artifact()` result to compiled KAC artifacts so compile surfaces the trust decision without mutating Artifact Trust records.
- Surfaced the gate state and blocked source-ref count in the Control Panel KAC card.
- Added a Control Panel `Scan KAC Artifact Trust` action that scans the latest compiled artifact through Artifact Trust and refreshes the trust replay card.
- Added blackbox/canon replay controls for `source_ref_security_gate`, `blocked_source_ref_replay`, `artifact_trust_preview`, and `artifact_trust_scan`.
- Added 3D visualizer/Control Panel page metrics for blocked KAC source refs and automatic artifact-trust preview status.
- Added KRC query response evidence for `source_ref_security_gate`, `blocked_source_refs`, and `artifact_trust_preview` when a compiled artifact satisfies the request.
- Added canon scorecard summaries for latest source-ref gate counts/reasons and latest artifact-trust preview state.
- Surfaced canon source-ref and artifact-trust preview summaries in the Control Panel KAC operator card.
- Added explicit required controls for `artifact_trust_preview` and `artifact_trust_scan`.
- Added regression coverage proving absolute workstation paths are blocked before KAC source-ref reads.
- Added a distinct `source_ref_directory_blocked` gate result so directory refs cannot be treated as file refs or generic missing refs.
- KRC query responses now mark quarantined compiled artifacts as `compiled_artifact_quarantined` with `runtime_context_allowed: false`.
- Canon KAC scorecards now emit active runtime blockers when the latest artifact is source-gate blocked or artifact-trust quarantined.
- Control Panel KAC card now surfaces active runtime blockers directly.
- Added `/ops/brain/knowledge-artifacts/freshness` and advertised it in KAC operator actions for source digest invalidation checks.
- Freshness checks now persist staleness back into the KAC artifact so list/scorecard `stale_count` reflects operator checks.
- KRC query responses now mark stale compiled artifacts as `compiled_artifact_stale` with `runtime_context_allowed: false`.
- Canon KAC scorecards now emit `kac_latest_artifact_stale` when freshness checks mark the latest artifact stale.
- Visualizer Knowledge Artifacts page now exposes `active_runtime_blocker_count`.
- Blackbox KAC frame now includes the freshness endpoint as replay evidence.
- Updated the KAC architecture doc to define the source-ref security gate and non-persistent artifact-trust preview contract.
- Added KAC JSONL index replay metadata for source-ref gate counts/reasons and artifact-trust preview status.
- Verified that blocked private/out-of-root material is not read into compiled artifact content or trust scans.
- Added downstream KRC runtime-gate lineage for DatasetForge, HiveModelGrowthEngine, production-spine teacher reviews/dream cycles, and RecursiveDreamEngine.
- Downstream KAC consumers now state `requires_krc_runtime_context_allowed: true` and `blocks_stale_or_quarantined_context: true` before compiled artifacts can act as training, review, or dream context.
- Added canon scorecard coverage for downstream KRC runtime gates across runtime-context consumers.
- Control Panel now displays KAC downstream runtime-gate coverage and marks each code-backed consumer with whether it requires KRC `runtime_context_allowed`.
- Visualizer Knowledge Artifacts page metrics now expose downstream KRC runtime-gate gated/required counts and all-gated status.
- Blackbox replay compliance controls now include `downstream_krc_runtime_gate_coverage` for KAC replay parity.
- KAC architecture doc now defines the downstream KRC runtime gate and the required consumer fields for DatasetForge, growth, teacher review, and recursive dreaming.
- Deep Replay `knowledge_artifact_ref` records now carry the downstream KRC runtime-gate fields for developer drilldown parity.
- DatasetForge now accepts KRC runtime-context evidence and blocks manifests when a referenced KAC artifact has `runtime_context_allowed: false`.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_artifact_source_ref_security_gate_blocks_missing_out_of_root_and_private_refs tests\test_artifact_trust_registry.py::test_artifact_trust_registry_quarantines_knowledge_artifact_with_blocked_source_refs
2 passed

python -m compileall nexusnet\knowledge nexusnet\security nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py
45 passed

pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_artifact_api_control_panel_and_blackbox_visibility
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_artifact_compiler_docs_and_ledger_entry_are_present
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_artifact_api_control_panel_and_blackbox_visibility
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_artifact_source_ref_security_gate_blocks_missing_out_of_root_and_private_refs
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
54 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
55 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
56 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
57 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
58 passed

python -m compileall nexusnet\knowledge nexusnet\security nexusnet\canon nexusnet\visuals nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_dataset_forge.py::test_dataset_forge_records_knowledge_artifact_refs_as_context_lineage tests\test_hive_model_growth_engine.py::test_growth_engine_carries_knowledge_artifact_refs_into_growth_lineage tests\test_nexusnet_production_spine.py::test_recursive_dream_cycle_materializes_candidates_and_growth_seed tests\test_nexusnet_production_spine.py::test_teacher_council_review_records_knowledge_artifact_refs_as_context_only tests\test_nexusnet_brain.py::test_nexusnet_phase2_loops_produce_artifacts_and_records
5 passed

pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_artifact_api_control_panel_and_blackbox_visibility
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_artifact_source_ref_security_gate_blocks_missing_out_of_root_and_private_refs
1 passed

pytest -q tests\test_nexusnet_visualizer.py::test_visualizer_endpoint_and_static_ui_are_available
1 passed

pytest -q tests\test_nexusnet_production_spine.py::test_deep_replay_bundle_indexes_cycle_artifacts_for_developer_drilldown
1 passed

pytest -q tests\test_dataset_forge.py::test_dataset_forge_records_knowledge_artifact_refs_as_context_lineage tests\test_dataset_forge.py::test_dataset_forge_blocks_kac_refs_when_runtime_context_evidence_is_disallowed
2 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
73 passed

python -m compileall nexusnet\knowledge nexusnet\security nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
73 passed

python -m compileall nexusnet\knowledge nexusnet\security nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
73 passed

python -m compileall nexusnet\knowledge nexusnet\security nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed
```

KAC runtime enforcement monitoring pass:

- KAC scorecard, Control Panel, and Visualizer now distinguish gated runtime consumers from code-enforced runtime consumers.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_artifact_api_control_panel_and_blackbox_visibility
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_artifact_source_ref_security_gate_blocks_missing_out_of_root_and_private_refs
1 passed
```

Production-spine KRC runtime-gate enforcement pass:

- Production Spine teacher-council review and recursive dream cycles now block when KRC runtime context evidence disallows a referenced KAC artifact.

Validation:

```text
pytest -q tests\test_nexusnet_production_spine.py::test_recursive_dream_cycle_blocks_disallowed_kac_runtime_context tests\test_nexusnet_production_spine.py::test_teacher_council_review_blocks_disallowed_kac_runtime_context tests\test_nexusnet_production_spine.py::test_recursive_dream_cycle_materializes_candidates_and_growth_seed tests\test_nexusnet_production_spine.py::test_teacher_council_review_records_knowledge_artifact_refs_as_context_only
4 passed

pytest -q tests\test_nexusnet_production_spine.py
21 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
77 passed

python -m compileall nexusnet\knowledge nexusnet\security nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

npx gitnexus analyze --force
Repository indexed successfully
20,061 nodes | 30,109 edges | 531 clusters | 216 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KAC query-event hash-chain pass:

- KRC query events now record `event_hash`.
- KRC query events now record `previous_event_hash`, with `genesis` on the first event.
- Tests verify event two points to event one and post-restart event three points to event two.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_request_contract_prefers_compiled_artifacts_and_records_fallback
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py
15 passed

python -m compileall nexusnet\knowledge nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
82 passed

npx gitnexus analyze --force
Repository indexed successfully
20,124 nodes | 30,092 edges | 522 clusters | 208 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KAC query-event durability pass:

- Query events now use persisted event sequence counts, so process restarts continue replay ordering instead of resetting sequence to one.
- Query events now use microsecond timestamps to reduce same-second collision ambiguity.
- Test coverage verifies same-second replay ordering and post-restart sequence continuation.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_request_contract_prefers_compiled_artifacts_and_records_fallback
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py
15 passed

python -m compileall nexusnet\knowledge nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
82 passed

npx gitnexus analyze --force
Repository indexed successfully
20,124 nodes | 30,086 edges | 525 clusters | 208 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KAC visualizer query-history metric pass:

- Knowledge Artifacts visualizer page metrics now include `query_event_count`.
- This lets the 3D/control-plane state show KRC query replay activity without opening the raw query-events endpoint first.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py
15 passed

python -m compileall nexusnet\visuals nexusnet\knowledge nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
82 passed

npx gitnexus analyze --force
Repository indexed successfully
20,122 nodes | 30,083 edges | 526 clusters | 209 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KAC query-events endpoint pass:

- Added `GET /ops/brain/knowledge-artifacts/query-events`.
- KAC operator actions, visualizer evidence refs, and blackbox evidence refs now include query-event replay.
- KAC docs now identify query events as append-only evidence with no context mutation authority.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py
15 passed

python -m compileall nexusnet\knowledge nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
82 passed

npx gitnexus analyze --force
Repository indexed successfully
20,120 nodes | 30,083 edges | 524 clusters | 209 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KRC query-history replay pass:

- KnowledgeArtifactStore now records append-only KRC query events.
- KRC query responses now include `query_event_ref` and `query_recorded_at`.
- Query replay ordering now uses `event_sequence` in addition to timestamp so multiple same-second queries replay deterministically.
- KAC scorecard and Control Panel now surface query-event count and latest query-event state.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py::test_knowledge_request_contract_prefers_compiled_artifacts_and_records_fallback
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py
15 passed

python -m compileall nexusnet\knowledge nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
82 passed

npx gitnexus analyze --force
Repository indexed successfully
20,119 nodes | 30,077 edges | 528 clusters | 209 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KAC blackbox replay boundary pass:

- Canon blackbox Knowledge Artifacts frame now includes `raw_retrieval_recall_only_boundary`.
- Canon blackbox Knowledge Artifacts frame now includes `query_mutation_boundary`.
- This keeps replay/compliance evidence aligned with the KRC query payload contract and downstream runtime gates.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py
15 passed

python -m compileall nexusnet\canon nexusnet\knowledge
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
82 passed

npx gitnexus analyze --force
Repository indexed successfully
20,116 nodes | 30,148 edges | 529 clusters | 217 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KRC query no-mutation boundary pass:

- KRC compiled-artifact payloads now expose `mutation_allowed: false`, `runtime_boundary`, allowed runtime uses, and blocked runtime uses.
- Raw-retrieval fallback KRC payloads now expose a separate recall-only runtime boundary and explicitly block teacher-council, DatasetForge, growth-cycle, dream-seed, prompt, model-weight, node-registry, and promotion-state use.
- KAC canon scorecard now includes `query_mutation_boundary` as a required control.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py
15 passed

python -m compileall nexusnet\knowledge nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
82 passed

npx gitnexus analyze --force
Repository indexed successfully
20,115 nodes | 30,148 edges | 528 clusters | 217 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

Production Spine raw-fallback KAC proof pass:

- Added Production Spine proof that raw-retrieval fallback KRC payloads are blocked before teacher-council review and recursive dream candidate materialization.
- Production Spine compiled knowledge context now surfaces `blocks_raw_retrieval_fallback_context: true`.

Validation:

```text
pytest -q tests\test_nexusnet_production_spine.py::test_production_spine_blocks_raw_retrieval_fallback_as_kac_runtime_context
1 passed

pytest -q tests\test_nexusnet_production_spine.py
22 passed

python -m compileall nexusnet\growth nexusnet\knowledge nexusnet\dreaming nexusnet\adapters nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
82 passed

npx gitnexus analyze --force
Repository indexed successfully
20,090 nodes | 30,117 edges | 528 clusters | 217 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KAC raw-retrieval fallback boundary pass:

- KRC raw-retrieval fallback payloads now return `runtime_context_allowed: false` with `runtime_context_role: raw_retrieval_recall_only`.
- DatasetForge, HiveModelGrowthEngine, Production Spine KAC context gates, and RecursiveDreamEngine now block raw-retrieval fallback payloads from training/growth/dream substrate use.
- Control Panel consumer labels show whether the consumer blocks raw fallback.
- The KAC spec now explicitly says raw retrieval fallback is recall-only and cannot seed training data, growth cycles, node promotion, recursive dream candidates, or teacher-council formation evidence.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py::test_kac_raw_retrieval_fallback_payload_is_recall_only_not_growth_context
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py
59 passed

python -m compileall nexusnet\knowledge nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
81 passed

npx gitnexus analyze --force
Repository indexed successfully
20,087 nodes | 30,115 edges | 527 clusters | 217 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KAC operator API runtime-gate proof pass:

- Added endpoint-level proof that a disallowed KAC query payload is rejected through:
  - `/ops/brain/dataset-forge/manifests`
  - `/ops/brain/growth-engine/cycles`
  - `/ops/brain/dream`
- This proves operator APIs preserve the same KRC runtime-context block semantics as direct component calls.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py::test_kac_disallowed_query_payload_is_rejected_by_operator_apis
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py
14 passed

python -m compileall nexusnet\knowledge nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
80 passed

npx gitnexus analyze --force
Repository indexed successfully
20,082 nodes | 30,110 edges | 527 clusters | 217 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KAC visualizer proof-ref replay pass:

- Knowledge Artifacts visualizer page now exposes downstream runtime-gate proof-ref counts.
- Knowledge Artifacts visualizer evidence refs now include the code/test proof refs published by the KAC scorecard.
- Required visualizer surfaces now include runtime gate proof refs so replay cannot hide enforcement evidence behind a summary count.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py
13 passed

python -m compileall nexusnet\visuals nexusnet\knowledge
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
79 passed

npx gitnexus analyze --force
Repository indexed successfully
20,078 nodes | 30,108 edges | 525 clusters | 217 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KAC runtime enforcement monitoring proof pass:

- KAC scorecard now publishes proof refs for each code-enforced downstream runtime consumer.
- Control Panel runtime-gate coverage now shows proof-ref counts and per-consumer proof counts.
- KRC query payloads now include `artifact_id` and `artifact_ref` so direct downstream runtime gate failures can cite the blocked compiled artifact.
- Added an end-to-end acceptance test proving a disallowed KRC query result is rejected by DatasetForge, HiveModelGrowthEngine, and RecursiveDreamEngine.

Validation:

```text
pytest -q tests\test_knowledge_artifact_compiler.py::test_kac_disallowed_query_payload_is_rejected_by_runtime_consumers
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py
13 passed

python -m compileall nexusnet\knowledge nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
79 passed

npx gitnexus analyze --force
Repository indexed successfully
20,079 nodes | 30,108 edges | 526 clusters | 217 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KRC runtime-gate enforcement expansion:

- TeacherCouncilReviewer blocks disallowed KAC runtime context evidence before council review can use it.
- RecursiveDreamCycleRunner blocks disallowed KAC runtime context evidence before emitting dream candidates.
- Standalone RecursiveDreamEngine rejects disallowed KAC runtime context evidence and records rejection/governance events.
- KAC scorecard, Control Panel, visualizer, and blackbox compliance now expose downstream runtime-gate coverage and code-enforced counts.

Validation:

```text
pytest -q tests\test_nexusnet_production_spine.py::test_teacher_council_review_blocks_disallowed_kac_runtime_context tests\test_nexusnet_production_spine.py::test_recursive_dream_cycle_blocks_disallowed_kac_runtime_context
2 passed

pytest -q tests\test_nexusnet_brain.py::test_recursive_dream_engine_rejects_disallowed_kac_runtime_context
1 passed

pytest -q tests\test_nexusnet_production_spine.py
21 passed

pytest -q tests\test_nexusnet_brain.py
6 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
78 passed

python -m compileall nexusnet\knowledge nexusnet\security nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

npx gitnexus analyze --force
Repository indexed successfully
20,069 nodes | 30,126 edges | 527 clusters | 216 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

Production-spine and standalone dream KRC runtime-gate enforcement pass:

- Production Spine teacher-council review and recursive dream cycles block when KRC runtime context evidence disallows a referenced KAC artifact.
- `DreamCycleRequest` now accepts KRC runtime context evidence.
- RecursiveDreamEngine rejects dream cycles before variant generation when a referenced KAC artifact has `runtime_context_allowed: false`.

Validation:

```text
pytest -q tests\test_nexusnet_production_spine.py::test_recursive_dream_cycle_blocks_disallowed_kac_runtime_context tests\test_nexusnet_production_spine.py::test_teacher_council_review_blocks_disallowed_kac_runtime_context tests\test_nexusnet_production_spine.py::test_recursive_dream_cycle_materializes_candidates_and_growth_seed tests\test_nexusnet_production_spine.py::test_teacher_council_review_records_knowledge_artifact_refs_as_context_only
4 passed

pytest -q tests\test_nexusnet_production_spine.py
21 passed

pytest -q tests\test_nexusnet_brain.py::test_recursive_dream_engine_rejects_disallowed_kac_runtime_context tests\test_nexusnet_brain.py::test_nexusnet_phase2_loops_produce_artifacts_and_records
2 passed

pytest -q tests\test_nexusnet_brain.py
6 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
78 passed

python -m compileall nexusnet\knowledge nexusnet\security nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

npx gitnexus analyze --force
Repository indexed successfully
20,074 nodes | 30,125 edges | 533 clusters | 216 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

GitNexus:

```text
npx gitnexus analyze --force
Repository indexed successfully
19,892 nodes | 29,850 edges | 528 clusters | 209 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium

npx gitnexus analyze --force
Repository indexed successfully
19,943 nodes | 29,968 edges | 529 clusters | 214 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium

npx gitnexus analyze --force
Repository indexed successfully
20,019 nodes | 30,060 edges | 530 clusters | 216 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium

npx gitnexus analyze --force
Repository indexed successfully
20,019 nodes | 30,060 edges | 530 clusters | 216 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

Additional verification:

```text
pytest -q tests\test_nexusnet_production_spine.py::test_deep_replay_bundle_indexes_cycle_artifacts_for_developer_drilldown
1 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
73 passed

python -m compileall nexusnet\knowledge nexusnet\security nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

npx gitnexus analyze --force
Repository indexed successfully
20,028 nodes | 30,067 edges | 532 clusters | 216 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```

KRC runtime-gate enforcement pass:

- DatasetForge accepts KRC runtime context evidence and blocks explicit `runtime_context_allowed: false` artifacts.
- HiveModelGrowthEngine accepts KRC runtime context evidence and hard-blocks growth cycles that try to use stale/quarantined/disallowed KAC artifacts.

Validation:

```text
pytest -q tests\test_dataset_forge.py
10 passed

pytest -q tests\test_hive_model_growth_engine.py::test_growth_engine_carries_knowledge_artifact_refs_into_growth_lineage tests\test_hive_model_growth_engine.py::test_growth_engine_blocks_kac_refs_when_runtime_context_evidence_is_disallowed
2 passed

pytest -q tests\test_hive_model_growth_engine.py
7 passed

pytest -q tests\test_knowledge_artifact_compiler.py tests\test_artifact_trust_registry.py tests\test_dataset_forge.py tests\test_hive_model_growth_engine.py tests\test_nexusnet_brain.py tests\test_nexusnet_production_spine.py tests\test_growth_lifecycle_orchestrator.py tests\test_nexusnet_visualizer.py
75 passed

python -m compileall nexusnet\knowledge nexusnet\security nexusnet\canon nexusnet\visuals nexusnet\adapters nexusnet\growth nexusnet\dreaming nexus\api
passed

node --check ui\control-panel\app.js
passed

npx gitnexus analyze --force
Repository indexed successfully
20,049 nodes | 30,100 edges | 528 clusters | 216 flows

npx gitnexus status
Status: up-to-date

npx gitnexus detect-changes -r NexusNet
Risk level: medium
```
