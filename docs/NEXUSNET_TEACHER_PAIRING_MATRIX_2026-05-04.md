# NexusNet Teacher Pairing Matrix - 2026-05-04

Status: canon-facing v0 matrix

Canon entry: `PB-2026-05-04-092 - Subsystem Teacher Pairing Matrix`

Refresh entry: `PB-2026-05-04-093 - Teacher Roster Current-Model Refresh`

Purpose: define the teacher pairings for NexusNet's O-level orchestrator brains, AO-level assistant orchestrator brains, and expert Mini-NexusNet brains. This is not a rigid ownership tree. It is a training, review, and routing matrix for a connected hive substrate where every O, AO, expert, memory plane, dream cycle, evaluator, runtime component, and idle node remains connected through the NeuralBus, HiveBlackboard, pathway ledgers, checkpoints, and governance gates.

## Source Anchors

- `nexusnet/teachers/teacher_registry_v2026_live.yaml`
- `nexusnet/teachers/expert_training_regimens.yaml`
- `nexusnet/teachers/teacher_routing_policy.yaml`
- `nexusnet/teachers/teacher_registry_historical.yaml`
- `docs/teachers_historical_vs_live.md`
- `docs/NEXUSNET_CHAT_RESEARCH_CANON_2026-04-28.md`
- `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
- `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`
- `https://huggingface.co/moonshotai/Kimi-K2.6`
- `https://mistral.ai/news/mistral-small-4`
- `https://api-docs.deepseek.com/news/news260424`
- `https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro`
- `https://github.com/QwenLM/Qwen3`
- `https://mistral.ai/news/devstral-2-vibe-cli`
- `https://huggingface.co/nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16`
- `https://huggingface.co/mistralai/Voxtral-Small-24B-2507`
- `https://github.com/openai/whisper`
- `https://owasp.org/www-project-top-10-for-large-language-model-applications/`

## Current-Model Refresh Notes

PB-2026-05-04-093 updates the matrix from a structurally correct v0 roster into a current v0.1 teacher roster:

- Kimi K2.5 -> Kimi K2.6 for research, browser/research, swarm/orchestration, and long-horizon agentic contrast.
- Magistral Small 1.2 is deprecated; use Mistral Small 4 as the default open replacement.
- Mistral Medium 3.5 is a high-compute council candidate only after modified MIT/license review.
- DeepSeek-V2-Lite is fallback-only; DeepSeek-V4-Flash becomes the fast runtime/router/federation teacher and DeepSeek-V4-Pro becomes the high-stakes governance/analysis/critique teacher.
- Devstral Small 2 is the Apache-clean coding fallback beside Devstral 2.
- Code LLaMA-Secure is blocked until an exact public model ID, license, and provenance are verified.
- Intent-BERT and LLaMA-Historian-tuned are historical/internal placeholders only; live rows use NexusNet-Intent-BERT-v0 and NexusNet-Historian-v0.
- LFM2 remains a license-gated efficiency coach, not a correctness, safety, or high-risk decision teacher.
- DreamerV3 and MuZero are algorithmic simulation professors, not ordinary LLM teachers.
- Security training must use LLM teachers plus deterministic validators such as CodeQL, Semgrep/OpenGrep, OWASP LLM Top 10, and unit/security tests.

## Pairing Grammar

Every NexusNet subsystem uses the same teacher grammar, scaled to its brain level.

| Role | Function |
| --- | --- |
| Primary Professor | Main domain teacher for Stage 1 domain professor distillation. |
| Secondary Contrast Teacher | Independent comparison teacher for Stage 2 dual-teacher contrast. |
| Skeptical Examiner | Critique Expert, CritiqueAO, EvalsAO, or GovernanceAO review path that challenges weak synthesis and promotion claims. |
| Optional Efficiency Coach | LFM2 only where explicitly allowed; it can improve efficiency, routing, memory budget, or tool protocol, but cannot override correctness, safety, grounding, or high-risk review. |
| Teacher Council | Additional experts, AOs, or validators activated when the task crosses domains or affects protected state. |
| Sandbox/Eval Gate | Closed sandbox, benchmark suite, policy review, checkpoint/rewind proof, and human/governance approval before protected mutation. |
| Federation Gate | Sanitized artifact and metadata learning only. No raw private prompts, outputs, files, paths, screenshots, secrets, personal identifiers, or unredacted logs. |

