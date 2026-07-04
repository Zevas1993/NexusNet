# NexusNet Full Architecture Understanding (from the Canon Book)

Status: research synthesis from a systematic read of the 41,529-line canon book
(`docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`) plus the post-book addendum. This corrects
earlier work that was built off the v0 implementation spec only. Sections cite canon message IDs.

## 0. Read coverage
Read: How-To-Read, Master TOC, Concept Index (every component + message weight), Decision & Canon
Marker Index (locked decisions), Artifact & Interface Index (concrete file/struct interfaces),
Aspect chapters 1 (Brain-First), 3 (Cortex/Neural Bus/Hive), 5 (Multi-Plane MemoryNode); post-book
PB-017 (Neuroplasticity), PB-018 (Fractal Mini-Brain), PB-019/020 (child gen + parent retirement).

## 1. The single most important canon decision (C01M0101, C01M0108, C04M0335)
**NexusNet is a neural-network REPLACEMENT/UPGRADE, not an orchestrator.** Locked, repeated:
- "[Final decision] NexusNet is meant to be the replacement/upgrade for a model's current Neural
  network" - not "call different models for different tasks."
- It is implanted into a host model first (cognition kernel atop an LLM/VLM), then grows toward its
  own native model family. It must learn, adapt, assimilate, improve its own code, and become its own
  LLM/VLM/MLM.
- Base = **Mixtral MoE**, existing experts retained; **Devstral** added as a coding expert (must be
  shape-compatible: same hidden dim, FFN shape, dtype - C01M0046/C01M0066/C01M0068).

This is the womb->birth goal stated at the neural level: NexusNet replaces the backbone, not wraps it.

## 2. The mother brain (main NexusNet brain) - internals
From C02M0023, C01M0101/0108, Aspect 3. The primary NexusBrain hosts:
- **MoE Router** (gating network) - sparse expert activation (Mixtral top-k style).
- **Cortex** - a PEER module to the Router (not just above it; C01M0101). The Cortex is the global
  meta-controller AND the **"dream director"**: it "decides what dreams (tasks, scenarios, samples)
  are sent to which experts" and distributes individualized or collaborative dreams to each expert's
  mini-brain (C01M0059/C01M0060). It attends over expert *summaries*, not full hidden states.
- **Multi-plane memory store** (the MemoryNode mind map, section 4).
- **CritiqueAO / Meta Reasoner** - arbitration, consequence feedback, self-review before promotion.
- **SelfTrainingAO** - monitors router gating accuracy/perplexity and triggers router self-training
  (nested self-training: mother brain trains the gating network; each mini-brain trains itself).

Cortex agency is "active planner/teacher/intervener," not a passive aggregator (C01M0062).

