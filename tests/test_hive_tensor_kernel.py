from __future__ import annotations

import math

from nexusnet.hive.kernel import HiveTensorKernel
from nexusnet.hive.kernel import tensor_ops as ops


def test_softmax_known_values_and_sums_to_one():
    p = ops.softmax([1.0, 2.0, 3.0])
    assert [round(v, 10) for v in p] == [0.0900305732, 0.2447284711, 0.6652409558]
    assert abs(sum(p) - 1.0) < 1e-12
    assert all(v >= 0.0 for v in p)


def test_softmax_is_numerically_stable():
    # Large logits must not overflow because of max-subtraction.
    p = ops.softmax([1000.0, 1001.0, 1002.0])
    assert abs(sum(p) - 1.0) < 1e-12
    assert p[2] > p[1] > p[0]


def test_matmul_exact():
    assert ops.matmul([[1, 2], [3, 4]], [[2], [1]]) == [[4.0], [10.0]]


def test_l2_normalize_unit_norm():
    v = ops.l2_normalize([3.0, 4.0])
    assert [round(x, 10) for x in v] == [0.6, 0.8]
    assert abs(ops.norm(v) - 1.0) < 1e-9


def test_rms_norm_has_unit_rms():
    v = ops.rms_norm([1.0, 2.0, 3.0])
    rms = math.sqrt(sum(x * x for x in v) / len(v))
    assert abs(rms - 1.0) < 1e-6


def test_sigmoid_and_gelu_reference_points():
    assert abs(ops.sigmoid(0.0) - 0.5) < 1e-12
    assert abs(ops.gelu(0.0) - 0.0) < 1e-12
    assert abs(ops.gelu(1.0) - 0.84119199) < 1e-6


def test_cosine_bounds_and_identity():
    assert abs(ops.cosine([1.0, 2.0], [1.0, 2.0]) - 1.0) < 1e-9
    assert abs(ops.cosine([1.0, 0.0], [0.0, 1.0])) < 1e-9
    assert -1.0 <= ops.cosine([1.0, -2.0], [3.0, 1.0]) <= 1.0


# --- harmonic / golden-ratio / sacred-geometry basis (computed, not labeled) ---

def test_phi_weights_decay_and_sum_to_phi():
    weights = [ops.phi_weight(k) for k in range(4)]
    assert [round(w, 8) for w in weights] == [0.61803399, 0.38196601, 0.23606798, 0.14589803]
    # Strictly decreasing, bounded (0,1).
    assert all(0.0 < w < 1.0 for w in weights)
    assert all(weights[i] > weights[i + 1] for i in range(len(weights) - 1))
    # Geometric series sum_{k>=1} phi^-k converges to phi.
    big_sum = sum(ops.phi_weight(k) for k in range(200))
    assert abs(big_sum - ops.PHI) < 1e-6


def test_golden_angle_rotary_preserves_norm():
    rotated = ops.rotary_pair(1.0, 0.0, position=1, k=0)
    assert abs(rotated[0] ** 2 + rotated[1] ** 2 - 1.0) < 1e-12


def test_harmonic_positional_encoding_on_unit_circle():
    pe = ops.harmonic_positional_encoding(position=3, dim=8)
    assert len(pe) == 8
    for k in range(0, 8, 2):
        assert abs(pe[k] ** 2 + pe[k + 1] ** 2 - 1.0) < 1e-9


def test_harmonic_resonance_routing_is_real_top_k_gate():
    # Three experts; harmonic resonance biases the gate but it still normalizes over top-k.
    gate = ops.harmonic_resonance_gate(
        capability_overlaps=[2, 0, 1],
        gate_logits=[0.1, 0.2, 0.05],
        top_k=2,
    )
    nonzero = [g for g in gate if g > 0.0]
    assert len(nonzero) == 2
    assert abs(sum(gate) - 1.0) < 1e-9
    assert all(g >= 0.0 for g in gate)


