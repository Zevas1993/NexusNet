# Assimilation Target Cluster Review - 2026-07-04

Status: documentation-only review and consolidation ruling
Branch: `codex/all-worktrees-integration`
Scope source: `docs/assimilation/NEXUSNET_ALL_ASSIMILATION_TARGETS_CONSOLIDATED_2026-05-31.md`

## Purpose

This review clarifies the recurring confusion around "rejected" assimilation targets. A target can be rejected as a hard dependency, control plane, brain replacement, or unsafe execution path while still being preserved as a planned assimilation pattern.

The output of this review is not "delete these targets." The output is a cluster-level map:

1. What NexusNet should assimilate from each target family.
2. What NexusNet should reject or block.
3. Which NexusNet-native subsystem should combine overlapping ideas.
4. Which gates must pass before implementation, promotion, training, or production use.

## Status Vocabulary

| Status | Meaning |
| --- | --- |
| `preserve_as_planned_assimilation` | Keep the idea as a roadmap/planning item. It is not production-complete. |
| `legitimate_reject` | Reject a specific dependency, ownership model, unsafe behavior, claim, or import path. |
| `blocked_pending_review` | Keep visible, but do not promote until source, license, provenance, security, eval, or operator gates pass. |
| `native_nexusnet_output` | The NexusNet-owned subsystem that should combine one or more target patterns. |
| `review_required` | Needs file-level or source-level inspection before a stronger status is allowed. |

## Global Ruling

Assimilation targets are not external products to install wholesale. They are pattern sources, candidate adapters, teacher resources, eval fixtures, runtime strategies, UX references, or research prompts. NexusNet remains the mother brain and owner of governance, routing, memory, expert birth, teacher selection, recursive dreaming, promotion, rollback, and creator observability.

No source-health failure is automatically a rejection. The 2026-05-31 source re-verification packet explicitly says the 61 failed URLs mix stale links, private/local links, malformed extracted URLs, and real dead links. Each target still needs file-level review before changing its status.

GitNexus is a current reference/provider for codegraph intelligence, not the final owner of graph awareness. NexusBrain must internalize GitNexus-like indexing, query, impact analysis, stale-index blocking, and changed-scope detection, then extend the same graph intelligence across everything NexusNet is permitted to perceive, connect to, learn from, reason over, govern, or mutate. Any category list is illustrative, not limiting: code, repos, docs, chats, files, workflows, skills, tools, prompts, models, runtimes, memories, policies, evals, teachers, experts, devices, sensors, APIs, connectors, finance/crypto streams, medical and health knowledge, quantum/science research, user/org context, federation, environment signals, evidence, replay, and future assimilation surfaces.

## Current Source Spot Check

This pass used the local corpus plus current primary or near-primary sources where useful. These sources do not replace the full promotion gates:

- Agent Skills standard and Gemini CLI skills docs: `https://agentskills.io/home`, `https://geminicli.com/docs/cli/skills/`
- MCP specification and security best practices: `https://modelcontextprotocol.io/specification/2025-03-26`, `https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices`
- n8n, Flowise, Langflow, Dify: `https://github.com/n8n-io/n8n`, `https://github.com/FlowiseAI/Flowise`, `https://github.com/langflow-ai/langflow`, `https://github.com/langgenius/dify`
- RCE-class workflow/MCP advisories: `https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-3gcm-f6qx-ff7p`, `https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-c9gw-hvqq-f33r`, `https://github.com/n8n-io/n8n/security/advisories/GHSA-62r4-hw23-cc8v`
- Runtime and model harnesses: `https://github.com/ggml-org/llama.cpp`, `https://github.com/vllm-project/vllm`, `https://github.com/sgl-project/sglang`, `https://github.com/mlc-ai/mlc-llm`, `https://github.com/EricLBuehler/mistral.rs`, `https://github.com/mudler/LocalAI`, `https://github.com/open-webui/open-webui`
- Eval and observability: `https://github.com/EleutherAI/lm-evaluation-harness`, `https://github.com/langfuse/langfuse`, `https://github.com/open-telemetry/semantic-conventions-genai`, `https://owasp.org/www-project-top-10-for-large-language-model-applications/`
- Domain and science benchmarks: `https://github.com/TsinghuaC3I/MedXpertQA`, `https://github.com/qiskit-community/Qiskit-QuantumKatas`, `https://github.com/AI4Finance-Foundation/FinRL`, `https://github.com/OpenBB-finance/OpenBB`, `https://github.com/danijar/dreamerv3`
- Formal/proof teacher candidate: `https://huggingface.co/mistralai/Leanstral-1.5-119B-A6B`
- Agent-native memory and evolving graph research: `https://arxiv.org/abs/2606.24775`, `https://arxiv.org/abs/2507.07957`, `https://arxiv.org/abs/2502.12110`, `https://arxiv.org/abs/2506.06326`, `https://github.com/getzep/graphiti`, `https://github.com/HKUDS/LightRAG`, `https://arxiv.org/abs/2507.21892`
- Operational spine references: `https://openfeature.dev/`, `https://opentelemetry.io/`, `https://docs.temporal.io/`, `https://slsa.dev/`, `https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds`

## Detailed Review Artifacts

This cluster review is now accompanied by two follow-up artifacts:

- `docs/assimilation/ASSIMILATION_TARGET_DETAILED_RULINGS_2026-07-04.md`: target-level rulings for the named target families in this review.
- `docs/assimilation/assimilation_cluster_registry_2026-07-04.json`: machine-readable registry of the cluster outputs, representative targets, assimilation rules, rejected patterns, and gates.

These artifacts reduce ambiguity for future agents, but they do not promote any target, prove source health, validate licenses, or replace file-level review of the 195-source corpus.

## Already Corrected Items

