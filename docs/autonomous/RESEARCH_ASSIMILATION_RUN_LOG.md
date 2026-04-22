# Research Assimilation Run Log

## Iteration 1: Audit And Scope
- Confirmed retrieval should land first through `nexus/retrieval/service.py` and `nexus/operator/kernel.py`.
- Confirmed OpenClaw-style patterns should extend existing NexusNet agent/governance/wrapper seams rather than create a new control plane.
- Confirmed LFM2.5-VL-450M edge lane is mostly greenfield and can remain additive to the teacher/runtime baseline.
- Confirmed AITune already exists and should be extended, not recreated.

## Iteration 2: Planned Ship-Now Order
- Task hygiene and source-backed playbook docs.
- Two-stage retrieval reranking with persisted provenance and ops visibility.
- Gateway/skills/approvals/policy lane with read-only inspection.
- Explicit LFM2.5-VL-450M edge vision lane.
- Bounded AITune extensions.

## Iteration 3: Playbook And Ship-Now Core Landed
- Added the 2026 assimilation playbook and company-pattern map with source-backed entries for reranking, OpenClaw patterns, LFM2.5-VL-450M, AITune, SkillClaw, MiniMax M2.7, and TriAttention.
- Landed two-stage retrieval reranking under `nexus/retrieval/service.py` with stage-1 fusion over lexical/graph/memory/temporal sources and stage-2 cross-encoder reranking over top-k only.
- Persisted rerank provenance into retrieval traces, operator trace steps, EvalsAO artifacts, and wrapper inspection surfaces.

## Iteration 4: Secure Runtime And Edge Vision Assimilation
- Added a NexusNet-owned local gateway pattern with skill packages, precedence, allowlists, approvals, ask fallback, and deny-by-default on ambiguous execution binding.
- Exposed read-only gateway state through wrapper/ops surfaces without introducing a second control plane.
- Added the explicit LFM2.5-VL-450M edge vision lane with safe-mode/low-power teacher candidacy, grounding schema, function-calling metadata, multilingual capability metadata, and latency profiles.
- Extended the existing AITune baseline with target-registry visibility, repo fit/avoid audit state, and richer inspection metadata rather than recreating the provider.

## Iteration 5: Prototype And Research Scaffolds
- Added governed skill-evolution scaffolds for trajectory aggregation, recurring-pattern summaries, and refinement proposals routed toward review/promotion/rollback.
- Added MiniMax M2.7 teacher/reference and agent-harness scaffolding without making it a runtime default.
- Added TriAttention provider-registry and benchmark scaffolding as a research-only, feature-flagged lane.

## Iteration 6: Regression Fixes And Hardening
- Fixed a package import cycle by keeping `nexusnet.__init__` lazy for `NexusBrain`.
- Fixed wrapper-surface gateway inspection by restoring session provenance lookup inside snapshot generation.
- Fixed promotion-evaluation artifact persistence so optional retrieval-rerank artifacts are only recorded when present.
- Normalized edge vision provider summaries to expose multilingual `languages` metadata directly.
- Added targeted tests for deny-by-default ambiguity handling, explicit LFM2.5-VL-450M metadata, AITune target-registry visibility, and research/skill-governance default states.

## Validation Notes
- `python -m py_compile` passed for the touched runtime, retrieval, gateway, eval, promotion, and vision files.
- `python -m pytest tests\test_research_assimilation.py -q` passed after regression fixes.
- `python -m pytest tests\test_research_assimilation.py tests\test_aitune_adapter.py tests\test_nexusnet_visualizer.py tests\test_nexusnet_wrapper_surface.py tests\test_nexusnet_promotion_loop.py -q` passed.
- Full regression suite passed: `81 passed, 1 skipped`.

## Failures Fixed
- Circular import at `nexusnet.__init__` during retrieval-rerank integration.
- `WrapperSurfaceService.snapshot()` missing `provenance` local when exposing gateway state.
- `PromotionEvaluationRecord.artifacts` receiving a `None` `retrieval_rerank` path.
- Edge-vision summary not surfacing a normalized multilingual language key for inspection/test use.
- One full-suite pytest run timed out at the shell limit while still progressing; rerun with a longer timeout completed green.

## Blockers
- No real blockers.
- Live AITune invocation remains intentionally gated out on unsupported Windows / Python 3.13 / non-NVIDIA paths.

## Next Highest-Leverage Tasks
- Bind a real Linux + supported-Python + NVIDIA validation lane for live AITune execution and benchmark artifact verification.
- Expand retrieval rerank evaluation into broader relevance corpora and wrapper/visual inspection overlays if retrieval observability needs to be deeper.
- Replace placeholder/community-source references for MiniMax with stronger primary-source references if a canonical official benchmark/runtime source becomes available.
