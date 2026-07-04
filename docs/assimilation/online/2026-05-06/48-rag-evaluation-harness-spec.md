# RAG Evaluation Harness Spec

Status: P1 online assimilation target. Research-only until existing NexusNet KAC/RAG paths and datasets are mapped.

## Source Evidence

- Ragas docs: https://docs.ragas.io/
- Ragas paper: https://arxiv.org/abs/2309.15217
- TruLens docs: https://www.trulens.org/
- DeepEval docs: https://docs.confident-ai.com/
- ARES paper: https://arxiv.org/abs/2311.09476
- ARES repository: https://github.com/stanford-futuredata/ARES
- Source status: official docs, public repositories, and primary paper pages.

## Finding

RAG evaluation frameworks converge on separate measurements for retrieval relevance, context precision, faithfulness, answer relevance, hallucination, citation quality, and task success. The useful NexusNet lesson is to evaluate retrieval and generation independently before treating a response as grounded.

## NexusNet Assimilation Target

Add a RAG/KAC evaluation harness that scores memory and document retrieval before synthesis. The system should detect wrong-source retrieval, unsupported claims, missing citations, stale context, and no-answer cases.

## Proposed NexusNet Components

- `RagEvalCase`: query, allowed corpus, expected evidence, answer constraints, and no-answer flag.
- `RetrievalEvidenceTrace`: retrieved chunk IDs, source class, rank, score, freshness, and rejected candidates.
- `FaithfulnessScorer`: checks whether answer claims are supported by retrieved evidence.
- `CitationVerifier`: validates source links, page or chunk anchors, and quote boundaries.
- `KacRegressionPack`: recurring tests for memory, docs, chat canon, browser exports, and repo knowledge.

## Promotion Gates

- Do not score final answer quality without scoring retrieval quality.
- Include adversarial, stale, contradictory, and no-answer cases.
- Require source-status separation for canon, refs-only candidates, memory, and external web.
- Keep model-judged RAG scores calibrated against deterministic checks.

## Risks

- RAG metrics can disagree or overfit to one evaluation framework.
- Model-graded faithfulness can miss subtle unsupported claims.
- Private corpora need redaction and local-only evaluation defaults.
