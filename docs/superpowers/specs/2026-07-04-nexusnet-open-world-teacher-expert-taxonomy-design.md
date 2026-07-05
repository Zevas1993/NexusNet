# NexusNet Open-World Teacher, Orchestrator, AO, Expert, and Dreaming Design

Date: 2026-07-04
Status: design approved in conversation, updated by assimilation cluster review, pending implementation plan
Scope: NexusNet teacher ensemble, Orchestrators, Assistant Orchestrators, Experts, recursive dreaming, auto-research, auto-assimilation, and live self-improvement

## Purpose

NexusNet must not depend on a fixed hand-written list of teachers, Orchestrators, Assistant Orchestrators, or Experts. Model releases, benchmarks, tools, and domain needs change too quickly. The system needs an open-world registry model that can research, quarantine, evaluate, shadow-route, promote, merge, retire, and replace models and experts with evidence.

This design treats the current NexusNet AO and teacher registries as seed registries, not the final universe.

## Assimilation Review Addendum

The 2026-07-04 live assimilation review expanded this design in three important ways:

1. Cluster 5 is now `NexusNet Knowledge Forge And Agent-Native Memory OS`, not only a retrieval or knowledge-artifact subsystem.
2. Cluster 13 is now `NexusGraph Intelligence Fabric`, including agentic evolving GraphRAG, universal graph intelligence, graph/memory passports, and mutation-impact reasoning.
3. The O/AO/Expert inventory needs another reconciliation pass for memory-specific and graph-specific lanes before any final roster is claimed.

The lists below are therefore seed lists. They are not exhaustive.

## Design Goals

1. Create an extensible expert ontology instead of a finite "complete" expert list.
2. Expand Orchestrators and Assistant Orchestrators to cover auto-research, assimilation, recursive dreaming, dynamic expert creation, expert merge, and regulated domains.
3. Add recursive dreaming as a first-class divergent self-improvement pathway using high-temperature generation and low-temperature critique.
4. Add domain-risk handling for crypto, finance, medicine, holistic and integrative medicine, law, security, and other high-impact areas.
5. Track teacher/model candidates as a changing universe with license, hardware, eval, source, and promotion state.
6. Support live-problem temporary experts and task forces without mutating permanent registries until evidence gates pass.

## Non-Goals

1. This spec does not claim any candidate model is permanently best.
2. This spec does not authorize production mutation from dream output, model scouting, or temporary expert output without gates.
3. This spec does not make NexusNet a medical, legal, financial, or crypto advisor without human and jurisdiction-aware controls.
4. This spec does not implement code. It defines the target architecture for the implementation plan.

## Architecture Overview

The target system has six coordinated registry layers:

1. **Orchestrator Registry**: mission-level controllers and lifecycle controllers.
2. **Assistant Orchestrator Registry**: durable capability managers.
3. **Expert Ontology Registry**: open-world domain and capability expert taxonomy.
4. **Teacher Candidate Universe**: models, tools, datasets, benchmarks, and verifier systems available for training or review.
5. **Recursive Dream Registry**: high-divergence dream cycles and sandbox-only growth proposals.
6. **Promotion and Evidence Registry**: proof bundles, replay evidence, licenses, safety reviews, and retirement decisions.

NexusNet should route real work through these layers:

`problem signal -> domain/risk classification -> orchestrator route -> AO panel -> expert panel -> teacher/model/tools -> evidence ledger -> optional dream/task-force/growth loop -> shadow/promotion gate`

## Orchestrator Layer

The Orchestrator layer should include at least these logical orchestrators:

