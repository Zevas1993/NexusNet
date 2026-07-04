# NexusNet Quantization And Agentic Research Expansion - 2026-04-28

Purpose: finish the missing research pass around modern quantization, model formats, runtime packaging, multi-agent research, self-review, and autonomous update loops so NexusNet can build its Control Panel from complete canon and current public evidence.

Primary local sources:

- `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`
- `docs/NEXUSNET_COMPLETE_CANON_RESEARCH_REFRESH_DIFF_2026-04-28.md`
- `docs/NEXUSNET_OPEN_FIRST_RESEARCH_EXPANSION_2026-04-28.md`
- `docs/NEXUSNET_RESEARCH_CANDIDATE_DOSSIER_2026-04-28.md`
- `F:\AndroidLLMApp\deep-research-report.md`
- `F:\NexusNet\NexusNet\.worktrees\nexusnet-full-product-sweep\docs\NEXUSNET_FULL_PRODUCT_SWEEP_ROADMAP.md`

Research date: 2026-04-28.

## Executive Finding

The prior research correctly made NexusNet open-first, brain-first, graph-backed, trace-governed, eval-driven, and safety-gated. The missing layer is that quantization and agent-harness research are now product primitives, not implementation details.

NexusNet should add three first-class registries before completing the Control Panel:

1. `QuantizationFormatRegistry`: records weight, activation, KV-cache, native-low-bit, and file/container formats.
2. `RuntimeCapabilityScorecard`: maps formats to vLLM, SGLang, llama.cpp/GGUF, TensorRT-LLM, torchao, ONNX Runtime GenAI, ExecuTorch, MLC LLM, MNN, LM Studio, and Ollama.
3. `AgenticImprovementRegistry`: records multi-agent research patterns, self-review loops, harness optimization, code-agent updates, held-out eval gates, and rollback requirements.

Do not promote any quantization, format, runtime, or autonomous update path from name alone. Promote only after license, hardware fit, benchmark, safety, provenance, and rollback gates pass.

## Quantization Is Several Different Problems

NexusNet needs to separate these lanes in the Control Panel. They are often conflated in local-AI discussions.

| Lane | What is compressed | Best current examples | NexusNet status |
|---|---|---|---|
| Weight-only PTQ | Model weights, usually dequantized during matmul | GPTQ, AWQ, GGUF K-quants/I-quants, HQQ, AQLM, AutoRound, SpQR | Required registry lane for local model packages. |
| Weight+activation quantization | Weights and runtime activations | SmoothQuant W8A8, torchao int8/float8, QuaRot, SpinQuant | Required runtime scorecard lane for real speed, not just file size. |
| KV-cache quantization | Attention keys/values stored per token | KIVI, KVQuant, QuaRot/SpinQuant KV modes, TurboQuant | Required effective-context lane. Critical for long context. |
| Microscaling and hardware float formats | FP8/FP4-style storage and compute, often with block or group scaling | FP8, NF4, MXFP4, NVFP4, BOF4 | Required hardware/runtime lane; quality depends on kernel, scaling, and hardware generation. |
| Native low-bit models | Model trained around low-bit arithmetic, not post-quantized | BitNet b1.58 / bitnet.cpp | Candidate edge/local lane, separate from PTQ. |
| File/container formats | Serialized model package and metadata | safetensors, GGUF, ONNX, ExecuTorch artifacts, MLC packages, vendor compiled artifacts | Required packaging and buyer-support lane. |
| Serving/runtime quantization | Runtime accepts/executes quant format | vLLM formats, compressed-tensors, TensorRT Model Optimizer, torchao, llama.cpp, SGLang, Quark, OpenVINO | Required runtime compatibility lane. |

### Why This Matters

- A `Q4_K_M.gguf` is not the same thing as AWQ, GPTQ, FP8, or KIVI.
- TurboQuant is primarily a KV-cache/vector compression method, not a drop-in replacement for standard 4-bit model weight quantization.
- A small quantized file is not proof of speed. Some quantized formats are memory savers but still dequantize into higher precision compute paths.
- Long-context viability depends heavily on KV cache memory and cache reuse, not just model weight size.
- Buyer support depends on package format, metadata, loader maturity, and reproducible benchmark output.

## Modern Quantization Findings

### TurboQuant

Current public finding:

- Google Research's TurboQuant paper, accepted at ICLR 2026, proposes online vector quantization with near-optimal distortion. It is data-oblivious, uses random rotation plus optimal scalar quantizers, and adds a 1-bit QJL residual correction for unbiased inner-product estimation.
- The paper reports quality neutrality for KV cache quantization at about 3.5 bits per channel and marginal degradation around 2.5 bits per channel.
- The Google Research post frames the main value as extreme compression for LLM KV caches and vector search engines, not as a complete model-weight quantization ecosystem.

