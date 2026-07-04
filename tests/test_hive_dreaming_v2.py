from __future__ import annotations

from nexusnet.hive.dreaming import (
    world_model_signals,
    sigreg_gauss_dev,
    prediction_error,
    latent_predict,
    introspect,
    critique_veto,
    rnd_r0_coevolve,
    run_dream_episode,
)


# --- JEPA world-model + SIGReg ---

def test_prediction_error_zero_iff_match():
    assert prediction_error([1.0, 2.0], [1.0, 2.0]) == 0.0
    assert prediction_error([1.0, 2.0], [0.0, 0.0]) > 0.0


def test_sigreg_low_for_isotropic_high_for_shifted():
    # Roughly zero-mean unit-variance batch (symmetric +/-1 across dims).
    isotropic = [[1.0, 1.0], [-1.0, -1.0], [1.0, -1.0], [-1.0, 1.0]]
    shifted = [[10.0, 10.0], [10.1, 9.9], [9.9, 10.1], [10.0, 10.0]]
    assert sigreg_gauss_dev(isotropic) < sigreg_gauss_dev(shifted)


def test_latent_predict_is_norm_preserving():
    import math
    v = [0.6, 0.8, 0.0, 1.0]
    p = latent_predict(v)
    assert abs(sum(x * x for x in p) - sum(x * x for x in v)) < 1e-9


def test_world_model_signals_present():
    cur = [[0.5, 0.5], [-0.5, 0.5]]
    nxt = [[0.5, 0.5], [-0.5, 0.5]]
    wm = world_model_signals(current_latents=cur, next_latents=nxt)
    assert wm["pred_err"] >= 0.0
    assert wm["gauss_dev"] >= 0.0


# --- SAE circuit introspection ---

def test_sae_respects_sparsity_and_risk_bounds():
    act = [0.4, -0.2, 0.9, 0.1, -0.5, 0.3]
    res = introspect(activation=act, num_features=16, top_k=3, risk_profile={0: 1.0, 1: 1.0})
    assert res["sparsity"] <= 3
    assert 0.0 <= res["circuits_risk_score"] <= 1.0


def test_sae_zero_activation_fires_nothing():
    res = introspect(activation=[0.0, 0.0, 0.0, 0.0], num_features=8, top_k=3)
    assert res["circuits_used"] == []
    assert res["circuits_risk_score"] == 0.0


# --- CritiqueAO veto ---

def test_veto_passes_within_thresholds():
    v = critique_veto(pred_err=0.1, gauss_dev=0.5, circuits_risk_score=0.1)
    assert v["vetoed"] is False
    assert v["stop_signal"] is False


def test_veto_fires_on_high_risk():
    v = critique_veto(pred_err=0.1, gauss_dev=0.5, circuits_risk_score=0.95)
    assert v["vetoed"] is True
    assert "circuit_risk_exceeded" in v["reasons"]


# --- RND-R0 co-evolution ---

def test_rnd_r0_competence_monotonic_and_bounded():
    res = rnd_r0_coevolve(rounds=40, init_competence=0.1)
    comp = [h["competence"] for h in res["history"]]
    for earlier, later in zip(comp, comp[1:]):
        assert later >= earlier - 1e-12
        assert 0.0 <= later <= 1.0
    assert res["final_competence"] > 0.1


def test_rnd_r0_challenger_tracks_frontier():
    res = rnd_r0_coevolve(rounds=20, init_competence=0.2, frontier_margin=0.1)
    for h in res["history"]:
        # difficulty stays within the frontier band above competence (clamped at 1.0)
        assert h["competence"] <= h["difficulty"] + 1e-9
        assert h["difficulty"] <= min(1.0, h["competence"] + 0.1) + 1e-9


# --- dream cycle orchestrator ---

def test_dream_episode_observe_only_is_never_promotable():
    ep = run_dream_episode(
        current_latents=[[0.5, 0.5]],
        next_latents=[[0.5, 0.5]],
        capsule_activation=[0.3, 0.4, 0.1, 0.2],
        mode="collaborative",
        observe_only=True,
    )
    assert ep["promotable_candidate"] is False
    assert ep["production_mutation_allowed"] is False


def test_dream_episode_candidate_requires_no_veto_and_active_mode():
    ep = run_dream_episode(
        current_latents=[[0.5, 0.5]],
        next_latents=[[0.5, 0.5]],
        capsule_activation=[0.3, 0.4, 0.1, 0.2],
        observe_only=False,
        risk_profile={},
    )
    assert ep["promotable_candidate"] == (not ep["critique_veto"]["vetoed"])