- **CoreMissionOrchestrator**: owns top-level goal decomposition and mission policy.
- **HiveMindOrchestrator**: routes across brain, AO, and expert layers.
- **WrapperOrchestrator**: handles operator-facing release-wrapper and runtime governance.
- **TeacherLifecycleOrchestrator**: scouts, evaluates, promotes, demotes, retires, and replaces teacher models.
- **ResearchAssimilationOrchestrator**: discovers papers, models, tools, datasets, benchmarks, and source-health changes.
- **ExpertEvolutionOrchestrator**: creates, merges, splits, retires, and promotes experts.
- **RecursiveDreamOrchestrator**: runs high-temperature divergent dreaming and routes outputs through sandbox gates.
- **TaskForceOrchestrator**: creates temporary live task-force experts when NexusNet is stuck.
- **EvaluationGovernanceOrchestrator**: owns eval gates, verifier panels, evidence standards, and regression policy.
- **MemoryKnowledgeOrchestrator**: consolidates durable knowledge, knowledge artifacts, and memory quality.
- **AgentNativeMemoryOrchestrator**: governs memory extraction, routing, maintenance, temporal updates, consolidation, forgetting, evals, and promotion.
- **MemoryEvolutionOrchestrator**: owns candidate memory deltas, memory merge/split/retire flows, sleep-time memory consolidation, and `MemoryEvolutionPassport` review.
- **NexusGraphOrchestrator**: owns graph registry contracts, graph query contracts, graph delta proposals, graph freshness, graph poisoning defenses, and graph replay.
- **GraphEvolutionOrchestrator**: governs agentic GraphRAG, ontology evolution, graph mutation candidates, `GraphEvolutionPassport` review, and graph rollback.
- **RuntimeResourceOrchestrator**: routes by hardware, cost, latency, privacy, and provider health.
- **SafetyPolicyOrchestrator**: blocks or constrains high-risk outputs and actions.
- **DomainRiskOrchestrator**: coordinates regulated domains such as medical, finance, crypto, legal, security, and safety.
- **WorldSimulationOrchestrator**: coordinates world models, simulations, causal labs, robotics, and physical AI.
- **MultimodalPerceptionOrchestrator**: coordinates text, image, audio, video, screen, document, and computer-use perception.
- **FederationTrustOrchestrator**: handles federated feedback, privacy, provenance, and trust boundaries.
- **ReleaseProductOrchestrator**: governs release readiness, UX, packaging, operator status, and rollback.

## Assistant Orchestrator Layer

The current AO registry should expand from broad seed AOs into durable capability managers.

### Core Operations AOs

- `PlanningAO`
- `OperatorAO`
- `RouterAO`
- `MemoryAO`
- `MemoryQualityAO`
- `MemoryExtractionAO`
- `MemoryRoutingAO`
- `TemporalMemoryAO`
- `MemoryMaintenanceAO`
- `MultimodalMemoryAO`
- `SleepConsolidationAO`
- `MemoryPrivacyAO`
- `MemoryEvalAO`
- `GraphRegistryAO`
- `GraphQueryAO`
- `GraphEvolutionAO`
- `GraphSafetyAO`
- `GraphPrivacyAO`
- `GraphReplayAO`
- `GraphEvalAO`
- `RuntimeAO`
- `GovernanceAO`
- `AdminAO`
- `ReleaseAO`
- `PackagingAO`
- `HardwareFleetAO`
- `CostAO`
- `ProviderHealthAO`
- `ToolUseAO`
- `MCPBridgeAO`
- `BrowserComputerUseAO`

### Research and Assimilation AOs

- `ModelScoutAO`
- `PaperScoutAO`
- `DatasetScoutAO`
- `BenchmarkScoutAO`
- `SourceVerifierAO`
- `LicenseProvenanceAO`
- `AssimilationAO`
- `TeacherRegistryAO`
- `TeacherLifecycleAO`
- `ForwardRadarAO`
- `SourceHealthAO`
- `CitationIntegrityAO`

### Evaluation and Training AOs

- `BenchmarkAO`
- `RegressionAO`
- `EvalsAO`
- `EvaluationAO`
- `CurriculumAO`
- `DatasetQualityAO`
- `SyntheticDataAO`
- `PreferenceDataAO`
- `RLAIFAO`
- `DistillationAO`
- `VerifierAO`
- `ShadowCanaryAO`

