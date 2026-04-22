# Retrieval Rerank Promotion Traceability

## Purpose
This document operationalizes retrieval rerank evidence as a promotion-grade traceability bundle for `retrieval-policy` candidates.

## Canon
- Retrieval remains explicitly two-stage:
  - stage 1 retrieve and fuse
  - stage 2 rerank top-k only
- The reranker never becomes the first-stage retriever.
- Retrieval-policy candidates remain subordinate to NexusNet-owned promotion and rollback discipline.

## Evidence Bundle
`retrieval-rerank-evidence-bundle` records:
- stage-1 top-k candidate snapshot
- stage-2 top-k after rerank
- rerank score
- reranker provider
- latency delta
- relevance delta
- groundedness delta
- provenance delta
- benchmark family used
- threshold set used
- scorecard linkage
- evaluator artifact linkage

## Promotion Integration
- Retrieval-policy candidates now carry `traceability.retrieval_rerank_evidence`.
- Retrieval-policy candidates also carry a readable rerank review report with:
  - report ID
  - stable review ID
  - review headline
  - human-readable review summary
  - review badges
  - candidate-shift summary
  - operator summary
  - stage-1 vs stage-2 candidate previews
  - benchmark family and threshold-set identity
  - evaluator artifact summary
- Wrapper and ops surfaces expose read-only `promotion_evidence` summaries.
- Visualizer overlay exposes the active rerank promotion evidence reference without changing the visualizer’s read-only role.

## EvalsAO Linkage
- Candidate evaluation persists:
  - `retrieval_rerank_evidence.json`
  - `retrieval_rerank_review.json`
  - `retrieval_rerank_review.md`
  - `assimilation_artifacts.json`
  - `assimilation_scorecards.json`
- Retrieval-policy candidates fail the retrieval-specific evaluation gate if the rerank evidence bundle is missing, lacks a reranker provider, or references a failing scorecard.

## Operator Review
- `report_id`, `scorecard_id`, `benchmark_family_id`, and `threshold_set_id` are now surfaced together.
- Wrapper and visualizer surfaces show rerank review IDs, review headlines, human summaries, candidate-shift counts, threshold versions, scorecard pass state, and linked evaluator artifacts.
- Ops surfaces expose:
  - a dedicated promotion-review listing endpoint
  - a stable review-detail endpoint per `review_report_id`
  - human-readable markdown review artifacts in addition to JSON payloads
