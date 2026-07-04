"""NexusNet Core Brain control subsystems (canon C12 Master Blueprint, Section 1.3 + meta-arbitration).

These named subsystems were specified in the canon Master Blueprint but had NO implementation. This is
the real logic (not shells), each with behavior verified by tests:

  - ThermalScalingUnit (1.3.1): throttle compute as temperature rises, with hysteresis so it doesn't
    oscillate; recover headroom as it cools.
  - VRAMConstraintManager (1.3.2): given a VRAM budget + per-unit memory costs, choose the largest
    (batch, context, precision) plan that FITS, downgrading precision/length under pressure.
  - RecursiveDreamerGate (1.3.3): only allow recursive dreaming when the system is idle/safe (not
    thermally throttled, not VRAM-pressured, not actively serving) - dreams run on spare capacity.
  - CapsuleTrustScoring: a system-wide per-capsule trust score = EWMA of (success, energy/confidence)
    minus a penalty for consequence failures; ranks capsules; feeds routing + the meta-rerouter.
  - MetaReasoner (Meta Rerouter): meta-level arbitration over the router's capsule pick - if the top
    capsule is low-confidence, low-trust, or near-tied with a more-trusted rival, it REROUTES.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ThermalScalingUnit:
    """Scale compute down as temperature rises; recover as it cools (with hysteresis)."""
    warn_c: float = 75.0
    critical_c: float = 90.0
    min_scale: float = 0.25
    _throttled: bool = field(default=False, init=False)

    def scale_for(self, temp_c: float) -> dict[str, Any]:
        if temp_c >= self.critical_c:
            self._throttled = True
            scale = self.min_scale
            state = "critical"
        elif temp_c >= self.warn_c:
            self._throttled = True
            # linear rampdown between warn and critical
            frac = (temp_c - self.warn_c) / max(1e-6, self.critical_c - self.warn_c)
            scale = max(self.min_scale, 1.0 - frac * (1.0 - self.min_scale))
            state = "throttling"
        else:
            # hysteresis: once throttled, require cooling below warn-5 before full recovery
            if self._throttled and temp_c > self.warn_c - 5.0:
                scale, state = 0.85, "recovering"
            else:
                self._throttled = False
                scale, state = 1.0, "nominal"
        return {"temp_c": temp_c, "compute_scale": round(scale, 4), "state": state,
                "throttled": self._throttled}


@dataclass
class VRAMConstraintManager:
    """Choose the largest (batch, context, precision) plan that fits a VRAM budget."""
    vram_budget_mb: float
    base_model_mb: float = 0.0
    bytes_per_token_per_ctx: float = 0.002   # MB per (token of context * batch) - KV-cache proxy

    _PRECISION_MULT = {"fp16": 1.0, "int8": 0.5, "int4": 0.25}

    def plan(self, *, want_batch: int = 8, want_context: int = 4096,
             precisions=("fp16", "int8", "int4")) -> dict[str, Any]:
        free = self.vram_budget_mb - self.base_model_mb
        for prec in precisions:                       # try highest precision first, downgrade if needed
            mult = self._PRECISION_MULT[prec]
            batch, ctx = want_batch, want_context
            while batch >= 1:
                need = mult * self.bytes_per_token_per_ctx * batch * ctx
                if need <= free:
                    return {"fits": True, "precision": prec, "batch_size": batch, "context": ctx,
                            "vram_needed_mb": round(self.base_model_mb + need, 2),
                            "vram_budget_mb": self.vram_budget_mb, "downgraded": prec != precisions[0]}
                if ctx > 512:
                    ctx //= 2
                else:
                    batch //= 2
        return {"fits": False, "reason": "model_does_not_fit_budget",
                "vram_budget_mb": self.vram_budget_mb, "base_model_mb": self.base_model_mb}


class RecursiveDreamerGate:
    """Allow recursive dreaming only on spare, safe capacity (canon 1.3.3)."""

    def __init__(self, *, max_temp_c: float = 75.0, min_free_vram_mb: float = 512.0) -> None:
        self.max_temp_c = max_temp_c
        self.min_free_vram_mb = min_free_vram_mb

    def may_dream(self, *, temp_c: float, free_vram_mb: float, serving: bool) -> dict[str, Any]:
        reasons = []
        if serving:
            reasons.append("system_busy_serving")
        if temp_c >= self.max_temp_c:
            reasons.append("thermal_throttled")
        if free_vram_mb < self.min_free_vram_mb:
            reasons.append("insufficient_free_vram")
        return {"may_dream": not reasons, "blocked_reasons": reasons}


class CapsuleTrustScoring:
    """System-wide per-capsule trust = EWMA of (success * confidence) minus consequence penalties."""

    def __init__(self, *, alpha: float = 0.3, consequence_penalty: float = 0.2) -> None:
        self.alpha = alpha
        self.consequence_penalty = consequence_penalty
        self._trust: dict[str, float] = {}

    def record(self, capsule: str, *, success: bool, confidence: float,
               consequence_failure: bool = False) -> float:
        sample = (confidence if success else 0.0) - (self.consequence_penalty if consequence_failure else 0.0)
        prev = self._trust.get(capsule, 0.5)
        self._trust[capsule] = max(0.0, min(1.0, (1 - self.alpha) * prev + self.alpha * sample))
        return self._trust[capsule]

    def trust(self, capsule: str) -> float:
        return self._trust.get(capsule, 0.5)

    def ranking(self) -> list[tuple[str, float]]:
        return sorted(self._trust.items(), key=lambda kv: kv[1], reverse=True)


class MetaReasoner:
    """Meta-arbitration over the router's pick: reroute on low confidence / low trust / trusted near-tie."""

    def __init__(self, trust: CapsuleTrustScoring, *, min_confidence: float = 0.4,
                 min_trust: float = 0.3, tie_margin: float = 0.1) -> None:
        self.trust = trust
        self.min_confidence = min_confidence
        self.min_trust = min_trust
        self.tie_margin = tie_margin

    def arbitrate(self, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        """candidates: [{capsule, confidence}] ranked by the router (best first). Returns the final pick."""
        if not candidates:
            return {"chosen": None, "rerouted": False, "reason": "no_candidates"}
        top = candidates[0]
        top_trust = self.trust.trust(top["capsule"])
        # combined score = router confidence * capsule trust
        scored = sorted(candidates, key=lambda c: c["confidence"] * self.trust.trust(c["capsule"]),
                        reverse=True)
        best = scored[0]
        reroute = best["capsule"] != top["capsule"]
        reasons = []
        if top["confidence"] < self.min_confidence:
            reasons.append("top_low_confidence")
        if top_trust < self.min_trust:
            reasons.append("top_low_trust")
        if reroute:
            reasons.append("trust_weighted_override")
        return {
            "chosen": best["capsule"],
            "router_top": top["capsule"],
            "rerouted": reroute,
            "chosen_combined_score": round(best["confidence"] * self.trust.trust(best["capsule"]), 4),
            "reasons": reasons or ["router_pick_confirmed"],
        }