### Expert Evolution AOs

- `StucknessDetectorAO`
- `CapabilityGapAO`
- `TaskForceAO`
- `ExpertForgeAO`
- `ExpertMergeAO`
- `ExpertSplitAO`
- `ExpertRetirementAO`
- `PromotionTribunalAO`
- `NoveltyLedgerAO`

### Recursive Dreaming AOs

- `DreamAO`
- `RecursiveDreamAO`
- `FailurePriorAO`
- `DivergentDreamAO`
- `DreamCritiqueAO`
- `DreamSandboxAO`
- `DreamPromotionAO`
- `DreamRollbackAO`

### Domain and Risk AOs

- `RiskTierAO`
- `MedicalSafetyAO`
- `HolisticMedicineEvidenceAO`
- `LegalRiskAO`
- `FinanceRiskAO`
- `CryptoRiskAO`
- `ComplianceAO`
- `PrivacyAO`
- `SecurityAO`
- `RedTeamAO`
- `SafetyAO`
- `BioSafetyAO`
- `ChildSafetyAO`

### Science, World, and Multimodal AOs

- `WorldModelAO`
- `RoboticsAO`
- `SimulationAO`
- `CausalLabAO`
- `QuantumResearchAO`
- `BioResearchAO`
- `ClimateAO`
- `MaterialsScienceAO`
- `ImageGenAO`
- `VideoGenAO`
- `AudioGenAO`
- `VisualOpsAO`
- `DocumentUnderstandingAO`
- `RetrievalAO`
- `RerankerAO`
- `KnowledgeGraphAO`

## Expert Ontology Layer

NexusNet should not try to enumerate every possible expert as final code. It should maintain an open-world ontology with root domains, subdomains, risk tiers, evidence requirements, and dynamic creation rules.

Every expert record should include:

- `expert_id`
- `domain`
- `subdomain`
- `capability_traits`
- `risk_tier`
- `regulated_status`
- `evidence_standard`
- `allowed_actions`
- `forbidden_actions`
- `source_requirements`
- `teacher_pool`
- `critic_pool`
- `verifier_pool`
- `retriever_pool`
- `eval_family`
- `update_cadence`
- `promotion_gates`
- `fallback_experts`
- `merge_candidates`
- `retirement_policy`

## Bootstrap Expert Families

### Software and Systems

- Software architect
- Frontend engineer
- Backend engineer
- Mobile engineer
- Android engineer
- iOS engineer
- Systems engineer
- Compiler engineer
- Runtime engineer
- Database engineer
- Distributed systems expert
- DevOps engineer
- SRE
- QA and test engineer
- Formal methods expert
- Static analysis expert
- Code review expert
- API design expert
- UI and UX expert
- Accessibility expert
- Technical writer

### AI, ML, and Data

- Model selection expert
- Training expert
- Fine-tuning expert
- RL expert
- RLAIF expert
- Evaluation expert
- Dataset curator
- Synthetic data expert
- Embeddings expert
- Retrieval expert
- Reranking expert
- Knowledge graph expert
- Multimodal expert
- Vision expert
- Audio expert
- Video expert
- Image generation expert
- World model expert
- Robotics learning expert
- Agentic workflow expert
- Prompt and instruction expert
- Model compression expert
- Quantization expert

### Security

- AppSec expert
- Cloud security expert
- Infrastructure security expert
- Supply-chain security expert
- Malware analysis expert
- Reverse engineering expert
- Cryptography expert
- Smart contract security expert
- Threat modeling expert
- Red team expert
- Blue team expert
- Privacy engineering expert
- Incident response expert
- Secure coding expert

### Crypto and Web3

- Blockchain protocol expert
- Consensus systems expert
- Smart contract expert
- Smart contract auditor
- DeFi expert
- Tokenomics expert
- Wallet and custody expert
- On-chain analytics expert
- MEV expert
- Bridge security expert
- ZK proof systems expert
- Crypto compliance expert
- AML and KYC expert
- Stablecoin expert
- DAO governance expert
- Digital asset risk expert

