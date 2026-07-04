# Canon Book Deep-Detail Addendum (full review, items earlier passes missed)

Status: research addendum from a detailed review of canon Aspects 4,6,7,9,10,12,14 (earlier docs only
covered 1,2,3,5,8). These are concrete engineering decisions that change how we build and fix the
design. Each cites canon message IDs. Pairs with the engineering blueprint + inspiration docs.

## A. Layer separation (was fuzzy before) - C09M0075, Formal Spec v1.2
- **NexusNet creates Nexus.** Three distinct layers: NexusNet (brain/core), AOs (executive cognitive
  entities), Nexus (host/platform shell). NexusNet is brain-first and starts BEFORE any attached model.
- **Recursive Dreaming applies to AOs**, not just experts.
- **Teachers are replaced when surpassed** (ties to PB-020 parent-retirement, but stated for teachers).
- `attach_base_model()` is the **canonical model-ingestion seam**; NexusNet is NOT a wrapper/gateway.
- Rejected: n8n in core, Ollama-only, Pocketpal as more than a mobile reference.

## B. Native-takeover provenance gate (ENFORCED, not just recorded) - C09M0132/0186
This is the concrete promotion gate for "NexusNet replaces the host model's neural network." A native
takeover candidate is eligible ONLY when ALL hold:
- `product_evidence == true`
- `attachment_mode == "product"`
- a `compatibility_plan_id` exists
- `compatibility_status in {COMPATIBLE, ADAPTER_REQUIRED}`
- lineage is not mixed/incomplete
On failure: takeover stays **shadow/blocked**, promotion is forced to `shadow`, governed runtime
**clamps to teacher fallback** or "needs more evidence." Distillation export must make blocked-takeover
readiness explicit even when artifacts exist (so distillation cannot launder non-product evidence).
=> Build note: this is the real `PromotionTribunal` rule set for native takeover; the developmental
spine's tribunal should encode exactly these five predicates.

## C. Recursive Neural Dreaming v2 (the real dreaming engineering) - Aspect 6, C07M*
Current dreaming = "generate scenarios -> run experts -> critique -> update." v2 is additive:
1. **JEPA world-model sidecar in front of the Dreamer.** Predict in latent space; enforce an
   **isotropic-Gaussian latent (~N(0,I))** via **SIGReg (Sketched Isotropic Gaussian Regularization)**
   on top of a JEPA predictive loss (LeJEPA). Makes dreaming world-model-driven, not just generative.
2. **Sparse-circuit introspection.** Train **SAEs** on 1-2 high-leverage capsule activations
   (Strategist/Security/Critique). Per dream episode log: which sparse features fired, which circuits
   were active, and the outcome (useful/safe/rejected/flagged). Over time learn which circuits produce
   high-value vs risky dreams -> `circuits_risk_score`.
3. **CritiqueAO veto power** over risky dreams; CritiqueAO + Meta Reasoner consume optional signals:
   `pred_err`, `gauss_dev`, `circuits_used`, `circuits_risk_score`.
4. **DreamAdapters** enabled first on 1-2 LOW-RISK capsules; **observe-only mode** before active.
5. Hard rule: changes are **additive, not destructive**; `legacy_dream_cycle` preserved; reviewed
   before implementation; must not break existing behavior.
=> Build note: the existing `DreamingSimulator` becomes the legacy core; add `WorldModelJEPA` sidecar
(latent predictor + SIGReg isotropy check) + `circuits_risk_score` evidence + CritiqueAO veto, all
shadow/observe-only first.

## D. Dreaming modes - Aspect 6
Cortex (dream director) distributes **individualized** dreams per expert, and supports
**collaborative** and **competitive** dream modes (multiple experts dream on the same scenario,
cooperate or compete; outcomes scored). Replay buffers store dream artifacts; learning from them is
gated. => DreamingSimulator should carry a `mode in {individual, collaborative, competitive}`.

## E. Council / Critique / Consequence / Meta-Reasoner - Aspect 7
- **CritiqueAO**: independent review + veto; the governor of dreaming/evolution promotion.
- **Meta Reasoner**: synthesizes multi-expert outputs; sits like a "neural governor/overseer node."
- **Consequence feedback**: pulsing feedback signal from outcomes back into routing/weights (RL-like
  credit assignment), shown as a first-class loop, not an afterthought.
- **Council/advisory + consensus/debate**: experts can advise/debate; promotion uses consensus
  (ties to honeybee quorum in the inspiration doc).