| Target | Revised ruling |
| --- | --- |
| n8n | Reject n8n as a dependency, external runtime, or NexusNet control plane. Preserve n8n-style node/workflow UI, trigger semantics, run history, credential UX, and workflow learning as native NexusNet workflow graph patterns. |
| Ollama | Reject Ollama-only runtime lock-in. Preserve Ollama as a simple optional provider, tool-calling harness reference, and user-friendly local model UX. The real internal engine path must include `llama.cpp` and other runtime engines behind a NexusNet runtime abstraction. |
| PocketPal | Reject PocketPal as a direct product dependency or substitute integration. Preserve its mobile/edge local-model UX as a reference for a NexusNet companion app that can run local models, connect to a hosted NexusNet or birthed model, and participate in the hive under governed limits. |
| Static image visualizer | Reject static images as the final control surface. Preserve static diagrams for docs, patent figures, onboarding, and fallback exports. Native target is a live interactive Control Panel/Three.js or equivalent hive visualizer. |
| Siloed self-improvement ownership | Reject any claim that one AO, expert, orchestrator, coordinator, or runtime lane owns self-improvement exclusively. Mother brain owns and coordinates hive-wide neuroplasticity; all nodes can participate through governance. |
| Mega-skills and isolated endpoints | Reject opaque monolithic skills and disconnected endpoints. Preserve modular skills, recipes, MCP adapters, scripts, references, assets, workflow nodes, and runtime capability cards through progressive disclosure and strict budgets. |
| Pinecone/KAC cluster | Reject direct Pinecone dependency, raw retrieval replacement, uncited trusted synthesis, and direct runtime mutation. Preserve context compiler, citations, typed artifacts, composable retrieval, graph retrieval, raw fallback, claim ledgers, and governance as NexusNet Knowledge Forge. |
| GitNexus/codegraph gate | Reject GitNexus as the final mother brain, sole graph memory, or only place NexusNet understands connected state. Preserve GitNexus-style code indexing, graph query, impact analysis, stale-index checks, and change detection as the reference pattern for a NexusBrain-owned graph intelligence fabric that spans every permitted NexusNet connection. |

## Cluster 1: Workflow Builders And Node UI

Representative targets:

- n8n
- Flowise
- Langflow
- Dify
- Node-RED
- Activepieces
- Windmill
- Kestra
- Airflow
- Huginn
- ComfyUI-style graph ergonomics where applicable

What NexusNet should assimilate:

- Node graph editing with typed inputs, outputs, edges, triggers, schedules, retries, error branches, subflows, and reusable templates.
- Visual workflow provenance: who created a workflow, which sources/tools/models it touched, what it cost, what failed, what retried, and which policies were consulted.
- Credential UX patterns, but only as references for NexusNet-owned credential brokers and scoped secrets.
- Workflow memory: successful user-built workflows become evidence for SkillOps proposals, not automatic production skills.
- Mixed visual/code authoring: users can compose nodes visually, but each node still maps to a typed contract, tests, policy effects, and run receipts.

What NexusNet rejects or blocks:

- Any workflow builder as the root NexusNet control plane.
- Untrusted code nodes or MCP nodes executing with host privileges.
- Credential passthrough without scoped identity, audit, and revocation.
- Workflow runs that bypass SafetyAO, EvalsAO, CritiqueAO, authority, sandbox, or rollback.
- Treating visual graph success as proof of model or expert correctness.

Native NexusNet output:

`NexusNet Workflow Graph Studio`

This should combine n8n-style workflow ergonomics, Langflow/Flowise-style LLM graph prototyping, Dify-style app/workflow packaging, Node-RED-style event flow, and Airflow/Kestra/Windmill-style scheduling discipline. It is a user and mother-brain interface to NexusNet workflows, not an external automation dependency.

Gates:

- Every node declares effects, permissions, data classes, tool/model dependencies, and rollback behavior.
- Code-capable nodes run in a sandbox or task runner with explicit policy.
- MCP/tool nodes require identity, source pinning, command validation, and approval.
- Workflow traces feed SkillOps only after redaction, eval, and retention review.

## Cluster 2: Skills, Recipes, MCP, And Protocol Tooling

Representative targets:

- Agent Skills standard
- Gemini CLI skills
- Goose recipes and persistent instructions
- OpenClaw/Hermes-style skills and memory loops
- MCP resources, prompts, tools, roots, and sampling
- Composio/Pipedream-style connector catalogs where source/license review passes

What NexusNet should assimilate:

- Progressive disclosure: L0 metadata always visible, L1 candidate shortlist retrieved, L2 full instructions loaded only for selected skills, L3 scripts/assets/tools loaded only after permission checks, L4 traces stored externally and summarized.
- Portable skill folders: `SKILL.md`, scripts, references, templates, assets, evals, and source refs.
- Recipe/runbook contracts for repeated procedures.
- MCP as a protocol layer for resources, prompts, and tools, not as authority.
- Per-client consent, token audience validation, redirect validation, SSRF defenses, and scope minimization from MCP security guidance.
- Skill lifecycle: propose, sandbox, eval, promote, monitor, retire, split, merge, or archive.

What NexusNet rejects or blocks:

- Skills that hide many unrelated domains behind one vague description.
- Skills that mutate the system without mother-brain governance.
- MCP token passthrough, ambiguous tool identity, silent command execution, or multi-server trust propagation.
- Standalone endpoints that do not emit traces, receipts, eval state, rollback metadata, and permissions.

Native NexusNet output:

`NexusNet SkillOps And Protocol Fabric`

This combines skills, recipes, MCP adapters, connector catalogs, and tool bindings into a governed substrate. The mother brain routes skills sparsely rather than stuffing the model context.

Gates:

- Source pinning, license review, sandbox execution, skill eval, security scan, and reversible disablement.
- Hard budgets for active skills, tokens, tool calls, runtime cost, and memory writes.
- Overload response must defer, split the task, spawn an AO/expert, or create/merge skills after review.

## Cluster 3: Agent Frameworks And Coding Agents

Representative targets:

- LangGraph
- Microsoft Agent Framework / AutoGen successor direction
- CrewAI
- OpenHands
- Aider
- Continue
- Cline/Roo-style IDE agents
- Goose coding/operator flows
- Gemini CLI and Qwen-code-style terminal agents
- Tabby-style local code assistant patterns