Crypto experts must be routed through security, legal, compliance, and financial-risk panels for user-impacting guidance.

### Finance and Economics

- Personal finance expert
- Corporate finance expert
- Accounting expert
- Tax expert
- Market analyst
- Macro economist
- Micro economist
- Quant finance expert
- Portfolio risk expert
- Banking expert
- Insurance expert
- Real estate expert
- Financial fraud expert
- Financial compliance expert
- Audit expert
- Actuarial expert
- Payments expert

Finance experts must use evidence and risk warnings. They must not provide personalized financial advice as autonomous final authority without the configured compliance path.

### Medical and Health

- Clinical medicine expert
- Biomedical research expert
- Pharmacology expert
- Drug interaction expert
- Radiology expert
- Pathology expert
- Public health expert
- Epidemiology expert
- Mental health expert
- Nutrition expert
- Exercise science expert
- Sleep expert
- Medical safety expert
- Patient education expert
- Medical literature appraisal expert
- Clinical trial expert
- Biostatistics expert

Medical experts must be safety gated. They may support education, triage framing, literature review, and question preparation, but must not replace licensed clinical judgment.

### Holistic, Integrative, and Lifestyle Medicine

- Lifestyle medicine expert
- Integrative medicine evidence reviewer
- Functional medicine claims reviewer
- Nutrition and supplement evidence expert
- Herbal interaction checker
- Mindfulness and stress management expert
- Traditional medicine research reviewer
- Sleep hygiene expert
- Exercise and mobility expert
- Wellness misinformation critic

Holistic and integrative medicine experts must be evidence-graded. They must distinguish peer-reviewed support, plausible but weak evidence, anecdotal claims, contraindications, interactions, and unsafe claims. They must route through `MedicalSafetyAO` and `HolisticMedicineEvidenceAO`.

### Law, Policy, and Governance

- Contract expert
- IP expert
- Privacy law expert
- Labor law expert
- Corporate law expert
- Healthcare law expert
- Financial regulation expert
- Crypto regulation expert
- AI policy expert
- Compliance expert
- Public policy analyst
- Governance expert
- Risk management expert
- Procurement expert

Legal experts must not provide jurisdiction-specific legal advice as final authority without jurisdiction, source, and human-professional caveats.

### Science and Engineering

- Mathematician
- Formal proof expert
- Physics expert
- Chemistry expert
- Biology expert
- Molecular biology expert
- Protein science expert
- Materials science expert
- Climate science expert
- Weather forecasting expert
- Energy systems expert
- Electrical engineer
- Mechanical engineer
- Civil engineer
- Aerospace engineer
- Manufacturing expert
- Quantum algorithms expert
- Quantum hardware expert
- Quantum chemistry expert
- Robotics expert
- Control systems expert

### Business and Operations

- Product manager
- Strategy expert
- Marketing expert
- Sales expert
- Customer support expert
- HR expert
- Recruiting expert
- Operations expert
- Logistics expert
- Supply-chain expert
- Manufacturing operations expert
- Project manager
- Business analyst
- Negotiation expert
- Founder and startup expert

### Humanities, Communication, and Education

- Writer
- Editor
- Researcher
- Historian
- Philosopher
- Linguist
- Translator
- Localization expert
- Teacher
- Tutor
- Curriculum expert
- Debate expert
- Rhetoric expert
- Media studies expert
- Game design expert
- Narrative design expert

### Practical Life and Civic Domains

- Agriculture expert
- Food safety expert
- Construction expert
- Home repair expert
- Automotive expert
- Emergency preparedness expert
- Accessibility expert
- Elder care expert
- Child development expert
- Travel expert
- Public benefits navigator
- Civic process expert

## Domain Risk Tiers

Each domain should be tagged with risk tiers:

- `low`: low-impact creative or informational tasks.
- `medium`: tasks where errors can waste time or money.
- `high`: user-impacting legal, financial, medical, security, crypto, privacy, or safety tasks.
- `critical`: tasks involving clinical decisions, legal decisions, financial trades, credential/security compromise, physical safety, child safety, or irreversible actions.

High and critical tiers require panel routing:

`domain expert + risk/compliance expert + evidence verifier + critic + source retriever`

## Teacher and Model Candidate Universe

NexusNet should maintain a changing candidate universe rather than permanent "best teacher" names.

Every candidate should include:

- `candidate_id`
- `model_or_tool_id`
- `provider`
- `source_url`
- `candidate_status`: `watchlist`, `quarantined`, `benchmarked`, `shadow`, `canary`, `active`, `retired`, `blocked`
- `teacher_roles`: `generator`, `critic`, `verifier`, `retriever`, `simulator`, `compact_apprentice`, `judge`
- `license_gate`
- `privacy_gate`
- `hardware_gate`
- `cost_gate`
- `eval_family`
- `domain_scope`
- `risk_scope`
- `last_researched_at`
- `source_refs`
- `benchmark_refs`
- `replacement_candidates`
- `retirement_reason`

### Candidate Families To Track

The initial watchlist should include at least:

- **General and agentic reasoning**: DeepSeek V4, GLM-4.5, MiniMax M2.x, Qwen3, Mistral Small, Kimi K2.x, Llama 4, Gemma, Granite, Phi.
- **Coding and software agents**: Qwen3-Coder, Devstral, GLM-4.5, MiniMax M2.x, GPT Codex-class models, Claude coding models, Gemini coding models, Grok coding models.
- **Formal proof and verification**: Leanstral, theorem provers, proof assistants, formal methods tools, static analyzers.
- **Multimodal perception**: Qwen3-VL, Nemotron Omni, Kimi multimodal, GLM vision, Llama multimodal, Gemma vision, Granite vision.
- **Medical and biomedical**: MedGemma, BioMistral, OpenBioLLM-style models, medical VQA and clinical reasoning benchmarks.
- **World models and robotics**: NVIDIA Cosmos, Genie, DreamerV3, MuZero, robotics simulators.
- **Science**: AlphaFold 3, Boltz, ESM, GraphCast, GenCast, domain simulators.
- **Quantum**: Qiskit, PennyLane, Classiq, quantum code benchmarks, theorem and circuit verifiers.
- **Retrieval and memory**: BGE rerankers, E5 embeddings, Jina rerankers, Granite embeddings, domain RAG tools.
- **Creative media**: FLUX, Stable Diffusion family, Wan video models, Hunyuan video models, audio and music models.

### Leanstral Role

Leanstral should not be treated as a broad Orchestrator teacher. Its best role is:

- formal proof teacher
- theorem proving teacher
- Lean 4 proof critic
- mathematical reasoning verifier
- code specification and formal-methods bridge
- critic for expert claims that can be formalized
- AO trainer for `FormalMethodsAO`, `MathAO`, `QuantumResearchAO`, and verification-heavy parts of `CodingAO`

## Recursive Dreaming Design

Recursive dreaming is a core self-improvement pathway, not a normal expert.

The intended loop is:

`stuck signal or failure prior -> high-temperature dream variants -> low-temperature critic -> sandbox-only proposal -> eval replay -> promotion tribunal -> shadow/canary/active if approved`

Dreaming may propose:

- generated expert
- expert merge candidate
- expert split candidate
- routing policy candidate
- dataset seed candidate
- curriculum seed candidate
- runtime method candidate
- teacher pairing candidate
- benchmark or verifier candidate
- research direction candidate

Dreaming must not directly mutate production routes, production weights, permanent registries, user-visible advice policy, or trusted sources.

### Temperature Contract

