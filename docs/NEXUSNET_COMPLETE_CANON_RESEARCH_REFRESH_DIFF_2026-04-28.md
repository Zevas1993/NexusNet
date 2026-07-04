# NexusNet Complete Canon Research Refresh Diff - 2026-04-28

Purpose: redo the research-refresh pass using the complete canon book instead of the shorter canon file, then identify what has changed, what is better now, and how those updates should improve NexusNet without silently replacing locked canon.

Primary input: `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`

Prior shorter refresh for comparison: `docs/NEXUSNET_RESEARCH_REFRESH_DIFF_2026-04-28.md`

Candidate research dossier: `docs/NEXUSNET_RESEARCH_CANDIDATE_DOSSIER_2026-04-28.md`

Updated research catalog: `docs/NEXUSNET_COMPLETE_CANON_UPDATED_RESEARCH_CATALOG_2026-04-28.md`

Open-first research expansion: `docs/NEXUSNET_OPEN_FIRST_RESEARCH_EXPANSION_2026-04-28.md`

Quantization and agentic research expansion: `docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md`

Forward research radar: `docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md`

Forward research deep dive: `docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md`

Research date: 2026-04-28

## Research Method

- Used the complete canon book as the controlling local source, including its 39 captured conversations, 6717 captured message nodes, and 15 aspect chapters.
- Checked current public sources where possible: official docs, official GitHub repositories, Hugging Face model/docs pages, arXiv/OpenReview papers, vendor research posts, and standards specifications.
- Treated third-party news and commentary as risk signals only, not as canon-changing evidence.
- Did not install packages, register providers, write hooks, run external agents, push PRs, merge code, deploy services, or enable autonomous execution.
- Preserved the core canon rule: research candidates can improve design, but locked NexusNet canon changes only through explicit registry, evidence, license, eval, security, and governance gates.

## Complete Book Scope Delta

The previous refresh was correct but too narrow. The complete book makes clear that NexusNet is not just a memory/control-center project. It is a brain-first neural-core product with a broad canon:

| Complete-book signal | Value |
|---|---:|
| Captured conversations | 39 |
| Captured message nodes | 6717 |
| User nodes | 930 |
| Assistant nodes | 3833 |
| Tool nodes | 1177 |
| System nodes | 777 |
| Known inaccessible chat | `Training LLM with ChatGPT` |

The complete-book refresh must therefore cover these older and broader lanes:

- Brain-first identity and native neural-core boundary.
- Mixtral, Devstral, MoE routing, mini-NexusNets, and expert assimilation.
- Cortex, Neural Bus, shared HiveMind, and non-linear scaling.
- Long context, effective context, RoPE/YaRN-style extension, and conversation consolidation.
- Multi-plane mind maps, MemoryNode, hypergraph memory, and cross-plane cognition.
- Recursive Neural Dreaming, replay, self-improvement, and consequence loops.
- Assistant Orchestrators, expert capsules, councils, critique, and consequence.
- EBT routing, decision traces, evals, benchmark evidence, and provenance.
- Teachers, distillation, RL, training jobs, and native growth.
- Tools, MCP, A2A, AG-UI, security, identity, consent, and audit.
- VisualOps, operator UI panels, visualizer, diagrams, and explainability.
- Runtime, hardware, local-first operation, safe mode, and packaging.
- Multimodal, GUI/computer-use, FARA, DeepEyes, LFM2, Qwen, and vision.
- Federation, privacy, meta-evolution, governance, and compliance.
- Research assimilation and candidate registry hygiene.

## Executive Findings

1. The complete canon remains directionally right. Current research strengthens the NexusNet thesis that the durable asset is the governed brain/harness/memory/eval layer, not a single model pick.
2. The strongest update is that harness engineering has become a first-class optimization target. NexusNet should store raw traces, propose harness diffs, and promote only through held-out eval gates.
3. The HiveMind should be a temporal, typed, graph-backed Memory OS, not just a vector store or wiki. Every AO and expert should have a mini graph that rolls up into the main HiveMind graph.
4. The 1M-token ambition should be framed as effective context, not raw prompt stuffing. Use graph memory, exact evidence archives, prefix/KV reuse, summaries, and context assembly.
5. Mixtral + Devstral remains a historical and near-term scaffold, but the model registry must now evaluate Devstral Small 1.1, Qwen3-VL, LFM2.5, Nemotron-Elastic, FARA-7B, and DeepEyesV2 as governed teachers or specialist lanes.
6. Protocols are useful but dangerous. MCP, A2A, and AG-UI should remain mediated capabilities with identity, consent, schema validation, sandboxing, and audit. None should become the brain authority.
7. VisualOps should be observability-first. The browser companion should show live brain path state, AO/expert activity, memory graph health, protocol posture, training gates, eval outcomes, runtime posture, and research registry changes.
8. Training and self-improvement should become legible to both humans and agents. Adopt structured reward specs, training manifests, trace-derived diagnostics, and explicit promotion provenance.
9. Security risk has increased. Agent ecosystems and MCP-style tool integration now need zero-trust defaults, privilege separation, signed capability definitions, and failure-visible dashboards.
10. Several older canon items need demotion from "candidate to implement" to "candidate to verify": Flash-DMD, Bloom, Codestral, raw weight surgery, and any external framework that cannot pass license, source, and eval review.

