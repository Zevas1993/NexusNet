# NexusNet Research Refresh Diff - 2026-04-28

Purpose: compare the NexusNet chat/research canon against current public sources and identify better or newer versions of the ideas that should improve NexusNet without silently replacing locked canon.

Primary input: `docs/NEXUSNET_CHAT_RESEARCH_CANON_2026-04-28.md`

Research date: 2026-04-28

## Research Method

- Used current public sources where available: official documentation, official GitHub repositories, Hugging Face model/docs pages, arXiv/OpenReview papers, and vendor research posts.
- Treated third-party news as supporting context only, mainly for security and adoption risk.
- Did not install packages, register providers, enable hooks, execute external agents, push PRs, or change runtime behavior.
- Kept the canon rule intact: research candidates can improve design, but locked NexusNet canon changes only through explicit registry, evidence, license, eval, and security gates.

## Executive Summary

The canon is directionally correct. The strongest 2026 updates do not argue for replacing NexusNet with one external framework. They argue for hardening NexusNet as a governed brain-first system with these upgrades:

1. Turn HiveMind memory into a temporal, typed, graph-backed system.
2. Give every AO and expert a mini knowledge graph that rolls up into the main HiveMind graph.
3. Treat memory operations as governed tool actions: store, retrieve, update, summarize, archive, discard, dereference, and provenance lookup.
4. Add indexed evidence memory so long tasks can keep compact summaries while preserving exact artifacts.
5. Make VisualOps an observability-first command center backed by trace schemas, not a decorative mission control.
6. Keep MCP, A2A, and AG-UI disabled by default until identity, consent, sandbox, schema, and audit gates pass.
7. Use harness engineering as a first-class optimization target, but gate self-evolution through held-out evals and raw trace evidence.
8. Expand runtime scorecards around vLLM V1, SGLang, LMCache, torchao, and edge model lanes.
9. Treat GUI/computer-use models as guarded execution tools, not autonomous operators.
10. Keep training/fine-tuning behind artifact, reward, license, security, and promotion-provenance gates.

## Canon Delta Matrix

