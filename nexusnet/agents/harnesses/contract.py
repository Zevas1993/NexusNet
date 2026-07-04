"""PB-2026-06-03-094 - Harness Contract And Agent Identity Preflight (non-mutating evidence ledger).

Canon doctrine (post-book addendum PB-094): harness AVAILABILITY != harness BENEFIT. Before an agentic
pipeline block / tool action / harness-backed run is eligible to proceed, NexusNet must know:
  - which harness artifacts were REQUIRED (skill / prompt / memory pack / tool policy / eval context),
  - which were actually LOADED (activation evidence),
  - whether the trajectory FOLLOWED them (adherence evidence - "loaded but ignored" is a failure),
  - which scoped IDENTITY / delegated account is acting and whether its scopes cover the request,
  - that NO raw secrets entered the ledger.

This first implementation is strictly NON-MUTATING: it emits an allow / block / review_required
decision and read-only evidence, and may file review-gated self-improvement *candidates* (as data).
It never updates prompts, skills, routes, credentials, weights, node registries, or runtime state, and
it never stores raw secrets (only field NAMES are recorded, with a violation flag).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel

HarnessPreflightDecision = Literal["allow", "block", "review_required"]


class IdentityClaim(BaseModel):
    """Scoped, auditable acting identity. NEVER carries raw secrets/tokens - names + scopes only."""
    model_config = ConfigDict(extra="forbid")

    account_id: str
    owner_bound: bool = False              # bound to a verified owner (vs an unclaimed/claimed account)
    claimed: bool = False                  # an account that has been claimed but not owner-verified
    available_scopes: list[str] = Field(default_factory=list)


class HarnessContractRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    harness_id: str
    required_artifacts: list[str] = Field(default_factory=list)   # what the run needs to be valid
    loaded_artifacts: list[str] = Field(default_factory=list)     # what actually loaded (activation)
    trajectory_followed: list[str] = Field(default_factory=list)  # artifacts the run actually used
    identity: IdentityClaim | None = None
    requested_scopes: list[str] = Field(default_factory=list)     # scopes the run needs
    high_risk_action: bool = False                                # touches APIs/private tools/writes
    raw_secret_field_names: list[str] = Field(default_factory=list)  # NAMES only; non-empty = violation
    metadata: dict[str, Any] = Field(default_factory=dict)


class HarnessContractLedger:
    """Records preflight contracts and renders an allow/block/review decision. Non-mutating."""

    mutates_production = False

    def __init__(self, *, artifacts_dir: Path | None = None,
                 adherence_threshold: float = 1.0) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.entries_dir = (self.artifacts_dir / "agents" / "harness-contract-ledger"
                            if self.artifacts_dir else None)
        if self.entries_dir is not None:
            self.entries_dir.mkdir(parents=True, exist_ok=True)
        self.adherence_threshold = adherence_threshold
        self._records: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    # --- evaluation -------------------------------------------------------

    def preflight(self, request: HarnessContractRequest) -> dict[str, Any]:
        """Evaluate a run's harness + identity evidence and return a read-only decision record."""
        required = list(dict.fromkeys(request.required_artifacts))
        loaded = set(request.loaded_artifacts)
        followed = set(request.trajectory_followed)

        missing_artifacts = [a for a in required if a not in loaded]
        activation_ok = not missing_artifacts
        skill_load_rate = (len([a for a in required if a in loaded]) / len(required)) if required else 1.0

        # adherence is measured over the required artifacts that DID load (you can't follow what
        # never loaded); "loaded but ignored" -> adherence failure.
        loaded_required = [a for a in required if a in loaded]
        followed_required = [a for a in loaded_required if a in followed]
        adherence_rate = (len(followed_required) / len(loaded_required)) if loaded_required else 1.0
        adherence_ok = adherence_rate >= self.adherence_threshold

        # identity: required when scopes are requested or the action is high-risk.
        needs_identity = bool(request.requested_scopes) or request.high_risk_action
        identity = request.identity
        missing_scopes: list[str] = []
        identity_violations: list[str] = []
        if needs_identity:
            if identity is None:
                identity_violations.append("identity_required_but_absent")
            else:
                missing_scopes = [s for s in request.requested_scopes
                                  if s not in set(identity.available_scopes)]
                if missing_scopes:
                    identity_violations.append("requested_scopes_exceed_available")
                if not (identity.owner_bound or identity.claimed):
                    identity_violations.append("account_unclaimed")
                if request.high_risk_action and not identity.owner_bound:
                    identity_violations.append("high_risk_requires_owner_bound")
        identity_ok = not identity_violations

        raw_secret_violation = bool(request.raw_secret_field_names)

        reasons: list[str] = []
        decision: HarnessPreflightDecision = "allow"
        # hard blocks
        if raw_secret_violation:
            decision = "block"
            reasons.append("raw_secret_present_in_run_context")
        if not activation_ok:
            decision = "block"
            reasons.append(f"required_artifacts_not_loaded:{missing_artifacts}")
        if needs_identity and ("identity_required_but_absent" in identity_violations
                               or "requested_scopes_exceed_available" in identity_violations
                               or "high_risk_requires_owner_bound" in identity_violations):
            decision = "block"
            reasons.append(f"identity_scope_block:{identity_violations}")
        # review-required (not a hard block): loaded the harness but ignored it, or claimed-not-owner
        if decision != "block":
            if not adherence_ok:
                decision = "review_required"
                reasons.append(f"harness_loaded_but_not_followed:adherence={adherence_rate:.2f}")
            if needs_identity and "account_unclaimed" in identity_violations:
                decision = "review_required"
                reasons.append("identity_unclaimed_review")
        if decision == "allow":
            reasons.append("activation+adherence+identity_ok")

        record = {
            "run_id": request.run_id,
            "harness_id": request.harness_id,
            "decision": decision,
            "required_artifacts": required,
            "missing_artifacts": missing_artifacts,
            "activation_ok": activation_ok,
            "skill_load_rate": skill_load_rate,
            "adherence_rate": adherence_rate,
            "adherence_ok": adherence_ok,
            "needs_identity": needs_identity,
            "identity_ok": identity_ok,
            "missing_scopes": missing_scopes,
            "identity_violations": identity_violations,
            "raw_secret_violation": raw_secret_violation,
            "redacted_secret_field_names": list(request.raw_secret_field_names),  # names only
            "reasons": reasons,
            "mutates_production": False,
            "created_at": utcnow().isoformat() if hasattr(utcnow(), "isoformat") else str(utcnow()),
            "metadata": dict(request.metadata),
        }
        # a blocked/review run may file a review-gated self-improvement CANDIDATE (data only)
        if decision != "allow":
            record["self_improvement_candidate"] = {
                "kind": "harness_contract_gap",
                "harness_id": request.harness_id,
                "gap": reasons,
                "review_required": True,
                "shadow_only": True,
            }
        self._records.append(record)
        self._persist(record)
        return record

    # --- aggregate metrics (read-only canon/control evidence) -------------

    def metrics(self) -> dict[str, Any]:
        n = len(self._records)
        if n == 0:
            return {"runs": 0}
        allowed = sum(1 for r in self._records if r["decision"] == "allow")
        return {
            "runs": n,
            "allow": allowed,
            "block": sum(1 for r in self._records if r["decision"] == "block"),
            "review_required": sum(1 for r in self._records if r["decision"] == "review_required"),
            "loaded_pass_rate": allowed / n,
            "mean_skill_load_rate": sum(r["skill_load_rate"] for r in self._records) / n,
            "harness_adherence_failures": sum(1 for r in self._records if not r["adherence_ok"]),
            "identity_scope_failures": sum(1 for r in self._records if not r["identity_ok"]),
            "raw_secret_violations": sum(1 for r in self._records if r["raw_secret_violation"]),
        }

    def records(self) -> list[dict[str, Any]]:
        return list(self._records)

    def _persist(self, record: dict[str, Any]) -> None:
        if self.entries_dir is None:
            return
        (self.entries_dir / f"{record['run_id']}.json").write_text(
            json.dumps(record, indent=2), encoding="utf-8")
        with (self.entries_dir / "index.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"run_id": record["run_id"], "harness_id": record["harness_id"],
                                 "decision": record["decision"]}) + "\n")
