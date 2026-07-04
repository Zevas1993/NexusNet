# NexusNet Forward Research Deep Dive - 2026-04-28

Purpose: complete the research behind `docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md`. The radar names the living lanes. This document expands those lanes into source-backed findings, NexusNet implications, Control Panel surfaces, registry fields, risks, and promotion gates.

Research date: 2026-04-28.

Companion documents:

- `docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md`
- `docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md`
- `docs/NEXUSNET_COMPLETE_CANON_RESEARCH_REFRESH_DIFF_2026-04-28.md`
- `docs/NEXUSNET_COMPLETE_CANON_UPDATED_RESEARCH_CATALOG_2026-04-28.md`
- `docs/NEXUSNET_OPEN_FIRST_RESEARCH_EXPANSION_2026-04-28.md`

## Executive Result

The missing forward-looking work is not another model list. The research points to nine operating-system style registries NexusNet should treat as first-class brain assets:

| Registry | Why NexusNet needs it | Control Panel surface |
|---|---|---|
| `RuntimeWorkloadScorecard` | Quantization alone does not predict latency, context length, memory pressure, or concurrency. | Runtime posture, TTFT, ITL, throughput, memory, cache hit rate, cost-per-1k tokens. |
| `KVCacheLedger` | Prefix caching, KV reuse, disaggregated prefill/decode, and LMCache-style tiers change effective context economics. | Cache health, cache lineage, prompt reuse, eviction, privacy boundary. |
| `TraceSchemaRegistry` | Custom traces are not enough; agent traces should map to OpenTelemetry GenAI conventions. | Brain trace export, span explorer, redaction policy, OTel export status. |
| `ProtocolTrustEnvelope` | MCP, A2A, AG-UI, and ACP/A2A are protocol surfaces, not brain authority. | Adapter trust level, auth scope, signing, consent, sandbox, last audit. |
| `EvalSuiteRegistry` | Autonomous updates are not credible without held-out, versioned, task-realistic evals. | GAIA, tau-bench, OSWorld, SWE-bench, BrowserGym, NexusNet private suites. |
| `MemoryQualityLedger` | Memory must be measurable by retrieval, grounding, claim support, decay, and graph quality. | Retrieval diagnostics, source-to-claim map, graph health, contradiction queue. |
| `ArtifactTrustLedger` | Models, quant files, plugins, MCP tools, and generated patches are supply-chain artifacts. | Signatures, hashes, ML-BOM, license, scanner result, provenance. |
| `EdgeHardwareMatrix` | Buyer devices are diverging across CUDA, ROCm, DirectML/WinML, OpenVINO, QAIRT, MLX, WebNN, LiteRT, ExecuTorch, and browser WebGPU/WebNN. | Per-device runtime eligibility and expected workload shape. |
| `HarnessImprovementLedger` | Recent agent research shows the harness can be the improvement target. | Proposed harness diffs, self-review, shadow runs, holdout deltas, rollback. |

Bottom line: NexusNet should not present "support" as a binary label. The Control Panel should show `watch`, `candidate`, `shadow-test`, `pilot`, `promoted`, `blocked`, or `retired`, with source evidence and promotion gates visible.

## Cross-Track: Quantization Is Necessary But Insufficient

The separate quantization expansion already covers TurboQuant, MXFP4/NVFP4/FP4/FP8, GPTQ, AWQ, SmoothQuant, SpinQuant, QuaRot, HQQ, AQLM, KV quantization, GGUF, safetensors, MLX, and other file/runtime formats. That track remains required, but this deep dive treats quantization as one input to a broader runtime decision.

NexusNet should score a model/runtime lane by:

- model quality on role-specific evals,
- artifact trust and license status,
- weight quantization and activation/KV precision,
- prefill/decode topology,
- cache reuse strategy,
- batching/scheduler behavior,
- hardware backend fit,
- thermal and memory behavior,
- observability and rollback support.

Source anchors:

- TurboQuant paper: https://arxiv.org/abs/2504.19874
- Google Research TurboQuant post: https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/
- NexusNet quantization companion: `docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md`

## Lane 1: Inference Architecture Beyond Quantization

### Findings

Modern inference performance is increasingly governed by scheduling, cache reuse, and runtime topology:

