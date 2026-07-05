# Cluster 9 Broad Model Teacher Research - 2026-07-04

Status: live research draft, not final approved roster

Purpose: widen Cluster 9 teacher-council research beyond the current NexusNet live registry before finalizing teacher pairings for the Root NexusBrain, O-level Orchestrators, Assistant Orchestrators, Experts, core nodes, birth/merge/split flows, dream review, and high-risk domain specialists.

This document preserves research findings for discussion. It does not replace `nexusnet/teachers/teacher_registry_v2026_live.yaml`, `docs/NEXUSNET_TEACHER_PAIRING_MATRIX_2026-05-04.md`, or any locked canon until the user approves a final ruling and the registry is updated with gates.

## Ground Rules

- Every Orchestrator, Assistant Orchestrator, Expert, core node, temporary child, merged brain, split brain, and promoted expert needs two or more teachers before distillation or birth verification can be treated as legitimate.
- More than two teachers are required for high-risk domains: medicine, holistic/integrative medicine, legal, finance, crypto, security, mental health, governance, quantum systems, and runtime self-modification.
- Open-weight or distillation-approved models can become teacher candidates after exact model, license, hardware, cost, privacy, safety, and benchmark review.
- Closed/API frontier models may be used as external evaluators or council reviewers only if their terms allow the intended use. They are not default distillation teachers.
- Benchmarks, datasets, proof assistants, security tools, and deterministic validators are not teachers by themselves. They are evidence gates.
- Model-card claims are not enough for birth or promotion. NexusNet needs local evals, task replay, source review, and rollback proof.

## Corrected Open-World Domain Atlas

Accepted correction: the Cluster 9 roster cannot be a closed list of the areas already named in this draft. NexusNet needs an open-world O/AO/Expert domain atlas where every known domain, subdomain, workflow, risk surface, and newly discovered problem area can receive a passport, teacher panel, eval gate, and lifecycle state.

The model roster is only one ingredient. The native object is the domain passport plus its teacher council. A model may teach many domains, and a domain may require many models, validators, datasets, tools, and human/governance gates.

### ExpertDomainPassport

Every domain, subdomain, AO family, Orchestrator plane, expert lane, child brain, merged expert, or split expert should be tracked with a passport before it can become part of production routing.

Required fields:

- `domain_id`: stable machine id, such as `medical.clinical.pharmacy` or `runtime.inference.quantization`.
- `display_name`: human-facing name.
- `scope`: what the domain owns and what it does not own.
- `parent_o`: owning Orchestrator plane.
- `owner_aos`: one or more Assistant Orchestrators responsible for operation, evals, and escalation.
- `expert_lanes`: existing, proposed, temporary, merged, split, retired, and archived experts.
- `teacher_panel`: at least two active teacher candidates, plus critic/verifier/eval sources.
- `risk_tier`: low, medium, high, protected, or forbidden.
- `license_status`: approved, gated, commercial-review, research-only, blocked, or unknown.
- `source_status`: source-confirmed, source-refresh-needed, manual/gated, stale, failed, or internal-placeholder.
- `eval_pack`: benchmarks, replay tasks, validators, test fixtures, and acceptance thresholds.
- `runtime_pack`: local, remote, edge, mobile, browser, GPU, CPU, quantized, or tool-only execution constraints.
- `privacy_boundary`: what data can be seen, retained, federated, distilled, or exported.
- `promotion_state`: seed, researched, teacher-paired, eval-ready, shadow, promoted, merged, split, retired, archived.
- `created_from`: user request, live-problem gap, dream proposal, eval failure, source refresh, assimilation review, or operator decision.

### Missing-Domain Birth Rule

During a live problem, if NexusNet encounters a domain that is not owned by an existing Expert, AO, or Orchestrator, it must not force-fit the task into the nearest existing lane. It should:

1. Create a temporary `ExpertDomainPassport`.
2. Assign the nearest parent O and provisional owner AO.
3. Search for teacher candidates, validators, benchmarks, and source material.
4. Route the work through a temporary child expert in shadow mode.
5. Compare the child against parent experts and teacher panels.
6. Promote, merge, split, archive, or reject the child only after eval, critique, rollback, and governance gates pass.

### Orchestrator Planes

These O planes are architectural coverage areas, not final class names. More O planes can be created or merged when the mother brain proves that a durable coordination layer is needed.

