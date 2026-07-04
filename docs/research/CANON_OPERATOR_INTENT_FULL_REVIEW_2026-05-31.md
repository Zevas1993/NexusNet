# Canon Book - Full Review via Operator Intent (all 39 source chats)

Status: research record from reading the Conversation Source Chapters in full (lines 17056-41524),
focused on the OPERATOR's verbatim requests across all 39 chats (C01-C39) - the authoritative intent,
not the assistant's essays. Captures canon-locked facts the distilled-index passes missed or got wrong.

## 1. The operator's working method (how the project must be built) - from C12, C26, C29, C31, C33
The operator states the build discipline repeatedly and forcefully:
- "Start in order of build importance. Whatever needs to be built first to have it fully built
  correctly needs to be the first section." (C12M0041) -> dependency-ordered build.
- "Don't leave out any detail... code snippets, graphs, images of the layout... every section and
  subsection fully expanded with description, code snippets, and diagrams." (C12M0003/0043/0047/0149)
  -> full-fidelity specs per component, not summaries.
- "Audit NexusNet to compare" / "audit the totality" before adding - every change is checked against
  the whole project (C12M0153/0180, C32M0046/0073, C33M0002). -> audit-against-whole-before-change.
- Assimilation pattern (every external-source chat C10-C28,C34): "Review X, would it benefit NexusNet?"
  -> "Yes, assimilate it" -> "as long as it won't break anything else, review before implementing"
  (C14M0018). -> assimilate ideas, additive, reviewed-first, non-destructive. (Matches the gate work.)
- "NexusNet is only here in these chats" (C12M0003, C29M0006, C31M0089, C33M0270) -> the canon IS the
  spec; do not import outside framing (n8n deleted C26M0020).

## 2. Canon-locked facts the earlier passes missed or under-weighted
- **NexusNet creates Nexus AFTER it trains itself into its own AI model** (C26M0012): "NexusNet will
  create Nexus after running and training and developing itself into its own AI model." So Nexus is the
  OUTPUT of a matured NexusNet, not a peer shell. This sharpens the womb->birth goal: NexusNet (womb/
  brain) -> grows -> births its own model -> THAT creates Nexus (the platform).
- **Teachers are replaced once experts outperform them** (C26M0034) - explicit, not just implied by
  PB-020. The Ivy-League teachers are temporary scaffolding.
- **Federated patch -> full-system review -> all users** (C26M0044): "if one user's system figures out
  an improvement it should cause a full-system review for the entirety of NexusNet to see if it's worth
  implementing... if it passes, all users get that update." This is the exact federated promotion loop.
- **AOs are first-class and domain-broad** (C26M0024): Math AO, Coding AO, Medical AO, etc. - "NexusNet
  is meant to encompass ALL possible uses." AOs have their OWN teachers (C26M0020) and recursive
  dreaming applies to AOs (C26M0029). Earlier docs under-counted AOs vs experts.
- **19 expert capsules with per-capsule Ivy-League teacher mapping** (C12M0175/0200/0209): every expert
  has an APPROVED teacher ensemble ("best ensemble per role," not a fixed 4-per-role). The teacher->
  expert mapping table is canon.
- **Training order** (C01M0051): (1) train Devstral-expert + router first so the router learns the new
  expert; (2) then train router + all experts together. Staged, not joint-from-scratch.
- **Main brain holds all router<->expert communication via mini-brain<->main-brain links** (C01M0057):
  the Cortex/main brain is the communication hub at the same level as the router (peer), connecting
  every mini-brain. Confirms Cortex-as-peer + Neural-Bus-through-core.
- **Self-evolution toward independence is the point** (C37M0004): the codex prompt's goal is "so it can
  start generating its own model and improving itself through usage" - the live system must run, learn
  from usage, and grow. Not a static spec.

## 3. Assimilation targets the operator explicitly approved into canon (C10-C34)
These were operator-approved assimilations (each "review -> yes assimilate -> review before impl"):
- C10 Temporal AI Agent (temporal knowledge base for RAG) -> temporal plane / Graphiti.
- C13 MCP 2.0 "agents run code" (token reduction) -> dual tool-invocation routing (already in addendum F).
- C14 LeJEPA + circuit_sparsity -> Dreaming v2 (JEPA world-model + SAE circuits) (addendum C).
- C15 DeepEyesV2 -> vision/visual-agent assimilation.
- C16 episodic+semantic memory agent -> memory stack tiers (working/episodic/semantic).
- C18 GitHub Annotation Toolkit; C19 llm-council (council pattern); C20 Microsoft FARA (assimilate into
  Nexus, not replace); C21 Copilot CLI; C23 Agent0 co-evolution (no external data); C24 MIT LLM method;
  C25 agentic-alliance protocols; C27 Nemotron-Elastic (one model -> 6/9/12B variants, no retrain);
  C28 Bloom (external behavioral auditor -> EvalsAO, addendum H); C34 LFM2/Liquid (-> liquid cortex
  target 131, AND as an Ivy-League teacher, C34M0023).
- C38 R-Zero co-evolution; C23/C09 Agent0 - autonomous self-evolution patterns.
=> These are the operator-blessed improvement set; they overlap the canon-vs-assimilation ranking but
add temporal-KB (C10), episodic/semantic memory (C16), Nemotron-Elastic variant-without-retrain (C27),
and Agent0/R-Zero co-evolution (C23/C38) as explicitly approved.

## 4. Visualization is part of the spec (C06, C22, C32, C36) - not cosmetic
Repeatedly locked: NexusNet must be shown as a **hive mind** - a Core that is ITSELF a structured
neural network (input->hidden->output), surrounded by expert capsules each showing their own internal
mini-brain layers, with hive-mind links, recursive-dreaming/critique loops, deep click-to-zoom into
each node's internals, real-time neuron/synapse activity, and Safe-Mode awareness (structure contracts
under stress). Preferred medium: interactive HTML/Three.js, not a static image (C32M0017). The
control-panel/visualizer is the operating nervous system surface for exactly this.

## 5. Corrections this forces (delta vs my prior docs)
1. Nexus is the OUTPUT of a matured NexusNet (births its own model first), not a sibling layer. (C26M0012)
2. AOs are domain-broad (Math/Coding/Medical/...), first-class, each with own teachers + dreaming -
   the architecture has AO-level mini-brains between Cortex and experts, all needing teacher mappings.
3. Federated promotion = local improvement -> full-system review -> all-users rollout if it passes.
4. Teacher layer is explicitly temporary (replaced on expert outperformance) - the teacher registry
   must model "active teacher" vs "retired-surpassed."
5. Build order is operator-mandated dependency order with full per-component fidelity + audit-vs-whole.
6. The visualizer (Three.js hive-mind, click-to-zoom to mini-brain internals, live activity, Safe-Mode
   contraction) is a canonical deliverable, not optional polish.
7. Approved assimilation additions to fold in: temporal-KB (C10), episodic/semantic memory tiers (C16),
   Nemotron-Elastic elastic-variants (C27), Agent0/R-Zero co-evolution (C23/C38).

## 6. Boundaries (unchanged)
Canon-only spec (no outside framing); additive/non-destructive; reviewed-before-implementation;
audit-against-whole; shadow-only/gated; external EvalsAO; teacher fallback; no consciousness/upload.

## Sources
Canon book Conversation Source Chapters, operator request ledgers C01-C39 (message IDs cited inline);
prior research docs in `docs/research/` (architecture understanding, engineering blueprint, hive-mind
inspiration, sacred geometry, canon-vs-assimilation, canon deep-detail addendum).