- Speculative decoding can reduce decode latency by letting a draft mechanism propose multiple tokens and having the target model verify them. The vLLM docs now cover draft-model speculation, n-gram prompt lookup, suffix decoding, MLP speculators, and EAGLE-based draft models. Important caveat: vLLM currently warns that speculative decoding is not optimized for all datasets or sampling parameters and is not compatible with pipeline parallelism in that documented version.
- Suffix/n-gram speculation is especially relevant to agentic loops because repeated scaffolding, self-review, code edits, and tool-call boilerplate create repeated token patterns. That means NexusNet should not treat speculation as a generic speedup; it should score it per workload family.
- Disaggregated prefill/decode separates prompt processing from token generation. vLLM positions this as a way to tune time-to-first-token and inter-token latency separately, and to control tail inter-token latency when prefill jobs interfere with decode.
- Prefix caching and KV reuse are becoming durable runtime primitives. LMCache exposes a multi-tier KV cache layer across GPU memory, CPU DRAM, local disk/NVMe, and remote backends, and is explicitly designed to reuse KV caches across queries and engines.
- Cache economics now belongs in the product layer. A long canon prompt, repeated research context, repeated AO instructions, and stable operator shell state are exactly the cases where prefix/KV reuse can turn expensive context into reusable state.
- Continuous batching, paged attention, chunked prefill, and cache-aware routing should be treated as scheduler capabilities in the runtime scorecard, not hidden implementation details.

### NexusNet Implications

NexusNet should add a `RuntimeWorkloadScorecard` for every local/provider runtime:

| Field | Reason |
|---|---|
| `ttft_ms_p50`, `ttft_ms_p95` | Measures prefill and routing impact. |
| `itl_ms_p50`, `itl_ms_p95` | Measures decode quality for interactive chat. |
| `tokens_per_sec_decode` | User-visible generation speed. |
| `max_effective_context_tokens` | Reality check against advertised context. |
| `kv_cache_hit_rate` | Shows whether repeated context is reused. |
| `prefix_cache_hit_rate` | Separates stable prompt reuse from full cache reuse. |
| `cache_bytes_gpu`, `cache_bytes_cpu`, `cache_bytes_disk` | Makes memory pressure visible. |
| `cache_privacy_boundary` | Prevents cross-user or cross-project cache leakage. |
| `batching_mode` | `none`, `static`, `continuous`, `chunked_prefill`, `disaggregated_pd`. |
| `speculation_mode` | `none`, `draft_model`, `ngram`, `suffix`, `eagle`, `mlp_speculator`. |
| `spec_acceptance_rate` | Required before claiming speculation helps. |
| `eviction_policy` | Explains why context reuse failed. |
| `workload_fit` | `chat`, `research`, `coding`, `agent_loop`, `batch`, `long_context`, `multimodal`. |

### Control Panel Surface

Add `Runtime Lab` and `Cache Economics` panels:

- Runtime lane cards: model, format, backend, quantization, hardware, memory, TTFT, ITL, throughput, eval score.
- Cache ledger: cached prefixes, source hash, owner, privacy scope, last hit, eviction reason.
- Workload simulator: run a stable prompt pack across runtime candidates and compare raw vs cached behavior.
- Warning state: "fast quant, poor cache behavior" or "good throughput, bad tail latency."

### What Not To Do

- Do not rank runtimes by quant format alone.
- Do not expose shared cache across users/projects without a privacy scope.
- Do not enable speculative decoding by default without acceptance-rate telemetry.
- Do not sell raw context length as effective context unless retrieval, summarization, KV reuse, and latency are measured.

### Source Anchors

- vLLM speculative decoding: https://docs.vllm.ai/en/v0.13.0/features/spec_decode/
- vLLM disaggregated prefill: https://docs.vllm.ai/en/v0.11.2/features/disagg_prefill/
- LMCache architecture: https://docs.lmcache.ai/developer_guide/architecture.html
- LMCache paper: https://arxiv.org/abs/2510.09665
- TensorRT-LLM speculative decoding: https://nvidia.github.io/TensorRT-LLM/1.2.0rc6/features/speculative-decoding.html
- SGLang documentation overview: https://docs.sglang.ai/

## Lane 2: Agent Observability Standards

### Findings

OpenTelemetry GenAI conventions have moved far enough that NexusNet should map its custom traces to OTel-style spans:

- GenAI inference spans include operation, provider, request model, response model, token usage, server address, and error fields.
- The OTel GenAI spec includes operations such as `chat`, `embeddings`, `execute_tool`, `generate_content`, `invoke_agent`, `invoke_workflow`, and `retrieval`.
- Tool execution spans use fields such as `gen_ai.tool.name`, `gen_ai.tool.type`, `gen_ai.tool.call.id`, arguments, and result, with explicit warnings that arguments/results may contain sensitive data.
- Retrieval spans include data-source identifiers and opt-in retrieved document/query fields.
- The spec is still marked development in many places, so NexusNet should version its mapping and not hard-code it as permanent.

