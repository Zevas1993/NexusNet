# KV Cache Runtime Efficiency Spec

Status: P1 online assimilation target. Research-only until local runtime compatibility, hardware fit, and privacy boundaries are inspected.

## Source Evidence

- LMCache docs: https://docs.lmcache.ai/
- LMCache repository: https://github.com/LMCache/LMCache
- LMCache paper: https://arxiv.org/abs/2510.09665
- vLLM disaggregated prefill docs: https://docs.vllm.ai/en/latest/features/disagg_prefill/
- SGLang project docs: https://docs.sglang.ai/
- OSCAR project page: https://oscar-quantize.github.io/
- OSCAR paper: https://arxiv.org/abs/2605.17757
- Source status: official docs, public repositories, and primary paper page.
- Reverified: 2026-05-31 via `docs/assimilation/ASSIMILATION_TARGET_SOURCE_REVERIFICATION_2026-05-31.md`.

## Finding

LLM serving is increasingly treating KV cache as a reusable runtime asset. LMCache emphasizes prefill-once and reuse-across-text semantics, while vLLM and SGLang expose related serving patterns such as prefix caching, disaggregated prefill, structured outputs, and cache-aware scheduling. The 2026-05-31 reverify adds OSCAR as a specific INT2 KV-cache candidate: an attention-aware, offline-calibrated rotation and clipping method with BF16 sink/recent protection and an SGLang/Triton serving path.

## NexusNet Assimilation Target

Create a Runtime Cache Planner for NexusNet. Long-context RAG, multi-turn sessions, and repeated canonical context blocks should avoid paying prefill cost repeatedly when a local or server runtime can safely reuse cache state.

## Proposed NexusNet Components

- `ContextReusePassport`: source block, digest, privacy class, model, tokenizer, quantization, runtime, and expiration.
- `KVCachePolicy`: allow, deny, encrypt, persist, spill, or discard cache segments by data class.
- `PrefillReusePlanner`: identifies reusable system prompts, canon chunks, tool schemas, user-approved memory, and RAG contexts.
- `RuntimeCacheMetrics`: TTFT, prefill tokens avoided, cache hit rate, memory pressure, eviction, and privacy denials.
- `CacheCompatibilityMatrix`: model/runtime/tokenizer/quantization compatibility and invalidation rules.

## Promotion Gates

- Never persist private or secret-bearing KV cache without explicit policy.
- Invalidate cache on model, tokenizer, prompt, safety policy, or source-content changes.
- Measure latency and memory wins on NexusNet workloads before adoption.
- For OSCAR-like INT2 cache paths, measure correctness under compression and preserve full-precision protection for sink/recent tokens before any route can use it.
- Keep local-device and server-runtime policies separate.

## Risks

- KV caches can carry sensitive information even when plain text is not logged.
- Runtime compatibility changes quickly across vLLM, SGLang, llama.cpp, MNN, ExecuTorch, and server stacks.
- Cache hits can create correctness bugs if stale context is reused after source changes.
