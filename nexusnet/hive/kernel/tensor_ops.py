"""Real, pure-Python neural tensor operations for the Hive Neural Substrate.

These are genuine computations (not formula labels): every function operates on real numbers
and satisfies a documented invariant covered by tests. Includes the golden-ratio / harmonic /
sacred-geometry computational basis, kept as deterministic symbolic heuristics — not physics or
consciousness claims. No dependency on numpy or any other nexusnet module.

Constants mirror nexusnet/hive/substrate.py so the kernel and the ledger agree.
"""
from __future__ import annotations

import math
from typing import Any


PHI = 1.61803398875
GOLDEN_ANGLE_RADIANS = math.radians(360 * (1 - (1 / PHI)))
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
# unison .. octave (just-intonation ratios), matching HARMONIC_INTERVALS in substrate.py
HARMONIC_RATIOS = [1.0, 6 / 5, 5 / 4, 4 / 3, 3 / 2, 2.0]
_EPS = 1e-12

Vector = list[float]
Matrix = list[list[float]]


# --- core linear algebra ---

def dot(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))


def norm(a: Vector) -> float:
    return math.sqrt(sum(x * x for x in a))


def matmul(left: Matrix, right: Matrix) -> Matrix:
    cols = len(right[0])
    inner = len(right)
    return [
        [sum(left[r][i] * right[i][c] for i in range(inner)) for c in range(cols)]
        for r in range(len(left))
    ]


def l2_normalize(a: Vector, eps: float = _EPS) -> Vector:
    scale = math.sqrt(sum(x * x for x in a) + eps)
    return [x / scale for x in a]


def rms_norm(a: Vector, gain: float = 1.0, eps: float = _EPS) -> Vector:
    ms = sum(x * x for x in a) / len(a)
    scale = math.sqrt(ms + eps)
    return [(x / scale) * gain for x in a]


def cosine(a: Vector, b: Vector, eps: float = _EPS) -> float:
    return dot(a, b) / (norm(a) * norm(b) + eps)


# --- nonlinearities ---

def softmax(values: Vector) -> Vector:
    # Numerically stable: subtract max before exp.
    top = max(values)
    exps = [math.exp(v - top) for v in values]
    total = sum(exps)
    return [e / total for e in exps]


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def gelu(x: float) -> float:
    # tanh approximation of GELU.
    return 0.5 * x * (1.0 + math.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * x ** 3)))


def leaky_relu(x: float, slope: float = 0.01) -> float:
    return x if x > 0 else slope * x


def geglu(gate: Vector, value: Vector) -> Vector:
    return [gelu(g) * v for g, v in zip(gate, value)]


def swish(x: float, beta: float = 1.0) -> float:
    return x * sigmoid(beta * x)


def swiglu(gate: Vector, value: Vector, beta: float = 1.0) -> Vector:
    # SwiGLU(x) = Swish_beta(xW) (x) (xV). Modern default FFN (Llama-class).
    return [swish(g, beta) * v for g, v in zip(gate, value)]


def reglu(gate: Vector, value: Vector) -> Vector:
    return [max(0.0, g) * v for g, v in zip(gate, value)]


# --- losses (scalars; no weight backprop in v0) ---

def mse(predicted: Vector, target: Vector) -> float:
    return sum((p - t) ** 2 for p, t in zip(predicted, target)) / len(predicted)


def cross_entropy(probs: Vector, target: Vector, eps: float = _EPS) -> float:
    return -sum(t * math.log(p + eps) for p, t in zip(probs, target))


# --- golden-ratio / harmonic / sacred-geometry basis (computed heuristics) ---

def phi_weight(index: int) -> float:
    """phi^-(index+1): strictly decreasing in (0,1); sum over k>=0 converges to PHI."""
    return PHI ** -(index + 1)


def harmonic_ratio(index: int) -> float:
    return HARMONIC_RATIOS[index % len(HARMONIC_RATIOS)]


def rotary_pair(x: float, y: float, *, position: int, k: int) -> tuple[float, float]:
    """Golden-angle rotation of a 2D pair; norm-preserving (phyllotaxis phase spread)."""
    theta = position * GOLDEN_ANGLE_RADIANS * (PHI ** -k)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    return (x * cos_t - y * sin_t, x * sin_t + y * cos_t)


def rope_theta(pair_index: int, *, dim: int, base: float = 10000.0, scale: float = 1.0) -> float:
    """Standard RoPE frequency theta_i = base^(-2i/d). `scale` enables NTK/YaRN-style extension."""
    return scale * (base ** (-2.0 * pair_index / dim))


def rope_pair(x: float, y: float, *, position: int, theta: float) -> tuple[float, float]:
    """Standard RoPE rotation of a 2D pair by position*theta; norm-preserving."""
    angle = position * theta
    cos_t, sin_t = math.cos(angle), math.sin(angle)
    return (x * cos_t - y * sin_t, x * sin_t + y * cos_t)


