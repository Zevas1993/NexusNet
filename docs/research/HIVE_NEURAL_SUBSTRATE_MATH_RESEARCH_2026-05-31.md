# Hive Neural Substrate - Architecture and Math Research

Status: research document. Defines the intended math for the AI Hive Mind neural substrate
before any kernel code is written. Pure-Python, deterministic, local-first (no numpy dependency),
matching the existing `_matmul`/`_softmax` style in `nexusnet/growth/production_spine.py`.

Sources of truth:
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md` (plane model + research table)
- `docs/superpowers/specs/2026-05-01-nexusnet-full-harness-doctrine-design.md` (organism model)
- `nexusnet/hive/substrate.py` (current v0 ledger implementation + harmonic constants)

## 1. Why this document exists

The current substrate (`nexusnet/hive/substrate.py`, ~12.5k lines) is a complete **evidence/ledger
layer**: it records 16 ordered planes, harmonic constants, trace records, and activation-function
*labels* such as `formula_ref: "exp(x_i)/sum(exp(x_j))"` and `softmax_normalized: true`. These are
descriptive strings and flags, not computations over real activation vectors. The only place real
tensor math executes today is `HiveTensorProgram` in `production_spine.py` (`_matmul`, `_softmax`,
`_l2_delta`), proven by `tests/test_nexusnet_production_spine.py` (`matmul_result == [[19,22],[43,50]]`).

The substrate spec itself states this was intentional (v0 note 8.2): *"These artifacts are v0 JSON
artifact ledgers first."* So the substrate is **architecturally complete but mathematically a stub**.
This document specifies the math so a real `HiveTensorKernel` can compute what the planes currently
only label, and store the numeric result next to the formula reference.

## 2. The AI Hive Mind architecture (organism model)

Four cooperating organism layers (doctrine spec):

1. **NexusBrain authority** - final routing/policy/promotion/containment. Owns the forward pass.
2. **AO Hive** - assistant-orchestrator departments (Research, Assimilation, Sandbox, Eval, Red-Team,
   Governance, Dean, Federated, Historian). Movable/replaceable via explicit contracts.
3. **Expert mini-brains** - modular MoE-style specialists with identity, tool perms, memory planes,
   lineage, runtime fit, reliability history, promotion/retirement metadata.
4. **Harness UI + Neural Bus** - control panel as nervous system; Neural Bus carries typed events.

Mapped to neural-network semantics (substrate spec §1):
- Nodes = AOs/experts/tools/models/sandboxes/memory/policy/evaluators
- Edges = task deps, trust, routing history, capability affinity, provenance
- Weights = performance/confidence/risk/usefulness/latency/cost/privacy/approval/reliability
- Activations = typed task signals on the Neural Bus
- Forward pass = task execution through the planes
- Recurrent loops = deliberation/self-review/dreaming/sandbox-retry
- Loss = eval results + operator feedback + regressions + security + cost drift
- Optimization = Ivy-League School over experts/routes (NOT weight backprop in v0)

## 3. The 16 substrate planes (from NEURAL_RUNTIME_INPUT_CONTRACT)

Ordered: sensory/input -> embedding/representation -> temporal/positional -> neural-bus/message-passing
-> attention/focus -> sparse-MoE-router -> expert-computation(feedforward/microcircuit) -> pathway/
transmission -> plasticity/neuromodulator -> recurrent-deliberation(latent-loop) -> memory/engram(kv-cache)
-> learning/eval/loss(backprop) -> optimizer/school -> residual-normalization -> action/output -> checkpoint/ledger.

Each plane below gets: its research source, the exact formula it should compute, inputs/outputs,
dimensions, and the invariant a unit test must assert.

## 4. Per-plane math specification

### 4.1 Embedding / Representation plane
- Source: Attention Is All You Need (typed feature vectors stand in for learned embeddings in v0).
- Formula: deterministic feature hashing of a typed token into a fixed-dim vector
  `e[j] = sum over tokens t of sign(h(t,j)) * value(t)`, then L2 normalize.
- L2 normalize: `x_hat = x / sqrt(sum(x_i^2) + eps)`, eps = 1e-12.
- Output dim: d_model (propose d_model = 16 for v0, a Fibonacci-adjacent small dim).
- Invariant: `abs(norm(x_hat) - 1.0) < 1e-6` for any nonzero input.

### 4.2 Temporal / Positional plane (rotary, golden-angle)
- Source: rotary positional encoding + existing harmonic kernel (`_harmonic_phase`).
- Formula (per 2-dim pair k at position p): theta = position * golden_angle_radians * phi^-k
  `[x'_2k, x'_2k+1] = [x_2k*cos(theta) - x_2k+1*sin(theta), x_2k*sin(theta) + x_2k+1*cos(theta)]`
  where golden_angle_radians = radians(GOLDEN_ANGLE_DEGREES) and phi from existing PHI constant.
- Invariant: rotation preserves norm: `abs(norm(rotated) - norm(original)) < 1e-9`.
- This makes the existing golden-angle metadata an actual transform, not just a phase label.

### 4.3 Attention / Focus plane (softmax attention)
- Source: Attention Is All You Need (scaled dot-product attention).
- Formula:
  `scores[i] = (q . k_i) / sqrt(d_k)`
  `attn = softmax(scores)`  (stable: subtract max before exp)
  `context = sum_i attn[i] * v_i`
- Stable softmax: `p_i = exp(s_i - max(s)) / sum_j exp(s_j - max(s))`.
- Invariant: `abs(sum(attn) - 1.0) < 1e-9` and all `attn_i >= 0`. This is what makes
  the current `softmax_normalized: true` claim provable instead of asserted.

### 4.4 Sparse MoE Router plane (top-k gating)
- Sources: Sparsely-Gated MoE (Shazeer 2017), Switch Transformers, GShard.
- Formula:
  `gate_logits[e] = w_e . x` for each expert e (w_e = expert capability vector)
  `gate = softmax(gate_logits)`
  top-k: keep the k highest gate weights, renormalize over the kept set:
  `gate_topk[e] = gate[e] / sum_{e in topk} gate[e]` for e in top-k, else 0.
- Load-balancing aux signal (Switch): `importance[e] = sum over tokens gate[e]`;
  report coefficient of variation `cv = std(importance)/mean(importance)` as a balance score
  (recorded as evidence, not used to mutate in v0).
- Invariant: exactly k experts have nonzero weight; `abs(sum(gate_topk) - 1.0) < 1e-9`.
- This replaces the current `_normalize_weight_records` heuristic with real gated routing.

### 4.5 Expert Computation plane (GeGLU feed-forward)
- Sources: GShard/Switch FFN experts; GLU-variants (GeGLU).
- Formula: `FFN(x) = (GELU(x @ W_gate) elementwise* (x @ W_value)) @ W_out`
  - GELU (tanh approx): `0.5*x*(1 + tanh(sqrt(2/pi)*(x + 0.044715*x^3)))`
- Invariant: with identity-ish init weights, output dim == d_model; deterministic for fixed inputs.

### 4.6 Residual / Normalization plane (RMSNorm + residual)
- Sources: ResNet (residual), LayerNorm, RMSNorm.
- Formula: `rmsnorm(x) = x / sqrt(mean(x^2) + eps) * g` (g = gain, default 1).
  Residual: `y = x + sublayer(rmsnorm(x))` (pre-norm).
- Invariant: `abs(rms(rmsnorm(x)) - 1.0) < 1e-6` (unit RMS) for g=1; residual preserves x when
  sublayer output is 0.

### 4.7 Recurrent Deliberation plane (latent loop + hazard exit)
- Source: Ouro LoopLM (recurrent latent computation + exit gates).
- Formula per loop t: update hidden state `h_t = rmsnorm(h_{t-1} + block(h_{t-1}))`;
  exit gate: hazard `lambda_t = sigmoid(w_exit . h_t)`, survival `S_t = prod_{<=t}(1 - lambda_j)`,
  exit probability `p_exit(t) = lambda_t * S_{t-1}`. Stop when cumulative exit prob >= threshold
  or `max_loops` reached (existing exit-gate metadata: confidence/risk/disagreement/max_loops).
- Invariant: `sum_t p_exit(t) + S_T == 1.0` (proper survival distribution) within 1e-9.
- phi-decay cadence (existing `_loop_harmonic_cadence`) becomes the per-loop step scale.

### 4.8 Plasticity / Neuromodulator plane (bounded reward modulation)
- Sources: eligibility traces (RL) + bounded symbolic modulation (existing `_bounded_delta`).
- Formula: `delta_w = clip(eta * reward_signal * eligibility, -0.05, +0.05)`;
  eligibility decay `e_t = phi^-t` (existing `eligibility_decay`); tanh-bounded reward
  `r = tanh(raw_reward)`. v0 records the proposed delta; it does NOT mutate active weights.
- Invariant: `abs(delta_w) <= 0.05` always (matches existing `_bounded_delta` clamp).

### 4.9 Message-Passing plane (Neural Bus / graph aggregation)
- Sources: Message Passing Neural Networks (Gilmer 2017), Graph Attention Networks (GAT).
- Formula (GAT-style neighbor aggregation):
  `alpha_ij = softmax_j( leaky_relu(a . [W h_i || W h_j]) )`
  `h_i' = sum_j alpha_ij * W h_j`
  leaky_relu(x) = x if x>0 else 0.01x.
