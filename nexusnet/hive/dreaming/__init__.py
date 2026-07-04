"""Recursive Neural Dreaming v2 (canon addendum C + C38 RND-R0). Additive to the legacy dream cycle.

JEPA world-model sidecar + SIGReg isotropy, SAE sparse-circuit introspection + circuits_risk_score,
CritiqueAO veto, observe-only-first dream cycle, and RND-R0 challenger/solver co-evolution. All
deterministic, shadow-only - dreams become promotion candidates only through the veto + gates.
"""
from __future__ import annotations

from .world_model import world_model_signals, latent_predict, sigreg_gauss_dev, prediction_error
from .sae import introspect, encode_sparse, circuits_risk_score
from .critique_veto import critique_veto
from .rnd_r0 import rnd_r0_coevolve
from .dream_cycle import run_dream_episode, DREAM_MODES

__all__ = [
    "world_model_signals",
    "latent_predict",
    "sigreg_gauss_dev",
    "prediction_error",
    "introspect",
    "encode_sparse",
    "circuits_risk_score",
    "critique_veto",
    "rnd_r0_coevolve",
    "run_dream_episode",
    "DREAM_MODES",
]
