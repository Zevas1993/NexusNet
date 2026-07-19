from __future__ import annotations

import base64
import fnmatch
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow
from pydantic import ValidationError

from .contracts import AuthorityDecisionRecord, EffectType


WRITE_EFFECTS = {"filesystem_write", "shell", "desktop", "browser", "model_update", "memory_update"}


class AuthorityIntegritySpine:
    def __init__(self, *, artifacts_dir: Path | str | None = None, signing_key: bytes | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.decisions_dir = self.artifacts_dir / "authority" / "decisions" if self.artifacts_dir else None
        if self.decisions_dir is not None:
            self.decisions_dir.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []
        self._signing_key = signing_key or self._load_or_create_signing_key()
        capability_state = self._load_capability_state()
        self._grants: dict[str, dict[str, Any]] = capability_state["grants"]
        self._transactions: dict[str, dict[str, Any]] = capability_state["transactions"]

    def issue_grant(
        self,
        *,
        grant_id: str,
        subject_ref: str,
        resource_patterns: list[str],
        allowed_effects: list[str],
        evidence_refs: list[str],
        expires_at: str,
    ) -> dict[str, Any]:
        if not all((grant_id, subject_ref, resource_patterns, allowed_effects, evidence_refs, expires_at)):
            raise ValueError("capability grant requires identity, scope, effects, evidence, and expiry")
        self._parse_time(expires_at)
        payload = {
            "grant_id": grant_id,
            "subject_ref": subject_ref,
            "resource_patterns": sorted(set(resource_patterns)),
            "allowed_effects": sorted(set(allowed_effects)),
            "evidence_refs": sorted(set(evidence_refs)),
            "expires_at": expires_at,
            "issued_at": datetime.now(timezone.utc).isoformat(),
        }
        encoded = self._b64(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        signature = self._b64(hmac.new(self._signing_key, encoded.encode("ascii"), hashlib.sha256).digest())
        record = {**payload, "token": f"{encoded}.{signature}", "token_kind": "nexusnet-scoped-capability-v1"}
        self._grants[grant_id] = record
        self._save_capability_state()
        return dict(record)

    def verify_token(self, token: str) -> dict[str, Any]:
        try:
            encoded, signature = token.split(".", 1)
            expected = self._b64(hmac.new(self._signing_key, encoded.encode("ascii"), hashlib.sha256).digest())
            if not hmac.compare_digest(signature, expected):
                return {"valid": False, "reason": "signature-invalid"}
            payload = json.loads(self._unb64(encoded).decode("utf-8"))
            if self._parse_time(payload["expires_at"]) <= datetime.now(timezone.utc):
                return {"valid": False, "reason": "expired", "grant": payload}
            return {"valid": True, "reason": None, "grant": payload}
        except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError):
            return {"valid": False, "reason": "token-malformed"}

    def observe_effect(
        self,
        *,
        token: str,
        effect: str,
        resource_ref: str,
        before_ref: str | None,
        after_ref: str | None,
        rollback_ref: str | None,
    ) -> dict[str, Any]:
        verification = self.verify_token(token)
        if not verification["valid"]:
            raise PermissionError(f"capability token rejected: {verification['reason']}")
        grant = verification["grant"]
        if effect not in grant["allowed_effects"]:
            raise PermissionError("effect is outside capability grant")
        if not any(fnmatch.fnmatch(resource_ref, pattern) for pattern in grant["resource_patterns"]):
            raise PermissionError("resource is outside capability grant")
        if effect in {"write", "execute", "memory_update", "model_update"} and not rollback_ref:
            raise PermissionError("mutating effect requires rollback_ref")
        receipt = {
            "receipt_id": f"effect:{hashlib.sha256((grant['grant_id'] + effect + resource_ref).encode()).hexdigest()[:20]}",
            "grant_id": grant["grant_id"],
            "effect": effect,
            "resource_ref": resource_ref,
            "before_ref": before_ref,
            "after_ref": after_ref,
            "rollback_ref": rollback_ref,
            "decision": "allowed",
            "observed_at": datetime.now(timezone.utc).isoformat(),
        }
        receipt["receipt_sha256"] = "sha256:" + hashlib.sha256(
            json.dumps(receipt, sort_keys=True).encode("utf-8")
        ).hexdigest()
        return receipt

    def apply_transaction(
        self,
        *,
        transaction_id: str,
        state: dict[str, Any],
        changes: dict[str, Any],
        evidence_refs: list[str],
        approval_ref: str,
    ) -> dict[str, Any]:
        if not transaction_id or not changes or not evidence_refs or not approval_ref:
            raise ValueError("transaction requires id, changes, evidence, and approval")
        if transaction_id in self._transactions:
            raise ValueError(f"transaction already exists: {transaction_id}")
        snapshot = dict(state)
        state.update(changes)
        record = {
            "transaction_id": transaction_id,
            "status": "applied",
            "snapshot": snapshot,
            "changes": dict(changes),
            "evidence_refs": list(evidence_refs),
            "approval_ref": approval_ref,
            "applied_at": datetime.now(timezone.utc).isoformat(),
        }
        self._transactions[transaction_id] = record
        self._save_capability_state()
        return dict(record)

    def rollback_transaction(self, transaction_id: str, *, state: dict[str, Any], reason_ref: str) -> dict[str, Any]:
        record = self._transactions.get(transaction_id)
        if not record or record["status"] != "applied":
            raise PermissionError("transaction is not applied")
        if not reason_ref:
            raise ValueError("reason_ref is required")
        state.clear()
        state.update(record["snapshot"])
        record["status"] = "rolled-back"
        record["rollback_reason_ref"] = reason_ref
        record["rolled_back_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capability_state()
        return dict(record)

    def evaluate(
        self,
        *,
        action_id: str,
        actor_ref: str,
        effect_type: EffectType,
        capability_refs: list[str],
        sandbox_state: str,
        operator_approved: bool,
        evidence_refs: list[str],
        observed_effect_type: str | None = None,
        rollback_available: bool = False,
        rollback_ref: str = "",
    ) -> dict[str, Any]:
        blockers = []
        if not evidence_refs:
            blockers.append("authority_decision_requires_evidence_refs")
        if effect_type in WRITE_EFFECTS and sandbox_state in {"", "none", "unknown"}:
            blockers.append("write_effect_requires_sandbox")
        if effect_type in WRITE_EFFECTS and not operator_approved:
            blockers.append("write_effect_requires_operator_approval")

        created_at = utcnow().isoformat()
        record = AuthorityDecisionRecord(
            action_id=action_id,
            actor_ref=actor_ref,
            effect_type=effect_type,
            status="blocked" if blockers else "allowed-shadow",
            blockers=blockers,
            capability_refs=capability_refs,
            sandbox_state=sandbox_state,
            operator_approved=operator_approved,
            evidence_refs=evidence_refs,
            observed_effect_receipt={
                "receipt_id": f"effect::{action_id}",
                "declared_effect_type": effect_type,
                "observed_effect_type": observed_effect_type or effect_type,
                "created_at": created_at,
            },
            rollback_record={
                "rollback_id": f"rollback::{action_id}",
                "rollback_required": effect_type in WRITE_EFFECTS,
                "rollback_available": bool(rollback_available),
                "rollback_ref": rollback_ref,
            },
            production_action_allowed=False,
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_records(limit=limit)
        blocked_count = sum(1 for record in records if record.get("status") == "blocked")
        return {
            "surface_id": "authority-integrity-spine",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if blocked_count else ("live-bound" if records else "static-canon"),
            "decision_count": len(records),
            "blocked_count": blocked_count,
            "latest_decision": records[0] if records else None,
            "decisions": records,
            "production_action_boundary": "write-effects-require-sandbox-operator-approval-and-evidence",
            "capability_grant_count": len(self._grants),
            "transaction_count": len(self._transactions),
        }

    def _load_or_create_signing_key(self) -> bytes:
        configured = os.environ.get("NEXUS_AUTHORITY_SIGNING_KEY")
        if configured:
            return configured.encode("utf-8")
        if self.artifacts_dir is None:
            return os.urandom(32)
        path = self.artifacts_dir / "authority" / "capability-signing.key"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return path.read_bytes()
        key = os.urandom(32)
        path.write_bytes(key)
        return key

    def _load_capability_state(self) -> dict[str, dict[str, Any]]:
        if self.artifacts_dir is None:
            return {"grants": {}, "transactions": {}}
        path = self.artifacts_dir / "authority" / "capability-state.json"
        if not path.exists():
            return {"grants": {}, "transactions": {}}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"grants": {}, "transactions": {}}
        return {
            "grants": dict(payload.get("grants") or {}),
            "transactions": dict(payload.get("transactions") or {}),
        }

    def _save_capability_state(self) -> None:
        if self.artifacts_dir is None:
            return
        path = self.artifacts_dir / "authority" / "capability-state.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"grants": self._grants, "transactions": self._transactions}, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        os.replace(temporary, path)

    @staticmethod
    def _b64(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    @staticmethod
    def _unb64(value: str) -> bytes:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

    @staticmethod
    def _parse_time(value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timestamp must include timezone")
        return parsed

    def _persist(self, record: dict[str, Any]) -> None:
        if self.decisions_dir is None:
            self._records.insert(0, record)
            return
        path = self._artifact_path_for_action_id(record["action_id"])
        record["artifact_path"] = str(path)
        payload = json.dumps(record, indent=2, sort_keys=True, allow_nan=False)
        path.write_text(payload, encoding="utf-8")
        persisted = json.loads(path.read_text(encoding="utf-8"))
        AuthorityDecisionRecord(**persisted)
        self._records.insert(0, record)

    def _artifact_path_for_action_id(self, action_id: str) -> Path:
        if self.decisions_dir is None:
            raise ValueError("decisions_dir is required for persisted authority decisions")
        digest = hashlib.sha256(action_id.encode("utf-8")).hexdigest()
        path = self.decisions_dir / f"{digest}.json"
        decisions_root = self.decisions_dir.resolve()
        resolved_path = path.resolve()
        if resolved_path.parent != decisions_root:
            raise ValueError("authority decision artifact path escaped decisions directory")
        return path

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records_by_action_id = {record.get("action_id"): record for record in reversed(self._records)}
        if self.decisions_dir is not None:
            disk_records: dict[str, tuple[str, str, dict[str, Any]]] = {}
            for path in sorted(self.decisions_dir.glob("*.json"), key=lambda item: item.name):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    if not isinstance(payload, dict):
                        continue
                    record = AuthorityDecisionRecord(**payload).model_dump(mode="json")
                except (OSError, json.JSONDecodeError, ValidationError):
                    continue
                action_id = record.get("action_id")
                created_at = str(record.get("observed_effect_receipt", {}).get("created_at") or "")
                candidate_key = (created_at, path.name)
                if action_id not in disk_records or candidate_key > disk_records[action_id][:2]:
                    disk_records[action_id] = (*candidate_key, record)
            for action_id, (_, _, record) in disk_records.items():
                records_by_action_id.setdefault(action_id, record)
        records = list(records_by_action_id.values())
        records.sort(key=lambda item: str(item.get("observed_effect_receipt", {}).get("created_at") or ""), reverse=True)
        return records[:limit]
