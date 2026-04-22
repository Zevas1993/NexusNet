# TriAttention Research Harness

## Canon
- TriAttention remains feature-flagged and research-only by default.
- It does not replace current long-context paths without benchmark proof.

## Operational Additions
- Provider estimates for context-window scaling
- Benchmark artifacts under `runtime/artifacts/research/attention/`
- Measured summary over:
  - KV memory
  - throughput
  - stability
  - reasoning quality
  - long-context regression

## Inspection Surface
- `/ops/brain/attention-providers`
- `/ops/brain/attention-providers/benchmark`
