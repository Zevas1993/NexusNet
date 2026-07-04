# Assimilation Target Detailed Rulings - 2026-07-04

Status: documentation-only target-level review
Branch: `codex/all-worktrees-integration`
Primary source: `docs/assimilation/ASSIMILATION_TARGET_CLUSTER_REVIEW_2026-07-04.md`
Raw corpus source: `docs/assimilation/NEXUSNET_ALL_ASSIMILATION_TARGETS_CONSOLIDATED_2026-05-31.md`

## Boundary

This file expands the cluster-level assimilation review into target-level rulings for the named target families currently in the review. It does not promote any external source into production, import third-party code, prove current source health, or waive license, security, privacy, eval, rollback, or governance gates.

The 195-source consolidated corpus remains the raw review queue. This file covers the named target families and major representative targets, not every line of the consolidated source register.

## Universal Rule

NexusNet is the mother brain. Every external target is a pattern source, adapter candidate, eval fixture, teacher candidate, runtime reference, UX reference, or research prompt. No target becomes the brain, final control plane, sole source of truth, or automatic production dependency.

`NexusGraph Intelligence Fabric` spans everything NexusNet is permitted to perceive, connect to, learn from, reason over, govern, or mutate. Any category list is illustrative, not limiting.

## Statuses

| Status | Meaning |
| --- | --- |
| `native_pattern` | Preserve the idea as a NexusNet-native implementation pattern. |
| `adapter_candidate` | May become an optional adapter after source, license, security, eval, and policy review. |
| `teacher_candidate` | May produce teaching/eval signals only after rights, domain, and benchmark review. |
| `eval_candidate` | Useful as benchmark or evidence pattern, not product proof by itself. |
| `blocked_direct_dependency` | Do not depend on or import directly without a later explicit approval. |
| `research_only` | Preserve for future study; no production or active-route claims. |
| `locked_clarification` | Canonical interpretation of how to treat a recurring target. |

## Cluster 1: Workflow Builders And Node UI

Native output: `NexusNet Workflow Graph Studio`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| n8n | Node/workflow UI, triggers, schedules, run history, credential UX, workflow learning signals. | n8n as dependency, runtime, control plane, or credential owner. | `native_pattern` |
| Flowise | LLM graph prototyping, chain/agent visual assembly, quick experiment ergonomics. | Unsandboxed graph nodes, external prompt state as authority, graph success as proof. | `native_pattern` |
| Langflow | Typed component graph UX, reusable components, visual/code mixed authoring. | Direct runtime lock-in or opaque component execution. | `native_pattern` |
| Dify | App/workflow packaging, dataset/app release concepts, user-facing workflow products. | SaaS app plane as NexusNet brain or knowledge owner. | `native_pattern` |
| Node-RED | Event-flow semantics, triggers, subflows, device/event routing patterns. | Ambient device/network writes or unmanaged external automation. | `native_pattern` |
| Activepieces | Connector catalog UX, automation templates, user-friendly trigger/action patterns. | Unsourced connector trust, broad token grants, SaaS dependency. | `adapter_candidate` |
| Windmill | Script/job workflow discipline, scheduling, typed parameters, run history. | Untrusted code execution without sandbox and approval. | `adapter_candidate` |
| Kestra | Durable orchestration, retries, backfills, declarative workflow discipline. | Hidden scheduler state as source of truth. | `native_pattern` |
| Airflow | DAG discipline, task dependency management, backfill/retry concepts. | Airflow as root orchestrator or production brain. | `native_pattern` |
| Huginn | User-owned event agents, web monitors, trigger/action thinking. | Scraping or credential automation without policy and consent. | `research_only` |
| ComfyUI-style graphs | Visual media/model pipeline ergonomics, node layout lessons. | Treating media graph UX as the universal brain architecture. | `native_pattern` |

## Cluster 2: Skills, Recipes, MCP, And Protocol Tooling

Native output: `NexusNet SkillOps And Protocol Fabric`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| Agent Skills standard | Portable skill folders, progressive disclosure, scripts/assets/references/evals layout. | Mega-skills, hidden unrelated capabilities, context stuffing. | `native_pattern` |
| Gemini CLI skills | Skill discovery and local instruction packaging patterns. | Vendor-specific skill semantics as final NexusNet contract. | `native_pattern` |
| Goose recipes | Repeatable runbooks, recipe execution, operator handoff patterns. | Recipe execution without receipts, approvals, or rollback state. | `native_pattern` |
| OpenClaw | Local-first skills, approval-aware execution, explicit packaged behavior. | Stronger claims from stale OpenClaw URLs until current primary docs are pinned. | `research_only` |
| Hermes/NemoClaw style loops | Trace-to-skill proposals, memory loops, self-evolving runtime ideas. | Automatic skill/memory promotion from traces. | `native_pattern` |
| MCP | Resources, prompts, tools, roots, sampling as protocol primitives. | MCP as authority, token passthrough, silent commands, trust propagation. | `adapter_candidate` |
| Composio/Pipedream-style catalogs | Connector discovery, scoped connector metadata, app integration patterns. | Broad connector dependency or unreviewed third-party action execution. | `adapter_candidate` |
| Skill marketplaces | Discovery of reusable capability ideas and domain coverage gaps. | Installing marketplace skills into active NexusNet without source/license/sandbox/eval review. | `research_only` |