What NexusNet should assimilate:

- Stateful graph execution and durable task state.
- Multi-agent role patterns: planner, implementer, reviewer, verifier, merger, operator, red-team, and documentation worker.
- Coding workspace isolation, ephemeral workspaces, worktree-per-agent patterns, event-sourced traces, and reproducible run receipts.
- Issue decomposition, plan-first execution, review gates, patch provenance, and test-evidence capture.
- Human intervention points for high-risk changes.

What NexusNet rejects or blocks:

- Any agent framework replacing NexusBrain, Orchestrator, AO, or Expert authority.
- Autonomous code merge, dependency installation, secret access, or production mutation without explicit gates.
- Hidden framework state that cannot be replayed or audited.
- Treating coding-agent success on one benchmark as general NexusNet readiness.

Native NexusNet output:

`Hive Agent Workbench`

This is a NexusNet-owned workbench for live problem solving, code work, research work, and implementation planning. It can use external agent frameworks as references or optional sandboxed workers, but every worker remains temporary, scoped, and trace-bound.

Gates:

- Worktree or sandbox isolation by default.
- GitNexus impact analysis before symbol edits.
- `detect_changes` before commit.
- Required test/eval evidence before promotion.
- Parent/child worker retention review before any new permanent expert/AO/orchestrator is created.

## Cluster 4: Runtime, Model Harnesses, And Edge Execution

Representative targets:

- `llama.cpp`
- Ollama
- vLLM
- SGLang
- TensorRT-LLM
- MLC-LLM
- mistral.rs
- LocalAI
- Open WebUI
- LM Studio
- PocketPal
- ONNX Runtime GenAI, MediaPipe, TFLite, ncnn where platform fit exists

What NexusNet should assimilate:

- Multi-engine runtime abstraction with model passport metadata, quantization profile, hardware fit, context limits, tool-calling compatibility, and privacy/cost class.
- `llama.cpp`/GGUF as a core local inference path for CPU/GPU/edge and quantized models.
- vLLM/SGLang/TensorRT-LLM as high-throughput or specialized server paths when hardware supports them.
- MLC/ONNX/TFLite/ncnn/MediaPipe-style device packaging for mobile and edge.
- LocalAI/Open WebUI/Ollama/LM Studio UX patterns for model catalogs, OpenAI-compatible endpoints, tool calling, and local admin ergonomics.
- PocketPal-style mobile model loading, download progress, quant choice, device constraints, and offline UX.

What NexusNet rejects or blocks:

- Any single runtime as mandatory.
- Ollama-only assumptions.
- A UI shell becoming the brain or primary router.
- Unscreened model downloads, unverified quantizations, unknown licenses, or untracked runtime binaries.
- Training/distillation from any model output without rights review.

Native NexusNet output:

`NexusNet Runtime Ladder And Model Passport Registry`

This combines local, mobile, server, remote, and cloud runtimes under one policy-controlled model passport. Runtime selection is a governed route decision, not a product preference.

Gates:

- Model card/license/provenance review.
- Hardware benchmark and degradation thresholds.
- Tool-calling compatibility tests.
- Privacy/offline classification.
- Rollback to known-good runtime and quant.
- Edge/mobile route cannot exceed device memory, thermal, or battery budgets.

## Cluster 5: Knowledge, Retrieval, And Memory

Representative targets:

- Pinecone Nexus / compiled knowledge layer
- Pinecone Assistant
- LlamaIndex
- LangChain retrieval components
- Microsoft GraphRAG
- Neo4j
- Qdrant, Weaviate, Chroma, pgvector, FAISS
- Semantic caches, provenance crates, evidence DAGs
- MIRIX, A-MEM, MemoryOS, Mem0, MemInsight, Cognitive Weave
- Graphiti/Zep, LangMem, Letta/MemGPT, context repositories
- Titans, Engram, M+, memory models, and conditional lookup research
- LongMemEval, LoCoMo/LoCoMo-Plus, MemoryAgentBench, BEAM, MemoryArena, STATE-Bench

What NexusNet should assimilate:

- Context compiler and artifact-first knowledge layer.
- Declarative query concepts similar to KnowQL, translated into NexusNet Knowledge Request Contracts.
- Document upload and grounded QA UX.
- Loaders, connectors, chunk/node abstractions, query engines, and retriever composition.
- Vector abstraction, metadata filters, hybrid search, local/cloud modes.
- Graph extraction, relationship reasoning, contradiction detection, community summaries, and memory graph links.
- Raw retrieval as audit path, fallback, live-data path, and source comparison.
- `Memory OS`: short-term, working, mid-term, long-term, archival, hot/conditional, and model-native memory tiers.
- `Memory Extraction Pipeline`: durable facts, preferences, procedures, failures, decisions, source claims, task lessons, and user-approved context distilled from traces.
- `Memory Router`: lexical, vector, graph, temporal, procedural, episodic, multimodal, hot-memory, and raw-source retrieval selection by task.
- `Memory Maintenance Loop`: merge, split, decay, retire, refresh, deduplicate, contradict, consolidate, and rollback memories.
- `Temporal Memory Layer`: valid time, observed time, stale state, previous fact history, source provenance, and contradiction history.
- `Agentic Memory Evolution`: autonomous linking, augmentation, abstraction, ontology refinement, and retrieval-policy learning as shadow-first memory deltas.
- `Multimodal Memory`: screen, image, document, tool, device, resource, and environment memory with explicit privacy boundaries.
- `Sleep-Time Memory Consolidation`: downtime processing that compresses traces, extracts lessons, updates retrieval policies, proposes memory deltas, and routes risky deltas to review.
- `Memory Eval Harness`: retrieval, test-time learning, long-range understanding, selective forgetting, temporal reasoning, cognitive constraints, multi-hop recall, action usefulness, cost, latency, and privacy checks.
- `Model-Native Memory Watchlist`: Titans, Engram, M+, memory models, and conditional lookup as future teacher, runtime, or model-birth inputs.

