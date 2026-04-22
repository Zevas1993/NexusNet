# Assimilation Convergence Run Log

## Iteration 0: Scope And Gap Map
- Accepted the 2026 assimilation operationalization run as baseline infrastructure.
- Audited retrieval rerank, promotion, EvalsAO, AITune validation, TriAttention harness, wrapper surface, and visualizer overlay seams.
- Identified the highest-leverage convergence sequence:
  1. retrieval-policy promotion traceability for rerank evidence
  2. AITune supported-lane validation readiness
  3. TriAttention comparative long-context baselines
  4. wrapper, ops, and visualizer inspection hardening
  5. targeted docs and validation

## Planned Validation
- targeted convergence tests first
- wrapper surface and promotion regressions next
- visualizer regressions next
- broader suite after the main workstreams land

## Known Risks
- Unrelated dirty-tree drift remains outside this task.
- Current Windows plus Python 3.13 lane must remain skip-safe for AITune.

## Iteration 1: Retrieval Promotion Evidence
- Added retrieval rerank benchmark-family and threshold-set identity to operational scorecards.
- Added explicit retrieval rerank evidence bundles and artifact persistence for `retrieval-policy` promotion candidates.
- Wired retrieval rerank evidence into promotion summary, wrapper inspection, ops inspection, visualizer overlay state, and candidate evaluation artifacts.

## Iteration 2: AITune Supported-Lane Readiness
- Added a supported-lane matrix and validation runner for Linux plus NVIDIA hosts.
- Preserved graceful skip behavior on unsupported Windows plus Python 3.13 environments.
- Added runner and validation artifacts plus supported-lane readiness reporting.

## Iteration 3: TriAttention Comparative Evidence
- Replaced isolated TriAttention-only estimates with comparative long-context baselines against accepted baseline paths.
- Added comparative scorecards and comparative summary artifacts.
- Surfaced comparative scorecard visibility through wrapper, ops, and visualizer inspection.

## Validation Progress
- `python -m py_compile ...` on touched convergence files passed.
- `node --check ui\\visualizer\\app.js` passed.
- `python -m pytest tests\\test_assimilation_convergence.py -q` passed.
- `python -m pytest tests\\test_assimilation_operationalization.py tests\\test_research_assimilation.py tests\\test_aitune_adapter.py tests\\test_nexusnet_visualizer.py tests\\test_nexusnet_wrapper_surface.py tests\\test_nexusnet_promotion_loop.py -q` passed.
- `python -m pytest tests\\test_assimilation_convergence.py tests\\test_assimilation_operationalization.py tests\\test_research_assimilation.py tests\\test_aitune_adapter.py tests\\test_nexusnet_visualizer.py tests\\test_nexusnet_wrapper_surface.py tests\\test_nexusnet_promotion_loop.py -q` passed.
- `python -m pytest -q` passed after rerunning with a longer timeout.

## Failures Fixed
- Replaced the default `python` test invocation with the repo’s working Python 3.13 interpreter because the PATH interpreter lacked `pytest`.
- Fixed a circular-import regression by changing `nexusnet.promotions.__init__` to lazy exports.
- Reran the broader regression set and the full suite with longer timeouts after both initial passes timed out while still progressing.

## Remaining Gaps
- AITune supported-lane execution remains readiness-only on the current unsupported Windows plus Python 3.13 host.
- TriAttention still relies on comparative synthetic baselines until additional accepted long-context provider hooks are available in-repo.