### NexusNet Implications

NexusNet should have a `TraceSchemaRegistry` with two layers:

| Layer | Purpose |
|---|---|
| Nexus-native trace | Brain/AO/expert/gate/memory/tool events in full local detail. |
| OTel export projection | Sanitized external trace shape that maps to OTel GenAI semantics. |

Mapping:

| NexusNet event | OTel-style operation |
|---|---|
| Brain route decision | `invoke_agent` or `invoke_workflow` |
| AO dispatch | `invoke_agent` |
| Expert capsule call | `invoke_agent` with `nexusnet.expert.role` attribute |
| Tool execution | `execute_tool` |
| Memory/RAG retrieval | `retrieval` |
| Model generation | `chat` or `generate_content` |
| Embedding update | `embeddings` |
| Self-review pass | `invoke_workflow` |
| Governance gate | Nexus custom span with OTel status/error mapping |

### Control Panel Surface

Add an `Observability` panel:

- Span waterfall for one operator action.
- Toggle between `Nexus Trace` and `OTel Projection`.
- Redaction preview before export.
- OTel collector/export status.
- Error taxonomy: model, tool, retrieval, policy, auth, cache, runtime, human-abort.

### What Not To Do

- Do not export prompts, tool arguments, retrieved documents, or tool results by default.
- Do not make OTel the only internal trace format; NexusNet needs richer brain-native events.
- Do not ignore OTel stability labels. Track spec version and export schema version.

### Source Anchors

- OTel GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OTel GenAI spans: https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/
- OTel GenAI events: https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/

## Lane 3: Agent Protocol Future

### Findings

The agent protocol space has split into complementary layers:

- MCP is the tool/resource/context access layer. Its 2026 roadmap emphasizes transport scalability, agent communication, governance maturation, and enterprise readiness.
- MCP security docs explicitly call out token passthrough, confused deputy risks, SSRF, session hijacking, local MCP server compromise, and least-privilege scope design.
- A2A is the agent-to-agent interoperability layer. It uses Agent Cards for identity/capability discovery, task/message/artifact concepts, auth declarations, and optional Agent Card signing.
- IBM's ACP is now described by IBM Research as part of A2A under the Linux Foundation, so NexusNet should track ACP as a historical/current migration item rather than a totally separate permanent lane.
- AG-UI is the agent-to-user-interface event protocol. It is relevant for streaming Control Panel state, human-in-the-loop updates, and frontend action proposals.

### NexusNet Implications

NexusNet should treat protocol integrations as adapters behind a `ProtocolTrustEnvelope`, never as authority:

| Field | Purpose |
|---|---|
| `protocol` | `mcp`, `a2a`, `ag-ui`, `acp_migrated`, `custom`. |
| `adapter_id` | Stable Nexus adapter identity. |
| `authority_level` | `observe_only`, `propose`, `read`, `write_limited`, `execute_limited`, `blocked`. |
| `auth_scheme` | OAuth/OIDC/JWT/API key/local token/none. |
| `token_audience_validated` | Required for remote MCP/A2A style calls. |
| `agent_card_signed` | Required before trusting A2A capabilities where signing exists. |
| `scopes_granted` | Least-privilege list. |
| `sandbox_profile` | Filesystem/network/process restrictions. |
| `human_consent_required` | Required for mutations, code execution, local process launch, secrets, or external network. |
| `last_security_review` | Date and result. |
| `known_blockers` | CVE, unsafe command, broad scopes, no auth, no signature, unclear license. |

### Control Panel Surface

Add `Protocol Governance`:

- MCP servers: local/remote, command line, scopes, sandbox, token audience, startup command diff.
- A2A agents: Agent Card, signature state, declared skills, auth scheme, task history.
- AG-UI streams: event types, UI proposal validation, mounted UI constraints, user approval state.
- ACP/A2A migration: show ACP items as `migrated_to_a2a` or `legacy_watch`.

### What Not To Do

- Do not let MCP tools, A2A agents, or AG-UI frontend proposals bypass NexusBrain.
- Do not trust local MCP startup commands without full command display and explicit consent.
- Do not accept broad tokens or token passthrough.
- Do not treat an Agent Card as trustworthy unless authenticity, freshness, and scope are checked.

### Source Anchors

- MCP 2026 roadmap: https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/
- MCP authorization: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- MCP security best practices: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- A2A specification: https://a2a-protocol.org/dev/specification/
- AG-UI docs: https://docs.ag-ui.com/
- AG-UI events: https://docs.ag-ui.com/sdk/js/core/events
- IBM ACP project note: https://research.ibm.com/projects/agent-communication-protocol