What NexusNet rejects or blocks:

- Direct Pinecone dependency or vendor-owned knowledge layer as brain.
- Static vector memory as enough.
- Raw transcript hoarding.
- Replacing raw retrieval entirely.
- Storing uncited synthesized facts as trusted knowledge.
- Silent memory overwrite.
- Memory writes without consent/privacy labels.
- Dream output promoted as memory fact.
- Cross-user or federated memory leakage.
- Letting compiled context or memory deltas mutate prompts, routes, experts, teachers, skills, runtimes, or model weights without governance.

Native NexusNet output:

`NexusNet Knowledge Forge And Agent-Native Memory OS`

The Forge includes Source Registry, Ingestion Pipeline, Evidence Ledger, Multi-Index Store, Context Compiler, Artifact Registry, Composable Retriever, Claim Ledger, Governance Gate, Raw Retrieval Fallback, Review UI, and agent-native memory lifecycle services for extraction, storage, update, retrieval, consolidation, forgetting, evaluation, and promotion.

Relationship to Cluster 13:

Cluster 5 owns memory substrate behavior. Cluster 13 owns the universal graph intelligence that connects memory to code, workflows, policy, tools, models, experts, devices, releases, dreams, and operational consequences.

Relationship to Cluster 9:

This memory expansion requires more O/AO/Expert lanes. Seed candidates, not final approved roster, include `AgentNativeMemoryOrchestrator`, `MemoryEvolutionOrchestrator`, `ContextRepositoryOrchestrator`, `MemoryQualityAO`, `MemoryExtractionAO`, `MemoryRoutingAO`, `TemporalMemoryAO`, `MemoryMaintenanceAO`, `MultimodalMemoryAO`, `SleepConsolidationAO`, `MemoryPrivacyAO`, `MemoryEvalAO`, `MemoryCompressionExpert`, `ContradictionResolutionExpert`, `SelectiveForgettingExpert`, `ProceduralMemoryExpert`, `EpisodicMemoryExpert`, `SemanticMemoryExpert`, `TemporalGraphMemoryExpert`, `HotMemory/EngramExpert`, and `MemoryBenchmarkExpert`.

Gates:

- Field-level citations, source hashes, freshness metadata, RBAC/privacy tags, conflict objects, and replayable query events.
- Unsupported claims stay candidate, research-only, or blocked pending evidence.
- Any artifact recommending a runtime, teacher, expert, skill, or route change becomes a candidate delta, not an automatic mutation.
- Every memory write/update requires a `MemoryEvolutionPassport` with `memory_id`, `memory_type`, `source_ref`, `source_hash`, `privacy_class`, `owner`, `valid_time`, `observed_time`, `confidence`, `contradiction_refs`, `staleness_state`, `retrieval_eval_delta`, `behavior_eval_delta`, `teacher_review`, `privacy_review`, `rollback_ref`, and `promotion_state`.

## Cluster 6: Evaluation, Observability, And Evidence

Representative targets:

- Inspect AI
- EleutherAI lm-evaluation-harness
- DeepEval
- promptfoo
- OpenAI eval-style graders
- Langfuse
- Arize Phoenix
- OpenTelemetry GenAI semantic conventions
- Agent/task benchmarks in the assimilation corpus

What NexusNet should assimilate:

- Standard benchmark runner adapters and custom task evals.
- LLM-as-judge only as one signal, calibrated against deterministic, human, or domain-specific checks.
- Dataset versioning, prompt/version management, experiment lineage, and trace-to-score links.
- OpenTelemetry-style spans, metrics, and events for model calls, tool calls, retrieval, MCP calls, skill activation, eval results, and agent steps.
- Continuous evals before promotion and after deployment.
- Evidence packets that can be replayed, exported, and compared.

What NexusNet rejects or blocks:

- Single leaderboard scores as promotion proof.
- Opaque judge-only evaluation.
- Eval results without datasets, prompts, model versions, seeds where applicable, tool versions, and trace refs.
- Monitoring systems as a second control plane.

Native NexusNet output:

`EvalsAO Evidence Spine`

EvalsAO remains external enough to judge the hive, but deeply integrated enough to gate teachers, skills, experts, runtimes, routes, dreams, and product changes.

Gates:

- Every promoted capability needs a scorecard, regression threshold, failure examples, source refs, and rollback plan.
- Medical, finance, legal, security, and high-authority domains require stricter evals and human/operator review.

## Cluster 7: Security, Authority, Isolation, And Supply Chain

Representative targets:

- OWASP LLM Top 10
- MCP security guidance
- Semgrep
- Trivy
- Grype
- Snyk
- OSSF Scorecard
- Sigstore/SLSA/SCITT-style provenance
- Biscuit/object-capability/datalog token patterns
- WASM, Landlock/seccomp, hardened JS compartments

What NexusNet should assimilate:

- Prompt-injection, insecure-output, training-data-poisoning, model-DoS, supply-chain, plugin, excessive-agency, and sensitive-disclosure controls.
- Capability tokens, scoped identity, per-client consent, no token passthrough, audience validation, exact redirect checks, and command allowlists.
- Sandboxed execution tiers for shell, code, browser, MCP, plugin, workflow, model runtime, and third-party adapters.
- SBOM/model-BOM/AI-BOM, signature verification, source pinning, dependency scanning, and reproducible build or rebuild evidence where practical.
- Incident receipts, denial receipts, and read-only replay.

What NexusNet rejects or blocks:

- Prompt-only security.
- Broad ambient credentials.
- Fail-open reviewer failure on high-risk paths.
- Unsandboxed code nodes, CustomMCP-style arbitrary command execution, or subprocess access from untrusted graph nodes.
- Plugins or skills with unclear update roots.

Native NexusNet output:

`Authority And Isolation Fabric`

