# NexusNet Patent Architecture Dossier - 2026-05-12

Status: all-in-one technical orientation document for patent preparation.

This document explains NexusNet as an invention candidate. It is written to help a patent reviewer, technical advisor, or future implementation agent understand the whole system without reading every raw transcript first.

This is not legal advice, not a patentability opinion, and not a final claim set. A registered patent practitioner should review the claims, ownership, inventorship, disclosure timing, prior art, eligibility, and enablement before filing.

## One-Sentence Invention Thesis

NexusNet is a brain-first artificial intelligence harness that routes tasks and candidate improvements through a neural core, typed hive nodes, a Neural Bus, a Cortex router, multi-plane memory, recurrent deliberation, sandbox/evaluation gates, checkpoint/rewind ledgers, and governance-controlled promotion so that model use, tool use, memory, self-improvement, visual operations, and federated learning remain traceable, reversible, and policy-bound.

## What NexusNet Is

NexusNet is not merely a chatbot wrapper. It is intended to be a neural-network-like harness around AI capabilities, tools, memory, runtimes, evaluators, and growth systems.

The live repo and canon divide the system into three layers:

| Layer | Meaning | Patent relevance |
| --- | --- | --- |
| NexusNet | Brain/core, wrapped inference path, cognitive substrate, memory, dreaming, growth, teacher replacement path | Main invention center |
| AOs | Assistant Orchestrators coordinating domain workflows, safety, memory, runtime, evaluation, and training loops | Hive node and workflow embodiments |
| Nexus | Host/platform shell exposing API, UI, ops, governance, storage, and compatibility layers | Delivery and operator-control embodiments |

The important architectural rule is that user-facing and system-affecting behavior should remain mediated by `NexusBrain` or equivalent brain authority. UI actions, model providers, tool adapters, protocol adapters, runtime routers, training jobs, and autonomous update loops should not bypass the brain-mediated route and policy path.

## What NexusNet Is Not

For patent drafting and product claims, do not describe current NexusNet as:

- a finished independent foundation model
- an unsandboxed self-modifying AI
- a consciousness or sentience system
- whole-brain emulation
- a direct replacement for all model providers today
- a system that has already proven native model superiority
- a system where research candidates can automatically mutate production behavior

The current stronger claim is a governed AI harness and developmental substrate with code-backed pieces, candidate pieces, and future embodiments.

## Core Source Basis

The current source basis is:

| Source | Role |
| --- | --- |
| `README.md` | Public repo identity, package split, canonical API and code layout |
| `docs/NEXUSNET_CANON_MATRIX.md` | Constitutional split between NexusNet, AOs, and Nexus |
| `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md` | Exhaustive project-history source map and concept index |
| `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md` | Later locked clarifications and post-book architecture deltas |
| `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md` | Candidate and locked assimilation ledger |
| `patent/nexusnet_micro_entity_packet_2026-05-01/` | Existing patent drafting packet |
| `docs/core_brain_execution.md` | Live brain execution order and trace contract |
| `docs/core_evidence_driven_execution.md` | Evidence-driven bounded native execution |
| `docs/core_promotion_replacement_linkage.md` | Promotion linkage and governed action contract |
| `docs/compiled_knowledge_artifact_layer.md` | KAC artifact contract and refs-only runtime boundary |
| `docs/SELF_IMPROVEMENT_LAYER.md` | Governed self-improvement candidate workflow |
| `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md` | Hive Neural Substrate design |
| `docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md` | Current state versus full spec packet |

## Existing Patent Packet

The existing patent packet lives at:

`patent/nexusnet_micro_entity_packet_2026-05-01/`

The current packet title is:

`Hive Mind Harness for Artificial Intelligence with Governed Sparse Routing`

Key packet documents:

- `03_INVENTION_DISCLOSURE_RECORD.md`
- `04_NONPROVISIONAL_SPECIFICATION_DRAFT.md`
- `05_CLAIMS_DRAFT.md`
- `06_ABSTRACT_DRAFT.md`
- `07_DRAWING_BRIEF_DESCRIPTION_AND_REFERENCE_NUMERALS.md`
- `08_PRIOR_ART_AND_DIFFERENTIATOR_WORKSHEET.md`
- `11_SOURCE_CANON_TO_CLAIM_SUPPORT_CHART.md`

Independent claim families already drafted:

- Claim 1: system
- Claim 15: method
- Claim 23: computer-readable medium

