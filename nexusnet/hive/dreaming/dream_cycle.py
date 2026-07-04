"""Recursive Neural Dreaming v2 cycle orchestrator (canon addendum C/D).

Composes the v2 pieces into one dream episode artifact: JEPA world-model signals (pred_err,
gauss_dev), SAE circuit introspection (circuits_used, circuits_risk_score), and the CritiqueAO veto.
Supports dream modes (individual/collaborative/competitive) and runs OBSERVE-ONLY first - a dream is
never promoted from the cycle itself; the veto + downstream gates decide. The legacy dream cycle is
preserved elsewhere; this is additive. Deterministic, shadow-only.
"""
from __future__ import annotations

from typing import Any

from .world_model import world_model_signals
from .sae import introspect
from .critique_veto import critique_veto

Vector = list[float]
DREAM_MODES = ("individual", "collaborative", "competitive")


def run_dream_episode(
    *,
    current_latents: list[Vector],
    next_latents: list[Vector],
    capsule_activation: Vector,
    mode: str = "individual",
    observe_only: bool = True,
    risk_profile: dict[int, float] | None = None,
) -> dict[str, Any]:
    if mode not in DREAM_MODES:
        raise ValueError(f"unknown dream mode {mode!r}; allowed {DREAM_MODES}")
    wm = world_model_signals(current_latents=current_latents, next_latents=next_latents)
    sae = introspect(activation=capsule_activation, risk_profile=risk_profile)
    veto = critique_veto(
        pred_err=wm["pred_err"],
        gauss_dev=wm["gauss_dev"],
        circuits_risk_score=sae["circuits_risk_score"],
    )
    # A dream can only be a promotion CANDIDATE when not observe-only and not vetoed.
    promotable_candidate = (not observe_only) and (not veto["vetoed"])
    return {
        "surface_id": "rnd-v2-dream-episode",
        "mode": mode,
        "observe_only": observe_only,
        "world_model": {"pred_err": wm["pred_err"], "gauss_dev": wm["gauss_dev"]},
        "circuits_used": sae["circuits_used"],
        "circuits_risk_score": sae["circuits_risk_score"],
        "critique_veto": veto,
        "promotable_candidate": promotable_candidate,
        "production_mutation_allowed": False,
        "native_weight_training": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