- Invariant: `abs(sum_j alpha_ij - 1.0) < 1e-9` per node i.

### 4.10 Memory / Engram plane (KV lookup + cosine retrieval)
- Sources: RAG, Differentiable Neural Computer, Engram conditional memory.
- Formula: cosine similarity retrieval `sim(q,m) = (q . m)/(norm(q)*norm(m))`; return top-k memory
  rows by sim; KV-cache hit = exact-key match else compute. (Existing memory planes already store
  provenance; this adds the actual similarity score.)
- Invariant: `-1 <= sim <= 1`; identical vectors give sim == 1 within 1e-9.

### 4.11 Learning / Eval / Loss plane (scalar losses, NOT weight backprop)
- Sources: Scaling Laws/Chinchilla (track axes), Adam (optimizer-over-scores).
- Formula: MSE `L = mean((y_hat - y)^2)`; cross-entropy for gate targets
  `L = -sum_i y_i*log(p_i + eps)`. v0 computes loss scalars for evidence/routing-weight updates,
  NOT gradients into model weights (doctrine: no native weight training in v0).
- Invariant: `L >= 0`; MSE == 0 iff y_hat == y.

### 4.12 Harmonic geometry kernel (already real, keep + bound)
- Existing constants are genuinely computed (PHI, golden angle, Fibonacci, intervals).
- Keep `claim_boundary: "deterministic-symbolic-math-heuristic-not-physics-claim"` - these are
  deterministic spacing/cadence heuristics, NOT a physics or consciousness claim. The kernel must
  not let harmonic values silently drive routing without the computed gate scores above.

