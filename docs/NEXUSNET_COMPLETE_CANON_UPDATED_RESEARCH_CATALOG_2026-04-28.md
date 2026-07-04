# NexusNet Complete Canon Updated Research Catalog - 2026-04-28

Purpose: use `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md` as the controlling NexusNet basis, then refresh every major canon lane against current public research, model, protocol, runtime, security, and tooling sources.

Research date: 2026-04-28

Primary local source:

- `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`

Related local research artifacts:

- `docs/NEXUSNET_COMPLETE_CANON_RESEARCH_REFRESH_DIFF_2026-04-28.md`
- `docs/NEXUSNET_RESEARCH_CANDIDATE_DOSSIER_2026-04-28.md`
- `docs/NEXUSNET_OPEN_FIRST_RESEARCH_EXPANSION_2026-04-28.md`
- `docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md`
- `docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md`
- `docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md`

Method:

- Treated the complete canon book as the primary source of NexusNet intent and architecture.
- Used current public sources for updates: official model docs, model cards, standards specs, vendor release notes, arXiv/OpenReview papers, and project docs.
- Did not install packages, register providers, enable tools, run external agents, train models, change default teachers, or alter NexusNet runtime behavior.
- Kept the core rule intact: new research candidates can improve NexusNet only through registry, license, eval, security, local-first, privacy, audit, and promotion gates.

## Executive Update

The older chat canon correctly aimed at a brain-first NexusNet with expert teachers, MoE inspiration, long context, memory graphs, recursive dreaming, eval routing, VisualOps, protocol bridges, and local-first operation. The main 2026 update is that the ecosystem has moved enough that NexusNet should stop treating old candidate names as the actual roster.

The most important upgrade is the teacher ensemble:

- Replace the old implicit "Mixtral + Devstral + whatever was current" thinking with a governed model roster that separates frontier API teachers, open-weight local teachers, specialist teachers, verifier teachers, and safety teachers.
- Keep Mixtral/Devstral as historical canon and assimilation scaffolding, but do not treat them as the best current choices without benchmark evidence.
- Add 2026 candidates such as GPT-5.5, Claude Opus 4.7, Gemini 3 Pro, DeepSeek V4-Pro/V4-Flash, Qwen3.6, Qwen3-VL, Mistral Small 4, Devstral 2, gpt-oss, and current verifier/security models.
- Keep every candidate gated. No model becomes a NexusNet default until its license, cost, runtime fit, safety profile, and NexusNet harness benchmarks are recorded.

The strongest product direction is still unchanged:

- NexusNet is the brain and governance layer.
- Models are teachers, experts, runtimes, evaluators, and tools.
- External protocols are mediated surfaces, not authority.
- Memory must become a typed temporal graph with evidence and decay.
- Long context should be sold as effective context, not prompt stuffing.
- Recursive dreaming and training remain shadow-only until eval gates exist.

## Updated Teacher Ensemble Catalog

### Recommended Roster Shape

| Layer | Purpose | Updated 2026 candidates | Status |
|---|---|---|---|
| Frontier reasoning teachers | Hard planning, architecture, code review, complex judgment | GPT-5.5, Claude Opus 4.7, Gemini 3 Pro | API-only, eval-gated |
| Balanced production teachers | Lower cost daily critique, route validation, synthesis | GPT-5.4, Claude Sonnet 4.6, Gemini 3 Flash, Mistral Small 4 | eval-gated |
| Open-weight reasoning teachers | Local/private reasoning, distillation candidates, reproducible evals | DeepSeek V4-Pro, DeepSeek V4-Flash, gpt-oss-120b, Qwen3.6-35B-A3B, Mistral Small 4 | license/runtime-gated |
| Coding and agentic SWE teachers | Repo navigation, patch generation, SWE task critique | GPT-5.5, Claude Opus 4.7, Devstral 2, Qwen3.6, DeepSeek V4-Pro, Mistral Small 4 | benchmark-gated |
| Multimodal/vision teachers | UI screenshots, diagrams, visual grounding, document vision | Gemini 3 Pro, Qwen3-VL, Mistral Small 4, Llama 4 Scout/Maverick, FARA/Universal Verifier | consent and provenance gated |
| Safety and policy teachers | Classifiers, tool-risk checks, policy review | gpt-oss-safeguard, Mistral Moderation 2, Llama Guard 4, ClawGuard-style rule gates | security-gated |
| Small local fallback teachers | Low-latency local tasks and canaries | gpt-oss-20b, Qwen3.6 FP8/quantized variants, Mistral Small 4 quantized, LFM2.5-VL, Llama Scout quantizations | hardware-gated |

