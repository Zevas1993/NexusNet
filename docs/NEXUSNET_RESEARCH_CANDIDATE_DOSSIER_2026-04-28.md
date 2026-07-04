# NexusNet Research Candidate Dossier - 2026-04-28

Purpose: research every candidate named in `docs/NEXUSNET_COMPLETE_CANON_RESEARCH_REFRESH_DIFF_2026-04-28.md` and convert the refresh summary into an auditable candidate disposition record.

Research date: 2026-04-28

Primary local input:

- `docs/NEXUSNET_COMPLETE_CANON_RESEARCH_REFRESH_DIFF_2026-04-28.md`
- `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`

Method:

- Reviewed the complete refresh diff and extracted the named research candidates, protocols, models, runtime systems, memory systems, training backends, security concerns, and ambiguous source identities.
- Checked current public sources where reachable, prioritizing official docs, official model cards, official repositories, standards specifications, arXiv/OpenReview pages, and vendor research posts.
- Treated third-party commentary as risk context only.
- Did not install packages, register providers, enable adapters, start training jobs, push code, open PRs, or replace locked NexusNet canon.

## Disposition Legend

| Disposition | Meaning for NexusNet |
|---|---|
| `promote-design` | Strong enough to become a NexusNet design requirement, with implementation still gated. |
| `candidate-registry` | Worth tracking in the candidate/source registry, but not active behavior. |
| `shadow-only` | May be prototyped or simulated only behind eval, security, and operator gates. |
| `watchlist` | Interesting, but not central enough for implementation work now. |
| `license-gated` | Do not use commercially or redistribute until the license review is explicit. |
| `source-ambiguous` | Name or intended source is not pinned well enough to implement. |
| `blocked-authority` | Cannot become brain authority or silently replace NexusNet governance. |

## Executive Disposition

The researched candidates support the same product direction: NexusNet should become a stronger governed brain, not a wrapper around any one new repo, model, paper, or protocol.

Priority promotions:

1. Harness engineering as a first-class NexusNet artifact.
2. Temporal graph HiveMind and mini AO/expert graphs.
3. Effective-context reporting instead of raw long-context claims.
4. Trace-backed EBT routing, verifier signals, and disagreement capture.
5. Read-only VisualOps backed by registry, trace, memory, runtime, protocol, and security state.
6. Zero-trust protocol/tool posture for MCP, A2A, AG-UI, skills, hooks, schedules, training jobs, deployments, and PR actions.

Priority blocks:

1. No external framework gets brain authority.
2. No model becomes "better" inside NexusNet without local harness benchmarks.
3. No protocol adapter gets write or execution authority without identity, schema, sandbox, consent, and audit gates.
4. No self-improvement loop promotes without reward specs, held-out evals, provenance, and rollback.
5. No ambiguous source identity moves past registry intake.

## Complete Candidate Inventory

### Harness And Orchestration