=> Build note: CritiqueAO veto + Meta-Reasoner aggregation are distinct from the Cortex router; the
consequence loop is a feedback edge updating route weights (pair with stigmergy trail update).

## F. Tool invocation + routing - Aspect 10 (C13M*)
- Routing must account for BOTH **MCP tool-call** invocation AND **code-execution** invocation
  (MCP 2.0 "agents run code"). Two parallel **token-budget paths**: Path A high context-overhead,
  Path B low (filtered) ~10x cheaper. Each of the 19 capsules has a **Tool Module**.
- **Tool Invocation Manager (TIM)**, safe-mode, sandboxing, monitoring, fallback are explicit.
=> Build note: the tool action harness should model both invocation styles + a token-budget split,
and the router should treat tool-cost as a routing input.

## G. Runtime / Safe Mode / Neural DNA / QES - Aspect 12 (C12M*, C37M*)
- **Safe Mode is a physiological stress response, not just a pause**: under thermal/VRAM pressure the
  structure should visibly contract/dim/simplify (fewer active capsules, smaller budgets).
- **Neural DNA**: mutates architecture + hyperparameters in production (gated, sandboxed, reversible).
- **Adaptive Runtime Profiler + QES** (Quantization Evolution System): hardware-aware self-optimization;
  a unified **QuantizationProvider** interface over llama.cpp/GGUF, TorchAO, ModelOpt driven by QES
  policies; Adaptive Computation Time. 16GB-VRAM target is a real constraint (left "assistant-supplied"
  in one chat but treated as real elsewhere).
=> Build note: Safe Mode should reduce the active capsule set + deliberation budget under a resource
signal (ties to the homeostatic active-inference target 116); QES sits behind a provider interface.

## H. Federation + governance + containment - Aspect 14 (C04M*)
- **Federated Continuous Learning is MANDATORY** (elevated to core, C04M0143). Sanitized deltas only;
  consent flows; secure aggregation; differential privacy; **every forward pass emits a sanitized
  packet** even when blocked (blocked failure classes are useful hive metadata).
- **Independence Milestones**: `dependency_ratio`, `native_generation`, `plane_maturity`; thresholds
  are **configurable, not hardcoded**. **Model Birth Protocol** governs becoming a native model.
- **Adaptive Safety Boundaries & Containment Rails**: at higher independence (e.g. 75%) additional
  containment activates. GovernanceAO + RACI reject malicious policy updates and auto-revert to last
  approved policy (governance drill suite).
- **External EvalsAO / Auditor Plane** (Bloom-style): evaluation is NOT self-grading; QES promotions,
  backend selection, graph-retrieval changes, and federated updates must NOT self-promote off their
  own homework. EvalsAO gates promotion.
=> Build note: this is the governance spine - the developmental PromotionTribunal must require an
EXTERNAL eval (EvalFederationRegistry, already built) and enforce independence-milestone +
provenance gates before any native-takeover step.

## I. What this CHANGES about the build (corrections/additions)
1. PromotionTribunal must encode the 5-predicate native-takeover gate (B) + external-EvalsAO rule (H).
2. DreamingSimulator -> add JEPA world-model sidecar (SIGReg isotropy), sparse-circuit risk score,
   CritiqueAO veto, dream modes (individual/collaborative/competitive), observe-only-first (C,D).
3. Add a Consequence-feedback edge that updates route weights (E) - pairs with stigmergy trails.
4. Router must consume tool-cost + token-budget path (F) and resource/Safe-Mode pressure (G).
5. QES behind a unified QuantizationProvider interface (G).
6. Federation packet emitted every forward pass, sanitized, even when blocked (H).
7. Independence Milestones (dependency_ratio/native_generation/plane_maturity) as configurable
   thresholds feeding the Model Birth Protocol (H).
8. Three-layer separation enforced: NexusNet creates Nexus; AOs executive; dreaming applies to AOs too (A).

## J. Boundaries (unchanged)
All shadow-only/gated; additive-not-destructive; external eval required; teacher fallback on blocked
takeover; no production self-mutation without sandbox+eval+governance+rollback; no consciousness/upload
claims; harmonic/geometry stays deterministic-symbolic.

## Sources
Canon (in repo, message IDs cited inline): canon book Aspects 4/6/7/9/10/12/14 + Decision/Artifact
indexes; conversations C04, C07, C09, C12, C13, C37. External research already cited in the EBT/Capsule
engineering blueprint, the math-research doc, and the hive-mind inspiration doc (LeJEPA/SIGReg, SAEs/
circuit sparsity, MoE/DeepSeek, RoPE/YaRN, GATv2, Ouro, swarm/DE).
