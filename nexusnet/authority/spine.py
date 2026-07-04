from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow
from pydantic import ValidationError

from .contracts import AuthorityDecisionRecord, EffectType


WRITE_EFFECTS = {"filesystem_write", "shell", "desktop", "browser", "model_update", "memory_update"}


class AuthorityIntegritySpine:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.decisions_dir = self.artifacts_dir / "authority" / "decisions" if self.artifacts_dir else None
        if self.decisions_dir is not None:
            self.decisions_dir.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

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
        }

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
