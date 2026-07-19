from __future__ import annotations

import hashlib
import json
import math
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


class NexusGraphIntelligenceFabric:
    """NexusBrain-owned, source-grounded connected-state graph with reversible evolution."""

    PRIVACY_CLASSES = {"public", "internal", "private", "federated"}
    MUTABILITY_CLASSES = {"immutable", "governed", "ephemeral"}

    def __init__(self, *, artifacts_dir: Path | str) -> None:
        self.path = Path(artifacts_dir) / "nexusgraph" / "fabric.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save({"facts": {}, "proposals": {}, "audit": []})

    def record_fact(self, **fields: Any) -> dict[str, Any]:
        record = self._validated_fact(fields)
        payload = self._load()
        payload["facts"][record["fact_id"]] = record
        payload["audit"].append({"event": "fact.recorded", "fact_id": record["fact_id"], "digest": self._digest(record)})
        self._save(payload)
        return deepcopy(record)

    def fact(self, fact_id: str) -> dict[str, Any] | None:
        record = self._load()["facts"].get(fact_id)
        return deepcopy(record) if record else None

    def query(
        self,
        *,
        query_id: str,
        terms: list[str],
        purpose: str,
        requester: str,
        allowed_privacy_classes: list[str],
        top_k: int = 20,
    ) -> dict[str, Any]:
        allowed = set(allowed_privacy_classes) & self.PRIVACY_CLASSES
        tokens = {token for term in terms for token in self._tokens(term)}
        scored: list[tuple[float, dict[str, Any]]] = []
        for fact in self._load()["facts"].values():
            if fact["privacy_class"] not in allowed:
                continue
            haystack = set(self._tokens(" ".join(str(fact[key]) for key in ("fact_id", "subject_ref", "predicate", "object_ref"))))
            overlap = len(tokens & haystack)
            if tokens and overlap == 0:
                continue
            score = (overlap / max(len(tokens), 1)) * float(fact["confidence"])
            scored.append((score, fact))
        scored.sort(key=lambda item: (-item[0], item[1]["fact_id"]))
        hits = [{**deepcopy(fact), "query_score": round(score, 6)} for score, fact in scored[: max(1, min(top_k, 100))]]
        return {
            "passport_kind": "GraphQueryPassport",
            "query_id": self._required_ref(query_id, "query_id"),
            "purpose": self._required_ref(purpose, "purpose"),
            "requester": self._required_ref(requester, "requester"),
            "term_digests": [self._digest(term) for term in terms],
            "allowed_privacy_classes": sorted(allowed),
            "hits": hits,
            "hit_count": len(hits),
            "raw_private_content_included": False,
            "replay_digest": self._digest([query_id, terms, [item["fact_id"] for item in hits]]),
        }

    def propose_evolution(
        self,
        *,
        proposal_id: str,
        operations: list[dict[str, Any]],
        evidence_refs: list[str],
        rollback_plan: dict[str, Any],
        eval_passed: bool,
        operator_approved: bool,
    ) -> dict[str, Any]:
        blockers = []
        if not operations:
            blockers.append("operations-required")
        if not evidence_refs:
            blockers.append("evidence-required")
        if not rollback_plan:
            blockers.append("rollback-plan-required")
        if not eval_passed:
            blockers.append("eval-required")
        if not operator_approved:
            blockers.append("operator-approval-required")
        proposal = {
            "passport_kind": "GraphEvolutionPassport",
            "proposal_id": self._required_ref(proposal_id, "proposal_id"),
            "status": "ready" if not blockers else "blocked",
            "operations": deepcopy(operations),
            "evidence_refs": sorted(set(evidence_refs)),
            "rollback_plan": deepcopy(rollback_plan),
            "eval_passed": bool(eval_passed),
            "operator_approved": bool(operator_approved),
            "blockers": blockers,
            "production_mutation_allowed": not blockers,
            "applied_snapshot": {},
        }
        payload = self._load()
        payload["proposals"][proposal_id] = proposal
        payload["audit"].append({"event": "evolution.proposed", "proposal_id": proposal_id, "status": proposal["status"]})
        self._save(payload)
        return deepcopy(proposal)

    def apply_evolution(self, proposal_id: str) -> dict[str, Any]:
        payload = self._load()
        proposal = payload["proposals"].get(proposal_id)
        if not proposal or proposal["status"] != "ready":
            raise PermissionError("graph evolution is not ready for application")
        snapshot: dict[str, Any] = {}
        for operation in proposal["operations"]:
            if operation.get("operation") != "add_fact" or not isinstance(operation.get("fact"), dict):
                raise ValueError("only add_fact operations are supported")
            record = self._validated_fact(operation["fact"])
            fact_id = record["fact_id"]
            snapshot[fact_id] = deepcopy(payload["facts"].get(fact_id))
            payload["facts"][fact_id] = record
        proposal["applied_snapshot"] = snapshot
        proposal["status"] = "applied"
        payload["audit"].append({"event": "evolution.applied", "proposal_id": proposal_id})
        self._save(payload)
        return {"proposal_id": proposal_id, "status": "applied", "operation_count": len(proposal["operations"])}

    def rollback_evolution(self, proposal_id: str) -> dict[str, Any]:
        payload = self._load()
        proposal = payload["proposals"].get(proposal_id)
        if not proposal or proposal["status"] != "applied":
            raise PermissionError("graph evolution is not applied")
        for fact_id, prior in proposal.get("applied_snapshot", {}).items():
            if prior is None:
                payload["facts"].pop(fact_id, None)
            else:
                payload["facts"][fact_id] = prior
        proposal["status"] = "rolled-back"
        payload["audit"].append({"event": "evolution.rolled_back", "proposal_id": proposal_id})
        self._save(payload)
        return {"proposal_id": proposal_id, "status": "rolled-back"}

    def summary(self) -> dict[str, Any]:
        payload = self._load()
        return {
            "surface_id": "nexusgraph-intelligence-fabric",
            "authority": "NexusBrain",
            "runtime_state": "live-bound",
            "fact_count": len(payload["facts"]),
            "evolution_count": len(payload["proposals"]),
            "audit_event_count": len(payload["audit"]),
            "passport_kinds": ["GraphFactPassport", "GraphQueryPassport", "GraphEvolutionPassport"],
        }

    def _validated_fact(self, fields: dict[str, Any]) -> dict[str, Any]:
        source_refs = list(fields.get("source_refs") or [])
        if not source_refs:
            raise ValueError("GraphFactPassport requires source_refs")
        confidence = float(fields.get("confidence", 0.0))
        if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be finite and between zero and one")
        privacy_class = str(fields.get("privacy_class"))
        mutability = str(fields.get("mutability"))
        if privacy_class not in self.PRIVACY_CLASSES:
            raise ValueError(f"unsupported privacy_class: {privacy_class}")
        if mutability not in self.MUTABILITY_CLASSES:
            raise ValueError(f"unsupported mutability: {mutability}")
        return {
            "passport_kind": "GraphFactPassport",
            "fact_id": self._required_ref(fields.get("fact_id"), "fact_id"),
            "subject_ref": self._required_ref(fields.get("subject_ref"), "subject_ref"),
            "predicate": self._required_ref(fields.get("predicate"), "predicate"),
            "object_ref": self._required_ref(fields.get("object_ref"), "object_ref"),
            "source_refs": sorted({self._required_ref(item, "source_ref") for item in source_refs}),
            "confidence": confidence,
            "privacy_class": privacy_class,
            "owner": self._required_ref(fields.get("owner"), "owner"),
            "mutability": mutability,
            "verification_state": "source-grounded",
            "raw_content_included": False,
        }

    def _load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temporary, self.path)

    @staticmethod
    def _tokens(value: str) -> list[str]:
        return re.findall(r"[a-z0-9_]+", value.lower())

    @staticmethod
    def _required_ref(value: Any, name: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError(f"{name} is required")
        return text[:256]

    @staticmethod
    def _digest(value: Any) -> str:
        return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:24]