## Lane 4: Agent Eval Suite

### Findings

Agent benchmarks now cover different failure modes. NexusNet needs a portfolio, not one leaderboard:

- GAIA tests general-assistant behavior requiring reasoning, multimodal handling, browsing, and tool use. It is useful for research synthesis and tool use, but it is not enough for product safety.
- tau-bench focuses on dynamic user-agent-tool interactions with domain policy and database state checks. It is highly relevant to NexusNet's AO Hive because it scores consistency across repeated trials, not just a single success.
- OSWorld evaluates multimodal computer agents in real OS environments and added OSWorld-Verified improvements. It is directly relevant to VisualOps and operator-shell computer use.
- WebArena and BrowserGym cover browser agents and reproducible web tasks. WebArena showed a large gap between an early GPT-4 agent and human performance, which remains a useful reminder that "browser control" is not solved by model access alone.
- SWE-bench has grown into a family: Full, Lite, Verified, Multilingual, Multimodal, plus related tools such as SWE-agent, mini-SWE-agent, SWE-smith, CodeClash, and SWE-ReX. SWE-Bench Pro pushes into longer-horizon, multi-file enterprise tasks with held-out/commercial partitions.
- Benchmarks drift, get saturated, and can be contaminated. NexusNet should keep private held-out suites for its own canon, research, memory, security, runtime, protocol, and Control Panel behavior.

### NexusNet Implications

NexusNet should add `EvalSuiteRegistry`:

| Suite | Use in NexusNet |
|---|---|
| `nexus_research_synthesis_holdout` | Checks source-grounded research outputs, citations, contradiction handling. |
| `nexus_control_panel_truth_holdout` | Ensures UI status labels match live brain/runtime/protocol state. |
| `nexus_memory_grounding_holdout` | Verifies source-to-claim maps and retrieval faithfulness. |
| `nexus_runtime_fallback_holdout` | Tests model/backend fallback, cache disabled paths, failure honesty. |
| `nexus_tool_denial_holdout` | Ensures unsafe tool/protocol requests are refused or escalated. |
| `nexus_artifact_trust_holdout` | Tests model/plugin/download provenance and scanner gates. |
| `nexus_computer_use_sandbox_holdout` | Tests screen actions in a sandbox with state-based verification. |
| `nexus_autonomous_update_holdout` | Tests self-review and proposed patches without allowing silent promotion. |

Every eval result should store:

- suite id and version,
- task id and source,
- model/runtime/harness version,
- trace id,
- final score,
- cost/time/tokens,
- failure type,
- human override,
- promotion decision.

### Control Panel Surface

Add `Eval Center`:

- Public benchmark watch: GAIA, tau-bench, OSWorld, WebArena/BrowserGym, SWE-bench family.
- Nexus private holdouts: run history, pass/fail trend, contamination guard, frozen seed status.
- Promotion gate: no autonomous update, protocol adapter, runtime, or memory change can promote without eval deltas.

### What Not To Do

- Do not call an autonomous loop reliable because it passes a demo task.
- Do not let model/harness changes tune directly against the only held-out suite.
- Do not use LLM-as-judge alone for high-risk promotion. Use state checks where possible.

### Source Anchors

- GAIA: https://arxiv.org/abs/2311.12983
- tau-bench: https://arxiv.org/abs/2406.12045
- OSWorld: https://os-world.github.io/
- OSWorld paper: https://arxiv.org/abs/2404.07972
- WebArena: https://arxiv.org/abs/2307.13854
- BrowserGym: https://arxiv.org/abs/2412.05467
- SWE-bench: https://www.swebench.com/
- SWE-Bench Pro: https://arxiv.org/abs/2509.16941

## Lane 5: Memory, RAG, And Knowledge Graphs

### Findings

The current memory/RAG lane has three strong directions:

- GraphRAG-style systems use graph construction, community summaries, local search, global search, and DRIFT-style hybrid search to answer questions that require cross-document structure rather than single chunk retrieval.
- LightRAG combines graph structure with vector retrieval and emphasizes faster, simpler graph-augmented RAG with incremental updates. Its repository now includes storage/backend, evaluation, tracing, reranking, deletion/regeneration, and multimodal RAG developments.
- HippoRAG 2 frames retrieval as non-parametric memory with graph and Personalized PageRank-style retrieval, targeting factual, sense-making, and associative memory tasks.
- RAGChecker and RAGAS-style evaluation show that memory quality has to be measured at retrieval and generation layers. Claim-level diagnostics are especially important because a final answer can be fluent while unsupported by sources.