## Main Patentable System Model

The patentable system model can be described as a governed AI harness made of these elements.

### 1. Neural Core Service

The neural core service is the central decision authority. It mediates task routing, memory assembly, policy application, expert selection, generation, critique, evaluation, trace capture, and final output metadata.

Live sources:

- `nexusnet/core/brain.py`
- `docs/core_brain_execution.md`
- `tests/test_nexusnet_brain.py`
- `tests/test_nexusnet_core_pivot.py`

Important behavior:

- starts before attached model work
- records startup/hardware/runtime/memory/fusion context
- routes generation through `NexusBrain.generate()`
- records core execution artifacts
- exposes read-only inspection through `/ops/brain/core`, trace endpoints, and wrapper-surface state

### 2. Hive Node Registry

The hive node registry stores typed records for operational nodes, including AOs, experts, Mini-NexusNets, memory banks, model adapters, tool adapters, evaluators, sandbox runners, policy gates, and training or curator components.

Patent-relevant fields include:

- node type
- capabilities
- allowed tools
- write scope
- privacy scope
- concurrency safety
- memory references
- certification state
- quarantine state
- scorecard references
- genome or lineage reference

Live sources:

- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`
- `nexusnet/hive/substrate.py`
- `nexusnet/canon/realization.py`
- `tests/test_hive_neural_substrate.py`
- `tests/test_node_registry_snapshot.py`

### 3. Neural Bus And Typed Hive Activations

The Neural Bus carries typed activations between nodes. A hive activation can include intent, task vector, risk vector, capability vector, memory refs, policy labels, confidence, novelty, privacy class, and trace refs.

Patent relevance:

- gives the harness a neural-network-like signal substrate
- allows traceable message passing between AI, memory, tool, policy, runtime, and eval components
- supports replay, debugging, and operator review

Live sources:

- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`
- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_network_internals.py`

### 4. Cortex Router And Sparse Expert Activation

The Cortex router selects a sparse subset of nodes for a task based on capability, confidence, risk, privacy, cost, latency, permission, certification, quarantine state, memory access, and historical reliability.

This is a harness-level analogue of sparse MoE routing. It does not only route tokens inside a model. It routes operational components such as AOs, experts, tools, models, memory banks, evaluators, and sandboxes.

Live sources:

- `nexusnet/moe/cortex/service.py`
- `nexusnet/moe/router_alignment/service.py`
- `nexusnet/moe/fusion/service.py`
- `docs/expert_router_alignment.md`
- `tests/test_expert_routing.py`
- `tests/test_hive_neural_substrate.py`

### 5. Multi-Plane Memory And Engram Layer

The memory system separates source canon, compact canon, post-book addenda, assimilation ledgers, project docs, trace ledgers, skill registries, expert genome registries, evaluation histories, provider scorecards, sandbox artifacts, and federated lessons.

Every retrieved item should carry provenance, status, freshness, permission, and source-quality labels.

Live sources:

- `nexusnet/memory/planes.py`
- `nexusnet/memory/engram_index.py`
- `nexusnet/memory/quality_ledger.py`
- `nexusnet/knowledge/compiler.py`
- `docs/compiled_knowledge_artifact_layer.md`
- `tests/test_engram_memory_index.py`
- `tests/test_memory_quality_ledger.py`
- `tests/test_knowledge_artifact_compiler.py`

### 6. Recurrent Deliberation And Exit Gates

NexusNet is designed to update internal harness state through one or more loops before external action. A loop can involve routing, memory lookup, expert computation, critique, policy checks, evaluator signals, and blackboard updates.

Exit conditions can include:

- confidence threshold
- risk threshold
- policy gate result
- disagreement resolution
- memory sufficiency
- maximum loop count
- operator checkpoint requirement
- policy forced stop

Live sources:

- `docs/core_evidence_driven_execution.md`
- `nexusnet/core/execution_policy.py`
- `nexusnet/core/native_execution.py`
- `nexusnet/core/self_review.py`
- `nexusnet/growth/production_spine.py`
- `tests/test_self_review_gate.py`
- `tests/test_nexusnet_core_execution_fusion.py`

### 7. Immune Governance Kernel

The governance layer blocks routes or candidate updates that lack required permissions, provenance, sandbox evidence, eval evidence, trusted protocol identity, artifact provenance, or checkpoint evidence.

Existing rule families include:

- write-enabled tools require sandboxing
- memory updates require provenance
- training and promotion require approval/eval evidence
- protocol adapters require trust envelopes
- artifact promotion requires provenance and trust state
- codegraph/test expectations must be respected

Live sources:

- `nexusnet/policy/kernel.py`
- `nexusnet/security/`
- `nexusnet/protocols/`
- `docs/core_promotion_replacement_linkage.md`
- `tests/test_policy_kernel.py`
- `tests/test_protocol_trust_registry.py`
- `tests/test_artifact_trust_registry.py`

### 8. Checkpoint And Rewind Ledger

The checkpoint/rewind concept requires pre-action rollback metadata before writes, promotions, route changes, candidate activation, or release pointer changes.

Patent relevance:

- autonomous or semi-autonomous changes become reversible
- failed attempts become side-barred evidence instead of invisible loss
- promotion claims can be tied to snapshots, rollback refs, and trace IDs

Live sources:

- `nexusnet/hive/substrate.py`
- `nexusnet/growth/production_spine.py`
- `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
- `tests/test_nexusnet_production_spine.py`