## Cluster 3: Agent Frameworks And Coding Agents

Native output: `Hive Agent Workbench`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| LangGraph | Stateful graph execution, durable task state, explicit edges. | Framework replacing NexusBrain authority. | `native_pattern` |
| Microsoft Agent Framework/AutoGen lineage | Multi-agent role patterns and group coordination. | Autonomous teams making production mutations without gates. | `native_pattern` |
| CrewAI | Role-based agent composition and task assignment. | Static role cosplay without evidence, policy, or replay. | `research_only` |
| OpenHands | Coding workspace automation, sandboxed dev loops, task replay ideas. | Direct code merge or secret/dependency access without approval. | `adapter_candidate` |
| Aider | Patch-focused coding workflow, repo-grounded code edits. | Direct edit authority without GitNexus impact and tests. | `adapter_candidate` |
| Continue | IDE assistance, local model/code context ergonomics. | IDE agent as hidden source of truth. | `adapter_candidate` |
| Cline/Roo-style agents | IDE task automation, tool approval UX, step receipts. | Unbounded desktop/shell authority. | `adapter_candidate` |
| Goose coding/operator flows | Operator workflows, recipes, subagents, and local automation ergonomics. | Goose as NexusNet control plane. | `native_pattern` |
| Gemini CLI/Qwen-code style terminals | Terminal agent command UX and coding assistant patterns. | Vendor/tool terminal as final orchestrator. | `research_only` |
| Tabby-style assistants | Local code assistant and codebase-aware autocomplete patterns. | Local code model replacing repo proof, impact analysis, or tests. | `adapter_candidate` |

## Cluster 4: Runtime, Model Harnesses, And Edge Execution

Native output: `NexusNet Runtime Ladder And Model Passport Registry`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| `llama.cpp` | Core GGUF/local inference engine path, CPU/GPU/edge quantized execution. | Treating one engine as universal runtime. | `adapter_candidate` |
| Ollama | Simple provider UX, tool-calling harness lessons, user-friendly local model serving. | Ollama-only inference strategy or dependency lock-in. | `adapter_candidate` |
| vLLM | High-throughput serving, paged attention, speculative/runtime acceleration paths. | Assuming server GPU path fits edge/mobile. | `adapter_candidate` |
| SGLang | Structured generation/server orchestration for high-throughput tasks. | Runtime lock-in or untested structured output claims. | `adapter_candidate` |
| TensorRT-LLM | NVIDIA acceleration path where hardware and license fit. | Making NVIDIA stack mandatory. | `adapter_candidate` |
| MLC-LLM | Cross-device packaging, WebGPU/mobile/native deployment lessons. | Untested mobile runtime promotion. | `adapter_candidate` |
| mistral.rs | Rust inference runtime pattern, local serving and quant support lessons. | Runtime import without maintenance/security review. | `adapter_candidate` |
| LocalAI | OpenAI-compatible local endpoint and admin UX patterns. | UI/server wrapper as brain. | `adapter_candidate` |
| Open WebUI | Local model catalog and admin interaction UX. | Product shell hiding readiness gaps. | `native_pattern` |
| LM Studio | Local model browsing/loading UX and OpenAI-compatible endpoint lessons. | Desktop app as internal engine. | `native_pattern` |
| PocketPal | Mobile local-model loading, quant choice, offline UX, device constraints. | Companion app as independent brain owner. | `native_pattern` |
| ONNX Runtime GenAI, MediaPipe, TFLite, ncnn | Edge/mobile packaging routes and hardware-specific deployment options. | Promoting without device benchmarks, thermal/memory limits, and rollback. | `adapter_candidate` |

## Cluster 5: Knowledge, Retrieval, And Memory

