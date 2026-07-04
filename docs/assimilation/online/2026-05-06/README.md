# NexusNet Online Assimilation Specs - 2026-05-06

Status: research-only online assimilation packet. These findings are non-video targets discovered from papers, official protocol/spec pages, GitHub/source pages, model release notes, and security advisories. Nothing here promotes a target into locked NexusNet canon by itself.

Purpose: keep the broader online assimilation queue separate from watched-video evidence. Every target below should remain a refs-only candidate until a later implementation pass validates it against the live NexusNet code, policy boundaries, tests, and operator-control surfaces.

## Source Reverification - 2026-05-31

See `docs/assimilation/ASSIMILATION_TARGET_SOURCE_REVERIFICATION_2026-05-31.md`.

The 2026-05-31 pass included this online packet in the all-file inventory. Across all assimilation-related docs, 191 files and 872 unique URLs were checked; 777 returned normal success, 34 were reachable but manual/gated, and 61 failed. This packet remains research-only: source liveness confirms that a reference exists, not that NexusNet has accepted, implemented, benchmarked, or licensed the target.

Updates from the pass that affect this packet:

- Add OSCAR to the KV-cache runtime-efficiency lane.
- Add EAGLE 3.1/vLLM to the speculative decoding lane.
- Add LiteParse v2.0 to the document parsing/certification lane.
- Add MiniCPM5-1B-GGUF and Keye-VL-2.0-30B-A3B to the open model/runtime ladder with separate edge-worker and conditional-teacher roles.
- Keep all 134 online specs behind source/license/security/local-eval gates.

## Final Missing Piece

The final synthesis is [Final Missing Piece Synthesis](FINAL_MISSING_PIECE_SYNTHESIS.md): NexusNet's highest-upside differentiator is a governed developmental cortex. The core is not a larger model or unsupported consciousness claim; it is the closed loop of self-model, world model, causal model, developmental growth, sleep consolidation, and evidence-gated promotion.

## Ranking

