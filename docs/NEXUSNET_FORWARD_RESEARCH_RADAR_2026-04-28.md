# NexusNet Forward Research Radar - 2026-04-28

Purpose: define a living research track for the technologies that can change NexusNet's architecture after the quantization and agentic research pass. This document is not a feature implementation. It is the forward-looking radar NexusNet should keep current so the Control Panel, brain authority, AO Hive, runtime planning, memory layer, and autonomous update gates do not freeze around one date's assumptions.

Primary local sources:

- `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`
- `docs/NEXUSNET_COMPLETE_CANON_RESEARCH_REFRESH_DIFF_2026-04-28.md`
- `docs/NEXUSNET_OPEN_FIRST_RESEARCH_EXPANSION_2026-04-28.md`
- `docs/NEXUSNET_RESEARCH_CANDIDATE_DOSSIER_2026-04-28.md`
- `docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md`
- `docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md`
- `F:\AndroidLLMApp\deep-research-report.md`
- `F:\NexusNet\NexusNet\.worktrees\nexusnet-full-product-sweep\docs\NEXUSNET_FULL_PRODUCT_SWEEP_ROADMAP.md`

Research date: 2026-04-28.

Deep-dive companion: `docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md` expands the lanes below into source-backed findings, NexusNet implications, Control Panel surfaces, registry fields, risks, and promotion gates.

## Executive Finding

The next missing research layer is a standing radar, not a one-time list. NexusNet already has a strong direction: brain-first control, AO specialization, governed protocols, evidence-led research candidates, runtime/model planning, and product-sweep gates. What can make it stale fastest is the pace of change in:

1. inference architecture,
2. agent observability,
3. agent protocols,
4. agent and computer-use evals,
5. memory/RAG/knowledge-graph methods,
6. AI/model supply-chain security,
7. edge/browser/local hardware runtimes,
8. multimodal computer-use workflows,
9. autonomous update and harness benchmarks.

The Control Panel should expose these as a `Forward Radar` surface with freshness, evidence, maturity, impact, and promotion gates. A future-focused NexusNet should not say "supported" because a technology exists. It should say: watched, candidate, shadow-tested, blocked, promoted, or retired, with the reason visible.

## Radar Method

Every forward-radar item should be tracked with the same promotion discipline as product-sweep candidates.

| Radar state | Meaning | Operator behavior |
|---|---|---|
| `watch` | Technology is relevant but not yet actionable. | Show source, freshness, and reason for watching. |
| `candidate` | There is enough public evidence to map to NexusNet. | Create a registry record and owner layer. |
| `shadow-test` | A non-production benchmark or prototype is possible. | Require eval artifact, rollback plan, and blocked-runtime reason. |
| `pilot` | Limited operator-visible integration is safe. | Show warnings, scope, and measured deltas. |
| `promoted` | Meets license, security, eval, runtime, and support gates. | Can appear as a real capability. |
| `blocked` | Fails security, license, reliability, or product fit. | Show the blocker and next review trigger. |
| `retired` | No longer worth tracking or was replaced. | Keep provenance so old decisions are explainable. |

Required common fields:

- `radar_id`
- `display_name`
- `category`
- `source_urls`
- `source_kind`: `official_docs`, `paper`, `reference_code`, `vendor_blog`, `benchmark`, `community_signal`
- `first_seen_on`
- `last_reviewed_on`
- `freshness_window_days`
- `maturity`: `paper_only`, `reference_code`, `runtime_integrated`, `production_runtime`, `standardizing`, `mature`
- `nexusnet_layer`: `brain`, `ao_hive`, `memory`, `runtime`, `protocol`, `control_panel`, `security`, `training`, `product_packaging`
- `operator_surface_required`
- `evidence_artifacts`
- `risk_level`
- `promotion_status`
- `blocked_reason`
- `next_review_trigger`

## Priority Radar Table