Sources:

- [TurboQuant arXiv](https://arxiv.org/abs/2504.19874)
- [TurboQuant OpenReview](https://openreview.net/forum?id=tO3ASKZlok)
- [Google Research TurboQuant post](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/)

NexusNet implication:

- Add `quantization.turboquant_kv` as `candidate-registry`, `shadow-only`, and `runtime-plugin-gated`.
- Treat any community TurboQuant weight-quantization repo as a separate candidate requiring source, license, benchmark, and kernel review.
- Control Panel must show: `kv_cache_quantization`, `bits_per_channel`, `long_context_delta`, `needle_recall_delta`, `attention_speed_delta`, `runtime_plugin`, and `unsupported_runtime_reason`.

Recommended status:

- High-priority research candidate for effective context and long-context local serving.
- Do not advertise as available in NexusNet until an actual runtime path is integrated and benchmarked.

### KIVI, KVQuant, And KV Cache Compression

Current public finding:

- KIVI is a tuning-free asymmetric 2-bit KV-cache quantization approach.
- KVQuant targets very long-context inference through per-channel key quantization, pre-RoPE key quantization, non-uniform datatypes, dense-and-sparse outlier handling, and Q-Norm.
- H2O and related cache-eviction systems show a separate lever: do not store all KV entries when attention can preserve heavy hitters and recent tokens.

Sources:

- [KIVI arXiv](https://arxiv.org/abs/2402.02750)
- [KVQuant arXiv](https://arxiv.org/abs/2401.18079)
- [KVQuant GitHub](https://github.com/SqueezeAILab/KVQuant)
- [H2O arXiv](https://arxiv.org/abs/2306.14048)

NexusNet implication:

- Add a Control Panel "Effective Context And KV Cache" section separate from "Model Size."
- Runtime scorecards must track KV policy: full precision, FP8, int8, int4, KIVI-like, TurboQuant-like, eviction, CPU offload, distributed KV, prefix cache, and LMCache reuse.
- Long-context claims must display measured recall and degradation, not just maximum tokens.

Recommended status:

- Promote the schema now.
- Keep specific methods candidate-gated until a runtime supports them in NexusNet.

### GPTQ, AWQ, SmoothQuant, And Classic PTQ

Current public finding:

- GPTQ remains a core one-shot weight quantization method using approximate second-order information, commonly 3-bit/4-bit.
- AWQ remains a hardware-friendly activation-aware weight-only method, widely used for 4-bit LLM serving.
- SmoothQuant remains the reference training-free W8A8 path that smooths activation outliers into weights to make both weights and activations quantizable.

Sources:

- [GPTQ arXiv](https://arxiv.org/abs/2210.17323)
- [AWQ arXiv](https://arxiv.org/abs/2306.00978)
- [AWQ MLSys paper](https://proceedings.mlsys.org/paper_files/paper/2024/file/42a452cbafa9dd64e9ba4aa95cc1ef21-Paper-Conference.pdf)
- [SmoothQuant arXiv](https://arxiv.org/abs/2211.10438)
- [SmoothQuant ICML page](https://proceedings.mlr.press/v202/xiao23c.html)

NexusNet implication:

- These are baseline weight/runtime formats for `RuntimeCapabilityScorecard`.
- Control Panel must show which backend can run which format on which hardware. vLLM's quantization table already separates AWQ, GPTQ, Marlin, INT8, FP8, bitsandbytes, DeepSpeedFP, and GGUF across GPU generations, AMD, Intel, and CPU.

Recommended status:

- Treat GPTQ/AWQ/SmoothQuant as required benchmark baselines.
- Use them as comparison points before adopting newer quantizers.

### FP8, FP4, MXFP4, NVFP4, NF4, And BOF4

Current public finding:

- NVIDIA TensorRT-LLM documents FP4, FP8 per-tensor, FP8 block scaling, FP8 rowwise, FP8 KV cache, AWQ, and GPTQ paths, with a hardware matrix that separates Blackwell, Hopper, Ada, and Ampere support.
- TensorRT-LLM's current support matrix exposes `NVFP4` and `MXFP4` as distinct claims. This matters because `FP4` is not one thing; the scale representation, block size, and hardware backend change the result.
- A 2025 microscaling FP4 study warns that MXFP4 and NVFP4 are promising but not automatically lossless; it specifically calls out MXFP4 scale quantization error and NVFP4 small-group behavior as practical quality risks.
- Hugging Face bitsandbytes docs distinguish NF4, FP4, compute dtype, and nested/double quantization. NF4 is best understood as a 4-bit datatype for normally distributed weights and QLoRA-style training/fine-tuning workflows, not a universal fast-inference kernel guarantee.
- A 2026 NF4 kernel paper argues that NF4 can save memory but still bottlenecks when the runtime dequantizes to FP16; it reports kernel speedups from optimizing dequantization, which reinforces the NexusNet rule that storage compression and compute speed must be measured separately.
- BOF4 proposes a block-wise optimal 4-bit float family that reduces quantization error relative to fixed 4-bit formats, but it is still a research candidate until common runtimes expose kernels and serialization.

Sources:

- [TensorRT-LLM quantization docs](https://nvidia.github.io/TensorRT-LLM/1.2.0rc4/features/quantization.html)
- [NVIDIA TensorRT-LLM developer page](https://developer.nvidia.com/tensorrt-llm)
- [Microscaling FP4 arXiv](https://arxiv.org/abs/2509.23202)
- [Transformers bitsandbytes docs](https://huggingface.co/docs/transformers/en/quantization/bitsandbytes)
- [QLoRA arXiv](https://arxiv.org/abs/2305.14314)
- [Fast NF4 dequantization kernels arXiv](https://arxiv.org/abs/2604.02556)
- [BOF4 arXiv](https://arxiv.org/abs/2505.06653)

NexusNet implication:

- Add `float_format_family`: `fp8`, `fp4`, `nf4`, `mxfp4`, `nvfp4`, `bof4`, `vendor_specific`.
- Add `scale_granularity`: `per_tensor`, `per_channel`, `per_group`, `per_block`, `rowwise`, `block_scaling`, `unknown`.
- Add `compute_path`: `native_low_precision`, `dequant_to_fp16`, `dequant_to_bf16`, `mixed_kernel`, `unknown`.
- Control Panel must not show "FP4 supported" as a flat green check. It must show hardware generation, runtime, model family, scaling mode, KV-cache support, and measured accuracy delta.

Recommended status:

- FP8 is a production runtime lane on modern accelerators, especially Hopper/Blackwell and selected serving stacks.
- MXFP4/NVFP4 are high-priority candidate lanes for Blackwell-class and newer hardware, but require model-specific evals.
- NF4 stays in the training/fine-tuning and memory-compression lane unless the runtime proves native or optimized dequantized inference.

### Newer Weight-Only, Sparse, And Mixed-Precision Candidates

Current public finding:

- HQQ is a calibration-free half-quadratic quantization toolkit with Transformers/vLLM-oriented usage paths and 2/3/4/8-bit style support, making it useful when NexusNet needs fast local candidate generation without a calibration dataset.
- AQLM targets extreme 2-3 bit compression with learned additive/multi-codebook quantization and joint block optimization.
- SpQR stores outlier-sensitive weights separately while quantizing the rest, making it a hybrid sparse-quantized representation rather than a plain integer format.
- AutoRound is Intel's tuning-based PTQ toolkit for LLMs/VLMs. Its public repository now calls out CPU/XPU/CUDA compatibility, vLLM/SGLang/Transformers compatibility, mixed precision, enhanced GGUF quantization, and MXFP4/NVFP4 dtype support.
- Squeeze10-LLM, FireQ, ABQ-LLM, SQ-format, and GlowQ are newer research/watchlist items around staged sub-2-bit mixed precision, INT4-FP8 kernels, arbitrary-bit acceleration, unified sparse-quantized formats, and low-rank correction over quantized models.

Sources:

- [HQQ GitHub](https://github.com/dropbox/hqq)
- [HQQ blog](https://mobiusml.github.io/hqq_blog/)
- [AQLM arXiv](https://arxiv.org/abs/2401.06118)
- [SpQR arXiv](https://arxiv.org/abs/2306.03078)
- [AutoRound GitHub](https://github.com/intel/auto-round)
- [AutoRound Hugging Face blog](https://huggingface.co/blog/autoround)
- [Squeeze10-LLM arXiv](https://arxiv.org/abs/2507.18073)
- [FireQ arXiv](https://arxiv.org/abs/2505.20839)
- [ABQ-LLM arXiv](https://arxiv.org/abs/2408.08554)
- [SQ-format arXiv](https://arxiv.org/abs/2512.05409)
- [GlowQ arXiv](https://arxiv.org/abs/2603.25385)

NexusNet implication:

- Add `algorithm_family`: `rounding`, `activation_aware`, `second_order`, `half_quadratic`, `additive_codebook`, `sparse_quantized`, `mixed_precision`, `low_rank_corrected`, `arbitrary_bit`, `hardware_float`.
- Add `artifact_maturity`: `paper_only`, `reference_code`, `runtime_integrated`, `production_runtime`, `buyer_supported`.
- Separate `storage_bits` from `effective_bits_per_weight`; EXL2, mixed precision, sparse-quantized, and codebook methods may not map cleanly to one integer bit count.

Recommended status:

- AutoRound, HQQ, AQLM, SpQR, and compressed-tensors support belong in the registry now.
- Squeeze10-LLM, FireQ, ABQ-LLM, SQ-format, BOF4, and GlowQ should be tracked as research candidates with no live promotion until a runtime path, license, and benchmark exist.

### Rotation-Based And Ultra-Low-Bit Quantization

Current public finding:

- QuaRot applies rotations to reduce outliers and enables 4-bit inference across weights, activations, and KV cache.
- SpinQuant learns rotations and reports strong W4A4/KV4 behavior relative to earlier methods.
- QuIP# uses randomized Hadamard incoherence and lattice codebooks for strong low-bit weight PTQ.

Sources:

- [QuaRot arXiv](https://arxiv.org/abs/2404.00456)
- [QuaRot OpenReview](https://openreview.net/forum?id=dfqsW38v1X)
- [SpinQuant arXiv](https://arxiv.org/abs/2405.16406)
- [QuIP# arXiv](https://arxiv.org/abs/2402.04396)
- [QuIP# ICML page](https://proceedings.mlr.press/v235/tseng24a.html)

NexusNet implication:

- Add `rotation_preprocessing`, `hadamard_transform`, `learned_rotation`, and `activation_quantized_compute` fields.
- Treat W4A4 as a separate claim from W4A16. W4A4 can be a real speed path only if the runtime kernels execute low precision rather than dequantizing early.

Recommended status:

- Candidate and benchmark-gated.
- Valuable for research/runtime scorecards, especially when a backend exposes kernels.

### Native 1-Bit / 1.58-Bit Models

Current public finding:

- BitNet b1.58 is a native low-bit model family, not a post-training quantized regular model.
- Microsoft's bitnet.cpp is the official inference framework for 1-bit LLMs and reports CPU speed and energy advantages for BitNet b1.58 style models.
- BitNet b1.58 2B4T is a public native 1-bit scale reference at 2B parameters.

Sources:

- [BitNet b1.58 arXiv](https://arxiv.org/abs/2402.17764)
- [BitNet b1.58 2B4T arXiv](https://arxiv.org/abs/2504.12285)
- [Microsoft BitNet GitHub](https://github.com/microsoft/BitNet)
- [Microsoft Research bitnet.cpp publication](https://www.microsoft.com/en-us/research/publication/1-bit-ai-infra-part-1-1-fast-and-lossless-bitnet-b1-58-inference-on-cpus/)

NexusNet implication:

- Add a native-low-bit lane to avoid treating BitNet as just "another quant."
- Useful for edge canaries, local fallback, and low-power always-on helpers, not a frontier teacher replacement.

Recommended status:

- Candidate lane for local canaries and buyer-friendly low-resource deployments.

## Model Format And Package Findings

| Format | Current finding | NexusNet use |
|---|---|---|
| safetensors | Safe, fast, zero-copy tensor storage alternative to pickle. Widely used across Transformers and related projects. Source: [HF safetensors docs](https://huggingface.co/docs/safetensors/index). | Preferred canonical raw checkpoint package when ingesting HF/open-weight models. |
| compressed-tensors | A safetensors extension for storing sparse and quantized tensors with metadata for formats such as GPTQ, AWQ, SmoothQuant, INT8, FP8, SparseGPT, and related schemes. Source: [compressed-tensors GitHub](https://github.com/vllm-project/compressed-tensors). | Required server-runtime format lane for vLLM/LLM Compressor style deployments. |
| GGUF | Binary format for GGML/llama.cpp inference, designed for single-file deployment, extensibility, mmap compatibility, and embedded metadata. Source: [GGUF spec](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md). | Preferred local/buyer-friendly package format for llama.cpp/LM Studio/Ollama lanes. |
| llama.cpp quantized GGUF | `llama-quantize` converts high-precision GGUF into quantized formats, supports imatrix, tensor-specific quant types, output/token embedding overrides, and MoE metadata overrides. Source: [llama.cpp quantize docs](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md). | Required quantization benchmark path for local CPU/GPU fallback. |
| EXL2 | ExLlamaV2-specific CUDA local-inference quantized format with flexible average bits-per-weight. Source: [ExLlamaV2 GitHub](https://github.com/turboderp-org/exllamav2). | Candidate NVIDIA-consumer-GPU lane; not a general buyer-default format because it is runtime-specific. |
| bitsandbytes 4-bit/8-bit | Runtime-side quantized linear layers and NF4/FP4/double-quant loading through Transformers. Source: [Transformers bitsandbytes docs](https://huggingface.co/docs/transformers/en/quantization/bitsandbytes). | Prototype/fine-tune lane; require proof before presenting as a production serving format. |
| ONNX / ONNX Runtime GenAI | Runtime-backed model packaging for Windows/edge/mobile ecosystems, with ONNX quantization APIs and GenAI builder paths. Source: [ONNX Runtime quantization docs](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html). | Candidate Windows, DirectML, and NPU/iGPU integration path. |
| ExecuTorch `.pte` | PyTorch on-device export/runtime path using portable ahead-of-time program files. Source: [ExecuTorch export docs](https://docs.pytorch.org/executorch/stable/using-executorch-export.html). | Candidate Android/mobile lane. |
| MLC LLM packages | Cross-platform compiled deployment path with named quantization modes such as `q3f16_1`, `q4f16_1`, and `q4f16_awq`. Source: [MLC quantization docs](https://llm.mlc.ai/docs/compilation/configure_quantization.html). | Candidate mobile/web lane. |
| OpenVINO IR / GenAI package | Intel edge and PC deployment package with NNCF/Optimum Intel 8-bit and 4-bit weight compression paths. Source: [OpenVINO weight compression docs](https://docs.openvino.ai/weight_compression). | Candidate Intel CPU/iGPU/NPU buyer lane. |
| Vendor compiled artifacts | Qualcomm, TensorRT-LLM, OpenVINO, LiteRT/MNN formats. | Runtime-specific scorecard path; never assume portability. |

Control Panel requirement:

- Every model row must display `source_format`, `serving_format`, `quantization_format`, `runtime`, `conversion_path`, `license_status`, `checksum`, `last_verified_on`, `hardware_fit`, and `fallback_runtime`.

## Runtime Capability Findings

### vLLM

Current public finding:

- vLLM documents many quantization options: AutoAWQ, bitsandbytes, GGUF, GPTQModel, Intel Neural Compressor, INT4 W4A16, INT8 W8A8, FP8 W8A8, NVIDIA Model Optimizer, online quantization, AMD Quark, quantized KV cache, and TorchAO.
- vLLM also documents custom out-of-tree quantization plugin registration.

Sources:

- [vLLM quantization docs](https://docs.vllm.ai/en/stable/features/quantization/)

NexusNet implication:

- vLLM should be a primary server runtime candidate, but the Control Panel must show exact quant support by hardware class.
- Out-of-tree quantization plugin support makes vLLM a plausible place to test TurboQuant-style plugins after safety and benchmark gates.
- Add `compressed_tensors_config_detected` and `llm_compressor_recipe` fields for models produced through vLLM/LLM Compressor pipelines.

### SGLang

Current public finding:

- SGLang supports explicit quantization selection for per-channel INT8/FP8 with per-token dynamic activation, including `w8a8_int8` and `w8a8_fp8` paths.
- Its docs include offline quantization examples through AutoRound and scheme examples such as `W2A16`, `W3A16`, `W4A16`, `W8A16`, `NVFP4`, `MXFP4`, and `GGUF:Q4_K_M`, while warning that some scheme examples may not have real kernels.
- SGLang also documents quantized KV cache with FP8/FP4-style lower precision storage.

Sources:

- [SGLang quantization docs](https://docs.sglang.io/docs/advanced_features/quantization)
- [SGLang quantized KV cache docs](https://docs.sglang.io/advanced_features/quantized_kv_cache.html)

NexusNet implication:

- SGLang should be scored separately from vLLM. Both may accept similarly named quantized models but differ in kernel selection, config interpretation, and production behavior.
- Control Panel must show `quantization_config_source`: `model_config`, `runtime_override`, `compressed_tensors`, `autoround`, `unknown`.

### TensorRT-LLM And NVIDIA Model Optimizer

Current public finding:

- TensorRT-LLM directly runs pre-quantized models generated with NVIDIA TensorRT Model Optimizer.
- Its quantization matrix differentiates FP4, FP8 variants, FP8 KV cache, AWQ, GPTQ, NVFP4, and MXFP4 by model family and hardware generation.
- NVIDIA positions TensorRT-LLM around NVIDIA GPU serving, including FP8/NVFP4 quantization, paged KV cache, speculative decoding, and in-flight batching.

Sources:

- [TensorRT-LLM quantization docs](https://nvidia.github.io/TensorRT-LLM/1.2.0rc4/features/quantization.html)
- [NVIDIA TensorRT-LLM developer page](https://developer.nvidia.com/tensorrt-llm)
- [NVIDIA Model Optimizer PTQ blog](https://developer.nvidia.com/blog/accelerate-generative-ai-inference-performance-with-nvidia-tensorrt-model-optimizer-now-publicly-available/)

NexusNet implication:

- Treat TensorRT-LLM as a high-performance NVIDIA server lane, not as a portable local model format.
- Control Panel fields must include `nvidia_arch`, `cuda_version`, `tensorrt_llm_version`, `modelopt_recipe`, `engine_build_artifact`, and `fallback_non_nvidia_runtime`.

### torchao / Transformers

Current public finding:

- torchao supports custom high-performance dtypes, quantization, sparsity, QAT, float8 training, optimizer quantization, KV cache quantization, and integration with `torch.compile`.
- Transformers docs list int8, int4, float8, autoquantization, per-module configuration, and hardware-specific recommendations.

Sources:

- [Transformers torchao docs](https://huggingface.co/docs/transformers/en/quantization/torchao)
- [Transformers quantization overview](https://huggingface.co/docs/transformers/en/quantization/overview)

NexusNet implication:

- Use torchao as a research and prototype lane for PyTorch-native quant experiments.
- Do not assume torchao results translate to llama.cpp, vLLM, or mobile runtimes without direct benchmark evidence.

### llama.cpp / GGUF

Current public finding:

- llama.cpp quantization remains the most buyer-friendly open local path because it gives single-file GGUF packages and a large spread of quant types.
- The quantization docs explicitly warn against requantizing already-quantized tensors because quality can degrade.

Sources:

- [llama.cpp quantize docs](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)
- [GGUF spec](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md)

NexusNet implication:

- Use GGUF as the first Control Panel local-package path for buyer workflows.
- Track whether a quant was made from F16/BF16 or from an already-quantized file.

### ONNX Runtime GenAI, OpenVINO, MLC LLM, And ExecuTorch

Current public finding:

- ONNX Runtime exposes quantization APIs, including INT4 model outputs, and points AWQ/GPTQ GenAI model building to the GenAI builder path.
- AMD Quark documents UINT4 AWQ export to ONNX Runtime GenAI for Ryzen AI / DirectML-style flows.
- OpenVINO documents 8-bit and 4-bit weight compression for LLMs through NNCF/Optimum Intel and OpenVINO GenAI usage.
- MLC LLM exposes named quantization modes including `q0f16`, `q0f32`, `q3f16_1`, `q4f16_1`, `q4f32_1`, and experimental `q4f16_awq`.
- ExecuTorch exports models into `.pte` program files for ahead-of-time on-device execution and backend partitioning.

Sources:

- [ONNX Runtime quantization docs](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html)
- [AMD Quark ONNX Runtime GenAI UINT4 AWQ docs](https://quark.docs.amd.com/latest/supported_accelerators/ryzenai/tutorial_uint4_oga.html)
- [OpenVINO weight compression docs](https://docs.openvino.ai/weight_compression)
- [OpenVINO GenAI workflow docs](https://docs.openvino.ai/2024/learn-openvino/llm_inference_guide.html)
- [MLC LLM quantization docs](https://llm.mlc.ai/docs/compilation/configure_quantization.html)
- [ExecuTorch export docs](https://docs.pytorch.org/executorch/stable/using-executorch-export.html)

NexusNet implication:

- These are platform lanes, not just quantization methods. The Control Panel must show the exported artifact, target accelerator, conversion command/recipe, and the fallback path.
- This is the natural buyer-support area for Windows laptops, Intel/AMD AI PCs, Android devices, WebGPU, and embedded/mobile deployments.

## Multi-Agent Research Findings

### Open Deep Research

Current public finding:

- LangChain's Open Deep Research is an open-source deep research agent intended to work across multiple model providers, search tools, and MCP servers.
- The associated guidance separates research delegation from final writing and supports parallel sub-researchers for multifaceted topics.

Sources:

- [Open Deep Research GitHub](https://github.com/langchain-ai/open_deep_research)
- [Open Deep Research blog](https://www.langchain.com/blog/open-deep-research)
- [LangChain deep research docs](https://docs.langchain.com/oss/python/deepagents/deep-research)

NexusNet implication:

- Add `ResearchScout` / `ResearchAO` as a governed lane.
- Research outputs must produce source ledgers, source freshness, credibility labels, conflict notes, candidate IDs, and registry deltas.
- Writing/synthesis should happen only after source collection completes.

Recommended status:

- Pattern to assimilate, not dependency to blindly embed.

### STORM

Current public finding:

- STORM researches before writing by gathering references and building outlines via multi-perspective question asking.

Sources:

- [STORM arXiv](https://arxiv.org/abs/2402.14207)
- [STORM NAACL paper PDF](https://aclanthology.org/anthology-files/pdf/naacl/2024.naacl-long.347.pdf)

NexusNet implication:

- Add `multi_perspective_questions`, `outline_before_answer`, and `source_to_claim_map` fields to research traces.
- Use STORM-style pre-writing for canon refreshes, model/runtime comparisons, and buyer documentation.

### Magentic-One / AutoGen

Current public finding:

- Magentic-One uses a lead Orchestrator that plans, tracks progress, replans after errors, and delegates to specialized web/file/code agents. Microsoft describes it as modular and extensible.
- AutoGenBench is positioned as an agentic evaluation tool with controls for repetition and isolation.

Sources:

- [Magentic-One Microsoft Research](https://www.microsoft.com/en-us/research/publication/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/)
- [Magentic-One arXiv](https://arxiv.org/abs/2411.04468)
- [Magentic-One AutoGen docs](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html)

NexusNet implication:

- The pattern reinforces NexusNet's AO Hive design: one brain authority, specialized agents, error recovery, and trace-driven evaluation.
- Do not let AutoGen become the authority layer. Use the orchestration pattern and benchmark discipline.

## Self-Review And Critique Findings

| Pattern | Finding | NexusNet assimilation |
|---|---|---|
| Reflexion | Converts scalar/binary/free-form feedback into verbal memory for future attempts. Source: [Reflexion arXiv](https://arxiv.org/abs/2303.11366). | Store failure reflections in AO/expert mini-graphs with expiry, source, and validation status. |
| Self-Refine | Iterative generate, feedback, refine loop using self-feedback. Source: [Self-Refine arXiv](https://arxiv.org/abs/2303.17651), [Self-Refine site](https://selfrefine.info/). | Useful for draft refinement, but must not be trusted without external verification. |
| CRITIC | Tool-interactive critique improves correction by using external feedback such as search or code execution. Source: [CRITIC arXiv](https://arxiv.org/abs/2305.11738). | Best fit for NexusNet: self-review must call tools/evals, not rely on self-opinion. |
| Self-critique limits | Research asks whether LLMs can really improve by self-critiquing plans and warns against unsupported self-correction. Source: [self-critique plans arXiv](https://arxiv.org/abs/2310.08118). | Control Panel must show whether review used external evidence, tests, verifier, or only self-critique. |

Control Panel requirement:

- Every self-review artifact must show `reviewer`, `target_artifact`, `external_evidence_used`, `tests_run`, `verifier_score`, `disagreement_summary`, `accepted_changes`, `rejected_changes`, and `authority_source`.

## Autonomous Updates And Harness Engineering Findings

### Harness Engineering

Current public finding:

- Meta-Harness treats harness code as the optimization target and gives the proposer access to source code, scores, and raw traces. It reports gains in context management, math retrieval, and agentic coding.
- Natural-Language Agent Harnesses externalize harness behavior as editable natural-language artifacts executed through explicit contracts, durable artifacts, and adapters.
- AutoHarness shows small models can synthesize code harnesses that prevent invalid actions in game environments and sometimes outperform larger models by improving the action boundary.

Sources:

- [Meta-Harness arXiv](https://arxiv.org/abs/2603.28052)
- [Natural-Language Agent Harnesses arXiv](https://arxiv.org/abs/2603.25723)
- [AutoHarness arXiv](https://arxiv.org/abs/2603.03329)

NexusNet implication:

- Add `HarnessRegistry` as a top-level Control Panel surface.
- Store raw traces, not only summaries.
- Harness changes must be shadow-tested against held-out evals before affecting production AO behavior.

### Coding-Agent Update Systems

Current public finding:

- SWE-agent takes GitHub issues and attempts automatic fixes with a language model.
- AutoCodeRover combines LLMs with program-structure-aware search and test/fault localization to improve GitHub issues.
- OpenHands provides an AI-driven development system, SDK, CLI, and isolated agent execution environments.

Sources:

- [SWE-agent GitHub](https://github.com/SWE-agent/SWE-agent)
- [AutoCodeRover arXiv](https://arxiv.org/abs/2404.05427)
- [AutoCodeRover site](https://www.autocoderover.net/)
- [OpenHands GitHub](https://github.com/OpenHands/OpenHands)
- [OpenHands Enterprise docs](https://docs.openhands.dev/enterprise)

NexusNet implication:

- Autonomous updates should not mean direct writes to main. They should produce:
  - issue intent,
  - retrieval trace,
  - affected files,
  - proposed patch,
  - tests run,
  - before/after behavior,
  - reviewer result,
  - rollback plan,
  - promotion gate result.
- Control Panel should expose "proposal", "shadow patch", "test-passed", "review-needed", "blocked", and "promoted" states.

Recommended status:

- Adopt pattern only. Keep real code updates behind branch, test, human-review, and rollback gates.

## Required Control Panel Additions From This Research

The Control Panel should include these additional pages/sections before it is called complete against the canon book:

1. Quantization And Format Registry
   - weight quant formats, activation formats, KV cache formats, native low-bit, file packages, conversion path, source precision, license, checksum, and quality delta.

2. Runtime Capability Scorecards
   - backend, version, hardware, model formats, quant formats, KV support, structured outputs, tool calls, vision/audio, prefix cache, telemetry, sandbox, local install path, and buyer-support risk.

3. Effective Context And KV Cache
   - raw tokens, cached tokens, prefix reuse, KV policy, KV bit width, recall checks, evidence dereferences, cache hit rate, and degradation warnings.

4. Model Package Provenance
   - source checkpoint, converted artifact, quantization recipe, calibration data, imatrix presence, runtime target, checksum, and rollback artifact.

5. Multi-Agent Research Workspace
   - research question, sub-researchers, sources, source freshness, claims, conflicts, confidence, registry deltas, and synthesis state.

6. Self-Review And Verifier Panel
   - self-review loops, tool-backed checks, tests, verifier scores, external evidence, accepted/rejected changes, and remaining risk.

7. Harness Registry
   - AO/expert harness contracts, allowed tools, budgets, raw traces, eval family, shadow status, promotion status, rollback plan, and owner layer.

8. Autonomous Update Gate
   - branch/proposal state, touched files, tests, security review, license review, human approval, deployment block, and rollback.

9. Security Cross-Check
   - every quantized model, runtime plugin, MCP tool, agent update, harness change, or research source must pass source identity, license, sandbox, audit, and kill-switch checks.

## Registry Fields To Add

### QuantizationFormatRegistry

- `quantization_id`
- `display_name`
- `lane`: `weight_only`, `weight_activation`, `kv_cache`, `native_low_bit`, `file_format`, `runtime_plugin`
- `algorithm_family`
- `storage_container`
- `source_url`
- `source_kind`
- `license_status`
- `bits_weight`
- `bits_activation`
- `bits_kv`
- `effective_bits_per_weight`
- `compute_dtype`
- `storage_dtype`
- `float_format_family`
- `scale_granularity`
- `compute_path`
- `requires_calibration`
- `calibration_data`
- `requires_training`
- `source_precision_required`
- `supports_moe`
- `supports_vision`
- `supports_kv_cache`
- `supported_runtimes`
- `unsupported_runtimes`
- `measured_quality_delta`
- `measured_speed_delta`
- `measured_memory_delta`
- `kernel_or_loader`
- `artifact_maturity`
- `last_verified_on`
- `promotion_status`
- `blocked_reason`

### RuntimeCapabilityScorecard

- `runtime_id`
- `version`
- `host_os`
- `hardware_class`
- `driver_or_sdk`
- `model_formats`
- `quantization_formats`
- `quantization_config_source`
- `kv_cache_modes`
- `compressed_tensors_config_detected`
- `modelopt_recipe`
- `engine_build_artifact`
- `prefix_cache_support`
- `structured_output_support`
- `tool_call_support`
- `vision_support`
- `audio_support`
- `telemetry_export`
- `sandbox_mode`
- `offline_install_path`
- `buyer_support_risk`
- `benchmark_artifacts`
- `last_verified_on`

### AgenticImprovementRegistry

- `improvement_id`
- `owner_layer`
- `pattern`: `research`, `self_review`, `critic`, `harness`, `autonomous_patch`, `dream`, `training`
- `source_url`
- `source_kind`
- `authority_role`
- `allowed_actions`
- `denied_actions`
- `raw_trace_links`
- `eval_family`
- `held_out_eval_required`
- `external_evidence_required`
- `rollback_plan`
- `promotion_status`
- `last_verified_on`

## Priority Recommendation

Before finishing the Control Panel UI, build the backend/API shape for these panels:

1. `GET /ops/brain/quantization/formats`
2. `GET /ops/brain/runtime/scorecards`
3. `GET /ops/brain/runtime/effective-context`
4. `GET /ops/brain/research/workspace`
5. `GET /ops/brain/self-review/status`
6. `GET /ops/brain/harness/registry`
7. `GET /ops/brain/autonomous-updates/gates`
8. `GET /ops/brain/quantization/watchlist`

The Control Panel can then be truthful: it shows what is locked, what is candidate-only, what is shadow-only, what is blocked, and what is actually live.

## Final Bottom Line

The next NexusNet product step is not simply "add more cards to the dashboard." The Control Panel must become the operator-visible truth layer for:

- quantized model package provenance,
- runtime/hardware/format fit,
- KV-cache and effective-context reality,
- multi-agent research evidence,
- self-review with external verification,
- harness changes,
- and autonomous updates gated by tests, review, security, rollback, and promotion authority.

This keeps NexusNet aligned with the canon book: NexusNet remains the brain authority; models, quantizers, runtimes, agents, protocols, and update loops are governed capabilities.