This is the policy, sandbox, identity, token, provenance, supply-chain, and audit substrate under every AO, expert, workflow, skill, tool, runtime, and companion device.

Gates:

- Permission envelope before execution.
- Explicit denied/allowed/review-required receipt.
- Security scan and source review before plugin/skill/model promotion.
- Production mutation requires sandbox, eval, rollback, monitoring, and human/governance approval.

## Cluster 8: Self-Improvement, Recursive Dreaming, And World Models

Representative targets:

- Recursive Neural Dreaming corpus items
- DreamerV3/world-model research
- PAN-style long-horizon world simulation research
- AlphaEvolve-style verifier-guided search
- Darwin-Godel-machine lineage
- GFlowNet diverse thought factory
- causal intervention cortex
- active inference/homeostasis
- hippocampal replay/consolidation
- developmental/open-ended AI embryo

What NexusNet should assimilate:

- High-temperature dream generation as unusual hypothesis search.
- Low-temperature critique, verifier checks, safety review, and eval before any dream output influences active behavior.
- Latent world-model rollouts for planning, failure prediction, and sandbox rehearsal.
- Replay consolidation from traces into memory candidates, curriculum candidates, skill proposals, expert proposals, and eval fixtures.
- Causal intervention experiments in sandboxed worlds.
- Intrinsic motivation only as a bounded curriculum selector that improves capability, not as random or unsafe autonomy.
- Expert birth, split, merge, and retirement review when the system is stuck or when a child outperforms a parent.

What NexusNet rejects or blocks:

- Direct active self-modification from dreams.
- Treating a dream as evidence.
- Consciousness, whole-brain-emulation, or organoid claims as product proof.
- Wetlab or biological experimentation instructions.
- Open-ended self-improvement without containment, evals, rollback, and operator approval.

Native NexusNet output:

`Recursive Dreaming And Imagination Foundry`

This combines dream cycles, world models, replay, diverse thought generation, causal experiments, and expert birth/merge flows into a shadow-first improvement engine.

Gates:

- Dreams produce candidates only.
- Every candidate must pass source/provenance, sandbox, eval, security/privacy, teacher review, and rollback gates.
- Live-problem expert creation is allowed only as a temporary child expert unless retention review approves permanence.

## Cluster 9: Teacher Council And Expert Expansion

Representative targets:

- Leanstral 1.5
- Nemotron/NVIDIA multimodal teacher candidates
- Keye-VL and other video-temporal teachers
- LFM/Liquid compact multimodal models
- MiniCPM and edge workers
- Qwen/DeepSeek/Kimi/Mistral/Devstral-style open or license-eligible teachers
- Medical reasoning benchmarks/models
- Finance/quant benchmarks and tools
- Quantum research/code benchmarks
- Root NexusBrain, O-level Orchestrators, Assistant Orchestrators, Experts, core nodes, temporary live-problem experts, memory/graph lanes, and birth/merge/split/retire flows

What NexusNet should assimilate:

- Dynamic teacher roster with current-source refresh, capability cards, license status, distillation rights, hardware fit, and domain scorecards.
- `TeacherCapabilityPassport` and `ExpertDomainPassport` records instead of a fixed roster.
- At least two teachers for every Expert, Assistant Orchestrator, Orchestrator, and core node before birth verification or distillation is treated as legitimate.
- Teacher roles including generator, critic, verifier, simulator, retriever, judge, compact apprentice, runtime teacher, safety reviewer, and domain specialist.
- Open-world O/AO/Expert domain atlas that can birth, merge, split, retire, archive, or refresh entries when evidence requires it.
- Leanstral as a formal-methods and Lean 4 theorem-proving teacher: proof repair, formal specification, theorem decomposition, proof-driven code contracts, and mathematical rigor for expert/AO training.
- Medical teachers as evidence-gated clinical reasoning curriculum and eval resources, not autonomous care providers.
- Finance and crypto teachers as data, risk, market-simulation, and quant-research experts, not autonomous trading authority.
- Quantum teachers as Qiskit/quantum-code/circuit-reasoning evaluators and research assistants, not hardware truth or physics oracle.
- Domain teachers for holistic medicine, law, cybersecurity, hardware, biology, chemistry, creative work, education, robotics, logistics, and other expert areas through a common expert-pack contract.
- Memory and graph teacher panels for agent-native memory, temporal graph memory, graph query, graph evolution, graph safety, GraphRAG planning, graph replay, graph privacy, and graph eval specialists.

What NexusNet rejects or blocks:

- A fixed, stale teacher roster.
- Any one "god teacher" for every domain.
- Closed or unclear-rights outputs used for training/distillation.
- Medical, financial, legal, or safety-critical production advice without regulatory/compliance/human-review gates.
- Replacing the mother brain with a teacher model.
- Treating the current examples as a complete O/AO/Expert inventory.
- Production birth, merge, split, retirement, or parent replacement from one teacher or one eval.

Native NexusNet output:

`Teacher Council And Expert Birth Registry`

This maintains O-level, AO-level, and Expert-level teacher panels. It can create, split, merge, retire, or temporarily spawn experts during live problems, but permanent changes require evidence and governance.

Gates:

- Source/license/provenance and distillation-rights review.
- Domain-specific evals.
- Multi-teacher disagreement capture.
- Child-vs-parent scorecard.
- Archive-not-delete retirement.
- Human/operator approval before permanent promotion or parent retirement.
- Cluster 5 memory expansion and Cluster 13 graph expansion require a follow-up O/AO/Expert reconciliation pass before any final roster is claimed.

## Cluster 10: Domain Expert Packs

Representative target domains:

- Medicine and clinical reasoning
- Holistic medicine and wellness
- Finance, quant, macroeconomics, accounting, taxes, and crypto
- Law, policy, compliance, patents, and contracts
- Cybersecurity, malware analysis, red team, blue team, and supply chain
- Mathematics, formal methods, proof, and theorem proving
- Quantum computing, physics, chemistry, biology, neuroscience, and materials
- Robotics, controls, embedded systems, edge devices, and IoT
- Education, psychology, communications, design, writing, media, and product
- Business operations, CRM, HR, sales, marketing, logistics, and procurement
- Local-device, mobile, accessibility, privacy, and offline-first operation