| Priority | Research lane | Why it matters to NexusNet | Initial status |
|---|---|---|---|
| P0 | Inference architecture beyond quantization | Quantized files do not guarantee low latency, long context, or concurrency. Scheduling, prefill/decode split, KV reuse, speculative decode, and cache tiers can matter more than a quant name. | Add now. |
| P0 | Agent observability standards | NexusNet's Control Panel should be able to export traces that enterprise tools understand, not only custom local JSON. | Add now. |
| P0 | Agent protocol future | MCP, A2A, AG-UI, ACP, identity, and delegation are becoming the network layer of agent systems. NexusNet needs governed interoperability without surrendering authority. | Add now. |
| P0 | Agent and computer-use evals | Autonomous updates and AO behavior are not credible unless evaluated against changing, task-realistic benchmarks plus NexusNet's own held-out suites. | Add now. |
| P1 | Memory, RAG, and knowledge graphs | NexusNet's memory layer should be measured by retrieval quality, source grounding, claim maps, and graph recall, not only by stored context volume. | Add now. |
| P1 | AI supply-chain security | Model packages, quantizers, runtime plugins, MCP tools, and agent patches are supply-chain artifacts and need provenance, signatures, scanning, and sandbox policy. | Add now. |
| P1 | Edge, browser, and local hardware runtimes | Buyer machines are moving toward NPU/GPU/browser/on-device inference. NexusNet needs runtime scorecards per hardware class. | Add now. |
| P1 | Multimodal computer use | VisualOps and operator-shell workflows need real desktop/browser/app evals, not only chat tests. | Add now. |
| P2 | Product intelligence and buyer support | Future readiness is also documentation, diagnostics, artifact portability, privacy, and support surface quality. | Add after P0/P1 registry surfaces. |

## Lane 1: Inference Architecture Beyond Quantization

Current public finding:

- vLLM documents speculative decoding, disaggregated prefilling, automatic prefix caching, quantized KV cache, and related serving features.
- LMCache adds a multi-tier KV cache layer for engines such as vLLM and SGLang, including GPU/CPU/disk/remote storage and reuse across queries or sessions.
- Research and runtime work around stored KV reuse, non-prefix cache reuse, prefill/decode disaggregation, and speculative decoding changes the effective context and throughput story.

Source anchors:

- [vLLM speculative decoding](https://docs.vllm.ai/en/v0.13.0/features/spec_decode/)
- [vLLM disaggregated prefilling](https://docs.vllm.ai/en/v0.11.2/features/disagg_prefill/)
- [LMCache architecture](https://docs.lmcache.ai/developer_guide/architecture.html)
- [LMCache paper](https://arxiv.org/abs/2510.09665)
- [Stored KV cache reuse paper](https://arxiv.org/abs/2503.14647)

NexusNet implication:

- Add `InferenceArchitectureScorecard` beside `RuntimeCapabilityScorecard`.
- Track runtime behavior that affects throughput and long context: `continuous_batching`, `speculative_decode`, `draft_model`, `prefix_cache`, `non_prefix_kv_reuse`, `kv_cache_tiers`, `prefill_decode_disaggregation`, `chunked_prefill`, `scheduler_policy`, `latency_p50`, `latency_p95`, `ttft`, `tokens_per_second`, `concurrency`, and `cost_per_1k_tokens`.
- Control Panel must separate "model can load" from "model can serve the expected workload."

Recommended action:

- Promote this lane to P0 research and Control Panel design.
- Treat all runtime throughput claims as untrusted until NexusNet has local benchmark artifacts per model/runtime/device tuple.

## Lane 2: Agent Observability Standards

Current public finding:

- OpenTelemetry has GenAI semantic conventions for LLM calls, agents, tool execution, and framework spans.
- The agent span conventions are still marked development, which means NexusNet should map to them cautiously but early.

Source anchors:

- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [OpenTelemetry GenAI agent spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/)
- [OpenTelemetry AI agent observability blog](https://opentelemetry.io/blog/2025/ai-agent-observability/)

NexusNet implication:

- Add `TelemetrySchemaRegistry`.
- Store each AO/expert/tool invocation as both native NexusNet trace and OTel-compatible projection.
- Required fields: `trace_id`, `span_id`, `agent_name`, `ao_id`, `tool_id`, `model_id`, `runtime_id`, `input_tokens`, `output_tokens`, `cached_tokens`, `latency_ms`, `error_type`, `retry_count`, `budget_spent`, `artifact_links`, `redaction_policy`, and `otel_mapping_version`.

Recommended action:

- Add a Control Panel "Trace Standards" page showing which traces are exportable, redacted, blocked, or local-only.
- Do not export prompt/completion content by default. Make content capture an explicit operator opt-in with redaction policy.

## Lane 3: Agent Protocol Future

Current public finding:

- MCP's 2026 roadmap emphasizes transport scalability, agent communication, governance maturity, and enterprise readiness.
- A2A is an open protocol for independent agents to communicate and interoperate.
- AG-UI standardizes agent-to-frontend event streams, state deltas, messages, tool call events, and long-running interaction patterns.
- ACP and related agent communication proposals point toward a fragmented but converging protocol space.

Source anchors:

- [MCP roadmap](https://modelcontextprotocol.io/development/roadmap)
- [MCP 2026 roadmap post](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)
- [A2A specification](https://a2a-protocol.org/dev/specification/)
- [AG-UI overview](https://docs.ag-ui.com/)
- [AG-UI events](https://docs.ag-ui.com/sdk/js/core/events)
- [IBM ACP project](https://research.ibm.com/projects/agent-communication-protocol)

NexusNet implication:

- NexusNet should keep its brain authority above protocols. Protocols are adapters, not authority.
- Add `ProtocolInteropRecord`: `protocol`, `version`, `direction`, `transport`, `identity_model`, `permission_model`, `sandbox_required`, `tool_surface`, `data_surface`, `event_surface`, `handoff_support`, `known_risks`, `policy_status`, and `kill_switch`.
- Keep MCP/A2A/AG-UI/ACP behind governed adapters and explicit operator consent.

Recommended action:

- Add a Control Panel "Protocol Radar" page.
- Every external agent, MCP server, A2A peer, or AG-UI frontend must show trust state, permissions, and execution boundaries.

## Lane 4: Agent And Computer-Use Evals

Current public finding:

- GAIA evaluates general assistant tasks requiring reasoning, tool use, and multi-step work.
- tau-bench evaluates tool-agent-user interaction in realistic domains.
- OSWorld evaluates multimodal agents in real desktop/web environments, with execution-based tasks and a verified benchmark update.
- SWE-bench remains important for coding agents, but must not be treated as the only signal. Its value depends on scaffold, data freshness, task quality, and whether the task resembles NexusNet work.

Source anchors:

- [GAIA arXiv](https://arxiv.org/abs/2311.12983)
- [GAIA Hugging Face page](https://huggingface.co/papers/2311.12983)
- [tau-bench arXiv](https://arxiv.org/abs/2406.12045)
- [tau-bench project](https://sierra.ai/resources/research/tau-bench)
- [OSWorld project](https://os-world.github.io/)
- [OSWorld arXiv](https://arxiv.org/abs/2404.07972)
- [SWE-bench official leaderboard](https://www.swebench.com/)
- [ASTRA-bench arXiv](https://arxiv.org/abs/2603.01357)

NexusNet implication:

- Add `AgentEvalScorecard`.
- Track eval family, task class, scaffold, tool permissions, model, runtime, context budget, cost, success, retries, hallucinated tool calls, unsafe actions, and verifier method.
- Add NexusNet-owned held-out evals for: product-sweep review, candidate license review, quantized model selection, runtime fallback, Control Panel state truthfulness, research synthesis, and autonomous patch proposals.

Recommended action:

- Treat external leaderboards as weak signals.
- Promote only on NexusNet-local evals with raw traces and deterministic replay where possible.

## Lane 5: Memory, RAG, And Knowledge Graphs

Current public finding:

- Microsoft GraphRAG separates local, global, DRIFT, basic search, and question generation over graph indexes.
- LightRAG combines graph structures with vector representations and includes incremental update behavior.
- RAGChecker provides fine-grained metrics for retrieval and generation modules.
- Memory quality depends on source-to-claim mapping, retrieval precision, recall, freshness, and contradiction handling.

Source anchors:

- [GraphRAG query overview](https://microsoft.github.io/graphrag/query/overview/)
- [Microsoft GraphRAG dynamic global search](https://www.microsoft.com/en-us/research/blog/graphrag-improving-global-search-via-dynamic-community-selection/)
- [LightRAG arXiv](https://arxiv.org/abs/2410.05779)
- [LightRAG GitHub](https://github.com/HKUDS/LightRAG)
- [RAGChecker arXiv](https://arxiv.org/abs/2408.08067)

NexusNet implication:

- Add `MemoryEvidenceScorecard`.
- Track `retrieval_mode`, `graph_mode`, `entity_resolution`, `claim_map`, `source_freshness`, `citation_coverage`, `contradiction_count`, `staleness_warning`, `retrieval_precision`, `retrieval_recall`, `answer_groundedness`, and `memory_write_policy`.
- NexusNet memory should be governed by evidence and decay, not just accumulation.

Recommended action:

- Add a Control Panel "Memory Quality" page separate from Context & Memory volume.
- Store source-to-claim maps for research artifacts and buyer-facing answers.

## Lane 6: AI And Model Supply-Chain Security

Current public finding:

- Hugging Face documents pickle risks, Hub scans, signed commits, and safetensors as a safer tensor serialization option.
- Sigstore model-transparency work applies signing and verification to ML models and uses transparency logs for auditability.
- Model packages, conversion scripts, quantizers, runtime plugins, MCP tools, and autonomous patches are all supply-chain artifacts.

Source anchors:

- [Hugging Face pickle scanning](https://huggingface.co/docs/hub/security-pickle)
- [PyTorch safetensors page](https://pytorch.org/projects/safetensors/)
- [Sigstore model transparency](https://blog.sigstore.dev/model-transparency-v1.0/)
- [Sigstore model-transparency GitHub](https://github.com/sigstore/model-transparency)
- [Sigstore security model](https://docs.sigstore.dev/about/security/)

NexusNet implication:

- Add `SupplyChainTrustRecord`.
- Track `artifact_type`, `artifact_url`, `digest`, `signature`, `signature_provider`, `transparency_log`, `sbom_or_aibom`, `serialization_format`, `pickle_present`, `scanner_results`, `license_status`, `runtime_permissions`, `sandbox_profile`, `network_access`, `install_path`, and `rollback_artifact`.
- A quantized model that performs well but has weak provenance should remain candidate-only.

Recommended action:

- Add a Control Panel "Artifact Trust" page.
- Fail closed on unsigned/high-risk executable artifacts unless an operator explicitly approves a quarantined shadow test.

## Lane 7: Edge, Browser, And Local Hardware Runtimes

Current public finding:

- WebNN exposes browser-side graph execution with NPU/GPU/CPU backends and is specifically positioned for web inference.
- Google LiteRT/LiteRT-LM targets on-device GenAI across mobile, desktop, and web, including session cloning, KV-cache management, prompt caching/scoring, and stateful inference.
- Apple's MLX is increasingly important for Apple Silicon local inference and quantization.
- Qualcomm AI Hub and Qualcomm AI Stack target optimized on-device deployment across Android, Windows, Linux, and Snapdragon-class hardware.

Source anchors:

- [WebNN docs](https://webnn.io/en)
- [LiteRT GenAI overview](https://ai.google.dev/edge/litert/genai/overview)
- [LiteRT overview](https://ai.google.dev/edge/litert/overview)
- [LiteRT-LM GitHub](https://github.com/google-ai-edge/LiteRT-LM)
- [Apple MLX LLM research](https://machinelearning.apple.com/research/exploring-llms-mlx-m5)
- [Qualcomm AI Hub](https://aihub.qualcomm.com/)
- [Qualcomm AI Hub get started](https://aihub.qualcomm.com/get-started)

NexusNet implication:

- Add `EdgeDeploymentCapability`.
- Track `platform`, `runtime`, `accelerator`, `driver_or_sdk`, `model_format`, `quant_format`, `conversion_path`, `offline_install`, `browser_support`, `npu_support`, `gpu_support`, `battery_profile`, `thermal_profile`, `memory_ceiling`, `fallback_runtime`, and `buyer_support_risk`.
- Treat edge/browser/hardware as separate product lanes, not one generic "local runtime."

Recommended action:

- Add a Control Panel "Edge Runtime Radar" page.
- Include buyer-machine diagnostics for whether WebNN, WebGPU, DirectML, Core ML, MLX, OpenVINO, Qualcomm, or Android LiteRT paths are actually usable.

## Lane 8: Multimodal Computer Use And VisualOps

Current public finding:

- OSWorld and related computer-use benchmarks show that real desktop/web/app tasks are a separate capability class from chat or API-only tool use.
- Computer-use safety and reliability depend on screenshots, UI trees, action traces, file system effects, rollback, and human interruption.

Source anchors:

- [OSWorld project](https://os-world.github.io/)
- [OSWorld arXiv](https://arxiv.org/abs/2404.07972)
- [OSWorld-MCP arXiv](https://arxiv.org/abs/2510.24563)
- [RiOSWorld arXiv](https://arxiv.org/abs/2506.00618)

NexusNet implication:

- Add `ComputerUseCapabilityRecord`.
- Track `observation_mode`, `action_space`, `screen_capture`, `ui_tree`, `tool_invocation`, `human_interrupt`, `safe_action_policy`, `rollback_available`, `screenshot_artifacts`, `replay_artifacts`, and `risk_category`.
- VisualOps must prove action safety and replayability before it can be called autonomous.

Recommended action:

- Add a Control Panel "Computer Use Lab" page.
- Start with read-only/sandboxed workflows before write-capable OS/browser actions.

## Lane 9: Autonomous Update And Harness Benchmarks

Current public finding:

- The prior quantization/agentic expansion already covered Meta-Harness, Natural-Language Agent Harnesses, AutoHarness, SWE-agent, AutoCodeRover, and OpenHands.
- The missing radar piece is the evaluation cadence: autonomous update systems should be compared against fresh tasks, held-out NexusNet tasks, and harness-regression checks.

Source anchors:

- [Meta-Harness arXiv](https://arxiv.org/abs/2603.28052)
- [Natural-Language Agent Harnesses arXiv](https://arxiv.org/abs/2603.25723)
- [AutoHarness arXiv](https://arxiv.org/abs/2603.03329)
- [SWE-agent GitHub](https://github.com/SWE-agent/SWE-agent)
- [AutoCodeRover arXiv](https://arxiv.org/abs/2404.05427)
- [OpenHands GitHub](https://github.com/OpenHands/OpenHands)

NexusNet implication:

- Add `AutonomousUpdateBenchmarkRecord`.
- Track `task_source`, `task_freshness`, `repository_snapshot`, `allowed_tools`, `patch_scope`, `tests_run`, `regression_result`, `security_review`, `human_review`, `cost`, `time_to_patch`, `rollback_plan`, and `promotion_authority`.
- Autonomous updates must remain branch/proposal/shadow-test gated.

Recommended action:

- Add a Control Panel "Autonomous Update Eval" page.
- Require at least one NexusNet-owned held-out task family before enabling any autonomous patch promotion flow.

## Control Panel Additions Required By This Radar

The Control Panel should add these surfaces after the currently planned quantization/runtime/research/self-review/harness surfaces:

1. Forward Radar
   - master list of watched technologies, maturity, freshness, owners, risk, and next review trigger.

2. Inference Architecture
   - serving features beyond model format: cache, scheduler, decode, prefill, batching, and concurrency behavior.

3. Trace Standards
   - NexusNet trace fields and OpenTelemetry GenAI mapping status.

4. Protocol Radar
   - MCP/A2A/AG-UI/ACP status, trust, permission, adapter state, and kill switch.

5. Evaluation Lab
   - external benchmarks, NexusNet held-out suites, raw trace links, and replay status.

6. Memory Quality
   - source-to-claim maps, retrieval quality, graph health, freshness, contradiction handling, and RAG diagnostics.

7. Artifact Trust
   - model/package/plugin/patch provenance, signatures, scanning, license, sandbox, and rollback.

8. Edge Runtime Radar
   - browser, NPU, GPU, mobile, Apple Silicon, Windows AI PC, Android, and web deployment fit.

9. Computer Use Lab
   - VisualOps and OS/browser action traces with safety, replay, and rollback state.

10. Autonomous Update Eval
   - patch proposal quality, harness metrics, held-out tests, security review, and promotion gate state.

## API Shapes To Reserve

These endpoints should be reserved before the Control Panel UI is called complete:

1. `GET /ops/brain/forward-radar/items`
2. `GET /ops/brain/forward-radar/summary`
3. `GET /ops/brain/inference/architecture-scorecards`
4. `GET /ops/brain/telemetry/schema-map`
5. `GET /ops/brain/protocol/radar`
6. `GET /ops/brain/evals/agent-scorecards`
7. `GET /ops/brain/memory/quality`
8. `GET /ops/brain/artifacts/trust`
9. `GET /ops/brain/edge-runtime/radar`
10. `GET /ops/brain/computer-use/lab`
11. `GET /ops/brain/autonomous-updates/evals`

## Refresh Cadence

| Cadence | What to refresh | Trigger |
|---|---|---|
| Weekly | Runtime docs, protocol docs, benchmark leaderboards, security advisories | Before Control Panel build claims or public demo. |
| Monthly | Full radar review, source freshness, candidate maturity, blocked reasons | Product sweep checkpoint. |
| Quarterly | Eval suite redesign, buyer hardware matrix, protocol adapter policy | Release planning. |
| Per incident | Supply-chain alerts, MCP/A2A/AG-UI security findings, model artifact warnings | Any critical/high advisory or local scanner finding. |
| Per major model/runtime release | Runtime capability, quantization, KV/cache, context, tool calling, multimodal behavior | New model/runtime enters candidate registry. |

## Final Bottom Line

NexusNet should treat this Forward Radar as the product's future-proofing layer. The quantization research makes model/runtime choices more truthful. This radar makes the entire system less likely to age badly.

The operating rule is simple: if a technology changes how agents communicate, observe, remember, evaluate, execute, deploy, or trust artifacts, it belongs in the radar before it belongs in the product.