| O plane | Owns |
| --- | --- |
| Root NexusBrain / Mother Brain O | global coordination, final arbitration, hive ownership, teacher council escalation, protected-state authority |
| Governance And Authority O | policy, approvals, rollback, operator authority, human gates, promotion/retirement authority |
| Safety And Risk O | high-risk classification, refusal/escalation policy, medical/legal/finance/mental-health safeguards |
| Security And Isolation O | threat modeling, prompt injection, tool containment, supply chain, permissions, sandbox policy |
| Planning And Strategy O | task decomposition, dependency planning, long-horizon strategy, resource allocation |
| Research And Knowledge O | source discovery, literature review, contradiction tracking, assimilation research, evidence synthesis |
| Memory And Temporal Context O | episodic/semantic memory, temporal truth, provenance, context compression, history repair |
| Execution And Build O | coding, tools, implementation loops, artifact construction, test/build execution |
| Runtime And Inference O | model serving, inference engines, routing, quantization, cache, fallback, hardware/runtime passports |
| Training And Teacher Council O | teacher selection, distillation, curriculum, expert birth verification, model assimilation gates |
| Dream And World Model O | recursive dreaming, world models, simulations, counterfactuals, high-temperature proposal generation |
| Evaluation And Observability O | evals, judges, benchmarks, scorecards, traces, proofpacks, regression gates |
| Federation And Hive O | multi-node hive behavior, sanitized sharing, trust scoring, poisoning checks, mother-brain ownership |
| Data And Knowledge Forge O | ingestion, schemas, databases, graphs, vectors, retrieval, document intelligence |
| Product And Operator Experience O | cockpit UX, workflows, node UI, visual proof surfaces, operator controls, end-user ergonomics |
| Infrastructure And Platform O | cloud, OS, networking, storage, deployments, service reliability, CI/CD |
| Hardware, Edge, And Mobile O | local devices, companion app, edge inference, sensors, thermal limits, portable runtimes |
| Multimodal Perception O | vision, audio, video, OCR, documents, GUI, speech, sensor fusion |
| Business And Operations O | product, sales, marketing, support, HR, finance ops, logistics, procurement |
| Domain Mission O | durable mission-specific expert groups, such as medicine, law, finance, science, education, robotics |
| Compliance And Legal O | contracts, regulations, jurisdiction, privacy law, audit trails, accessibility law |
| Finance And Economics O | accounting, tax, markets, crypto, macroeconomics, risk, fraud, insurance |
| Health And Human Care O | medical, mental health, wellness, nutrition, holistic/integrative review, clinical safety gates |
| Science And Engineering O | math, physics, chemistry, biology, quantum, materials, aerospace, energy, manufacturing |
| Human Communication O | language, education, tutoring, writing, negotiation, culture, accessibility, social context |

### Assistant Orchestrator Families

AO families are operational owners below O planes. They can be instantiated broadly or narrowly depending on the problem and runtime evidence.

| AO family | Candidate AOs |
| --- | --- |
| Planning and routing | PlanningAO, StrategyAO, TaskDecompositionAO, RouteSelectionAO, BudgetAO, ConstraintAO, ConsequenceAO |
| Coding and build | CodingAO, BuilderAO, RefactorAO, TestAO, DebuggingAO, DevOpsAO, CIRepairAO, ReleaseEngineeringAO |
| Tools and workflows | ToolsmithAO, ProtocolAO, ToolCallingAO, SkillsAO, WorkflowAO, NodeUXAO, AutomationAO, ConnectorAO |
| Runtime and inference | RuntimeAO, InferenceOptimizationAO, ServingAO, QuantizationAO, KernelLabAO, CacheAO, SpeculativeDecodingAO, StructuredOutputAO |
| Hardware and edge | HardwareMonitorAO, EdgeInferenceAO, MobileCompanionAO, BrowserRuntimeAO, SensorAO, ThermalAO, OfflineModeAO |
| Data and knowledge | DataIngestAO, SchemaAO, KnowledgeGraphAO, RetrievalAO, CitationAO, DocumentIntelligenceAO, ProvenanceAO, TemporalTruthAO |
| Memory and context | MemoryAO, ContextCompilerAO, CompressionAO, ReplayAO, HistorianAO, ForgettingAO, PrivacyMemoryAO |
| Research and assimilation | ResearchAO, LiteratureReviewAO, SourceHealthAO, AssimilationResearchAO, ModelRadarAO, StandardsAO |
| Evals and evidence | EvalsAO, BenchmarkAO, JudgeCalibrationAO, RegressionAO, TraceAO, ProofpackAO, ScorecardAO |
| Governance and safety | GovernanceAO, SafetyAO, PolicyAO, HumanApprovalAO, RollbackAO, MedicalSafetyAO, LegalSafetyAO, FinanceRiskAO |
| Security and privacy | SecurityAO, RedTeamAO, SupplyChainAO, SecretsAO, IdentityAO, PrivacyAO, SandboxAO, MalwareAnalysisAO |
| Dream and evolution | DreamAO, DreamReviewerAO, WorldModelAO, SimulationAO, SelfTrainingAO, ExpertBirthAO, MergeSplitRetireAO, MutationReviewAO |
| Federation and hive | FederationAO, TrustScoringAO, PoisoningDetectionAO, SecureAggregationAO, PeerReviewAO, HiveSyncAO |
| Multimodal | VisionAO, AudioAO, VideoAO, SpeechAO, OCRAO, DocumentLayoutAO, GUIUnderstandingAO, SensorFusionAO |
| Product and operator UX | ProductAO, VisualOpsAO, CockpitAO, UXResearchAO, AccessibilityAO, SupportAO, PackagingAO |
| Business operations | BusinessOpsAO, SalesAO, MarketingAO, CustomerSuccessAO, ProcurementAO, LogisticsAO, HRAO, AccountingAO |
| Domain specialists | MedicalAO, LegalAO, FinanceAO, CryptoAO, QuantumAO, ScienceAO, RoboticsAO, EducationAO, RealEstateAO, TaxAO |