def gatv2_neighbor_attention(
    *,
    node: Vector,
    neighbors: list[Vector],
    w_left: float = 1.0,
    w_right: float = 1.0,
    leaky_slope: float = 0.2,
) -> Vector:
    """GATv2 dynamic attention: e_ij = sum(LeakyReLU(W_l h_i + W_r h_j)); alpha = softmax_j(e_ij).

    LeakyReLU is applied AFTER combining node and neighbor features (the v2 fix that makes the
    attention ranking depend on the query node), then normalized over neighbors.
    """
    scores = []
    for neighbor in neighbors:
        combined = [w_left * hi + w_right * hj for hi, hj in zip(node, neighbor)]
        scores.append(sum(leaky_relu(c, leaky_slope) for c in combined))
    return softmax(scores)


def loss_free_top_k_gate(scores: Vector, bias: Vector, top_k: int) -> Vector:
    """DeepSeek auxiliary-loss-free balancing.

    Selection uses biased scores (score + bias); the returned gate weight uses the ORIGINAL score,
    renormalized over the selected set. The bias steers load balance without entering the gate value
    (no interference gradients).
        g_i = s_i if (s_i + b_i) in TopK({s_j + b_j}) else 0, then renormalize over selected.
    """
    biased = [s + b for s, b in zip(scores, bias)]
    ranked = sorted(range(len(biased)), key=lambda i: biased[i], reverse=True)
    keep = set(ranked[: max(1, min(top_k, len(scores)))])
    kept_total = sum(scores[i] for i in keep) or 1.0
    return [scores[i] / kept_total if i in keep else 0.0 for i in range(len(scores))]


def loss_free_bias_update(bias: Vector, *, loads: list[int], mean_load: float, update_rate: float) -> Vector:
    """DeepSeek bias update: b_i <- b_i + u * sign(mean_load - load_i).

    Underloaded experts (load < mean) get a positive nudge; overloaded get negative. Deterministic
    ledger operation, not a backprop gradient.
    """
    updated = []
    for b, load in zip(bias, loads):
        error = mean_load - load
        sign = 1.0 if error > 0 else (-1.0 if error < 0 else 0.0)
        updated.append(b + update_rate * sign)
    return updated


def harmonic_positional_encoding(*, position: int, dim: int, base: float = 1.0) -> Vector:
    """Harmonic-series positional encoding; each (sin,cos) pair lies on the unit circle."""
    pe: Vector = []
    for pair in range(dim // 2):
        partial = harmonic_ratio(pair) ** -(pair // len(HARMONIC_RATIOS) + 1)
        freq = base * partial
        pe.append(math.sin(position * freq))
        pe.append(math.cos(position * freq))
    if dim % 2:
        pe.append(0.0)
    return pe


def top_k_gate(gate_logits: Vector, top_k: int) -> Vector:
    """Softmax over logits, keep top-k, renormalize over the kept set."""
    probs = softmax(gate_logits)
    ranked = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)
    keep = set(ranked[: max(1, min(top_k, len(probs)))])
    kept_total = sum(probs[i] for i in keep) or 1.0
    return [probs[i] / kept_total if i in keep else 0.0 for i in range(len(probs))]


def harmonic_resonance_gate(*, capability_overlaps: list[int], gate_logits: Vector, top_k: int) -> Vector:
    """Top-k gated softmax with a harmonic/phi resonance prior added to each logit.

    resonance_e = (capability_overlap_e + 1) * harmonic_ratio(e) * phi_weight(rank_e)
    biased_logit_e = gate_logit_e + log(resonance_e)
    The harmonic resonance is a computed prior on the gate; the decision is still the real
    top-k softmax (which the test asserts sums to 1).
    """
    ranked = sorted(range(len(gate_logits)), key=lambda i: gate_logits[i], reverse=True)
    rank_of = {idx: rank for rank, idx in enumerate(ranked)}
    biased = []
    for e, logit in enumerate(gate_logits):
        resonance = (capability_overlaps[e] + 1) * harmonic_ratio(e) * phi_weight(rank_of[e])
        biased.append(logit + math.log(resonance))
    return top_k_gate(biased, top_k)


def hazard_exit_schedule(hazards: Vector) -> dict[str, Any]:
    """Survival/CDF exit gate over recurrent loops.

    exit_prob(t) = hazard_t * survival_{t-1}; survival_t = prod_{j<=t}(1 - hazard_j).
    Returns a proper distribution: sum(exit_probabilities) + final_survival == 1.
    """
    survival = 1.0
    exit_probs: Vector = []
    for hazard in hazards:
        h = max(0.0, min(1.0, hazard))
        exit_probs.append(h * survival)
        survival *= (1.0 - h)
    # Ouro-style entropy-regularized depth signal over the full distribution (exits + final survival).
    distribution = exit_probs + [survival]
    entropy = -sum(p * math.log(p + _EPS) for p in distribution if p > 0.0)
    return {"exit_probabilities": exit_probs, "final_survival": survival, "exit_entropy": entropy}
