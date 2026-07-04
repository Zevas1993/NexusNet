# NexusNet Open-First Research Expansion - 2026-04-28

Purpose: correct and expand the research refresh around the actual NexusNet chat canon, with special focus on open-weight models, research papers, inference backends, and no-cost/local-first teacher choices.

Primary local source:

- `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`

Related local artifacts:

- `docs/NEXUSNET_COMPLETE_CANON_RESEARCH_REFRESH_DIFF_2026-04-28.md`
- `docs/NEXUSNET_COMPLETE_CANON_UPDATED_RESEARCH_CATALOG_2026-04-28.md`
- `docs/NEXUSNET_RESEARCH_CANDIDATE_DOSSIER_2026-04-28.md`
- `docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md`
- `docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md`
- `docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md`

Research date: 2026-04-28

## Correction Scope

The prior catalog was too shallow for the user's stated intent. It named some current candidates, but it did not sufficiently:

- Pull and organize AI research papers.
- Expand the open-weight teacher/model scan around current leaders such as Kimi, Nemotron, DeepSeek, Qwen, GLM, Gemma, Mistral, gpt-oss, Granite, Phi, and Llama.
- Compare current inference backends beyond a short list.
- Preserve NexusNet's original no-cost/open-model attraction as the primary default.
- Surface hidden outliers that can beat expensive or premium options for specific NexusNet roles.

This expansion treats open models as the default research lane and API-only premium models as optional external teachers or benchmark references.

## Canon Signals Used

The complete canon book makes these lanes non-optional:

| Canon signal | Why it matters for this refresh |
|---|---|
| C01/C02 Mixtral and Devstral branch | Keep historical MoE/expert lineage, but refresh the live teacher candidates. |
| C27 Nemotron-Elastic-12B | Research Nemotron successors and elastic/efficient model families. |
| C34 LFM2 deep dive | Keep small efficient multimodal models and hybrid architectures in scope. |
| C38 R-Zero integration | Include self-improvement, generated tasks, RL, and evaluator papers. |
| Aspect 9 teachers/distillation/RL | Research must materially update the teacher ensemble, not just list tools. |
| Aspect 12 runtime/local-first packaging | Backends are part of the product strategy, not an implementation footnote. |
| Aspect 13 multimodal/FARA/DeepEyes/Qwen/vision | Vision, GUI, and computer-use models belong in the roster. |
| Aspect 15 candidate registry | Every item must land as a governed candidate, not as a silent default replacement. |

## Open-First Thesis

NexusNet should not begin as a paid API wrapper. The primary path should be:

1. Open-weight models as local, reproducible, privacy-friendly teachers and specialists.
2. Local inference backends as interchangeable runtime candidates behind a NexusNet-owned scorecard.
3. Premium APIs only as optional external teachers, red-team reviewers, or temporary evaluation baselines.
4. Teacher replacement based on role-specific evidence, not model hype.

Important distinction: open weights remove provider fees and lock-in, but they do not remove compute costs. Kimi K2.6, DeepSeek V4-Pro, GLM-5.1, and Llama 4 Maverick are open or available as weights, but they still need serious hosting hardware or a third-party inference provider. Small sparse-active models such as Qwen3.6-35B-A3B, Gemma 4 26B-A4B, Granite 4.0 H-Tiny/H-Small, gpt-oss-20b, and Phi-4 reasoning variants are more realistic no-cost/local starting points.

## Immediate Roster Change

Preserve historical canon:

- Historical central mentor ensemble: Mixtral-87B, Yi-1.5-9B, Qwen-0.5B MoE, Llama-3 8B.
- Historical branch: Mixtral plus Devstral, Mini-NexusNet per expert, Cortex, Neural Bus, Expert-Router Alignment.

Add live open-first registry overlays:

- `teacher_registry_historical.yaml`: immutable history.
- `teacher_registry_live_open_2026_04.yaml`: current candidate roster, eval-gated.
- `runtime_backend_catalog_2026_04.yaml`: backend scorecards.
- `paper_registry_2026_04.yaml`: research papers mapped to NexusNet lanes.

Do not overwrite canon defaults until license, eval, runtime, security, and governance gates pass.

## Current Open Model Catalog