### NexusNet Implications

NexusNet should evolve HiveMind into a measurable Memory OS:

| Component | Role |
|---|---|
| `MemoryNode` | Atomic item with type, source, timestamp, owner, decay policy, confidence. |
| `EvidenceEdge` | Link between claim, source span, memory item, and generated answer. |
| `CommunitySummary` | GraphRAG-style summary for clusters of canon/research/runtime/tool knowledge. |
| `MemoryQualityLedger` | Retrieval recall, context precision, claim support, contradiction rate, stale source count. |
| `SourceToClaimMap` | Every important generated claim should be traceable to a source or marked as inference. |
| `ConsolidationRun` | Periodic merge/decay process with before/after metrics. |

### Control Panel Surface

Add `Memory Lab`:

- Graph health: nodes, edges, orphan nodes, stale clusters, contradiction clusters.
- Retrieval diagnostics: query, retrieved items, scores, used vs ignored evidence.
- Claim map viewer: generated claim -> source span -> retrieval event -> memory node.
- Consolidation queue: proposed merges, deletions, decays, conflicts, human approval.

### What Not To Do

- Do not replace all memory with a knowledge graph. Some facts should stay as exact evidence archives.
- Do not trust graph edges without source spans.
- Do not let memory consolidation rewrite canon without a provenance record.
- Do not use RAG metrics as product truth unless the eval set matches NexusNet workflows.

### Source Anchors

- Microsoft GraphRAG docs: https://microsoft.github.io/graphrag/
- GraphRAG DRIFT search blog: https://www.microsoft.com/en-us/research/blog/introducing-drift-search-combining-global-and-local-search-methods-to-improve-quality-and-efficiency/
- LightRAG paper: https://arxiv.org/abs/2410.05779
- LightRAG repository: https://github.com/HKUDS/LightRAG
- HippoRAG 2: https://arxiv.org/abs/2502.14802
- RAGChecker: https://arxiv.org/abs/2408.08067
- RAGAS: https://arxiv.org/abs/2309.15217

## Lane 6: AI Supply Chain Security

### Findings

NexusNet's "models and tools" are a software supply chain:

- Pickle-based model files can execute code when loaded. Hugging Face's security docs explicitly warn not to unpickle untrusted data and run pickle scanning on pushed pickled model files.
- safetensors exists specifically as a safer tensor-only format that avoids arbitrary code execution during deserialization.
- Sigstore model-transparency work recommends signing models and storing signatures/certificates in a transparency log so consumers can verify integrity.
- CycloneDX ML-BOM supports model/dataset/configuration transparency, provenance, dataset details, training methodology, framework configuration, and risk/compliance visibility.
- The same supply-chain thinking applies to GGUF files, ONNX models, LiteRT/ExecuTorch/OpenVINO exports, MCP servers, protocol adapters, generated patches, prompt packs, and Control Panel plugins.

### NexusNet Implications

NexusNet should add `ArtifactTrustLedger`:

| Field | Required for |
|---|---|
| `artifact_type` | model, quant, adapter, runtime, plugin, MCP server, A2A agent card, prompt pack, dataset, patch. |
| `source_url` | Every artifact. |
| `source_commit_or_revision` | Git/HF-backed artifacts. |
| `sha256` | Every downloaded/generated artifact. |
| `signature_status` | Signed/unsigned/verified/failed/unavailable. |
| `provenance_status` | Known training/export/source chain or unknown. |
| `ml_bom_path` | Model/dataset/runtime dependency summary. |
| `license_status` | allow, restricted, noncommercial, unknown, blocked. |
| `scanner_status` | safe, warning, malicious, unsupported, not_scanned. |
| `unsafe_format_flag` | pickle, executable installer, script startup, opaque binary, unknown. |
| `sandbox_required` | Whether artifact must run isolated. |
| `promotion_gate` | What must pass before operator-visible use. |

### Control Panel Surface

Add `Artifact Trust`:

- Model/plugin/tool inventory.
- Hash and signature verification status.
- License gate and commercial-use warnings.
- Unsafe format warnings for pickle or arbitrary-code loaders.
- MCP startup command review.
- ML-BOM/AI-BOM export for buyer/support packages.

### What Not To Do

- Do not treat safetensors as a complete security solution; it reduces deserialization risk but does not prove license, provenance, or model behavior.
- Do not run downloaded MCP servers or plugins without sandbox and consent.
- Do not let a model become "promoted" without hash, license, scanner result, and eval artifact.