| Rank | Spec | Assimilation target | Disposition |
| --- | --- | --- | --- |
| 1 | [AgentFloor Routing Ladder](01-agentfloor-routing-ladder-spec.md) | Small/open model routing for routine tool calls with frontier escalation for hard planning | Critical. Directly matches NexusNet open-first model economics and workload routing. |
| 2 | [Computer-Use Safety Reliability](05-computer-use-safety-reliability-spec.md) | OS-BLIND, AgentHazard, and repeated-run reliability gates for browser/desktop operators | Critical before any higher-authority VisualOps or computer-use lane. |
| 3 | [MCP Security And Dynamic Red Team](09-mcp-security-dynamic-red-team-spec.md) | MCP STDIO, tool-poisoning, prompt-injection, and capability-attestation hardening | Critical for any MCP/tool marketplace or protocol bridge. |
| 4 | [ClawMark Coworker Eval](02-clawmark-coworker-eval-spec.md) | Multi-day, multimodal, evolving workspace benchmark for persistent assistant behavior | High. Strong fit for KAC, memory, Control Panel, and workspace-state certification. |
| 5 | [AgentProcessBench Step Verifier](03-agentprocessbench-step-verifier-spec.md) | Step-level quality signals before irreversible side effects | High. Turns agent traces into reviewable process evidence. |
| 6 | [Amazing Agent Race Navigation](04-amazing-agent-race-navigation-spec.md) | Navigation/context selection benchmark for retrieval planners | High. Directly targets RAG drift and wrong-context action loops. |
| 7 | [ClawArena Belief Revision](06-clawarena-belief-revision-spec.md) | Dynamic belief revision, contradiction handling, and implicit personalization | High. Strong fit for memory quality ledger and source-status logic. |
| 8 | [ParseBench Document Certification](07-parsebench-document-certification-spec.md) | Enterprise document parsing gates for KAC ingestion and artifact trust | High. Prevents bad extracted tables/charts/OCR from becoming memory. |
| 9 | [AgentProof Workflow Verification](08-agentproof-workflow-verification-spec.md) | Static graph verification for agent workflows before runtime | High where NexusNet exposes graph-like plans or skill pipelines. |
| 10 | [Protocol Trust Stack](10-protocol-trust-stack-spec.md) | A2A, AIP, MCP, AOP, and OpenTelemetry boundaries | High. Defines identity, delegation, observability, and protocol separation. |
| 11 | [Embeddable Agent Core](11-embeddable-agent-core-spec.md) | Sema Code, OpenDev, OpenHands, and local-first agent core patterns | Medium-high. Useful architecture comparison without copying product behavior. |
| 12 | [Open Model Runtime Ladder](12-open-model-runtime-ladder-spec.md) | Qwen3-Coder-Next, Gemma 4, LFM2.5-350M, speculative decoding | Medium-high. Feed the open-first teacher/runtime roster and edge certification lane. |
| 13 | [Agentic Commerce Authority](13-agentic-commerce-authority-spec.md) | AP2/AIP-style signed delegation, payment-like authority scopes, and replay prevention | Watchlist. Useful as an authority-control pattern even if NexusNet never handles payments. |
| 14 | [Workstream Observability Surface](14-workstream-observability-surface-spec.md) | Local-first command center, AI-readiness scoring, and agent observability | Watchlist. Product-surface reference for Control Panel and development cockpit. |
| 15 | [Agent UI Protocols](15-agent-ui-protocols-spec.md) | AG-UI, A2UI, and UCP-style declarative/capability-negotiated surfaces | Watchlist. Useful for generated UI safety and Control Panel protocol boundaries. |
| 16 | [Terminal Bench Sandbox](16-terminal-bench-sandbox-spec.md) | Real terminal task harness with task tests, oracle solutions, and sandboxed execution | High. Strong fit for native expert execution and shell/code-change certification. |
| 17 | [AndroidWorld Mobile Agent](17-androidworld-mobile-agent-spec.md) | Dynamic Android emulator benchmark for mobile computer-control agents | High for mobile/edge aspirations. Use as VisualOps/mobile certification pattern. |
| 18 | [Tau Bench Customer Reliability](18-tau-bench-customer-reliability-spec.md) | Tool-agent-user conversations with policy rules and final database-state scoring | High. Excellent pattern for policy-compliant, multi-turn, state-changing tasks. |
| 19 | [Tau Knowledge And Voice](19-tau-knowledge-voice-spec.md) | Knowledge-grounded customer support and full-duplex voice-agent evaluation | High. Useful for RAG plus action, human-facing latency, and voice reliability gates. |
| 20 | [SABER Mutating Action Guard](20-saber-mutating-action-guard-spec.md) | Mutation-gated verification, targeted reflection, and context cleaning before state changes | Critical adjunct to shell/browser/MCP/file authority gates. |
| 21 | [Agent Memory Stack](21-agent-memory-stack-spec.md) | Memory survey, Hindsight, MemMachine, MemX, MemoryAgentBench, xMemory | High. Refines NexusNet memory/KAC into write-manage-read, evidence-preserving retrieval, and selective forgetting. |
| 22 | [AIRS Research Lifecycle](22-airs-research-lifecycle-spec.md) | Autonomous ML research tasks spanning idea generation, experiments, and refinement | Medium-high. Strong fit for research/dreaming lanes where objective metrics exist. |
| 23 | [OccuBench Professional Faults](23-occubench-professional-faults-spec.md) | Cross-industry professional task simulation with explicit/implicit fault injection | Medium-high. Useful for robustness and industry-specific expert lane scorecards. |
| 24 | [ASTRA Personal Context](24-astra-personal-context-spec.md) | Time-evolving personal context with multi-step tool action and argument-generation failures | Medium-high. Useful for consented personal-context memory and tool-argument validation. |
| 25 | [BrowserGym Web Agent Harness](25-browsergym-web-agent-harness-spec.md) | Unified browser-task harness across WebArena, WorkArena, VisualWebArena, AssistantBench, OpenApps, and related suites | High. Best fit as the BrowserOps certification spine. |
| 26 | [OSWorld Desktop Agent](26-osworld-desktop-agent-spec.md) | Real desktop/OS task harnesses with VM state, GUI actions, file I/O, and Windows task variants | High. Best fit as the DesktopOps/VisualOps sandbox model. |
| 27 | [SWE Bench Code Repair](27-swe-bench-code-repair-spec.md) | Real GitHub issue-to-patch tasks with Docker-backed tests, Verified, and Multimodal extensions | High. Core coding-lane certification reference. |
| 28 | [BFCL Tool Calling](28-bfcl-tool-calling-spec.md) | Function/tool-call accuracy, no-call decisions, multi-turn carryover, memory, search, and format sensitivity | High. Directly targets model-tool reliability before authority delegation. |
| 29 | [Frontier Research Engineering](29-frontier-research-engineering-spec.md) | MLE-bench, PaperBench, and RE-Bench style experiment/reproduction/rubric gates | Medium-high. Useful for research/dreaming lanes with objective artifacts. |
| 30 | [SWE Lancer Commercial Coding](30-swe-lancer-commercial-coding-spec.md) | Real freelance coding tasks and manager-style proposal selection | Medium-high. Strong commercial-readiness reference beyond tests alone. |
| 31 | [Inspect AI Evaluation Spine](31-inspect-ai-evaluation-spine-spec.md) | Task/dataset/solver/scorer/log framework for agent, tool, sandbox, and model evals | High. Strong reference for one NexusNet eval evidence model. |
| 32 | [Red Team Toolchain](32-red-team-toolchain-spec.md) | Promptfoo, PyRIT, and Garak style red-team cases for RAG, MCP, coding agents, sandbox escape, and exfiltration | Critical adjunct to every high-authority lane. |
| 33 | [OWASP Agentic Skill Risk](33-owasp-agentic-skill-risk-spec.md) | MCP, agentic skill, and behavior-layer risk taxonomy for tool and workflow governance | Critical for third-party skill, MCP, and protocol onboarding. |
| 34 | [ToolSandbox Stateful Tool Use](34-toolsandbox-stateful-tool-use-spec.md) | Stateful, conversational, interactive tool-use evaluation with hidden state and milestone checks | High. Bridges BFCL schema tests and real high-authority tools. |
| 35 | [EnterpriseOps Governed Operations](35-enterpriseops-governed-ops-spec.md) | Large enterprise-operation benchmark with policies, persistent state, infeasible tasks, and SQL verification | High. Direct pattern for governed business-workflow agents. |
| 36 | [ClawsBench Productivity Agent](36-clawsbench-productivity-agent-spec.md) | Mock Gmail, Calendar, Docs, Drive, and Slack services with task success and unsafe-action scoring | High. Direct pattern for productivity connector safety. |
| 37 | [MultiAgentBench Coordination](37-multiagentbench-coordination-spec.md) | Collaboration and competition benchmark for multi-agent topologies and milestone KPIs | Medium-high. Useful for Hive Mind coordination scorecards. |
| 38 | [Data Agent Enterprise Query](38-data-agent-enterprise-query-spec.md) | DataAgentBench, DS-Bench, and DSBench style enterprise-data and data-science tasks | High. Direct fit for DataOps, schema-linking, and analytic evidence gates. |
| 39 | [Enterprise Deep Research](39-enterprise-deep-research-spec.md) | DRBench and sensemaking benchmarks for multi-source public/private enterprise research | Medium-high. Useful for citation-grounded research artifacts. |
| 40 | [Durable Agent Orchestration](40-durable-agent-orchestration-spec.md) | LangGraph, Microsoft Agent Framework, and AutoGen migration lessons around durable runs, checkpoints, and replay | High. Direct fit for long-running NexusNet behavior loops. |
| 41 | [KV Cache Runtime Efficiency](41-kv-cache-runtime-efficiency-spec.md) | LMCache, vLLM, and SGLang style KV reuse, prefill caching, and runtime cache planning | High. Direct fit for long-context RAG and open-first runtime efficiency. |
| 42 | [Agent Observability Standards](42-agent-observability-standards-spec.md) | OpenTelemetry GenAI, OpenInference, Phoenix, AgentTrace, and AgentSight style trace schemas | High. Direct fit for Control Panel traces and incident replay. |
| 43 | [Artifact Provenance Supply Chain](43-artifact-provenance-supply-chain-spec.md) | SLSA, Sigstore, and in-toto provenance for model packs, skills, evals, and release artifacts | High. Direct fit for sellable packaging and buyer trust. |
| 44 | [Five Eyes Agentic Security](44-five-eyes-agentic-security-spec.md) | April/May 2026 joint government guidance for careful adoption of agentic AI services | Critical. Should become a baseline for high-authority NexusNet lanes. |
| 45 | [Policy As Code Action PDP](45-policy-as-code-action-pdp-spec.md) | OPA and Cedar style policy decision points for high-authority agent actions | High. Converts security guidance into enforceable runtime decisions. |
| 46 | [Agent Identity Delegation](46-agent-identity-delegation-spec.md) | SPIFFE/SPIRE, token exchange, proof-of-possession, and scoped authorization patterns | High. Direct fit for agent principal and delegated capability grants. |
| 47 | [Sandbox Isolation Tiering](47-sandbox-isolation-tiering-spec.md) | gVisor, Firecracker, Kata Containers, and E2B isolation tradeoffs | High. Direct fit for shell, code, browser, desktop, and experiment lanes. |
| 48 | [RAG Evaluation Harness](48-rag-evaluation-harness-spec.md) | Ragas, TruLens, DeepEval, and ARES style retrieval/generation quality checks | High. Direct fit for KAC and memory grounding gates. |
| 49 | [Context Compression Governor](49-context-compression-governor-spec.md) | LLMLingua, LongLLMLingua, SnapKV, and H2O style prompt and KV compression controls | Medium-high. Useful only with strict correctness gates. |
| 50 | [Model Eval Harness Federation](50-model-eval-harness-federation-spec.md) | OpenAI Evals, lm-eval-harness, LightEval, HELM, Inspect, and NexusNet custom suites | High. Direct fit for open-first model passports. |
| 51 | [Privacy Redaction Preflight](51-privacy-redaction-preflight-spec.md) | Presidio and guardrail-style PII gates before prompts, traces, memory, and release artifacts | High. Direct fit for privacy/shareability hardening. |
| 52 | [LLM Gateway Budget Control](52-llm-gateway-budget-control-spec.md) | LiteLLM, Langfuse, and Helicone style route, budget, fallback, and cost-control patterns | Medium-high. Useful if kept optional for local-only packaging. |
| 53 | [GraphRAG Knowledge Structure](53-graphrag-knowledge-structure-spec.md) | Microsoft GraphRAG, LightRAG, and HippoRAG style evidence graph retrieval | Medium-high. Useful for KAC if raw-source lineage remains dominant. |
| 54 | [AI BOM Supply Chain Graph](54-ai-bom-supply-chain-graph-spec.md) | CycloneDX, SPDX, OpenSSF Scorecard, and GUAC style component inventory and dependency graphing | High. Direct fit for buyer-safe NexusNet releases. |
| 55 | [Workflow Engine Substrate](55-workflow-engine-substrate-spec.md) | Temporal, Restate, Inngest, and Hatchet durable workflow patterns | Medium-high. Useful if NexusNet needs stronger idempotency and retry substrate. |
| 56 | [Prompt Governance Optimization](56-prompt-governance-optimization-spec.md) | Langfuse, DSPy, Promptfoo, and ChainForge style prompt versioning, evals, and promotion gates | Medium-high. Useful for controlled prompt evolution without silent production drift. |
| 57 | [Grammar Constrained Decoder Kernel](57-grammar-constrained-decoder-kernel-spec.md) | XGrammar, LMQL, Guidance, and constrained decoding as structural-output enforcement | High. Direct reliability primitive for tool plans, policy decisions, and memory writes. |
| 58 | [Parallel Tool DAG Compiler](58-parallel-tool-dag-compiler-spec.md) | LLMCompiler-style dependency-aware parallel tool execution | High. Direct latency and cost unlock for safe independent tool calls. |
| 59 | [Adaptive Reasoning Effort Router](59-adaptive-reasoning-effort-router-spec.md) | Ares-style per-step reasoning effort selection for multi-step agents | High. Hidden cost-quality lever for long agent trajectories. |
| 60 | [Reflective Text Optimization](60-reflective-text-optimization-spec.md) | GEPA and TextGrad style trace-driven prompt/component evolution | Medium-high. Powerful only if shadow-only with promotion gates. |
| 61 | [Agentic Context Playbook](61-agentic-context-playbook-spec.md) | ACE-style evolving playbooks from execution feedback | Medium-high. Useful for bounded self-improvement without weight updates. |
| 62 | [Object Capability Delegation](62-object-capability-delegation-spec.md) | UCAN and macaroons for attenuable, locally verifiable delegated authority | High. Stronger primitive than broad role permissions for agents. |
| 63 | [Hermetic Task Capsule](63-hermetic-task-capsule-spec.md) | Nix, Bazel, and Devbox style reproducible execution environments | High. Direct fit for code/eval/model-pack/release replayability. |
| 64 | [Local First CRDT State](64-local-first-crdt-state-spec.md) | Yjs, Automerge, ElectricSQL, and local-first sync for operator-owned state | Medium-high. Useful for offline review/control surfaces. |
| 65 | [Formal Workflow Model Checking](65-formal-workflow-model-checking-spec.md) | TLA+, Apalache, Alloy, and PlusCal style invariant checking | Medium-high. Best for high-risk authority workflows. |
| 66 | [Property Based Agent Testing](66-property-based-agent-testing-spec.md) | Hypothesis, fast-check, and stateful invariant generation for agent runs | High. Direct way to turn safety bugs into generated regressions. |
| 67 | [Content Addressed Evidence DAG](67-content-addressed-evidence-dag-spec.md) | IPFS/IPLD-style CIDs and Merkle DAGs for immutable evidence identity | High. Direct fit for trace, memory, eval, and release integrity. |
| 68 | [Speculative Decoding Runtime Stack](68-speculative-decoding-runtime-stack-spec.md) | vLLM, Medusa, EAGLE, and SpecInfer style faster generation paths | Medium-high. Runtime speed lever that needs workload-specific certification. |
| 69 | [Verifier Guided Search Controller](69-verifier-guided-search-controller-spec.md) | Reflexion, Tree of Thoughts, and LATS style search before execution | Medium-high. Useful for hard planning if bounded and verifier-gated. |
| 70 | [Learned Model Cascade Router](70-learned-model-cascade-router-spec.md) | RouteLLM, FrugalGPT, and LLMRouter style learned routing/cascades | Medium-high. Useful after deterministic open-first routing baseline. |
| 71 | [Data Model Lineage Ledger](71-data-model-lineage-ledger-spec.md) | OpenLineage, lakeFS, MLflow, and DataLad style lineage for data/model artifacts | High. Direct fit for candidate promotion and buyer-safe evidence. |
| 72 | [Effect Typed Authority Surface](72-effect-typed-authority-surface-spec.md) | Deno permissions, Unison abilities, and Koka effect types for explicit side effects | High. Deep control-plane primitive for every tool and skill. |
| 73 | [WASM Component Tool Sandbox](73-wasm-component-tool-sandbox-spec.md) | WebAssembly Component Model, WASI, and Wasmtime for typed, capability-limited tool capsules | High. Strong primitive for third-party tool containment and portable skill execution. |
| 74 | [Confidential AI Execution Envelope](74-confidential-ai-execution-envelope-spec.md) | Confidential Containers, enclave attestation, and encrypted model/input release gates | Watchlist. Useful for buyer or remote deployments, but local-first remains the default. |
| 75 | [Event Sourced Agent Trace Log](75-event-sourced-agent-trace-log-spec.md) | Append-only agent events with rebuildable projections | High. Direct fit for replayable Control Panel traces, memory lineage, and audit recovery. |
| 76 | [Feature Flagged Agent Rollout](76-feature-flagged-agent-rollout-spec.md) | OpenFeature-style behavior flags, hooks, targeting, and kill switches | High. Needed for staged prompt, router, policy, and tool-behavior promotion. |
| 77 | [Proof Carrying Action Guard](77-proof-carrying-action-guard-spec.md) | Lean, Dafny, F*, and Why3 style checkable obligations before high-risk actions | Medium-high. Powerful for narrow invariants; too heavy for general agent behavior. |
| 78 | [Verified Semantic Cache](78-verified-semantic-cache-spec.md) | GPTCache, RedisVL, and LangChain semantic caching with state and privacy verification | High. Cost/latency diamond if cache hits are treated as gated evidence, not truth. |
| 79 | [Private Federated Learning](79-private-federated-learning-spec.md) | Flower, NVIDIA FLARE, OpenDP, and TFF style local learning with aggregation/privacy controls | Watchlist. Valuable only for opt-in, narrow, poisoning-resistant learning signals. |
| 80 | [Syscall Runtime Sensor](80-syscall-runtime-sensor-spec.md) | Tetragon, Falco, and eBPF-style observed-effects tracing | High. Bridges declared tool authority with actual runtime behavior. |
| 81 | [Agent Chaos Failure Injection](81-agent-chaos-failure-injection-spec.md) | Chaos Mesh, LitmusChaos, and chaos-engineering principles for agent reliability | High. Turns model/tool/browser failures into replayable recovery gates. |
| 82 | [Fine Grained Authz Graph](82-fine-grained-authz-graph-spec.md) | OpenFGA and Zanzibar-style relationship authorization for agent/resource permissions | High. Stronger authority primitive than broad roles for agent delegation. |
| 83 | [Secure Update Trust Root](83-secure-update-trust-root-spec.md) | TUF, Notary, and Sigstore/Rekor for signed, rollback-protected artifact updates | High. Direct fit for model packs, skills, plugins, and commercial release trust. |
| 84 | [Reversible Patch Transaction Log](84-reversible-patch-transaction-log-spec.md) | JSON Patch, SQLite changesets, and inverse patches for inspectable rollback-capable state changes | High. Direct fit for memory, policy, flag, and tool-manifest mutation safety. |
| 85 | [Deterministic Starlark Plugin DSL](85-deterministic-starlark-plugin-dsl-spec.md) | Starlark-style deterministic, hermetic extension language for plugins and manifests | High. Useful for safe plugin/rule authoring without ambient authority. |
| 86 | [CUE Constraint Config Kernel](86-cue-constraint-config-kernel-spec.md) | CUE-style unified constraints for config, schema, policy, and code generation | High. Direct fit for manifest validation and Control Panel/schema drift control. |
| 87 | [Hardened JS Ocap Compartment](87-hardened-js-ocap-compartment-spec.md) | SES/HardenedJS/LavaMoat object-capability compartments for JavaScript plugins | High. Strong fit for UI/plugin containment and supply-chain hardening. |
| 88 | [Biscuit Datalog Capability Token](88-biscuit-datalog-capability-token-spec.md) | Biscuit-style attenuable Datalog tokens for offline delegated authority | High. Strong agent-grant primitive beyond broad session roles. |
| 89 | [SCITT Supply Chain Receipt](89-scitt-supply-chain-receipt-spec.md) | IETF SCITT signed supply-chain statements and transparency receipts | High. Direct fit for eval, release, model-pack, and evidence statement receipts. |
| 90 | [zkVM Proof Of Execution](90-zkvm-proof-of-execution-spec.md) | RISC Zero/SP1 style receipts proving narrow verifier execution | Watchlist. Powerful for tiny kernels, too heavy for broad agent workflows today. |
| 91 | [Private Compute Crypto Lane](91-private-compute-crypto-lane-spec.md) | OpenFHE and MP-SPDZ style private aggregate/compare computations | Watchlist. Useful only for narrow privacy-preserving signals with crypto review. |
| 92 | [Deterministic Replay Snapshot](92-deterministic-replay-snapshot-spec.md) | rr and CRIU style record/replay and checkpoint/restore for agent incidents | High. Turns flaky native/tool failures into replayable evidence. |
| 93 | [Reproducible Rebuilder Network](93-reproducible-rebuilder-network-spec.md) | Reproducible Builds, OSS Rebuild, NixOS, and Guix independent rebuild evidence | High. Direct fit for buyer-verifiable NexusNet releases and helper binaries. |
| 94 | [Landlock Seccomp Micro Sandbox](94-landlock-seccomp-micro-sandbox-spec.md) | Linux Landlock and seccomp for lightweight local process containment | High. Practical local coding-agent sandbox primitive where supported. |
| 95 | [Verifiable Agent Credential Passport](95-verifiable-agent-credential-passport-spec.md) | W3C VC/DID style portable signed claims for agents, tools, evals, and deployments | Medium-high. Useful for buyer trust if bound to real evidence digests. |
| 96 | [Static Taint Flow Gate](96-static-taint-flow-gate-spec.md) | CodeQL and Semgrep taint/data-flow analysis for privacy and authority leaks | High. Direct fit for generated-code, plugin, and adapter promotion gates. |
| 97 | [Verified Isolation Kernel](97-verified-isolation-kernel-spec.md) | seL4-style verified microkernel isolation, capabilities, and TCB budgeting | Watchlist. Deep appliance/embedded primitive; use as architecture discipline first. |
| 98 | [Capability Hardware Rights](98-capability-hardware-rights-spec.md) | CHERI and Capsicum style hardware/OS capability rights for native helpers | Watchlist. Long-horizon but powerful for native helper and edge-runtime safety. |
| 99 | [Flight Software Command Telemetry Bus](99-flight-software-command-telemetry-bus-spec.md) | NASA cFS and F Prime command, telemetry, health, and limit-checking patterns | High. Strong mental model for NexusNet Control Panel operations beyond chat. |
| 100 | [Deterministic Simulation Failure Foundry](100-deterministic-simulation-failure-foundry-spec.md) | FoundationDB simulation, Jepsen, libFuzzer, and AFL++ style adversarial deterministic testing | High. One of the strongest ways to find rare orchestration failures before users do. |
| 101 | [Runtime Monitor Synthesis](101-runtime-monitor-synthesis-spec.md) | NASA Ogma and Copilot-style generation of runtime monitors from properties | High. Converts policy/invariants into live tripwires for agent runs. |
| 102 | [Assurance Case Evidence Graph](102-assurance-case-evidence-graph-spec.md) | OMG SACM-style claims, arguments, assumptions, and evidence | High. Turns NexusNet trust claims into auditable buyer/operator evidence. |
| 103 | [Scientific Provenance Crate](103-scientific-provenance-crate-spec.md) | W3C PROV and RO-Crate packaging for research/eval/memory artifacts | High. Strong fit for durable, source-linked NexusNet evidence exports. |
| 104 | [Content Credential Evidence Layer](104-content-credential-evidence-layer-spec.md) | C2PA Content Credentials for media, screenshots, generated artifacts, and visual evidence | High. Useful for shareable visual proof and artifact authenticity. |
| 105 | [Capability RPC Object Fabric](105-capability-rpc-object-fabric-spec.md) | Cap'n Proto and Fuchsia-style object capabilities and routed component authority | High. Stronger internal service model than global singletons and broad REST endpoints. |
| 106 | [Trusted Time Attestation Receipts](106-trusted-time-attestation-receipts-spec.md) | RFC 3161, Roughtime, OpenTimestamps, RATS, and EAT evidence timing/attestation | High. Direct fit for audit, release, eval, approval, and provenance receipts. |
| 107 | [Digital Twin Simulation Gate](107-digital-twin-simulation-gate-spec.md) | FMI, Eclipse Ditto, and ASAM OSI style simulation-before-action gates | Medium-high. Powerful where NexusNet can model a target environment before mutation. |
| 108 | [Incremental Dataflow Projection Engine](108-incremental-dataflow-projection-engine-spec.md) | Differential Dataflow and Materialize-style maintained projections over changing evidence | High. Direct fit for scalable Control Panel, memory, trace, and assurance views. |
| 109 | [Human Brain Atlas Connectome Ladder](109-human-brain-atlas-connectome-ladder-spec.md) | HCP, BICAN, Allen Brain Atlas, and EBRAINS multiscale brain mapping | High. Use as architecture atlas discipline, not as an upload claim. |
| 110 | [Synapse Connectome Simulation Ladder](110-synapse-connectome-simulation-ladder-spec.md) | FlyWire, OpenWorm, and NeuroML structure-to-dynamics-to-behavior ladder | High. Directly reframes NexusNet graphs as executable circuits with perturbation tests. |
| 111 | [Whole Brain Emulation Boundary](111-whole-brain-emulation-boundary-spec.md) | Whole Brain Emulation roadmap as strict levels and success criteria | Watchlist. Important boundary setter; no consciousness-uploading claim. |
| 112 | [Organoid Intelligence Ethics](112-organoid-intelligence-ethics-spec.md) | Organoid intelligence, DishBrain, and closed-loop wetware learning ethics | Watchlist. Transfer only closed-loop learning patterns; no biological protocols. |
| 113 | [Neuromorphic Event Driven Substrate](113-neuromorphic-event-driven-substrate-spec.md) | Loihi, SpiNNaker, and Nengo sparse event-driven computation | High. Strong fit for sparse NexusNet routing and local plasticity metadata. |
| 114 | [Neocortical Microcircuit Reconstruction](114-neocortical-microcircuit-reconstruction-spec.md) | Blue Brain digital reconstruction and simulation of cortical microcircuits | High. Good pattern for small executable NexusNet circuits and ablation tests. |
| 115 | [Global Workspace Consciousness Router](115-global-workspace-consciousness-router-spec.md) | Global neuronal workspace and IIT comparison as broadcast/integration design pressure | Medium-high. Useful router idea, but not a consciousness claim. |
| 116 | [Active Inference Homeostatic Agent](116-active-inference-homeostatic-agent-spec.md) | Free Energy Principle, predictive coding, and active inference as viability control | High. Strong fit for self-stabilizing NexusNet state without self-preservation drift. |
| 117 | [Hippocampal Replay Consolidation Engine](117-hippocampal-replay-consolidation-engine-spec.md) | Memory engrams, replay, sharp-wave ripples, and brain-inspired continual learning | High. Direct fit for offline NexusNet sleep/consolidation loops. |
| 118 | [Bioelectric Morphogenesis Growth Engine](118-bioelectric-morphogenesis-growth-engine-spec.md) | Levin Lab bioelectricity, morphogenesis, and collective intelligence of cells | Medium-high. Best computational transfer for controlled growth and repair. |
| 119 | [Developmental Open Ended AI Embryo](119-developmental-open-ended-ai-embryo-spec.md) | Turing child machine, developmental robotics, POET, and open-ended evolution | High. Core grounded version of an artificial embryo that grows capabilities under gates. |
| 120 | [Ancient Memory Palace Spatial KAC](120-ancient-memory-palace-spatial-kac-spec.md) | Method of loci and art-of-memory traditions as spatial retrieval architecture | Medium. Useful inspiration for KAC navigation if source-grounded. |
| 121 | [Lullian Combinatorial Search Engine](121-lullian-combinatorial-search-engine-spec.md) | Ramon Llull's Ars and controlled symbolic recombination | Medium-high. Useful for systematic ideation and stepping-stone generation. |
| 122 | [Archaic Symbolic Change Calculus](122-archaic-symbolic-change-calculus-spec.md) | I Ching and historical symbolic change systems as bounded state-machine inspiration | Watchlist. Inspiration only; never evidence of lost technology. |
| 123 | [Cortical Reference Frame Swarm](123-cortical-reference-frame-swarm-spec.md) | Thousand Brains, TEM, and predictive maps as many local models plus consensus | High. Missing architectural bridge from Hive Mind to brain-like local world models. |
| 124 | [Latent World Model Imagination Engine](124-latent-world-model-imagination-engine-spec.md) | World Models, Dreamer, and V-JEPA style latent prediction and rollout | High. Lets NexusNet dream/simulate futures before acting. |
| 125 | [Continuous Self Model Body Schema](125-continuous-self-model-body-schema-spec.md) | Self-modeling robots and body-schema learning transferred to tool/model/memory capability maps | High. Gives NexusNet operational self-knowledge without consciousness claims. |
| 126 | [Causal Representation Intervention Cortex](126-causal-representation-intervention-cortex-spec.md) | Causal representation learning and CausalWorld-style safe interventions | High. Turns associations into tested mechanisms and counterfactuals. |
| 127 | [GFlowNet Diverse Thought Factory](127-gflownet-diverse-thought-factory-spec.md) | GFlowNets for diverse high-reward compositional candidate generation | High. Preserves non-obvious stepping stones instead of hill-climbing one plan. |
| 128 | [Intrinsic Motivation Empowerment Drive](128-intrinsic-motivation-empowerment-drive-spec.md) | Learning-progress curiosity and empowerment as bounded developmental drives | High. Selects the learnable frontier while avoiding uncontrolled autonomy. |
| 129 | [Semantic Pointer Binding Substrate](129-semantic-pointer-binding-substrate-spec.md) | Spaun, semantic pointers, and hyperdimensional/vector-symbolic binding | Medium-high. Missing middle layer between embeddings and symbolic graphs. |
| 130 | [Neural Cellular Self Organizing Growth](130-neural-cellular-self-organizing-growth-spec.md) | Growing Neural Cellular Automata as computational growth, persistence, and regeneration | High. Concrete embryo/growth primitive for metadata/circuit structures. |
| 131 | [Liquid Dynamical Cortex](131-liquid-dynamical-cortex-spec.md) | Liquid time-constant and continuous-time neural controllers | Medium-high. Useful for narrow adaptive telemetry and homeostatic control loops. |
| 132 | [Autopoietic Viability Kernel](132-autopoietic-viability-kernel-spec.md) | Autopoiesis/enactive autonomy as boundary-maintaining software viability | Medium-high. Useful if strictly bounded away from life/consciousness claims. |
| 133 | [Open Ended Self Improvement Archive](133-open-ended-self-improvement-archive-spec.md) | Darwin Godel Machine, AlphaEvolve, and Godel-machine lineage with empirical gates | High. Makes self-improvement archival, evaluated, and review-gated. |
| 134 | [Final Missing Piece Developmental Cortex](134-final-missing-piece-developmental-cortex-spec.md) | Cross-spec synthesis: self-model, world model, causal model, developmental growth, and promotion tribunal | Critical. The final P0 target for making NexusNet a governed growing intelligence substrate. |