### Expert Domain Coverage Map

This map is intentionally broad and non-exhaustive. Any row can split into many child passports and experts.

| Domain group | Expert lanes to support |
| --- | --- |
| NexusNet-native cognition | Mother Brain Coordination, Teacher Council, Expert Birth, Expert Merge/Split/Retire, Recursive Dreamer, Dream Reviewer, World Model, Memory Weaver, Critic Historian, Intent Mapper, Router, Meta Reasoner |
| Software engineering | Coding, architecture, debugging, testing, refactoring, DevOps, SRE, CI/CD, API design, web, mobile, desktop, embedded, games, compilers, interpreters, operating systems, drivers, databases, distributed systems |
| AI/ML engineering | LLMs, multimodal AI, agents, RL, world models, training, fine-tuning, synthetic data, evals, alignment, prompt/program synthesis, inference optimization, quantization, model compression, model security |
| Data systems | data engineering, ETL, analytics, BI, data governance, schemas, SQL, graph databases, vector databases, search, RAG, streaming, warehouses, lakehouses, provenance |
| Security | application security, cloud security, network security, cryptography, identity, privacy, red-team review, incident response, forensics, supply chain, SBOM/AI-BOM, secure coding, vulnerability management |
| Medical and health | clinical medicine, triage support, pharmacy, lab interpretation, radiology, pathology, genomics, public health, epidemiology, medical research, nutrition, fitness, rehabilitation, mental health, clinical safety review |
| Holistic and integrative health | integrative medicine, complementary medicine evidence review, herbal/supplement review, TCM, Ayurveda, lifestyle medicine, sleep, stress, wellness coaching, contraindication checking |
| Legal and compliance | legal research, contracts, IP, employment, privacy, health law, finance law, tax law, accessibility, regulatory compliance, litigation support, jurisdiction-aware citation, policy drafting |
| Finance and economics | accounting, tax, personal finance, corporate finance, markets, portfolio risk, trading simulation, crypto, DeFi, tokenomics, fraud, insurance, actuarial science, macroeconomics, real estate finance |
| Crypto and decentralized systems | blockchain protocols, smart contracts, wallet/security UX, DeFi risk, token economics, consensus, on-chain analytics, crypto compliance, exploit review, custody models |
| Mathematics and formal methods | pure math, applied math, statistics, optimization, formal verification, theorem proving, Lean, proof review, numerical methods, symbolic computation |
| Quantum and advanced computing | quantum algorithms, Qiskit, quantum error correction, calibration, quantum simulation, HPC, GPU computing, distributed training, neuromorphic and unconventional compute |
| Physical sciences | physics, chemistry, materials science, climate, geoscience, astronomy, energy systems, mechanical/electrical/civil/aerospace engineering |
| Life sciences | biology, bioinformatics, neuroscience, ecology, agriculture, drug discovery, therapeutics, molecular modeling, lab automation, biosafety review |
| Robotics and physical action | robotics, embodied AI, motion planning, manipulation, drones, autonomous systems, CAD/CAM, manufacturing, industrial control, IoT, hardware safety |
| Product and UX | product strategy, UX/UI design, accessibility, design systems, visual design, workflow design, documentation, operator cockpit, end-user education |
| Creative and media | writing, editing, storytelling, graphic design, brand, 3D, animation, audio, music, video, film, game design, interactive media |
| Business and operations | strategy, operations, sales, marketing, customer support, HR, recruiting, procurement, logistics, project management, compliance operations |
| Education and communication | tutoring, curriculum, instructional design, translation, linguistics, rhetoric, negotiation, accessibility communication, cross-cultural communication |
| Humanities and social systems | history, philosophy, ethics, sociology, psychology, policy, governance, public administration, geopolitics, anthropology |
| Consumer and life logistics | travel, home planning, cooking, career support, personal productivity, purchasing research, family logistics, local services, consumer safety review |

