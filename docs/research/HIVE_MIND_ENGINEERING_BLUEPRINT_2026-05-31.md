# NexusNet AI Hive Mind - Engineering Blueprint

Status: research + engineering synthesis. Answers "how is the hive mind actually supposed to be
designed/engineered" by tying the canon architecture to its verified sources of inspiration and a
buildable, pure-Python, modular, shadow-only construction plan. Supersedes guesswork in earlier docs.

Companion docs:
- `NEXUSNET_FULL_ARCHITECTURE_UNDERSTANDING_2026-05-31.md` (what the canon says)
- `HIVE_NEURAL_SUBSTRATE_MATH_RESEARCH_2026-05-31.md` (per-op math, researched)
- `HIVE_MIND_ARCHITECTURE_AND_SACRED_GEOMETRY_2026-05-31.md` (geometry per plane)
- `CANON_VS_ASSIMILATION_IMPROVEMENTS_2026-05-31.md` (which targets upgrade the canon)

## 1. The building block: the Capsule Neuron (canon C12M0048/0064, source: Capsule Networks)
Canon: "The fundamental building block of NexusNet is the Capsule Neuron, inspired by Capsule
Networks but extended for a multimodal, context-sensitive environment. Each capsule is a
self-contained unit with its own input, hidden, output layers; specializes in a domain; activates
only when relevant tokens arrive." The NexusNet core itself is also a structured capsule network
(input->hidden->output), the master brain at the hive center (C06M0123).

Verified source - Capsule Networks (Sabour/Hinton 2017, arXiv:1710.09829):
- **Pose vector**: a capsule's output is a VECTOR; its LENGTH = probability the entity is present,
  its ORIENTATION = instantiation parameters. (Not a scalar activation.)
- **Squash**: `squash(s) = (||s||^2 / (1 + ||s||^2)) * (s / ||s||)` - shrinks length into [0,1) as a
  probability while preserving direction. This is the capsule nonlinearity.
- **Routing-by-agreement**: lower capsules send output to higher capsules whose prediction AGREES
  (high dot product). Iterative: coupling coefficients `c_ij = softmax(b_ij)`; update
  `b_ij += u_hat_{j|i} . v_j` over a few iterations.

NexusNet mapping: each expert = a capsule (pose vector = its summary + confidence); the Cortex/Router
combines capsules by agreement, not just top-k softmax. This is EXACTLY the canon Neural Bus tuple
`(summary_embedding, uncertainty, request_for_help, token_ids)` - the pose vector IS the summary, the
uncertainty IS the inverse of squash length. Routing-by-agreement is the principled version of the
"reference-frame consensus router" (assimilation target 123).

## 2. The decision core: EBT routing (canon C11/C12, source: Energy-Based Transformers)
Canon: "EBT Core Routing - Energy-Based Transformer used in routing + selection (approved July 26)";
"the EBT module is integrated into the Meta Reasoner AND into expert capsules to optimize them at
runtime"; "layered EBT that refines decisions dynamically, not statically."

Verified source - Energy-Based Transformers (Gladstone 2025, arXiv:2507.02092):
- An EBT assigns an **energy** to every (input, candidate-prediction) pair; lower energy = more
  compatible. Prediction = start from a guess and **minimize energy by gradient descent** until
  convergence. This IS "thinking"/System-2: more optimization steps = more deliberation.
- It's a learned **verifier**: re-frames prediction as optimization against a compatibility score,
  works on any modality, no external verifiable reward needed.

NexusNet mapping: this is the engineering meaning of "recurrent deliberation + exit gates" and the
Cortex's decision refinement. A route/answer candidate is scored by an energy function; the recurrent
loop does a few gradient/refinement steps lowering energy; the hazard-exit gate stops when energy
stops improving (convergence) or max-loops. The energy minimization is the "dynamic, not static"
refinement the canon demands. v0 pure-Python: finite-difference / coordinate descent on a scalar
energy over a small candidate vector (deterministic, testable), with the step count as the
deliberation budget.

