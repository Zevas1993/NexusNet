# Compiled Knowledge Layer Review - 2026-05-05

Status: candidate research record

## Sources

- VentureBeat: `https://venturebeat.com/data/the-rag-era-is-ending-for-agentic-ai-a-new-compilation-stage-knowledge-layer-is-what-comes-next/`
- Pinecone Nexus: `https://www.pinecone.io/product/nexus/`

## Verdict

Assimilate the architecture pattern, not Pinecone Nexus as a required dependency. The useful pattern is moving repeated agentic context assembly upstream into compiled, task-specific, typed, cited, permission-aware artifacts.

## NexusNet Fit

NexusNet already has raw retrieval, memory, provenance, Dataset Radar, DatasetForge, growth cycles, replay, and governance surfaces. KAC sits above raw retrieval and below NexusBrain/AO/expert execution as a context artifact layer.

## Risk Controls

- Vendor claims are treated as evaluation targets, not proven production evidence.
- Source material must pass license, privacy, RBAC, and provenance gates.
- Every factual field must have citations.
- Conflicting facts produce conflict objects instead of silent overwrite.
- Source digest changes mark artifacts stale.
- Raw retrieval remains available as fallback.

## Initial Implementation Evidence

The v0 implementation is local JSON/JSONL backed and exposes:

- `POST /ops/brain/knowledge-artifacts/compile`
- `POST /ops/brain/knowledge-artifacts/query`
- `GET /ops/brain/knowledge-artifacts`
- `GET /ops/brain/knowledge-artifacts/{artifact_id}`
- `GET /ops/brain/canon/knowledge-artifacts`

Control Panel and blackbox recorder visibility are required before this can move beyond candidate.
