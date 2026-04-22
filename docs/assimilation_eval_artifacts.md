# Assimilation Eval Artifacts

## Purpose
EvalsAO remains external. This document makes the new assimilation-era artifact bundles machine-readable and operator-readable without reducing the system to raw JSON dumps.

## Directly Consumable Artifact Families
- retrieval rerank evidence bundles
- gateway policy and approval provenance bundles
- edge vision benchmark artifacts
- AITune validation artifacts
- TriAttention comparative baseline artifacts

## Current Convergence Additions
- `retrieval_rerank_evidence.json`
- `retrieval_rerank_review.json`
- `retrieval_rerank_review.md`
- `assimilation_artifacts.json`
- `assimilation_scorecards.json`
- AITune execution-plan, execution-plan markdown, runner, benchmark, and tuned-artifact references inside validation bundles
- TriAttention comparative-summary, runtime-anchor, and runtime-anchor-quality references inside comparative bundles

## Operator Readability
Artifacts should expose:
- stable IDs
- benchmark family and threshold-set references
- provider provenance
- pass/fail summary
- artifact paths for rollback-ready inspection
- review summaries for retrieval-policy promotion evidence
- candidate-shift counts and top-shift previews for retrieval-policy promotion evidence
- supported-lane readiness and skip-safe reasons for AITune
- supported-host execution-plan markdown paths and runner artifact references for AITune
- comparative baseline provenance for TriAttention
- runtime-anchor measurement quality for TriAttention
- report IDs, evidence IDs, and threshold references that wrapper/ops/visualizer surfaces can display directly

## Promotion Discipline
These artifacts are additive evidence only. They do not bypass:
- EvalsAO
- governed promotion review
- rollback readiness