### Frontier API Teachers

| Candidate | Current update | NexusNet use | Caveat |
|---|---|---|---|
| GPT-5.5 | OpenAI docs list `gpt-5.5` as the flagship for complex reasoning and coding, with 1M context, tools, configurable reasoning, and a Dec 1, 2025 knowledge cutoff. Source: https://developers.openai.com/api/docs/models | Primary frontier teacher for complex code, planning, agent orchestration, and regression review. | API-only; cost and privacy gates required. |
| Claude Opus 4.7 | Anthropic docs describe Opus 4.7 as the most capable generally available Claude model for complex reasoning and agentic coding, with 1M context. Source: https://platform.claude.com/docs/en/about-claude/models/overview | High-quality critique teacher for long-horizon planning, repo review, and adversarial review. | API-only; data routing and provider policy gates required. |
| Claude Sonnet 4.6 | Anthropic positions Sonnet 4.6 as the speed/intelligence balance, 1M context, and extended thinking. Source: https://platform.claude.com/docs/en/about-claude/models/overview | Mid-cost teacher and evaluator for routine critique and synthesis. | API-only. |
| Gemini 3 Pro | Google docs list `gemini-3-pro-preview` with text, image, audio, video, PDF input, 1,048,576 input tokens, 65,536 output tokens, thinking, function calling, code execution, file search, search grounding, and structured output. Source: https://ai.google.dev/gemini-api/docs/models/gemini | Strong multimodal and long-context teacher for canon book review, document analysis, visual evidence, and codebase-scale context. | Preview status and Google Cloud terms must be tracked. |
| Grok 4.1 | xAI announced Grok 4.1 for consumer surfaces; official API/model status should be confirmed before relying on it. Source: https://x.ai/news/grok-4-1/ | Optional external comparison teacher for conversational and creative judgment. | Treat as watchlist unless exact API model, privacy terms, and safety profile are pinned. |

### Open-Weight And Local-Control Teachers

