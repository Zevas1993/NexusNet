from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class MemoryGovernanceService:
    OPERATIONS = {"store", "update", "archive", "delete", "compact", "share"}

    def __init__(self, *, memory_os: Any | None = None, artifacts_dir: Path | str, events: Any | None = None):
        self.memory_os = memory_os
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "memory-governance"
        self.events = events

    def propose(
        self,
        *,
        fact_id: str,
        content: str,
        source: str,
        operation: str = "store",
        evidence: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        if operation not in self.OPERATIONS:
            raise ValueError(f"unsupported memory governance operation: {operation}")
        proposal = {
            "proposal_id": new_id("memproposal"),
            "fact_id": fact_id,
            "content": content,
            "source": source,
            "operation": operation,
            "status": "approval_required",
            "created_at": utcnow().isoformat(),
            "evidence": evidence or {},
            "linked_trace_ids": list(linked_trace_ids or []),
            "approval_path": {"decision": "not_requested", "memory_mutation_requires_policy": True},
            "provenance_diff": {
                "before": self._existing_memory(fact_id),
                "after": {"fact_id": fact_id, "content": content, "source": source},
                "state": "proposal_only",
            },
            "mutation_allowed": False,
        }
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{proposal['proposal_id']}.json"
        proposal["artifact_path"] = str(path)
        path.write_text(json.dumps(proposal, indent=2), encoding="utf-8")
        if self.events:
            self.events.record(
                event_type="memory.proposal_recorded",
                subject=f"memory:{fact_id}",
                trace_ids=proposal["linked_trace_ids"],
                payload={
                    "proposal_id": proposal["proposal_id"],
                    "operation": operation,
                    "status": proposal["status"],
                    "mutation_allowed": False,
                },
            )
        return {"status_label": "STRONG ACCEPTED DIRECTION", "proposal": proposal, "summary": self.summary()}

    def summary(self) -> dict[str, Any]:
        proposals = self._proposals(limit=100)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "proposal_count": len(proposals),
            "status_counts": self._counts(proposals, "status"),
            "latest_proposal": proposals[0] if proposals else None,
            "compaction": {"status": "available", "mutation_allowed": False, "approval_required": True},
            "archival_memory": {"status": "governed", "mutation_allowed": False, "approval_required": True},
            "shared_memory": {"status": "deny_by_default", "mutation_allowed": False, "policy_grant_required": True},
            "update_delete_approvals": {"required": True, "manual_approval_is_not_execution_authority": True},
            "provenance_diffs": {"recorded": bool(proposals), "latest": (proposals[0].get("provenance_diff") if proposals else None)},
            "items": proposals,
        }

    def _existing_memory(self, fact_id: str) -> dict[str, Any] | None:
        if self.memory_os is None:
            return None
        try:
            record = self.memory_os.retrieve(fact_id)
        except Exception:
            return None
        return record.model_dump(mode="json") if record is not None else None

    def _proposals(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        items = []
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(items) >= limit:
                break
        return items

    def _counts(self, items: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = str(item.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
