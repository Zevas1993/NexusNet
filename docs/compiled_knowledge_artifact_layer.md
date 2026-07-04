# Compiled Knowledge Artifact Layer

Status: candidate
Ledger: PB-2026-05-05-080
Source reverified: 2026-05-31, see `docs/assimilation/ASSIMILATION_TARGET_SOURCE_REVERIFICATION_2026-05-31.md`

## Purpose

The NexusNet Knowledge Artifact Compiler converts approved source material into reusable, typed, cited, versioned, permission-aware task artifacts. It does not replace raw retrieval. Raw retrieval remains a lower-level recall and fallback lane when a compiled artifact is missing, stale, or out of scope.

The 2026-05-31 source check confirms the VentureBeat/Pinecone Nexus article is still reachable and still describes a compilation-stage knowledge layer, context compiler, field-level citations, and deterministic conflict handling. Those claims remain architecture references only. NexusNet KAC stays local-first and vendor-independent, and any vendor performance claims require independent local reproduction before they can influence promotion.

## Boundary

KAC is local-first and vendor-independent. The VentureBeat and Pinecone Nexus materials are architecture references for compilation-stage knowledge, not runtime dependencies. KAC cannot mutate prompts, model weights, runtime binaries, node registries, growth-cycle promotion state, or provider routing. It only produces replayable context artifacts.

## Artifact Contract

Every artifact records:

- artifact id and deterministic hash
- task family and scope
- typed content
- field-level citations
- source digests
- confidence metadata
- deterministic conflict objects
- governance/RBAC/privacy state
- freshness policy
- source-ref security gate results for project-local reads
- blocked source refs and blocked reasons
- non-persistent artifact-trust preview state
- downstream KRC runtime gate coverage
- raw retrieval fallback policy

## Source-Ref Security Gate

KAC may compile operator-provided `source_refs`, but every ref is checked before read through a source-ref security gate. The gate blocks:

- missing refs
- out-of-root refs
- absolute workstation paths
- private path segments such as `.secrets`, `.keys`, `private`, and `credentials`
- non-UTF8 text refs

Blocked refs are recorded as sanitized replay metadata. Their contents are not read into the compiled artifact, KRC response, Control Panel card, blackbox frame, or trust scan metadata.

## Artifact-Trust Preview

Each compiled artifact receives an automatic, non-persistent artifact-trust preview. The preview uses the same KAC-aware Artifact Trust rules as the operator-triggered scan, but it does not mutate Artifact Trust registry state. Operators can then run the explicit `artifact-trust` scan endpoint when they want a persistent trust record.

## Downstream KRC Runtime Gate

Every runtime-context consumer must treat KAC output as refs-only lineage until a Knowledge Request Contract query returns `runtime_context_allowed: true` for a `compiled_artifact` payload. This downstream KRC runtime gate blocks stale, quarantined, source-ref-blocked, raw-retrieval-fallback, or otherwise unsafe KRC payloads from becoming teacher-council context, DatasetForge curriculum material, growth-cycle context, or recursive dream seeds.

Raw retrieval fallback remains available for answering and recall, but it is `raw_retrieval_recall_only`. It cannot seed training data, growth cycles, node promotion, recursive dream candidates, or teacher-council formation evidence.

The gate does not prevent Deep Replay from showing blocked refs. Replay remains read-only and must surface blocked/quarantined state for operator inspection.

Every KRC query payload must also carry a no-mutation boundary. A valid compiled artifact can provide context refs, citations, and confidence evidence, but it cannot directly mutate prompts, model weights, node registries, or promotion state. Those changes must pass through the separate sandbox/eval/governance/checkpoint flows.

KRC queries are recorded as append-only replay events under the project-local KAC store and exposed through `/ops/brain/knowledge-artifacts/query-events`. Query events include event hashes and previous-event hashes for tamper-evident replay ordering. They are evidence only; they cannot authorize context mutation.

## Runtime Flow

```text
approved sources
  -> Knowledge Artifact Compiler
  -> typed cited task artifact
  -> Knowledge Request Contract
  -> NexusBrain / AO / Expert / teacher council context
  -> Control Panel replay and blackbox evidence
```

## Current Code-Backed Consumers

As of the first v0 implementation pass, KAC artifacts are consumed only by explicit artifact refs. The consuming subsystem receives the ref and a non-mutating compiled knowledge context block; it does not receive permission to rewrite prompts, mutate model weights, promote nodes, or bypass raw-data gates.

Current consumers:

- DatasetForge records `knowledge_artifact_refs` on manifests, examples, eval cases, and dataset summaries.
- HiveModelGrowthEngine records KAC refs in growth cycles, material scout manifests, curriculum, teacher council manifests, accepted cases, dataset manifests, student birth records, model genomes, and training context.
- Production Spine teacher council review records KAC refs as `compiled_knowledge_context`.
- Recursive Dreaming records KAC refs in dream scenarios, dream candidates, growth seeds, memory/experiment lineage, and governance events.
- Deep Replay bundles index KAC refs as ref-only `knowledge_artifact_ref` records for developer drilldown and trust scanning.

DatasetForge, HiveModelGrowthEngine, Production Spine teacher-council review, and Recursive Dreaming must all record:

```text
requires_krc_runtime_context_allowed: true
blocks_stale_or_quarantined_context: true
blocks_raw_retrieval_fallback_context: true
runtime_gate_source: KnowledgeArtifactCompiler.query
```

The required boundary is:

```text
KAC artifact -> explicit ref -> consumer lineage/context -> sandbox/eval/replay
```

not:

```text
KAC artifact -> automatic training data -> direct mutation
```

## Promotion Rule

This layer remains candidate until local evals prove citation coverage, deterministic hashing, freshness invalidation, permission filtering, conflict handling, Control Panel replay, and compiled-vs-raw value. Promotion requires governance approval and must preserve raw retrieval fallback.