| Candidate | Current update | NexusNet use | Caveat |
|---|---|---|---|
| DeepSeek V4-Pro | DeepSeek V4 Preview is live/open-sourced; V4-Pro is 1.6T total / 49B active, 1M context, open weights, and agentic/coding/reasoning positioning. Source: https://api-docs.deepseek.com/news/news260424 and https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro | Top open-weight reasoning and coding teacher candidate; benchmark against frontier API teachers. | Very large runtime footprint; geopolitical/privacy/security review required. |
| DeepSeek V4-Flash | V4-Flash is the efficient 284B / 13B active member of the V4 preview family with 1M context. Source: https://api-docs.deepseek.com/news/news260424 | Efficient open-weight daily teacher candidate and fallback for long-context work. | Same review as V4-Pro; still large. |
| DeepSeek V3.2 | V3.2 was the prior reasoning-agent release with thinking in tool-use. Source: https://api-docs.deepseek.com/news/news251201 | Demote to fallback/benchmark baseline now that V4 Preview exists. | Superseded by V4 candidates. |
| Qwen3.6-35B-A3B | Hugging Face model card lists Apache 2.0, 35B total / 3B active, agentic coding improvements, 262,144 native context, extensible to about 1,010,000 tokens, and vLLM/SGLang deployment guidance. Source: https://huggingface.co/Qwen/Qwen3.6-35B-A3B | Strong local/open coding and reasoning teacher; good fit for NexusNet scorecards. | Needs local hardware validation and evals. |
| Qwen3-VL-235B-A22B-Instruct | Hugging Face model card says Qwen3-VL improves text, visual perception, long context, video, spatial reasoning, and visual agent interaction; Apache 2.0. Source: https://huggingface.co/Qwen/Qwen3-VL-235B-A22B-Instruct | Primary open multimodal teacher candidate for screenshots, UI, vision, visual coding, and CUA critique. | Heavy runtime; screenshot privacy and action-proposal gates required. |
| Mistral Small 4 | Mistral docs list March 2026 open model, 119B total / 6.5B active, 256k context, hybrid instruct/reasoning/coding capabilities. Source: https://docs.mistral.ai/models/model-cards/mistral-small-4-0-26-03 | Strong efficient open teacher candidate, especially for local-ish routing and multi-role tasks. | Needs Apache/license confirmation in registry and local eval. |
| Devstral 2 | Mistral model overview lists Devstral 2 as an open frontier code-agent model for SWE tasks. Source: https://docs.mistral.ai/models/overview | Replace Devstral Small 1.1/Small 2 as the current Devstral candidate for coding-agent lanes. | Exact model card, license, runtime footprint, and deprecation dates must be pinned. |
| gpt-oss-120b | OpenAI docs describe `gpt-oss-120b` as open-weight, 117B / 5.1B active, Apache 2.0, and fitting a single H100. Source: https://developers.openai.com/api/docs/models/gpt-oss-120b | Strong local/open reasoning teacher and policy/safety experiment base. | Not served by OpenAI API; local hosting required. |
| gpt-oss-20b | OpenAI gpt-oss release describes the smaller model as suitable for edge/local use with 16 GB memory. Source: https://openai.com/index/introducing-gpt-oss/ | Local fallback, canary, and low-cost teacher for simple tasks. | Lower capability; must be benchmarked against NexusNet tasks. |
| Llama 4 Scout/Maverick | Meta Llama 4 model card on Hugging Face shows custom Llama 4 Community License, multimodal training, and Scout/Maverick data disclosures. Source: https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E | Keep as multimodal/open-weight comparison candidates. | License and data provenance require explicit commercial review. |
| Nemotron-Elastic-12B | Still useful as elastic-size architecture/runtime reference. Source: https://huggingface.co/nvidia/Nemotron-Elastic-12B | Keep as elastic-runtime reference, not primary teacher. | Confirm current successor models before implementation. |
| LFM2.5-VL | Small Liquid AI multimodal lane remains relevant for edge vision. Source: https://huggingface.co/LiquidAI/LFM2.5-VL-1.6B | Edge/local vision candidate. | Verify license and real device performance. |

### Specialist Teacher Updates

| Canon item | Updated recommendation |
|---|---|
| Mixtral + Devstral fusion | Treat as historical scaffold and design influence only. Current open MoE candidates such as DeepSeek V4, Qwen3.6, Mistral Small 4, and Llama 4 are better research targets than raw Mixtral/Devstral weight surgery. |
| Codestral | Keep as code-completion candidate only after current Mistral license review. Do not use commercially by assumption. |
| DeepEyesV2 | Keep as multimodal architecture influence; Qwen3-VL and FARA/Universal Verifier are now more directly actionable for screenshot and computer-use lanes. |
| FARA-7B | Use as a guarded computer-use candidate. Microsoft verifier work matters more than direct action execution. |
| Bloom | Still source-ambiguous. The current public Bloom source found previously is an agent registry, not enough to confirm the canon's intended behavioral-eval source. |
| Flash-DMD | Keep as visual generation/distillation watchlist only; it is not a core brain-path replacement. |
| LLM-Council | Adopt disagreement capture and peer-review trace pattern, not the external app. |
| Agent0 / space-agent | Pattern-only review for UI and agent-space concepts. |

## Aspect-by-Aspect Update Catalog

### 1. Brain-First Identity And Neural-Core Boundary

Canon basis:

- NexusNet is the brain/harness/memory/eval/control layer, not a wrapper around a single model.

2026 update:

- Frontier models are now strong enough to act as teachers and advisors, but they also make the boundary more important. GPT-5.5, Claude Opus 4.7, Gemini 3 Pro, and DeepSeek V4 should feed NexusNet evidence, critiques, traces, and candidates. None should become the NexusNet brain.
- Anthropic's public beta Managed Agents and advisor tool show that agent harnesses are becoming productized, which validates NexusNet's harness-first direction without requiring NexusNet to outsource authority. Source: https://platform.claude.com/docs/en/release-notes/overview

Catalog action:

- Add `BrainAuthorityBoundary` to the candidate registry.
- Every model or framework must have `authority_role = teacher | evaluator | runtime | tool | adapter | memory_backend | blocked`.
- Default all external systems to `blocked_authority = true`.