### 9. Sandboxed Self-Assimilation

Candidate improvements are not directly installed. A candidate is source-pinned, license-checked, privacy-classified, converted into a capability genome or structured candidate, tested in a sandbox, compared against baselines, evaluated for security/regressions, and then promoted, rejected, blocked, or side-barred.

Live sources:

- `nexusnet/growth/engine.py`
- `nexusnet/growth/production_spine.py`
- `nexusnet/core/self_review.py`
- `nexusnet/core/self_improvement/`
- `docs/SELF_IMPROVEMENT_LAYER.md`
- `docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md`
- `tests/test_growth_lifecycle_orchestrator.py`
- `tests/test_hive_model_growth_engine.py`
- `tests/test_self_improvement_layer.py`

### 10. VisualOps And Control Panel

VisualOps exposes the system state to an operator. It should show brain path traces, selected/rejected nodes, route decisions, memory lookups, policy blocks, sandbox outcomes, eval scores, checkpoint refs, federation state, and readiness. Missing telemetry must be shown as unavailable instead of fabricated.

Live sources:

- `ui/control-panel/app.js`
- `ui/control-panel/index.html`
- `ui/visualizer/app.js`
- `nexusnet/canon/realization.py`
- `nexusnet/ui_surface/surface.py`
- `nexusnet/visuals/layout.py`
- `tests/test_nexusnet_visualizer.py`
- `tests/test_video_assimilation_control_panel.py`

### 11. Federated Learning Boundary

NexusNet can share approved, redacted deltas such as route-score summaries, expert scorecards, eval summaries, runtime scorecards, or failure signatures. It should block raw private prompts, secrets, local file contents, proprietary code, and unredacted transcripts unless explicitly approved.

Live sources:

- `nexusnet/federation/`
- `nexusnet/hive/substrate.py`
- `patent/nexusnet_micro_entity_packet_2026-05-01/04_NONPROVISIONAL_SPECIFICATION_DRAFT.md`
- `patent/nexusnet_micro_entity_packet_2026-05-01/05_CLAIMS_DRAFT.md`

### 12. Native Model Evolution Path

The long-horizon path is to use traces, expert scorecards, eval results, dream outputs, and federated aggregate lessons as training material for later native MoE-style model evolution. This should be described carefully as an embodiment or growth path unless the exact feature is code-backed and tested.

Live sources:

- `nexusnet/growth/production_spine.py`
- `nexusnet/hive/substrate.py`
- `nexusnet/foundry/`
- `docs/core_promotion_replacement_linkage.md`
- `tests/test_nexusnet_production_spine.py`

## Operational Walkthrough - Normal User Task

1. Operator submits a task through the API, UI, CLI, or host shell.
2. The input is converted into a typed activation with intent, risk, capability, privacy, memory, and policy metadata.
3. The neural core wakes or reuses current startup/runtime state.
4. Memory context is assembled from multi-plane memory and KAC artifacts where allowed.
5. The Cortex router selects a sparse active set of AOs, experts, tools, models, evaluators, or policy nodes.
6. Recurrent deliberation may run one or more internal loops.
7. The execution policy determines proposed mode and effective governed mode.
8. Native guidance can be suppressed, shadowed, challenger-shadowed, planner-live, or guarded-live depending on evidence.
9. Attached-model generation or internal expert execution proceeds under the effective mode.
10. Critique, eval, and policy evidence are recorded.
11. The output/action subsystem emits an approved output only after gates pass.
12. The trace, core execution artifact, memory refs, and operator-visible status are persisted.

