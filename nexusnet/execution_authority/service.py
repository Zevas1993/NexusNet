from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class ExecutionAuthorityService:
    """Central lease authority for risky NexusNet actions.

    Phase 0 deliberately does not execute actions. It records whether a scoped,
    expiring lease would authorize an execution attempt after approval, gateway,
    product-sweep, budget, rollback, and expiry checks all pass.
    """

    SUPPORTED_CAPABILITIES = {
        "external_package_install",
        "provider_registration",
        "hook_write",
        "pr_push",
        "pr_merge",
        "deployment",
        "autonomous_agent_execution",
        "model_download",
        "network_write",
        "file_write",
        "cloud_fallback",
        "context_graph_query",
        "context_graph_semantic_extraction",
        "factory_orchestration",
        "harness_spec_registration",
        "harness_optimization",
        "harness_safety_rule",
        "sandbox_workspace_execution",
        "deterministic_tool_boundary",
        "protocol_trust_registration",
        "telemetry_export",
        "shadow_optimizer_run",
        "paired_eval_run",
        "runtime_pack_certification",
        "serving_gateway_probe",
        "memory_hierarchy_mutation",
        "citation_research_ingestion",
        "model_growth_cycle",
    }

    ALLOW_DECISIONS = {"allow", "allowed", "approved", "passed", "grant", "granted"}

    def __init__(self, *, artifacts_dir: Path | str, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "execution-authority"
        self.events = events

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        leases = self._leases(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "lease_count": len(leases),
            "capability_counts": self._counts(leases, "capability"),
            "status_counts": self._counts(leases, "status"),
            "execution_allowed_count": len([lease for lease in leases if lease.get("execution_allowed") is True]),
            "mutation_allowed_count": len([lease for lease in leases if lease.get("mutation_allowed") is True]),
            "deny_by_default": True,
            "lease_required_for": sorted(self.SUPPORTED_CAPABILITIES),
            "latest_lease": leases[0] if leases else None,
            "items": leases,
        }

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "lease_count": payload["lease_count"],
            "capability_counts": payload["capability_counts"],
            "status_counts": payload["status_counts"],
            "execution_allowed_count": payload["execution_allowed_count"],
            "mutation_allowed_count": payload["mutation_allowed_count"],
            "deny_by_default": True,
            "latest_lease": payload["latest_lease"],
        }

    def request_lease(
        self,
        *,
        capability: str,
        scope: dict[str, Any] | None = None,
        expires_at: str | None = None,
        budget: dict[str, Any] | None = None,
        rollback_plan: dict[str, Any] | None = None,
        approval_id: str | None = None,
        approval_decision: str = "not_requested",
        gateway_decision: str = "hold",
        product_sweep_gate_ids: list[str] | None = None,
        product_sweep_decision: str = "not_evaluated",
        evidence: dict[str, Any] | None = None,
        requested_execution: bool = True,
        requested_mutation: bool = False,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        capability = str(capability)
        if capability not in self.SUPPORTED_CAPABILITIES:
            raise ValueError(f"unsupported execution authority capability: {capability}")
        lease_id = new_id("lease")
        scope_payload = scope or {}
        required = self._required_authority(
            approval_id=approval_id,
            approval_decision=approval_decision,
            gateway_decision=gateway_decision,
            product_sweep_gate_ids=product_sweep_gate_ids or [],
            product_sweep_decision=product_sweep_decision,
            rollback_plan=rollback_plan or {},
            budget=budget or {},
            expires_at=expires_at,
        )
        granted = all(value == "satisfied" for value in required.values())
        trace_ids = list(linked_trace_ids or []) or [f"trace_{lease_id}"]
        artifact_path = self.output_dir / f"{lease_id}.json"
        lease = {
            "lease_id": lease_id,
            "status": "granted" if granted else "blocked_missing_authority",
            "capability": capability,
            "scope": scope_payload,
            "scope_hash": self._scope_hash(scope_payload),
            "expires_at": expires_at,
            "budget": budget or {},
            "rollback_plan": rollback_plan or {},
            "approval_id": approval_id or "",
            "approval_decision": approval_decision,
            "gateway_decision": gateway_decision,
            "product_sweep_gate_ids": [str(item) for item in (product_sweep_gate_ids or [])],
            "product_sweep_decision": product_sweep_decision,
            "evidence": evidence or {},
            "requested_execution": bool(requested_execution),
            "requested_mutation": bool(requested_mutation),
            "required_authority": required,
            "execution_allowed": bool(granted and requested_execution),
            "mutation_allowed": bool(granted and requested_mutation),
            "policy_path": [
                {
                    "stage": "execution-authority",
                    "decision": "allow" if granted else "deny",
                    "reason": "all authority gates satisfied" if granted else "approval, gateway, product-sweep, rollback, budget, or expiry authority missing",
                }
            ],
            "approval_path": {
                "decision": approval_decision,
                "approval_id": approval_id or "",
                "human_approval_is_not_execution_authority": True,
            },
            "telemetry_trace_ids": trace_ids,
            "artifact_path": str(artifact_path),
            "created_at": utcnow().isoformat(),
        }
        self._write(lease, artifact_path)
        self._event("execution_authority.lease_requested", lease)
        return {"status_label": "STRONG ACCEPTED DIRECTION", "lease": lease}

    def evaluate(
        self,
        *,
        lease_id: str,
        capability: str,
        scope: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        lease = self._load(lease_id)
        reason = "allowed"
        execution_allowed = True
        mutation_allowed = bool(lease.get("mutation_allowed"))
        if lease.get("status") != "granted":
            reason = "lease_not_granted"
            execution_allowed = False
            mutation_allowed = False
        elif lease.get("capability") != capability:
            reason = "capability_mismatch"
            execution_allowed = False
            mutation_allowed = False
        elif self._is_expired(lease.get("expires_at")):
            reason = "lease_expired"
            execution_allowed = False
            mutation_allowed = False
        elif self._scope_hash(scope or {}) != lease.get("scope_hash"):
            reason = "scope_mismatch"
            execution_allowed = False
            mutation_allowed = False

        decision = {
            "lease_id": lease_id,
            "capability": capability,
            "scope_hash": self._scope_hash(scope or {}),
            "execution_allowed": execution_allowed,
            "mutation_allowed": mutation_allowed,
            "reason": reason,
            "policy_path": [
                {
                    "stage": "execution-authority-evaluate",
                    "decision": "allow" if execution_allowed else "deny",
                    "reason": reason,
                }
            ],
            "telemetry_trace_ids": list(linked_trace_ids or []) or lease.get("telemetry_trace_ids") or [],
            "evaluated_at": utcnow().isoformat(),
        }
        self._event("execution_authority.lease_evaluated", {**lease, "decision": decision})
        return {"status_label": "STRONG ACCEPTED DIRECTION", "decision": decision, "lease": lease}

    def _required_authority(
        self,
        *,
        approval_id: str | None,
        approval_decision: str,
        gateway_decision: str,
        product_sweep_gate_ids: list[str],
        product_sweep_decision: str,
        rollback_plan: dict[str, Any],
        budget: dict[str, Any],
        expires_at: str | None,
    ) -> dict[str, str]:
        return {
            "approval": "satisfied" if approval_id and self._is_allow(approval_decision) else "missing",
            "gateway": "satisfied" if self._is_allow(gateway_decision) else "missing",
            "product_sweep": "satisfied" if product_sweep_gate_ids and self._is_allow(product_sweep_decision) else "missing",
            "rollback": "satisfied" if rollback_plan.get("strategy") else "missing",
            "budget": "satisfied" if budget else "missing",
            "expires_at": self._expiry_state(expires_at),
        }

    def _expiry_state(self, expires_at: str | None) -> str:
        if not expires_at:
            return "missing"
        return "expired" if self._is_expired(expires_at) else "satisfied"

    def _is_expired(self, expires_at: str | None) -> bool:
        if not expires_at:
            return True
        try:
            parsed = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
        except ValueError:
            return True
        return parsed <= utcnow()

    def _is_allow(self, decision: str | None) -> bool:
        return str(decision or "").lower() in self.ALLOW_DECISIONS

    def _scope_hash(self, scope: dict[str, Any]) -> str:
        encoded = json.dumps(scope, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]

    def _load(self, lease_id: str) -> dict[str, Any]:
        path = self.output_dir / f"{lease_id}.json"
        if not path.exists():
            raise KeyError(lease_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def _leases(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        items: list[dict[str, Any]] = []
        for path in sorted(self.output_dir.glob("lease_*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(items) >= limit:
                break
        return items

    def _write(self, payload: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _event(self, event_type: str, lease: dict[str, Any]) -> None:
        if not self.events:
            return
        decision = lease.get("decision") or {}
        self.events.record(
            event_type=event_type,
            subject=f"execution_authority:{lease['lease_id']}",
            trace_ids=lease.get("telemetry_trace_ids") or decision.get("telemetry_trace_ids") or [],
            payload={
                "lease_id": lease["lease_id"],
                "capability": lease.get("capability"),
                "status": lease.get("status"),
                "execution_allowed": decision.get("execution_allowed", lease.get("execution_allowed", False)),
                "mutation_allowed": decision.get("mutation_allowed", lease.get("mutation_allowed", False)),
                "decision": "allow" if decision.get("execution_allowed", lease.get("execution_allowed", False)) else "deny",
                "artifact_path": lease.get("artifact_path"),
            },
        )

    def _counts(self, leases: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for lease in leases:
            value = str(lease.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