## 3. The mini brain (per-expert Mini-NexusNet) - internals
From C02M0022/0023, C06M0021/0028/0029/0043, PB-018.
- Each expert IS its own full neural subnetwork (input/hidden/output layers) - a "Subnetwork Brain,"
  explicitly NOT a prompt wrapper (C06M0021: "each mini brain is its own neural network in the grand
  scheme of the total hive mind neural network").
- Each runs its OWN training loop in parallel with the mother brain (nested self-training, C02M0023),
  under a coordinated schedule respecting the VRAM budget (16GB target hardware).
- **Expert diversity is allowed and intended** (C01M0064): not all experts share one architecture -
  some lightweight, some heavy, some external/symbolic plug-ins. So the Mini-NexusNet contract is an
  interface, not a fixed network shape.
- Each carries explainability hooks ("why" output) for post-hoc trace (C01M0064).
- The project canon counts "19 expert capsules" as the working roster (C03M0032), each a capsule
  subnetwork firing independently when routed.

## 4. Multi-plane MemoryNode (the mind map) - exact struct
From C02M0046/0054/0064, C04M0004, C05M0251. A MemoryNode is a tuple of per-plane subvectors (each
"neuron" is a plane of thought), 11 planes (grew from 8):

```
class MemoryNode(NamedTuple):
    conceptual    # [Hc]  abstract / symbolic reasoning
    temporal      # [Ht]  time, sequence, causality
    emotional     # [He]  affect / valence
    procedural    # [Hp]  skills / how-to
    imaginal      # [Hi]  generative / scenario
    social        # [Hs]  relationships / roles
    ethical       # [Hv]  values / constraints
    metacognitive # [Hm]  self-monitoring
    goal          # [Hg]  intent / objective
    spatial       # [Hsp] layout / geometry
    predictive    # [Hpr] forecast / expectation
```
- **Cross-plane attention**: learnable matrices let one plane attend to another (imaginal->emotional,
  conceptual->procedural). Planes integrate into a unified thought vector (C04M0119).
- **Hypergraph**: MemoryNodes are nodes; typed hyperedges (`trusts`, `aligned_with`, `predicts`)
  connect them across planes (C02M0078 edges.yaml). DreamAO does random walks over the hypergraph,
  sampling MemoryNodes across planes to generate dreams (C02M0046).
- **Data-driven**: planes defined in `planes.yaml` (dims, encoders) so planes can grow by config
  without code rewrites (C02M0071/0086).
- **Associative recall**: Modern Hopfield continuous-state layers for one-step recall + dual-memory
  (fast episodic buffer + slow semantic store) with Elastic Weight Consolidation against forgetting
  (C04M0080/0119).

## 5. Cortex + Neural Bus communication contract
From C01M0066/0068, Aspect 3.
- Neural Bus must be **bandwidth-efficient**: experts send sparse summaries, not full hidden states:
  `(summary_embedding, uncertainty_score, request_for_help_flag, token_ids)` (C01M0068).
- Cortex uses **attention-based aggregation** over expert summaries (attention pooling), not raw
  concatenation. Message heads = mean-pool / max-pool / learned summary.
- "Non-linear scaling": the hive scales by adding experts and routing sparsely, plus long-context
  (RoPE/YaRN to 1M-2M tokens), NOT by one monolith (Aspect 3/4).

## 6. Self-improvement loops (the living-organism layer)
From Aspect 6, PB-017, C04M0119.
- **Recursive (Neural) Dreaming**: Cortex-directed offline self-supervised generation. Distributed
  protocol: high-temp dreamer -> low-temp reviewer -> critic/consequence/eval/sandbox -> governance.
- **Assimilation pipeline**: external data -> ContextController -> MemoryNode encoding -> cross-plane
  attention update -> agent validation -> memory storage.
- **Nested self-training**: mother brain trains the gating/router; each mini-brain self-trains;
  CritiqueAO validates; LoRA/PEFT adapters merge only after validation.
- **Hive-wide neuroplasticity** (PB-017): self-improvement is not owned by one lane; any node can
  request research/dream/critique/sandbox/eval or participate in expert generation, behind gates.
- **Generation + retirement** (PB-019/020): generated children are temporary + shadow-scoped; become
  permanent only after retention review; a parent retires only after Ivy-grade outperformance review
  and is archived (rollback-restorable), never deleted.

## 7. Cross-cutting required subsystems (from Master Spec, C04M0018/0119/0127)
- **Federated, continuous learning** across installs (sanitized deltas only).
- **Security-first**: WASI/sandbox tool isolation, syscall audit, breach containment, fingerprint
  integrity, GPG-encrypted logs/memory.
- **VisualOps**: floating console, live causal trace graphs (UI event -> MemoryNode activation ->
  attention weight), rewindable reasoning, explainability (XAIAgent decision traces).
- **Safe Mode / Auto-Resume**: thermal/VRAM safeguards, throttle/pause on overload (consumer hw).
- **Neuro-symbolic**: lightweight Datalog/constraint layer enforcing hard policy across pipelines.

## 8. How this corrects my earlier kernel/geometry work
- The `HiveTensorKernel` computes ONE brain instance's forward pass. Canon says the SAME interface is
  reused at every brain_scale (mother over experts, O over AOs, expert over skills) AND experts may
  have DIVERSE architectures - so the kernel must be an interface with a default impl, not a single
  fixed network. Mini-brains plug their own forward in.
- Attention over experts is over SUMMARIES with uncertainty + help-request flags, not raw vectors -
  the router input is the Neural Bus summary tuple, and the gate should consume `uncertainty_score`.
- Memory is an 11-plane MemoryNode with cross-plane attention + a hypergraph + Hopfield recall - the
  cosine-retrieval stub in the kernel is only plane-local; the real memory plane is multi-plane.
- The Cortex is a peer dream-director with active agency - not just a softmax router. Dreaming routes
  individualized tasks per expert.
- Sacred geometry / harmonic basis stays the substrate's organizing structure (deterministic-symbolic
  heuristic), now mapped to the 11 planes + the brain-scale hierarchy, not just positions.

## 9. Faithful build order (modular, additive, gated)
1. `MemoryNode` 11-plane struct + cross-plane attention + hypergraph edges (the mind map) as its own
   module with exact-value tests (plane dims, cross-plane attention sums to 1, hyperedge typing).
2. Neural Bus summary contract `(summary_embedding, uncertainty, request_for_help, token_ids)` +
   attention-pooling aggregation in the Cortex.
3. Cortex dream-director: per-expert individualized dream task routing (shadow-only).
4. brain_scale recursion: apply HiveTensorKernel at {primary, orchestrator, assistant_orchestrator,
   expert} with the SAME interface; experts may override forward.
5. Sacred-geometry per-plane signatures (Platonic solid per plane, Euler invariant) + harmonic cadence.
Each step: new package, own tests, additive wiring, shadow-only, gated. No existing module reworked.

## Sources
In-repo canon (hash-pinned): `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md` (Concept Index,
Decision Index, Artifact Index, Aspects 1/3/5, message IDs cited inline);
`docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md` (PB-017/018/019/020 and per-plane ledgers
PB-054..077); `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`.