## 5. One real forward pass (composition target)

```
typed input -> embed(4.1) -> rotary(4.2) -> [loop t (4.7):
    attention(4.3) over context
    -> router top-k(4.4) -> selected experts geglu(4.5)
    -> residual + rmsnorm(4.6)
    -> hazard exit gate ] -> linear projection -> output vector
```
Every step stores its computed numeric result next to its existing `formula_ref` label, plus the
invariant check (sum-to-1, unit-norm, bounded-delta) as machine-checkable evidence.

## 6. Proposed module shape (pure Python, modular)

`nexusnet/hive/kernel/` (new, self-contained; imports no other nexusnet surface):
- `tensor_ops.py`: `matmul`, `dot`, `softmax`, `l2_normalize`, `rms_norm`, `sigmoid`, `gelu`,
  `geglu`, `leaky_relu`, `cosine`, `rotary_pair`, `top_k_gate`, `hazard_exit`, `mse`, `cross_entropy`.
- `forward.py`: `HiveTensorKernel.forward(...)` composing section 5.
- `__init__.py`: exports.
- `tests/test_hive_tensor_kernel.py`: exact-value tests (e.g. `softmax([1,2,3])` known values,
  `matmul` like the existing `[[19,22],[43,50]]` test) + every invariant in section 4.

