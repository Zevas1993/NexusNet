# Speculative Decoding Runtime Stack Spec

Status: P2 online assimilation target. Research-only until measured on NexusNet local/open model workloads.

## Source Evidence

- vLLM speculative decoding docs: https://docs.vllm.ai/en/v0.20.1/features/speculative_decoding/
- Medusa paper: https://arxiv.org/abs/2401.10774
- Medusa repository: https://github.com/FasterDecoding/Medusa
- EAGLE paper: https://arxiv.org/abs/2401.15077
- EAGLE 3.1 vLLM update: https://vllm.ai/blog/2026-05-26-eagle-3-1
- SpecInfer paper: https://arxiv.org/abs/2305.09781
- Source status: official runtime docs, public repository, and primary paper pages.
- Reverified: 2026-05-31 via `docs/assimilation/ASSIMILATION_TARGET_SOURCE_REVERIFICATION_2026-05-31.md`.

## Finding

Speculative decoding is a runtime lever for faster generation without changing final distribution when implemented correctly. vLLM's current docs expose several practical methods, from n-gram and suffix decoding to model-based EAGLE and draft-model approaches. The 2026-05-31 reverify adds EAGLE 3.1 as a current vLLM-integrated runtime candidate; it is still an acceleration layer, not a reasoning or governance layer.

## NexusNet Assimilation Target

Add speculative decoding as a runtime certification dimension, not a blanket toggle. NexusNet should detect which models, prompts, and workloads benefit, then expose safe route-level configuration.

## Proposed NexusNet Components

- `SpecDecodeProfile`: target model, draft model or method, speculative tokens, acceptance rate, latency, memory, and quality.
- `RuntimeAccelerationPolicy`: allow, deny, or benchmark-required by model route and workload class.
- `SpecDecodeRegression`: checks output equivalence, latency, memory, and tool-call formatting.
- `DraftModelInventory`: source, license, compatibility, checksum, and hardware fit.
- `OperatorRuntimePanel`: shows acceleration method, measured benefit, and fallback path.

## Promotion Gates

- Measure on NexusNet prompts and hardware before enabling.
- Disable if structured outputs, tool calls, or safety behavior regress.
- Track draft model license and provenance.
- For EAGLE 3.1, require route-specific acceptance-length, throughput, and structured-output regression evidence before enabling.
- Keep per-route fallback to non-speculative decoding.

## Risks

- Speedups are workload and hardware dependent.
- Draft model setup can consume memory that local devices do not have.
- Runtime support changes quickly across vLLM, SGLang, TensorRT-LLM, llama.cpp, and edge stacks.
