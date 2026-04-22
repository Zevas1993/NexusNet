# Live Validation Run Log

## Iteration 0: Scope And Gap Map
- Accepted the 2026 assimilation convergence run as baseline infrastructure.
- Audited AITune validation/runner code, retrieval rerank promotion evidence, TriAttention comparative harness, wrapper snapshot seams, visualizer overlay seams, and assimilation status endpoints.
- Identified the highest-leverage execution order:
  1. AITune supported-lane runner and live-validation workflow depth
  2. retrieval-policy promotion review/reporting depth
  3. TriAttention comparative evidence quality
  4. cross-cutting wrapper, ops, and visualizer inspection hardening
  5. targeted docs and validation

## Planned Validation
- targeted live-validation tests first
- convergence and operationalization regressions next
- visualizer and wrapper regressions next
- broader suite after the main workstreams land

## Known Risks
- Current Windows plus Python 3.13 host must remain skip-safe for AITune.
- The repo already has unrelated dirty-tree drift outside this task.

## Iteration 1: AITune Supported-Lane Runner
- Added explicit health-report and execution-plan artifacts for AITune validation.
- Added a dry-run and simulated supported-lane path without breaking unsupported hosts.
- Added a CLI runner entry point and enriched provider summaries with latest validation and health reporting.

## Iteration 2: Retrieval Promotion Review Depth
- Added readable retrieval rerank review reports and markdown artifacts.
- Surfaced rerank review report IDs, threshold-set refs, and evaluator artifact linkage through promotion, wrapper, ops, and visualizer surfaces.
- Extended EvalsAO artifacts so retrieval rerank reviews are not operator-hostile raw JSON only.

## Iteration 3: TriAttention Comparative Evidence
- Added baseline registry provenance for accepted in-repo long-context paths.
- Added comparative summary artifacts and head-to-head averages against accepted baselines.
- Surfaced comparative report IDs and baseline counts through wrapper, ops, and visualizer inspection.

## Validation Progress
- `python -m py_compile ...` on touched live-validation files passed.
- `node --check ui\\visualizer\\app.js` passed.
- `python -m pytest tests\\test_live_validation_productionization.py -q` passed.
- `python -m pytest tests\\test_live_validation_productionization.py tests\\test_assimilation_convergence.py -q` passed.
- `python -m pytest tests\\test_live_validation_productionization.py tests\\test_assimilation_convergence.py tests\\test_assimilation_operationalization.py tests\\test_research_assimilation.py tests\\test_aitune_adapter.py tests\\test_nexusnet_visualizer.py tests\\test_nexusnet_wrapper_surface.py tests\\test_nexusnet_promotion_loop.py -q` passed.
- `python -m pytest -q` passed.

## Failures Fixed
- The first broader regression run timed out at the shell limit while still making progress; reran with a longer timeout and completed green.

## Remaining Gaps
- Live AITune execution still requires a real supported Linux plus NVIDIA host to move from dry-run readiness into actual benchmark evidence.
- TriAttention still uses estimated provider curves; stronger evidence will need additional accepted in-repo long-context runtime hooks as they land.