### 2. MoE, Experts, Router, Mini-NexusNets, And Expert Assimilation

Canon basis:

- Mixtral, Devstral, routers, mini-NexusNets, expert capsules, and neural-bus coordination are central influences.

2026 update:

- The field has moved toward practical MoE and sparse-active designs: DeepSeek V4-Pro/V4-Flash, Qwen3.6, Mistral Small 4, and Llama 4 Scout/Maverick all provide current MoE/sparse-active evidence.
- Direct weight fusion remains risky. Router-level, harness-level, and teacher-ensemble assimilation are safer than unsupervised parameter surgery.

Catalog action:

- Replace "try Mixtral/Devstral fusion" with `ExpertAssimilationScorecard`.
- Score candidates by task role, active parameters, total parameters, context, multimodality, license, runtime, eval history, teacher value, and replacement risk.

### 3. Cortex, Neural Bus, Shared HiveMind, And Non-Linear Scaling

Canon basis:

- Cortex and Neural Bus coordinate experts, dreams, AOs, and shared memory.

2026 update:

- A2A reached a 1.0 spec for external agent communication; it is useful as an envelope for external agent handoffs, not as the internal bus. Source: https://a2a-protocol.org/dev/specification/
- SGLang Model Gateway shows router/gateway patterns for heterogeneous model backends, privacy-sensitive history storage, MCP tooling, and OpenAI-compatible backends. Source: https://docs.sglang.io/advanced_features/sgl_model_gateway.html

Catalog action:

- Keep Neural Bus internal, typed, and auditable.
- Add external bus adapters only through `ProtocolAdapterRegistry`.
- Do not let A2A or SGLang Gateway replace NexusNet's internal authority graph.

### 4. Long Context, Effective Context, RoPE, YaRN, And Consolidation

Canon basis:

- Older chats pursued 1M+ context through RoPE/YaRN, long-context training, and context consolidation.

2026 update:

- 1M context is now available or emerging in several hosted/open systems: GPT-5.5, Claude Opus 4.7/Sonnet 4.6, Gemini 3 Pro, and DeepSeek V4.
- The product claim should still be "effective context" because raw context is not enough. Current systems also rely on caching, compaction, retrieval, graph memory, file search, and tool grounding.
- vLLM V1, SGLang, LMCache, and TensorRT-LLM show that runtime-level context/cache engineering is now a first-class optimization surface. Sources: https://docs.vllm.ai/en/latest/usage/v1_guide.html, https://docs.sglang.io/, https://docs.lmcache.ai/developer_guide/architecture.html, https://developer.nvidia.com/tensorrt-llm

Catalog action:

- Add `EffectiveContextReport` to every long-context answer.
- Track raw tokens, cached tokens, graph nodes, dereferenced evidence, summaries, tool results, retrieval misses, and recall checks.
- Treat raw 1M context claims as untrusted until NexusNet evals prove useful recall.

### 5. Multi-Plane Mind Map, MemoryNode, Hypergraph, And Cross-Plane Cognition

Canon basis:

- NexusNet wants MemoryNode, multi-plane cognition, hypergraph memory, and cross-plane links.

2026 update:

- Graphiti/Zep and Mem0 make graph and memory-lifecycle patterns more concrete. Zep's graph is built on Graphiti and automatically constructs temporal knowledge graphs; Mem0 reports an April 2026 memory algorithm with user/session/agent memory, entity linking, and hybrid retrieval. Sources: https://help.getzep.com/groups and https://github.com/mem0ai/mem0
- Letta's context repositories show a useful git-backed memory pattern for coding agents. Source: https://www.letta.com/blog/context-repositories
- MemX adds a local-first memory baseline useful for privacy-focused NexusNet deployments. Source: https://arxiv.org/abs/2603.16171

Catalog action:

- Build NexusNet's own HiveMind schema first.
- External memory tools are candidates, not canonical authority.
- Required fields: temporal validity, source provenance, confidence, decay, conflict, owner graph, and exact evidence handle.

### 6. Recursive Neural Dreaming, Replay, And Self-Improvement

Canon basis:

- Recursive dreaming, replay buffers, self-training, consequence loops, DreamAO, SelfTrainingAO, and recursive learning are core ambitions.

2026 update:

- The safe path is not free-running autonomous self-improvement. Use R-Zero/RAGEN-style task generation and RL diagnostics only as shadow proposals.
- TRL v1.0 now positions itself as a post-training library that should emit structured warnings parseable by agents. Source: https://huggingface.co/blog/trl-v1
- Current RL backends such as TRL, verl, NeMo-RL, RAGEN, AReaL, ROLL, OpenRLHF, LLaMA-Factory, and torchtune should be backend manifests, not active training defaults.

Catalog action:

- Add `DreamRunManifest`.
- Dreaming output must be a candidate task, trace, reward spec, eval delta, failure taxonomy, and rollback plan.
- Promotion remains disabled until held-out evals and provenance gates exist.

### 7. Expert Capsules, AOs, Council, Critique, And Consequence

Canon basis:

- AOs, expert capsules, council review, CritiqueAO, consequence scoring, and assistant orchestrators are repeatedly established.

2026 update:

- LLM-Council remains useful as a disagreement-capture pattern.
- Claude advisor tool and frontier teacher ensembles show that "fast executor + stronger advisor" is now a practical architecture. Source: https://platform.claude.com/docs/en/release-notes/overview

Catalog action:

- Add `AdvisorTeacherTrace`.
- Every AO/expert run should record primary model, advisor model, disagreement summary, consequence score, resolution decision, and final authority source.

### 8. EBT Routing, Decision Traces, Evals, Benchmarks, And Provenance

Canon basis:

- EBT routing and decision traces should make choices explainable and benchmark-driven.

2026 update:

- Universal Verifier work shows verifier design matters as much as model selection for computer-use agents, and separates process quality from outcome. Source: https://www.microsoft.com/en-us/research/articles/the-art-of-building-verifiers-for-computer-use-agents/
- OpenTelemetry GenAI conventions cover model spans, agent spans, events, and metrics. Source: https://opentelemetry.io/docs/specs/semconv/gen-ai/

Catalog action:

- Add EBT dimensions for task fit, evidence freshness, verifier confidence, memory confidence, route risk, tool risk, cost, latency, privacy, eval history, disagreement, fallback availability, and consent state.
- Every route decision must produce a portable decision record.

### 9. Teachers, Distillation, RL, Training, And Native Growth

Canon basis:

- Teacher ensembles, distillation, RL, native growth, and training jobs are central but must be governed.

2026 update:

- The teacher roster should be refreshed as above.
- The strongest teacher ensemble is heterogeneous: frontier API models for hard judgment, open-weight models for reproducible local evaluation, specialist models for vision/code/security, and safety classifiers for guardrails.
- gpt-oss, DeepSeek V4, Qwen3.6, Qwen3-VL, and Mistral Small 4 materially improve the open/local side compared with the old Mixtral/Devstral-centered plan.

Catalog action:

- Add `TeacherRegistryV2`.
- Required fields: provider, model_id, snapshot, license, modality, context, runtime, teacher_role, eval_family, prompt contract, cost, privacy posture, failure modes, last_verified_on, and promotion status.

### 10. Tools, MCP, A2A, AG-UI, Security, Identity, Consent, And Audit

Canon basis:

- Tools and protocols are valuable only with identity, consent, sandboxing, and audit.

2026 update:

- A2A 1.0 is a stable external-agent interoperability spec.
- MCP remains useful but high-risk. OpenTelemetry now has MCP-related semantic conventions, and security research around MCP tool poisoning has grown quickly. Sources: https://modelcontextprotocol.io/specification/2025-11-25/basic, https://opentelemetry.io/docs/specs/semconv/gen-ai/, https://arxiv.org/abs/2604.05969
- AG-UI remains a good VisualOps event-stream candidate.

Catalog action:

- Add `ProtocolAdapterRegistryV2`.
- Required fields: protocol, transport, auth, identity, source trust, allowed verbs, schema validation, signed descriptor, sandbox class, consent mode, audit sink, kill switch, and last security review.

### 11. VisualOps, Operator UI Panels, Visualizer, Diagrams, And Explainability

Canon basis:

- VisualOps should show the brain, hives, experts, routes, tools, runtime, memory, training, and governance.

2026 update:

- VisualOps should be observability-first, not decorative.
- Use OpenTelemetry GenAI/OpenInference-compatible exports where practical, but keep NexusNet-specific brain-path fields.
- SGLang/vLLM/LMCache/TensorRT runtime metrics should be shown beside NexusNet traces.

