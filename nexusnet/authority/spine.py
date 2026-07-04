from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow

from .contracts import AuthorityDecisionRecord


WRITE_EFFECTS = {"filesystem_write", "shell", "desktop", "browser", "model_update", "memory_update"}


class AuthorityIntegritySpine:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "authority" / "decisions" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def evaluate(
        self,
        *,
        action_id: str,
        actor_ref: str,
        effect_type: str,
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
        receipt = {
            "receipt_id": f"effect::{action_id}",
            "declared_effect_type": effect_type,
            "observed_effect_type": observed_effect_type or effect_type,
            "created_at": utcnow().isoformat(),
        }
        rollback = {
            "rollback_id": f"rollback::{action_id}",
            "rollback_required": effect_type in WRITE_EFFECTS,
            "rollback_available": bool(rollback_available),
            "rollback_ref": rollback_ref,
        }
        record = AuthorityDecisionRecord(
            action_id=action_id,
            actor_ref=actor_ref,
            effect_type=effect_type,
            status="blocked" if blockers else "allowed-shadow",
            blockers=sorted(set(blockers)),
            capability_refs=capability_refs,
            sandbox_state=sandbox_state,
            operator_approved=operator_approved,
            evidence_refs=evidence_refs,
            observed_effect_receipt=receipt,
            rollback_record=rollback,
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "authority-integrity-spine",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(record.get("status") == "blocked" for record in self._records) else ("live-bound" if self._records else "static-canon"),
            "decision_count": len(self._records),
            "blocked_count": sum(1 for record in self._records if record.get("status") == "blocked"),
            "latest_decision": self._records[0] if self._records else None,
            "production_action_boundary": "write-effects-require-sandbox-operator-approval-and-evidence",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._records.insert(0, record)
        if self.root is None:
            return
        path = self.root / f"{record['action_id'].replace(':', '_').replace('/', '_')}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
