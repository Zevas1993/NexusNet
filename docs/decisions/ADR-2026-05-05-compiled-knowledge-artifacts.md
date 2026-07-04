# ADR-2026-05-05: Compiled Knowledge Artifacts

## Status

Candidate.

## Decision

Add a NexusNet-native Knowledge Artifact Compiler and Knowledge Request Contract. The subsystem compiles approved source material into typed, cited, versioned task artifacts and exposes them through local ops endpoints and Control Panel replay.

## Context

Agentic workflows repeatedly rebuild context, source authority, citations, and output shape at runtime. The reviewed VentureBeat and Pinecone Nexus materials argue for a compilation-stage knowledge layer. NexusNet should assimilate the pattern while remaining local-first and vendor-independent.

## Consequences

- Raw retrieval remains available as fallback.
- KAC artifacts may feed NexusBrain, AOs, experts, teacher councils, DatasetForge, Growth Engine, and assimilation reviews only by explicit artifact refs.
- KAC cannot mutate prompts, weights, routes, providers, binaries, node registries, or promotion state.
- Promotion requires eval evidence for citation coverage, deterministic artifact hashes, freshness invalidation, permission filtering, conflict handling, and Control Panel replay.

## Rejected Alternatives

- Direct Pinecone Nexus dependency.
- Replacing raw retrieval.
- Storing uncited synthesized facts.
- Letting compiled context mutate runtime behavior without governance.