| Canon area | Canon stance | Current update or better version | NexusNet improvement | Recommended action |
|---|---|---|---|---|
| Brain-first identity | NexusNet is the neural-core brain; Nexus is the shell. | Current agent ecosystem is moving toward harness/runtime specialization, but external agents remain wrappers around model calls. | Keep NexusBrain as authority. Use external protocols and agents only as mediated capabilities. | No canon change. Preserve locked split. |
| AO Hive | AOs coordinate domain workflows but cannot mutate production memory or promote models. | Harness papers emphasize explicit contracts, durable artifacts, and delegation boundaries. | Encode AO contracts as typed execution contracts with required outputs, budgets, permissions, completion conditions, and artifact paths. | Upgrade AO registry schema and VisualOps display. |
| Expert capsules | 19 starting expert capsules are locked. | Multi-agent and MoE practice increasingly uses traceable roles and narrow delegation rather than broad always-on agents. | Give each expert a scoped mini-HiveMind graph, permissions, eval coverage, memory access class, and evidence freshness. | Add mini-graph metadata to expert registry. |
| HiveMind graph | Canon wants main HiveMind plus per-AO/expert mini-brains. | Graphiti/Zep, Graphify, A-MEM, AgeMem, MemexRL, LightMem, and SwiftMem all strengthen the case for typed graph/evidence memory. | Make the HiveMind a temporal graph with per-brain subgraphs, typed edges, provenance, decay, conflict records, and exact-evidence dereference. | Promote to Phase 4/5 design priority. |
| Memory OS | Memory operations and provenance are already part of the roadmap. | MemOS formalizes memory as schedulable resources; AgeMem learns memory operations as tool actions; MemexRL keeps exact evidence out of context but dereferenceable. | Split memory into records, operations, scheduler policy, lifecycle, governance, and evidence archives. | Registry update: strengthen MemOS/AgeMem/MemexRL candidates. |
| Karpathy LLM wiki | User requested Karpathy-style brain/wiki research and graph improvement. | Karpathy's pattern favors LLM-maintained, interlinked, git-versionable knowledge. Graphify now turns mixed corpora into queryable graph artifacts and MCP-accessible graph state. | Add a local HiveMind compiler that writes Markdown pages plus machine-readable graph records and updates them through governed Memory OS actions. | Prototype. Do not make external Graphify a hidden dependency. |
| RAG/retrieval | Retrieval is capability, not cognition. | New memory systems combine graph, temporal, sparse/dense, and evidence indexing instead of flat vector lookup alone. | Retrieval should feed brain path trace, Memory OS, context assembly, and EBT route scoring. | Keep RAG subordinate to NexusBrain. Add graph/evidence retrieval metrics. |
| EBT routing | Contract locked; exact score weights unresolved. | Harness and memory research show that narrow attempt loops and raw trace feedback matter more than broad search. | EBT should include memory confidence, evidence freshness, route risk, eval history, runtime budget, and disagreement state. | Keep formula unresolved, but add required score dimensions. |
| Harness engineering | NexusNet has factory/self-improvement ambitions. | Meta-Harness shows harness code itself can be optimized using raw failed traces; NLAH shows harness logic can be represented as portable natural language contracts. | NexusNet should store harness traces, propose harness diffs, and test them in shadow before promotion. | Add harness registry and held-out eval gate. |
| Evaluation | Canon requires trace-first evals. | DeepEval, OpenAI agent evals, OSWorld-Verified, and Microsoft Fara verifier work converge on trace grading, task-specific rubrics, and process/outcome separation. | Add explicit eval families for route choice, memory recall, tool correctness, CUA action success, security holds, and hallucinated completion. | Upgrade eval roadmap and VisualOps panels. |
| MCP | Candidate protocol, disabled by default. | MCP spec now has schema/auth guidance, but recent security research/news shows MCP-style local execution and registries remain high risk. | NexusNet should require signed server definitions, schema validation, transport policy, consent, sandboxing, output sanitization, and audit. | Keep disabled by default. Raise risk level. |
| A2A | Candidate protocol for agent interoperability. | A2A positions itself as a standard for interoperability between independent agent systems. | Use A2A only for AO/external-agent handoff envelopes, never for brain authority transfer. | Candidate. Require identity and delegation provenance. |
| AG-UI | Candidate protocol for agent/user interaction. | AG-UI standardizes event-driven agent-to-frontend interaction. | Good fit for browser-based visual companion, live activity streams, task status, approvals, and replay panels. | Prototype UI transport only, not cognition. |
| Observability | VisualOps is required, dense, and truthful. | OpenTelemetry GenAI and OpenInference provide portable semantic conventions for model, agent, tool, retrieval, and framework traces. | Normalize NexusNet traces toward OTel/OpenInference while preserving NexusNet-specific brain path fields. | Add telemetry mapping document and exporter candidate. |
| Runtime | vLLM, SGLang, LMCache, torchao are candidates. | vLLM V1 simplified scheduling; SGLang has production tracing/metrics and broad runtime features; LMCache targets reusable KV cache; torchao has current quantization and KV cache support. | Runtime scorecards should compare local/cloud, vLLM/SGLang, KV reuse, quantization, context cap, fallback, hardware, and safe-mode reasons. | Strengthen runtime scorecard schema. |
| Long context | One-million-token target is effective context, not raw context. | LMCache, vLLM prefix caching, SGLang RadixAttention, MemexRL indexed evidence, and graph memory support effective context better than raw-window promises. | Position one-million-token goal as effective-context assembly across memory graph, exact evidence, summaries, and cache reuse. | Keep wording strict. No raw-context claim. |
| TriAttention and CASK | TriAttention was research-only. | TriAttention has an April 2026 arXiv paper; CASK appears as a newer KV-compression candidate claiming improved fidelity in some gates. | Both are research-only optimization ideas, not product dependencies. | Keep research-only until reproducible local benchmark exists. |
| Training/RL | Training gates exist but real jobs are gated. | TRL v1.0 claims a stability milestone and broad post-training method coverage; verl, SkyRL, and OpenRLHF continue to move toward scalable agentic/VLM RL. | Use these as external training backends behind reward specs, dataset manifests, eval reports, license review, and promotion gates. | Candidate. No autonomous training enablement. |
| Multimodal/GUI | Computer-use and GUI actions require consent, audit, sandbox, rollback. | Qwen3-VL improves multimodal long-context vision; LFM2.5 strengthens edge and browser/local lanes; Fara-7B and its verifier work improve local computer-use patterns. | Add CUA as guarded tool lane with screenshot provenance, action plan, user approval at critical points, and verifier result. | Candidate. No silent desktop control. |
| Local-first productization | Local-first remains default; cloud is capability tier. | OpenJarvis and LFM2.5 reinforce local-first, device-aware execution, while agent security failures reinforce least privilege. | NexusNet should show local/cloud posture, provider provenance, and degraded/fallback mode in VisualOps. | Keep local-first default. Add product status evidence. |
| Security | Security is non-negotiable. | OpenClaw-style ecosystems show the risk of broad local permissions, exposed panels, malicious extensions, and prompt-injected skills. | NexusNet must treat tool/plugin ecosystems as hostile until signed, reviewed, sandboxed, and scoped. | Raise protocol/plugin governance priority. |
| Visual control center | Control center must show connections, activity, memory, AOs, experts, runtime, training, governance. | Observability-first dashboards are more valuable than decorative mission control. AG-UI and OTel/OpenInference can back live views. | Build panels around actual registry/trace/artifact state: Canon, Brain Path, AO Hive, Experts, Hive Activity, Memory OS, EBT, Protocol Security, Training, Runtime, Research, Eval, Federation, Packaging. | Proceed with browser-based visual companion backed by read-only APIs first. |

## Updated Source Findings

### 1. HiveMind Memory And Knowledge Graphs

#### Graphiti / Zep

Current public update:

- Graphiti is an open-source temporal context graph engine used by Zep for AI agent memory.
- It supports incremental temporal updates and combines graph, semantic, keyword, and temporal retrieval.
- Zep positions Graphiti as the open-source engine and Zep as managed context graph infrastructure with governance and low-latency retrieval.

Sources:

- [Graphiti docs](https://help.getzep.com/graphiti/getting-started/welcome)
- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [Zep temporal knowledge graph paper](https://arxiv.org/abs/2501.13956)

Difference from canon:

- The canon already names Graphiti/Zep as candidates. The update strengthens them from generic graph-memory inspiration to the best current reference for temporal graph memory and per-user/per-entity context graphs.

How this improves NexusNet:

- The main HiveMind can become a temporal graph with valid-time and recorded-time style fields.
- Every AO/expert mini-HiveMind can be an owned subgraph.
- Contradictions become graph events, not overwritten facts.
- VisualOps can show fact age, provenance, and relationship confidence.

Recommended NexusNet artifact:

- `HiveGraphRecord`
- `HiveGraphEdge`
- `HiveGraphEpisode`
- `HiveGraphConflict`
- `HiveGraphProjection` for AO/expert subgraphs

#### Karpathy LLM Wiki And Graphify

Current public update:

- Karpathy's LLM wiki pattern is a deliberately simple pattern: the LLM maintains interlinked Markdown knowledge that it can reread and update across sessions.
- Graphify has matured quickly into a multimodal code/docs/paper/audio/video knowledge graph tool. It supports AST extraction, local audio/video transcription, graph reports, HTML, JSON, and an MCP server for graph queries.
- Graphify's official package is `graphifyy`, not `graphify`.

Sources:

- [Karpathy llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Graphify GitHub](https://github.com/safishamsi/graphify)
- [Graphify PyPI](https://pypi.org/project/graphifyy/)

Difference from canon:

- Earlier canon treated Karpathy/wiki and Graphify mostly as conceptual inspiration. Current Graphify makes the idea operational across mixed corpora and assistant tools.

How this improves NexusNet:

- NexusNet should combine both patterns: human-readable Markdown Hive pages plus machine-readable graph artifacts.
- This gives end users the "AI brain wiki" experience while preserving strict provenance, evals, and governance.
- The graph should be generated from NexusNet registry/state, not be a separate untrusted source of truth.

Recommended gated approach:

- Local-only `hivemind-compiler` candidate.
- Inputs: canon docs, traces, Memory OS records, expert registry, AO registry, eval artifacts.
- Outputs: Markdown brain pages, `hivemind.graph.json`, source map, stale-node report, conflict report.
- No automatic overwrite of production memory without Memory OS approval.

#### MemOS

Current public update:

- MemOS treats memory as a manageable system resource.
- It uses memory units with metadata such as provenance and versioning and unifies plaintext, activation, and parameter-level memory concepts.

Source:

- [MemOS arXiv](https://arxiv.org/abs/2507.03724)

Difference from canon:

- The canon already has Memory OS terminology. MemOS provides a cleaner architectural vocabulary for memory scheduling, lifecycle, governance, and memory-type transitions.

How this improves NexusNet:

- Memory records should not be passive blobs. They should be scheduled, governed resources with lifecycle state, version chain, provenance, and promotion eligibility.
- Parameter-level or activation-level memory remains research-only unless NexusNet later has reproducible local training/promote gates.

Recommended NexusNet action:

- Add Memory OS scheduler concepts to the roadmap: priority, decay, conflict, summarization need, archival need, dereference cost, and retrieval budget.

#### A-MEM

Current public update:

- A-MEM proposes agentic memory that dynamically organizes memory instead of relying on static predeclared memory operations.
- It draws on Zettelkasten-style atomic notes and links.

Source:

- [A-MEM OpenReview PDF](https://openreview.net/pdf?id=LB0nTqxAKd)

Difference from canon:

- The canon wants mini-brains, but A-MEM sharpens how those mini-brains should evolve: memory links are created and revised as new records arrive.

How this improves NexusNet:

- Each expert mini-HiveMind should be able to create local links, propose edge changes, and surface conflicts.
- NexusBrain or MemoryAO approves what rolls up to the shared HiveMind.

Recommended gate:

- Expert-local graph changes are candidates until approved by MemoryAO plus NexusBrain.

#### AgeMem

Current public update:

- AgeMem integrates long-term and short-term memory management directly into the agent policy through tool-based memory actions.
- It uses progressive reinforcement learning and step-wise GRPO to learn memory operation behavior.

Sources:

- [AgeMem arXiv](https://arxiv.org/abs/2601.01885)
- [AgeMem Hugging Face paper page](https://huggingface.co/papers/2601.01885)

Difference from canon:

- The canon has memory operations. AgeMem makes those operations first-class agent actions that can be evaluated and trained.

How this improves NexusNet:

- Store, retrieve, update, summarize, discard, archive, and dereference should be explicit actions in traces.
- Memory operations can become eval targets and future reward signals.

Recommended gate:

- Add `memory_action` trace events before any learning loop uses them.

#### MemexRL, LightMem, SwiftMem, And HippoRAG2

Current public update:

- MemexRL uses indexed experience memory so agents can compress context while preserving exact evidence.
- LightMem and SwiftMem show the trend toward cheaper memory-augmented generation and faster memory search.
- HippoRAG2-style graph retrieval remains useful as inspiration for multi-hop memory retrieval.

Sources:

- [MemexRL arXiv](https://arxiv.org/abs/2603.04257)
- [LightMem arXiv](https://arxiv.org/abs/2510.18866)
- [LightMem GitHub](https://github.com/zjunlp/LightMem)
- [SwiftMem arXiv](https://arxiv.org/abs/2601.08160)

Difference from canon:

- The canon names MemexRL but does not fully spell out the exact-evidence archive pattern.

How this improves NexusNet:

- Long-running tasks should keep compact working summaries plus exact evidence pointers.
- VisualOps should show when the brain used summaries vs dereferenced exact source artifacts.
- This directly supports the one-million-token effective-context goal without pretending the raw prompt is one million tokens.

Recommended artifacts:

- `IndexedEvidenceRecord`
- `EvidencePointer`
- `ContextBudgetLedger`
- `DereferenceTrace`

## 2. Protocols, UI Events, And Observability

### MCP

Current public update:

- The MCP spec uses JSON Schema with 2020-12 support expectations and defines schema source-of-truth behavior.
- HTTP authorization guidance exists, but STDIO implementations remain especially sensitive because credentials are typically environment based.
- The spec warns consumers to sanitize rendered content such as icons.
- Public security research and recent coverage show MCP-like plugin/server ecosystems can create dangerous local execution and supply-chain risk.

Sources:

- [MCP specification](https://modelcontextprotocol.io/specification/2025-11-25/basic)
- [MCP production design paper](https://arxiv.org/abs/2603.13417)
- [Agent identity protocol paper](https://arxiv.org/abs/2603.24775)

Difference from canon:

- The canon already requires MCP to be disabled or held without security gates. Current evidence strengthens that decision.

How this improves NexusNet:

- MCP should be treated as a high-risk protocol adapter, not a convenience plugin layer.
- All MCP server registrations need signature/allowlist, identity metadata, schema validation, consent, sandbox profile, and audit.

Recommended status:

- `candidate_high_risk`.
- Default: disabled.
- Runtime: hold until explicit user approval.

### A2A

Current public update:

- A2A is positioned as an open standard for interoperability between independent, potentially opaque agent systems.

Source:

- [A2A protocol specification](https://a2a-protocol.org/dev/specification/)

Difference from canon:

- The canon treats A2A as a candidate protocol. Current docs confirm it is a coordination boundary, not a cognition layer.

How this improves NexusNet:

- A2A can express external delegation between NexusNet and outside agents.
- It should also fit internal AO-to-AO simulation, but only as an envelope. NexusBrain remains authority.

Recommended action:

- Add `delegation_identity`, `delegation_scope`, `delegation_expiry`, and `returned_artifact_hash` fields to the protocol adapter model.

### AG-UI

Current public update:

- AG-UI is an event-driven protocol for connecting agents to frontend applications and compatible clients.

Sources:

- [AG-UI docs](https://docs.ag-ui.com/)
- [AG-UI GitHub](https://github.com/ag-ui-protocol/ag-ui)

Difference from canon:

- The canon needs a browser-based visual companion. AG-UI is a stronger fit for the UI/event layer than for the brain layer.

How this improves NexusNet:

- Use AG-UI-style event streams for task progress, approvals, AO proposals, expert activity, live trace updates, and replay.
- Do not use AG-UI as the source of truth for brain decisions.

Recommended action:

- Prototype a read-only AG-UI-compatible event surface backed by NexusNet traces.

### OpenTelemetry GenAI And OpenInference

Current public update:

- OpenTelemetry GenAI semantic conventions cover events, exceptions, metrics, model spans, and agent spans.
- OpenInference provides AI observability semantic conventions and instrumentations over OpenTelemetry-compatible traces.

Sources:

- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [OpenInference spec](https://arize-ai.github.io/openinference/spec/)
- [OpenInference docs](https://arize-ai.github.io/openinference/)

Difference from canon:

- The canon requires trace-first evals and VisualOps. OTel/OpenInference give NexusNet a portable mapping layer.

How this improves NexusNet:

- VisualOps can expose standard spans while preserving NexusNet-specific fields:
  - `brain_path`
  - `ao_id`
  - `expert_id`
  - `memory_action`
  - `ebt_score`
  - `security_decision`
  - `promotion_gate`
  - `runtime_posture`

Recommended action:

- Create a telemetry normalization map from NexusNet traces to OTel/OpenInference attributes.

## 3. Harness Engineering And Self-Improvement

### Meta-Harness

Current public update:

- Meta-Harness treats the harness itself as the optimization target.
- It uses raw traces, scores, and source files from prior candidates to propose new harnesses.
- Raw traces matter; summaries lose critical signal.

Source:

- [Meta-Harness arXiv](https://arxiv.org/abs/2603.28052)

Difference from canon:

- The canon has autonomous self-improvement and recursive loops. Meta-Harness gives the strongest current evidence for trace-backed harness evolution.

How this improves NexusNet:

- NexusNet should store raw execution traces, failed attempts, evaluator notes, and exact artifacts for harness-improvement proposals.
- Summaries are useful for UI, but not enough for optimization.

Recommended gate:

- Harness changes can be proposed automatically but only promoted after:
  - held-out eval pass
  - regression trace comparison
  - security review
  - human or governed approval, depending on autonomy tier

### Natural-Language Agent Harnesses

Current public update:

- NLAH expresses harness behavior as executable natural language artifacts.
- It separates runtime policy, infrastructure, and task-specific harness logic.
- It emphasizes contracts, roles, stages, adapters, durable artifacts, and file-backed state.

Source:

- [Natural-Language Agent Harnesses arXiv](https://arxiv.org/abs/2603.25723)

Difference from canon:

- The canon has AO, expert, memory, and eval contracts, but this source pushes those contracts into portable executable artifacts.

How this improves NexusNet:

- AO workflows should become versioned harness cards:
  - purpose
  - role set
  - permitted tools
  - memory permissions
  - required artifacts
  - budgets
  - stop conditions
  - failure taxonomy

Recommended action:

- Add `HarnessSpec` and `HarnessRun` registry objects.

### AutoHarness, AgentFlow, And Narrow Attempt Loops

Current public update:

- AutoHarness and similar systems show that generated code harnesses and domain constraints can improve agents.
- Newer vulnerability-discovery harness work shows powerful results but also increases risk.

Sources:

- [AutoHarness arXiv](https://arxiv.org/abs/2603.03329)
- [AgentFlow arXiv](https://arxiv.org/abs/2604.20801)

Difference from canon:

- The canon wants recursive self-improvement, but these sources show the importance of gating the search space.

How this improves NexusNet:

- Self-improvement should narrow first:
  - retry with better context
  - use exact evidence
  - run targeted eval
  - escalate only when failure signals justify broader changes

Recommended action:

- Add attempt-loop state: `narrow_retry`, `evidence_dereference`, `scope_broadened`, `human_hold`, `promotion_blocked`.

## 4. Evals, Verifiers, And Computer-Use Reliability

### DeepEval

Current public update:

- DeepEval emphasizes pytest-native evals, trace grading, multi-turn metrics, multimodal support, and CI integration.

Source:

- [DeepEval](https://deepeval.com/)

Difference from canon:

- The canon requires trace-first evals. DeepEval shows a practical model for local unit-test-like agent evals.

How this improves NexusNet:

- NexusNet evals should run as normal tests where possible.
- Every eval should point to traces, route choices, memory operations, tool calls, and failure explanations.

Recommended action:

- Add optional DeepEval-compatible export, but keep NexusNet's own eval schema canonical.

### OpenAI Agent Evals

Current public update:

- OpenAI's docs emphasize traces, graders, datasets, and eval runs for improving agent workflows.

Source:

- [OpenAI agent evals](https://platform.openai.com/docs/guides/agent-evals)

Difference from canon:

- The canon already wants trace-first evals. This confirms the need to make eval datasets and graders first-class product artifacts.

How this improves NexusNet:

- VisualOps should show dataset name, grader, eval run, score, trace, and regression delta.

Recommended action:

- Add eval artifact fields: `dataset_id`, `grader_id`, `trace_ids`, `accepted_threshold`, `regression_delta`, `promotion_effect`.

### OSWorld-Verified

Current public update:

- OSWorld added verified benchmark improvements, fixed examples, AWS support, and updated results.
- It remains useful for computer-use benchmarking across real apps and OS environments.

Source:

- [OSWorld](https://os-world.github.io/)

Difference from canon:

- The canon lists OSWorld as a candidate. The verified update makes it a better CUA/GUI eval target than older OSWorld snapshots.

How this improves NexusNet:

- GUI/computer-use ability should be evaluated through reproducible task setup and execution-based verification, not screenshots alone.

Recommended action:

- Registry status: `candidate_eval_suite`.
- Add note: compare only against current verified benchmark version.

### Fara-7B And Universal Verifier

Current public update:

- Fara-7B is an open-weight computer-use model that acts from screenshots and coordinate actions.
- Microsoft's verifier work separates process and outcome rewards, distinguishes controllable and uncontrollable failures, and reduces false positives.

Sources:

- [Fara-7B arXiv](https://arxiv.org/abs/2511.19663)
- [Microsoft verifier article](https://www.microsoft.com/en-us/research/articles/the-art-of-building-verifiers-for-computer-use-agents/)
- [Universal Verifier arXiv](https://arxiv.org/abs/2604.06240)

Difference from canon:

- The canon lists FARA as a GUI candidate. The newer verifier work is more important than the model itself for NexusNet reliability.

How this improves NexusNet:

- Computer-use actions need a verifier artifact with:
  - user goal
  - intended action
  - screenshots
  - process score
  - outcome score
  - controllable/uncontrollable failure class
  - approval checkpoints

Recommended action:

- Add CUA verifier schema before adding any desktop-control model.

## 5. Training And Native Growth

### TRL v1.0

Current public update:

- Hugging Face released TRL v1.0 as a post-training library milestone with broad method coverage and stability goals.

Source:

- [TRL v1.0 blog](https://huggingface.co/blog/trl-v1)

Difference from canon:

- The canon already lists TRL v1. This confirms it is the best general-purpose first training backend candidate for supervised fine-tuning, preference optimization, and GRPO-style experiments.

How this improves NexusNet:

- Training jobs should export TRL-compatible datasets and reward specs, but not run automatically.

Recommended action:

- Keep `candidate_training_backend`.
- Require dataset manifest, license review, reward spec, eval report, and promotion gate.

### verl

Current public update:

- verl has moved to the `verl-project` organization and emphasizes modular RL dataflows, GRPO/PPO, integration with vLLM/SGLang, and flexible device mapping.

Source:

- [verl GitHub](https://github.com/verl-project/verl)

Difference from canon:

- The canon names verl. Current status makes it a stronger candidate for scalable RL training when NexusNet moves beyond local toy jobs.

How this improves NexusNet:

- Keep verl as a scaling backend for future multi-GPU or cluster training.

Recommended action:

- Do not promote until NexusNet has stable reward specs and trace-derived datasets.

### SkyRL

Current public update:

- SkyRL is documented as modular RL for real-world agentic workloads, including vLLM/SGLang backends and cloud orchestration through SkyPilot.

Source:

- [SkyRL docs](https://docs.skypilot.co/en/latest/examples/training/skyrl.html)

Difference from canon:

- The canon lists SkyRL. It is now clearly useful for cloud-scaled agentic training experiments, not local default training.

How this improves NexusNet:

- Mark as cloud-run candidate only.
- VisualOps should display cost, provider, GPU profile, and approval status.

Recommended action:

- Keep disabled by default. Require explicit training-run approval.

### OpenRLHF

Current public update:

- OpenRLHF 0.10 adds VLM and multi-turn VLM RL support according to the repo.

Source:

- [OpenRLHF GitHub](https://github.com/OpenRLHF/OpenRLHF)

Difference from canon:

- The roadmap already marks OpenRLHF as `candidate_requires_pin`. That remains correct because fast-moving README claims need pinned commit, license, and reproducibility review.

How this improves NexusNet:

- Useful later for multimodal reward training, but only after version pinning.

Recommended action:

- Keep `candidate_requires_pin`.

## 6. Runtime, Hardware, And Effective Context

### vLLM V1

Current public update:

- vLLM V1 uses a unified scheduler, functional prefix caching, chunked prefill, LoRA, FP8 KV cache, speculative decoding, and removes several V0 features.

Source:

- [vLLM V1 docs](https://docs.vllm.ai/en/latest/usage/v1_guide.html)

Difference from canon:

- The canon lists vLLM generally. The update means NexusNet runtime scorecards must distinguish vLLM V0 vs V1 and removed features.

How this improves NexusNet:

- Avoid showing unsupported vLLM features as available.
- Track exact engine generation and feature support.

Recommended action:

- Add `runtime_family`, `runtime_version`, `engine_generation`, `supported_features`, and `removed_features`.

### SGLang

Current public update:

- SGLang supports production metrics, production tracing, prefill/decode optimizations, multimodal serving, structured outputs, quantization, and post-training integration.

Source:

- [SGLang docs](https://sgl-project.github.io/)

Difference from canon:

- The canon lists SGLang. The newer docs make it a runtime and training-rollout backbone candidate, not just a serving candidate.

How this improves NexusNet:

- Compare SGLang against vLLM per task: latency, throughput, structured output reliability, model support, tracing, and hardware support.

Recommended action:

- Add SGLang to runtime scorecard with tracing/metrics columns.

### LMCache

Current public update:

- LMCache stores reusable KV caches so repeated text does not need repeated prefill. Its docs claim significant TTFT and GPU cycle savings with vLLM in common multi-round/RAG workloads.

Source:

- [LMCache docs](https://docs.lmcache.ai/)

Difference from canon:

- The canon names LMCache-style reuse. The update makes it a concrete effective-context candidate.

How this improves NexusNet:

- Repeated system canon, expert capsule context, AO contracts, and project summaries can be cache candidates.

Recommended action:

- Add `cache_candidate`, `cache_reuse_reason`, `cache_hit_rate`, and `cache_invalidated_by` to runtime traces.

### torchao

Current public update:

- torchao supports quantization, sparsity, optimizer quantization, float8 training, and KV cache quantization. Transformers now requires object-based configs rather than older string APIs for torchao integration.

Source:

- [torchao Transformers docs](https://huggingface.co/docs/transformers/en/quantization/torchao)

Difference from canon:

- The canon lists torchao. The update means NexusNet runtime recipes must not rely on stale string config examples.

How this improves NexusNet:

- Hardware-aware quantization plans can be explicit and modern.

Recommended action:

- Add version-sensitive recipe validation to runtime scorecards.

### TriAttention And CASK

Current public update:

- TriAttention has a 2026 arXiv paper for KV compression in long reasoning.
- CASK appears as a newer April 2026 research candidate claiming better fidelity under some reasoning gates.

Sources:

- [TriAttention arXiv](https://arxiv.org/abs/2604.04921)
- [CASK arXiv](https://arxiv.org/abs/2604.10900)

Difference from canon:

- TriAttention remains research-only. CASK should be added as a research-only comparator.

How this improves NexusNet:

- Long-context roadmap should include KV-compression research watchlist, not product claims.

Recommended action:

- Add `CASK` to research candidates with `research_only` status.

## 7. Multimodal, Edge, And Computer-Use Models

### Qwen3-VL

Current public update:

- Qwen3-VL is documented in Transformers and includes dense/MoE, Instruct/Thinking variants, improved visual understanding, video time alignment, and strong multimodal reasoning.

Sources:

- [Qwen3-VL Transformers docs](https://huggingface.co/docs/transformers/main/en/model_doc/qwen3_vl)
- [Qwen3-VL technical report](https://arxiv.org/abs/2511.21631)

Difference from canon:

- The canon lists Qwen3-VL. It remains a strong multimodal candidate, especially for vision-heavy expert lanes and CUA verification.

How this improves NexusNet:

- Use as candidate for Vision Expert, UI screenshot understanding, document/image ingestion, and multimodal evals.

Recommended action:

- Candidate only. Add model license and runtime feasibility checks.

### LFM2.5

Current public update:

- LFM2.5-VL-1.6B has Hugging Face model cards for vision-language use, local/browser demos, GGUF, ONNX, and MLX deployment variants.
- LFM2.5-350M shows strong edge deployment focus across Qualcomm, Intel/OpenVINO, Apple Silicon, local engines, and constrained devices.

Sources:

- [LFM2.5-VL-1.6B Hugging Face](https://huggingface.co/LiquidAI/LFM2.5-VL-1.6B)
- [LFM2.5-350M Liquid AI blog](https://www.liquid.ai/blog/lfm2-5-350m-no-size-left-behind)

Difference from canon:

- The canon had LFM2.5 as an edge lane. Current source confirms it is a strong local-first runtime candidate for low-cost always-on assistant/expert work.

How this improves NexusNet:

- Use small local models for low-risk classification, routing prechecks, dashboard summaries, local transcript tagging, and offline status explanations.

Recommended action:

- Add edge model scorecards for memory, latency, quantized format, hardware target, and license.

### DeepEyesV2

Current public update:

- DeepEyesV2 is an agentic multimodal model research paper focused on data construction, training, and evaluation.

Source:

- [DeepEyesV2 arXiv](https://arxiv.org/abs/2511.05271)

Difference from canon:

- The canon lists DeepEyesV2 as a GUI/computer-use candidate. It remains research-only unless weights, license, and reproducible evals are verified.

How this improves NexusNet:

- Useful as design inspiration for multimodal agent evaluation, not immediate runtime.

Recommended action:

- Keep `research_only`.

## 8. Product Surface And VisualOps Control Center

Current public update:

- The best "mission control" pattern is observability-first: live sessions, task queue, schedules, approvals, token/cost metrics, cache hit rate, tool latency, error rates, skill usage, MCP status, context health, and recent sessions.
- Current standards suggest the UI should be backed by traces and event streams, not only custom logs.

Sources:

- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [OpenInference spec](https://arize-ai.github.io/openinference/spec/)
- [AG-UI docs](https://docs.ag-ui.com/)

Difference from canon:

- The canon already names 15 VisualOps panels. The update is that each panel should be trace/registry-backed and exportable to standard observability formats.

How this improves NexusNet:

- The browser-based visual companion should auto-update from:
  - brain traces
  - AO/expert activity
  - Memory OS events
  - protocol security decisions
  - eval runs
  - runtime scorecards
  - training gates
  - research registry changes

Recommended initial panel set:

1. Canon Status
2. Brain Path Trace
3. AO Hive
4. Expert Roster
5. HiveMind Graph
6. Memory OS
7. EBT Routing
8. Protocol Security
9. Task Queue And Approvals
10. Runtime And Hardware
11. Token/Cost/Cache
12. Tool And MCP Latency
13. Eval Health
14. Training And Promotion Gates
15. Research Assimilation Registry
16. Packaging And Product Readiness

## 9. Security Delta

The biggest negative update is agent ecosystem risk.

Current public update:

- Broad local-access agents and extension ecosystems have produced real safety concerns: exposed control panels, malicious extensions, broad filesystem/service access, and prompt-injection-assisted exfiltration.
- OpenClaw-style patterns remain useful as operator/runtime inspiration, but broad autonomous local execution is not safe as a default.

Sources:

- [OpenClaw safety analysis arXiv](https://arxiv.org/abs/2604.04759)
- [TechRadar OpenClaw exposure coverage](https://www.techradar.com/pro/security/the-math-is-simple-openclaw-trojan-horse-ai-agents-give-hackers-full-control-of-28-000-systems)
- [TechRadar extension risk coverage](https://www.techradar.com/pro/shadow-ai-and-agents-like-openclaw-are-hijacking-corporate-data-too-easily)

Difference from canon:

- The canon already rejects silent external execution. Current evidence says this is not just caution; it is a product safety requirement.

How this improves NexusNet:

- Every external tool, protocol server, skill, package, and generated action must be:
  - signed or allowlisted
  - scoped
  - sandboxed
  - consent-gated
  - audited
  - revocable
  - visible in VisualOps

Recommended action:

- Add plugin/tool risk score to the Protocol Security panel and Assimilation Registry.

## 10. Recommended Assimilation Registry Updates

| Candidate | Updated status | Reason |
|---|---|---|
| Graphiti/Zep | `prototype_next` | Strong temporal graph memory fit; do not outsource core memory authority. |
| Graphify | `prototype_next_local_only` | Strong local graph compiler/reference; avoid dependency lock-in and API cost surprise. |
| Karpathy LLM Wiki | `design_pattern` | Good human-readable HiveMind companion, not enough alone for governed memory. |
| MemOS | `candidate_memory_architecture` | Strong Memory OS vocabulary and lifecycle model. |
| A-MEM | `candidate_memory_linking` | Useful for expert/AO mini-graph evolution. |
| AgeMem | `candidate_memory_policy_learning` | Useful for future learned memory operations. |
| MemexRL | `candidate_indexed_evidence` | High-value pattern for long-horizon exact evidence. |
| LightMem | `research_candidate_efficiency` | Add as memory efficiency comparator. |
| SwiftMem | `research_candidate_efficiency` | Add as query-aware memory indexing comparator. |
| HippoRAG2 | `research_reference` | Multi-hop graph retrieval inspiration only. |
| MCP | `candidate_high_risk_disabled` | Needs strict identity, schema, sandbox, consent, audit. |
| A2A | `candidate_delegation_envelope` | Useful for external delegation, not authority. |
| AG-UI | `candidate_visual_event_protocol` | Strong fit for browser visual companion events. |
| OpenTelemetry GenAI | `candidate_observability_mapping` | Standard span/event/metric vocabulary. |
| OpenInference | `candidate_observability_mapping` | AI-specific trace conventions and instrumentations. |
| Meta-Harness | `research_to_prototype_shadow` | Useful for self-improving harnesses; must use held-out evals. |
| NLAH | `candidate_harness_spec` | Good AO/workflow contract representation. |
| DeepEval | `candidate_eval_export` | Useful CI/eval runner, but NexusNet eval schema remains canonical. |
| OpenAI agent evals | `reference_eval_pattern` | Confirms traces, graders, datasets, eval runs. |
| OSWorld-Verified | `candidate_cua_eval_suite` | Better GUI/computer-use eval reference. |
| Fara-7B | `candidate_cua_model` | Guarded computer-use model; no autonomous control. |
| Universal Verifier | `candidate_cua_verifier` | Stronger than model-only GUI adoption. |
| TRL v1 | `candidate_training_backend` | Best first post-training backend candidate. |
| verl | `candidate_scaling_backend` | Scalable RL candidate after reward/eval maturity. |
| SkyRL | `candidate_cloud_training_backend` | Useful for cloud jobs only with explicit approval. |
| OpenRLHF | `candidate_requires_pin` | Keep pinned/reproducibility gate. |
| vLLM V1 | `candidate_runtime_profile` | Needs version-aware feature matrix. |
| SGLang | `candidate_runtime_profile` | Add tracing/metrics/post-training columns. |
| LMCache | `candidate_kv_cache` | Strong effective-context support. |
| torchao | `candidate_quantization` | Use current object config APIs. |
| TriAttention | `research_only` | Not product-ready. |
| CASK | `research_only` | Add as KV compression watchlist comparator. |
| Qwen3-VL | `candidate_multimodal` | Strong vision/video/doc candidate. |
| LFM2.5 | `candidate_edge_model` | Strong local-first/edge model lane. |
| DeepEyesV2 | `research_only` | Interesting agentic multimodal research. |
| OpenJarvis | `operator_runtime_reference` | Local-first product inspiration; not brain replacement. |
| OpenClaw patterns | `risk_reference_bounded` | Use as cautionary/security reference more than adoption target. |

## NexusNet Implementation Priorities From This Refresh

### Priority 1: HiveMind Graph Upgrade

Build the knowledge graph version of the HiveMind:

- Main HiveMind graph.
- AO subgraphs.
- Expert capsule subgraphs.
- Temporal fact records.
- Conflict/disagreement records.
- Source/evidence dereference.
- Memory lifecycle state.
- Roll-up rules from mini-graphs to main graph.

Impact:

- Turns the user-requested "knowledge graph hivemind" into a concrete architecture.
- Makes each AO/expert a real mini-brain without violating NexusBrain authority.

### Priority 2: Memory Action Trace Schema

Add explicit memory operation events:

- `store`
- `retrieve`
- `update`
- `summarize`
- `archive`
- `discard`
- `dereference`
- `provenance_lookup`
- `conflict_record`
- `rollup_proposal`

Impact:

- Enables evals for memory behavior.
- Prepares for AgeMem/MemexRL-style learned memory policy later.

### Priority 3: VisualOps Observability Backbone

Map NexusNet traces to a stable observability model:

- Native NexusNet trace schema remains canonical.
- Add OTel/OpenInference export mapping.
- Use AG-UI-style streams for browser visual companion updates.

Impact:

- Control center becomes live, truthful, and inspectable.
- Users can see connections, activities, costs, errors, cache, memory, AOs, experts, and gates.

### Priority 4: Protocol Security Upgrade

Harden MCP/A2A/AG-UI adapters:

- Identity.
- Signature/allowlist.
- Consent.
- Sandbox.
- Permission scope.
- Schema validation.
- Output sanitization.
- Audit.
- Revocation.

Impact:

- Makes NexusNet safer than fast-moving agent ecosystems that expose local systems by default.

### Priority 5: Runtime Scorecards

Add current runtime support fields:

- vLLM V0/V1 distinction.
- SGLang metrics/tracing support.
- LMCache KV reuse candidate status.
- torchao config compatibility.
- Edge model formats: GGUF, ONNX, MLX, WebGPU, OpenVINO, NPU.
- Effective-context budget and cache hit/miss.

Impact:

- Prevents false claims that unsupported runtimes are runnable.
- Supports local-first and hardware-aware adaptation.

### Priority 6: Harness Self-Improvement Gate

Create a shadow-only harness improvement loop:

- Collect raw failed traces.
- Propose harness spec diffs.
- Run held-out evals.
- Compare regression traces.
- Record security review.
- Promote only through gatekeeper.

Impact:

- Makes the autonomous self-improvement idea real without allowing silent self-mutation.

## What Should Not Change

- NexusBrain remains authority.
- AOs and experts propose/coordinate; they do not silently mutate production memory or promote models.
- External tools and protocols remain mediated capabilities.
- Cloud remains a capability tier, not the default replacement for local-first behavior.
- Training, deployment, PR creation/merge, provider registration, hooks, and autonomous external execution remain gated.
- Research candidates do not become locked canon by being popular or newly updated.

## Open Research Gaps

1. Exact EBT scoring weights remain unresolved.
2. Mini-HiveMind graph merge policy needs design: when does an expert-local belief become shared HiveMind knowledge?
3. Memory decay/archive policy needs explicit metrics.
4. Learned memory policy should wait until memory actions are traced and evaluated.
5. CUA/computer-use adoption should start with verifier schema before model integration.
6. OTel/OpenInference mapping needs local schema work.
7. Runtime scorecards need local hardware tests before any "ready" status.
8. CASK and TriAttention need reproducible local evidence before promotion.
9. OpenRLHF needs pinned commit/version/license review before use.
10. Any Graphify-style compiler must be local-first and produce governed artifacts, not become a hidden autonomous source of truth.

## Final Recommendation

The best updated version of the NexusNet canon is not a pivot away from the existing plan. It is a stricter, more inspectable version:

- NexusNet remains the brain.
- The HiveMind becomes a temporal knowledge graph.
- AOs and experts each gain governed mini-graphs.
- Memory operations become traceable tool actions.
- Effective context is built from graph memory, indexed evidence, summaries, and KV/cache reuse.
- VisualOps becomes an observability-first browser companion.
- Harness self-improvement runs in shadow until evals and gates prove it.
- Protocols, training, and computer-use remain gated by security, consent, provenance, and promotion evidence.