Native output: `NexusNet Knowledge Forge`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| Pinecone Nexus/KAC pattern | Compiled knowledge artifacts, context compiler, typed cited task artifacts. | Pinecone as vendor-owned memory layer or brain. | `native_pattern` |
| Pinecone Assistant | Document QA UX, upload-grounded question flows. | Hosted assistant as NexusNet knowledge authority. | `native_pattern` |
| LlamaIndex | Loader/retriever/query-engine patterns and index abstractions. | Framework-owned memory truth. | `adapter_candidate` |
| LangChain retrieval | Retriever composition, tool/document integration patterns. | Broad framework dependency as core memory layer. | `adapter_candidate` |
| Microsoft GraphRAG | Graph extraction, community summaries, relationship-grounded retrieval. | Uncited graph summaries as trusted facts. | `native_pattern` |
| Neo4j | Property graph modeling and graph query lessons. | A graph database as final mother brain. | `adapter_candidate` |
| Qdrant, Weaviate, Chroma, pgvector, FAISS | Vector abstraction, local/cloud index options, hybrid search candidates. | Single vector DB lock-in or raw vector answers as knowledge. | `adapter_candidate` |
| Semantic caches, provenance crates, evidence DAGs | Freshness-aware reuse, source lineage, content-addressed evidence. | Cached synthesis without source state, privacy, and policy match. | `native_pattern` |

## Cluster 6: Evaluation, Observability, And Evidence

Native output: `EvalsAO Evidence Spine`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| Inspect AI | Eval runner patterns, task definitions, model/tool evaluation discipline. | Eval runner as authority without domain gates. | `adapter_candidate` |
| EleutherAI lm-evaluation-harness | Standard model benchmark execution and result normalization. | Leaderboard score as promotion proof. | `adapter_candidate` |
| DeepEval | Unit-style LLM eval ergonomics and regression checks. | Opaque judge-only acceptance. | `adapter_candidate` |
| promptfoo | Prompt/model regression matrix and provider comparison UX. | Prompt-only testing as production proof. | `adapter_candidate` |
| OpenAI eval-style graders | Grader patterns and rubric-based evaluation. | Closed or unclear-rights grader outputs used for training without review. | `native_pattern` |
| Langfuse | Trace, prompt, dataset, and score lineage patterns. | Monitoring product as second control plane. | `adapter_candidate` |
| Arize Phoenix | Tracing, observability, eval dashboard lessons. | Observability replacing replayable NexusNet evidence. | `adapter_candidate` |
| OpenTelemetry GenAI | Exportable spans/metrics/events for model, tool, retrieval, and agent steps. | Losing NexusNet-specific context in generic telemetry. | `native_pattern` |
| Agent/task benchmarks | Browser, OS, coding, tool-use, research, customer, data, and professional fault benchmarks as eval packs. | Benchmark success as general readiness without local task proof. | `eval_candidate` |

## Cluster 7: Security, Authority, Isolation, And Supply Chain

Native output: `Authority And Isolation Fabric`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| OWASP LLM Top 10 | Threat categories for prompt injection, excessive agency, disclosure, supply chain, and model risk. | Checklist compliance as sufficient security. | `native_pattern` |
| MCP security guidance | Consent, audience validation, redirect validation, scope minimization, SSRF defenses. | Token passthrough, ambiguous tool identity, silent execution. | `native_pattern` |
| Semgrep | Static code scanning and policy checks. | Scan-only security signoff. | `adapter_candidate` |
| Trivy | Dependency/container/IaC scanning patterns. | Scanner output as sole supply-chain proof. | `adapter_candidate` |
| Grype, Snyk, OSSF Scorecard | Vulnerability and repository health signals. | Vendor score as promotion authority. | `adapter_candidate` |
| Sigstore, SLSA, SCITT | Signing, provenance, receipt, and supply-chain attestation patterns. | Unsigned or unverifiable release claims. | `native_pattern` |
| Biscuit, object capabilities, datalog tokens | Attenuated delegated authority and policy-checkable capabilities. | Broad ambient credentials. | `native_pattern` |
| WASM, Landlock/seccomp, hardened JS compartments | Tool sandbox tiers and constrained execution envelopes. | Unsandboxed arbitrary command execution from untrusted graph nodes. | `adapter_candidate` |

## Cluster 8: Self-Improvement, Recursive Dreaming, And World Models