Catalog action:

- Build read-only VisualOps first.
- Required panels: teacher roster, candidate registry, memory graph health, EBT trace, protocol posture, runtime/cache posture, security posture, eval outcomes, dreaming queue, training gates, and release/privacy posture.

### 12. Runtime, Hardware, Local-First Operation, Safe Mode, And Packaging

Canon basis:

- NexusNet should be local-first, hardware-aware, safe-mode capable, and packageable.

2026 update:

- Runtime candidates should be scored by real throughput, latency, cache hit rate, memory, quantization, fallback behavior, and local privacy.
- vLLM V1, SGLang, LMCache, TensorRT-LLM, llama.cpp, Ollama, LM Studio, MLC/ExecuTorch, OpenVINO, and ONNX Runtime GenAI are all scorecard candidates.
- The best runtime depends on model, device, and risk. No single runtime should be hard-coded as winner.

Catalog action:

- Add `RuntimeScorecardV2`.
- Required fields: model support, context support, quantization, KV cache, tool/function calling compatibility, metrics, hardware target, privacy, install burden, crash replay, and safe-mode reason.

### 13. Multimodal, GUI/Computer Use, FARA, DeepEyes, LFM2, Qwen, And Vision

Canon basis:

- NexusNet should handle vision, GUI/computer use, multimodal evidence, and visual reasoning without unsafe autonomy.

2026 update:

- Qwen3-VL and Gemini 3 Pro are stronger multimodal teacher candidates than older references.
- FARA/Universal Verifier points to the right architecture: screenshot evidence, process verifier, outcome verifier, and action guardrails.
- FARA itself should be a candidate lane, not silent desktop control.

Catalog action:

- Add `ComputerUseLaneV1`.
- Required fields: screenshot hash, UI state source, proposed action, allowed action class, verifier rubric, process score, outcome score, environment blocker, rollback availability, and human approval requirement.

### 14. Federation, Privacy, Meta-Evolution, Governance, And Compliance

Canon basis:

- Federation and privacy are part of NexusNet scale, but governance is required before distributed autonomy.

2026 update:

- Model/provider options now increase privacy choices, but also increase data-routing risk.
- Claude, Gemini, OpenAI, DeepSeek, xAI, and local open-weight models each imply different data handling, residency, licensing, and audit surfaces.
- Federation should start as manifest and audit export work, not cross-node autonomous learning.

Catalog action:

- Add `FederationManifest`.
- Required fields: node identity, allowed data classes, teacher access, memory export scope, eval artifacts, privacy budget candidate, audit sink, operator approvals, and revocation path.

### 15. Research Assimilation And Candidate Registry

Canon basis:

- NexusNet needs a candidate registry, source ledger, license review, and explicit assimilation gates.

2026 update:

- The ecosystem changes too quickly for static chat-derived candidate names.
- The new registry must be the main place where "current best" is tracked. The canon book remains the source of intent; registry entries track current implementation candidates.

Catalog action:

- Add `CandidateRegistryV2` and seed it with the catalog below.
- Do not convert catalog entries into behavior until each has an evidence record and gate status.

## Candidate Registry Seed List

### Immediate High-Value Adds

| Candidate | Assimilation mode | Gate |
|---|---|---|
| GPT-5.5 | frontier teacher, coding teacher, planner, eval critic | provider/privacy/cost/eval |
| Claude Opus 4.7 | frontier teacher, critique teacher, agentic code reviewer | provider/privacy/cost/eval |
| Claude Sonnet 4.6 | balanced teacher and advisor | provider/privacy/cost/eval |
| Gemini 3 Pro | multimodal and long-context teacher | provider/privacy/preview/eval |
| DeepSeek V4-Pro | open-weight reasoning/coding teacher | license/security/runtime/eval |
| DeepSeek V4-Flash | efficient open-weight teacher | license/security/runtime/eval |
| Qwen3.6-35B-A3B | open coding/reasoning teacher | Apache/runtime/eval |
| Qwen3-VL-235B-A22B | multimodal/vision teacher | Apache/runtime/privacy/eval |
| Mistral Small 4 | efficient hybrid teacher | license/runtime/eval |
| Devstral 2 | SWE/code-agent teacher | license/runtime/eval |
| gpt-oss-120b | local reasoning teacher | Apache/runtime/eval |
| gpt-oss-20b | local fallback teacher | Apache/runtime/eval |
| Graphiti/Zep | temporal graph memory candidate | data/privacy/license/eval |
| Mem0 | memory-layer candidate | data/privacy/security/eval |
| vLLM V1 | runtime candidate | runtime/eval |
| SGLang | runtime/gateway candidate | runtime/privacy/eval |
| LMCache | effective-context cache candidate | runtime/eval |
| A2A 1.0 | external agent envelope | protocol/security/consent |
| MCP latest spec | tool/resource protocol | protocol/security/consent |
| AG-UI | VisualOps event stream | protocol/UI/security |
| OTel GenAI | trace export vocabulary | observability/eval |
| Universal Verifier | CUA verifier pattern | eval/security |
| ClawGuard-style rule gate | deterministic tool-call guard | security/eval |

