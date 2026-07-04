# GraphRAG Knowledge Structure Spec

Status: P2 online assimilation target. Research-only until NexusNet graph memory and KAC architecture are mapped against these references.

## Source Evidence

- Microsoft GraphRAG repository: https://github.com/microsoft/graphrag
- Microsoft GraphRAG docs: https://microsoft.github.io/graphrag/
- LightRAG repository: https://github.com/HKUDS/LightRAG
- HippoRAG repository: https://github.com/OSU-NLP-Group/HippoRAG
- Source status: public repositories and official project documentation where available.

## Finding

GraphRAG-style systems use entity, relationship, community, and graph traversal structures to improve retrieval over large corpora. The useful NexusNet lesson is not to replace memory with a graph, but to attach graph structure to evidence so retrieval can reason over entities, contradictions, chronology, and communities.

## NexusNet Assimilation Target

Refine KAC and memory around graph-backed evidence views. NexusNet should preserve raw source chunks while generating separate entity and relationship layers that can be invalidated, audited, and refreshed.

## Proposed NexusNet Components

- `EvidenceGraphNode`: entity, claim, source, memory, task, artifact, or contradiction.
- `EvidenceGraphEdge`: cites, derived-from, contradicts, updates, depends-on, same-as, and temporal-next.
- `GraphRetrievalTrace`: query expansion, traversed nodes, selected evidence, rejected paths, and confidence.
- `GraphRefreshJob`: rebuilds derived graph layers when source evidence changes.
- `CommunitySummaryRecord`: generated summary with source anchors, confidence, and invalidation rules.

## Promotion Gates

- Never let graph summaries replace raw sources.
- Track source lineage for every node and edge.
- Rebuild or invalidate derived graph layers after source changes.
- Test graph retrieval against simple vector retrieval before adoption.

## Risks

- Graph construction can hallucinate entities or relations.
- GraphRAG can add complexity without improving specific NexusNet tasks.
- Community summaries can blur evidence if not tied to source anchors.