### Atlas Routing Rule

The mother brain owns the atlas. Existing Experts, AOs, and O planes are not permanent boundaries. They are current routing hypotheses. If a problem repeatedly crosses a boundary, produces poor evals, or requires a new teacher panel, NexusNet should split, merge, or birth a specialist instead of letting a generalist silently absorb the work.

### Atlas Verification Rule

No atlas entry becomes production-authoritative from naming alone. Each entry needs at least:

- two or more teacher candidates;
- one skeptical examiner path;
- one eval or replay pack;
- one source/provenance record;
- one runtime feasibility path;
- one rollback/archive path;
- high-risk review gates when applicable.

## New Candidate Families Beyond The Current Registry

| Family | Candidate models or assets | Source status | Best NexusNet lane | Initial ruling |
| --- | --- | --- | --- | --- |
| OpenAI open-weight | `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `gpt-oss-safeguard-*` | Source-confirmed open-weight model family; official source says weights are on Hugging Face, MXFP4 quantized, with 120B fitting about 80GB and 20B about 16GB. | General reasoning contrast, agentic developer tasks, safety/safeguard reviewer, local high-reasoning teacher candidate. | Add to watchlist as a major general-reasoning and safety teacher candidate. License and output-training rights must be reviewed before distillation. |
| Meta Llama 4 | Llama 4 Scout, Llama 4 Maverick | Source-confirmed open-weight, native multimodal MoE family. | Multimodal generalist contrast, long-context/research contrast, local/cloud teacher council. | Add as a candidate, but not primary until license and benchmark reproducibility concerns are reviewed. |
| Ai2 OLMo / Tulu | OLMo 3 7B/32B, OLMo Hybrid 7B, Tulu 3 post-training recipes | Source-confirmed fully open research flow. | Transparency teacher, reproducible training teacher, open post-training recipe source. | Add strongly for training-pipeline transparency and auditability, even when not the highest raw capability model. |
| IBM Granite | Granite 4.0, Granite 4.1, Granite vision/document variants | Source-confirmed open enterprise model family; Granite 4.1 emphasizes tool calling, instruction following, coding, math. | Regulated enterprise, governance, document intelligence, tool calling, deployment efficiency. | Add as governance/enterprise/document teacher candidate. |
| Cohere Command | Command A+, Command A, Command R/R+ | Source-confirmed open-source/open-weight releases for agentic, multilingual, reasoning, RAG, and enterprise tasks. | Enterprise RAG, multilingual business reasoning, tool-use contrast. | Add as enterprise/RAG council candidate after license and distillation review. |
| Z.ai GLM | GLM-5.2, GLM-5, GLM-4.7, GLM-4.7-Flash, GLM-4.6V | Source-confirmed; GLM-5.2 is current long-horizon/1M-context candidate, GLM-4.7-Flash is lightweight 30B-A3B candidate. | Long-horizon coding, coding agents, browser/task agents, visual reasoning, security/code critique. | Promote from old GLM-4.6 mention to GLM-5.2/GLM-4.7 review candidates. Security lane requires extra misuse gating. |
| Moonshot Kimi | Kimi K2.7-Code, Kimi K2.6 | Source-confirmed; K2.7-Code is a newer coding-focused agentic model built on K2.6. | Coder/Builder/Execution O, long-horizon coding, token-efficiency teacher. | Add K2.7-Code as replacement candidate for K2.6 in coding lanes; keep K2.6 for multimodal/swarm review until final comparison. |
| MiniMax | MiniMax-M2.7 | Source-confirmed; model card emphasizes agent teams, complex skills, dynamic tool search, and self-evolution participation. | SkillsAO, Toolsmith, WorkflowAO, Dream Reviewer contrast, self-improvement harness. | Add as a high-priority agentic/skills teacher candidate. Must gate self-evolution claims through sandbox/evals. |
| Qwen world model | Qwen-AgentWorld-35B-A3B | Source-confirmed; language world model for seven agent interaction domains, simulates environment state from action/history. | WorldModelAO, DreamAO, Dream Reviewer, Simulation Expert, live-problem rehearsal. | Add as first-class language world-model teacher candidate. |
| Nous Hermes | Hermes 4 70B, Hermes Agent patterns, Hermes function-calling datasets | Source-confirmed. | Tool calling, agent personality/control, function-call discipline, local agent harness contrast. | Add as Toolsmith/ProtocolAO/SkillsAO candidate, with license and dataset provenance review. |
| Mistral code/formal | Leanstral 1.5 / Leanstral 2603, Codestral 22B | Leanstral source-confirmed for Lean 4 proof engineering. Codestral source-confirmed but non-production license. | Formal proof, specification verification, theorem proving, code completion research. | Leanstral should be a formal-verification/proof teacher, not a general teacher. Codestral is research-only unless commercial license clears. |
| DeepSeek formal/math | DeepSeek-Prover-V2 7B/671B, DeepSeek-Math-V2 | Source-confirmed for Lean 4 proving and advanced math/theorem verification. | Lean/proof reviewer, math verifier, formal spec council. | Pair with Leanstral for formal proof lanes; do not use as general coding teacher. |
| Quantum models | Qiskit Mistral-Small-3.2-24B-Qiskit, Qiskit Granite models, NVIDIA Ising Calibration/Decoding | Source-confirmed; Qiskit model specializes in Qiskit code; Ising targets quantum calibration/error correction. | Quantum Expert, QuantumAO, scientific simulation, quantum hardware calibration review. | Add a dedicated quantum teacher pack; Ising is partly model/tool family and needs hardware/vendor gating. |
| Medical | MedGemma 1.5/27B, TxGemma, Med42-v2, BioMistral, OpenBioLLM, HuatuoGPT-o1 | Source-confirmed families; licenses and clinical-use constraints vary. | Medical Expert, Clinical Reviewer, Therapeutics Expert, Biomedical ResearchAO. | Add as multi-teacher medical council only. Never single-model medical output. Human/professional gate required. |
| Integrative/holistic medicine | NCCIH evidence sources, ShizhenGPT, TCMChat, BianCang/CMLM TCM models | Source-confirmed research/model families exist for TCM/integrative medicine. | Holistic/Integrative Medicine Expert, TCM contrast teacher, evidence reviewer. | Add as high-risk domain-specific candidates with strict evidence and clinical-safety gates. |
| Legal | SaulLM 54B/141B, Saul 7B, LEGAL-BERT, LegalBench/LEXam/Legal RAG Bench | Source-confirmed legal models and benchmarks. | Legal Expert, ComplianceAO, ContractAO, policy/legal reviewer. | Add SaulLM plus jurisdictional retrieval and benchmarks. Legal answers require citation and jurisdiction gates. |
| Finance/Crypto | FinGPT, FinRobot, finance-LLM, Kronos/market models, BloombergGPT as non-open reference only | Source-confirmed open finance ecosystem; BloombergGPT remains paper/proprietary reference. | Finance Expert, Crypto Expert, RiskAO, Market SimulationAO. | Add FinGPT/FinRobot as finance teacher and workflow source; market decisions require simulator/backtest gates and anti-memorization tests. |
| Edge/mobile | Gemma 3n, Gemma 3/4, LFM2.5, SmolLM3, Phi-4 mini/reasoning, MobileLLM-Pro/R1, MiniCPM-V 4.6 | Source-confirmed on-device and compact families. | EdgeInferenceAO, MobileCompanionAO, Router fast path, local fallback, mobile hive companion. | Add as mandatory edge teacher pool so NexusNet can learn to run on phones, laptops, and constrained devices. |
| Robotics/action | OpenVLA 7B, VLA/VLM robotics families | Source-confirmed open vision-language-action model. | PhysicalWorldAO, Robotics Expert, embodied action simulation. | Add as future physical-action expert lane, gated behind simulation and hardware-safety review. |
| World simulation | Cosmos 3, LingBot-World/open world simulators, DreamerV3, MuZero, Qwen-AgentWorld | Source-confirmed research lines; not all are deployable teacher checkpoints. | WorldModelAO, DreamAO, Simulation Expert, unusual hypothesis generation. | Add as world-model council. Separate generative dreamer from conservative dream reviewer. |

## Proposed Expanded Teacher Packs

These are discussion candidates, not final registry rows.

### Core / Root NexusBrain

Candidate panel:

- Primary reasoning: Qwen3-30B-A3B or GPT-OSS-120B.
- Contrast reasoning: DeepSeek-V4-Pro, GLM-5.2, or OLMo 3 32B Think.
- Agentic/world-model contrast: MiniMax-M2.7, Qwen-AgentWorld-35B-A3B.
- Transparency/audit teacher: OLMo/Tulu.
- Safety reviewer: gpt-oss-safeguard, Claude/GPT/Gemini as external evaluator only if terms allow.

Rationale: the Root brain needs capability plus auditability. A pure frontier-performance panel is not enough because NexusNet needs self-improvement evidence it can inspect.

### Orchestrators

| Orchestrator lane | Candidate teacher pack |
| --- | --- |
| Root NexusBrain O | Qwen3-30B-A3B or GPT-OSS-120B + DeepSeek-V4-Pro + GLM-5.2 + OLMo/Tulu audit teacher |
| Governance O | DeepSeek-V4-Pro + Granite 4.1 + SaulLM legal reviewer + gpt-oss-safeguard or external frontier evaluator |
| Execution O | Qwen3-Coder-Next + Kimi K2.7-Code + GLM-5.2/GLM-4.7 + Devstral Small 2 |
| Research O | Qwen3-30B-A3B + Kimi K2.6 + Command A+/Command R+ + OLMo audit teacher |
| Runtime O | DeepSeek-V4-Flash + LFM2.5 + Gemma 3n + SmolLM3 + Phi-4 mini/reasoning |
| Dream Evolution O | Qwen-AgentWorld + MiniMax-M2.7 + DreamerV3 + MuZero + Cosmos/LingBot-style simulator source |
| Federation O | DeepSeek-V4-Flash + Granite/Command R+ + Security Expert validators + privacy/federated eval gates |
| Multimodal O | Qwen3-Omni + Qwen3-VL + Nemotron Omni + Llama 4 multimodal + GLM-4.6V/MiniCPM-V |
| Product/VisualOps O | GLM-4.7/GLM-5.2 + Kimi K2.7-Code + Gemini/GPT/Claude external UI evaluator only if terms allow |
| World Model O | Qwen-AgentWorld + DreamerV3/MuZero + Cosmos 3/LingBot-World source + OpenVLA for embodied action |

### Assistant Orchestrator Families

| AO family | Candidate teacher pack |
| --- | --- |
| Planning/Operator/Router | Qwen3-30B-A3B + DeepSeek-V4-Pro/Flash + GLM-5.2 + LFM2.5 for budget routing |
| Coding/Builder/Toolsmith/Protocol | Qwen3-Coder-Next + Devstral Small 2 + Kimi K2.7-Code + GLM-5.2 + Hermes/Nous function-call sources |
| Skills/Workflow/Node UX | MiniMax-M2.7 + Hermes Agent patterns + n8n/node-graph UX sources + Toolsmith Expert |
| Runtime/Inference/Quant/Edge | DeepSeek-V4-Flash + LFM2.5 + Gemma 3n + SmolLM3 + MobileLLM + MiniCPM-V |
| Memory/Research/DataIngest | Qwen3-30B-A3B + Command R+ + Granite document models + OLMo/Tulu audit teacher |
| Dream/DreamReviewer/WorldModel | Qwen-AgentWorld + DreamerV3 + MuZero + MiniMax-M2.7 + Leanstral/DeepSeek-Prover for formal review of claims |
| Governance/Safety/Security | DeepSeek-V4-Pro + Granite 4.1 + SaulLM + gpt-oss-safeguard + deterministic validators |
| Medical/Holistic/Mental Health | MedGemma + Med42/OpenBioLLM/BioMistral + NCCIH evidence sources + safety reviewer + human/professional gate |
| Finance/Crypto/Market | FinGPT/FinRobot + Command R+ or Granite + risk/backtest simulator + anti-memorization benchmarks |
| Legal/Compliance | SaulLM + LEGAL-BERT retrieval/classifier + LegalBench/LEXam + jurisdiction-aware RAG |
| Quantum/Science/Formal | Leanstral + DeepSeek-Prover-V2 + Qiskit-Mistral + NVIDIA Ising/Qiskit benchmarks |
| Robotics/Physical Action | OpenVLA + multimodal perception model + world simulator + sandbox/hardware safety validator |

### Expert Expansions Needed

The current 19-expert roster remains the canon baseline, but it is not close to complete. The open-world atlas above is the governing shape. The following are only high-priority initial expansions to seed the passport process:

- Medical Expert: MedGemma + Med42/OpenBioLLM + BioMistral + clinical benchmark/human gate.
- Holistic/Integrative Medicine Expert: MedGemma or BioMistral + NCCIH retrieval + ShizhenGPT/TCMChat only as TCM contrast + clinical safety gate.
- Legal Expert: SaulLM + LegalBERT/retrieval + LEXam/LegalBench.
- Finance Expert: FinGPT + Command/Granite + financial eval/backtest gates.
- Crypto Expert: FinGPT/FinRobot + code/security teacher + market/manipulation risk simulator.
- Quantum Expert: Qiskit-Mistral + Leanstral + DeepSeek-Prover + NVIDIA Ising validators.
- Formal Verification Expert: Leanstral + DeepSeek-Prover-V2 + Lean/LeanDojo/Axle-style proof checking.
- World Model Expert: Qwen-AgentWorld + DreamerV3 + MuZero + Cosmos/LingBot-world-model source.
- Robotics Expert: OpenVLA + Qwen3-Omni/Nemotron + safety simulator.
- Edge/Mobile Expert: Gemma 3n + LFM2.5 + SmolLM3 + MobileLLM + MiniCPM-V.
- Enterprise/RAG Expert: Command R+ + Granite + Qwen/DeepSeek + retrieval/evidence gates.
- Transparency/Open-Science Expert: OLMo + Tulu + StarCoder2 transparent code-data governance.
- Cybersecurity Expert refresh: GLM-5.2 candidate + Devstral/Qwen coder + Semgrep/CodeQL/OWASP validators. Treat high-capability cyber models as dual-use and high-risk.

## Immediate Registry Refresh Candidates

| Existing registry area | Problem | Candidate update |
| --- | --- | --- |
| `Kimi K2.6` for coding | K2.7-Code is newer and explicitly coding-focused. | Keep K2.6 for multimodal/swarm until compared; add K2.7-Code for Coder/Builder/Execution O review. |
| `GLM-4.6` references in notes | GLM-5.2 and GLM-4.7 are now source-confirmed newer candidates. | Add GLM-5.2 as long-horizon/coding/security review candidate; add GLM-4.7-Flash for lighter routes. |
| `LFM2` efficiency coach | LFM2.5 family is newer and better aligned with on-device teacher needs. | Replace broad `LFM2` language with exact LFM2.5 candidate rows after license review. |
| `Mistral Small 4` | Needs exact source refresh. | Verify current Mistral small/medium model IDs before retaining as primary teacher. |
| `Devstral 2` | Needs exact source refresh versus Devstral Small 2. | Prefer source-confirmed Devstral Small 2 for Apache-clean local coding fallback until Devstral 2 terms are verified. |
| `BLOOMZ` as Linguist contrast | Stable but old and not enough for modern multilingual expert training. | Add Command A/R+, Gemma multilingual, Qwen, Llama 4, and OLMo as language contrast candidates. |
| Internal placeholders | `NexusNet-Intent-BERT-v0`, `NexusNet-Historian-v0`, `NexusNet-RecurrentMemory-v0` still need owned/provenance-cleared evidence. | Keep as placeholders, not rejects. Require provenance cards before active teacher status. |
| Dream/simulation | DreamerV3 and MuZero are algorithmic teachers, not LLM teacher cards. | Add Qwen-AgentWorld and MiniMax-M2.7 as language/agentic companions; keep Dreamer/MuZero as simulation algorithms. |

## Source Anchors Checked

- OpenAI GPT-OSS: https://openai.com/index/introducing-gpt-oss/ and https://huggingface.co/openai/gpt-oss-120b
- Meta Llama 4: https://ai.meta.com/blog/llama-4-multimodal-intelligence/ and https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E
- OLMo: https://allenai.org/olmo and https://huggingface.co/allenai/Olmo-3.1-32B-Instruct
- Granite: https://www.ibm.com/granite/docs/models/granite4-1
- Command A+: https://huggingface.co/CohereLabs/command-a-plus-05-2026-w4a4
- GLM-5.2: https://huggingface.co/zai-org/GLM-5.2 and https://z.ai/blog/glm-5.2
- GLM-4.7/Flash: https://huggingface.co/zai-org/GLM-4.7 and https://huggingface.co/zai-org/GLM-4.7-Flash
- Kimi K2.7-Code: https://huggingface.co/moonshotai/Kimi-K2.7-Code
- MiniMax M2.7: https://huggingface.co/MiniMaxAI/MiniMax-M2.7
- Qwen-AgentWorld: https://huggingface.co/Qwen/Qwen-AgentWorld-35B-A3B
- Hermes 4: https://huggingface.co/NousResearch/Hermes-4-70B
- StarCoder2: https://huggingface.co/blog/starcoder2 and https://huggingface.co/bigcode/starcoder2-15b-instruct-v0.1
- Codestral: https://mistral.ai/news/codestral/
- Leanstral: https://mistral.ai/news/leanstral/ and https://huggingface.co/mistralai/Leanstral-2603
- DeepSeek-Prover-V2: https://huggingface.co/deepseek-ai/DeepSeek-Prover-V2-7B and https://huggingface.co/deepseek-ai/DeepSeek-Prover-V2-671B
- DeepSeek-Math-V2: https://huggingface.co/deepseek-ai/DeepSeek-Math-V2
- Qiskit model and benchmark: https://huggingface.co/Qiskit/mistral-small-3.2-24b-qiskit and https://huggingface.co/datasets/Qiskit/Qiskit-QuantumKatas
- NVIDIA Ising: https://github.com/NVIDIA/ising and https://huggingface.co/nvidia/Ising-Calibration-1-35B-A3B
- MedGemma: https://developers.google.com/health-ai-developer-foundations/medgemma/model-card and https://huggingface.co/google/medgemma-27b-it
- TxGemma: https://developers.google.com/health-ai-developer-foundations/txgemma/model-card
- Med42: https://huggingface.co/m42-health/Llama3-Med42-8B
- BioMistral: https://huggingface.co/BioMistral/BioMistral-7B
- OpenBioLLM: https://huggingface.co/blog/aaditya/openbiollm
- NCCIH: https://www.nccih.nih.gov/
- ShizhenGPT: https://huggingface.co/FreedomIntelligence/ShizhenGPT-7B-VL
- TCMChat: https://huggingface.co/ZJUFanLab/TCMChat-600k
- SaulLM: https://huggingface.co/Equall/SaulLM-141B-Instruct
- LEGAL-BERT: https://huggingface.co/nlpaueb/legal-bert-base-uncased
- LEXam: https://huggingface.co/datasets/LEXam-Benchmark/LEXam
- FinGPT: https://github.com/ai4finance-foundation/fingpt and https://huggingface.co/FinGPT
- Gemma 3n: https://ai.google.dev/gemma/docs/gemma-3n and https://huggingface.co/google/gemma-3n-E4B-it
- SmolLM3: https://huggingface.co/HuggingFaceTB/SmolLM3-3B
- MobileLLM: https://huggingface.co/facebook/MobileLLM-Pro and https://huggingface.co/facebook/MobileLLM-R1-950M
- LFM2.5: https://huggingface.co/LiquidAI/LFM2.5-350M and https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking
- Phi-4: https://huggingface.co/microsoft/Phi-4-multimodal-instruct and https://huggingface.co/microsoft/Phi-4-mini-reasoning
- OpenVLA: https://huggingface.co/openvla/openvla-7b
- Cosmos 3: https://huggingface.co/papers/2606.02800
- LingBot-World: https://huggingface.co/papers/2601.20540

## Open Verification Gaps

- Exact license and derivative-output rights must be checked model by model before any distillation, fine-tuning, or teacher-data generation.
- Hardware feasibility must be measured for each local route: GPU VRAM, CPU fallback, quantization quality, thermal behavior, load time, token throughput, and context-window stability.
- Source freshness must be rechecked immediately before final registry update because new open-weight models are releasing weekly.
- High-risk domains require benchmark packs and human/governance gates before active use.
- Current registry names like `Mistral Small 4`, `Mistral Medium 3.5`, `Devstral 2`, and `LFM2` need exact model-ID refresh rather than broad family references.
- Closed frontier models need terms review before any use as evaluator, judge, or synthetic-data source.