## 3. The full forward path (canon C12M0056/0060/0064 - Input Preprocessing Engine)
```
raw input
  -> Input Normalization (learned scale/center: (x-mean)/std)        [C12M0064]
  -> Token Embedding (typed multi-plane embedding)
  -> Energy Encoding (initial energy / routing condition)            [EBT]
  -> Positional (RoPE + golden-angle harmonic basis)                 [math doc]
  -> Capsule Router (routing-by-agreement + EBT energy + harmonic resonance prior)
       activates a sparse set of expert capsules (each input->hidden->output)
  -> Expert capsules compute (GeGLU/SwiGLU FFN), emit pose vectors
  -> Recurrent Deliberation (EBT energy minimization, N steps, hazard exit)
  -> Residual + RMSNorm consolidation
  -> Cross-plane MemoryNode update (11 planes + cross-plane attention + hypergraph)
  -> Cortex aggregation (attention-pool over capsule pose vectors)
  -> Action/Output projection
  -> Checkpoint/trace ledger (every step recorded; shadow-only)
```
The SAME path runs at every brain_scale (mother brain over experts; O over AOs; expert over skills) -
the fractal nesting (PB-018). Experts may have diverse internal architectures (C01M0064); the capsule
interface (pose-vector in/out) is the contract, not a fixed network.

## 4. Sources of inspiration - confirmed, with their engineering contribution
| Source | Verified mechanism | NexusNet engineering use |
| --- | --- | --- |
| Capsule Networks (1710.09829) | pose vectors, squash, routing-by-agreement | the Capsule Neuron building block + agreement routing |
| Energy-Based Transformers (2507.02092) | energy verifier, predict-by-energy-minimization, System-2 | EBT routing/selection + recurrent deliberation/exit |
| Attention Is All You Need | scaled-dot-product softmax | attention/focus plane |
| Sparsely-Gated MoE / Switch / GShard | sparse top-k experts | router sparse activation |
| DeepSeek loss-free balancing (2408.15664) | per-expert bias on selection only | balanced routing without aux-loss |
| GLU variants (2002.05202) | SwiGLU/GeGLU FFN | expert feed-forward |
| RMSNorm (1910.07467) | mean-square normalize | residual normalization |
| RoPE / YaRN | rotary positions, long-context scaling | positional plane (1M-2M ctx goal) |
| GATv2 (2105.14491) | dynamic neighbor attention | Neural Bus graph message-passing |
| Ouro LoopLM (2510.25741) | parameter-shared recurrent depth | the fractal recursion + deliberation loops |
| Modern Hopfield | one-step associative recall | MemoryNode fast episodic recall |
| Thousand Brains / reference frames (target 123) | many local models + consensus | reference-frame swarm routing |
| Global Workspace (target 115) | ignition/broadcast bottleneck | Cortex global-visibility gate |
| Golden ratio / Platonic solids / harmonics | phi, Euler V-E+F=2, harmonic ratios | deterministic-symbolic organizing basis per plane |

## 5. Engineering principles locked by canon (the design intentions)
1. **Replace, don't wrap** (C01M0101): NexusNet is the neural network, implanted into a host model
   first, growing to its own native model. The kernel must be a real forward pass, not a prompt shim.
2. **Capsule + pose vector** is the unit; **routing-by-agreement + EBT energy** is the decision.
3. **Fractal self-similarity**: one kernel interface at every brain scale; experts may differ inside.
4. **Sparse activation, full connectivity** (PB-017): compute is sparse, awareness/monitoring is not.
5. **Bandwidth-efficient Neural Bus**: pose-vector summaries + uncertainty + help-flag, not full state.
6. **Multi-plane memory** (11 planes) with cross-plane attention + hypergraph + Hopfield recall.
7. **Cortex is the dream director** (peer to router), with active agency, distributing per-expert dreams.
8. **Everything gated**: shadow-only, evidence-ledgered, eval+governance+operator-approval before any
   promotion; no native weight mutation in v0; no consciousness/upload/physics claims.