Substrate integration is additive: the attention/router/normalization/loop ledger payloads gain a
`computed` block (the real numbers) beside the existing `formula_ref`/`softmax_normalized` fields.
No existing plane is removed; the labels stay as documentation and the computation becomes real.

## 6b. Harmonic / golden-ratio / sacred-geometry computational basis (REQUIRED)

The harmonic constants are not decoration. They are a real, deterministic computational basis that
modulates the neural ops above. Every item below is computed numbers with an asserted invariant, and
all stay inside `claim_boundary: "deterministic-symbolic-math-heuristic-not-physics-claim"`.

Constants (reuse existing substrate values): `PHI = 1.61803398875`,
`GOLDEN_ANGLE = radians(360*(1 - 1/PHI))`, `FIBONACCI = [1,1,2,3,5,8,13,21,...]`,
`HARMONIC_RATIOS = [1/1, 6/5, 5/4, 4/3, 3/2, 2/1]` (unison..octave).

1. **Harmonic-frequency positional encoding** (replaces geometric `10000^(-2k/d)` with a harmonic series):
   `freq_k = base * HARMONIC_RATIOS[k % len]^(-floor(k/len)-1)` (descending harmonic partials)
   `pe[2k] = sin(position * freq_k)`, `pe[2k+1] = cos(position * freq_k)`.
   Invariant: each `(pe[2k], pe[2k+1])` lies on the unit circle: `pe[2k]^2 + pe[2k+1]^2 == 1` (1e-9).

2. **Golden-angle rotary** (section 4.2 made harmonic): `theta_k = position * GOLDEN_ANGLE * PHI^-k`.
   Real 2D rotation; norm-preserving. Golden angle gives maximally-spread, non-repeating phases
   (the phyllotaxis property) so positions stay distinguishable.

3. **phi-decay weighting**: `phi_weight(k) = PHI^-(k+1)` applied as a real multiplicative scale on
   per-expert / per-loop contributions and as eligibility decay (matches existing `_phi_weight`).
   Invariant: strictly decreasing, `0 < phi_weight(k) < 1`, `sum_k phi_weight(k)` converges to
   `1/(PHI-1) = PHI` (geometric series), reported as evidence.

4. **Harmonic-resonance routing** (makes existing `routing_formula` real): for expert e,
   `resonance_e = (capability_overlap_e + 1) * HARMONIC_RATIOS[e % len] * phi_weight(rank_e)`,
   then `gate_logits_e += log(resonance_e)` before the top-k softmax (section 4.4). So harmonic
   resonance is a computed prior on the gate, not a label. Invariant: gate still sums to 1 over top-k.

5. **Fibonacci loop cadence**: recurrent loop t uses step scale `PHI^-t` and cadence interval
   `HARMONIC_RATIOS[(t-1) % len]` (matches existing `_loop_harmonic_cadence`), feeding the hazard
   exit gate timing (section 4.7).

6. **Harmonic resonance score** (bounded heuristic, evidence-only): `resonance_score = bounded(
   product of active HARMONIC_RATIOS normalized to [0,1])` — recorded, never used to bypass the
   real gate/eval. Keeps the "sacred geometry" surface honest: it scores, it does not decide.

These give the substrate a genuine golden-ratio/harmonic identity that is *computed and testable*,
while the actual routing/promotion decisions still require the real softmax/eval/governance gates.

## 7. Boundaries (unchanged)

- v0 computes a real forward pass over typed vectors; it does NOT train native model weights,
  perform production self-mutation, or make consciousness/sentience/physics claims.
- Harmonic/golden-ratio values remain deterministic symbolic heuristics, not physical claims.
- All outputs stay shadow-only evidence until eval/governance gates pass.

## 7b. Online research findings - real variants (2026 state of the art)

The v0 formulas above used 2017-era defaults. Online research (sources at end) shows each component
has evolved; the substrate should track the current real designs, not the oldest one. Key corrections:

### Attention - MHA / GQA / MLA (not just vanilla MHA)
- **MHA** (vanilla): full Q/K/V heads. Memory bottleneck is the KV cache.
- **GQA** (grouped-query, Llama-2/3, Mistral): adjacent Q heads share one K/V head. KV cache shrinks
  by the group factor. `n_kv_heads < n_q_heads`, K/V projected once per group.
