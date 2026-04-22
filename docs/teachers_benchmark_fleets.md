# NexusNet Teacher Benchmark Fleets

Status: `LOCKED CANON`

Date: `2026-04-12`

## Purpose
Benchmark fleets extend teacher governance from subject-local repeated runs to fleet-scoped evidence. They let NexusNet judge teacher/native behavior across expert capsules, teacher pairs, budget classes, hardware classes, and governance windows instead of relying on one subject’s local history alone.

## Canonical Files
- catalog: `nexusnet/teachers/teacher_benchmark_fleets.yaml`
- registry: `nexusnet/teachers/fleet_registry.py`
- window registry: `nexusnet/teachers/fleet_windows.py`
- analyzer: `nexusnet/teachers/fleets.py`

## Fleet Concepts
The current fleet catalog includes:
- `local_reasoning_fleet`
- `coding_agent_fleet`
- `multimodal_fleet`
- `low_hardware_fleet`
- `edge_constrained_fleet`
- `long_context_fleet`
- `takeover_validation_fleet`
- `safety_sensitive_fleet`

## Governance Dimensions
Each fleet may constrain or report across:
- expert capsule / subject
- teacher pair
- budget class
- output form
- risk tier
- locality
- hardware class / device profile
- dream-derived vs live-derived lineage
- threshold set id and version

## Governance Windows
- `short`
  Operator-facing recent window for rapid checks
- `medium`
  Primary promotion and replacement review window
- `long`
  Long-horizon regression and replacement-confidence window

## Runtime Use
- Promotions can now reference fleet summaries through the cohort gate.
- Foundry/native takeover now records fleet summaries for takeover validation.
- Wrapper and ops surfaces expose fleet IDs, windows, threshold versions, and artifact references.

## Canon Rule
Fleets extend the accepted teacher system. They do not replace:
- the historical/live registry split
- the 19-core live pair map
- Critique arbitration
- bounded LFM2 lanes