| Candidate | Source | Finding | NexusNet disposition |
|---|---|---|---|
| Meta-Harness | [arXiv](https://arxiv.org/abs/2603.28052) | Treats harness code and raw traces as optimization material, which maps directly to AO/expert execution improvement. | `promote-design`: add `HarnessRegistry`, raw trace retention, shadow evals, and promotion gates. |
| Natural-Language Agent Harnesses | [arXiv](https://arxiv.org/abs/2603.25723) | Reinforces portable execution contracts, adapters, durable artifacts, and task-specific harness logic. | `candidate-registry`: use as design influence for AO/expert contracts. |
| AutoHarness | [arXiv](https://arxiv.org/abs/2603.03329) | Supports compiling task rules, constraints, and guardrails into harness artifacts instead of hiding them in prompts. | `candidate-registry`: pattern-only until eval harness exists. |

Required NexusNet artifact:

- `HarnessRegistry` with `harness_id`, `owner_layer`, `required_outputs`, `allowed_tools`, `budgets`, `permissions`, `completion_conditions`, `artifact_paths`, `raw_trace_links`, `eval_family`, `shadow_status`, `promotion_status`, and `rollback_plan`.

### HiveMind, Memory OS, And Canon Compilation

| Candidate | Source | Finding | NexusNet disposition |
|---|---|---|---|
| Graphiti | [docs](https://help.getzep.com/graphiti/getting-started/welcome), [GitHub](https://github.com/getzep/graphiti) | Strong match for temporal knowledge graph operations, incremental updates, and hybrid retrieval. | `promote-design`: adopt temporal graph principles; keep external dependency optional. |
| Zep temporal knowledge graph paper | [arXiv](https://arxiv.org/abs/2501.13956) | Provides research basis for continuously updated agent memory graphs. | `candidate-registry`: evidence source for graph memory design. |
| MemOS | [arXiv](https://arxiv.org/abs/2507.03724) | Frames memory as a managed resource with scheduling, migration, fusion, provenance, and versioning. | `promote-design`: use as memory lifecycle schema influence. |
| A-MEM | [OpenReview](https://openreview.net/pdf?id=LB0nTqxAKd) | Pushes memory toward agentic operations and evolving links instead of static recall. | `candidate-registry`: pattern for link and conflict operations. |
| AgeMem | [arXiv](https://arxiv.org/abs/2601.01885) | Useful signal for age/decay handling and memory lifecycle rather than infinite accumulation. | `candidate-registry`: use for decay and retention policy. |
| MemexRL | [arXiv](https://arxiv.org/abs/2603.04257) | Supports indexed experience memory and dereferenceable evidence outside the prompt. | `promote-design`: tie exact evidence handles to effective-context reporting. |
| Karpathy LLM Wiki | [gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | Practical durable pattern: raw immutable sources, generated wiki pages, schema, logs, and maintenance loops. | `promote-design`: compile into HiveMind, do not copy as authority. |
| Graphify | [GitHub](https://github.com/safishamsi/graphify), [PyPI](https://pypi.org/project/graphifyy/) | Useful as a source-to-graph inspiration for project code/docs/media. | `candidate-registry`: pattern-only; verify license and output quality before use. |

Required NexusNet artifact:

- `HiveMindGraphSchema` with main graph, AO subgraphs, expert subgraphs, provenance, conflict records, decay fields, exact evidence links, and cross-graph edges.
- `HiveMindCompiler` with immutable raw sources, generated canon pages, graph node/edge generation, update logs, stale-claim linting, orphan-node checks, contradiction checks, and source-gap reports.

### Effective Context, Runtime, Cache, And Quantization

| Candidate | Source | Finding | NexusNet disposition |
|---|---|---|---|
| vLLM V1 | [docs](https://docs.vllm.ai/en/latest/usage/v1_guide/) | Relevant for prefix caching, context extension, KV events, disaggregated prefill, metrics, and OTel direction. | `candidate-registry`: runtime scorecard target, not default runtime. |
| SGLang | [docs](https://docs.sglang.io/), [observability](https://docs.sglang.io/advanced_features/observability.html), [gateway](https://docs.sglang.io/advanced_features/sgl_model_gateway.html), [metrics](https://docs.sglang.io/references/production_metrics.html) | Strong runtime pattern for RadixAttention, structured outputs, metrics, request replay, and gateway posture. | `candidate-registry`: runtime scorecard target and telemetry influence. |
| LMCache | [docs](https://docs.lmcache.ai/) | Useful for cross-request KV reuse and cache-aware effective context. | `candidate-registry`: cache scorecard target. |
| Transformers torchao | [docs](https://huggingface.co/docs/transformers/en/quantization/torchao) | Relevant to quantization and local runtime fit, especially when scoring hardware constraints. | `candidate-registry`: runtime capability, not a governance layer. |
| llama.cpp | [GitHub](https://github.com/ggml-org/llama.cpp) | Existing local-first runtime class; useful for CPU/GPU fallback and GGUF lanes. | `candidate-registry`: scorecard target. |
| LM Studio | [docs](https://lmstudio.ai/docs) | Useful local model serving target for operator-friendly desktop flows. | `candidate-registry`: scorecard target only. |
| Ollama | [docs](https://docs.ollama.com/) | Useful local runtime/provider target; must stay adapter-mediated. | `candidate-registry`: scorecard target only. |
| Local/mobile runtimes | Internal canon plus Android runtime history | Important for local-first product claims and safe-mode fallback. | `candidate-registry`: runtime scorecards must include device class and fallback reason. |

Required NexusNet artifact:

- `EffectiveContextReport` with prompt tokens, cached tokens, prefix reuse, graph nodes consulted, evidence records dereferenced, summaries inserted, raw sources avoided, recall checks, context assembly reason, and runtime cache metrics.
- Runtime scorecards for latency, throughput, cache hit rate, VRAM/RAM, quantization, model fit, fallback, safe-mode reason, and supported trace export.

### Model And Teacher Candidates

| Candidate | Source | Finding | NexusNet disposition |
|---|---|---|---|
| Devstral Small 1.1 | [Hugging Face](https://huggingface.co/mistralai/Devstral-Small-2507) | Strong current coding-agent candidate; model card states Apache 2.0 and agentic coding positioning. | `candidate-registry`: upgrade as coding teacher/specialist candidate; benchmark before promotion. |
| Devstral Medium | [Mistral docs](https://docs.mistral.ai/models/devstral-medium-1-0-25-07) | Larger Devstral lane for stronger coding tasks, likely less local-friendly. | `candidate-registry`: teacher/evaluator candidate, not local default. |
| Mixtral 8x22B Instruct | [Hugging Face](https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1) | Still a historical MoE scaffold, but heavy and not a reason to freeze model choices. | `candidate-registry`: keep canon scaffold; require runtime and license review. |
| Nemotron-Elastic-12B | [Hugging Face](https://huggingface.co/nvidia/Nemotron-Elastic-12B) | Relevant for elastic-capacity thinking and runtime-scaled model operation. | `candidate-registry`: evaluate as elastic-runtime reference. |
| Qwen3-VL | [Transformers docs](https://huggingface.co/docs/transformers/main/en/model_doc/qwen3_vl) | Strong multimodal lane with visual understanding and long-context configuration details. | `candidate-registry`: multimodal/vision teacher candidate; benchmark with screenshot provenance. |
| LFM2.5-VL-1.6B | [Hugging Face](https://huggingface.co/LiquidAI/LFM2.5-VL-1.6B) | Small multimodal lane relevant to edge/local vision exploration. | `candidate-registry`: edge-vision candidate; verify license/runtime. |
| DeepEyesV2 | [arXiv](https://arxiv.org/abs/2511.05271) | Relevant as agentic multimodal architecture influence, not a drop-in replacement. | `watchlist`: CUA/vision influence only. |
| Codestral | [Mistral docs](https://docs.mistral.ai/capabilities/code_generation/) | Coding model family is relevant but commercial use and redistribution need explicit current license review. | `license-gated`: do not adopt until license review is captured. |

Required NexusNet artifact:

- Model/teacher scorecard fields: `role`, `license_status`, `runtime_fit`, `context_claim`, `measured_effective_context`, `teacher_value`, `eval_family`, `promotion_status`, `blocked_reason`, and `last_verified_on`.

### Recursive Dreaming, RL, And Training Backends

| Candidate | Source | Finding | NexusNet disposition |
|---|---|---|---|
| R-Zero | [arXiv](https://arxiv.org/abs/2508.05004) | Useful challenger/solver inspiration for self-generated curricula. | `shadow-only`: idea/task generation only until eval gates exist. |
| RAGEN | [GitHub](https://github.com/mll-lab-nu/RAGEN) | Relevant for reasoning-agent RL diagnostics and collapse prevention. | `candidate-registry`: diagnostics influence. |
| TRL v1.0 | [Hugging Face blog](https://huggingface.co/blog/trl-v1) | Mature post-training toolkit candidate, but methods are shifting quickly. | `candidate-registry`: backend manifest, disabled by default. |
| verl | [GitHub](https://github.com/verl-project/verl) | Scalable RL/post-training backend candidate. | `candidate-registry`: backend manifest only. |
| NeMo-RL | [docs](https://docs.nvidia.com/nemo/rl/latest/index.html) | Enterprise-scale RL backend candidate with NVIDIA stack assumptions. | `candidate-registry`: backend manifest; hardware/cloud gates required. |
| AReaL | [GitHub](https://github.com/inclusionAI/AReaL) | Agent/RL backend candidate from InclusionAI. | `candidate-registry`: backend manifest; evaluate maturity and license. |
| ROLL | [GitHub](https://github.com/alibaba/ROLL) | Alibaba RL/post-training candidate. | `candidate-registry`: backend manifest; license/security review required. |
| Agent Lightning | [arXiv](https://arxiv.org/abs/2508.03680) | Useful framing for training agents through separated runtime/training signals. | `candidate-registry`: architecture influence; no training activation. |

Required NexusNet artifact:

- `DreamRunManifest` with task source, challenger, solver, verifier, reward spec, allowed tools, memory snapshot, generated artifacts, failure taxonomy, eval family, promotion gate, rollback path, and poisoning checks.
- Training backend manifests with backend version, license, runtime requirements, data contract, reward spec contract, eval contract, artifact outputs, cost/risk estimate, and disabled-by-default status.

### EBT, Verifiers, Graph Retrieval, And Computer Use

| Candidate | Source | Finding | NexusNet disposition |
|---|---|---|---|
| Universal Verifier | [Microsoft article](https://www.microsoft.com/en-us/research/articles/the-art-of-building-verifiers-for-computer-use-agents/), [arXiv](https://arxiv.org/abs/2604.06240) | Strong evidence that verifier rubric quality, process/outcome separation, and hallucinated completion detection matter. | `promote-design`: EBT and CUA traces must include verifier fields. |
| FARA-7B | [arXiv](https://arxiv.org/abs/2511.19663) | Relevant computer-use model lane for screenshot-to-action proposals. | `shadow-only`: guarded tool lane; no silent desktop control. |
| Graph-R1 | [arXiv](https://arxiv.org/abs/2507.21892), [GitHub](https://github.com/LHRLAB/Graph-R1) | Supports graph reasoning as multi-turn interaction, useful for EBT/retrieval research. | `candidate-registry`: retrieval/eval influence. |
| GraphRAG-R1 | [Hugging Face paper page](https://huggingface.co/papers/2507.23581) | Supports graph-RAG reasoning and route evaluation direction. | `candidate-registry`: retrieval/eval influence. |

Required NexusNet artifact:

- EBT route record fields: task fit, memory confidence, evidence freshness, route risk, tool risk, model/runtime budget, eval history, verifier confidence, disagreement spread, consent requirement, fallback availability, and trace artifact links.
- `ComputerUseLane` with screenshot evidence, proposed action, allowed action class, process score, outcome score, verifier rubric, environment blocker, undo availability, and human approval requirement.

### Protocols, Telemetry, And VisualOps

| Candidate | Source | Finding | NexusNet disposition |
|---|---|---|---|
| MCP | [spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic) | Useful tool/resource protocol, but high-risk if adapter trust is implicit. | `blocked-authority`: mediated adapter only; never brain authority. |
| A2A | [spec](https://a2a-protocol.org/dev/specification/) | Useful external-agent task and artifact envelope. | `candidate-registry`: handoff envelope only, signed and consent-gated. |
| AG-UI | [docs](https://docs.ag-ui.com/), [events](https://docs.ag-ui.com/concepts/events) | Strong match for VisualOps event streams between agents and frontend. | `promote-design`: read-only VisualOps event stream candidate. |
| OpenTelemetry GenAI | [semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | Useful common telemetry vocabulary for model/tool/retrieval traces. | `promote-design`: normalize outward traces while preserving NexusNet fields. |
| OpenInference | [spec](https://arize-ai.github.io/openinference/spec/) | Useful AI trace conventions for model/tool/retrieval systems. | `candidate-registry`: export compatibility target. |
| SGLang metrics | [docs](https://docs.sglang.io/references/production_metrics.html) | Runtime metrics should appear beside NexusNet brain-path traces. | `candidate-registry`: metric mapping source. |
| vLLM metrics/context docs | [docs](https://docs.vllm.ai/en/latest/usage/v1_guide/) | Runtime context/cache telemetry should feed effective-context reporting. | `candidate-registry`: metric mapping source. |

Required NexusNet artifact:

- `ProtocolAdapterRegistry` with protocol, transport, auth, identity, consent mode, allowed verbs, sandbox class, schema validation, audit sink, source trust, kill switch, trace fields, and last verification.
- Read-only VisualOps panels for brain status, ingestion queue, memory graph health, AO/expert hives, EBT route traces, build artifacts, dreaming/training gates, runtime posture, protocol posture, security posture, governance, federation/privacy, and research registry changes.

### Security And Zero-Trust Candidates

| Candidate | Source | Finding | NexusNet disposition |
|---|---|---|---|
| OWASP MCP Tool Poisoning | [OWASP](https://owasp.org/www-community/attacks/MCP_Tool_Poisoning) | Confirms indirect prompt injection through tool definitions is a first-class risk. | `promote-design`: security gate for protocol/tool descriptions. |
| OpenClaw variants security evaluation | [arXiv](https://arxiv.org/abs/2604.03131) | Reinforces that tool-augmented agents need systematic security evaluation. | `candidate-registry`: adversarial eval source. |
| OpenClaw PRISM | [arXiv](https://arxiv.org/abs/2603.11853) | Relevant to agent security threat modeling and adversarial posture. | `candidate-registry`: adversarial eval source. |
| ClawGuard | [arXiv](https://arxiv.org/abs/2604.11790) | Relevant defense candidate for tool/agent ecosystem risk. | `candidate-registry`: security candidate; evaluate claims before adoption. |
| OpenClaw security docs | [docs](https://docs.openclaw.ai/security) | Useful external security guidance, not a NexusNet control plane. | `candidate-registry`: reference only. |

Required NexusNet artifact:

- `SecurityPosturePanel` with unsigned tools, exposed local endpoints, broad filesystem access, untrusted descriptions, prompt-injection exposure, missing audit sinks, stale adapters, disabled sandbox, dangerous schedules, and pending approvals.
- Privilege separation for untrusted-content reader, planner, tool executor, memory writer, deployment actor, training actor, and release actor.

### Councils, External Agent Spaces, Source Identity, And Watchlist Items

| Candidate | Source | Finding | NexusNet disposition |
|---|---|---|---|
| LLM-Council | [GitHub](https://github.com/karpathy/llm-council) | Useful pattern for disagreement capture, peer review, ranking, and synthesis. | `candidate-registry`: adopt trace pattern only; no top-level replacement. |
| Agent0 space-agent | [GitHub](https://github.com/agent0ai/space-agent) | Useful to review for UI/agent-space patterns, not authority. | `candidate-registry`: pattern-only. |
| Bloom | [site](https://www.usebloom.org/) | Current public source found is an agent registry; that does not prove the intended canon source if the canon meant behavioral eval. | `source-ambiguous`: pin exact source before any implementation. |
| GitHub Annotation Toolkit / NNAT | Current source not pinned in the refresh diff | The concept is valuable, but the exact intended GitHub source is unresolved. Generic annotation-toolkit search results are not enough. | `source-ambiguous`: require exact URL, license, schema, and source-kind before work. |
| Flash-DMD | [arXiv](https://arxiv.org/abs/2511.20549), [OpenReview](https://openreview.net/forum?id=PwelCOoiiA) | Appears relevant to image-generation distillation/RL rather than core brain self-improvement. | `watchlist`: visual generation/distillation only. |

Required NexusNet artifact:

- `candidate_source_identity` fields: canonical name, exact URL, source type, license, last verified date, intended assimilation, replacement risk, implementation status, and unresolved ambiguity.

## Registry Field Additions

Every candidate should have:

| Field | Required use |
|---|---|
| `candidate_id` | Stable internal key, independent of display name. |
| `canonical_name` | Human name used in docs/UI. |
| `source_url` | Exact primary source URL. |
| `source_kind` | Paper, repo, docs, model card, standard, vendor post, internal canon, or ambiguous. |
| `source_owner` | Project, company, individual, standards group, or unknown. |
| `last_verified_on` | Date of most recent public-source check. |
| `license_status` | Allowed, restricted, unknown, noncommercial, requires review, or not applicable. |
| `replacement_risk` | None, low, medium, high, or blocked-authority. |
| `assimilation_mode` | Pattern, teacher, runtime, protocol, UI, eval, memory, training backend, security, or research-only. |
| `owner_layer` | Neural core, AO Hive, Expert Hive, HiveMind, VisualOps, Runtime, Training, Governance, Security, or Federation. |
| `gates_required` | License, eval, security, local-first, consent, audit, promotion, privacy, sandbox, or external-service. |
| `evidence_links` | Source links, source lines, local artifacts, benchmarks, traces, or review records. |
| `implementation_status` | Unreviewed, candidate, design, prototype, shadow, active, blocked, deprecated, or watchlist. |
| `blocked_reason` | Required when status is blocked, source-ambiguous, license-gated, or watchlist. |
| `next_review_on` | Refresh date for fast-moving candidates. |

## Candidate-Specific Next Actions

### Immediate Registry Intake

Create source records for:

- Meta-Harness
- Graphiti
- MemOS
- MemexRL
- Karpathy LLM Wiki
- vLLM
- SGLang
- LMCache
- Devstral Small 1.1
- Qwen3-VL
- Universal Verifier
- MCP
- A2A
- AG-UI
- OTel GenAI
- OpenInference
- OWASP MCP Tool Poisoning
- LLM-Council
- Flash-DMD

These should be registry entries first, not executable integrations.

### Requires License Review Before Commercial Lane

- Codestral
- Mixtral 8x22B Instruct
- Graphify
- Nemotron-Elastic-12B
- LFM2.5-VL-1.6B
- RAGEN
- verl
- NeMo-RL
- AReaL
- ROLL
- Agent Lightning
- space-agent
- Any model weight or training artifact not explicitly cleared.

### Requires Source Disambiguation

- Bloom
- GitHub Annotation Toolkit / NNAT
- Any canon item whose source is a name without URL, version, owner, and license.

### Requires Shadow-Only Treatment

- R-Zero
- FARA-7B
- Recursive dreaming
- Computer-use action lanes
- Protocol adapters with write actions
- Training backends
- Harness auto-rewrites

### Can Become Design Requirements Now

- Harness registry and raw trace retention.
- HiveMind graph schema and compiler.
- Effective-context reporting.
- EBT route trace dimensions.
- Protocol adapter registry with zero-trust fields.
- Security posture panel.
- Read-only VisualOps registry/trace dashboard.

## Open Questions That Remain After Research

1. What exact source does the canon intend by "Bloom"?
2. What exact GitHub repository is the intended "Annotation Toolkit" behind NNAT?
3. Which model licenses are acceptable for the commercial NexusNet product lane?
4. What held-out eval families will gate harness, memory, EBT, protocol, and training changes?
5. Which runtime scorecards should be implemented first: desktop local, GPU server, mobile/local, or provider adapter?
6. What exact VisualOps data contracts should ship before any approval/action controls are added?

## Final Recommendation

Proceed in this order:

1. Implement the candidate/source registry schema and seed it with these records.
2. Build read-only VisualOps panels from registry and trace state.
3. Add HiveMind graph and effective-context schemas.
4. Add HarnessRegistry and EBT route trace records.
5. Add zero-trust protocol/security posture reporting.
6. Only then prototype shadow-only lanes for dreaming, computer-use, training backends, and external protocol adapters.

This keeps the complete canon intact while making the research candidates operationally useful, auditable, and blocked from silent authority escalation.