| Candidate | Source | Open/license posture | Current signal | NexusNet role | Caveat |
|---|---|---|---|---|---|
| Kimi K2.6 | [Kimi page](https://www.kimi.com/ai-models/kimi-k2-6), [HF](https://huggingface.co/moonshotai/Kimi-K2.6), [license](https://huggingface.co/moonshotai/Kimi-K2.6/blob/main/LICENSE) | Modified MIT; attribution trigger for very large commercial products | 1.1T parameter native multimodal MoE, 32B active, 256K context, MLA, vision encoder, strong agentic/coding benchmark claims | Top open agentic/coding/visual teacher candidate | Very large; practical use likely through hosted providers or heavy local cluster. Safety review required. |
| Kimi K2.5 | [HF](https://huggingface.co/moonshotai/Kimi-K2.5), [paper](https://arxiv.org/abs/2602.02276), [safety eval](https://arxiv.org/abs/2604.03121) | Modified MIT | Strong multimodal agentic model with Agent Swarm paper; independent safety evaluation flags deployment risks | Prior Kimi baseline and safety study anchor | Superseded by K2.6 for capability, still valuable for paper/safety evidence. |
| Kimi K2 | [paper](https://arxiv.org/abs/2507.20534) | Open checkpoints per paper | 1T MoE, 32B active, agentic data synthesis and RL | Original Kimi architecture baseline | K2.5/K2.6 are stronger live candidates. |
| DeepSeek V4-Pro | [DeepSeek release](https://api-docs.deepseek.com/news/news260424), [HF](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) | MIT on HF model page | 1.6T total, 49B active, 1M context, hybrid attention, strong open model claims | Top open reasoning/coding teacher and long-context research target | Huge runtime footprint; security, provenance, and geopolitical review required. |
| DeepSeek V4-Flash | [DeepSeek release](https://api-docs.deepseek.com/news/news260424), [HF](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) | MIT | 284B total, 13B active, 1M context, cheaper/faster V4 line | Efficient long-context open teacher and daily evaluator candidate | Still too large for ordinary consumer hardware. |
| Qwen3.6-35B-A3B | [HF](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) | Apache 2.0 | 35B total, 3B active, vision encoder, native 262K context, extension path to about 1M, vLLM/SGLang/KTransformers support | Best practical open local teacher candidate for coding, agentic work, vision, and iterative development | The "3B active" efficiency does not eliminate memory needs; test with GGUF/quantized variants before promotion. |
| Qwen3-VL-235B-A22B-Instruct | [HF](https://huggingface.co/Qwen/Qwen3-VL-235B-A22B-Instruct) | Apache 2.0 | Dedicated vision-language MoE, visual agent/GUI operation, visual coding, spatial grounding, OCR in 32 languages, native 256K context expandable to 1M | Primary open vision/GUI/CUA teacher candidate for VisualOps and computer-use review | Heavy model; use smaller Qwen/LFM/Phi/Gemma lanes for local tests. |
| GLM-5.1 | [HF](https://huggingface.co/zai-org/GLM-5.1) | MIT | 754B parameter open agentic engineering model with strong SWE-Bench Pro, NL2Repo, Terminal-Bench, CyberGym, BrowseComp, and MCP-Atlas claims | Hidden high-end outlier for long-horizon agentic engineering and tool workflows | Large infrastructure model; benchmark claims are partly self-reported and need local harness validation. |
| MiniMax M2.5 | [MiniMax page](https://www.minimax.io/models/text), [HF](https://huggingface.co/MiniMaxAI/MiniMax-M2.5) | Modified MIT | 229B parameter open-weight model focused on coding, agentic tool use, search, office work, cost efficiency, and private deployment with vLLM/SGLang/Transformers/KTransformers support | Hidden cost/performance outlier for SWE, browser/search, office automation, and agent economics | Large model; claims are heavily vendor-reported and need NexusNet-owned harness proof. |
| Mistral Small 4 | [Mistral docs](https://docs.mistral.ai/models/model-cards/mistral-small-4-0-26-03) | Marked Open by Mistral docs | 119B total, 6.5B active, 256K context, unified instruct/reasoning/coding | Efficient open general teacher, strong replacement for stale Mistral Small 3.x references | Confirm exact weight license and local deploy path before commercial defaults. |
| Devstral 2 | [Mistral overview](https://docs.mistral.ai/models/overview) | Marked Open | Current Mistral code-agent model; Devstral Small/Medium predecessors are listed as replaced by Devstral 2 | Current coding/SWE specialist for the historical Devstral branch | Exact model card and local packaging must be pinned before registry promotion. |
| gpt-oss-120b | [OpenAI release](https://openai.com/index/introducing-gpt-oss/), [HF](https://huggingface.co/openai/gpt-oss-120b), [model card](https://openai.com/index/gpt-oss-model-card/) | Apache 2.0, open-weight | 117B total, 5.1B active, designed for reasoning and tool use, runs on a single 80 GB GPU class system | Strong open reasoning teacher and transparent chain-of-thought audit candidate | Text-only; use harmony format; not served by OpenAI API. |
| gpt-oss-20b | [OpenAI release](https://openai.com/index/introducing-gpt-oss/) | Apache 2.0 | Lower-latency/local variant intended to run within 16 GB memory | Local no-cost fallback, canary, and small teacher | Lower ceiling than current Kimi/DeepSeek/Qwen/GLM leaders. |
| gpt-oss-safeguard | [OpenAI release](https://openai.com/index/introducing-gpt-oss-safeguard/), [technical report](https://openai.com/index/gpt-oss-safeguard-technical-report/) | Apache 2.0 | Open safety reasoning models that classify against developer-provided policies | Local safety/policy teacher and EvalsAO guardrail candidate | Research preview; must be tested against NexusNet tool/security policies. |
| Gemma 4 26B-A4B | [Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/), [HF](https://huggingface.co/google/gemma-4-26B-A4B-it) | Apache 2.0 | Multimodal MoE, open, efficient, up to 256K context family, strong intelligence-per-parameter | Hidden local efficiency outlier for multimodal reasoning, coding, and edge-friendly teacher roles | Verify real quality at long context and with quantized runtimes. |
| Gemma 4 E2B/E4B | [Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/), [DeepMind page](https://deepmind.google/models/gemma/gemma-4/) | Apache 2.0 | Small edge models with image/video and native audio on smaller variants | No-cost edge/mobile fallback, canary, and Android/desktop local lane | Not a frontier teacher; value is latency and ubiquity. |
| Granite 4.0 H-Small/H-Tiny/H-Micro | [IBM Granite](https://www.ibm.com/granite), [Granite 4.0 announcement](https://www.ibm.com/new/announcements/ibm-granite-4-0-hyper-efficient-high-performance-hybrid-models) | Apache 2.0 | Hybrid Mamba/Transformer, signed checkpoints, ISO 42001 positioning, RAG/tool/cybersecurity/enterprise focus | Hidden trust/governance/RAG outlier for buyer-facing local enterprise deployments | Less likely to beat frontier models on raw reasoning, but strong for trust, RAG, and efficient operations. |
| Phi-4-reasoning-vision-15B | [HF](https://huggingface.co/microsoft/Phi-4-reasoning-vision-15B), [paper](https://arxiv.org/abs/2603.03975) | MIT | Compact multimodal reasoning model for OCR, GUI grounding, scientific/math reasoning | Hidden GUI/document/vision teacher for VisualOps and CUA review | 16K context; not a general long-context teacher. |
| Phi-4-reasoning | [paper](https://arxiv.org/abs/2504.21318) | MIT for Phi-4 line per Microsoft materials | Compact reasoning model trained from curated teachable prompts and reasoning demos | Small local math/reasoning teacher | Needs role-limited use and benchmark comparison against Gemma/Qwen small variants. |
| Nemotron 3 Nano/Super/Ultra | [NVIDIA developer page](https://developer.nvidia.com/nemotron), [NVIDIA page](https://www.nvidia.com/en-us/ai-data-science/foundation-models/nemotron/), [paper](https://arxiv.org/abs/2512.20856) | NVIDIA Open Model License, free production use per NVIDIA page | Open model family, up to 1M context, hybrid Mamba-Transformer, LatentMoE, NVFP4/MTP, RL for agentic/tool use | Successor to Nemotron-Elastic as an efficiency/agentic/runtime research lane | Larger Super/Ultra availability and exact weights must be confirmed per model at implementation time. |
| LFM2.5 / LFM2.5-VL | [Liquid blog](https://www.liquid.ai/blog/lfm2-5-350m-no-size-left-behind), [LFM2.5-VL HF](https://huggingface.co/LiquidAI/LFM2.5-VL-450M), [paper](https://arxiv.org/abs/2511.23404) | LFM 1.0 license on HF; open weights per Liquid/paper | Tiny edge-oriented text/vision family, 350M to 8.3B class, on-device focus, GGUF/ONNX/MLX/vLLM/ExecuTorch/llama.cpp paths | Hidden edge VisualOps/data-extraction/tool-use outlier and Android/local assistant lane | Not a frontier reasoning teacher; use for edge speed, function calling, extraction, OCR, and local canaries. |
| Llama 4 Scout | [HF card](https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E), [HF release blog](https://huggingface.co/blog/llama4-release) | Llama 4 Community License | 109B total, 17B active, multimodal MoE, 10M instruct context claim | Long-context multimodal comparison and synthetic-data teacher | Custom license, Meta data disclosures, and benchmark controversies require strict commercial review. |
| Llama 4 Maverick | [HF card](https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E) | Llama 4 Community License | 400B total, 17B active, multimodal MoE, 1M context | Multimodal comparison teacher, not default | Too heavy and license-gated for default no-cost local path. |

## Hidden Outliers To Test Before Paying For Premium APIs

These are not necessarily the absolute best models. They are high leverage because they may beat paid options on a role-specific basis or remove recurring provider cost.

| Outlier | Why it matters | First NexusNet test |
|---|---|---|
| Qwen3.6-35B-A3B | Sparse-active, Apache, multimodal, 262K native context, strong coding/agentic card, multiple backends | Run repo-edit, tool-call, vision, and 128K/262K context tasks locally through vLLM, SGLang, LM Studio, and llama.cpp quantizations. |
| Gemma 4 26B-A4B | Apache, efficient MoE, strong performance-per-parameter, mainstream ecosystem support | Compare against Qwen3.6 and gpt-oss-20b for local coding, doc reasoning, and multimodal VisualOps tasks. |
| Granite 4.0 H-Tiny/H-Small | Trust posture, signed checkpoints, Apache, RAG/tool/cybersecurity enterprise focus | Use as buyer-safe RAG, policy, and support automation teacher where legal/provenance matters. |
| Phi-4-reasoning-vision-15B | MIT, compact, GUI/OCR/document reasoning emphasis | Use for VisualOps screenshot review and CUA verifier shadow tasks before reaching for paid multimodal APIs. |
| LFM2.5-VL-450M / LFM2.5-350M | Tiny open-weight edge models with ONNX/GGUF/MLX paths and tool/data extraction focus | Use for always-on local visual/data extraction canaries and Android/edge proof loops. |
| gpt-oss-safeguard-20b | Open safety model with custom policy reasoning | Use for local policy classification over MCP/tool requests, agent traces, and generated actions. |
| Nemotron 3 Nano | Open, efficient, agentic family with open data and recipes | Test as an agentic local helper and as an efficiency reference for NexusNet runtime scorecards. |
| DeepSeek V4-Flash | 13B active, 1M context, much cheaper than Pro class | Use as long-context teacher/evaluator where Kimi/GLM class is overkill. |
| GLM-5.1 | Long-horizon engineering and tool-use focus | Use for extended coding-agent benchmarks and tool-heavy plan execution against Kimi K2.6. |
| MiniMax M2.5 | Vendor claims strong coding, search, office, tool-use, and very low agentic runtime cost | Test against Kimi K2.6, GLM-5.1, Qwen3.6, and Devstral 2 on NexusNet SWE, spreadsheet/document, web research, and tool-loop tasks. |

## Recommended Open-First Teacher Ensemble

This is a live overlay, not a canon rewrite.

| Teacher layer | Primary open candidates | Reason |
|---|---|---|
| Central reasoning and planning | Kimi K2.6, DeepSeek V4-Pro, GLM-5.1, gpt-oss-120b | Strongest open-frontier style reasoning/agentic pool. |
| Practical local daily teacher | Qwen3.6-35B-A3B, Gemma 4 26B-A4B, Mistral Small 4, gpt-oss-20b | Better no-cost/local balance than relying on huge models. |
| Coding/SWE teacher | Kimi K2.6, GLM-5.1, MiniMax M2.5, Qwen3.6, Devstral 2, DeepSeek V4-Pro, gpt-oss-120b | Covers repo editing, long-horizon agentic engineering, and tool use. |
| Multimodal/VisualOps teacher | Kimi K2.6, Qwen3-VL, Qwen3.6, Gemma 4, Phi-4-reasoning-vision-15B, LFM2.5-VL | Open-first vision and GUI grounding before paid multimodal APIs. |
| Safety/policy teacher | gpt-oss-safeguard, Granite Guardian/Granite safety lineage, Llama Guard 4 if license passes, ClawGuard research | Local policy classification and tool-risk gates. |
| Enterprise/RAG/support teacher | Granite 4.0, Qwen3.6, Gemma 4, gpt-oss-20b | Cost-efficient, transparent, and buyer-friendly. |
| Long-context teacher | DeepSeek V4-Pro/Flash, Qwen3.6, Kimi K2.6, Llama 4 Scout as comparison | Use effective-context tests, not just advertised windows. |

## Research Papers And Technical Reports

Papers must become registry evidence. They should not directly mutate NexusNet behavior.

### Model And Architecture Papers

| Paper/report | Source | NexusNet use |
|---|---|---|
| Kimi K2: Open Agentic Intelligence | https://arxiv.org/abs/2507.20534 | MoE, MuonClip, agentic data synthesis, joint RL, open agentic teacher baseline. |
| Kimi K2.5: Visual Agentic Intelligence | https://arxiv.org/abs/2602.02276 | Multimodal agentic training, Agent Swarm, text/vision joint optimization. |
| Independent Safety Evaluation of Kimi K2.5 | https://arxiv.org/abs/2604.03121 | Required safety/adversarial evaluation pattern for powerful open teachers. |
| NVIDIA Nemotron 3: Efficient and Open Intelligence | https://arxiv.org/abs/2512.20856 | Hybrid Mamba-Transformer, LatentMoE, 1M context, MTP, RL budget control. |
| DeepSeek V4 technical report | https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/DeepSeek_V4.pdf | Hybrid attention, CSA/HCA efficiency, 1M context, expert consolidation. |
| DeepSeek-R1 | https://arxiv.org/abs/2501.12948 | Open reasoning RL, self-verification, distillation teacher references. |
| DeepSeek-V3 | https://arxiv.org/abs/2412.19437 | MLA, MoE efficiency, MTP, routing and long-context efficiency lineage. |
| GLM-5: from Vibe Coding to Agentic Engineering | https://arxiv.org/abs/2602.15763 | Long-horizon coding-agent and tool-use teacher design. |
| MiniMax-M1: Scaling Test-Time Compute Efficiently with Lightning Attention | https://arxiv.org/abs/2506.13585 | Hybrid attention, long-context reasoning, cost-efficient RL, and the M2.5 lineage for agentic coding/search. |
| Qwen3 Technical Report | https://arxiv.org/abs/2505.09388 | Qwen3 reasoning/agent foundation and Qwen3-VL citation lineage. |
| Qwen2.5-VL Technical Report | https://arxiv.org/abs/2502.13923 | Dedicated Qwen vision-language lineage for OCR, spatial reasoning, and GUI/visual tasks. |
| gpt-oss-120b and gpt-oss-20b Model Card | https://arxiv.org/abs/2508.10925 | Open reasoning model card, full reasoning access, agentic tool-use format. |
| Phi-4-reasoning Technical Report | https://arxiv.org/abs/2504.21318 | Compact reasoning distillation and teachable-prompt curation. |
| Phi-4-reasoning-vision-15B Technical Report | https://arxiv.org/abs/2603.03975 | Compact multimodal GUI/document/math reasoning. |
| Gemma 4 official technical materials | https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/ | Apache open models, local-first multimodal reasoning, edge models. |
| Llama 4 model card | https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E | Multimodal MoE, 1M/10M long-context comparison, license-risk example. |
| Granite 4.0 technical release | https://www.ibm.com/new/announcements/ibm-granite-4-0-hyper-efficient-high-performance-hybrid-models | Hybrid Mamba/Transformer efficiency, signed checkpoints, enterprise trust posture. |
| LFM2 Technical Report | https://arxiv.org/abs/2511.23404 | Edge-efficient hybrid backbone, multimodal/audio/retrieval variants, ExecuTorch/llama.cpp/vLLM deployment packages. |

### Memory, Graph, Harness, And Context Papers

| Paper/report | Source | NexusNet use |
|---|---|---|
| Zep/Graphiti temporal knowledge graph | https://arxiv.org/abs/2501.13956 | Typed temporal memory graph with provenance and updates. |
| MemOS | https://arxiv.org/abs/2507.03724 | Memory lifecycle, migration, scheduling, fusion, provenance, versioning. |
| A-MEM | https://openreview.net/pdf?id=LB0nTqxAKd | Agentic memory operations and evolving links. |
| AgeMem | https://arxiv.org/abs/2601.01885 | Age, decay, and retention policy for memory. |
| MemexRL | https://arxiv.org/abs/2603.04257 | Indexed experience memory and evidence dereferencing for effective context. |
| Meta-Harness | https://arxiv.org/abs/2603.28052 | Harness code and raw traces as optimization material. |
| Natural-Language Agent Harnesses | https://arxiv.org/abs/2603.25723 | Portable execution contracts and durable agent artifacts. |
| AutoHarness | https://arxiv.org/abs/2603.03329 | Task rules and constraints compiled into harness artifacts. |
| Graph-R1 | https://arxiv.org/abs/2507.21892 | Graph reasoning as multi-turn interaction for EBT/retrieval. |
| GraphRAG-R1 | https://huggingface.co/papers/2507.23581 | Graph-RAG reasoning and route evaluation. |

### Dreaming, RL, Evaluation, And Computer-Use Papers

| Paper/report | Source | NexusNet use |
|---|---|---|
| R-Zero | https://arxiv.org/abs/2508.05004 | Self-generated curricula and challenger/solver loops. |
| RAGEN | https://github.com/RAGEN-AI/RAGEN | Agent RL environment and trace/eval scaffolding. |
| Agent Lightning | https://arxiv.org/abs/2508.03680 | Separating runtime and training signals for agents. |
| Universal Verifier | https://arxiv.org/abs/2604.06240 | Process/outcome verification and CUA completion checks. |
| FARA-7B | https://arxiv.org/abs/2511.19663 | Computer-use/action proposal teacher under guarded execution. |
| DeepEyesV2 | https://arxiv.org/abs/2511.05271 | Agentic multimodal architecture influence. |
| OpenClaw security evaluation | https://arxiv.org/abs/2604.03131 | Tool-agent security evaluation. |
| OpenClaw PRISM | https://arxiv.org/abs/2603.11853 | Agent security threat-model patterns. |
| ClawGuard | https://arxiv.org/abs/2604.11790 | Defense candidate for tool-agent ecosystems. |
| MCP tool poisoning/security | https://arxiv.org/abs/2604.05969 | Required MCP threat model and registry scanning. |

## Inference Backend Catalog

NexusNet should not choose one backend globally. It should select by hardware, model format, quantization, context, safety, and telemetry.

| Backend | Source | Best fit | NexusNet status |
|---|---|---|---|
| vLLM | https://docs.vllm.ai/en/latest/ | High-throughput server inference, OpenAI-compatible serving, prefix caching, context extension, structured outputs, tool calling, metrics, distributed serving | Primary server/backend scorecard candidate. |
| SGLang | https://docs.sglang.io/ | Production low-latency/high-throughput inference, OpenAI APIs, RadixAttention lineage, structured generation, model gateway patterns | Primary server/backend scorecard candidate, especially for agentic workloads. |
| TensorRT-LLM | https://nvidia.github.io/TensorRT-LLM/ | NVIDIA optimized deployment, Blackwell/Hopper, TensorRT kernels, OpenAI/Responses examples, Prometheus metrics | Best NVIDIA production acceleration candidate. |
| llama.cpp | https://github.com/ggml-org/llama.cpp | Local-first GGUF, CPU/GPU fallback, quantized consumer hardware | Primary no-cost local fallback and GGUF path. |
| Ollama | https://docs.ollama.com/ | Simple local model management, Windows/macOS/Linux, Modelfile, context and hardware docs | User-friendly local provider adapter, not brain authority. |
| LM Studio | https://lmstudio.ai/docs | Local GUI, downloads, local REST/OpenAI-compatible API, Codex/Claude/OpenClaw/MCP integrations | Buyer/developer-friendly desktop adapter and testing surface. |
| Hugging Face TGI | https://huggingface.co/docs/text-generation-inference/index | Production HF serving, Prometheus/Grafana, quantization, tensor parallelism, PagedAttention, guidance/tools | Server runtime candidate and HF deployment path. |
| ExLlamaV2 | https://github.com/turboderp-org/exllamav2 | Consumer NVIDIA GPUs and EXL2/GPTQ-style quantized local inference | Specialist local GPU backend candidate. |
| Aphrodite Engine | https://github.com/aphrodite-engine/aphrodite-engine | Large-scale LLM inference, vLLM-adjacent serving patterns | Watchlist runtime, compare maturity and model support. |
| KTransformers | https://github.com/kvcache-ai/ktransformers | CPU-GPU heterogeneous inference and large sparse/MoE local experiments | Hidden large-model local experimentation candidate. |
| MLC LLM | https://llm.mlc.ai/docs/ | Cross-platform compiled deployment, WebLLM, iOS, Android, REST, CLI, quantization | Mobile/web/local deployment candidate. |
| ONNX Runtime GenAI | https://onnxruntime.ai/docs/genai/ | ONNX-backed Generate API, C#/web/edge workflows, Windows/mobile ecosystem | Windows/edge integration candidate. |
| OpenVINO GenAI | https://docs.openvino.ai/2025/openvino-workflow-generative.html | Intel CPU/GPU/NPU, model preparation, Optimum Intel, tokenizers | Intel local acceleration candidate. |
| ExecuTorch | https://docs.pytorch.org/executorch/stable/ | On-device PyTorch export/runtime, profiling/debugging/memory tools | Android/mobile runtime candidate. |
| MNN | https://github.com/alibaba/MNN | Lightweight on-device LLM/Edge AI engine, existing Nexus Android relevance | Keep as Android/local mobile candidate. |
| MLX | https://ml-explore.github.io/mlx/build/html/ | Apple Silicon native array/ML framework and local model serving ecosystem | Mac local performance candidate. |
| Transformers serve | https://huggingface.co/docs/transformers/main_classes/serving | Quick test/moderate-load serving and model compatibility baseline | Good compatibility fallback, not production default. |
| LMCache | https://docs.lmcache.ai/ | KV cache reuse and disaggregated serving patterns | Context/cache layer candidate, not standalone model runtime. |

## Backend Selection Rules

| Hardware/context | First backend to test | Why |
|---|---|---|
| Windows desktop, single consumer NVIDIA GPU | llama.cpp/LM Studio/Ollama, then vLLM or SGLang if model support works | Fastest path to no-cost local experiments. |
| Multi-GPU NVIDIA server | vLLM, SGLang, TensorRT-LLM | Throughput, metrics, distributed serving, large model support. |
| AMD/Intel/Linux server | vLLM/SGLang if supported, ONNX/OpenVINO for Intel | Avoid NVIDIA-only lock-in. |
| Apple Silicon | MLX, llama.cpp, Ollama/LM Studio | Local-first Mac performance and ergonomics. |
| Android/mobile | MNN, ExecuTorch, MLC LLM, ONNX Runtime | On-device deployment and native packaging relevance. |
| Huge MoE open models | SGLang, vLLM, TensorRT-LLM, KTransformers | Need MoE-aware serving, parallelism, cache strategy. |
| Buyer-friendly no-code local | LM Studio, Ollama | Easier packaging, local API, support handoff. |

## Runtime Scorecard Fields

Add these fields before any backend becomes a promoted NexusNet runtime:

- `backend_id`
- `version`
- `license`
- `host_os`
- `hardware_class`
- `model_formats`
- `quantization_formats`
- `openai_compatible_api`
- `tool_call_support`
- `structured_output_support`
- `vision_support`
- `audio_support`
- `context_limit_observed`
- `effective_context_score`
- `prefix_cache_support`
- `kv_cache_export_or_reuse`
- `batching_strategy`
- `telemetry_export`
- `security_sandbox`
- `offline_install_path`
- `buyer_support_risk`
- `last_verified_on`

## Open-First Implementation Priority

1. Seed `TeacherRegistryV2` with historical and live open-first rosters separated.
2. Seed `RuntimeBackendRegistry` with the backend catalog above.
3. Build a small benchmark harness before swapping models: repo edit, tool-call, long-context retrieval, screenshot/OCR, safety classification, RAG support, and "ask for proof" tasks.
4. Start local with Qwen3.6-35B-A3B, Gemma 4 26B-A4B, gpt-oss-20b, Granite 4.0, Phi-4-reasoning-vision-15B, and Mistral Small 4 quantized variants where available.
5. Use Kimi K2.6, DeepSeek V4-Pro/Flash, GLM-5.1, gpt-oss-120b, Nemotron 3, and Llama 4 as heavier teachers or hosted open-weight comparators.
6. Keep premium APIs out of the default path. Use them only for external review, red-team comparison, or temporary gaps.

## What To Demote

| Old/default idea | New status |
|---|---|
| Raw Mixtral plus Devstral weight surgery | Historical branch and research scaffold only; do not promote without architecture compatibility and eval proof. |
| Mixtral as automatic current open default | Preserve historically; live roster should benchmark newer MoE/open models first. |
| Devstral Small 1.1 as current coding default | Superseded by Devstral 2 per Mistral overview, and challenged by Kimi K2.6, GLM-5.1, Qwen3.6, DeepSeek V4, and gpt-oss. |
| Premium API teacher first | Optional external teacher only. Open/no-cost candidates are the default NexusNet attraction. |
| Single inference backend | Wrong abstraction. Use backend scorecards and hardware-specific runtime routing. |
| "1M context" as a marketing claim | Replace with measured effective context, retrieval proof, cache behavior, and evidence dereference coverage. |

## Candidate Registry Additions

Add these candidates to the live registry as `candidate`, not `promoted`:

- `model.kimi.k2_6`
- `model.kimi.k2_5`
- `model.deepseek.v4_pro`
- `model.deepseek.v4_flash`
- `model.qwen.qwen3_6_35b_a3b`
- `model.qwen.qwen3_vl_235b_a22b`
- `model.zai.glm_5_1`
- `model.minimax.m2_5`
- `model.mistral.small_4`
- `model.mistral.devstral_2`
- `model.openai.gpt_oss_120b`
- `model.openai.gpt_oss_20b`
- `model.openai.gpt_oss_safeguard`
- `model.google.gemma_4_26b_a4b`
- `model.ibm.granite_4_hybrid`
- `model.microsoft.phi_4_reasoning_vision_15b`
- `model.nvidia.nemotron_3`
- `model.liquid.lfm2_5`
- `model.liquid.lfm2_5_vl`
- `model.meta.llama_4_scout`
- `model.meta.llama_4_maverick`
- `runtime.vllm`
- `runtime.sglang`
- `runtime.tensorrt_llm`
- `runtime.llama_cpp`
- `runtime.ollama`
- `runtime.lm_studio`
- `runtime.hf_tgi`
- `runtime.exllamav2`
- `runtime.aphrodite`
- `runtime.ktransformers`
- `runtime.mlc_llm`
- `runtime.onnx_runtime_genai`
- `runtime.openvino_genai`
- `runtime.executorch`
- `runtime.mnn`
- `runtime.mlx`

## Open Questions Before Promotion

1. Which of the large open teachers can be run on the user's actual Windows hardware versus only through hosted inference?
2. Which quantized Qwen3.6, Gemma 4, gpt-oss, Granite, and Phi variants preserve enough quality for NexusNet's real tasks?
3. Which licenses are acceptable for commercial resale, especially Modified MIT attribution triggers, Llama 4 Community License thresholds, and NVIDIA Open Model License terms?
4. Which backends expose enough telemetry for VisualOps and EBT?
5. Which models handle NexusNet's actual historical-canon tasks, not just public benchmark tasks?
6. Which models produce safe, auditable tool calls under MCP/OpenClaw-style adversarial prompts?

## Bottom Line

The current open model landscape is strong enough that NexusNet should stay open-first by default. The best path is not to pick one replacement for Mixtral/Devstral. It is to make NexusNet prove which open teacher, specialist, and runtime wins for each role.

The first practical no-cost/local shortlist should be:

- Qwen3.6-35B-A3B
- Gemma 4 26B-A4B or E4B depending on hardware
- gpt-oss-20b
- Granite 4.0 H-Tiny/H-Small
- Phi-4-reasoning-vision-15B
- LFM2.5-350M / LFM2.5-VL for edge canaries
- Mistral Small 4 quantized when weights/runtime are pinned

The heavy open-frontier comparison pool should be:

- Kimi K2.6
- DeepSeek V4-Pro and V4-Flash
- GLM-5.1
- MiniMax M2.5
- gpt-oss-120b
- Nemotron 3 Super/Ultra when weights are available
- Llama 4 Scout/Maverick for multimodal/long-context comparison after license review

NexusNet should promote none of these by name alone. It should promote candidates only after the registry records license, runtime fit, measured task performance, effective context, safety behavior, and provenance.