What NexusNet should assimilate:

- A repeatable expert-pack schema: domain scope, contraindications, allowed actions, disallowed actions, teacher set, eval set, knowledge sources, required human gates, output style, confidence policy, and escalation path.
- Evidence grading and source ranking per domain.
- Auto-research for new domains, subdomains, and live-problem gaps.
- Auto-discovery of teacher models, validators, datasets, simulators, tools, and source authorities.
- Domain simulators and benchmark datasets where licenses allow.
- Expert merge/split rules when domains overlap, such as medical + pharmacology, finance + crypto, law + tax, cybersecurity + software engineering, or quantum + chemistry.
- Holistic medicine as an evidence-graded wellness research lane with interaction/risk warnings, not as medical authority.

What NexusNet rejects or blocks:

- "Every possible expert" as one giant static list inside context.
- High-risk domain outputs without citations, confidence, disclaimers, and escalation gates.
- Autonomous trading, diagnosis, legal filing, or security exploitation without scoped permission and human approval.
- Domain packs that cannot be evaluated.
- The Forge mutating production state by itself.

Native NexusNet output:

`Expert Pack Radar And Domain Curriculum Forge`

This is an auto-research, auto-proposal, auto-eval, and auto-update system for expert packs. It should discover new model/paper/tool candidates, compare them to existing packs, and propose births/merges/retirements without mutating production state by itself.

Gates:

- Domain pack cannot activate fully until it has a minimum source set, eval set, risk policy, and teacher pairings.
- Live problem spawn is temporary by default.
- Permanent expert creation requires retention review.
- The mother brain owns promotion, and production mutation requires eval evidence, teacher review, rollback, and governance approval.

## Cluster 11: UI, Visualizer, Companion, And Product Shell

Representative targets:

- Static diagrams
- interactive Three.js/control-panel visualizer direction
- PocketPal
- Open WebUI
- LocalAI WebUI
- Dify/Langflow/Flowise UX references
- OpenJarvis first-run/productization patterns

What NexusNet should assimilate:

- Live hive visualizer with brain, O, AO, expert, skill, model, memory, runtime, eval, and dream state.
- Deep replay drilldown for traces, decisions, promotions, denials, rollback, and expert creation.
- Workflow Graph Studio and node UX owned by NexusNet, not delegated to external builders.
- Teacher registry, expert pack radar, runtime/model controls, and skill manager surfaces.
- Mobile companion app for local model loading, edge inference, offline mode, device-to-host communication, and hive participation under mother-brain governance.
- First-run `init`, `doctor`, model-fit recommendations, hardware status, and safe-mode reporting.
- User-visible controls for workflow graph, skills, teachers, experts, and runtime routes.

What NexusNet rejects or blocks:

- Static image as final product UI.
- Companion app as independent brain owner.
- UI-only evidence of implementation.
- Product shell that hides readiness gaps.
- Raw private trace sync to companion devices without explicit authorization and redaction.

Native NexusNet output:

`NexusNet Control Panel And Companion`

This combines live visualizer, workflow graph studio, model/runtime controls, skill manager, teacher registry, expert pack radar, mobile/edge companion, and evidence replay.

Gates:

- UI labels must distinguish verified implementation, shadow candidate, planned placeholder, blocked item, stale item, production-active item, and research-only target.
- Read-only replay must not mutate runtime.
- Companion devices are subordinate hive participants only.
- Companion devices cannot receive private raw traces unless explicitly authorized and redacted.
- Mobile and edge participation requires a permission envelope, redacted sync, device trust state, rollback, and offline-safe behavior.

## Cluster 12: Productization, Ops, And Worktree Governance

Representative targets:

- OpenJarvis productization patterns
- Goose runtime/operator patterns
- Sandcastle/worktree-per-agent patterns
- GitNexus codegraph gate
- feature-flagged rollouts
- reversible patch transaction logs
- deterministic replay snapshots

What NexusNet should assimilate:

- `Workspace Alignment Spine`: canonical branch, worktree registry, dirty-tree classifier, preserved artifact index, merge queue, branch ancestry, and enforcement that dirty work is never assumed to be clean baseline.
- `Agent Workcell Factory`: worktree-per-agent and sandbox-per-agent execution with owner, goal, base commit, permissions, created artifacts, exit state, review state, merge state, and rollback receipt.
- `Release And Rollout Spine`: stable, candidate, shadow, and canary channels for prompts, routers, skills, policies, models, runtimes, dreams, expert packs, UI, and federation updates.
- `Operational Evidence Spine`: proofpacks, command receipts, GitNexus status, impact analysis, detect-changes, source-health snapshots, eval results, artifact scans, replay links, and approval receipts.
- `First-Run And Doctor Spine`: bootstrap, local-first setup, dependency checks, model/runtime fit, hardware readiness, safe mode, preset bundles, scheduler setup, and honest readiness labels.
- `Incident Replay And Rollback Spine`: deterministic event histories, replay snapshots, reversible transaction logs, rollback tests, incident timelines, and post-incident promotion holds.
- `Telemetry And SLO Spine`: traces, metrics, logs, model calls, tool calls, agent/workflow/runtime health, latency, cost, energy, memory, failures, eval drift, and user-visible health.
- `Supply Chain And Provenance Spine`: signing, source provenance, build provenance, artifact attestations, SBOMs, dependency/license/security scans, and artifact trust.
- `Model/Data/Artifact Registry Spine`: model lifecycle records, dataset and experiment versioning, model card metadata, model aliases, champion/challenger routing, rollbackable datasets, and release manifests.
- `Ops Scheduler And Monitor Spine`: scheduled jobs, monitors, workflow runs, recurring source/model scans, dependency update reviews, hardware checks, source radar, and assimilation radar.
- `Auto-Update And Assimilation CI`: research new releases, model cards, papers, security advisories, benchmarks, and dependency updates, then produce candidate updates only.
- `Disaster Recovery Spine`: backups, restore points, state snapshots, offline-safe mode, failed-update recovery, companion-device resync rules, and historical artifact retention.

