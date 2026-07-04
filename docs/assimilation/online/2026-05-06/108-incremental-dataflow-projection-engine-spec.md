# Incremental Dataflow Projection Engine Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet Control Panel, memory, eval, and trace projections.

## Source Evidence

- Differential Dataflow book: https://timelydataflow.github.io/differential-dataflow/
- Differential Dataflow repository: https://github.com/TimelyDataflow/differential-dataflow
- Materialize incremental computation guide: https://materialize.com/guides/incremental-computation/
- Materialize arrangements docs: https://materialize.com/docs/get-started/arrangements/
- Source status: official project docs and repository.

## Finding

Differential dataflow maintains complex computations as inputs change, emitting updates rather than recomputing everything. NexusNet's traces, memory, evals, policy decisions, and Control Panel views have the same shape: many projections over changing evidence.

## NexusNet Assimilation Target

Create an incremental projection engine for NexusNet evidence. Instead of rebuilding dashboards, scorecards, memory indexes, and assurance gaps from scratch, maintain them as derived views over append-only events and patch transactions.

## Proposed NexusNet Components

- `EvidenceUpdateTuple`: artifact id, logical time, delta, and privacy class.
- `IncrementalProjection`: maintained view for health, risk, eval scores, memory lineage, or assurance gaps.
- `ProjectionArrangement`: indexed intermediate state used by multiple projections.
- `ProjectionCorrectnessCheck`: compares incremental output to full recompute on sample traces.
- `ProjectionFreshnessMeter`: tracks lag, stale dependencies, and invalidation reasons.

## Promotion Gates

- Use append-only event streams or reversible patches as projection inputs.
- Periodically compare incremental projections against full recomputation.
- Keep privacy classes through every derived view.
- Record logical time and input frontier for every projection.
- Fall back to full rebuild when projection correctness is uncertain.

## Risks

- Incremental systems can hide drift if correctness checks are weak.
- Projection state can leak private information if privacy classes are dropped.
- The architecture is not worth it until evidence volume or dashboard latency justifies it.
