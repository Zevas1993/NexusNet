# NexusNet Teacher System Validation Report

Status: `LOCKED CANON`

Date: `2026-04-12`

## Scope
This report validates the accepted teacher-system baseline before and after operational wiring into curriculum, foundry, promotion, evaluation, and wrapper traceability flows.

The validated baseline preserves:

- historical teacher canon as a separate immutable layer
- live `v2026` teacher routing as a separate operational layer
- best-ensemble-per-role historical semantics
- the authoritative 19-core live roster without auxiliary renumbering
- Critique Expert arbitration
- bounded LFM2 usage
- shadow-only teacher retirement/replacement scaffolding

## Verification Results

### 1. Historical Registry Integrity
- `PASS`: the historical central mentor ensemble remains exactly `Mixtral-8x7B`, `Yi-1.5-9B`, `Qwen-0.5B-MoE`, `LLaMA-3-8B`.
- `PASS`: all historical expert-role ensembles remain exact and were not replaced with newer live models.
- `PASS`: historical principles remain `best_ensemble_per_role: true`, `one_teacher_per_role: false`, `teachers_discarded_after_surpass: true`.
- `PASS`: the historical layer still routes as `best-ensemble-per-role`, not as primary/secondary-only pairs.

### 2. Live v2026 Registry Integrity
- `PASS`: all 19 core expert capsules remain present.
- `PASS`: each live expert preserves the expected primary teacher, secondary teacher, critique arbiter, optional efficiency coach, locality preference, and historical anchor reference.
- `PASS`: `Toolsmith`, `Security`, `Memory Weaver`, and `Router` remain the bounded LFM2 lanes.
- `PASS`: `Curriculum Architect` remains auxiliary with status `STRONG ACCEPTED DIRECTION`.
- `PASS`: the authoritative 19-core roster is not renumbered by auxiliary paths.

### 3. Routing Correctness
- `PASS`: routing can select from either `historical` or `v2026_live`.
- `PASS`: routing honors domain, budget class, output form, risk tier, locality, modality, coding/tool need, thinking mode hints, and hardware constraints.
- `PASS`: Critique arbitration is triggered on high-risk or disagreement-sensitive paths.
- `PASS`: LFM2 remains bounded and non-primary.

### 4. Provenance Correctness
- `PASS`: traces and attached-teacher provenance preserve registry layer, selected roles, arbitration result, benchmark family, dream/live lineage, and native-takeover linkage.
- `PASS`: curriculum stage records now persist teacher-flow evidence, disagreement artifacts, and dream/evaluation lineage.
- `PASS`: native-takeover promotion candidates now carry teacher evidence in `traceability`.
- `PASS`: threshold-set references are now preserved end-to-end for scored teacher flows.

### 5. Retirement Shadow Correctness
- `PASS`: no historical or live registry entries are deleted during shadow retirement evaluation.
- `PASS`: historical canon remains immutable.
- `PASS`: live teachers only enter shadow replacement logic when native evidence crosses the configured threshold, and they still require evaluator/governance/rollback gates.

## Passive-Only Audit

### Previously Passive-Only
- `nexusnet/curriculum/engine.py`
  Teacher regimens existed as YAML only; curriculum execution did not use primary/secondary/critique stages.
- `nexusnet/foundry/benchmarks.py`
  Foundry benchmarks only tracked coarse `dependency_ratio` and `native_generation`.
- `nexusnet/promotions/service.py`
  Promotion evaluation did not pass teacher evidence into EvalsAO.
- `nexusnet/evals/service.py`
  EvalsAO was still mostly a recent-trace gate with weak teacher awareness.
- `nexusnet/ui_surface/surface.py`
  Wrapper visibility exposed teacher metadata, but not disagreement evidence or takeover-linked teacher evidence.

### Operationalized In This Pass
- curriculum stage execution now uses the teacher regimens directly
- dual-teacher disagreement artifacts now feed foundry and native-takeover evidence
- promotion candidates can now carry teacher evidence through `traceability`
- EvalsAO now runs teacher-aware scenario checks
- wrapper/ops surfaces now expose teacher evidence, recent teacher traces, and takeover-linked teacher evidence
- benchmark families and threshold sets are now first-class teacher artifacts rather than passive metadata
- retirement shadow status is now persisted as inspectable state

## Hardening Additions

### Benchmark and Threshold Artifacts
- `PASS`: each expert capsule now resolves benchmark families from `teacher_benchmark_families.yaml`.
- `PASS`: threshold resolution is versioned and referenceable through `teacher-v2026-r1`.
- `PASS`: auxiliary Curriculum Architect remains auxiliary in the benchmark catalog.

### Promotion / Foundry Evidence
- `PASS`: teacher evidence bundles are persisted and linkable from promotion candidates.
- `PASS`: takeover scorecards are persisted and exposed through foundry status.
- `PASS`: retirement shadow records are persisted without deleting live or historical teachers.

### Schema / Trend Governance
- `PASS`: teacher hardening records now carry explicit schema family/version compatibility metadata.
- `PASS`: a manifest-backed schema compatibility path now exists without breaking startup auto-create behavior.
- `PASS`: repeated-run teacher trend scorecards now gate teacher-linked promotion readiness.
- `PASS`: repeated-run takeover trend reports now gate native takeover and retirement shadow readiness.

## Tests Run

- `tests/test_teacher_registry.py`
- `tests/test_teacher_routing.py`
- `tests/test_teacher_provenance.py`
- `tests/test_teacher_arbitration.py`
- `tests/test_teacher_retirement_shadow.py`
- `tests/test_teacher_operationalization.py`
- `tests/test_teacher_hardening.py`
- `tests/test_teacher_trends.py`
- `tests/test_nexusnet_brain.py`
- `tests/test_nexusnet_promotion_loop.py`
- `tests/test_nexusnet_wrapper_surface.py`
- `tests/test_nexusnet_assimilation.py`

## Validation Results
- Teacher-focused suite with trend governance: `21 passed`
- Broader regression slice: `13 passed`
- Full suite: `59 passed, 1 skipped`

## Canon Notes
- Historical canon remains distinct from live operations.
- The teacher system is still a bootstrapping and internalization layer, not the final identity of NexusNet.
- AOs remain open-ended and are not frozen by this work.
- Native takeover remains shadow-gated and teacher-evidence-backed.
- Benchmark-scored teacher evidence now forms part of the promotion-grade evidence path instead of remaining provenance-only.
