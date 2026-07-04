# Agentic RAG Planner Spec

Status: high-priority candidate. Checked on 2026-05-06.

Video:

- `YTDown_YouTube_RAG-s-Evolution-From-Simple-Retrieval-to_Media_JB2P5Gk23VI_001_1080p.mp4`

Evidence pack:

- `<LOCAL_VIDEO_WATCH_OUTPUT>/nexusnet-assimilation-batch-20260506/04-rag-evolution/...`
- Watcher outputs: `WATCH_REPORT.md`, `transcript/transcript.txt`, `manifest.json`, `contact_sheets/sheet_001.jpg`

## Target Pattern

The useful target is an explicit retrieval planner that decides what to retrieve, when to retrieve, how to combine retrieval modes, and when to refuse unsupported claims.

This is stronger than "add RAG." NexusNet already has retrieval, GraphRAG, reranking, memory quality, and KAC surfaces. The improvement target is the decision layer above them.

## External Confirmation

- The original RAG paper frames retrieval as a way to combine parametric generation with non-parametric memory and provenance: https://arxiv.org/abs/2005.11401
- LangGraph's agentic RAG guide shows an agent deciding whether to retrieve, grading documents, rewriting questions, and generating answers: https://docs.langchain.com/oss/python/langgraph/agentic-rag
- A 2026 Agentic RAG SoK highlights multi-step reasoning, dynamic memory, iterative retrieval, and reliability risks such as hallucination propagation and retrieval misalignment: https://arxiv.org/abs/2603.07379

## NexusNet Use

Build a `retrieval-planner` candidate over existing surfaces:

- `nexus/retrieval/service.py` for baseline retrieval.
- `nexusnet/retrieval/graphrag/` for graph-aware retrieval and provenance.
- `nexusnet/retrieval/rerank/` for second-stage scoring and promotion evidence.
- `nexusnet/memory/quality_ledger.py` for source and claim quality.
- `nexusnet/knowledge/compiler.py` for refs-only knowledge artifacts.
- `nexusnet/security/artifact_trust.py` for blocked/private refs and trust scan results.
- `tests/test_assimilation_convergence.py` and `tests/test_assimilation_operationalization.py` for retrieval evidence/visibility behavior.

## Spec Requirements

- Retrieval plan schema: user goal, query decomposition, retrieval modes, source classes, cost/latency budget, stop condition, and evidence threshold.
- Hybrid retrieval: lexical precision, semantic recall, graph neighborhood, temporal recency, and rerank fusion as explicit choices.
- Claim ledger: every generated claim maps to supporting refs, contradiction refs, source trust state, and confidence.
- Critic loop: judge whether retrieved evidence actually answers the question; rewrite or abstain when it does not.
- Poisoning controls: private-source blocks, stale-source warnings, memory-quality downgrade, and contradiction detection.

## Refusals

- Do not let retrieved snippets become truth by proximity.
- Do not hide which retrieval mode supplied a claim.
- Do not increase retrieval depth without cost/latency and source-quality receipts.
- Do not promote untrusted source refs into KAC as mutable authority.

## Acceptance Criteria

- A complex query produces a visible retrieval plan before answer generation.
- Each answer claim includes supporting source refs or an explicit unsupported/uncertain label.
- Contradictory sources cause a resolution step rather than a single-source answer.
- Control Panel exposes retrieval plan, source quality, rerank evidence, and blocked refs.