## Operational Walkthrough - Candidate Improvement

1. A candidate is found through operator request, research monitor, repo scan, video, paper, product review, failure trace, or eval gap.
2. Source identity is pinned.
3. License, privacy, provenance, and security status are checked.
4. The candidate is converted into a structured candidate record, genome, training candidate, route update, prompt policy candidate, or memory update candidate.
5. KAC or memory context may be attached as refs-only context.
6. The candidate is run in a sandbox or deterministic proof path where available.
7. Teacher council, self-review, eval registry, verifier search, policy kernel, artifact trust, and memory quality gates contribute evidence.
8. The candidate is classified as rejected, blocked, archived, shadow, canary-requested, active-requested, or side-barred.
9. A checkpoint/rollback reference is required before any production-affecting action.
10. Human/operator approval remains required for protected mutations and active promotion.

## Claim Element Map

| Patent element | Why it matters | Current source support |
| --- | --- | --- |
| Brain-mediated core | Prevents model/tool/UI bypass | `nexusnet/core/brain.py`, `docs/core_brain_execution.md` |
| Hive node registry | Turns components into typed harness nodes | `nexusnet/hive/substrate.py`, Hive substrate design |
| Neural Bus | Makes activations traceable and replayable | Hive substrate design, hive substrate tests |
| Cortex router | Sparse operational routing beyond token-level MoE | `nexusnet/moe/cortex/service.py`, router alignment docs |
| Multi-plane memory | Avoids flat prompt-only context | `nexusnet/memory/planes.py`, KAC, memory quality ledger |
| Recurrent deliberation | Adds internal loops and exit gates before action | execution policy, native execution, self-review |
| Immune governance | Blocks unsafe routes, writes, protocols, and promotions | `nexusnet/policy/kernel.py`, security and protocol registries |
| Checkpoint/rewind | Makes changes reversible and auditable | hive substrate, production spine |
| Sandboxed assimilation | Prevents direct self-installation of untrusted improvements | growth engine, production spine, self-improvement layer |
| VisualOps | Gives operator visibility into brain path and readiness | Control Panel, visualizer, canon realization scorecards |
| Federated boundary | Allows learning from redacted deltas, not raw private data | federation modules, patent packet |
| Native MoE evolution | Uses traces and evidence for later native model growth | production spine, foundry, promotion linkage |

## Differentiators To Preserve

These are the most important technical differentiators to preserve in patent drafting:

1. Unified brain authority across model routing, memory, tools, runtime, evals, UI, and candidate updates.
2. Harness-level sparse routing across operational nodes, not only token routing inside one neural model.
3. Typed activations moving over a Neural Bus with trace refs and policy labels.
4. Multi-plane memory with provenance, status, freshness, and permission labels.
5. Recurrent deliberation with exit gates before external action.
6. Candidate improvement lifecycle with source pinning, license/privacy/security review, sandbox, eval, checkpoint, and governance.
7. Checkpoint/rewind ledgers for reversible AI-assisted changes.
8. VisualOps surfaces that display readiness, selected nodes, blocked nodes, policy blocks, and replay evidence.
9. Federated learning as redacted scorecard/delta exchange, not raw private prompt or code export.
10. A future native model evolution path built from governed traces, dream outputs, evals, and expert scorecards.

## Current Implementation Maturity

Use this maturity scale:

- M0: absent
- M1: documented/spec-only
- M2: code scaffold or registry exists
- M3: code plus tests or UI-backed scorecards exist, still gated/shadow/replay-first
- M4: active production behavior with live execution, rollback, tests, and operator promotion path

Current audit summary:

| Area | Maturity | Notes |
| --- | --- | --- |
| Brain-first core execution | M3 | Code and tests exist; full-suite status still needs current verification |
| Evidence-driven execution policy | M3 | Bounded native modes and promotion linkage are represented |
| KAC and source-ref gates | M3 | Strong refs-only boundary and tests |
| Self-improvement candidate queue | M3 | Governed candidates, no direct model fine-tuning |
| Hive neural substrate | M2-M3 | Large code and tests exist, but many pieces remain ledger/scorecard/shadow-first |
| Growth and production spine | M3 | Sandbox proof, teacher council, sealed eval, replay, runtime foundry paths exist |
| Control Panel/VisualOps | M2-M3 | Broad scorecard surface, not all live benchmark lanes |
| Federated learning | M1-M2 | Boundary and hooks exist; production federation is not proven |
| Developmental cortex kernel | M1-M2 | Ingredients exist, unified kernel not present |
| Native model independence | M1-M2 | Future growth path, not current product claim |

