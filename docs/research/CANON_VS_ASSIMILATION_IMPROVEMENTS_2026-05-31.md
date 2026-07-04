# Canon Architecture vs. Assimilation Targets That Improve It

Status: research comparison. For each canon hive-mind component (from
`NEXUSNET_FULL_ARCHITECTURE_UNDERSTANDING_2026-05-31.md`), this maps which assimilation targets are
mere restatements vs. which genuinely IMPROVE the canon design, with the concrete upgrade each adds.
All remain research-only / shadow-only until gated. Targets are the numbered online specs (2026-05-06).

## Method
Canon defines the components (NexusBrain mother brain, Cortex dream-director, MoE router, 11-plane
MemoryNode, Mini-NexusNet experts, Neural Bus, recursive dreaming, neuroplasticity). The targets were
written AFTER the canon as a forward research radar. A target "improves" the canon only if it adds a
mechanism the canon names but leaves underspecified, or adds a missing safety/quality property. The
canon's own "Final Missing Piece Synthesis" (spec 134) confirms the gap is a *governed developmental
cortex* with four linked models - i.e. the canon itself points at these targets.

## Improvement map (canon component -> target -> what it ADDS)

| Canon component | Best target(s) | Net improvement over canon |
| --- | --- | --- |
| Cortex (peer router + dream director) | **115 Global Workspace Router** | Canon says Cortex "decides what becomes global"; 115 gives the *mechanism*: an explicit broadcast/ignition gate (goals, anomalies, contradictions, eval failures compete for global visibility). Turns the Cortex from "meta-controller" into a testable global-workspace bottleneck. |
| MoE router over experts | **123 Cortical Reference-Frame Swarm** | Canon experts emit one summary tuple; 123 says each expert keeps a *local model* (object/task/codebase/memory-region) and a consensus router combines them WITHOUT forcing one lossy summary. Fixes the canon Neural Bus's lossy-summary weakness (Thousand-Brains style). |
| Recursive dreaming (Cortex-directed) | **124 Latent World-Model Imagination** + **117 Hippocampal Replay Consolidation** | Canon dreaming generates candidates; 124 adds *rollout before high-risk action* (imagine futures in a latent workspace model); 117 adds the wake/sleep split: capture awake, replay+consolidate+abstract during sleep into reviewable proposals. Makes dreaming predictive and consolidative, not just generative. |
| Self-improvement / candidate generation | **127 GFlowNet Diverse Thought Factory** + **133 Open-Ended Self-Improvement Archive** | Canon generates children + retention review; 127 adds *diversity-preserving* sampling proportional to reward (avoids mode collapse to one expert lineage) with ancestry; 133 adds the shadow-only ancestry-tracked archive (quality-diversity / POET style) the canon's GrowthArchive only sketched. |
| CritiqueAO / consequence feedback | **126 Causal Intervention Cortex** | Canon critiques outcomes; 126 adds *causal* reasoning: identify candidate causal variables in traces, run sandboxed interventions, update routing/memory-confidence/policy from real cause->effect rather than correlation. Upgrades critique from scoring to causal explanation. |
| Governance / immune kernel | **116 Active Inference Homeostatic Agent** | Canon gates actions; 116 adds a *homeostatic objective*: act to restore stable operation (minimize prediction error/uncertainty/contradiction/resource/policy risk) rather than blindly maximize task completion. Gives the immune plane a principled free-energy-style control signal. |
| 11-plane MemoryNode + hypergraph | **129 Semantic Pointer Binding** + **120 Memory-Palace Spatial KAC** + **21 Agent Memory Stack** | Canon stores per-plane subvectors + cross-plane attention; 129 adds *composable* high-dim identities (VSA/HRR binding/unbinding/analogy/conflict detection) so concepts compose and contradictions are detectable; 120 adds spatial/method-of-loci indexing for the spatial plane; 21 adds the working/episodic/semantic tiering. |
| Continuous self-model (implicit in canon) | **125 Continuous Self-Model / Body Schema** | Canon has no explicit operational self-model; 125 adds one (the substrate's live capability/health/degraded-state self-image) - exactly the BodySchema already prototyped in the developmental spine. |
| Runtime adaptation lanes | **131 Liquid Dynamical Cortex** | Canon uses discrete scorecards; 131 adds continuous-time (liquid/CfC) controllers for telemetry, latency/cost, salience decay, homeostatic regulation - smooth adaptation where discrete polling is brittle. |
| Substrate growth model | **130 Neural Cellular Automata** + **118 Bioelectric Morphogenesis** + **119/134 Developmental Embryo/Cortex** | Canon grows by adding experts; 130/118 add *local growth rules* (self-organizing, regeneration, target-shape morphogenesis); 134 frames the whole thing as a staged, measurable, reversible developmental lifecycle - the canon's own "missing piece." |
| Hardware substrate | **113 Neuromorphic Event-Driven** | Adds spiking/event-driven execution lane for the edge/local-first goal; complements not replaces the dense kernel. |

## Targets that are RESTATEMENTS (already in canon, low new value)
- **109/110/111 connectome/whole-brain-emulation** - canon explicitly bounds these as NOT goals
  (no consciousness/upload claims). Keep as research-only watch lanes; do not build.
- **112 organoid ethics** - boundary/ethics doc, not an architecture upgrade.
- **132 autopoietic viability kernel** - overlaps 116 homeostatic; fold into 116.
- **128 intrinsic motivation/empowerment** - real but secondary; useful as a dreaming reward term,
  not a standalone subsystem yet.

## Highest-leverage improvements (ranked, gated, modular)
Ranked by canon-fit x safety x buildability in pure Python, shadow-only:
1. **123 Reference-Frame Swarm** - fixes the canon's lossy-summary Neural Bus weakness; each expert
   keeps a local frame, consensus router combines them. Directly upgrades routing quality.
2. **115 Global Workspace Router** - makes the Cortex's "what becomes global" an explicit, testable
   ignition/broadcast gate. Small, high clarity.
3. **117 Hippocampal Replay Consolidation** - adds wake/sleep consolidation to dreaming; produces
   reviewable abstractions (honest, gated).
4. **124 Latent World-Model Imagination** - rollout-before-risky-action; pairs with the existing
   DreamingSimulator in the developmental spine.
5. **129 Semantic Pointer Binding** - composable concept identities + contradiction detection;
   upgrades the MemoryNode planes from storage to composition.
6. **126 Causal Intervention Cortex** - causal (not correlational) critique; pairs with the existing
   CausalInterventionLab stub.

## How this lands on what is already built
The developmental spine already prototypes the scaffolding for several of these:
- `BodySchema` <- 125 self-model. `DreamingSimulator` <- 124 imagination. `CausalInterventionLab`
  <- 126 causal cortex. `GrowthArchive` <- 127/133 diversity archive. `PromotionTribunal` <- gating.
The improvement is to make each of those *real* per the target mechanism (e.g. GrowthArchive ->
quality-diversity with ancestry; CausalLab -> actual intervention design), and to ADD the two missing
routing upgrades the canon most needs: 123 reference-frame swarm and 115 global-workspace ignition.

## Boundaries (unchanged)
Every improvement is shadow-only, evidence-gated, operator-approved before promotion; no consciousness/
upload/physics claims (109-112 stay bounded); harmonic/sacred-geometry stays deterministic-symbolic.

## Sources
In-repo: numbered specs under `docs/assimilation/online/2026-05-06/` (115,116,117,120,123,124,125,126,
127,129,130,131,133,134 + FINAL_MISSING_PIECE_SYNTHESIS); canon book + post-book addendum;
`docs/research/NEXUSNET_FULL_ARCHITECTURE_UNDERSTANDING_2026-05-31.md`.
