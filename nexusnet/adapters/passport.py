"""PB-2026-06-03-096 - Persistent Adapter State Fabric (governed PEFT adapter passports + registry).

Canon doctrine: PEFT adapters are governed PERSISTENT STATE for AOs / experts / Mini-NexusNets /
operators / task families - NOT uncontrolled per-user fine-tuning. Every adapter needs identity,
revision, source lineage, allowed base models, eval suite, route constraints, residency, and rollback
metadata before use. The registry may ENUMERATE candidates WITHOUT loading weights; routing stays
SHADOW-ONLY until compatibility / eval / privacy / rollback / source-rights checks pass. Raw adapter
weights must never appear in logs, federated packets, or ordinary canon evidence.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AdapterPassport(BaseModel):
    """Governance metadata for one adapter. Carries NO weights - identity + provenance + gates only."""
    model_config = ConfigDict(extra="forbid")

    adapter_id: str
    revision: str
    source_lineage: list[str] = Field(default_factory=list)
    allowed_base_models: list[str] = Field(default_factory=list)
    eval_suite_refs: list[str] = Field(default_factory=list)
    eval_delta: float = 0.0                      # held-out delta vs base (>= 0 to be promotable)
    route_constraints: list[str] = Field(default_factory=list)   # task families it may serve
    residency: Literal["local", "regional", "cloud"] = "local"
    privacy_class: Literal["public", "internal", "private"] = "internal"
    rights_cleared: bool = False
    rollback_target: str = ""                    # adapter_id or "base" to roll back to


class AdapterRouteDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adapter_id: str
    base_model: str
    decision: Literal["shadow_route", "block"]
    reasons: list[str] = Field(default_factory=list)
    shadow_only: bool = True


class AdapterRegistry:
    """Enumerate adapter passports (no weight loading) and gate shadow routing. Non-mutating."""

    mutates_production = False

    def __init__(self) -> None:
        self._passports: dict[str, AdapterPassport] = {}
        self._active: dict[str, str] = {}        # base_model -> currently shadow-routed adapter_id
        self._history: dict[str, list[str]] = {}

    def register(self, passport: AdapterPassport) -> None:
        """Enumerate a candidate adapter by metadata only (weights are never loaded here)."""
        self._passports[passport.adapter_id] = passport

    def candidates(self, *, base_model: str | None = None) -> list[str]:
        if base_model is None:
            return sorted(self._passports)
        return sorted(a for a, p in self._passports.items() if base_model in p.allowed_base_models)

    def gate(self, adapter_id: str, base_model: str, *, allowed_residencies=("local", "regional")
             ) -> AdapterRouteDecision:
        """Decide whether an adapter may be SHADOW-routed on a base model (never production-promoted)."""
        p = self._passports.get(adapter_id)
        reasons: list[str] = []
        if p is None:
            return AdapterRouteDecision(adapter_id=adapter_id, base_model=base_model,
                                        decision="block", reasons=["unknown_adapter"])
        if base_model not in p.allowed_base_models:
            reasons.append("base_model_incompatible")
        if not p.rights_cleared:
            reasons.append("source_rights_not_cleared")
        if p.privacy_class == "private":
            reasons.append("private_adapter")
        if p.eval_delta < 0:
            reasons.append("eval_regression")
        if not p.eval_suite_refs:
            reasons.append("no_eval_evidence")
        if p.residency not in allowed_residencies:
            reasons.append(f"residency_disallowed:{p.residency}")
        if not p.rollback_target:
            reasons.append("no_rollback_target")
        decision = "block" if reasons else "shadow_route"
        return AdapterRouteDecision(adapter_id=adapter_id, base_model=base_model,
                                    decision=decision, reasons=reasons, shadow_only=True)

    def shadow_attach(self, adapter_id: str, base_model: str) -> AdapterRouteDecision:
        """Record a shadow-route selection (after a passing gate). Previous selection is kept for rollback."""
        decision = self.gate(adapter_id, base_model)
        if decision.decision == "shadow_route":
            prev = self._active.get(base_model)
            self._history.setdefault(base_model, [])
            if prev:
                self._history[base_model].append(prev)
            self._active[base_model] = adapter_id
        return decision

    def rollback(self, base_model: str) -> str:
        """Roll back to the previous adapter (or 'base' if none) - rollback is always restorable."""
        history = self._history.get(base_model, [])
        target = history.pop() if history else "base"
        if target == "base":
            self._active.pop(base_model, None)
        else:
            self._active[base_model] = target
        return target

    def active(self, base_model: str) -> str:
        return self._active.get(base_model, "base")