## Aspect Refresh Map

| Aspect | Complete-book canon | Current update | NexusNet improvement |
|---|---|---|---|
| 1. Brain-first identity | NexusNet is a neural-core brain, not a wrapper. | Harness research says the non-weight system layer drives large outcome differences. | Keep the brain-first boundary, but make harness/memory/eval artifacts native brain assets. |
| 2. MoE and experts | Mixtral + Devstral, expert routing, mini-NexusNets. | Devstral Small 1.1 is a stronger coding-agent candidate; Nemotron-Elastic validates elastic capacity; Qwen/LFM/FARA add specialist lanes. | Upgrade the model registry and expert-capsule scorecards. Do not do unsupervised weight surgery. |
| 3. Cortex and Neural Bus | Shared bus and cross-brain coordination. | A2A/AG-UI offer protocol surfaces, while SGLang gateway shows router-bound context and telemetry patterns. | Make Neural Bus evented, typed, auditable, and protocol-adapted. |
| 4. Long/effective context | 1M-token ambition and context consolidation. | Graph memory, prefix/KV reuse, LMCache, vLLM V1, SGLang RadixAttention, and indexed evidence memory are stronger than raw long-window claims. | Reword product claims as effective context with measurable assembly, cache reuse, and dereference coverage. |
| 5. Multi-plane memory | MemoryNode, hypergraph, cross-plane cognition. | Graphiti, MemOS, A-MEM, AgeMem, MemexRL, GraphRAG, and Graph-R1 converge on typed temporal graph memory plus exact evidence. | Create main HiveMind graph plus AO/expert subgraphs with typed edges, provenance, conflict records, and decay. |
| 6. Recursive dreaming | Replay, dreaming, self-improvement. | R-Zero and RAGEN show self-generated curricula and agent RL need tight diagnostics. | Make dreaming generate candidate tasks, traces, reward specs, and eval deltas before any training/promotion. |
| 7. AO/expert/council | AOs and experts coordinate, critique, and specialize. | LLM-Council is useful as a review/synthesis pattern, but not production governance alone. | Add council-style disagreement capture inside AO/Expert trace records, not as an external top-level app. |
| 8. EBT/evals/provenance | Route decisions need evidence. | Verifier research shows process/outcome separation, rubric quality, and hallucination checks matter. | Add EBT dimensions for evidence freshness, memory confidence, disagreement, risk, budget, and eval history. |
| 9. Training/native growth | Distillation, RL, reward, and promotion gates. | TRL v1.0, verl, NeMo-RL, RAGEN, AReaL, ROLL, and Agent Lightning improve candidate training backends. | Keep training disabled by default, but define backend manifests, structured warnings, and promotion provenance. |
| 10. Tools/protocol/security | MCP/code execution beneficial but gated. | MCP latest spec has clearer auth/schema layers, but security research shows high-risk agent-tool attack surfaces. | Keep MCP/A2A/AG-UI behind signed, scoped, sandboxed, auditable protocol adapters. |
| 11. VisualOps/control center | Control panel must show brain, AOs, experts, connections, and activity. | OTel GenAI, OpenInference, AG-UI events, and command-center patterns support real observability. | Build a browser companion that is read-only by default and backed by trace/registry APIs. |
| 12. Runtime/hardware | Local-first, hardware-aware, safe-mode execution. | vLLM V1, SGLang, LMCache, torchao, LFM2.5, and Nemotron reinforce local-first runtime scoring. | Add runtime scorecards for latency, throughput, cache hit rate, VRAM, quantization, fallback, and safe-mode reason. |
| 13. Multimodal/CUA | FARA, DeepEyes, LFM2, Qwen, vision. | FARA-7B and Universal Verifier improve CUA execution/eval; Qwen3-VL and LFM2.5 improve multimodal lanes. | Treat GUI/computer-use as a guarded tool lane with screenshot provenance, verifier labels, and consent gates. |
| 14. Federation/privacy | Federated learning and governance. | Protocol and agent-security risk grew. Federation needs privacy, identity, and trace scoping before scale. | Add federation manifests, per-node permissions, differential privacy candidates, and audit exports. |
| 15. Research assimilation | Candidate registry and canonical decisions. | The ecosystem changes too fast for untracked adoption. | Add source freshness, license, risk, eval status, implementation status, and deprecation fields to every candidate. |

