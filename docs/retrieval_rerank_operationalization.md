# Retrieval Rerank Operationalization

## Canon
- Stage 1 remains cheap retrieval and fusion.
- Stage 2 remains reranking over top-k only.
- The reranker does not become first-stage retrieval.

## Operational Additions
- Config-backed benchmark corpora and query families in `runtime/config/retrieval.yaml`
- Threshold evaluation for pass rate, latency delta, relevance delta, groundedness delta, provenance delta, and provider coverage
- Scorecard artifacts under `runtime/artifacts/retrieval/rerank-operational/`
- Wrapper and ops visibility for recent rerank candidate lists and latest scorecards
- EvalsAO linkage through `retrieval_rerank_scorecard` artifacts

## Persisted Metrics
- top-k before rerank
- top-k after rerank
- reranker provider
- rerank score
- latency delta
- relevance delta
- groundedness delta
- provenance delta

## Inspection Surfaces
- `/ops/brain/retrieval/rerank-benchmark`
- `/ops/brain/retrieval/rerank-scorecard`
- `/ops/brain/wrapper-surface`
- `/ops/brain/evals/report`