- Dreamer temperature: high, divergent, novelty-seeking.
- Critic temperature: low, conservative, evidence-seeking.
- Reviewer panel: low-temperature domain critics plus safety and evidence verifiers.

### Dream Candidate Metadata

- `dream_id`
- `source_failure_refs`
- `source_research_refs`
- `dream_temperature`
- `critic_temperature`
- `candidate_type`
- `proposal`
- `novelty_score`
- `risk_tier`
- `sandbox_required`
- `promotion_required`
- `required_gates`
- `artifact_refs`
- `operator_visible`
- `production_mutation_allowed`: always false before approval

## Live Task-Force Experts

During a live problem, NexusNet may create temporary experts when existing coverage is insufficient.

Temporary expert fields:

- `temporary_expert_id`
- `ttl`
- `trigger_failure_ids`
- `problem_statement`
- `member_experts`
- `teacher_pairing`
- `allowed_tools`
- `forbidden_tools`
- `risk_tier`
- `evidence_log`
- `eval_gate`
- `promotion_candidate`
- `merge_candidate`
- `retire_at`

Temporary experts can assist a live problem immediately inside a quarantine boundary. They cannot become permanent unless promotion evidence passes.

## Expert Merge and Split

NexusNet should merge experts when repeated evidence shows overlapping capability and better combined routing.

Merge gates:

- shared capability traits
- compatible risk tier
- no unresolved safety conflicts
- improved eval performance
- no regression in parent tasks
- rollback path
- human or governance approval for high-risk domains

NexusNet should split experts when a domain becomes too broad, risk semantics diverge, or routing evidence shows repeated specialization.

## Auto-Research and Auto-Assimilation

NexusNet needs continuous research loops:

1. Discover candidate models, tools, papers, datasets, and benchmarks.
2. Verify source health and provenance.
3. Extract model cards, licenses, evals, hardware needs, and risk notes.
4. Quarantine new candidates by default.
5. Run benchmark and compatibility checks.
6. Add candidates to shadow routing only after minimum evidence.
7. Promote to canary or active only after eval gates and rollback plans.
8. Retire or demote stale, unsafe, expensive, license-blocked, or underperforming candidates.

The candidate universe should update frequently, but active teacher promotion should remain evidence-gated.

## Evidence Standards

NexusNet should tag claims and sources:

- `peer_reviewed`
- `official_docs`
- `regulatory_source`
- `benchmark_result`
- `repo_source`
- `model_card`
- `empirical_internal_eval`
- `expert_consensus`
- `anecdotal`
- `speculative`
- `unsafe_or_disallowed`

Regulated or high-risk domains must require stronger source classes.

## Data Flow

1. User request enters NexusNet.
2. Router classifies intent, domain, risk tier, modality, tool need, and evidence requirement.
3. Orchestrator selects an AO panel.
4. AO panel selects experts and teacher roles.
5. Retrieval and verifier pools gather current evidence.
6. Expert panel produces answer, plan, code, or proposal.
7. Critic and verifier panel checks risk, source quality, and regressions.
8. If stuck, route to `TaskForceOrchestrator` and optionally `RecursiveDreamOrchestrator`.
9. Any new expert/model/route proposal enters quarantine and evidence registry.
10. Promotion tribunal decides shadow, canary, active, retire, merge, split, or reject.

## Error Handling

- Missing domain: create temporary task-force expert and open ontology expansion proposal.
- Missing teacher: route to model scout and fallback teacher pool.
- Missing source evidence: downgrade confidence and block high-risk finalization.
- License uncertainty: quarantine candidate.
- High-risk domain without verifier: block or ask for human confirmation.
- Dream candidate without eval evidence: keep sandbox-only.
- Model benchmark regression: demote or retire candidate.
- Expert merge regression: rollback to parent experts.

## Testing Strategy

Implementation should add focused tests for:

- expert ontology registration and lookup
- domain/risk classification
- regulated-domain panel routing
- crypto and finance risk gates
- holistic medicine evidence-grade gates
- temporary task-force expert lifecycle
- recursive dream candidate lifecycle
- expert merge and rollback
- teacher candidate quarantine and promotion
- source-health and license gates
- model replacement and retirement
- shadow route before active route mutation
- GitNexus detect-changes after registry implementation
- `MemoryEvolutionPassport` before any memory write/update is promoted
- `GraphFactPassport` for graph nodes and edges
- `GraphQueryPassport` for graph queries
- `GraphEvolutionPassport` before any graph delta is promoted
- graph/memory O/AO/Expert reconciliation before final roster claims

## Implementation Slices

Recommended slices:

1. Add ontology schema and static bootstrap domain taxonomy.
2. Add risk-tier and evidence-standard metadata.
3. Add candidate universe schema for teachers/models/tools.
4. Add recursive dream metadata and route integration.
5. Add temporary task-force expert lifecycle.
6. Add expert merge/split proposal lifecycle.
7. Add regulated-domain panel routing.
8. Add auto-research intake and source verification.
9. Add promotion tribunal integration.
10. Add UI/control-panel status surfaces for honest operator visibility.
11. Add agent-native memory schema and `MemoryEvolutionPassport`.
12. Add memory eval policy, privacy policy, and forgetting policy.
13. Add NexusGraph schema, graph query profile, and graph passport contracts.
14. Add agentic evolving GraphRAG shadow-delta lifecycle.
15. Reconcile Cluster 9 graph/memory O/AO/Expert seed candidates into the open-world atlas.

## Source References For Initial Research Watchlist

- Leanstral 1.5: https://huggingface.co/mistralai/Leanstral-1.5-119B-A6B
- Qwen3-Coder: https://qwen.ai/blog?id=qwen3-coder-next
- GLM-4.5: https://github.com/zai-org/GLM-4.5
- MiniMax: https://www.minimax.io/
- Mistral Devstral: https://mistral.ai/news/devstral-2
- NVIDIA Nemotron Omni: https://developer.nvidia.com/blog/nvidia-nemotron-3-nano-omni-powers-multimodal-agent-reasoning-in-a-single-efficient-open-model/
- Qwen3-VL: https://github.com/QwenLM/Qwen3-VL
- MedGemma: https://huggingface.co/google/medgemma-1.5-4b-it
- BioMistral: https://huggingface.co/BioMistral/BioMistral-7B
- NVIDIA Cosmos: https://www.nvidia.com/en-us/ai/cosmos/
- Genie: https://deepmind.google/models/genie/
- DreamerV3: https://arxiv.org/abs/2301.04104
- MuZero: https://deepmind.google/blog/muzero-mastering-go-chess-shogi-and-atari-without-rules/
- AlphaFold 3: https://www.nature.com/articles/s41586-024-07487-w
- Boltz: https://github.com/jwohlwend/boltz
- GraphCast: https://github.com/google-deepmind/graphcast
- QuanBench: https://arxiv.org/html/2604.08570v2
- Qiskit: https://www.ibm.com/quantum/qiskit
- PennyLane: https://pennylane.ai/
- Classiq: https://www.classiq.io/
- BGE reranker: https://huggingface.co/BAAI/bge-reranker-v2-m3
- multilingual E5: https://huggingface.co/intfloat/multilingual-e5-large-instruct
- FLUX.2 dev: https://huggingface.co/black-forest-labs/FLUX.2-dev
- Wan2.2: https://github.com/Wan-Video/Wan2.2

## Approval State

The user approved the full conversation direction on 2026-07-04, including:

- expanded Orchestrators
- expanded AOs
- open-world experts
- model candidate universe
- live temporary experts
- expert merge and split
- recursive dreaming with high-temperature dreamer and low-temperature critic
- world models
- medical models
- quantum research
- crypto
- finance
- holistic medicine
- auto-research, auto-assimilation, and auto-update

Implementation should proceed only after this spec is reviewed and an implementation plan is written.