## Updated Source Findings And NexusNet Deltas

### 1. Harness Engineering Is Now A Native NexusNet Concern

Current public update:

- Meta-Harness treats harness code as the optimization target and shows that access to raw traces is crucial for finding better harnesses.
- Natural-Language Agent Harnesses externalize control logic as portable natural-language artifacts executed through explicit contracts, durable artifacts, and adapters.
- AutoHarness and related work reinforce that task rules, constraints, and safety layers can be compiled into harnesses instead of buried in prompts.

Sources:

- [Meta-Harness](https://arxiv.org/abs/2603.28052)
- [Natural-Language Agent Harnesses](https://arxiv.org/abs/2603.25723)
- [AutoHarness](https://arxiv.org/abs/2603.03329)

Difference from complete canon:

- The complete canon already implies harness-like AO/expert orchestration, but it treats this mostly as architecture. Current research says the harness itself should be represented, traced, evaluated, and optimized as a product artifact.

How it improves NexusNet:

- Add a `HarnessRegistry` beside the candidate/source registry.
- Store raw failed traces, not just summaries.
- Require each AO/expert execution contract to include required outputs, budgets, permissions, completion conditions, and artifact paths.
- Promote harness changes through shadow runs and held-out evals before they can alter production behavior.

Recommended status:

- Promote to Phase 0/1 design priority.
- Do not auto-rewrite production harnesses without approval and eval gates.

### 2. HiveMind Should Become A Temporal Graph Memory OS

Current public update:

- Graphiti is a temporal knowledge graph framework designed for AI agents, with real-time incremental updates and hybrid semantic/keyword/graph retrieval.
- MemOS frames memory as a manageable system resource with representation, scheduling, migration, fusion, provenance, and versioning.
- A-MEM and AgeMem push memory beyond fixed store/retrieve hooks into agentic memory operations and evolving links.
- MemexRL argues for indexed experience memory where exact evidence can be kept outside the prompt but dereferenced when needed.

Sources:

- [Graphiti docs](https://help.getzep.com/graphiti/getting-started/welcome)
- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [Zep temporal knowledge graph paper](https://arxiv.org/abs/2501.13956)
- [MemOS](https://arxiv.org/abs/2507.03724)
- [A-MEM](https://openreview.net/pdf?id=LB0nTqxAKd)
- [AgeMem](https://arxiv.org/abs/2601.01885)
- [MemexRL](https://arxiv.org/abs/2603.04257)

Difference from complete canon:

- The canon asks for a HiveMind, per-AO/per-expert mini brains, memory stores, and a graph-like design. The newer evidence clarifies the missing mechanics: temporal edges, provenance, memory operations, lifecycle policy, conflict handling, and exact-evidence dereference.

How it improves NexusNet:

- Main HiveMind graph:
  - Stores project, user-approved canon, source ledgers, AO results, expert capsule knowledge, eval history, runtime evidence, and research registry records.
- AO mini HiveMind graph:
  - Stores role-specific state, decisions, recent traces, tools, local eval results, unresolved risks, and handoff edges to other AOs.
- Expert mini HiveMind graph:
  - Stores domain knowledge, capability bounds, teacher sources, tool affordances, and confidence/decay metadata.
- Cross-graph edges:
  - `supports`, `contradicts`, `updates`, `depends_on`, `derived_from`, `routes_to`, `delegates_to`, `trained_from`, `validated_by`, `supersedes`.
- Memory operations:
  - `store`, `retrieve`, `update`, `summarize`, `archive`, `discard`, `link`, `conflict`, `dereference`, `promote`, `decay`.

Recommended status:

- Promote from concept to core design.
- Keep external graph systems as candidates, not hidden dependencies.

### 3. Karpathy LLM Wiki Should Be Compiled Into HiveMind, Not Copied As-Is

Current public update:

- Karpathy's LLM Wiki pattern defines a persistent, LLM-maintained, interlinked markdown knowledge base with raw immutable sources, generated wiki pages, and a schema file.
- Graphify turns code, docs, papers, images, and videos into a queryable graph artifact and can be used by coding assistants as a context accelerator.

Sources:

- [Karpathy LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Graphify GitHub](https://github.com/safishamsi/graphify)
- [Graphify PyPI package](https://pypi.org/project/graphifyy/)

Difference from complete canon:

- The complete canon asks for a HiveMind graph and project memory. Karpathy/Graphify add the practical build pattern: compile sources once into durable pages and graph records, then keep them current with log/index/lint operations.

How it improves NexusNet:

- Add a `HiveMindCompiler` concept:
  - Raw sources remain immutable.
  - Canon pages are generated and versioned.
  - Graph nodes/edges are generated from the pages and evidence records.
  - Each update writes a chronological log entry and provenance record.
  - Lint passes detect stale claims, orphan nodes, contradictions, source gaps, and high-risk unsourced assertions.

Recommended status:

- Adopt the pattern, not the exact tooling.
- Do not let LLM-written wiki pages become authority without source/provenance links.

### 4. Effective Context Beats Raw Context

Current public update:

- vLLM V1 exposes prefix caching, context extension, KV events, disaggregated prefill, metrics, and OpenTelemetry proof-of-concept support.
- SGLang emphasizes RadixAttention, prefix caching, structured outputs, tool parsing, metrics, request replay, crash replay, and an emerging model gateway.
- LMCache targets KV reuse across requests and runtime integrations.
- Graph and indexed memory systems reduce repeated rediscovery by storing compiled knowledge and exact-evidence handles.

Sources:

- [vLLM V1 guide](https://docs.vllm.ai/en/latest/usage/v1_guide/)
- [SGLang docs](https://docs.sglang.io/)
- [SGLang observability](https://docs.sglang.io/advanced_features/observability.html)
- [SGLang model gateway](https://docs.sglang.io/advanced_features/sgl_model_gateway.html)
- [LMCache docs](https://docs.lmcache.ai/)
- [Transformers torchao quantization](https://huggingface.co/docs/transformers/en/quantization/torchao)

Difference from complete canon:

- The canon's 1M-token ambition is still valid if it means effective context capacity. It is risky if interpreted as dumping 1M tokens into every prompt.

How it improves NexusNet:

- Add an `EffectiveContextReport`:
  - Prompt tokens used.
  - Cached/prefix tokens reused.
  - Graph nodes consulted.
  - Evidence records dereferenced.
  - Summaries inserted.
  - Raw sources avoided.
  - Recall checks passed.
  - Context assembly reason.
- Add runtime scorecards for vLLM, SGLang, llama.cpp, LM Studio, Ollama, and local mobile runtimes.

Recommended status:

- Update claims and UI copy to "effective context" unless raw context is actually benchmarked.

### 5. Model And Teacher Registry Needs A Fresh Ranking Pass

Current public update:

- Devstral Small 1.1 is Apache 2.0, 24B, 128k context, and positioned by Mistral as an agentic coding model for software engineering agents.
- Nemotron-Elastic-12B provides a current elastic-size reference for 6B/9B/12B-style operation.
- Qwen3-VL is a current multimodal family with dense/MoE variants, visual understanding, video grounding, and 128k text configuration in the documented model config.
- LFM2.5-VL is a small Liquid AI multimodal model lane relevant to local/edge vision.
- DeepEyesV2 remains relevant as an agentic multimodal architecture influence.

Sources:

- [Devstral Small 1.1](https://huggingface.co/mistralai/Devstral-Small-2507)
- [Devstral Medium](https://huggingface.co/mistralai/Devstral-Medium-2507)
- [Mixtral 8x22B Instruct](https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1)
- [Nemotron-Elastic-12B](https://huggingface.co/nvidia/Nemotron-Elastic-12B)
- [Qwen3-VL Transformers docs](https://huggingface.co/docs/transformers/main/en/model_doc/qwen3_vl)
- [LFM2.5-VL-1.6B](https://huggingface.co/LiquidAI/LFM2.5-VL-1.6B)
- [DeepEyesV2](https://arxiv.org/abs/2511.05271)

Difference from complete canon:

- Mixtral + Devstral is canon as a near-term scaffold and project-history decision. It should not freeze the model roster forever.
- Current sources support a richer teacher/capsule registry where different models compete for coding, multimodal, GUI, edge, reasoning, and elastic-runtime roles.

How it improves NexusNet:

- Add registry fields:
  - `role`: base, teacher, evaluator, specialist expert, CUA, multimodal, coding, summarizer, local fallback.
  - `license_status`: allowed, restricted, unknown, requires review.
  - `runtime_fit`: local GPU, CPU, mobile, vLLM, SGLang, llama.cpp, cloud.
  - `context_claim`: raw window and measured effective-context performance.
  - `teacher_value`: distillation target, reward model, critique model, synthetic-data generator.
  - `promotion_status`: candidate, shadow, eval-passed, blocked, deprecated.

Recommended status:

- Keep Mixtral/Devstral canon, but mark new models as governed candidates.
- Require benchmarks before declaring any model superior inside NexusNet.

### 6. Recursive Dreaming Should Inherit R-Zero And RAGEN Discipline

Current public update:

- R-Zero uses a Challenger/Solver loop to generate tasks and self-improve from zero human-labeled data.
- RAGEN focuses on reinforcement learning for reasoning agents in interactive environments, with diagnostics for reasoning collapse and stable training interventions.
- TRL v1.0 broadened and stabilized post-training support, while explicitly acknowledging that post-training methods keep shifting.
- verl, NeMo-RL, AReaL, ROLL, and Agent Lightning broaden the candidate backend space for agent RL and scalable post-training.

Sources:

- [R-Zero](https://arxiv.org/abs/2508.05004)
- [RAGEN](https://github.com/mll-lab-nu/RAGEN)
- [TRL v1.0](https://huggingface.co/blog/trl-v1)
- [verl](https://github.com/verl-project/verl)
- [NeMo-RL docs](https://docs.nvidia.com/nemo/rl/latest/index.html)
- [AReaL](https://github.com/inclusionAI/AReaL)
- [ROLL](https://github.com/alibaba/ROLL)
- [Agent Lightning](https://arxiv.org/abs/2508.03680)

Difference from complete canon:

- The canon's dreaming/self-improvement ambition is correct, but the updated field shows that the loop must be narrow, diagnostic-rich, and gated.

How it improves NexusNet:

- Add `DreamRunManifest`:
  - task source, challenger model, solver model, reward spec, allowed tools, memory snapshot, generated artifacts, failure taxonomy, eval family, and promotion gate.
- Add collapse diagnostics:
  - repeated templates, reward variance collapse, no-op skill loops, verifier overfitting, memory poisoning, and hallucinated completion.
- Split dreaming into:
  - idea generation,
  - task generation,
  - attempt,
  - critique,
  - consequence scoring,
  - eval replay,
  - registry proposal.

Recommended status:

- Implement as shadow-only until promotion provenance and eval gates are complete.

### 7. EBT Routing Must Include Verifier And Trace Signals

Current public update:

- Microsoft FARA/Universal Verifier work shows that verifier design, rubric quality, process/outcome separation, and hallucination detection can matter more than simply picking a stronger model.
- Meta-Harness shows raw traces are much more valuable than over-compressed summaries for improving harness behavior.
- Graph-R1 and GraphRAG-R1 style work strengthens the idea that retrieval/routing can be optimized as multi-turn graph interaction rather than one-shot chunk retrieval.

Sources:

- [Microsoft Universal Verifier article](https://www.microsoft.com/en-us/research/articles/the-art-of-building-verifiers-for-computer-use-agents/)
- [Universal Verifier paper](https://arxiv.org/abs/2604.06240)
- [FARA-7B](https://arxiv.org/abs/2511.19663)
- [Graph-R1](https://arxiv.org/abs/2507.21892)
- [Graph-R1 GitHub](https://github.com/LHRLAB/Graph-R1)
- [GraphRAG-R1 paper page](https://huggingface.co/papers/2507.23581)

Difference from complete canon:

- EBT routing is already central, but the complete book leaves the final formula unresolved. Current work clarifies dimensions that should be mandatory even before weights are tuned.

How it improves NexusNet:

- EBT score dimensions should include:
  - task fit,
  - memory confidence,
  - evidence freshness,
  - route risk,
  - tool risk,
  - model/runtime budget,
  - eval history,
  - verifier confidence,
  - disagreement/council spread,
  - user consent requirement,
  - fallback availability.

Recommended status:

- Keep exact EBT weights unresolved.
- Add required score dimensions and trace output now.

### 8. Protocols Should Be Mediated Capabilities, Not Authority

Current public update:

- MCP latest spec formalizes core JSON-RPC, lifecycle, authorization for HTTP transports, schemas, client/server features, and utilities.
- A2A 1.0 provides agent discovery, task operations, streaming, artifacts, security schemes, and agent card signing.
- AG-UI provides event-driven interaction between agents and frontends, making it a good fit for VisualOps streams.
- OTel GenAI and OpenInference provide trace conventions for model, agent, tool, retrieval, and framework observability.

Sources:

- [MCP specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic)
- [A2A specification](https://a2a-protocol.org/dev/specification/)
- [AG-UI docs](https://docs.ag-ui.com/)
- [AG-UI events](https://docs.ag-ui.com/concepts/events)
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [OpenInference spec](https://arize-ai.github.io/openinference/spec/)

Difference from complete canon:

- The complete canon accepts MCP/code execution as beneficial and treats A2A/AG-UI as standards candidates. The update is that these now map cleanly to different NexusNet roles:
  - MCP for tool/resource access.
  - A2A for external agent handoff envelopes.
  - AG-UI for browser companion event streams.
  - OTel/OpenInference for telemetry export.

How it improves NexusNet:

- Add `ProtocolAdapterRegistry` fields:
  - protocol, transport, auth, identity, consent mode, allowed verbs, sandbox class, schema validation, audit sink, source trust, and kill switch.
- Require protocol adapters to emit standardized trace fields into VisualOps.

Recommended status:

- Implement read-only and local-only first.
- Keep write actions, autonomous agent routing, and cloud routing disabled until gates pass.

### 9. Security Posture Needs To Move To Zero Trust

Current public update:

- MCP/tool-poisoning and agent skill ecosystems are now documented high-risk areas.
- OpenClaw-style security analyses emphasize that prompt-level safeguards are insufficient for tool-augmented agents with local permissions.
- OWASP describes MCP tool poisoning as indirect prompt injection through tool definitions.

Sources:

- [OWASP MCP Tool Poisoning](https://owasp.org/www-community/attacks/MCP_Tool_Poisoning)
- [Systematic Security Evaluation of OpenClaw and Variants](https://arxiv.org/abs/2604.03131)
- [OpenClaw PRISM](https://arxiv.org/abs/2603.11853)
- [ClawGuard](https://arxiv.org/abs/2604.11790)
- [OpenClaw security docs](https://docs.openclaw.ai/security)

Difference from complete canon:

- The canon already says security is non-negotiable. The current field makes this more urgent and more concrete: any autonomous tool/plugin/skill capability is hostile until verified.

How it improves NexusNet:

- Add a `SecurityPosturePanel` to VisualOps:
  - unsigned tools,
  - exposed local endpoints,
  - broad filesystem access,
  - untrusted tool descriptions,
  - prompt-injection exposure,
  - missing audit sinks,
  - stale protocol adapters,
  - disabled sandbox,
  - dangerous schedules,
  - pending human approvals.
- Add privilege separation:
  - untrusted content reader,
  - planner,
  - tool executor,
  - memory writer,
  - deployment actor,
  - training actor.

Recommended status:

- Raise from supporting concern to Phase 0 product gate.

### 10. VisualOps Should Become The Browser-Based Visual Companion

Current public update:

- Observability-first command centers provide more business value than decorative mission-control UIs.
- AG-UI can support event streaming to a frontend.
- OTel/OpenInference can normalize model/tool/retrieval traces.
- SGLang and vLLM expose runtime metrics that should be displayed beside NexusNet-specific brain-path traces.

Sources:

- [AG-UI docs](https://docs.ag-ui.com/)
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [OpenInference spec](https://arize-ai.github.io/openinference/spec/)
- [SGLang production metrics](https://docs.sglang.io/references/production_metrics.html)
- [vLLM metrics docs](https://docs.vllm.ai/en/latest/usage/v1_guide/)

Difference from complete canon:

- The complete book and architecture image make VisualOps central. The update is that the companion should be backed by live registries and traces, not manually drawn state.

How it improves NexusNet:

- Browser companion panels:
  - Neural Core Brain status.
  - Input layer ingestion queue.
  - Context/Memory layer graph health.
  - Main HiveMind graph.
  - AO Hive list with live state and mini-graph health.
  - Expert Hive list with role, teacher, memory, eval, and model/runtime status.
  - EBT route trace and decision record viewer.
  - Build/execution artifacts.
  - Dreaming/self-improvement queue.
  - Training gate status.
  - Runtime/hardware posture.
  - Protocol/security posture.
  - Governance/audit/export status.
  - Research assimilation registry.
  - Federation/privacy/compliance posture.
- Default mode:
  - read-only dashboard,
  - no autonomous task launch,
  - no deployment,
  - no PR merge,
  - no training job,
  - no provider registration,
  - no hook writes.

Recommended status:

- Proceed with read-only visual companion first.
- Add approval-gated control actions later.

### 11. Computer-Use Agents Are Guarded Tool Lanes

Current public update:

- FARA-7B is a small, open-weight computer-use model designed to perceive screenshots and output coordinate actions.
- Microsoft verifier work separates process quality from final outcome and flags hallucinated completion with screenshot evidence.
- Qwen3-VL, LFM2.5-VL, and DeepEyesV2 strengthen the multimodal specialist lane.

Sources:

- [FARA-7B](https://arxiv.org/abs/2511.19663)
- [Microsoft verifier article](https://www.microsoft.com/en-us/research/articles/the-art-of-building-verifiers-for-computer-use-agents/)
- [Qwen3-VL docs](https://huggingface.co/docs/transformers/main/en/model_doc/qwen3_vl)
- [LFM2.5-VL-1.6B](https://huggingface.co/LiquidAI/LFM2.5-VL-1.6B)
- [DeepEyesV2](https://arxiv.org/abs/2511.05271)

Difference from complete canon:

- FARA and DeepEyes are accepted influences, but neither should replace NexusNet. They become tools/teachers/capsules under NexusNet governance.

How it improves NexusNet:

- Add `ComputerUseLane`:
  - screenshot evidence,
  - action proposal,
  - allowed action class,
  - verifier rubric,
  - process score,
  - outcome score,
  - environment blocker label,
  - rollback/undo availability,
  - human approval requirement.

Recommended status:

- Candidate lane only.
- No silent desktop control.

### 12. LLM-Council, Agent0, Space-Agent, Bloom, And NNAT Need Clean Assimilation Boundaries

Current public update:

- LLM-Council is a small local app that asks multiple LLMs for answers, has them review/rank each other, then synthesizes a final response.
- Agent0/space-agent remains an external agent framework/repo to mine for patterns, not a replacement for NexusNet.
- Bloom, based on the public site found during this refresh, appears to be an open registry for AI agents. If the canon intended Anthropic's behavioral-eval Bloom instead, that exact source still needs to be pinned.
- The NexusNet Annotation Toolkit (NNAT) remains a valuable concept, but the exact GitHub Annotation Toolkit source should be pinned in the candidate registry before implementation.

Sources:

- [LLM-Council](https://github.com/karpathy/llm-council)
- [space-agent](https://github.com/agent0ai/space-agent)
- [Bloom open registry](https://www.usebloom.org/)

Difference from complete canon:

- The complete book contains older assimilation decisions, but some source identities remain ambiguous or have shifted.

How it improves NexusNet:

- Add `candidate_source_identity` to registry records:
  - canonical name,
  - exact URL,
  - source type,
  - license,
  - last verified date,
  - intended assimilation,
  - replacement risk,
  - implementation status,
  - unresolved source ambiguity.

Recommended status:

- LLM-Council: adopt council/disagreement trace pattern only.
- Agent0/space-agent: review for UI/agent-space patterns only.
- Bloom: mark source ambiguity until exact intended Bloom is pinned.
- NNAT: keep concept accepted, require exact source pin and schema-first implementation.

### 13. Flash-DMD Is Useful But Not Central To NexusNet Yet

Current public update:

- Flash-DMD is an image-generation distillation/RL paper, not a general NexusNet brain replacement.
- It may be relevant to future visual generation or multimodal distillation, but it is not a core brain-path dependency.

Sources:

- [Flash-DMD arXiv](https://arxiv.org/abs/2511.20549)
- [Flash-DMD OpenReview entry](https://openreview.net/forum?id=PwelCOoiiA)

Difference from complete canon:

- The complete book notes uncertainty around the original Flash-DMD paper identity. Current lookup identifies an image-generation distillation paper, so the safe action is demotion until exact relevance is proven.

How it improves NexusNet:

- Keep as a research-only candidate for visual model distillation or fast image-generation lanes.

Recommended status:

- Demote to research watchlist.
- Do not implement in core self-improvement.

## Recommended Registry Changes

Add or strengthen these registry fields for every source/candidate:

| Field | Why it matters |
|---|---|
| `source_url` | Prevents ambiguous names like Bloom or Flash-DMD from drifting. |
| `source_kind` | Paper, repo, docs, model card, standard, video, transcript, internal canon. |
| `last_verified_on` | Forces refresh for fast-moving sources. |
| `license_status` | Blocks accidental commercial or redistribution violations. |
| `replacement_risk` | Flags anything that might incorrectly replace NexusNet brain authority. |
| `assimilation_mode` | Pattern, teacher, runtime, protocol, UI, eval, training backend, research-only. |
| `gates_required` | Security, eval, license, local-first, user consent, audit, promotion. |
| `evidence_links` | Stores source line, artifact, benchmark, trace, or repo reference. |
| `implementation_status` | Unreviewed, candidate, design, prototype, shadow, active, blocked, deprecated. |
| `owner_layer` | Neural core, AO Hive, Expert Hive, HiveMind, VisualOps, Runtime, Training, Governance. |

## Priority Update

### Wave 1 - Canon And Safety Foundation

1. Create the complete candidate/source registry using the fields above.
2. Add protocol/security gates for MCP, A2A, AG-UI, skills, tools, hooks, schedules, PR actions, deployments, and training jobs.
3. Update VisualOps read-only companion requirements from the complete architecture image and complete book.
4. Add EBT trace dimensions and decision-record schema.
5. Add HiveMind graph schemas for main graph, AO subgraphs, expert subgraphs, and cross-graph edges.

### Wave 2 - Memory, Harness, Runtime, And Observability

1. Implement HiveMind compiler pattern: raw sources, generated canon pages, graph nodes/edges, update logs, lint checks.
2. Add HarnessRegistry and AO/expert execution contracts.
3. Add runtime scorecards for vLLM, SGLang, LMCache, llama.cpp, LM Studio, Ollama, and local/mobile lanes.
4. Normalize telemetry toward OTel GenAI and OpenInference while preserving NexusNet brain-path fields.
5. Add dashboard panels for memory graph health, runtime posture, protocol posture, and eval outcomes.

### Wave 3 - Self-Improvement And Native Growth

1. Add DreamRunManifest and challenger/solver/evaluator trace records.
2. Add training backend manifests for TRL, verl, NeMo-RL, RAGEN, AReaL, ROLL, and Agent Lightning.
3. Add model/teacher registry scorecards for Devstral Small 1.1, Nemotron-Elastic, Qwen3-VL, LFM2.5, FARA-7B, and DeepEyesV2.
4. Add held-out eval gates for memory updates, harness changes, route changes, tool adapters, and trained artifacts.
5. Keep all promotion disabled until provenance, reward spec, license, security, and eval gates pass.

## Items To Demote Or Treat Carefully

| Item | Complete-book status | Updated status | Reason |
|---|---|---|---|
| Raw 1M context | Ambition | Reframe as effective context | Current systems favor memory/cache/evidence assembly over raw prompt stuffing. |
| Mixtral + Devstral weight fusion | Historical near-term scaffold | Keep as candidate/scaffold, not automatic implementation | Shape/license/runtime/eval risks remain. |
| Devstral | Specialist expert/coding model | Upgrade to latest Devstral Small 1.1 candidate | Stronger current model card and Apache 2.0 license. |
| Codestral | Possible coding model | License-gated candidate | Needs current license review before commercial use. |
| Bloom | Behavioral-eval inspiration in canon | Source-identity unresolved | Current public Bloom found is an agent registry; exact intended source must be pinned. |
| Flash-DMD | Vision/distillation candidate | Research watchlist | Relevant paper appears image-generation focused, not core brain self-improvement. |
| External agent frameworks | Assimilation targets | Pattern-only unless gated | Do not let external orchestration replace NexusNet brain authority. |
| MCP | Beneficial tool protocol | High-risk mediated adapter | Tool poisoning, prompt injection, auth/sandbox risk. |
| CUA models | FARA/DeepEyes influence | Guarded tool/teacher lane | Needs screenshot provenance, action scopes, and verifier labels. |
| Autonomous self-improvement | Core ambition | Shadow-first, eval-gated | Training/promotion without evidence would violate governance. |

## Open Gaps After This Refresh

1. The `Training LLM with ChatGPT` chat remains inaccessible and should not be inferred from surrounding context.
2. The exact source behind "GitHub Annotation Toolkit" needs to be pinned before NNAT implementation.
3. The exact intended "Bloom framework" source needs disambiguation. The current public `usebloom.org` source is an agent registry, not enough to confirm the canon's behavioral-eval interpretation.
4. Codestral and any non-Apache models need current license review before inclusion in a commercial product lane.
5. Model benchmarks must be run in NexusNet's own harness before changing default teachers, experts, or base candidates.
6. No external protocol should be write-enabled until a protocol adapter passes identity, schema, sandbox, consent, and audit tests.
7. VisualOps needs real trace/registry data surfaces before adding action buttons.
8. Dreaming/self-improvement needs held-out eval families before promotion or training jobs.

## Final Recommendation

The complete canon book does not call for replacing NexusNet with Graphiti, Graphify, FARA, LLM-Council, R-Zero, Devstral, Qwen, SGLang, or any protocol. It calls for a stronger NexusNet:

- brain-first,
- graph-backed,
- trace-governed,
- local-first,
- security-gated,
- harness-aware,
- eval-driven,
- visually observable,
- and capable of native growth only through explicit promotion gates.

The most important next concrete product artifact is a read-only VisualOps control center backed by the full registry/trace layer:

1. Main HiveMind graph and mini AO/expert graphs.
2. AO/expert activity, memory, tools, model/runtime, and eval state.
3. EBT route traces and decision records.
4. Protocol/security posture.
5. Runtime/hardware/cache posture.
6. Dreaming/training/promotion gates.
7. Research assimilation registry with source freshness, license, risk, and implementation status.

That gives NexusNet the browser-based visual companion the user requested, while preserving the safety rule that no external package install, provider registration, hook write, PR push/merge, deployment, training job, or autonomous execution is silently enabled.