def test_hazard_exit_is_proper_survival_distribution_and_reports_entropy():
    result = ops.hazard_exit_schedule([0.2, 0.5, 0.9])
    total_exit = sum(result["exit_probabilities"])
    assert abs(total_exit + result["final_survival"] - 1.0) < 1e-9
    assert all(0.0 <= p <= 1.0 for p in result["exit_probabilities"])
    # Ouro-style entropy-regularized depth signal: H(p_exit) >= 0.
    assert result["exit_entropy"] >= 0.0


# --- real 2026 variants (researched): SwiGLU, RoPE, GATv2, DeepSeek loss-free balancing ---

def test_swish_and_swiglu():
    # Swish(0)=0; Swish(x)=x*sigmoid(beta*x).
    assert abs(ops.swish(0.0) - 0.0) < 1e-12
    out = ops.swiglu([0.0, 1.0], [2.0, 3.0])
    assert out[0] == 0.0  # swish(0)*2 = 0
    assert abs(out[1] - ops.swish(1.0) * 3.0) < 1e-9


def test_rope_theta_standard_base_and_norm_preserving():
    # Standard RoPE base^(-2i/d); rotation preserves norm.
    theta0 = ops.rope_theta(0, dim=8, base=10000.0)
    assert abs(theta0 - 1.0) < 1e-12  # base^0 = 1 for the first pair
    rx, ry = ops.rope_pair(1.0, 0.0, position=5, theta=theta0)
    assert abs(rx * rx + ry * ry - 1.0) < 1e-12


def test_gatv2_dynamic_attention_normalizes_per_node():
    # GATv2: e_ij = a . LeakyReLU(W_l h_i + W_r h_j); softmax over neighbors sums to 1.
    alphas = ops.gatv2_neighbor_attention(
        node=[1.0, 0.0],
        neighbors=[[0.5, 0.5], [1.0, 1.0], [-1.0, 0.2]],
    )
    assert abs(sum(alphas) - 1.0) < 1e-9
    assert all(a >= 0.0 for a in alphas)


def test_deepseek_loss_free_bias_selection_and_update():
    # Bias affects top-k SELECTION only; gate weight uses original score.
    scores = [0.3, 0.31, 0.1, 0.05]
    bias = [0.0, 0.0, 0.5, 0.0]  # expert 2 underloaded -> boosted into selection
    gate = ops.loss_free_top_k_gate(scores, bias, top_k=2)
    # Expert 2 selected via bias, but its gate weight is its ORIGINAL score (renormalized), not biased.
    assert gate[2] > 0.0
    assert gate[1] > 0.0  # highest raw score still selected
    assert gate[0] == 0.0 and gate[3] == 0.0
    assert abs(sum(gate) - 1.0) < 1e-9

    # Bias update: underloaded experts get +u, overloaded get -u.
    new_bias = ops.loss_free_bias_update([0.0, 0.0], loads=[2, 8], mean_load=5, update_rate=0.01)
    assert new_bias[0] > 0.0   # expert 0 underloaded (2 < 5) -> bias up
    assert new_bias[1] < 0.0   # expert 1 overloaded (8 > 5) -> bias down


# --- composed forward pass ---

def test_hive_tensor_kernel_runs_real_forward_pass():
    kernel = HiveTensorKernel(d_model=8, top_k=2)
    result = kernel.forward(
        token_values=[1.0, 0.5, -0.5, 1.0],
        position=2,
        expert_capability_overlaps=[2, 1, 0],
    )
    assert result["d_model"] == 8
    # Attention weights are a real probability distribution.
    assert abs(sum(result["attention"]) - 1.0) < 1e-9
    # Router selected exactly top_k experts, gate normalized.
    assert sum(1 for g in result["router_gate"] if g > 0.0) == 2
    assert abs(sum(result["router_gate"]) - 1.0) < 1e-9
    # Output vector has the right shape and a finite computed norm.
    assert len(result["output"]) == 8
    assert math.isfinite(result["output_norm"])
    # Harmonic basis is computed evidence, not a label.
    assert result["harmonic"]["golden_angle_radians"] > 0.0
    assert len(result["harmonic"]["phi_weights"]) == 3
    # Boundary preserved.
    assert result["production_mutation_allowed"] is False
    assert result["claim_boundary"] == "deterministic-symbolic-math-heuristic-not-physics-claim"