### Source Anchors

- Hugging Face pickle scanning: https://huggingface.co/docs/hub/security-pickle
- safetensors: https://pytorch.org/projects/safetensors/
- Sigstore model transparency: https://blog.sigstore.dev/model-transparency-v1.0/
- Sigstore model-transparency repository: https://github.com/sigstore/model-transparency
- CycloneDX ML-BOM: https://cyclonedx.org/capabilities/mlbom/

## Lane 7: Edge, Browser, And Local Hardware Roadmap

### Findings

The local-first runtime map is fragmenting, which means NexusNet should not have one "local model" assumption:

- WebNN targets graph-based browser inference and is positioned as the only web API that can access NPUs directly, while also supporting CPU/GPU paths. WebGPU remains the broader browser GPU compute lane.
- LiteRT now positions GenAI deployment across mobile, desktop, and web, with LiteRT-LM handling LLM-specific concerns such as session cloning, KV-cache management, prompt caching/scoring, and stateful inference.
- ExecuTorch targets on-device model deployment, including LLM export to `.pte`, C++ runtime, Swift/Java bindings, and Android/iOS paths with XNNPACK, Qualcomm AI Engine, Core ML, MPS, Vulkan, MediaTek, OpenVINO, and other backends.
- ONNX Runtime GenAI provides the generative loop for ONNX models, including tokenization, preprocessing, inference, logits processing, sampling/search, chat templates, structured output, and KV cache management.
- OpenVINO GenAI has explicit NPU LLM pipeline performance hints for prompt processing and generation stages.
- AMD Quark/Ryzen AI, Qualcomm AI Hub/AI Stack/QAIRT, Apple MLX, Windows ML/DirectML/WinML, ROCm, CUDA, and Intel OpenVINO all need separate lanes because their artifact formats, driver maturity, and performance envelopes differ.

### NexusNet Implications

Add `EdgeHardwareMatrix`:

| Hardware lane | Runtime candidates | Notes |
|---|---|---|
| NVIDIA GPU | vLLM, TensorRT-LLM, llama.cpp CUDA, ONNX Runtime CUDA | Best for throughput and server-style local rigs. |
| AMD GPU/iGPU/NPU | ROCm where available, ONNX Runtime/WinML/DirectML, AMD Quark/Ryzen AI | Track Windows vs Linux support separately. |
| Intel CPU/GPU/NPU | OpenVINO GenAI, ONNX Runtime, llama.cpp | Good for buyer PCs and Core Ultra/NPU cases. |
| Apple silicon | MLX, llama.cpp Metal, Core ML, ExecuTorch iOS | Treat MLX as a first-class artifact format. |
| Android Qualcomm | LiteRT-LM, ExecuTorch Qualcomm backend, QAIRT/AI Hub, llama.cpp/Vulkan where practical | Phone thermals and memory matter as much as speed. |
| Android MediaTek/Pixel | LiteRT-LM, MediaTek delegate, Tensor ML SDK/Pixel paths | Track device/vendor availability. |
| Browser | WebGPU, WebNN, Transformers.js, ONNX Runtime Web, LiteRT web | Useful for thin Control Panel inference and private client-side tasks. |
| Windows AI PC | ONNX Runtime GenAI, WinML, DirectML, OpenVINO, AMD/Intel NPU paths | Must detect real EP availability, not only TOPS marketing. |

### Control Panel Surface

Add `Hardware Matrix`:

- Device inventory: CPU, GPU, NPU, RAM, VRAM, OS, driver/runtime versions.
- Runtime eligibility: supported, blocked, unverified, degraded.
- Artifact eligibility: GGUF, safetensors, MLX, ONNX, OpenVINO IR, LiteRT, ExecuTorch `.pte`.
- Thermal/soak status for local devices.
- "Advertised vs validated" flag for NPU/GPU acceleration.

### What Not To Do

- Do not assume NPU support means LLM decode is fast. Validate prompt/decode separately.
- Do not assume a model export format carries behavior parity.
- Do not mix browser/client-side inference with server-side trust without a data-boundary label.

### Source Anchors

- WebNN: https://webnn.io/en
- MDN WebGPU: https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API
- LiteRT GenAI: https://ai.google.dev/edge/litert/genai/overview
- ExecuTorch LLM deployment: https://docs.pytorch.org/executorch/stable/llm/getting-started.html
- ONNX Runtime GenAI: https://onnxruntime.ai/docs/genai/
- OpenVINO GenAI on NPU: https://docs.openvino.ai/2026/openvino-workflow-generative/inference-with-genai/inference-with-genai-on-npu.html
- Qualcomm AI developers: https://www.qualcomm.com/developer/artificial-intelligence
- AMD Quark for Ryzen AI: https://quark.docs.amd.com/release-0.9/supported_accelerators/ryzenai/
- Apple MLX research: https://machinelearning.apple.com/research/exploring-llms-mlx-m5