Teacher sources must be open-source, open-weight, or otherwise distillation-approved for the intended training, fine-tuning, derivative, or internal-improvement use. Historical teacher names are provenance anchors only until current licenses are verified. DeepSeek-style permissive or explicit output-training rights fit the intended lane only after exact model, API channel, and version-specific license review. Any teacher source with anti-distillation, anti-competitive-model, no-output-training, no-automated-extraction, or unclear rights is blocked from NexusNet training and distillation.

## O-Level Teacher Pairings

O-level brains are smaller NexusNet-style brains beneath the Root NexusBrain and above AOs. They are functional routing/governance views over the same hive substrate, not silos.

| O brain | Primary Professor | Secondary Contrast Teacher | Skeptical Examiner | Supporting council | Graduation focus |
| --- | --- | --- | --- | --- | --- |
| Root NexusBrain O | Qwen3-30B-A3B | Mistral Small 4 | Critique Expert plus GovernanceAO | DeepSeek-V4-Pro, DeepSeek-R1-Distill-Qwen-32B, Router Expert, Meta Reasoner Expert | global task routing, sparse activation, budget/risk arbitration, final answer policy |
| Governance O | DeepSeek-V4-Pro | Qwen3-30B-A3B | Critique Expert plus SafetyAO | DeepSeek-R1-Distill-Qwen-32B compact contrast, Security Expert, EvalsAO, Checkpoint/Rewind gate | policy, promotion authority, rollback discipline, human approval gates |
| Planning O | Qwen3-30B-A3B | Mistral Small 4 | Critique Expert | Strategist Expert, Meta Reasoner Expert, ConsequenceAO, Mistral Medium 3.5 license-gated council | decomposition, dependency graph, route planning, escalation timing |
| Execution O | Qwen3-Coder-Next | Devstral 2 | Critique Expert plus EvalsAO | Coder Expert, Builder Expert, Toolsmith Expert, RuntimeAO | code/tool execution, build-test loops, sandboxed implementation |
| Research O | Qwen3-30B-A3B | Kimi K2.6 | Critique Expert plus EvalsAO | Researcher Expert, Analyst Expert, Critic Historian Expert | source synthesis, assimilation target triage, contradiction handling |
| Memory Context O | NexusNet-RecurrentMemory-v0 | DeepSeek-V4-Flash | Critique Expert plus MemoryAO | Memory Weaver Expert, Router Expert, LFM2, Federated Influence Ledger | retrieval budgeting, provenance, temporal truth, privacy-preserving memory use |
| Runtime O | DeepSeek-V4-Flash | Qwen3-30B-A3B | Critique Expert plus GovernanceAO | Router Expert, Toolsmith Expert, LFM2, DeepSeek-V2-Lite fallback, Backend Quantization Execution Ledger | runtime selection, fallback, quantization trials, backend evidence |
| Dream Evolution O | DreamerV3 algorithmic professor | MuZero algorithmic professor | Critique Expert plus EvalsAO | Simulation Expert, Meta Reasoner Expert, TrainingAO, SelfTrainingAO | recursive dreaming, candidate generation, adversarial scenarios, improvement proposals |
| Federation O | DeepSeek-V4-Flash | Qwen3-30B-A3B | GovernanceAO plus SafetyAO | FederationAO, MemoryAO, Security Expert, EvalsAO, DeepSeek-V2-Lite fallback | sanitized federation, trust scoring, poisoning checks, differential privacy knobs |
| Multimodal Perception O | NVIDIA Nemotron 3 Nano Omni | Qwen3-VL | Critique Expert plus EvalsAO | Vision Expert, Audio Expert, Multimodal Professor, SafetyAO | image, audio, video, document, GUI, and mixed-modality teacher evidence |
| VisualOps Productization O | Mistral Small 4 | Qwen3-30B-A3B | GovernanceAO plus Critique Expert | VisualOpsAO, PackagingAO, Conversationalist Expert, Instructor Expert | cockpit clarity, operator proof, buyer readiness, replay visibility |

