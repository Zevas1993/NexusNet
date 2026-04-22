# Multi-Plane MemoryNode

## Canon
- Memory planes are config-driven.
- The operational structure supports the accepted 11-plane layout.
- Compatibility views for earlier 8-plane and 3-plane lineages remain available.
- The plane count is not hardcoded.

## Runtime Behavior
- `MemoryNode` owns the root config path: `config/planes.yaml`.
- If the root config is missing, it is created from the runtime config or the default payload.
- `MemoryPlaneRegistry` still performs the schema/config load, but `MemoryNode` becomes the operational service that the brain uses.

## Core Integration
- Routing uses `routing_planes`.
- Dreaming uses `dreaming_planes`.
- Retrieval uses `retrieval_planes`.
- Foundry/takeover evidence uses `foundry_evidence_planes`.
- Evidence-driven execution policy uses active planes and foundry-evidence planes as part of native-shadow/live-planner readiness.
- Operator inspection can read the resolved plane layout through the brain summary and wrapper surface.

## Migration
- `scripts/migrations/add_new_planes.py` adds planes into the root config without freezing the plane count.
- Tests prove that adding a twelfth plane changes the live load result without code edits.

## Files
- `nexusnet/memory/memory_node.py`
- `nexusnet/memory/planes.py`
- `config/planes.yaml`
- `scripts/migrations/add_new_planes.py`
