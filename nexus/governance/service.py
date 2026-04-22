from __future__ import annotations

import json
from pathlib import Path

from ..config import NexusPaths
from ..schemas import ApprovalRequest, PromotionDecision, RollbackRecord, new_id, utcnow
from ..storage import NexusStore


class GovernanceService:
    def __init__(self, paths: NexusPaths, store: NexusStore):
        self.paths = paths
        self.store = store
        self.audit_log_path = paths.logs_dir / "audit.log"
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def approval_required(self, subject: str, require_flag: bool = False) -> bool:
        subject_low = subject.lower()
        return require_flag or any(token in subject_low for token in ["promotion", "rollback", "dream", "foundry"])

    def record_event(self, action: str, detail: dict) -> dict:
        event_id = new_id("audit")
        created_at = utcnow().isoformat()
        self.store.save_audit_event(event_id, action, detail, created_at)
        with self.audit_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"event_id": event_id, "action": action, "detail": detail, "created_at": created_at}) + "\n")
        try:
            from core.ops.audit import log as legacy_log  # type: ignore

            legacy_log(action, detail)
        except Exception:
            pass
        return {"event_id": event_id, "action": action, "detail": detail, "created_at": created_at}

    def record_approval(self, request: ApprovalRequest) -> PromotionDecision:
        decision = PromotionDecision(
            subject=request.subject,
            decision=request.decision,
            approver=request.approver,
            rationale=request.rationale,
            metadata=request.metadata,
        )
        self.store.save_approval(decision.model_dump(mode="json"))
        self.record_event("approval.recorded", decision.model_dump(mode="json"))
        return decision

    def prepare_rollback(self, subject: str, target_version: str, metadata: dict | None = None) -> RollbackRecord:
        record = RollbackRecord(subject=subject, target_version=target_version, metadata=metadata or {})
        self.store.save_rollback(record.model_dump(mode="json"))
        self.record_event("rollback.prepared", record.model_dump(mode="json"))
        return record

    def list_audit(self, limit: int = 200) -> list[dict]:
        return self.store.list_audit_events(limit=limit)