- **MLA** (multi-head latent attention, DeepSeek-V2/V3): compress K/V into a low-rank latent
  `c = x W_DKV` (down-proj), cache only `c`, reconstruct `K = c W_UK`, `V = c W_UV` at use time.
  Most aggressive KV compression; current SOTA for long context.
- **Substrate choice:** v0 kernel keeps scaled-dot-product softmax (correct base), but the design
  must expose `attention_variant in {mha, gqa, mla}` and, for the harness, MLA's latent-compression
  is the right target because the substrate is memory/evidence-ledger oriented. Formula unchanged at
  the softmax core: `attn = softmax(QK^T / sqrt(d_k)) V`; the variants change how K,V are stored.

### MoE routing - top-k is the base, but balancing evolved
- **2017 (Shazeer):** top-k softmax gate + auxiliary load-balancing loss. K=2 standard (Mixtral 8x7B).
- **Expert-choice (Google 2022):** invert it - each expert picks its top tokens. Guarantees perfect
  load balance, variable experts per token.
- **DeepSeek auxiliary-loss-free (2024, now standard):** add a per-expert **bias** to the score for
  selection only, and update the bias from observed load. Exact equations (verified from the paper):
  - Selection: `g_{i} = s_i` if `s_i + b_i in TopK({s_j + b_j}, K)` else `0`.
    The bias `b_i` affects **selection only**; the gate weight uses the original `s_i` (no bias).
  - Bias update: `b_i <- b_i + u * sign(e_i)`, where `e_i = mean_load - c_i`
    (`c_i` = tokens routed to expert i last batch, `u` = update rate, sign is +1 if underloaded).
  - Init `b_i = 0`. No interference gradients -> better performance AND balance than aux-loss.
- **Substrate choice:** adopt DeepSeek loss-free balancing. It fits the harness perfectly because the
  substrate already records per-node load as evidence; the bias update is a deterministic ledger
  operation, not a backprop gradient. This replaces the v0 harmonic-only gate prior with
  `biased_logit = gate_logit + harmonic_resonance_prior + load_balance_bias`.

### Positional - RoPE base + harmonic, with long-context scaling
- **RoPE** (standard): `theta_i = base^(-2i/d)`, base=10000 (Llama-3.1 uses base up to 500000 for 128K).
  Each dim-pair rotates by `position * theta_i`; norm-preserving.
- **NTK-aware / YaRN:** scale the base/frequencies (YaRN = NTK-by-parts + attention temperature) to
  extend context to 128K+ with ~0.1% fine-tune data. Frequency-aware: high-freq dims preserved,
  low-freq interpolated.
- **Substrate choice:** keep the golden-angle harmonic encoding as the substrate's distinctive basis
  (phyllotaxis spread is genuinely a good non-repeating phase property), but expose a standard RoPE
  `theta_i = base^(-2i/d)` path alongside it and a YaRN-style `scale` knob, so the substrate is not
  locked to one encoding. The harmonic basis becomes one selectable `position_basis in
  {rope, harmonic_golden, yarn}` rather than the only option.

### Feed-forward - GLU family, SwiGLU is the modern default
- `GeGLU(x) = GELU(xW) ⊗ (xV)` ; `SwiGLU(x) = Swish_beta(xW) ⊗ (xV)` ; `ReGLU(x) = ReLU(xW) ⊗ (xV)`.
  All use 3 weight matrices (W, V, W_out). SwiGLU/GeGLU give best perplexity; Llama uses SwiGLU,
  Gemma uses GeGLU.
- **Substrate choice:** support the GLU family via `ffn_variant in {geglu, swiglu, reglu}`; default
  SwiGLU (Swish = `x*sigmoid(beta*x)`, beta=1) to match current Llama-class models, keep GeGLU available.