## AO-Level Teacher Pairings

AO-level brains coordinate local workflows and proposals. They cannot bypass the Root NexusBrain, governance gates, sandbox/eval proof, checkpoint/rewind, or human approval. Their pairings are derived v0 pairings from the live teacher registry and source canon until a dedicated AO runtime registry is promoted.

| AO | Parent O view | Primary Professor | Secondary Contrast Teacher | Skeptical Examiner | Optional Efficiency Coach | Expert council |
| --- | --- | --- | --- | --- | --- | --- |
| PlanningAO | Planning O | Qwen3-30B-A3B | Mistral Small 4 | Critique Expert | none | Strategist Expert, Meta Reasoner Expert, Router Expert, Mistral Medium 3.5 license-gated council |
| GovernanceAO | Governance O | DeepSeek-V4-Pro | Qwen3-30B-A3B | Critique Expert | none | Security Expert, EvalsAO, DeepSeek-R1-Distill-Qwen-32B compact contrast, Checkpoint/Rewind gate |
| CodingAO | Execution O | Qwen3-Coder-Next | Devstral 2 | Critique Expert | none | Coder Expert, Builder Expert, Toolsmith Expert |
| RuntimeAO | Runtime O | DeepSeek-V4-Flash | Qwen3-30B-A3B | Critique Expert | LFM2 | Router Expert, Toolsmith Expert, DeepSeek-V2-Lite fallback, Backend Quantization Execution Ledger |
| EvalsAO | Governance O | DeepSeek-V4-Pro | Qwen3-30B-A3B | Critique Expert | none | Analyst Expert, Critique Expert, Simulation Expert |
| ResearchAO | Research O | Qwen3-30B-A3B | Kimi K2.6 | Critique Expert | none | Researcher Expert, Analyst Expert, Critic Historian Expert |
| MemoryAO | Memory Context O | NexusNet-RecurrentMemory-v0 | DeepSeek-V4-Flash | Critique Expert | LFM2 | Memory Weaver Expert, Router Expert, Federated Influence Ledger |
| DreamAO | Dream Evolution O | DreamerV3 algorithmic professor | MuZero algorithmic professor | Critique Expert | none | Simulation Expert, Meta Reasoner Expert, EvalsAO |
| CritiqueAO | Governance O | DeepSeek-V4-Pro | Qwen3-30B-A3B | GovernanceAO | none | Critique Expert, Analyst Expert, Security Expert |
| ConsequenceAO | Planning O | DeepSeek-V4-Pro | Qwen3-30B-A3B | Critique Expert | none | Meta Reasoner Expert, Strategist Expert, SafetyAO |
| SafetyAO | Governance O | Devstral 2 | Qwen3-Coder-Next | Critique Expert | LFM2 | Security Expert, GovernanceAO, EvalsAO, CodeQL, Semgrep/OpenGrep, OWASP LLM Top 10 |
| TrainingAO | Dream Evolution O | Qwen3-30B-A3B | DeepSeek-R1-Distill-Qwen-32B | Critique Expert | none | Curriculum Architect, Instructor Expert, EvalsAO |
| SelfTrainingAO | Dream Evolution O | Qwen3-30B-A3B | DeepSeek-R1-Distill-Qwen-32B | GovernanceAO plus Critique Expert | LFM2 when optimizing route/memory budgets | Curriculum Architect, DreamAO, EvalsAO |
| ProtocolAO | Runtime O | Devstral 2 | Qwen3-Coder-Next | Critique Expert | LFM2 | Toolsmith Expert, Security Expert, RuntimeAO |
| VisualOpsAO | VisualOps Productization O | Mistral Small 4 | Qwen3-30B-A3B | GovernanceAO | none | Conversationalist Expert, Instructor Expert, Analyst Expert |
| FederationAO | Federation O | DeepSeek-V4-Flash | Qwen3-30B-A3B | SafetyAO plus GovernanceAO | LFM2 for metadata budget only | Memory Weaver Expert, Security Expert, EvalsAO |
| PackagingAO | VisualOps Productization O | Mistral Small 4 | Qwen3-30B-A3B | GovernanceAO | none | Instructor Expert, Conversationalist Expert, Builder Expert |
| MaintenanceAO | Runtime O | DeepSeek-V4-Flash | Qwen3-30B-A3B | RuntimeAO plus GovernanceAO | LFM2 | Router Expert, Memory Weaver Expert, Toolsmith Expert |
| EvolutionAO | Dream Evolution O | DreamerV3 algorithmic professor | Qwen3-30B-A3B | Critique Expert plus EvalsAO | none | Simulation Expert, Meta Reasoner Expert, SelfTrainingAO |
| BrowserAO / Local Browser Memory Agent | Research O | Qwen3-30B-A3B | Kimi K2.6 | SafetyAO plus Critique Expert | LFM2 for local metadata budgeting only | Researcher Expert, Memory Weaver Expert, Security Expert |