## Source Classes Covered

- Fresh papers and benchmark pages: arXiv, Hugging Face paper pages, and source repositories from 2024-May 2026, prioritizing recent revisions and still-active benchmark suites.
- Protocol and observability specs: MCP, A2A, AOP, OpenTelemetry GenAI, AP2/AIP, AG-UI, A2UI, UCP.
- Security research: CSA, OX Security, MCP protocol threat modeling, AgentDyn, AgentHazard, OS-BLIND.
- Open-source and architecture references: OpenHands, OpenDev, Sema Code, OpenEvolve-adjacent patterns.
- Open-first model/runtime sources: Qwen3-Coder-Next, Gemma 4, LFM2.5-350M, LiteRT-LM, speculative decoding.
- Browser/desktop/code harnesses: BrowserGym, OSWorld, Windows Agent Arena, SWE-bench, BFCL, SWE-Lancer.
- Eval and red-team infrastructure: Inspect AI, Promptfoo, PyRIT, Garak, OWASP MCP Top 10, OWASP Agentic Skills Top 10.
- Stateful enterprise and productivity benchmarks: ToolSandbox, EnterpriseOps-Gym, ClawsBench, DataAgentBench, DRBench.
- Agent orchestration and runtime infrastructure: LangGraph, Microsoft Agent Framework, AutoGen, LMCache, vLLM, SGLang.
- Observability, provenance, and governance standards: OpenTelemetry GenAI, OpenInference, SLSA, Sigstore, in-toto, NIST AI RMF, and Five Eyes agentic AI guidance.
- Policy, identity, and sandbox primitives: OPA, Cedar, SPIFFE, SPIRE, OAuth RFCs, gVisor, Firecracker, Kata Containers, E2B.
- RAG, model, context, and prompt evaluation infrastructure: Ragas, TruLens, DeepEval, ARES, OpenAI Evals, lm-eval-harness, LightEval, HELM, Langfuse, DSPy, Promptfoo, ChainForge.
- Privacy, gateway, graph, BOM, and workflow-control systems: Presidio, LiteLLM, Helicone, GraphRAG, LightRAG, HippoRAG, CycloneDX, SPDX, OpenSSF Scorecard, GUAC, Temporal, Restate, Inngest, Hatchet.
- Deeper systems primitives: XGrammar, LMQL, Guidance, LLMCompiler, Ares, GEPA, TextGrad, ACE, UCAN, macaroons, Nix, Bazel, Yjs, Automerge, TLA+, Apalache, Alloy, Hypothesis, fast-check, IPFS/IPLD, vLLM speculative decoding, Medusa, EAGLE, Reflexion, Tree of Thoughts, LATS, RouteLLM, FrugalGPT, OpenLineage, MLflow, Deno permissions, Unison abilities, and Koka effect types.
- Hardening and rollout primitives: WebAssembly Component Model, WASI, Wasmtime, Confidential Containers, OpenFeature, EventStoreDB/Kurrent, CloudEvents, NATS JetStream, Lean, Dafny, F*, Why3, GPTCache, RedisVL, Flower, NVIDIA FLARE, OpenDP, TensorFlow Federated, Tetragon, Falco, Inspektor Gadget, Chaos Mesh, LitmusChaos, OpenFGA, TUF, Notary, Sigstore/Rekor, JSON Patch, SQLite session changesets, and Immer patches.
- Obscure governance and proof primitives: Starlark, CUE, SES/HardenedJS, LavaMoat, Biscuit tokens, SCITT, RISC Zero, SP1, OpenFHE, MP-SPDZ, rr, CRIU, Reproducible Builds, OSS Rebuild, Guix, Landlock, seccomp, W3C Verifiable Credentials, W3C DID Core, CodeQL data flow, and Semgrep taint mode.
- High-assurance and out-of-domain primitives: seL4, CHERI, Capsicum, NASA cFS, NASA F Prime, FoundationDB deterministic simulation, Jepsen, libFuzzer, AFL++, NASA Ogma, Copilot runtime verification, OMG SACM, W3C PROV, RO-Crate, C2PA Content Credentials, Cap'n Proto RPC, Fuchsia component capabilities, RFC 3161, Roughtime, OpenTimestamps, RATS, EAT, FMI, Eclipse Ditto, ASAM OSI, Differential Dataflow, and Materialize incremental computation.
- Neuroscience, development, and consciousness boundaries: Human Connectome Project, BRAIN Initiative Cell Atlas Network, Allen Brain Atlas, EBRAINS, FlyWire, OpenWorm, NeuroML, Whole Brain Emulation roadmap, organoid intelligence, DishBrain, Loihi, SpiNNaker, Nengo, Blue Brain, global neuronal workspace, IIT, active inference, memory engrams, hippocampal replay, Levin Lab bioelectricity, developmental robotics, POET, and open-ended evolution.
- Historical cognition and archaic inspiration lanes: method of loci, art of memory, Ramon Llull's Ars, combinatorial logic, I Ching scholarship, and symbolic change systems, all explicitly kept as inspiration rather than factual evidence for advanced lost civilizations.
- Final missing-piece sources: Thousand Brains Project, Tolman-Eichenbaum Machine, World Models, Dreamer, V-JEPA, continuous self-modeling robots, causal representation learning, CausalWorld, GFlowNets, intrinsic motivation systems, empowerment, Spaun, semantic pointers, hyperdimensional computing, Growing Neural Cellular Automata, liquid neural networks, autopoiesis/enactive autonomy, Darwin Godel Machine, Godel Machines, and AlphaEvolve.