### Normalization - RMSNorm pre-norm is the universal modern default
- `RMSNorm(x) = x / sqrt(mean(x^2) + eps) * g` (no mean-centering, no beta; only gain g). eps=1e-5/1e-6.
- Every major LLM since 2023 (Llama, Mistral, DeepSeek, Qwen, Gemma, Phi) uses RMSNorm + **pre-norm**:
  `y = x + sublayer(RMSNorm(x))`. 7-64% faster than LayerNorm at comparable quality.
- **Substrate choice:** v0 already uses RMSNorm pre-norm. Confirmed correct; set eps=1e-6.

### Message-passing - GATv2 (dynamic) over GAT (static)
- **GAT v1 (static):** `e_ij = LeakyReLU(a^T [W h_i || W h_j])` - attention ranking of neighbors is
  the same for every query (a proven limitation).
- **GATv2 (dynamic):** `e_ij = a^T LeakyReLU(W_l h_i + W_r h_j)` - LeakyReLU applied *after* combining,
  so ranking depends on the query. Nearly free, strictly more expressive.
- Both normalize: `alpha_ij = softmax_j(e_ij)`, aggregate `h_i' = sum_j alpha_ij * W h_j`.
- **Substrate choice:** use GATv2 (dynamic) for the Neural Bus graph-aggregation plane. The v0 doc's
  GAT-v1 formula should be upgraded to v2.

### Recurrent loop - Ouro LoopLM (parameter-shared, entropy-regularized exit)
- Ouro (2025): same transformer block applied recurrently in latent space; loop depth is a third
  scaling axis. Adaptive early-exit gates trained with an **entropy-regularized** objective; reasoning
  models run ~4 recurrent steps. 1.4B/2.6B looped match up to 12B non-looped.
- **Substrate choice:** v0's hazard/survival exit gate is the right shape. Add the entropy-regularized
  depth signal as evidence: `H(p_exit) = -sum_t p_exit(t) log p_exit(t)` recorded per loop (higher
  entropy = less decisive halting = needs more eval). Keep parameter-shared block reuse.

## 8. Open questions for review before coding

1. d_model for v0 - propose 16 (small, Fibonacci-adjacent, fast in pure Python). OK?
2. Router k - propose top-2 (Switch/GShard default is 1-2). OK?
3. Should the real forward pass replace the labels in `substrate.py` in-place, or live in the new
   kernel module and be *referenced* by the substrate ledger (preferred: modular, additive)?
4. Any formula above you want changed before implementation (e.g. GELU exact vs tanh-approx,
   pre-norm vs post-norm residual)?
5. Attention variant for v0 kernel: keep scaled-dot-product softmax core, but which KV strategy to
   expose first - GQA (simpler) or MLA latent compression (SOTA, fits the ledger)?
6. Routing: adopt DeepSeek loss-free bias balancing (recommended) vs classic aux-loss vs expert-choice?

## 9. Online sources (researched 2026-05-31)

MoE routing / load balancing:
- Auxiliary-Loss-Free Load Balancing (DeepSeek): https://arxiv.org/abs/2408.15664
- Expert-Choice Routing (Google): https://arxiv.org/abs/2202.09368
- A Visual Guide to MoE: https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-mixture-of-experts

Attention variants (MHA/GQA/MLA):
- MLA explainer (Raschka): https://sebastianraschka.com/llm-architecture-gallery/mla/
- Big LLM Architecture Comparison: https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison

Positional (RoPE/YaRN/NTK):
- YaRN paper (ICLR 2024): https://proceedings.iclr.cc/paper_files/paper/2024/file/874a4d89f2d04b4bcf9a2c19545cf040-Paper-Conference.pdf
- EleutherAI RoPE/YaRN: https://blog.eleuther.ai/yarn/

Feed-forward (GLU variants):
- GLU Variants Improve Transformer (Shazeer): https://arxiv.org/pdf/2002.05202

Normalization (RMSNorm):
- Root Mean Square Layer Normalization: https://arxiv.org/pdf/1910.07467

Message-passing (GATv2):
- How Attentive are Graph Attention Networks?: https://arxiv.org/pdf/2105.14491

Recurrent depth (Ouro LoopLM):
- Scaling Latent Reasoning via Looped Language Models: https://arxiv.org/html/2510.25741v2
- Ouro project: https://ouro-llm.github.io/