Native output: `Recursive Dreaming And Imagination Foundry`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| Recursive Neural Dreaming | High-temperature hypothesis generation and unusual solution search. | Dreams as evidence or direct active mutation. | `native_pattern` |
| DreamerV3/world models | Latent rollout, planning, failure prediction, simulated rehearsal. | World model as truth oracle. | `research_only` |
| PAN-style long-horizon simulation | Long-horizon planning stress tests and imagined consequence chains. | Planning simulation bypassing policy. | `research_only` |
| AlphaEvolve-style verifier search | Proposal generation with verifier-scored search. | Verifier score as automatic promotion. | `native_pattern` |
| Darwin-Godel-machine lineage | Self-improvement proposal archive and lineage tracking. | Uncontained recursive self-modification. | `research_only` |
| GFlowNet diverse thought factory | Diverse candidate generation and non-myopic exploration. | Random novelty as improvement. | `research_only` |
| Causal intervention cortex | Sandboxed causal experiments and counterfactual tests. | Causal claim without experimental evidence. | `native_pattern` |
| Active inference/homeostasis | Resource, uncertainty, contradiction, and stability control loops. | Autonomy drift without operator goals. | `native_pattern` |
| Hippocampal replay/consolidation | Offline trace replay into memories, curricula, eval fixtures, and skill proposals. | Raw trace promotion or private data leakage. | `native_pattern` |
| Developmental/open-ended AI embryo | Staged growth, genome-like configs, viability constraints. | Unbounded growth without containment and eval. | `research_only` |
| Whole-brain/organoid/bioelectric inspiration | Boundary language and computational-only analogies. | Consciousness, wetlab, or biological product claims. | `research_only` |

## Cluster 9: Teacher Council And Expert Expansion

Native output: `Teacher Council And Expert Birth Registry`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| Leanstral 1.5 | Formal methods, Lean 4 proof repair, theorem decomposition, proof-driven contracts. | General god-teacher role or unreviewed distillation. | `teacher_candidate` |
| Nemotron/NVIDIA multimodal teachers | Optional multimodal perception/reasoning evidence packets. | Replacement brain or production inference without license/hardware/privacy gates. | `teacher_candidate` |
| Keye-VL/video-temporal teachers | Long-video, temporal perception, multimodal localization curriculum. | Video teacher as uncited truth source. | `teacher_candidate` |
| LFM/Liquid compact models | Efficient compact multimodal/local teacher or worker candidates. | License/provenance-gated models as active teachers without review. | `teacher_candidate` |
| MiniCPM/edge workers | Local/edge assistant and constrained teacher roles. | Edge worker as mother brain. | `teacher_candidate` |
| Qwen, DeepSeek, Kimi, Mistral, Devstral-style models | Domain/open-or-license-eligible teacher panels and model-route candidates. | Closed/unclear-rights outputs for distillation. | `teacher_candidate` |
| Medical models/benchmarks | Evidence-gated clinical reasoning curriculum and safety evals. | Autonomous diagnosis or care authority. | `teacher_candidate` |
| Finance/quant/crypto tools and models | Risk, simulation, accounting, market, and quant research curriculum. | Autonomous trading or financial advice authority. | `teacher_candidate` |
| Quantum research/code benchmarks | Qiskit/circuit/code reasoning and quantum research evals. | Hardware truth or physics oracle claims. | `teacher_candidate` |

## Cluster 10: Domain Expert Packs

Native output: `Expert Pack Radar And Domain Curriculum Forge`

| Target domain | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| Medicine and clinical reasoning | Evidence hierarchy, contraindications, escalation, clinical evals. | Diagnosis/treatment authority without licensed human review. | `native_pattern` |
| Holistic medicine and wellness | Wellness research lane, interaction/risk warnings, source grading. | Medical authority, unsupported claims, supplement/drug interaction blindness. | `native_pattern` |
| Finance, quant, macro, accounting, taxes, crypto | Market/data/risk simulations, tax/accounting references, crypto risk models. | Autonomous trading, tax filing, or investment directives. | `native_pattern` |
| Law, policy, compliance, patents, contracts | Legal research and contract/policy analysis with jurisdiction labels. | Legal filing or legal advice without human/legal review. | `native_pattern` |
| Cybersecurity | Red/blue/supply-chain labs, malware analysis under containment, defensive evals. | Exploit execution without scoped permission and sandbox. | `native_pattern` |
| Math, formal methods, theorem proving | Proof, verification, specs, theorem decomposition. | Proof-looking text as proof. | `native_pattern` |
| Quantum, physics, chemistry, biology, neuroscience, materials | Research assistants, simulation/coding evals, lab-safety boundaries. | Wetlab or physical-world claims without controls. | `native_pattern` |
| Robotics, controls, embedded, IoT | Simulation-first control, edge-device constraints, hardware safety. | Real actuator/device mutation without digital twin and approval. | `native_pattern` |
| Education, psychology, communications, design, writing, media | Teaching, coaching, rhetoric, UX, creative review, media workflows. | Therapeutic/clinical authority or manipulative persuasion. | `native_pattern` |
| Business ops, CRM, HR, sales, marketing, logistics, procurement | Workflow automation, decision support, process analysis. | Unapproved external commitments, hiring/firing/procurement actions. | `native_pattern` |
| Local device, mobile, accessibility, privacy, offline-first | Device-aware UX, local model fit, accessibility profiles, privacy modes. | Private trace sharing or companion-device independence from mother brain. | `native_pattern` |

