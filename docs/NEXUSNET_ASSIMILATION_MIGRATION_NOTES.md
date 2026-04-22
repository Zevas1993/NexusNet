# NexusNet Assimilation Migration Notes

## Canon
- `LOCKED CANON`: `nexusnet/core`, `nexusnet/teachers`, `nexusnet/agents`, `nexusnet/foundry`, dream lineage fields, external evaluator gates.
- `STRONG ACCEPTED DIRECTION`: `nexusnet/runtime`, `nexusnet/retrieval/graphrag`, `nexusnet/federation`, wrapper agent surfaces, GraphRAG provider abstraction.
- `UNRESOLVED CONFLICT`: `runtime/config/planes.yaml`, `nexusnet/memory/planes.py`, `nexusnet/memory/projections.py`, `nexusnet/memory/migrations.py`.
- `IMPLEMENTATION BRANCH`: specific backend providers such as `vllm`, `llama.cpp`, `onnx-genai`, optional Neo4j provider, recurrent memory specialist teachers.

## Migration Notes
- `nexusnet/` is the constitutional brain-owned line. New runtime, teacher, graph, federation, foundry, and agent execution semantics land there first.
- `nexus/` remains the host shell, API/UI façade, and compatibility layer over the brain-owned modules.
- `core/` and `app/` runtime, QES, federated, and temporal code remain migration inputs only. They should not receive new canonical behavior.
- `runtime/config/teachers.yaml` is now the canonical teacher payload, replacing Python-only defaults.
- `runtime/config/planes.yaml` is now the canonical memory-plane contract with schema versioning and migration notes. Plane count is not frozen in core logic.
- Graph storage remains provider-neutral. The current local default is an implementation branch, not constitutional truth.
- Federated discoveries remain local candidate improvements until review, EvalsAO evaluation, and rollback-ready rollout planning complete.
- Native-growth artifacts remain shadow-governed until foundry benchmarks and external evaluation clear promotion.