### Demote Or Keep As Watchlist

| Candidate | Updated status | Reason |
|---|---|---|
| Raw Mixtral + Devstral weight surgery | demote | newer MoE/open-weight teachers exist; direct fusion still high-risk. |
| Mixtral 8x22B | historical scaffold | useful benchmark, not current center. |
| Devstral Small 1.1 / Small 2 | superseded | Mistral docs point toward Devstral 2 and Mistral Small 4. |
| Codestral | license-gated | useful coding candidate but commercial terms must be pinned. |
| Bloom | source-ambiguous | exact intended source still not pinned. |
| Flash-DMD | watchlist | relevant to image generation distillation, not core brain growth. |
| OpenClaw | blocked-authority | security risk; pattern mining only. |
| External agent frameworks | pattern-only | cannot replace NexusNet brain. |
| FARA direct control | shadow-only | useful CUA candidate, but no silent desktop action. |
| Autonomous training | shadow-only | no promotion without eval/provenance/reward gates. |

## Concrete Schema Updates

### `TeacherRegistryV2`

Required fields:

- `candidate_id`
- `provider`
- `model_id`
- `snapshot_or_version`
- `source_url`
- `last_verified_on`
- `license_status`
- `hosted_or_local`
- `modality`
- `context_window`
- `max_output`
- `tool_support`
- `runtime_targets`
- `teacher_role`
- `cost_profile`
- `privacy_profile`
- `eval_family`
- `benchmark_status`
- `promotion_status`
- `blocked_reason`

### `HarnessRegistryV1`

Required fields:

- `harness_id`
- `owner_layer`
- `execution_contract`
- `required_outputs`
- `allowed_tools`
- `budget`
- `permissions`
- `completion_conditions`
- `raw_trace_links`
- `held_out_eval_family`
- `shadow_status`
- `promotion_status`

### `EffectiveContextReport`

Required fields:

- `raw_context_tokens`
- `cached_tokens`
- `prefix_reuse`
- `kv_reuse`
- `graph_nodes_consulted`
- `evidence_records_dereferenced`
- `summaries_inserted`
- `raw_sources_avoided`
- `recall_checks`
- `context_assembly_reason`
- `runtime_cache_metrics`

### `ProtocolAdapterRegistryV2`

Required fields:

- `protocol`
- `version`
- `transport`
- `auth`
- `identity`
- `source_trust`
- `allowed_verbs`
- `schema_validation`
- `signed_descriptor`
- `sandbox_class`
- `consent_mode`
- `audit_sink`
- `kill_switch`
- `last_security_review`

## Recommended Next Product Step

Build the registry layer before building more behavior:

1. Add `TeacherRegistryV2` and seed it with the updated teacher ensemble.
2. Add `CandidateRegistryV2` for memory, runtime, protocol, security, and training candidates.
3. Add `EffectiveContextReport` and `RuntimeScorecardV2`.
4. Add read-only VisualOps panels backed by these registries.
5. Add local harness evals for the first model comparison:
   - codebase task,
   - long-context canon recall,
   - graph-memory retrieval,
   - CUA screenshot verification,
   - security/tool-poisoning refusal,
   - cost/latency/runtime report.

The next implementation should not be "swap in the newest model." It should be "make NexusNet able to know, compare, prove, and govern which teacher/model/runtime is best for each role."