9. **Local-first, consumer hardware** (16GB VRAM target): pure-Python deterministic kernels first;
   real tensor backends added behind the same interface later.
10. **Deterministic-symbolic geometry/harmonics** organize routing/cadence; never bypass the real gate.

## 6. Buildable construction plan (modular, additive, TDD, shadow-only)
Build the real neural network and components in this order. Each = new self-contained module under
`nexusnet/hive/kernel/` (or a sibling), own exact-value tests, additive wiring, no rework of existing
modules. Builds on the HiveTensorKernel already shipped (softmax/SwiGLU/RMSNorm/RoPE/top-k/loss-free).

- **B1. Capsule Neuron** (`capsule.py`): pose vector in/out, `squash()`, an input->hidden->output
  forward (RMSNorm + SwiGLU). Tests: squash length in [0,1) and direction preserved; deterministic.
- **B2. Routing-by-agreement** (`agreement_routing.py`): iterative coupling `c_ij=softmax(b_ij)`,
  agreement update, combined with the existing harmonic-resonance + loss-free-bias gate. Tests:
  coupling sums to 1 per lower capsule; agreement increases for aligned poses.
- **B3. EBT deliberation** (`ebt.py`): scalar energy `E(input, candidate)`, predict-by-minimization
  (coordinate/finite-diff descent), step count = deliberation budget, hazard-exit on convergence.
  Tests: energy decreases monotonically to a fixed point; more steps -> lower energy; exit fires.
- **B4. Capsule Router + forward** (`capsule_forward.py`): the section-3 path composing B1-B3 + the
  shipped ops; emits pose vectors, runs deliberation, consolidates. Tests: end-to-end real numbers,
  sparse activation, attention sums to 1, output finite.
- **B5. MemoryNode** (`memory_node.py`): 11-plane tuple, cross-plane attention (sums to 1), hypergraph
  edges, Hopfield one-step recall. Tests: plane dims, cross-plane attention normalized, recall returns
  nearest stored pattern.
- **B6. Cortex dream-director** (`cortex.py`): global-workspace ignition gate (target 115) over
  capsule pose vectors + per-expert dream task routing (shadow-only). Tests: only top-salience signals
  ignite; dreams are per-expert; nothing mutates production.
- **B7. Fractal scale runner** (`brain_scale.py`): apply the capsule forward at
  {primary, orchestrator, assistant_orchestrator, expert} with the same interface; experts may
  override. Tests: same kernel runs at each scale; child override respected.
- **B8. Substrate ledger integration**: each plane's existing ledger payload gains a `computed` block
  (real numbers from B1-B7) beside its `formula_ref` label, plus `geometry_signature` (Platonic solid
  per plane, Euler==2) and harmonic cadence. Additive; no plane removed.

After B1-B8 the substrate computes a real, deterministic, fractal capsule-EBT forward pass with
multi-plane memory and a dream-director Cortex - the actual neural network the canon designs - while
every decision stays gated and shadow-only.

## 7. Boundaries (unchanged)
Pure-Python deterministic first; no native weight training, production mutation, consciousness/upload,
or physics claims in this layer. Harmonic/sacred-geometry stays deterministic-symbolic. All shadow-only
until eval/governance/operator gates pass.

## Sources
Canon (hash-pinned in repo): canon book Aspects 2/3/5/8 + Master Blueprint messages C11M0003/0004/0018,
C12M0040/0048/0056/0060/0064, C06M0123; post-book PB-017/018/019/020.
External (researched 2026-05-31):
- Energy-Based Transformers: https://arxiv.org/abs/2507.02092 , https://energy-based-transformers.github.io/
- Capsule Networks / Dynamic Routing: https://arxiv.org/pdf/1710.09829
- (plus the math-doc sources: MoE/DeepSeek 2408.15664, GLU 2002.05202, RMSNorm 1910.07467, GATv2
  2105.14491, Ouro 2510.25741, RoPE/YaRN.)