What NexusNet rejects or blocks:

- Another product shell that becomes the real system.
- Untracked dirty work becoming assumed baseline.
- Deleting preserved worktrees, historical refs, or artifacts just to reduce confusion.
- Branch/worktree confusion.
- Feature rollout without flags, monitoring, rollback, owner, and evidence.
- Dependency, model, data, skill, prompt, router, policy, runtime, dream, or expert-pack upgrades without license, provenance, eval, security, and rollback review.
- Replay paths that mutate live state.
- CI-green-only release readiness.
- Mixing research, dream, shadow, canary, blocked, stale, placeholder, and production-active states.

Native NexusNet output:

`NexusNet Operational Spine`

This keeps future work aligned: canonical branch, GitNexus status, source-of-truth docs, preserved artifacts, worktree hygiene, evidence packets, release channels, registries, monitors, and rollback-ready changes.

Gates:

- Start from canonical branch unless the user explicitly chooses another.
- Preserve historical refs and artifacts unless explicitly approved for deletion.
- Before code symbol edits, run GitNexus impact analysis.
- Before commits, run GitNexus detect-changes.
- Every operational change needs an `OperationalChangePassport` with owner, goal, source, base state, branch/worktree, affected surfaces, data class, permissions, feature flag, rollout stage, evidence packet, eval result, telemetry plan, rollback plan, approval state, and expiry or review date.

## Cluster 13: Mother Brain Graph Intelligence

Representative targets:

- GitNexus codegraph indexing and MCP query patterns
- NexusNet `CodegraphGate`
- Knowledge graphs, GraphRAG, Neo4j-style relationship modeling, and provenance DAGs
- Agentic GraphRAG, Graph-R1-style graph environments, LazyGraphRAG, LightRAG, HippoRAG, and temporal graph memory
- Workflow, skill, model, runtime, policy, eval, memory, expert, teacher, device, and federation graphs
- Control Panel deep replay graph and pathway ledgers
- Every current and future NexusNet-connected artifact, signal, source, system, environment, user-approved device, and external service

What NexusNet should assimilate:

- `Universal Graph Registry`: typed nodes and edges for code, docs, workflows, skills, tools, prompts, models, runtimes, memories, policies, evals, experts, teachers, devices, releases, dreams, incidents, source feeds, market feeds, medical/science/quantum knowledge, user/org context, federation, and external permitted signals.
- `Codegraph Cortex`: GitNexus-like indexing, query, impact analysis, stale-index gates, detect-changes, affected-neighborhood views, replayable codegraph evidence, and patterns from SCIP/LSIF, Tree-sitter, and CodeQL.
- `Agentic Evolving GraphRAG Cortex`: graph planner, subgraph search, tool/retriever actions, multi-hop reasoning, contradiction checks, source/eval checks, graph update proposals, shadow graph deltas, teacher/eval review, and rollback.
- `Agentic Memory Evolution Cortex`: links Cluster 5 memory evolution into the graph, including memory deltas, stale facts, contradictions, retrieval-policy changes, sleep consolidation, and memory-driven expert birth/merge/split triggers.
- `Capability Graph`: maps which Orchestrator, Assistant Orchestrator, Expert, skill, tool, model, runtime, workflow, connector, or device can act on each surface under which authority and permission envelope.
- `Policy And Risk Graph`: permissions, privacy class, authority, high-risk domain rules, human gates, blocked actions, escalation paths, and protected surfaces.
- `Operational Dependency Graph`: worktrees, branches, rollouts, feature flags, evidence packets, source-health records, release manifests, incident replay, rollback receipts, and operational passports from Cluster 12.
- `Memory And Dream Graph`: failures, successes, dream proposals, dream reviews, memory deltas, teacher disagreements, eval outcomes, and self-improvement candidates.
- `Federation And Device Graph`: companion devices, local nodes, hive participants, trust state, redaction state, contribution lineage, and data-sharing boundaries.
- `Mutation Impact Engine`: pre-change impact, post-change detect scope, affected-neighborhood view, rollback path, and Control Panel replay.
- Agentic evolving GraphRAG loop: `task/stuck signal -> graph planner -> subgraph search -> tool/retriever actions -> multi-hop reasoning -> contradiction check -> source/eval check -> graph update proposal -> shadow graph delta -> teacher/eval review -> promotion or rollback`.

What NexusNet rejects or blocks:

- Treating GitNexus, a graph database, a vector store, or any external index as the mother brain.
- Letting graph output replace direct source reading, tests, evals, red-team review, rights review, or human/governance approval.
- Static GraphRAG as enough.
- Inferred edges treated as verified facts.
- Graph or memory poisoning promoted without quarantine.
- Dream-generated graph edges treated as facts.
- Stale graph facts, uncited graph facts, hidden graph state, or graph paths that cannot be replayed.
- Stuffing the full graph into model context instead of using progressive disclosure and typed graph queries.
- Separate silo graphs for code, memory, tools, workflows, models, runtime, policy, evals, and operations with no mother-brain visibility.
- Private, regulated, or federated graph leakage across users, devices, organizations, or permission boundaries.
- Direct runtime mutation from graph conclusions without sandbox, eval, policy, rollback, and promotion gates.

Native NexusNet output:

`NexusGraph Intelligence Fabric`

This is the mother-brain-owned graph layer that generalizes GitNexus-like code intelligence into whole-system intelligence. It is not limited to software artifacts or the current hive internals. It is the connected-state substrate for everything NexusNet can access under permission and policy, and it is how the mother brain knows what it is connected to, what can be changed, what should not be changed, and what every change may affect. GitNexus can remain an adapter, provider, and reference implementation for codegraph evidence, but NexusBrain owns the final universal graph contracts, routing authority, freshness checks, impact analysis, mutation gates, and replay surface.