## Common Promotion Gates

- Keep every online finding refs-only until at least one code-backed NexusNet consumer exists.
- Separate source status from confidence: a primary source can still describe a target that is not safe to promote.
- Prefer reproducible benchmarks, datasets, code, specs, and model cards over social posts or demo claims.
- Browser, desktop, payment, shell, MCP, and code-writing authority must require explicit consent, scoped capability records, replayable traces, and revocation.
- Self-improvement ideas remain shadow-only: lineage, scoring, suggestions, and review are allowed; production self-mutation is not.
- Model/runtime candidates need license, hardware fit, quantization path, benchmark scope, and local verification before becoming recommended routes.

## Follow-Up Queue

1. Pull repos/datasets for the P0/P1 benchmark targets and record exact licenses, dataset formats, and runnable harness requirements.
2. Add a source-status ledger row for each target in the broader NexusNet candidate dossier if this packet is accepted.
3. Convert only the highest-leverage implementation candidates after code-level mapping: AgentFloor routing, computer-use safety reliability, MCP security red-team gates, Terminal-Bench shell certification, tau/SABER mutating-action gates, BFCL tool-call certification, BrowserOps/DesktopOps sandboxing, and memory-stack evidence preservation.
4. Check whether Inspect-style logging can normalize results from Terminal-Bench, SWE-bench, BFCL, BrowserGym, OSWorld, and local NexusNet release gates into one evidence store.
5. Add a security-baseline mapping pass for ranks 32, 33, 43, and 44 before implementing any new connector, MCP, browser, shell, or desktop authority.
6. Add a runtime-efficiency mapping pass for rank 41 against NexusNet's local/open runtime stack before recommending any KV-cache persistence behavior.
7. Add a control-plane mapping pass for ranks 45, 46, 47, 51, and 54 before promoting any high-authority tool or release artifact.
8. Add a quality-evidence mapping pass for ranks 48, 50, 53, and 56 before expanding KAC, prompt, and model-route automation.
9. Treat ranks 57, 58, 59, 62, 63, 66, 67, 71, 72, 73, 75, 77, 80, 82, 83, 84, 85, 86, 87, 88, 89, 92, 93, 94, and 96 as the current "diamond" primitive set because they can compound across multiple NexusNet lanes.
10. Keep ranks 60, 61, and 69 shadow-only until policy, lineage, eval, and rollback gates exist; these are powerful self-improvement primitives but also the easiest to let drift.
11. Map ranks 73, 75, 80, 82, 83, and 84 together as one authority-integrity spine: typed tool capsules, append-only events, observed effects, relationship permissions, signed updates, and reversible state changes.
12. Map ranks 85, 86, 87, 88, 89, 92, 93, 94, and 96 as the new "abyss spine": deterministic rule evaluation, constraint validation, ocap plugin compartments, attenuable tokens, signed receipts, replayable incidents, reproducible builds, micro-sandboxing, and taint-flow promotion gates.
13. Map ranks 99, 100, 101, 102, 103, 104, 105, 106, and 108 as the "deep ops spine": command/telemetry bus, deterministic failure foundry, runtime monitor generation, assurance cases, provenance crates, media credentials, capability RPC, trusted time receipts, and maintained evidence projections.
14. Keep ranks 97, 98, and 107 as high-upside long-horizon transfer targets: verified kernels, capability hardware, and digital twins are powerful but should not drive near-term implementation until the live NexusNet deployment profile needs them.
15. Map ranks 109, 110, 113, 114, 116, 117, 118, and 119 as the "neural growth spine": multiscale atlas, executable connectome circuits, sparse event substrate, microcircuit experiments, homeostatic active inference, sleep-like consolidation, morphogenetic repair, and developmental open-ended growth.
16. Keep ranks 111, 112, 115, 120, 121, and 122 behind strict language boundaries: no consciousness-uploading claims, no wetware protocols, no consciousness assertions, and no advanced-lost-civilization evidence claims without independent source support.
17. Treat rank 134 as the final P0 synthesis target: a governed developmental cortex combining self-model, world model, causal model, intrinsic motivation, sleep consolidation, growth archive, and promotion tribunal.
18. Convert ranks 123, 124, 125, 126, 127, 128, 130, and 133 into the first implementation plan before adding any more research-only candidates.
