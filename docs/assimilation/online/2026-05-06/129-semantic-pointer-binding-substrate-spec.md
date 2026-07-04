# Semantic Pointer Binding Substrate Spec

Status: P1 final-pass assimilation target. Research-only until mapped to NexusNet memory encoding, symbolic reasoning, and multimodal binding.

## Source Evidence

- Spaun Science paper PDF: https://compneuro.uwaterloo.ca/files/2012-Spaun.pdf
- Semantic Pointer Architecture book chapter page: https://academic.oup.com/book/6263/chapter/149922017
- Nengo documentation: https://www.nengo.ai/nengo/
- Hyperdimensional computing survey Part I: https://arxiv.org/abs/2111.06077
- Hyperdimensional computing survey Part II: https://arxiv.org/abs/2112.15424
- Source status: primary model paper, official framework docs, and survey paper pages.

## Finding

Semantic Pointer Architecture and vector-symbolic/hyperdimensional computing show how neural-style distributed vectors can bind, compose, and manipulate symbols. This is a missing middle layer between raw embeddings and brittle symbolic graphs.

## NexusNet Assimilation Target

Add a semantic binding substrate to NexusNet. Concepts, tools, memories, policies, sources, and actions should have composable high-dimensional identities that support binding, unbinding, analogy, retrieval, and conflict detection.

## Proposed NexusNet Components

- `SemanticPointer`: high-dimensional representation for concept, role, source, or action.
- `BindingOperator`: combines entity and role, such as tool-used-by-agent or source-supports-claim.
- `UnbindingProbe`: retrieves the bound component from a composite representation.
- `VectorSymbolicMemory`: stores compositional memories with source links and privacy class.
- `AnalogyAndConflictDetector`: finds structural similarity or contradiction across bound representations.

## Promotion Gates

- Keep semantic pointers linked to raw evidence and graph nodes.
- Benchmark against existing vector search and graph retrieval.
- Require deterministic serialization for reproducible traces.
- Avoid treating vectors as proof; they are candidate retrieval and binding structures.
- Test robustness to noise, near-duplicates, and adversarially similar concepts.

## Risks

- High-dimensional symbols can be hard to inspect without explanation tools.
- Bad binding design can make retrieval opaque.
- It may duplicate graph/RAG behavior unless it unlocks measurable compositional gains.
