# TriAttention Comparative Baselines

## Purpose
TriAttention remains research-track. This harness strengthens evidence by comparing TriAttention against accepted long-context baseline paths instead of relying on isolated scores.

## Comparative Baselines
- `accepted-dense-kv`
- `accepted-windowed-hybrid`

Each baseline now carries in-repo path provenance so the comparison is not only synthetic:
- `accepted-dense-kv`
  - `core/engines/transformers_engine.py`
  - `runtime/config/inference.yaml`
- `accepted-windowed-hybrid`
  - `nexus/retrieval/service.py`
  - `runtime/config/retrieval.yaml`

## Compared Metrics
- KV memory use
- throughput
- latency
- stability
- reasoning quality
- long-context regression

## Comparative Scorecard
The `triattention-comparative-scorecard` records:
- average KV memory ratio
- average throughput ratio
- average latency ratio
- average stability delta
- average reasoning delta
- average long-context regression delta
- threshold-set outcome
- comparative findings
- baseline registry provenance
- report ID

## Comparative Summary
- The benchmark now writes a comparative summary artifact with:
  - head-to-head averages per accepted baseline
  - baseline registry provenance
  - runtime anchor registry
  - runtime anchor summary
  - report IDs and scorecard linkage

## Runtime-Aware Anchors
Comparative evidence is no longer limited to static synthetic baselines. Where in-repo runtime profiles are available, the harness also records accepted-provider anchors for:
- `transformers`
- `llama.cpp`
- `vllm`
- `onnx-genai`
- retrieval-windowed hybrid paths when graph, memory, or temporal retrieval windows are enabled

These anchors remain comparative evidence only. They do not change the accepted long-context default paths.

## Runtime-Anchor Quality
- Comparative summaries now record:
  - runtime-anchor quality summary
  - available anchor count
  - latency-anchored runtime baseline count
  - measurement-mode counts
  - source health per accepted runtime anchor
- This makes it clear which comparisons were anchored to observed runtime-profile signals and which remain heuristic.

## Canon
- TriAttention stays feature-flagged and research-only by default.
- Comparative evidence is required before any future promotion consideration.
- Existing accepted long-context paths remain authoritative until TriAttention proves itself inside NexusNet benchmarks.