## Lane 8: Multimodal Computer Use

### Findings

Computer-use agents need perception, action, verification, and safety as separate layers:

- OSWorld and OSWorld-Verified provide real desktop task evaluation, setup, execution-based checks, and screenshot/accessibility-tree observation modes.
- OmniParser-style screen parsing converts screenshots into structured UI elements for pure vision GUI agents. This is useful when accessibility/DOM APIs are missing, but it should be treated as a perception layer with false-positive/false-negative risk.
- UI-TARS, Screen Agent, AndroidWorld, MobileWorld, VenusBench-Mobile, WebArena, BrowserGym, and Windows/desktop agent arenas show the same broad pattern: GUI action is brittle unless the agent has robust state verification, recovery, and sandboxing.
- OCR, VLM grounding, accessibility trees, DOM snapshots, audio ASR/TTS, document understanding, and file-system state checks are complementary signals. None should be the sole source of truth.

### NexusNet Implications

Add `ComputerUseSafetyCase` for every operator/computer-use workflow:

| Field | Purpose |
|---|---|
| `observation_sources` | screenshot, OCR, accessibility tree, DOM, OS state, logs, file diff, audio. |
| `action_channel` | browser automation, OS mouse/keyboard, app API, shell, file edit, network call. |
| `allowed_action_scope` | read-only, form-fill, local file, browser, shell, external system. |
| `verification_method` | state check, DOM check, file hash, screenshot match, log event, human approval. |
| `rollback_plan` | Undo path for mutation tasks. |
| `human_gate` | Required for payments, deletion, external send, credential use, system settings. |
| `privacy_class` | screenshot/document/audio sensitivity. |
| `eval_suite` | OSWorld/WebArena/BrowserGym/Nexus private task id. |

### Control Panel Surface

Add `VisualOps`:

- Live perception stack: screenshot, OCR, a11y/DOM tree, parsed UI elements.
- Action proposal card: target element, coordinates, action, expected state change, risk.
- Verification pane: before/after state, file diff, DOM diff, screenshot diff, logs.
- Human gate queue for irreversible or external actions.

### What Not To Do

- Do not let screenshot-only perception directly execute high-risk actions.
- Do not rely only on a VLM saying "done" for verification.
- Do not store screenshots/audio/documents in memory without privacy classification and retention rules.

### Source Anchors

- OSWorld: https://os-world.github.io/
- OSWorld paper: https://arxiv.org/abs/2404.07972
- OmniParser repository: https://github.com/microsoft/OmniParser
- AndroidWorld paper: https://arxiv.org/abs/2405.14573
- MobileWorld: https://arxiv.org/abs/2512.19432
- VenusBench-Mobile: https://arxiv.org/abs/2604.06182
- WebArena: https://arxiv.org/abs/2307.13854
- BrowserGym: https://arxiv.org/abs/2412.05467

## Lane 9: Autonomous Update, Self-Review, And Harness Benchmarks

### Findings

The 2025-2026 agent research trend is that the harness, not just the model, is a major capability lever:

- SWE-agent showed that agent-computer interfaces can materially affect software engineering performance.
- OpenHands emphasizes sandboxed execution, trace capture, and scalable evaluation for coding agents.
- AutoHarness and Meta-Harness research argue that agents can synthesize or optimize scaffolding/harnesses, but this creates a governance problem: the system must not silently optimize itself against the wrong objective or leak into held-out tests.
- SWE-Skills-Bench-style work asks whether named agent skills actually help, which is exactly the question NexusNet needs for AO capsules, expert roles, and self-review loops.

### NexusNet Implications

NexusNet should separate four concepts that are often blurred:

| Concept | NexusNet meaning |
|---|---|
| Self-review | The agent critiques its own output before surfacing or promoting it. |
| Autonomous update proposal | The agent proposes a code/config/research change but cannot promote it alone. |
| Harness optimization | The system changes prompt/tool/retry/verification scaffolding. |
| Native evolution | Long-term improvement loop; must stay shadow-only until eval and governance are mature. |

Add `HarnessImprovementLedger`:

- proposed change,
- motivation trace,
- training/eval data touched,
- holdout firewall status,
- before/after public evals,
- before/after Nexus private evals,
- cost delta,
- risk delta,
- rollback artifact,
- human approval.