## What Can Be Claimed More Safely

More supportable current claims:

- computer-implemented governed AI harness
- neural core service mediating task execution
- typed hive node registry
- neural bus / typed activation routing
- sparse operational component routing
- multi-plane provenance/status memory
- governed candidate assimilation lifecycle
- sandbox/eval/checkpoint promotion path
- operator-visible control panel for traces, gates, and readiness
- redacted federated delta boundary

Claims that need narrower wording or stronger support:

- fully autonomous self-improvement
- native model replacement
- active federated learning across real deployments
- production-grade browser/desktop agent control
- consciousness-inspired or whole-brain analogies
- any statement that all future developmental cortex pieces are already live

## Patent Drafting Risks

### Inventorship And Ownership

The invention disclosure record must be filled with every person who contributed to claimed technical concepts. Employment, contractor, investor, university, or assignment issues must be reviewed before filing.

### Public Disclosure Timing

If any architecture was publicly posted, sold, offered, demoed, or shared, record dates and scope in the disclosure record. Timing can matter for filing strategy.

### Enablement

Claims should not overreach beyond what the specification enables. The strongest packet language should focus on data structures, gates, ledgers, routes, and workflows, not only outcomes such as "self-improves."

### Prior Art

The differentiator worksheet should be expanded with targeted searches for:

- AI agent frameworks
- RAG and memory systems
- multi-agent orchestration
- model routing and MoE systems
- autonomous coding sandboxes
- AI governance and eval platforms
- federated learning systems
- AI control panels and observability tools

### Shareability And Privacy

The exhaustive canon book is useful as source evidence, but it contains historical raw export material, old sandbox links, and local path references. Treat it as internal source material until a shareability pass produces a sanitized evidence bundle.

The patent packet itself is cleaner, but it should still be reviewed before external sharing.

### Git State

The working tree is not clean. The current dossier describes the live workspace as audited on 2026-05-12, not a clean release tag. Patent support charts should eventually point to a clean commit or archived evidence snapshot.

## Repo Evidence Snapshot From This Audit

Live audit facts on 2026-05-12:

- Current branch: `codex/knowledge-artifact-compiler`
- HEAD: `f1986e5 docs: record video assimilation verification`
- GitNexus indexed `NexusNet` on 2026-05-06 with 1257 files, 21746 symbols, and 211 processes.
- Current Git status is heavily dirty:
  - 46 tracked modified files
  - 387 untracked files
  - most untracked volume is under `docs/`, `nexusnet/`, `tests/`, and `patent/`
- High-confidence token/key pattern scan over selected project text/code paths did not find obvious API keys or private-key blocks.
- Local path/shareability scan found internal path or sandbox-history references in several docs, especially the exhaustive canon book and selected research/planning docs.

## Recommended Patent Prep Actions

1. Fill `03_INVENTION_DISCLOSURE_RECORD.md` completely.
2. Decide provisional versus nonprovisional path using `09_FILING_CHECKLIST_AND_PATENT_CENTER_STEPS.md`.
3. Review and narrow `05_CLAIMS_DRAFT.md` with a practitioner.
4. Update `11_SOURCE_CANON_TO_CLAIM_SUPPORT_CHART.md` after Git cleanup so source refs point to a clean commit or evidence snapshot.
5. Create a sanitized share bundle containing:
   - patent packet
   - this dossier
   - reading walkthrough
   - selected canon excerpts
   - source support chart
   - selected code/test evidence
   - no raw private transcript material unless intentionally included
6. Expand `08_PRIOR_ART_AND_DIFFERENTIATOR_WORKSHEET.md` with actual search results and dates.
7. Separate implemented, candidate, and future embodiment language before filing.

## Bottom Line

NexusNet's patent center of gravity is a governed neural-harness architecture: a brain-first AI system that treats tools, models, memory, experts, evaluators, sandboxes, UI surfaces, and growth loops as typed, traceable, policy-bound hive nodes. The strongest invention narrative is not "an AI that magically improves itself." It is a concrete, inspectable, reversible, gated architecture for AI execution and self-improvement, with a future path toward native model evolution.