## Expert-Level Teacher Pairings

These 19 expert pairings are registry-backed by `nexusnet/teachers/teacher_registry_v2026_live.yaml`. Each expert follows the four-stage training regimen: primary professor distillation, dual-teacher contrast, skeptical examination, and dream/self-evolution.

| Expert | Primary Professor | Secondary Contrast Teacher | Skeptical Examiner | Optional Efficiency Coach | Training/eval focus |
| --- | --- | --- | --- | --- | --- |
| Coder Expert | Qwen3-Coder-Next | Devstral 2 | Critique Expert | none | repo navigation, multi-file patching, tests green after edits, terminal recovery |
| Strategist Expert | Qwen3-30B-A3B | Mistral Small 4 | Critique Expert | none | task decomposition, objective trees, dependency planning, long-horizon planning |
| Analyst Expert | DeepSeek-V4-Pro | Qwen3-30B-A3B | Critique Expert | none | evidence weighting, diagnosis, structured comparison, benchmark-grade evaluation |
| Researcher Expert | Qwen3-30B-A3B | Kimi K2.6 | Critique Expert | none | multi-source synthesis, contradiction handling, document reasoning, long-context study |
| Critique Expert | DeepSeek-V4-Pro | Qwen3-30B-A3B | Critique Expert | none | adversarial judging, rubric scoring, promotion review, rollback criticism |
| Conversationalist Expert | Mistral Small 4 | Qwen3-30B-A3B | Critique Expert | none | tone control, dialogue continuity, persona stability, helpfulness without drift |
| Toolsmith Expert | Devstral 2 | Qwen3-Coder-Next | Critique Expert | LFM2 | tool schemas, tool-chain recovery, sandbox-safe execution, API discipline |
| Security Expert | Devstral 2 | Qwen3-Coder-Next | Critique Expert | LFM2 | misuse-case generation, safe tool use, secure patching, exploit-to-mitigation reasoning, validator-backed review |
| Memory Weaver Expert | NexusNet-RecurrentMemory-v0 | DeepSeek-V4-Flash | Critique Expert | LFM2 | episodic/semantic linkage, compression, retrieval budgeting, memory-safe stitching |
| Meta Reasoner Expert | DeepSeek-R1-Distill-Qwen-32B | Qwen3-30B-A3B | Critique Expert | none | self-reflection, synthesis, conflict arbitration, policy-aware reasoning |
| Router Expert | DeepSeek-V4-Flash | Qwen3-30B-A3B | Critique Expert | LFM2 | route selection, budget/risk typing, fallback choice, capsule gating |
| Linguist Expert | Qwen3-30B-A3B | BLOOMZ | Critique Expert | none | multilingual generation, translation nuance, register control, cross-lingual paraphrase |
| Vision Expert | Qwen3-VL | Kimi K2.6 | Critique Expert | none | OCR/layout grounding, chart/UI/screenshot reasoning, image task grounding |
| Audio Expert | Voxtral Small | Whisper-Large-V3 | Critique Expert | none | ASR, spoken instruction grounding, audio-to-task routing, timestamp sensitivity |
| Simulation Expert | DreamerV3 algorithmic professor | MuZero algorithmic professor | Critique Expert | none | world-model rollouts, counterfactuals, uncertainty planning, dream scenario generation |
| Builder Expert | Devstral 2 | Mistral Small 4 | Critique Expert | none | feature assembly, API/UI scaffolding, build-debug-rebuild loops, artifact validation |
| Instructor Expert | Qwen3-30B-A3B | Mistral Small 4 | Critique Expert | none | Socratic questioning, scaffolding, remediation, mastery checks, lesson pacing |
| Intent Mapper Expert | NexusNet-Intent-BERT-v0 | Qwen3-30B-A3B | Critique Expert | none | intent classification, ambiguity reduction, risk/domain typing, plan normalization |
| Critic Historian Expert | NexusNet-Historian-v0 | DeepSeek-V4-Pro | Critique Expert | none | chronology repair, source conflict resolution, temporal consistency, historical critique |

