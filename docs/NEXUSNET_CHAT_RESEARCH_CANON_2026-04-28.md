# NexusNet Chat And Research Canon - Decision Basis

Date compiled: 2026-04-28

Purpose: compile the fuller NexusNet ChatGPT project capture, the prior synthesis artifacts, the 2026 research refresh, and the current repo implementation direction into one decision-basis document. This is not a verbatim transcript. The raw transcript archive remains the exhaustive record. This document is the consolidated map of what the chats appear to have decided, what they repeatedly reinforced, what the research update changed, and what still needs a final lock.

## 1. Source Coverage And Reliability

This document supersedes the earlier `NEXUSNET_38_CHAT_IDEA_SYNTHESIS.md` as the working basis because that earlier synthesis was built from truncated browser-visible content. It remains a useful historical helper, but the stronger evidence set is the 2026-04-28 Playwright/Chrome capture.

Source hierarchy used here:

1. Fresh Playwright API capture from the ChatGPT project, with raw JSON, active-path transcripts, and all-message-node exports.
2. Fresh DOM top-scroll verification capture proving the visible conversation pages were forced to the top before DOM scraping.
3. Current repo canon docs and implementation docs in `docs/`, especially `NEXUSNET_CANON_MATRIX.md`, `core_brain_execution.md`, `multi_plane_memorynode.md`, `teachers_operational_flow.md`, `hardware_aware_core.md`, and `research/NEXUSNET_ASSIMILATION_PLAYBOOK_2026.md`.
4. Product-sweep worktree docs under `.worktrees/nexusnet-full-product-sweep/docs/`, especially `NEXUSNET_FULL_PRODUCT_SWEEP_ROADMAP.md` and `visuals/nexusnet_visual_spec.md`.
5. Prior 38-chat synthesis as a secondary historical reference only.
6. April 2026 research refresh as candidate evidence that must enter through the Assimilation Registry, not as silent replacement of locked NexusNet decisions.

Fresh capture summary:

- Project conversations discovered: 40.
- API conversations captured: 39.
- API active-path messages captured: 6,640.
- API all-mapping messages captured: 6,717.
- DOM conversations captured after scrolling to top: 39.
- DOM pages with `top_reached=true`: 39.
- DOM visible turns captured: 1,818.
- Known inaccessible/bugged chat: `Training LLM with ChatGPT`. The API path returned a conversation-length failure and the UI did not expose a full turn sequence. This remains an evidence gap.
- Browser DOM gaps are not treated as primary source gaps where the API mapping has complete message-node exports. API JSON is the stronger source for full conversation content.

Captured conversation map:

| No. | Conversation | API active messages | API all messages | Status |
| --- | --- | ---: | ---: | --- |
| 1 | Increasing Context Window | 109 | 109 | Captured |
| 2 | Mixtral DevStral NexusNet Setup | 89 | 89 | Captured |
| 3 | RL Libraries for NexusNet | 54 | 54 | Captured |
| 4 | NexusNet Architecture Review | 328 | 335 | Captured |
| 5 | NexusNet Implementation Plan | 252 | 252 | Captured |
| 6 | Neural network diagram explanation | 175 | 184 | Captured |
| 7 | Transformer-based Neural Network | 384 | 386 | Captured |
| 8 | AI Architecture Research | 216 | 216 | Captured |
| 9 | Project Chat Analysis | 211 | 211 | Captured |
| 10 | NexusNet Temporal AI Review | 48 | 48 | Captured |
| 11 | NexusNet diagram improvements | 46 | 46 | Captured |
| 12 | Project review request | 242 | 242 | Captured |
| 13 | MCP integration for NexusNet | 39 | 39 | Captured |
| 14 | Improving NexusNet with data | 42 | 42 | Captured |
| 15 | DeepEyesV2 review for NexusNet | 30 | 30 | Captured |
| 16 | Review AI Memory Features | 36 | 36 | Captured |
| 17 | Chat access details | 42 | 42 | Captured |
| 18 | NexusNet Annotation Toolkit Review | 49 | 53 | Captured |
| 19 | Review LLM-Council for NexusNet | 41 | 41 | Captured |
| 20 | Review Microsoft FARA framework | 40 | 40 | Captured |
| 21 | Improving NexusNet with Copilot | 39 | 39 | Captured |
| 22 | NexusNet final packaging | 81 | 81 | Captured |
| 23 | Compare Agent0 with NexusNet | 53 | 53 | Captured |
| 24 | LLM capabilities review | 40 | 40 | Captured |
| 25 | Agentic AI alliance review | 32 | 32 | Captured |
| 26 | Project Deep Dive Spec | 77 | 77 | Captured |
| 27 | Nemotron-Elastic-12B review | 35 | 35 | Captured |
| 28 | Review Bloom framework | 64 | 64 | Captured |
| 29 | Generate NexusNet blueprint | 82 | 82 | Captured |
| 30 | Review of Flash-DMD paper | 38 | 38 | Captured |
| 31 | NexusNet project overview | 135 | 141 | Captured |
| 32 | Neural network details | 94 | 114 | Captured |
| 33 | Audit nexusnet chats | 328 | 328 | Captured |
| 34 | LFM2 Deep Dive | 58 | 58 | Captured |
| 35 | Project Breakdown Request | 13 | 13 | Captured |
| 36 | AI Architecture Visualization | 39 | 39 | Captured |
| 37 | Codex Project Prompt | 866 | 866 | Captured |
| 38 | Research R-Zero integration | 1,154 | 1,156 | Captured |
| 39 | Project status overview | 966 | 966 | Captured |
| 40 | Training LLM with ChatGPT | Unknown | Unknown | Inaccessible/bugged |

Reliability stance:

- Decisions repeated across multiple chats and current repo docs are treated as strongest.
- Single-chat ideas are preserved as candidate or unresolved unless they were later implemented or repeatedly reaffirmed.
- External research is not treated as canon by default. It must be entered into a registry with source URL, verified date, license, maturity, replacement target, integration status, and evidence.
- Diagrams are explanatory views unless generated from validated registry/canon state.

## 1A. Post-Book Canon Addendum Rule

Locked decision: the 2026-04-28 complete canon book remains the historical source ledger for captured pre-addendum material. Anything added to NexusNet after that source book, if it was not already present there, must be recorded in a dated canon addendum or assimilation ledger before it can be treated as accepted NexusNet state.

Current post-book records:

- `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
- `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`

Required rule:

- Post-book additions do not silently rewrite the source book.
- Post-book additions must be labeled as locked clarification, candidate, code-backed candidate, live control plane, research-only, blocked, side-barred, rejected, or superseded.
- Post-book additions need source refs, original-book status, affected lanes, implementation refs where applicable, validation refs where applicable, security/policy gates, and rollback or sidebar semantics.
- Any future implementation that introduces a concept absent from the 2026-04-28 source book is not canon-complete until the addendum or ledger is updated.
- Candidate assimilation can improve NexusNet, but candidates do not replace locked canon without provenance, license, eval, security, sandbox, and promotion evidence.

## 2. Core Identity

Locked decision: NexusNet is a brain-first neural-core system. It is not a thin wrapper around MCP, RAG, a GUI, generic tools, or a prompt-routing shell.

The chats repeatedly converge on a stronger version of this point:

- NexusNet should behave as an intelligence substrate, not as a product shell that forwards prompts to outside models.
- Tools, MCP servers, RAG stores, UI panels, model providers, and protocol adapters are mediated capabilities.
- The neural core remains the cognition authority.
- The host shell can expose APIs, dashboards, security controls, deployment paths, and runtime surfaces, but it must not become the real brain.
- A model may be attached, taught from, distilled from, compared against, or routed through, but teacher models are not the permanent identity of the product.

Important correction from the later architecture-visualization discussion:

- NexusNet is not a single monolithic brain.
- It is brain-first, but internally it is a layered, hive-like intelligence structure.
- The missing layer in earlier diagrams was the Assistant Orchestrators Hive.
- Experts are not just decorative roles around one center. They form a specialization network.
- The emergent layer is a Shared Hive Mind where decisions are negotiated, routed, critiqued, and then governed by the core brain.

Canonical framing:

- `NexusNet` is the neural core, expert hive, memory/dream/training substrate, and native-growth path.
- `AOs` are the assistant-orchestrator layer coordinating domain workflows, memory, critique, safety, runtime, training, and UI-facing operations.
- `Nexus` is the platform/API/runtime shell that hosts and exposes NexusNet safely.

Required build implication:

- All user-facing generation and task execution must pass through `NexusBrain.generate()` or an equivalent canonical brain-mediated path.
- Anything outside that path is an adapter, not the intelligence center.
- The trace must show that the brain woke, selected posture, considered memory, selected expert/capsule routes, applied security policy, generated, critiqued, and emitted final metadata.

Operator/UI implication:

- Every UI panel must reinforce that the brain is the authority.
- Protocol, model, memory, training, and tool panels should show mediated status, not imply direct uncontrolled execution.
- The UI should show where a decision came from: core brain, AO, expert capsule, memory, teacher, eval, protocol policy, runtime fallback, or human consent.

## 3. Repo Split And Product Boundary

Locked decision: the repo split is canonical.

- `nexusnet/` is the neural brain/core.
- `nexus/` is the platform, API, runtime shell, governance surface, and product host.

The split prevents a common drift failure:

- `nexus/` may expose REST routes, operator panels, status views, runtime launchers, and protocol adapters.
- `nexus/` may never become the real decision center.
- `nexusnet/` owns brain path, expert capsules, teacher policy, memory OS, trace semantics, eval semantics, and native-growth gates.

Current repo-aligned canon:

- `nexusnet/core` owns the canonical wrapped inference path through `NexusBrain.generate()`.
- `nexusnet/teachers` owns teacher registry, assignment routing, attachment state, and provenance.
- `nexusnet/aos` owns AO registry and routing plans.
- `nexusnet/memory` owns memory plane loading and MemoryNode.
- `nexusnet/runtime_optimizer` and runtime modules own device profile, token budget, QES-style candidate surfaces, safe-mode posture, and runtime selection.
- `nexusnet/ui_surface` exposes brain-first wrapper state for API/UI use.
- `nexusnet/evals` owns evaluator conventions and trace-based validation.
- `nexus/` exposes delivery surfaces without taking brain ownership.

Required build implication:

- API endpoints should call into `nexusnet` services rather than duplicating policy logic.
- Product dashboards should render state from registries, traces, artifacts, and canonical services.
- Status pages must distinguish `locked`, `candidate`, `unresolved`, `disabled`, `diagnostic_only`, and `research_only`.

## 4. Core Brain Execution Path

Locked decision: NexusNet must wake and plan before model attachment.

Canonical execution order:

1. `NexusBrain.wake()` records startup telemetry and hardware posture.
2. Runtime/QES planning chooses an execution posture for the requested model or task.
3. MemoryNode assembles the relevant memory plane context.
4. MoE/fusion scaffold builds the Mixtral, Devstral, Router, Cortex, and Neural Bus view where applicable.
5. Execution policy decides whether the system should run teacher fallback, native-shadow guidance, challenger shadow, or guarded live behavior.
6. Internal experts can participate only through bounded, traceable, policy-aware execution.
7. Promotion/replacement linkage records whether foundry evidence changes posture, triggers alignment hold, or requires rollbackable refs.
8. `attach_base_model()` routes through the canonical model ingestion seam.
9. Runtime generation happens only after the brain has recorded plan and posture.
10. Critique runs after generation and trace artifacts persist.

Required trace metadata:

- Brain startup event.
- Hardware profile.
- Runtime and QES plan.
- Token budget and long-context posture.
- Quantization decision.
- Safe-mode posture.
- Attached model identity.
- Teacher registry layer and teacher ID when present.
- Dream/live lineage tags.
- Memory-plane context.
- Fusion scaffold snapshot.
- Teacher evidence bundle.
- Native execution preview and result.
- Expert selection and disagreement capture.
- Critique result.
- Promotion linkage and rollback reference.
- Final output metadata.

Non-negotiable constraint:

- The brain path cannot be bypassed by a UI action, tool call, model provider, test shortcut, protocol adapter, or training job.

Operator/UI panel:

- `Brain Path Trace` should show a timeline from wake to final response.
- It should have stage chips for memory, routing, expert selection, tool/security, generation, critique, eval labels, and output.
- It should allow drilling into why a fallback happened.
- It should show proposed mode versus effective governed mode.

## 5. Assistant Orchestrators Hive

Locked direction: the Assistant Orchestrators Hive is a first-class layer between user-facing workflows and the expert/capsule network.

Why it matters:

- Earlier diagrams underrepresented how complex NexusNet coordination is.
- A single central controller does not capture the intended multi-agent internal structure.
- AOs provide structured workflow control without making external agents the cognition center.

AO responsibilities:

- Interpret user intent at workflow level.
- Decide which expert capsules should participate.
- Coordinate multi-step work without skipping policy.
- Request memory reads and writes through the Memory OS.
- Request tool use through the governed protocol stack.
- Trigger critique, eval, simulation, or training-artifact paths.
- Expose status to operator panels.

Likely AO families:

- `MemoryAO`: memory lifecycle, provenance, temporal truth, evidence lookup.
- `DreamAO`: offline/self-supervised dreaming and simulation artifacts.
- `CritiqueAO`: skeptical review and disagreement capture.
- `ConsequenceAO`: forecast, risk, downstream effect analysis.
- `SafetyAO`: policy, denial, security, high-risk task handling.
- `EvalsAO`: trace-first scenarios, scorecards, benchmark linkage.
- `TrainingAO`: dataset export, reward spec, teacher/capsule provenance.
- `ProtocolAO`: MCP/A2A/AG-UI adapter mediation.
- `RuntimeAO`: runtime profile, hardware, context budget, fallback.
- `VisualOpsAO`: live neural dashboard and replay/compare surfaces.
- `FederationAO`: consented learning, privacy, sync, opt-out.
- `PackagingAO`: product surface, launch flow, buyer/operator readiness.

Authority boundary:

- AOs coordinate and propose.
- NexusBrain remains final decision authority.
- AOs cannot directly mutate production memory, enable tools, promote checkpoints, or bypass security.

Operator/UI panel:

- `AO Hive` panel should show active orchestrators, responsibilities, task ownership, current proposals, blocked actions, and handoff history.
- It should visibly separate AO proposal from brain decision.

## 6. Expert Capsule Roster

Locked decision: the starting roster is 19 expert capsules. The exact registry should remain typed and inspectable.

Current accepted roster:

1. `Coder`
   - Builds and modifies code.
   - Participates in implementation plans, tests, refactors, and debugging.
   - Should be heavily sandboxed for filesystem/tool effects.

2. `Strategist`
   - Breaks down long-horizon goals.
   - Converts raw ideas into phases, dependencies, risks, and operator next steps.
   - Should be used for roadmap and product-sweep planning.

3. `Analyst`
   - Performs structured reasoning, diagnostics, measurement, and comparisons.
   - Helps interpret traces, eval reports, benchmark deltas, and failure modes.

4. `Researcher`
   - Gathers and summarizes external or internal research evidence.
   - Must record source, verified date, license, maturity, and replacement target.
   - Cannot silently upgrade architecture.

5. `Critique`
   - Performs immediate skeptical review of outputs, routes, assumptions, and risk.
   - Should be part of generation and promotion loops.

6. `Conversationalist`
   - Handles user-facing clarity, tone, summarization, and explanation.
   - Should not override technical policy or invent readiness claims.

7. `Toolsmith`
   - Designs, evaluates, and scores tools, adapters, skills, and protocol bridges.
   - Owns ToolScore-style metadata and integration reports.

8. `Security`
   - Owns identity, sandboxing, permissions, consent, audit, denial, and hold states.
   - Must review MCP/local tool enablement and secret-handling flows.

9. `Memory Weaver`
   - Coordinates storage, retrieval, summarization, temporal update, archive, and provenance.
   - Must distinguish current truth from historical truth.

10. `Meta Reasoner`
   - Watches the reasoning process itself.
   - Detects circular loops, missing evidence, overclaiming, route mismatch, and confidence problems.

11. `Router`
   - Selects capsules, teachers, runtimes, memory planes, and fallback paths.
   - Must emit route evidence and EBT score metadata.

12. `Linguist`
   - Handles language, translation, semantic normalization, prompt rewriting, and text style.
   - Should support multilingual and structured-output paths.

13. `Vision`
   - Handles image/video/spatial inputs and multimodal model routing.
   - Candidate model sources include Qwen3-VL, LFM2.5, and other registry candidates.

14. `Audio`
   - Handles speech, audio, sound analysis, transcription, and audio pipeline routing.
   - Must be kept separate from general text generation.

15. `Simulation`
   - Runs scenario, dream, consequence, and what-if paths.
   - Outputs remain shadow-mode unless eval/security gates prove mutation is safe.

16. `Builder`
   - Integrates product modules, scaffolds app surfaces, assembles runtime flows, and converts plans into deliverables.
   - Strong overlap with Coder, but Builder is product/integration oriented.

17. `Instructor`
   - Owns curriculum, teaching stages, distillation tasks, and learning sequences.
   - Bridges teacher models into structured training artifacts.

18. `Intent Mapper`
   - Converts raw user request into goals, constraints, policy labels, memory needs, and route hints.
   - Should fire early in the brain path.

19. `Critic Historian`
   - Tracks longitudinal critique, regressions, old decisions, recurring mistakes, and decision drift over time.
   - Important for a project with years of evolving chats.

Unresolved naming issue:

- `Critique` and `Critic Historian` are both valid but overlapping labels. The roster should keep both unless the registry explicitly records a later approved rename.
- Auxiliary roles should not inflate the locked 19 without a canon update.

Registry requirements:

- Every expert needs `id`, `name`, `purpose`, `capabilities`, `permissions`, `memory_access`, `tool_access`, `eval_coverage`, `status`, `evidence`, and `verified_at`.
- Expert selection must appear in traces.
- Experts cannot bypass Security, Critique, Evals, or NexusBrain authority.

Operator/UI panel:

- `Expert Roster` should show all 19 capsules.
- Each capsule should expose capabilities, current activation, last route, memory permissions, tool permissions, eval coverage, blocked actions, and training lineage.
- The panel should support expert comparison and route replay.

## 7. Shared Hive Mind, Neural Bus, And Cortex

Locked direction: the internal structure should be more than isolated specialists.

Core idea:

- Expert capsules need lateral communication.
- The cortex aggregates signals, broadcasts context, coordinates global posture, and detects cross-expert disagreement.
- The Neural Bus carries messages, activations, route requests, memory snippets, critiques, and confidence/risk metadata.
- A Hive-Blackboard pattern was discussed for shared intermediate state.
- CRDT-style merges and conflict-aware updates were discussed as useful for shared knowledge, distributed edits, or federation-style synchronization.

Required components:

- `Cortex`: global coordinator and context broadcaster.
- `Neural Bus`: structured message transport inside the brain.
- `Hive Blackboard`: shared working state with provenance.
- `Capsule Links`: capsule-to-capsule communication edges.
- `Disagreement Store`: captures conflicting expert views.
- `Consensus/Vote Artifact`: records proposals and vote results where council mode is used.

Authority boundary:

- Negotiation can inform the final answer.
- NexusBrain remains decision authority.
- No capsule or council vote directly mutates production state.

Trace requirements:

- Capsule proposals.
- Capsule critiques.
- Broadcast context.
- Bus messages or summarized bus events.
- Disagreement deltas.
- Final authority decision.

Operator/UI panel:

- `Hive Activity` should show live capsule links, bus traffic, hot edges, disagreement hotspots, and cortex interventions.
- It should not use random animation as fake activity. Sparse telemetry should display as inactive or degraded.

## 7A. Non-Linear Scaling, Large Conversation Scaling, And Horizontal Growth

Locked direction: NexusNet should not scale by simply making one bigger prompt, one bigger model, or one longer linear chat transcript. The intended scaling pattern is non-linear, distributed across experts, planes, memory, cortex, routing, and training loops.

Why this matters:

- The long-context conversations made clear that raw context extension alone does not create true comprehension.
- The MoE and Cortex conversations made clear that NexusNet should scale through sparse expert activation, Mini-NexusNets, router/cortex coordination, and memory-backed context assembly.
- The multi-plane memory conversations made clear that memories and dreams should not live in one flat vector or one flat chronological chat log.
- The RL conversations raised unresolved questions about scaling rollouts when context windows grow toward one to two million tokens.

Non-linear scaling principles:

- Sparse activation over brute-force activation.
- Expert-specific Mini-NexusNets over one monolithic expert block.
- Cortex-level coordination parallel to the Router, not merely above it.
- Neural Bus compression/gating over unrestricted message flooding.
- Memory-plane retrieval over appending all prior chat history.
- Dream consolidation over preserving every intermediate token in active context.
- Rerank/evidence dereference over naive top-k retrieval.
- Horizontal expert and training schedules over single giant training runs.
- Effective context over raw context length.

Large conversation/chat scaling:

- This is the non-linear chat-scaling path: chats become durable structured cognition, not linear prompt bloat.
- Massive project chats should be converted into structured memory artifacts, not repeatedly injected as full text.
- A long conversation should produce:
  - decision records
  - unresolved decision records
  - source/evidence links
  - expert/capsule implications
  - memory-plane updates
  - training examples where appropriate
  - dream/simulation prompts where appropriate
  - eval scenarios where appropriate
  - operator-visible provenance
- The Memory OS should preserve the full dereference path to the original transcript while active reasoning uses summaries, structured records, temporal graph links, and evidence snippets.
- The system should distinguish active working context from archived historical context.
- A conversation should be able to influence future routing without requiring the full transcript to be loaded into every prompt.

MoE/non-linear model scaling:

- Mixtral-style sparse MoE behavior is valuable because only a subset of experts needs to activate per token or task.
- Devstral was accepted as a specialist expert candidate inside the Mixtral/NexusNet direction, not as a full replacement for Mixtral.
- The Router remains the MoE orchestrator for expert activation.
- The Cortex remains a peer-level coordinator that handles memory, dreaming, communication, and meta-reasoning.
- Each expert should have its own Mini-NexusNet so growth can happen locally without forcing every capability into one shared block.

Hardware and training scaling:

- Local consumer hardware should support scaffold, adapter, LoRA, routing, and bounded expert work.
- Large MoE pretraining or joint expert training requires multi-GPU/cloud scale and should be treated as a later gated path.
- SelfTrainingAO should trigger bounded router or expert updates when enough examples accumulate.
- MaintenanceAO should queue/stagger jobs so the system does not exceed local VRAM/RAM.
- Horizontal scaling should allow overnight/staggered jobs, remote/cloud jobs, or multi-GPU jobs without rewriting orchestration logic.

RL scaling:

- TRL is the first practical post-training candidate.
- Verl/RAGEN style scale-out was discussed for multi-turn agentic RL.
- NeMo-RL or ROLL style production scale was discussed as a later candidate.
- Verifiers/SkyRL remain research/prototyping candidates.
- Exact reward functions and rollout contracts for multi-plane memory, dreaming, consequence feedback, and long-context tasks remain unresolved.

Required architecture surfaces:

- `ContextAssemblyPlan`: handles active context without linear transcript stuffing.
- `MemoryConsolidationJob`: turns large chats into structured records.
- `DreamConsolidationJob`: turns memory gaps and performance gaps into dream tasks.
- `ExpertTrainingQueue`: tracks local/horizontal training jobs.
- `NeuralBusBudget`: tracks message budget, compression, and gating.
- `RouteScaleReport`: explains why the system chose sparse expert activation, memory retrieval, summarization, or fallback.

Operator/UI panel:

- `Scale And Consolidation` should show active-context budget, archived chat memory, summary quality, evidence dereference, expert activation sparsity, Neural Bus load, training queue, RL rollout size, and whether a task is being scaled by context, memory, experts, or runtime.

## 8. EBT Hive-Mind Routing

Locked decision: EBT is a core routing contract. The exact scoring formula remains unresolved.

What EBT should do:

- Evaluate task intent, expert fit, memory influence, risk, confidence, runtime constraints, policy constraints, and fallback needs.
- Select capsules, teachers, tools, memory planes, and runtime posture.
- Record why a route was chosen.
- Permit pluggable scoring rather than a hardcoded magic formula.

Required EBT fields:

- `trace_id`
- `input_id`
- `candidate_routes`
- `selected_route`
- `capsule_scores`
- `confidence`
- `risk`
- `memory_influence`
- `tool_need`
- `runtime_need`
- `fallback_reason`
- `critique_result`
- `policy_constraints`
- `eval_labels`

Open decisions:

- Exact EBT score weights.
- Whether scores are independent per capsule, jointly normalized, or learned by a router model.
- How much council voting should influence EBT.
- How to balance novelty, safety, speed, and accuracy.
- When EBT should choose teacher fallback versus native-shadow participation.

Required tests:

- A prompt produces a brain trace with input, intent, capsule routing, memory decision, execution decision, critique, and output metadata.
- EBT rejects malformed routes.
- EBT records fallback reason when route confidence is low.
- EBT never treats missing data as high confidence.

Operator/UI panel:

- `EBT Routing` should show route candidates, scores, chosen capsule set, risk/confidence, rejected alternatives, fallback reason, and post-critique adjustment.

## 9. Memory Operating System

Locked decision: NexusNet memory is not just RAG. It is a Memory Operating System layered over config-driven memory planes.

The chats repeatedly point to memory as a core brain function:

- Memory must be persistent.
- Memory must be structured by plane.
- Memory must preserve provenance.
- Memory must support temporal truth.
- Memory must support graph reasoning.
- Memory must support evidence dereferencing.
- Memory must support dream/training/eval lineage.
- Memory must be inspectable and correctable.

Current repo-aligned canon:

- `MemoryNode` owns operational memory behavior.
- `MemoryPlaneRegistry` loads schema/config.
- `config/planes.yaml` is the root plane config.
- The plane count is not hardcoded.
- The operational structure supports an accepted 11-plane layout.
- Earlier 8-plane and 3-plane views are compatibility projections, not destructive rewrites.

Core operations:

- `store`: record a fact, event, artifact, skill, trace, or decision with provenance.
- `retrieve`: fetch current relevant memory.
- `update`: supersede or refine memory while preserving history.
- `summarize`: compress state into durable summaries.
- `archive`: remove from active retrieval while preserving record.
- `discard`: mark non-retained or invalid content according to policy.
- `dereference`: jump from a summary/fact to the full evidence.
- `provenance_lookup`: explain where a memory came from and why it is trusted.
- `temporal_lookup`: retrieve current truth or historical truth at a given time.

Provisional plane families to preserve until config finalizes:

- Working/session plane.
- Episodic/user-history plane.
- Semantic/knowledge plane.
- Procedural/skills plane.
- Tool/protocol plane.
- Expert/capsule plane.
- Temporal graph plane.
- Evidence/provenance plane.
- Safety/policy plane.
- Dream/simulation plane.
- Federation/shared plane.

Research candidates:

- Graphiti/Zep: temporal graph memory and entity/time-aware retrieval.
- MemOS: memory as an operating-system-level substrate.
- A-MEM: adaptive memory concepts.
- AgeMem: age-aware retention and decay.
- MemexRL: indexed evidence and RL feedback loops.

Adoption rule:

- These are design candidates, not mandatory dependencies.
- A candidate can inspire schema or adapters without replacing MemoryNode.
- No memory dependency becomes canonical until license, maturity, test, provenance, and security records exist.

Required tests:

- Same fact can be stored with source/provenance.
- Same fact can be updated over time.
- Current truth retrieval returns the latest accepted state.
- Historical truth retrieval returns earlier state.
- Dereference returns full evidence.
- Archive and discard alter active retrieval without erasing audit trail improperly.

Operator/UI panel:

- `Memory OS` should show planes, record lifecycle, provenance, temporal updates, dereference links, archived state, and active retrieval influence on current outputs.
- It should allow an operator to inspect memory without silently mutating it.

## 9A. Multi-Plane Mind Map, Hypergraph Memory, And Cross-Plane Cognition

Locked direction: the brain/memory structure should not be a flat two-dimensional grid or one generic vector space. The chats developed the idea into a multi-plane "mind map" where memories, dreams, and reasoning can connect across multiple cognitive dimensions.

Core decision:

- Each memory should be representable as a tuple of subvectors, one per cognitive plane.
- The system should be configurable through plane definitions rather than hardcoded to one fixed plane count.
- The graph underneath should be multi-relational and hypergraph-like, not just a vector table.
- Cross-plane message passing and attention should allow one plane to influence another.
- Dreaming should be able to sample, stitch, and recombine across planes.

Accepted plane set from the multi-plane discussion:

1. `conceptual`
   - Abstract reasoning, concepts, categories, symbolic ideas, and high-level relationships.

2. `temporal`
   - Event sequence, time, causality order, memory age, and historical versus current truth.

3. `emotional`
   - Valence, affective tone, user sentiment, urgency, preference, and motivational color.

4. `procedural`
   - Steps, actions, workflows, plans, recipes, and operational know-how.

5. `imaginal`
   - Sensory/dream imagery, visual-spatial imagination, scenario fragments, and synthetic dream material.

6. `social`
   - Roles, trust, people, relationship context, collaboration state, and social expectations.

7. `ethical`
   - Values, norms, moral judgment, policy alignment, harm boundaries, and safety reasoning.

8. `metacognitive`
   - Confidence, uncertainty, self-monitoring, limits, route quality, and introspective state.

9. `goal`
   - Intent, objectives, desired outcomes, active tasks, priorities, and success criteria.

10. `spatial`
   - Physical layout, UI layout, location, object relationships, and geometry.

11. `predictive`
   - Forecasts, consequences, likely outcomes, risk estimates, and future-state modeling.

Hypergraph relationship examples:

- `happens_before`: temporal relationship.
- `causes`: procedural/causal relationship.
- `feels_like`: emotional relationship.
- `visual_similar`: imaginal relationship.
- `trusts`: social relationship.
- `aligned_with`: ethical relationship.
- `knows_limit`: metacognitive relationship.
- `aims_for`: goal relationship.
- `nearby`: spatial relationship.
- `predicts`: predictive relationship.

Cross-plane cognition requirements:

- Intra-plane updates should improve reasoning inside one plane.
- Inter-plane projections should let one plane influence another through learned adapters or MLP projections.
- Cross-plane attention should let MemoryNodes attend from one subvector to another.
- Plane weights should be config-driven for retrieval, routing, dreaming, and critique.
- Plane dimensions should be configurable.
- Adding a plane should require config/schema work and tests, not a rewrite of every reasoning loop.

Dreaming connection:

- DreamAO should be able to perform random walks across the hypergraph.
- DreamAO should stitch plane subvectors from multiple MemoryNodes into a dream vector or dream scenario.
- CritiqueAO should score the dream against ethical, social, metacognitive, goal, spatial, predictive, and factual expectations.
- Dream results should feed replay buffers, eval scenarios, and training candidates only through gates.

Self-awareness boundary:

- The chats used multi-plane memory and dream reflection as a path toward richer self-modeling.
- That should be treated as an architectural aspiration and research direction, not as a claim that the system is conscious.
- Higher-order meta-nodes such as "I am learning" can be modeled as memory artifacts, but they need provenance, eval labels, and safety boundaries.

Implementation requirements:

- `planes.yaml` or equivalent config should define planes, dimensions, encoders, and weights.
- `MemoryNode` should load plane definitions dynamically.
- Encoders should be registered per plane.
- Graph builders should create nodes with plane attributes and typed cross-plane edges.
- Reasoning loops should iterate over configured planes.
- Tests should validate plane shape, retrieval weighting, dream sampling, and cross-plane message stability.

Operator/UI panel:

- `Multi-Plane Mind Map` should show the active cognitive planes, plane dimensions, plane weights, cross-plane edges, dream sampling paths, plane-specific eval health, and whether a plane is locked, candidate, disabled, or unresolved.

## 10. Teacher Models And Mentor Policy

Locked decision: teacher models bootstrap NexusNet but are not permanent cognition.

Teacher role:

- Provide domain teaching.
- Generate comparison outputs.
- Create distillation data.
- Participate in curriculum stages.
- Serve as fallback while native capability matures.
- Supply benchmark/disagreement evidence.

Teacher boundary:

- Teachers are replaceable capability providers.
- Teachers must not become hidden permanent brains.
- Teacher routing must be visible.
- Teacher outputs need provenance and license metadata.
- Teacher retirement/native takeover requires eval, rollback, safety, and provenance proof.

Historical teacher ideas:

- Mixtral-8x7B.
- Yi-1.5-9B.
- Qwen-0.5B MoE.
- LLaMA-3 8B.
- Devstral and Mixtral fusion paths.
- LFM2 as a bounded lane.

Current repo-aligned teacher flow:

- `historical` registry layer preserves original best-ensemble-per-role canon.
- `v2026_live` layer provides operational primary/secondary routing.
- Critique Expert arbitrates disagreements.
- LFM2 remains bounded and non-primary.
- Curriculum stages include domain professor distillation, dual-teacher contrast, skeptical examination, and dream/self-evolution.
- Foundry/native growth tracks dependency ratio, native generation, teacher disagreement delta, takeover readiness, rollbackability, and native-vs-wrapper slices.

Required metadata:

- Teacher identity.
- Registry layer.
- Role.
- License.
- Source.
- Assignment reason.
- Disagreement artifact.
- Benchmark family.
- Dream/eval lineage.
- Replacement readiness.

Operator/UI panel:

- `Teachers` should show active teacher layer, selected primary/secondary teachers, arbitration history, disagreement deltas, retirement status, native takeover evidence, and license status.

## 11. Model Fusion, Assimilation, And Expert Block Adaptation

Strong accepted direction: NexusNet should be able to ingest and adapt models or expert blocks without manual surgery, but actual promotion must be gated.

Historical architecture ideas:

- Build MoE with per-expert NexusNet modules.
- Mixtral-style expert structure and Devstral-style coding strength can be combined through router, adapters, or block adaptation experiments.
- A global cortex can coordinate experts and memory across specialist modules.
- Automated block matching can inspect new model components and generate adapter plans.
- Expert onboarding should create reports visible through VisualOps.

Proposed core modules:

- `ModelIngestionService`: canonical model attach and ingestion metadata.
- `attach_base_model()`: controlled attach seam.
- `ExpertBlockAdapter`: inspects shape, capability, interface, and compatibility.
- `Assimilation Registry`: tracks external candidates.
- `Integration Report`: records compatibility, adapter generation, eval results, and retraining needs.
- `Router Retraining Plan`: determines whether only router alignment is enough or full joint tuning is required.
- `Rollback Reference`: preserves prior runnable posture.

Important distinction:

- Ingesting a model is not the same as promoting it.
- Registering a candidate is not the same as enabling it.
- Passing a benchmark is not the same as replacing a teacher or native module.

Required gates:

- License review.
- Capability metadata.
- Security review.
- Runtime support.
- Shape/interface compatibility.
- Traceable eval.
- Regression comparison.
- Rollback path.
- Operator visibility.

Operator/UI panel:

- `Assimilation` or `Model Integration` should show candidate status, adapter plan, shape mismatches, eval deltas, required retraining, license, promotion gate, and rollback status.

## 12. Training, RL, Curriculum, And Native Growth

Locked decision: scaffold first, train later.

The chats repeatedly caution that real training should not begin until schemas, traces, evals, memory provenance, security, and baseline tests are stable.

Training phases:

1. Bootstrap.
   - Attach teacher models.
   - Build curriculum.
   - Capture teacher outputs.
   - Generate supervised examples.
   - Establish routing and memory traces.

2. Fusion/alignment.
   - Train router and adapters.
   - Align capsule behavior.
   - Compare primary/secondary teachers.
   - Preserve fallback.

3. RL/self-improvement.
   - Use trace-based rewards.
   - Train on task completion, route quality, critique quality, memory correctness, and tool correctness.
   - Keep reward specs explicit.

4. Native-growth and independence.
   - Reduce teacher dependency only when evidence supports it.
   - Promote native candidates behind rollbackable gates.
   - Preserve teacher fallback until replacement readiness is proven.

5. Federation or autonomous improvement.
   - Remains gated by consent, privacy, eval, and provenance.

Research/tool candidates:

- TRL v1: default post-training candidate.
- verl: candidate for larger RL/tool-agent training.
- SkyRL: candidate for RL scaling.
- DeepEval and OpenAI agent eval patterns: trace-first evaluation candidates.
- OpenRLHF: `candidate_requires_pin` due to future-dated README entries found in research refresh relative to 2026-04-26.

Training artifact requirements:

- Dataset export must include provenance.
- Teacher/capsule source must be present.
- Safety labels must be present.
- Eval target must be present.
- License metadata must be present.
- Reward spec must be versioned.
- Eval report must be versioned.
- Promotion decision must be separate from diagnostic score.

Operator/UI panel:

- `Training` should show dataset exports, teacher source, capsule source, reward spec, eval report, license state, safety labels, checkpoint status, promotion gate, and why training is blocked or allowed.

## 13. Dreaming, Simulation, Critique, And Consequence Loops

Locked decision: recursive dreaming, critique, and consequence analysis are core NexusNet ideas, but production mutation remains gated.

Purpose:

- Dreaming explores synthetic scenarios and self-supervised improvements.
- Critique catches hallucination, weak routes, unsafe plans, and incomplete work.
- Consequence analysis forecasts risks and downstream effects.
- Simulation creates shadow-mode artifacts for eval and training.

Core loops:

- `DreamAO`: generates dream episodes, hypothetical tasks, gaps, or synthetic scenarios.
- `CritiqueAO`: reviews outputs and internal proposals.
- `ConsequenceAO`: forecasts effects and risk.
- `Simulation` expert: executes scenario reasoning.
- `Meta Reasoner`: evaluates whether the loop is improving or circling.

Mutation boundary:

- Dream outputs cannot directly mutate production memory.
- Dream outputs cannot directly promote checkpoints.
- Simulation outputs remain advisory until eval gates prove benefit.
- Critique can block, flag, or request fallback, but final authority remains NexusBrain.

Trace requirements:

- Dream episode ID.
- Simulation inputs.
- Critique events.
- Consequence predictions.
- Risk labels.
- Whether any output was stored, archived, discarded, or held.

Operator/UI panel:

- `Dream And Simulation` should show shadow artifacts, current scenario, risk labels, critique status, mutation-block state, and whether an artifact is eligible for eval/training.

## 13A. Recursive Neural Dreaming And Recursive Learning

Locked decision: NexusNet should include Recursive Neural Dreaming (RND) as a core self-improvement mechanism. This was not just a generic "simulation" idea. The captured chats explicitly accepted Cortex-directed dreaming, individualized expert dreams, replay buffers, collaborative/competitive dream modes, and imagine-evaluate-learn loops.

Final decision from the Mixtral/Devstral/Cortex thread:

- NexusNet is not just a multi-model orchestrator.
- Mixtral is the accepted MoE base for that thread.
- Devstral is the accepted specialist expert to integrate into the Mixtral/NexusNet direction.
- The Router remains the Mixtral MoE orchestrator.
- NexusNet should be integrated before training, not bolted on afterward.
- Each expert should have its own Mini-NexusNet.
- A separate global Cortex should exist at the same level as the Router.
- The Cortex should communicate with expert mini-brains through the Neural Bus.
- For Dreaming, the Cortex should remain the main processor and send individualized dreams to each expert mini-brain.
- Block matching/adaptation should be automated inside NexusNet, not manual.

RND purpose:

- Run offline, scheduled, or performance-triggered synthetic tasks.
- Replay and recombine memories.
- Generate rare, adversarial, cross-domain, or underrepresented scenarios.
- Target underperforming experts.
- Improve routing, memory, critique, and expert capability.
- Produce training candidates, not direct production mutations.
- Feed self-improvement loops with traceable evidence.

Canonical RND loop:

1. Trigger.
   - Scheduled, on-demand, performance-based, eval-gap-based, memory-gap-based, or post-assimilation.

2. Cortex objective selection.
   - Cortex reviews traces, eval gaps, teacher disagreement, memory gaps, failed routes, and expert performance.

3. Dream plan.
   - Cortex creates individualized or collaborative dream prompts for one or more expert Mini-NexusNets.

4. Expert dream execution.
   - Expert Mini-NexusNets execute dream tasks locally or in bounded shadow mode.

5. Cross-expert collaboration.
   - Dreams can combine domains such as code+math, code+language, vision+procedure, safety+tooling, or memory+planning.

6. Replay buffer write.
   - Dream inputs, generated artifacts, selected memories, expert states, and outputs are stored in a replay buffer.

7. Critique.
   - CritiqueAO and Meta Reasoner score factuality, route quality, novelty, safety, coherence, confidence, and usefulness.

8. Consequence analysis.
   - ConsequenceAO forecasts risks or likely downstream effects if the dream result were used.

9. Evaluation.
   - EvalsAO turns strong dream outputs into eval scenarios or training candidates.

10. Gated learning.
   - SelfTrainingAO may propose LoRA/adapters/router updates, but promotion remains gated.

11. Memory lifecycle.
   - MemoryAO stores, updates, archives, or discards dream artifacts with provenance.

12. Agenda adaptation.
   - Cortex updates future dream schedules based on which dream protocols improved which skills.

Dream modes:

- `individualized`: one expert receives a targeted dream based on its performance gap.
- `collaborative`: multiple experts jointly work a cross-domain dream.
- `competitive`: experts produce competing dream outputs for critique or tournament-style comparison.
- `dream_tournament`: a competitive/collaborative dream run where experts or expert groups produce alternate dream solutions, then CritiqueAO, EvalsAO, and Meta Reasoner compare which dream improved the target skill or exposed the strongest risk.
- `creative`: dream explores novel combinations for synthesis.
- `adversarial`: dream stress-tests safety, robustness, tool misuse, or edge cases.
- `replay`: dream revisits prior failures or important memories.
- `consolidation`: dream compresses and organizes memory.
- `assimilation`: dream helps integrate a newly attached model, expert, or capability.

Recursive learning connection:

- Recursive dreaming should not stop at one generated artifact.
- The system should use critique and eval feedback to create the next dream agenda.
- Dream outputs can become training examples only if provenance, safety labels, license labels, teacher/capsule source, and eval target are present.
- Training should be incremental and bounded first: adapters, LoRA, router tuning, plane-specific encoders, or expert-local updates.
- Full weight mutation, Neural DNA-style architecture mutation, or autonomous checkpoint promotion remains gated and research-only until proven safe.

Replay buffer requirements:

- Dream ID.
- Trigger reason.
- Cortex objective.
- Expert IDs.
- Memory references.
- Plane references.
- Prompt/config.
- Output artifact.
- Critique score.
- Eval labels.
- Safety labels.
- Proposed learning target.
- Whether it was stored, archived, discarded, or exported.
- Promotion eligibility.

Metrics:

- Dream usefulness.
- Novelty.
- Safety pass/fail.
- Critique quality.
- Expert improvement delta.
- Route improvement delta.
- Memory recall improvement.
- Hallucination/regression rate.
- Replay reuse rate.
- Cost/runtime.

Boundaries:

- Dream artifacts are not production facts by default.
- Dream artifacts cannot directly mutate production memory without lifecycle decision.
- Dream artifacts cannot directly promote model weights.
- Competitive or adversarial dreams cannot bypass safety policy.
- RND improves the system only through MemoryAO, CritiqueAO, EvalsAO, SelfTrainingAO, and promotion gates.

Operator/UI panel:

- `Recursive Dreaming` should show dream schedule, trigger reason, Cortex objective, expert dream assignments, replay buffer, dream graph, critique score, eval conversion, training proposal, blocked mutations, and skill-improvement metrics.

## 14. Tooling, MCP, A2A, AG-UI, And Protocol Governance

Locked decision: protocol integration must be governed. MCP is not the brain.

Historical idea:

- MCP gives NexusNet tools.
- Tool Invocation Manager and Toolsmith manage tool use.
- Path A can use traditional MCP tool calls.
- Path B can support sandboxed code execution.
- ToolScore evaluates tools.

Research update:

- Treat MCP, A2A, and AG-UI as a protocol layer.
- MCP is for tool/server integration.
- A2A is for agent-to-agent work.
- AG-UI is for user-facing agent event streams.
- All adapters are disabled or held until a security envelope allows them.

Security envelope:

- Signed or allowlisted server definitions.
- Identity metadata.
- Sandboxing mode.
- Per-tool permissions.
- User consent.
- Audit logs.
- Denial and hold states.
- No secret collection through form-mode elicitation.
- Accept, decline, and cancel must all be supported for elicitation.

Required protocol states:

- `disabled`.
- `candidate`.
- `held_for_consent`.
- `denied`.
- `sandboxed`.
- `allowed`.
- `audit_only`.

Required tests:

- Untrusted MCP config is rejected.
- Sensitive elicitation requires URL/out-of-band flow.
- Denied tools do not execute.
- Unsandboxed execution fails closed.
- Every tool attempt creates audit metadata.

Operator/UI panel:

- `Protocol Security` should show server identity, allowlist status, sandbox state, permission scope, elicitation mode, last attempts, denied attempts, consent history, and audit links.

## 15. Security, Identity, Privacy, And Consent

Locked direction: security is core architecture, not a post-hoc wrapper.

Why this changed in the research refresh:

- Local tools and MCP servers can expose high-risk host capabilities.
- Agent-to-agent flows can accidentally inherit privileges.
- UI elicitation can leak secrets if designed incorrectly.
- Training and memory systems can accidentally preserve private data.
- Federation or shared-skill systems require consent and provenance.

Required security interfaces:

- `SecurityPolicy`
- `ProtocolAdapter`
- `ToolAttempt`
- `SecurityDecision`
- `ConsentDecision`
- `AuditEvent`
- `IdentityMetadata`

Policy fields:

- `tool_id`
- `protocol`
- `identity_required`
- `sandbox_required`
- `permissions`
- `elicitation_modes`
- `approval_required`
- `deny_reason`
- `audit_ref`

High-risk defaults:

- Unknown tools are denied.
- Unknown servers are denied.
- Missing identity is denied or held.
- Secret elicitation is denied in form mode.
- Missing sandbox is denied for local execution.
- Missing audit path is denied.
- Tool call failures should not silently become model-only guesses when tool output was required.

Privacy requirements:

- Memory writes must include retention policy.
- Training exports must include license and source labels.
- Federation requires consent and opt-out.
- Shared skill evolution must not promote raw private user data.
- Operator exports should avoid workstation metadata unless explicitly intended.

Operator/UI panel:

- `Security Center` should show policy matrix, current holds, consent queue, identity metadata, audit log, denied attempts, secret-flow warnings, and training/privacy flags.

## 16. Long Context And Effective Context Architecture

Locked ambition: NexusNet should target one-million-token effective context. This is not a promise that every local model already supports raw 1M context.

The early context-window chats established the technical reality:

- Extending context requires positional encoding changes, RoPE/attention strategy, continued training, memory-efficient attention, and data.
- Raw context length without training quality is misleading.
- Long-context quality requires purpose-built long-document data and evaluation.
- Context packing, compression, retrieval, memory, and KV/cache reuse are part of the real solution.

Canonical interpretation:

- 1M tokens is an effective-context product architecture target.
- The system should combine memory planes, indexed evidence, summarization, context packing, KV/cache reuse, long-context model support, route-aware assembly, and runtime budgeting.
- The runtime should report what is possible on the current machine.
- Safe hosts must degrade gracefully instead of pretending million-token execution is available.

Candidate runtime technologies:

- vLLM.
- SGLang.
- LMCache-style KV reuse.
- torchao quantization.
- FlashAttention-family techniques where supported.
- TriAttention remains research-only unless benchmarks prove value.

Required context-planner fields:

- Raw prompt tokens.
- System/context tokens.
- Rolling summary budget.
- Memory plane budget.
- Evidence budget.
- Tool result budget.
- Teacher/capsule context budget.
- KV/cache reuse status.
- Runtime max context.
- Effective context estimate.
- Truncation or summarization decisions.

Operator/UI panel:

- `Context Assembly` should show raw tokens, memory tokens, evidence tokens, summary tokens, model cap, effective-context plan, dropped/archived evidence, and why a context fallback occurred.

## 17. Hardware, Runtime, And Local-First Adaptation

Locked direction: hardware adaptation is a product-level capability.

Historical ideas:

- HardwareScanner.
- AdaptiveSystemProfiler.
- Device profile.
- VRAM/RAM/thermal routing.
- Runtime fallback.
- Safe mode.
- Quantization decisions.
- Long-context host cap.
- Neuromorphic candidates as aspirational/research-only.

Current repo-aligned runtime outputs:

- `device_profile`.
- `token_budget_profile`.
- Runtime candidates.
- Quantization decision.
- Selected runtime.
- Safe-mode fallback signal.
- Long-context profile.
- Execution-policy runtime bias.

Runtime profiles:

- Local CPU.
- Local GPU.
- Cloud.
- Constrained-device.
- Safe mode.
- Diagnostic-only.

Runtime candidates:

- vLLM.
- SGLang.
- LMCache.
- torchao.
- AITune for NVIDIA/PyTorch tuning where supported.
- OpenClaw/Goose/OpenJarvis product patterns as bounded operator/runtime inspirations, not brain replacements.

Required behavior:

- Unsupported runtimes are not shown as runnable.
- Candidate presence does not imply readiness.
- Hardware profile influences brain path before model attachment.
- Safe mode bounds native behavior but keeps the policy engine alive.
- Runtime fallback must be visible.

Operator/UI panel:

- `Runtime And Hardware` should show CPU/GPU/RAM/VRAM/thermal posture, selected profile, safe-mode reason, quantization decision, runtime candidates, support status, and fallback chain.

## 18. VisualOps, Operator UI, And Product Panels

Locked direction: NexusNet needs an operator-facing UI that makes the whole brain understandable and controllable.

This was underrepresented in the earlier truncated synthesis. The fuller chats include repeated VisualOps/dashboard discussions.

VisualOps purpose:

- Show real-time expert activations.
- Show token/path routing.
- Show Neural Bus traffic.
- Show cortex interventions.
- Show memory access.
- Show dream/simulation outcomes.
- Show adaptation/onboarding logs.
- Show integration status.
- Show decision traces.
- Show safe-mode, thermal, VRAM, retry, and fallback physiology.
- Make the system inspectable, controllable, and explainable.

Candidate/local file ideas from early chats:

- `ops/visualops_dashboard.py`.
- `ops/start_dashboard.py`.
- `ops/add_expert.py`.

Current product-sweep visualizer canon:

- One canonical visualizer: `/ui/visualizer/`.
- Default renderer: repo-local HTML/CSS/JS with layered SVG plus Canvas.
- Repo-local Three.js is allowed only where depth, parallax, deep zoom, or capsule interiors materially improve fidelity.
- No external CDN dependencies.
- Legacy `/ui/3d/` should redirect to canonical visualizer.
- Visualizer is read-only.
- Missing telemetry must be shown as inactive or unbound, never fabricated.

Required operator panels:

1. `Canon Status`
   - Shows locked, candidate, unresolved, disabled, diagnostic-only, and research-only items.
   - Shows unresolved decisions and evidence gaps.

2. `Brain Path Trace`
   - Shows wake, route, memory, tool/security, generation, critique, eval labels, and final output.

3. `AO Hive`
   - Shows active orchestrators, proposals, handoffs, blocked actions, and authority boundaries.

4. `Expert Roster`
   - Shows all 19 experts, capabilities, permissions, memory access, eval coverage, activation, and training lineage.

5. `Hive Activity`
   - Shows Neural Bus traffic, capsule links, cortex broadcasts, consensus, and disagreement hotspots.

6. `Memory OS`
   - Shows memory planes, lifecycle operations, provenance, temporal truth, and dereference paths.

7. `EBT Routing`
   - Shows route candidates, score breakdown, selected path, fallback reason, confidence, risk, and critique result.

8. `Protocol Security`
   - Shows MCP/A2A/AG-UI adapters, tool identity, sandbox, allowlist, consent, denial, hold, and audit state.

9. `Training`
   - Shows datasets, reward specs, eval reports, teacher/capsule source, license, safety labels, checkpoints, and promotion blocks.

10. `Runtime And Hardware`
   - Shows device profile, context cap, quantization, selected runtime, safe mode, fallback, and unsupported runtimes.

11. `Research Candidates`
   - Shows Assimilation Registry records, verified dates, license, maturity, integration status, replacement target, and notes.

12. `Visualizer`
   - Shows neural sculpture, 19 capsule ring, hive links, dream/critique/consequence loops, physiology overlays, replay, compare, and depth inspection.

13. `Eval Health`
   - Shows scenarios, latest trace scores, policy violations, memory recall, route correctness, tool correctness, and critique quality.

14. `Federation And Privacy`
   - Shows consent, opt-out, sync status, shared-skill proposals, privacy flags, and retention state.

15. `Packaging And Product Readiness`
   - Shows launch readiness, docs, operator status, blocked dependencies, buyer-facing artifacts, and support diagnostics.

UI design rule:

- The UI should not be a marketing page.
- It should be dense, operational, inspectable, and built for repeated expert use.
- It should avoid implying readiness where canon says candidate, unresolved, disabled, diagnostic-only, or research-only.

## 19. Canonical Visual Architecture And Diagrams

Locked direction: visual architecture must reflect the full NexusNet structure, not a simplified single-brain diagram.

Required diagram concepts:

- NexusNet Core as layered neural structure.
- 19 expert capsules as mini-brains or specialized neural capsules.
- Assistant Orchestrators Hive above/around workflow coordination.
- Shared Hive Mind / cortex / neural bus layer.
- Memory OS with multiple planes and temporal/evidence graph.
- Teacher model layer as replaceable providers.
- Tool/protocol layer as governed external capability.
- Dreaming, Critique, and Consequence loops as distinct recursive loops.
- Runtime/hardware physiology overlays.
- Training/foundry/promotion gates.
- Security/identity envelope.
- UI/operator panels reading from brain state.

Diagram source-of-truth rule:

- Diagrams are not source of truth until generated from schema/canon state or validated against it.
- If a diagram omits locked features, it is a stale view.
- Visualizer and diagrams should show unavailable telemetry as unbound, not fake.

Current visualizer requirements:

- Structured live state from `/ops/brain/visualizer/state`.
- Replay from `/ops/brain/visualizer/replay`.
- Read-only compare helpers for teacher evidence, disagreements, replacement readiness, route activity, cohort/fleet windows.
- Render tiers: `full`, `balanced`, `safe`.
- Hidden-tab downgrade and low-power clamp.
- Provider provenance: provider kind, signal counts, latest trace reference, bound/degraded health, log-channel coverage.

Operator/UI panel:

- `Visualizer` should combine beauty and engineering truth: neural scene plus traceable overlays, replay, compare, provider health, and bounded depth inspection.

## 20. Trace-First Evals

Locked decision: evals must be trace-first and available before real autonomous training or promotion.

Why:

- Without traces, route choices cannot be audited.
- Without evals, dreaming/self-improvement can amplify wrong behavior.
- Without provenance, training data becomes untrustworthy.
- Without policy labels, tools and security cannot be verified.

Eval scenario families:

- Route choice.
- Tool correctness.
- Memory recall.
- Memory temporal truth.
- Critique quality.
- Policy violation detection.
- Teacher disagreement.
- Native takeover readiness.
- Dream contamination.
- Long-context retrieval quality.
- Runtime fallback correctness.
- Security denial/hold correctness.

Required trace interface:

- `trace_id`.
- `input_id`.
- `brain_path`.
- `capsule_routes`.
- `memory_operations`.
- `tool_attempts`.
- `security_decisions`.
- `critique_events`.
- `eval_labels`.

Research candidates:

- OpenAI agent eval patterns.
- DeepEval.
- OSWorld for UI/agent task evaluation.
- Fara/UI-TARS style GUI-agent eval inspiration.

Operator/UI panel:

- `Eval Health` should show scenario coverage, latest scores, regressions, trace links, missing labels, and promotion blockers.

## 21. Research Assimilation Registry

Locked decision: new ideas enter through a living registry.

Required candidate fields:

- `id`.
- `name`.
- `category`.
- `source_url`.
- `verified_at`.
- `license`.
- `evidence_level`.
- `maturity`.
- `integration_status`.
- `replacement_target`.
- `notes`.
- `status`.

Current research refresh candidates:

- Graphiti/Zep: temporal graph memory candidate.
- MemOS: memory operating system research candidate.
- A-MEM: adaptive memory candidate.
- AgeMem: retention/aging candidate.
- MemexRL: evidence-indexed RL/memory candidate.
- MCP: governed tool protocol.
- A2A: governed agent-to-agent protocol.
- AG-UI: governed user-facing agent event protocol.
- TRL v1: default post-training candidate.
- verl: larger RL/tool-agent training candidate.
- SkyRL: larger RL candidate.
- Fara: GUI/computer-use candidate.
- OSWorld: UI-agent eval candidate.
- UI-TARS: GUI-agent model/tooling candidate.
- Qwen3-VL: multimodal candidate.
- LFM2.5: compact edge multimodal candidate.
- vLLM: serving candidate.
- SGLang: serving candidate.
- LMCache: KV/cache reuse candidate.
- torchao: quantization candidate.
- DeepEval: eval candidate.
- OpenAI agent eval patterns: eval methodology candidate.
- OpenRLHF: `candidate_requires_pin`.

Earlier assimilation playbook statuses:

- Ship now: cross-encoder reranking, OpenClaw runtime patterns, LFM2.5-VL edge lane, NVIDIA AITune, OpenJarvis productization patterns, Goose runtime/operator bounded lane, Core NexusNet Pivot.
- Prototype next: SkillClaw/OpenSpace pattern, MiniMax M2.7.
- Research only: TriAttention, OBLITERATUS safe-boundary/quarantined analysis.

Adoption rule:

- A research candidate can improve a design.
- It cannot silently replace locked canon.
- Registry status must be explicit.
- License review can disable a candidate.
- Maturity and evidence must be visible to operators.

Operator/UI panel:

- `Research Candidates` should provide a sortable registry with status, evidence, license, maturity, replacement target, and last verification date.

## 22. Retrieval, RAG, Evidence, And Grounding

Locked boundary: retrieval and RAG are important capabilities, but they are not NexusNet itself.

Accepted retrieval ideas:

- First-stage retrieval can be cheap and broad.
- Cross-encoder reranking can improve noisy top-k candidates.
- Retrieval score provenance should be recorded.
- Evidence should be dereferenceable.
- Grounded outputs should cite memory/evidence when appropriate.
- Retrieval should feed Memory OS and context assembly, not bypass them.

Required metadata:

- Query.
- Candidate set.
- Retrieval score.
- Rerank score.
- Source.
- License/permission where relevant.
- Time validity.
- Evidence hash or artifact ID.
- Memory plane.
- Whether evidence was used, rejected, summarized, or archived.

Operator/UI panel:

- `Evidence And Retrieval` should show retrieved documents, rerank scores, evidence influence, provenance, and dereference links.

## 23. GUI, Computer Use, And Multimodal Interaction

Strong accepted direction: NexusNet should be able to interact with GUIs and multimodal inputs, but this remains mediated and eval-gated.

Discussed candidates:

- DeepEyesV2 review for visual/computer-use ideas.
- Microsoft FARA framework review.
- UI-TARS style UI interaction.
- OSWorld style evals.
- Qwen3-VL and LFM2.5 for multimodal capability.

Boundary:

- GUI agents cannot bypass protocol security.
- Visual perception does not equal permission to act.
- UI-control actions need audit, consent, sandboxing, and rollback where possible.
- Multimodal models are capability providers, not the core brain.

Required surfaces:

- Visual input metadata.
- Screen/action trace.
- Permission state.
- Tool or browser target identity.
- Eval scenario label.
- Failure/fallback.

Operator/UI panel:

- `Computer Use` should show perception inputs, proposed actions, consent status, sandbox, action log, screenshots/artifacts, and eval score.

## 24. Federation, Privacy, And Shared Learning

Accepted but gated direction: NexusNet can eventually support federated or shared learning, but only with strong privacy and consent.

Historical ideas:

- Federated learning/privacy layer.
- EMV/FLP-style shared improvement.
- Opt-out and consent.
- Shared skill repositories.
- Skill evolution from repeated successful behavior.

Required boundaries:

- No raw private data promotion.
- Consent required for sharing.
- Opt-out must be honored.
- Shared artifacts need provenance and license.
- Federated updates need eval and rollback.
- Production memory cannot be mutated by remote untrusted updates.

Operator/UI panel:

- `Federation And Privacy` should show local-only status, sync proposals, consent state, retention policy, privacy flags, and shared artifact provenance.

## 25. Packaging, API, Product Surface, And Buyer Readiness

Accepted direction: NexusNet needs a real product shell, not just research scripts.

Product needs:

- API routes for brain status, canon status, experts, memory, runtime, security, training, evals, visualizer, and product status.
- Operator dashboards.
- Launchers and docs.
- Diagnostics export.
- Honest readiness status.
- Runtime profiles.
- Local-first startup and doctor checks.
- Product-sweep gates.

Current product-sweep status surfaces:

- `/ops/brain/canon`.
- `/ops/brain/research-candidates`.
- `/ops/brain/memory-os`.
- `/ops/brain/security/protocol/*`.
- `/ops/brain/runtime/context-assembly`.
- `/ops/brain/training/*`.
- `/ops/brain/product-sweep/*`.
- `/ops/brain/product-status`.
- `/ops/brain/visualizer/state`.

Readiness truth rule:

- Do not imply production readiness where canon says candidate, unresolved, disabled, diagnostic-only, or research-only.
- Product pages must be truthful even when a feature is aspirational.

Operator/UI panel:

- `Product Status` should aggregate canon, memory, security, runtime, eval, training, visualizer, and packaging readiness with blockers and evidence links.

## 26. Build Roadmap From The Compiled Canon

The current best build order remains scaffold-first and gate-first.

Phase 0: Baseline rescue.

- Ensure imports and test collection pass.
- Restore/validate `nexus.models.ModelRegistry` or equivalent.
- Gate: `python -m pytest --collect-only -q`.

Phase 1: Canon and research lock.

- Finalize this decision-basis document into registry records.
- Validate locked/candidate/unresolved decisions.
- Gate: canon validation fails on missing status, evidence, license, or verified date.

Phase 2: Schemas and registries.

- Add typed registries for experts, teachers, model/runtime candidates, memory planes, memory operations, protocols, security policy, traces, eval scenarios, and EBT scores.
- Gate: schema tests load valid data and reject malformed entries.

Phase 3: Brain path unification.

- Route all generation through `NexusBrain.generate()`.
- Gate: prompt produces full trace with memory, routing, execution, critique, and output metadata.

Phase 4: Memory OS.

- Implement lifecycle operations, provenance, temporal truth, and evidence dereference.
- Gate: store/update/retrieve/current/historical/dereference tests pass.

Phase 5: Secure protocol stack.

- Govern MCP, A2A, AG-UI, local tools, identity, sandbox, consent, audit.
- Gate: untrusted configs, secret elicitation, denied tools, and unsandboxed execution fail closed.

Phase 6: Expert hive and council.

- Make all 19 experts typed, inspectable, permissioned, and eval-covered.
- Council remains advisory.
- Gate: expert selection traceable and policy cannot be bypassed.

Phase 7: Runtime and long context.

- Runtime profiles, context budget accounting, fallback, cache/KV candidate support.
- Gate: unsupported runtime never shown as runnable.

Phase 8: Training and assimilation.

- Export datasets, reward specs, eval reports, license/provenance metadata before checkpoint promotion.
- Gate: promotion blocked until eval/license/security/provenance pass.

Phase 9: Product surface and docs.

- Operator panels, visualizer, product status, docs, diagrams generated from schema/canon state.
- Gate: status surfaces truthfully distinguish readiness categories.

## 27. Unresolved Conflicts And Decisions To Lock Next

1. Exact EBT formula.
   - Contract is locked.
   - Weights, thresholds, and learning strategy remain unresolved.

2. Memory plane names and counts.
   - Config-driven approach is locked.
   - 11-plane operational structure is accepted.
   - 8-plane and 3-plane lineages remain compatibility views.
   - Final public plane taxonomy should be locked in registry.

3. Expert aliases and auxiliary roles.
   - 19 starting capsules are locked.
   - Alias collisions and auxiliary AOs need registry clarity.

4. Teacher licensing and final cohort.
   - Teacher-as-provider policy is locked.
   - Specific models need current license verification before use.

5. Training reward definitions.
   - Scaffold-first policy is locked.
   - Exact reward spec, dataset schema, and promotion metrics need final registry.

6. GUI/computer-use scope.
   - Candidate direction is accepted.
   - Safety, eval, and protocol rules must be locked before enabling action-taking.

7. Federation.
   - Direction is accepted.
   - Privacy, consent, and data-sharing policy need a concrete implementation spec.

8. Visual diagram source-of-truth.
   - Visualizer requirements are strong.
   - Diagrams must be regenerated from validated canon to avoid stale omissions.

9. Non-linear scaling contracts.
   - Direction is now explicit.
   - Exact schemas for conversation consolidation, scale reports, Neural Bus budget, and RL rollout scaling need implementation specs.

10. Recursive Dreaming protocol internals.
   - Cortex-directed individualized dreaming is locked.
   - Exact dream prompt schema, replay buffer behavior, learning update policy, and promotion criteria remain unresolved.

11. Multi-plane mind map implementation.
   - Plane set and hypergraph direction are strong accepted canon.
   - Exact dimensions, encoders, cross-plane adapter shapes, retrieval weights, and evals remain unresolved.

12. Inaccessible chat 40.
   - It remains outside the evidence base until ChatGPT exposes it or the user provides an export.

## 28. What This Document Should Be Used For

Use this as:

- The basis for a canonical NexusNet spec.
- The guide for converting chat decisions into typed registries.
- The source checklist for operator UI panels.
- The roadmap for implementation gates.
- The decision map for separating locked canon, candidates, unresolved choices, and research-only items.
- The working replacement for the earlier truncated 38-chat synthesis.

Do not use this as:

- A claim that all features are implemented.
- A license clearance record.
- A substitute for raw transcript preservation.
- A substitute for tests.
- A promise that raw 1M-token context is currently available.
- A reason to bypass security/provenance/eval gates.

## 29. Compact Canon Statement

NexusNet is a brain-first, hive-structured neural core. It is built around a canonical NexusBrain path, an Assistant Orchestrators Hive, 19 expert capsules, peer-level Cortex and Router coordination, Neural Bus communication, Mini-NexusNets per expert, non-linear scaling through sparse experts and structured memory, EBT hive routing, a multi-plane Memory Operating System and hypergraph mind map, teacher-model bootstrapping, Cortex-directed Recursive Neural Dreaming, recursive learning through critique/evals/training gates, governed protocol/tool access, trace-first evals, hardware-aware runtime planning, effective long-context assembly, and an operator-grade VisualOps UI. Nexus is the platform shell; NexusNet remains the cognition authority. All research, model, runtime, protocol, memory, dreaming, and training additions must enter through explicit registries with provenance, license, maturity, eval, security, and readiness status.

Post-book rule: the 2026-04-28 complete canon book is the historical source ledger. Any later NexusNet addition that was not present in that book must be captured in a dated canon addendum or assimilation ledger before it can be treated as accepted NexusNet state.
