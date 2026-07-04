"""PB-2026-06-03-097 - Trace-Optimized Secure Self-Evolving Agent Runtime (extends PB-094).

Canon doctrine (Hermes/NemoClaw pattern, vendor-neutral): a secure self-evolving runtime = model +
harness + POLICY-ENFORCED runtime. Credentials are brokered OUTSIDE the agent, network access is
ALLOWLISTED, traces are exportable + REDACTED, and learned state survives rebuilds via redacted
snapshots. Trace analysis may PROPOSE skill/memory/prompt/policy candidates, but they are
review-required and shadow-only. Never relies on prompt-only security; never stores raw credentials.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .contract import HarnessContractLedger, HarnessContractRequest


class CredentialBroker:
    """Broker credentials OUTSIDE the agent: issues scoped handles (ref + scopes), never raw secrets."""

    def __init__(self) -> None:
        self._issued: dict[str, dict[str, Any]] = {}

    def issue(self, account_id: str, scopes: list[str]) -> dict[str, Any]:
        handle = f"cred::{account_id}::{len(self._issued)}"
        record = {"handle": handle, "account_id": account_id, "scopes": list(scopes),
                  "carries_raw_secret": False}     # by construction: only a handle, no secret value
        self._issued[handle] = record
        return record

    def resolve_scopes(self, handle: str) -> list[str]:
        return list(self._issued.get(handle, {}).get("scopes", []))


class NetworkAllowlist:
    """Allowlisted network egress - default deny."""

    def __init__(self, allowed_hosts: list[str]) -> None:
        self.allowed_hosts = set(allowed_hosts)

    def check(self, host: str) -> dict[str, Any]:
        allowed = host in self.allowed_hosts
        return {"host": host, "allowed": allowed, "reason": "allowlisted" if allowed else "default_deny"}


_SECRET_TAGS = ("secret", "token", "password", "api_key", "credential")


def redact_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    """Strip secret-tagged fields from a learned-state snapshot (names kept, values dropped)."""
    redacted: dict[str, Any] = {}
    removed: list[str] = []
    for k, v in state.items():
        if any(tag in k.lower() for tag in _SECRET_TAGS):
            removed.append(k)
            continue
        redacted[k] = v
    return {"snapshot": redacted, "redacted_fields": removed}


def restore_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Restore from a redacted snapshot; proof = restored keys carry no secret-tagged field."""
    restored = dict(snapshot.get("snapshot", {}))
    clean = not any(any(tag in k.lower() for tag in _SECRET_TAGS) for k in restored)
    return {"restored": restored, "secret_free": clean}


class TraceCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["skill", "memory", "prompt", "policy"]
    summary: str
    review_required: bool = True
    shadow_only: bool = True


def propose_candidates_from_trace(trace: list[dict[str, Any]]) -> list[TraceCandidate]:
    """Analyze a redacted trace and PROPOSE improvement candidates (review-required, shadow-only)."""
    candidates: list[TraceCandidate] = []
    repeated_tools: dict[str, int] = {}
    for step in trace:
        if step.get("type") == "tool_call":
            repeated_tools[step.get("tool", "?")] = repeated_tools.get(step.get("tool", "?"), 0) + 1
        if step.get("type") == "error":
            candidates.append(TraceCandidate(kind="policy",
                              summary=f"add guard for error: {step.get('error', '')[:60]}"))
        if step.get("type") == "retrieval_miss":
            candidates.append(TraceCandidate(kind="memory",
                              summary="add memory pack for missed retrieval"))
    for tool, n in repeated_tools.items():
        if n >= 3:
            candidates.append(TraceCandidate(kind="skill",
                              summary=f"encapsulate repeated tool '{tool}' ({n}x) into a skill"))
    return candidates


class SecureRuntimeContract:
    """Bundle PB-094 preflight + policy-as-code enforcement + trace candidates + snapshot proof."""

    mutates_production = False

    def __init__(self, *, allowlist: NetworkAllowlist | None = None) -> None:
        self.ledger = HarnessContractLedger()
        self.broker = CredentialBroker()
        self.allowlist = allowlist or NetworkAllowlist([])

    def evaluate(self, request: HarnessContractRequest, *, egress_hosts: list[str] | None = None,
                 trace: list[dict[str, Any]] | None = None,
                 learned_state: dict[str, Any] | None = None) -> dict[str, Any]:
        preflight = self.ledger.preflight(request)
        egress = [self.allowlist.check(h) for h in (egress_hosts or [])]
        egress_ok = all(e["allowed"] for e in egress)
        policy_pass = (preflight["decision"] != "block") and egress_ok and not preflight["raw_secret_violation"]
        candidates = [c.model_dump() for c in propose_candidates_from_trace(trace or [])]
        snap = redact_snapshot(learned_state or {})
        restored = restore_snapshot(snap)
        return {
            "preflight": preflight,
            "egress_checks": egress,
            "egress_ok": egress_ok,
            "policy_pass": policy_pass,
            "improvement_candidates": candidates,   # review-required, shadow-only
            "snapshot": snap,
            "restore_secret_free": restored["secret_free"],
            "mutates_production": False,
        }