## Cluster 11: UI, Visualizer, Companion, And Product Shell

Native output: `NexusNet Control Panel And Companion`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| Static diagrams | Patent figures, docs, onboarding, fallback exports. | Static image as live product UI. | `native_pattern` |
| Interactive Three.js/control-panel visualizer | Live hive graph, replay, runtime state, expert/teacher/skill controls. | Visual-only proof of implementation. | `native_pattern` |
| PocketPal | Mobile local-model loading, offline UX, companion constraints. | Companion as independent brain. | `native_pattern` |
| Open WebUI | Model catalog, local admin, conversation UX references. | WebUI as brain or route authority. | `native_pattern` |
| LocalAI WebUI | Local endpoint/admin ergonomics. | Runtime wrapper hiding model/passport truth. | `native_pattern` |
| Dify/Langflow/Flowise UX | Workflow/app graph ergonomics and packaging ideas. | External product shell as final UI. | `native_pattern` |
| OpenJarvis productization | First-run init, doctor, preset bundles, local-first recommendations. | Product shell that masks readiness gaps. | `native_pattern` |

## Cluster 12: Productization, Ops, And Worktree Governance

Native output: `NexusNet Operational Spine`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| OpenJarvis ops patterns | First-run diagnostics, doctor reports, presets, scheduled monitors. | Wrapper product as system owner. | `native_pattern` |
| Goose operator/runtime patterns | Recipes, local automation, bounded subagents, operator workflows. | Goose as permanent control plane. | `native_pattern` |
| Sandcastle/worktree-per-agent | Isolated workspaces, AFK sandbox agent factories, reproducible receipts. | Dirty work becoming baseline or hidden side effects. | `native_pattern` |
| GitNexus codegraph gate | Code navigation, impact analysis, stale-index checks, detect-changes. | GitNexus as final mother brain. | `locked_clarification` |
| Feature flags | Staged rollout of prompts, skills, routers, policies, models, UI. | Rollout without monitor and rollback. | `native_pattern` |
| Reversible patch transaction logs | Apply/rollback receipts and state mutation audit. | Irreversible mutation without preview and rollback proof. | `native_pattern` |
| Deterministic replay snapshots | Incident replay, eval reproduction, trace audit. | Replay as active mutation path. | `native_pattern` |

## Cluster 13: Mother Brain Graph Intelligence

Native output: `NexusGraph Intelligence Fabric`

| Target | Assimilate | Reject or block | Status |
| --- | --- | --- | --- |
| GitNexus | Reference for graph indexing, query, impact, stale-index, detect-change discipline. | GitNexus as sole graph memory or mother brain. | `locked_clarification` |
| NexusNet `CodegraphGate` | Manifest gate pattern for requiring graph evidence before high-risk changes. | Gate-only implementation mistaken for universal graph intelligence. | `native_pattern` |
| Knowledge graphs and GraphRAG | Relationship modeling, source-grounded graph query, contradiction paths. | Graph DB or graph summary as trusted truth without evidence. | `native_pattern` |
| Workflow/skill/model/runtime/policy/eval graphs | Unified connected-state view of all internal artifacts and permissioned external surfaces. | Siloed graphs with no mother-brain visibility. | `native_pattern` |
| Replay/pathway ledgers | Read-only graph replay, affected-neighborhood view, promotion readiness. | Replay leaking raw private content or mutating runtime. | `native_pattern` |
| Universal permitted connected state | Everything NexusNet can perceive, connect to, learn from, reason over, govern, or mutate. | Any category list treated as a boundary. | `locked_clarification` |

## Items Needing Focused Follow-Up

| Area | Reason |
| --- | --- |
| OpenClaw source pins | Local source-health review found stale OpenClaw docs URLs; refresh before stronger claims. |
| Skill marketplaces and connector catalogs | Need current-source review and security/license triage before adapter candidates become real. |
| Teacher/model roster | Model cards, licenses, hardware fit, and distillation rights change often; refresh before training or teaching use. |
| Medical, finance, legal, cyber, robotics | High-risk domains need domain-specific evals, citation policies, and human escalation gates. |
| `NexusGraph Intelligence Fabric` | Needs a schema, query contract, privacy model, mutability labels, adapters, and Control Panel replay design. |
| Machine-readable target registry | Needed so future agents can query status without parsing prose. |
