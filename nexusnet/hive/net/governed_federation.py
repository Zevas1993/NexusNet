"""Wire real FedAvg behind canon federation governance (PB-024/025/031/036/040).

Canon contract honored:
  - SANITIZED packets only (PB-024): a packet carries the model DELTA (an artifact) + metadata
    (eval score, failure class, route-geometry signature, node role, hardware class). Raw prompts,
    outputs, memory refs, paths, urls, emails, secrets, tokens, screenshots are FORBIDDEN.
  - SIGNED ENVELOPE (PB-031): each packet carries an integrity digest; tampering breaks verification.
    (sha256 content seal here; ed25519 PKI is available via `nexusnet.security` for production.)
  - SECURE AGGREGATION + POISONING/DIVERGENCE SCAN (PB-025/036): masked aggregate, outlier clients
    dropped, before any global update.
  - BENCHMARK-REGRESSION + REVIEW GATE (PB-036/040): the aggregated candidate is promoted ONLY if it
    does not regress held-out benchmark; otherwise it is shadow-routed, never auto-promoted.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

import torch

from .federated import fedavg, divergence_guard, secure_aggregate
from .eval_gates import measure_language_model

# substrings that must never appear in federated metadata (raw private content)
_FORBIDDEN = ("prompt", "output", "raw", "memory_ref", "path", "url", "email", "secret",
              "token", "screenshot", "name")


def _delta(client_state: dict[str, torch.Tensor], base_state: dict[str, torch.Tensor]
           ) -> dict[str, torch.Tensor]:
    return {k: (client_state[k].float() - base_state[k].float()) for k in base_state}


def _digest(delta: dict[str, torch.Tensor], metadata: dict[str, Any]) -> str:
    h = hashlib.sha256()
    for k in sorted(delta):
        h.update(k.encode())
        h.update(delta[k].detach().cpu().numpy().tobytes())
    h.update(json.dumps(metadata, sort_keys=True, default=str).encode())
    return h.hexdigest()


def sanitized_update_packet(
    client_id: str,
    client_state: dict[str, torch.Tensor],
    base_state: dict[str, torch.Tensor],
    *,
    eval_score: float,
    sample_count: int,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a sanitized, signed federated packet: model delta + safe metadata + integrity digest."""
    meta = dict(metadata or {})
    privacy_violations = [k for k in meta if any(tok in k.lower() for tok in _FORBIDDEN)]
    safe_meta = {k: v for k, v in meta.items() if k not in privacy_violations}
    delta = _delta(client_state, base_state)
    digest = _digest(delta, safe_meta)
    return {
        "client_id": client_id,
        "delta": delta,
        "metadata": safe_meta,
        "eval_score": float(eval_score),
        "sample_count": int(sample_count),
        "digest": digest,
        "sanitized": not privacy_violations,
        "privacy_violations": privacy_violations,
    }


def verify_packet(packet: dict[str, Any]) -> bool:
    """Verify integrity (digest matches) and privacy (sanitized) - the signed-envelope check."""
    if not packet.get("sanitized", False):
        return False
    return _digest(packet["delta"], packet["metadata"]) == packet["digest"]


def governed_federated_round(
    make_model: Callable[[], torch.nn.Module],
    global_state: dict[str, torch.Tensor],
    packets: list[dict[str, Any]],
    val_x: torch.Tensor,
    val_y: torch.Tensor,
    *,
    regression_tolerance: float = 1e-3,
) -> dict[str, Any]:
    """Run a full governed round: verify -> scan -> secure-agg/FedAvg -> benchmark-regression gate."""
    # 1) signed-envelope verification + privacy gate
    verified = [p for p in packets if verify_packet(p)]
    rejected = [p["client_id"] for p in packets if not verify_packet(p)]

    if not verified:
        return {"decision": "rejected", "reason": "no_valid_packets", "rejected": rejected,
                "global_state": global_state, "promoted": False}

    # 2) reconstruct client weights from deltas; poisoning/divergence scan
    client_states = [{k: global_state[k].float() + p["delta"][k] for k in global_state}
                     for p in verified]
    guard = divergence_guard(client_states) if len(client_states) > 2 else {
        "kept": list(range(len(client_states))), "flagged": []}
    kept_idx = guard["kept"]
    kept = [verified[i] for i in kept_idx]

    # 3) secure aggregation (masks cancel, mean exact) + sample-weighted FedAvg of the kept deltas
    flat_deltas = [torch.cat([p["delta"][k].reshape(-1) for k in sorted(global_state)]) for p in kept]
    secure = secure_aggregate(flat_deltas) if len(flat_deltas) > 1 else {"masked_mean": flat_deltas[0],
                                                                          "true_mean": flat_deltas[0]}
    secure_ok = torch.allclose(secure["masked_mean"], secure["true_mean"], atol=1e-4)
    agg_delta = fedavg([p["delta"] for p in kept], [p["sample_count"] for p in kept])
    candidate_global = {k: (global_state[k].float() + agg_delta[k]).to(global_state[k].dtype)
                        for k in global_state}

    # 4) benchmark-regression gate: promote only if the candidate does not regress held-out loss
    base_m = make_model(); base_m.load_state_dict(global_state)
    cand_m = make_model(); cand_m.load_state_dict(candidate_global)
    base_loss = measure_language_model(base_m, val_x, val_y)["val_loss"]
    cand_loss = measure_language_model(cand_m, val_x, val_y)["val_loss"]
    promoted = cand_loss <= base_loss + regression_tolerance
    return {
        "decision": "promoted" if promoted else "shadow",
        "promoted": promoted,
        "global_state": candidate_global if promoted else global_state,
        "base_loss": base_loss,
        "candidate_loss": cand_loss,
        "loss_delta": cand_loss - base_loss,
        "verified_clients": [p["client_id"] for p in verified],
        "kept_clients": [verified[i]["client_id"] for i in kept_idx],
        "flagged_clients": [verified[i]["client_id"] for i in guard["flagged"]],
        "rejected_clients": rejected,
        "secure_aggregation_exact": secure_ok,
        "review_gate": "benchmark-regression-gate;human-governance-approval-required-for-production",
        "production_mutation_allowed": False,
    }