Gates:

- Every graph node and edge must carry source refs, artifact or signal version, freshness state, permissions, privacy class, ownership, mutability, and confidence.
- Code edits still require GitNexus-compatible impact and detect-changes evidence until the native codegraph path proves equivalent or stronger coverage.
- Non-code mutations across any connected surface require the same pattern: pre-change impact, policy/eval gate, sandbox or shadow run, post-change detect scope, rollback proof, and replay evidence.
- Graph-driven expert birth, merge, split, retirement, dream proposal, or skill promotion remains shadow-only until teacher/eval/governance approval passes.
- Control Panel graph views must label verified implementation, planned placeholder, blocked item, research-only target, and stale evidence distinctly.
- Every graph node and edge needs a `GraphFactPassport`.
- Every graph query needs a `GraphQueryPassport`.
- Every proposed graph delta needs a `GraphEvolutionPassport`.
- `MemoryEvolutionPassport` links in from Cluster 5 for memory-specific writes and updates.
- Cluster 5 memory expansion and Cluster 13 graph expansion require a follow-up Cluster 9 O/AO/Expert reconciliation pass before any final roster is claimed.

## Consolidated Final Outputs

| Native subsystem | Combines target families |
| --- | --- |
| `NexusNet Workflow Graph Studio` | n8n, Flowise, Langflow, Dify, Node-RED, Activepieces, scheduler/workflow engines |
| `NexusNet SkillOps And Protocol Fabric` | Agent Skills, Gemini skills, Goose recipes, OpenClaw/Hermes patterns, MCP, connector catalogs |
| `Hive Agent Workbench` | LangGraph, Microsoft Agent Framework/AutoGen lineage, CrewAI, OpenHands, coding agents, worktree workers |
| `NexusNet Runtime Ladder And Model Passport Registry` | llama.cpp, Ollama, vLLM, SGLang, TensorRT-LLM, MLC, mistral.rs, LocalAI, Open WebUI, PocketPal, mobile runtimes |
| `NexusNet Knowledge Forge` | Pinecone/KAC pattern, LlamaIndex, GraphRAG, vector DBs, graph DBs, semantic cache, raw retrieval |
| `EvalsAO Evidence Spine` | Inspect AI, lm-eval, DeepEval, promptfoo, Langfuse, Phoenix, OTel GenAI, benchmark packs |
| `Authority And Isolation Fabric` | OWASP, MCP security, object capabilities, sandbox tiers, SBOM/AI-BOM, source pinning, signed receipts |
| `Recursive Dreaming And Imagination Foundry` | recursive dreaming, world models, replay, causal intervention, AlphaEvolve/DGM/GFlowNet-style proposal search |
| `Teacher Council And Expert Birth Registry` | Leanstral, Nemotron, Keye-VL, LFM, MiniCPM, Qwen/DeepSeek/Kimi/Mistral/Devstral, medical/finance/quantum teachers |
| `Expert Pack Radar And Domain Curriculum Forge` | every domain expert class, expert-pack schema, domain evals, auto-research, expert split/merge |
| `NexusNet Control Panel And Companion` | live visualizer, mobile/edge app, local model UX, workflow UI, teacher/expert/skill controls |
| `NexusGraph Intelligence Fabric` | GitNexus, CodegraphGate, graph retrieval, all permitted connected artifacts/signals/systems, workflow graphs, skill graphs, model/runtime graphs, policy/eval graphs, replay ledgers |
| `NexusNet Operational Spine` | GitNexus, worktrees, feature flags, replay snapshots, reversible patches, consolidation status |

## Final Reject Rules

These are legitimate rejects:

1. External product as NexusNet brain, mother brain, or final control plane.
2. Single-runtime lock-in.
3. Direct source import without license/provenance/security review.
4. Closed or unclear-rights output used for distillation/training.
5. Untrusted code/MCP/workflow execution without sandbox and consent.
6. Static diagrams as final live-control product.
7. Siloed self-improvement ownership.
8. Opaque mega-skills or context-stuffed expert lists.
9. Trusted knowledge without citations.
10. Direct runtime mutation from dreams, retrieval artifacts, eval results, or model suggestions.
11. External codegraph or graph database treated as the final NexusNet brain.

These are not legitimate rejects:

1. Planned placeholders clearly labeled as planned, pre-production, future assimilation, or blocked pending evidence.
2. Source-health failures without file-level review.
3. External products used only as UI, workflow, skill, runtime, eval, teacher, or governance pattern references.
4. Temporary live-problem child experts that remain sandboxed and review-bound.
5. Research-only targets kept as future options.
6. GitNexus-style graph intelligence preserved as a planned native mother-brain capability across everything NexusNet is permitted to connect to while the current adapter/gate remains external.

## Next Documentation And Implementation Work

Approved follow-up queue after this review:

1. Specify `NexusNet Knowledge Forge And Agent-Native Memory OS` schemas, `MemoryEvolutionPassport`, memory eval policy, privacy policy, and forgetting policy.
2. Reconcile Cluster 9 graph/memory O/AO/Expert seed candidates into the open-world teacher/expert atlas before any final roster is claimed.
3. Specify the `NexusNet Operational Spine`, including `OperationalChangePassport`, worktree registry, release-channel policy, disaster recovery policy, model/data/artifact registries, scheduler contracts, monitor contracts, and Control Panel projection.
4. Specify the `NexusGraph Intelligence Fabric` schema, adapters, graph query contracts, impact-analysis contracts, detect-scope contracts, privacy filters, mutability labels, graph delta storage, poisoning defenses, ontology evolution policy, and Control Panel graph replay.
5. Build a model/source radar job that watches model cards, papers, GitHub releases, licenses, source liveness, and benchmark deltas, then proposes updates through the mother-brain governance queue.
6. Continue converting the 195-source raw corpus into reviewable target-level batches when a source file contains a distinct target not already represented in the detailed rulings.