## Auxiliary Teacher Paths

| Auxiliary path | Primary Professor | Secondary Contrast Teacher | Skeptical Examiner | Optional Efficiency Coach | Status |
| --- | --- | --- | --- | --- | --- |
| Curriculum Architect | Qwen3-30B-A3B | DeepSeek-R1-Distill-Qwen-32B | Critique Expert | LFM2 | strong accepted direction, auxiliary, not part of the authoritative 19-expert roster |
| Multimodal Professor | NVIDIA Nemotron 3 Nano Omni | Qwen3-VL | Critique Expert | none | strong accepted direction, optional teacher/perception adapter, license/hardware review required |

## Promotion And Retirement Rules

1. A new expert, AO, O, or merged Mini-NexusNet brain starts as a temporary child candidate.
2. First useful output does not make a child permanent. It only creates evidence.
3. Permanent retention requires Ivy-grade teacher review, parent comparison, sandbox/eval evidence, regression proof, rollback plan, checkpoint/rewind proof, and operator/governance approval.
4. If the child greatly outperforms one parent, the other parent, or both, only the respective outperformed parent is retired from primary routing.
5. Parent retirement is archive-not-delete. Retired parents remain provenance-preserved and rollback-restorable.
6. Teacher retirement from runtime is allowed only after teacher-surpass and post-teacher stability evidence exists.
7. Recursive Neural Dreaming can propose improvements anywhere in the hive, but every dream-derived change remains shadow-only until low-temperature critique, sandbox/eval, governance, checkpoint, and human approval pass.
8. Federated learning influences shadow priors through sanitized artifact and metadata packets only. Global promotion requires secure aggregation, poisoning/anomaly checks, privacy audit, sandbox replay, benchmark proof, and human/governance approval.

## Implementation Notes

- The expert layer is currently the most registry-backed layer.
- The AO and O pairings in this document are canon-aligned v0 pairings derived from the existing expert registry, AO canon, and post-book substrate rules.
- A future runtime registry should promote these O/AO rows into structured machine-readable YAML after sandbox/eval proof.
- Pairings are allowed to activate sparse subsets. Sparse routing saves compute, but does not isolate nodes from hive-wide neuroplasticity, replay, governance, or federation evidence.
- Any future pairing change that was not present in the source book must receive a new addendum and ledger entry before it is canon-complete.