### Control Panel Surface

Add `Evolution Lab`:

- Self-review queue.
- Proposed autonomous updates.
- Harness diff viewer.
- Shadow-run result.
- Held-out eval guard.
- Promotion provenance.
- Rollback button for pilot/promoted changes.

### What Not To Do

- Do not give an autonomous update loop write authority over its own eval gate.
- Do not optimize prompts/harnesses against the same benchmark used for public claims.
- Do not let self-review hide uncertainty from the operator.

### Source Anchors

- SWE-agent: https://arxiv.org/abs/2405.15793
- OpenHands SWE-bench evaluation: https://openhands.dev/blog/evaluation-of-llms-as-coding-agents-on-swe-bench-at-30x-speed
- OpenHands Index: https://openhands.dev/blog/openhands-index
- AutoHarness: https://arxiv.org/abs/2603.03329
- AutoHarness OpenReview: https://openreview.net/forum?id=g9rEYVNn5T
- Meta-Harness: https://arxiv.org/abs/2603.28052
- SWE-Skills-Bench: https://arxiv.org/abs/2603.15401

## Control Panel Build Requirements From This Research

The Control Panel should include these top-level pages or tabs:

| Page | Required views |
|---|---|
| Forward Radar | Live research lane states, freshness, source list, next review trigger. |
| Runtime Lab | Model/runtime/hardware/quant/cache scorecards and benchmark comparisons. |
| Cache Economics | Prefix/KV reuse, cache tiers, privacy scope, hit/miss/eviction telemetry. |
| Observability | Nexus trace, OTel projection, redaction preview, export status. |
| Protocol Governance | MCP/A2A/AG-UI/ACP adapters, consent, auth scopes, sandbox, signing. |
| Eval Center | Public benchmarks, Nexus private suites, promotion gates, failure clusters. |
| Memory Lab | Graph health, source-to-claim maps, retrieval diagnostics, consolidation queue. |
| Artifact Trust | Model/plugin/tool provenance, signatures, ML-BOM, scanner/license status. |
| Hardware Matrix | Device inventory, backend eligibility, validated vs advertised acceleration. |
| VisualOps | Screen/OCR/a11y/DOM perception, action proposals, verification state. |
| Evolution Lab | Self-review, harness diffs, shadow runs, held-out eval gates, rollback. |

## API Shapes To Reserve

These endpoint names are intentionally descriptive placeholders for future implementation:

- `GET /ops/brain/forward-radar`
- `GET /ops/brain/forward-radar/{radar_id}`
- `POST /ops/brain/forward-radar/{radar_id}/review`
- `GET /ops/brain/runtime-scorecards`
- `GET /ops/brain/cache-ledger`
- `GET /ops/brain/trace-schema`
- `GET /ops/brain/trace-schema/otel-projection/{trace_id}`
- `GET /ops/brain/protocol-trust`
- `GET /ops/brain/eval-suites`
- `POST /ops/brain/eval-suites/{suite_id}/run-shadow`
- `GET /ops/brain/memory-quality`
- `GET /ops/brain/artifact-trust`
- `GET /ops/brain/hardware-matrix`
- `GET /ops/brain/computer-use/safety-cases`
- `GET /ops/brain/evolution/harness-ledger`

## Promotion Rules

No forward-radar item should be promoted unless all applicable checks pass:

| Gate | Required evidence |
|---|---|
| Source gate | Official docs, paper, reference code, or verified benchmark. |
| License gate | Commercial/local use terms recorded. |
| Security gate | Artifact/protocol/tool risk reviewed. |
| Runtime gate | Hardware and performance measured on target class. |
| Eval gate | Public or Nexus private eval passes with trace artifact. |
| Observability gate | Trace/export behavior available or explicitly not applicable. |
| Rollback gate | Rollback path exists for pilot/promoted items. |
| Operator gate | Control Panel can explain status, risk, and next action. |

## Final Bottom Line

The forward-focused update for NexusNet is a governed evidence system:

- Inference becomes a runtime and cache economy problem, not only a quantization problem.
- Agent behavior becomes observable through Nexus-native traces with OTel export projections.
- Protocols become sandboxed trust envelopes, not authority.
- Memory becomes measurable through retrieval, graph, and claim-support diagnostics.
- Autonomous evolution becomes a shadow-tested harness workflow with held-out gates.
- Local-first becomes a hardware matrix across real backends and artifact formats.
- Computer use becomes a perception/action/verification/safety stack.

This is the research basis that should feed the Control Panel build.
