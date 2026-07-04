"""Close the loop: recursive dreaming -> GATED training feedback (canon PB-034 / Aspect 6 / addendum C-D).

Canon contract honored here:
  - EVIDENCE-CONDITIONED: the dream reads the model's OWN failures (highest-loss windows) before
    proposing - it does not dream from nothing (PB-034: dreams consume failed candidate refs).
  - dreamer HIGH-temperature (a JEPA world-model over the failure latents), critic LOW-temperature
    (the CritiqueAO veto on pred_err / gauss_dev) - both conditioned by substrate evidence.
  - dreams are CANDIDATES gated by the veto AND a held-out eval; a dream-update is applied to a SHADOW
    copy first and KEPT only if held-out loss improves - otherwise rolled back (rollback-restorable).
  - this updates the TRAINABLE womb (legitimate self-training), never a production/shadow-evidence layer.

This makes Recursive Neural Dreaming actually recursive: failures -> dream -> gated weight update.
"""
from __future__ import annotations

import copy
from typing import Any

import torch

from .lm import NexusNetLM
from .birth import train_language_model
from .eval_gates import measure_language_model
from .dreaming_jepa import JEPAWorldModel, train_world_model, sigreg


@torch.no_grad()
def _per_window_loss(model: NexusNetLM, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    was = model.training
    model.eval()
    logits = model(x)                                          # (N, T, V)
    N, T, V = logits.shape
    ce = torch.nn.functional.cross_entropy(
        logits.reshape(-1, V), y.reshape(-1), reduction="none").reshape(N, T).mean(dim=1)
    if was:
        model.train()
    return ce                                                 # (N,) per-window loss


def recursive_dream_train(
    model: NexusNetLM,
    x_tr: torch.Tensor,
    y_tr: torch.Tensor,
    x_val: torch.Tensor,
    y_val: torch.Tensor,
    *,
    failure_fraction: float = 0.25,
    dream_steps: int = 30,
    replay_factor: int = 2,
    shadow_epochs: int = 12,
    lr: float = 2e-3,
    veto_pred_err: float = 0.5,
    veto_gauss_dev: float = 6.0,
    seed: int = 0,
) -> dict[str, Any]:
    """One recursive-dream training episode. Returns a decision record (applied / vetoed / rolled-back)."""
    torch.manual_seed(seed)
    baseline = measure_language_model(model, x_val, y_val)

    # 1) EVIDENCE-CONDITIONING: the model's own failures = highest-loss training windows.
    pls = _per_window_loss(model, x_tr, y_tr)
    k = max(1, int(failure_fraction * x_tr.shape[0]))
    fail_idx = torch.topk(pls, k).indices

    # 2) DREAMER (high-temp): a JEPA world-model over the FAILURE latents.
    with torch.no_grad():
        fail_latents = model.embed(x_tr[fail_idx]).detach()
    jepa = JEPAWorldModel(model.d_model, ema=0.9)
    dream = train_world_model(jepa, fail_latents, steps=dream_steps, lr=3e-3)
    reg = sigreg(fail_latents)

    # 3) CRITIC (low-temp) veto: incoherent dream (high pred_err) or anomalous latents (high gauss_dev).
    gauss_dev = float(reg["gauss_dev"])
    vetoed = (dream["final_pred_err"] > veto_pred_err) or (gauss_dev > veto_gauss_dev)
    if vetoed:
        return {
            "applied": False, "vetoed": True,
            "reason": "critique_veto", "baseline": baseline,
            "dream": {"final_pred_err": dream["final_pred_err"], "gauss_dev": gauss_dev},
            "failure_count": int(k), "rolled_back": False,
            "production_mutation_allowed": False,
        }

    # 4) DREAM-REPLAY on a SHADOW copy: oversample the failure set (consolidate what was hard).
    shadow = copy.deepcopy(model)
    x_rep = torch.cat([x_tr, x_tr[fail_idx].repeat(replay_factor, 1)], dim=0)
    y_rep = torch.cat([y_tr, y_tr[fail_idx].repeat(replay_factor, 1)], dim=0)
    train_language_model(shadow, x_rep, y_rep, epochs=shadow_epochs, lr=lr,
                         val_x=x_val, val_y=y_val)
    after = measure_language_model(shadow, x_val, y_val)

    # 5) EVAL GATE: keep the dream-update only if held-out loss improved; else roll back.
    improved = after["val_loss"] < baseline["val_loss"] - 1e-4
    if improved:
        model.load_state_dict(shadow.state_dict())
    return {
        "applied": bool(improved),
        "vetoed": False,
        "rolled_back": not improved,
        "baseline": baseline,
        "after": after,
        "val_loss_delta": after["val_loss"] - baseline["val_loss"],
        "failure_count": int(k),
        "dream": {"final_pred_err": dream["final_pred_err"], "gauss_dev": gauss_dev,
                  "world_model_learned": dream["world_model_learned"]},
        "production_mutation_allowed": False,
        "claim_boundary": "gated-self-training-of-the-womb-not-production-mutation",
    }


def recursive_dream_cycles(model: NexusNetLM, x_tr, y_tr, x_val, y_val, *, cycles: int = 3, **kw
                           ) -> dict[str, Any]:
    """Run several recursive-dream episodes; report how many were kept vs vetoed vs rolled back."""
    records = []
    for c in range(cycles):
        rec = recursive_dream_train(model, x_tr, y_tr, x_val, y_val, seed=kw.pop("seed", 0) + c, **kw)
        records.append(rec)
    return {
        "cycles": cycles,
        "applied": sum(1 for r in records if r["applied"]),
        "vetoed": sum(1 for r in records if r["vetoed"]),
        "rolled_back": sum(1 for r in records if r.get("rolled_back")),
        "records": records,
        "final_val_loss": measure_language_model(model, x_val, y_val)["val_loss"],
    }
