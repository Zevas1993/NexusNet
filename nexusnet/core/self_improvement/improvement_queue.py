from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from .event_schema import ImprovementEvent
from .triage import TriageDecision, triage_improvement_event


QueueStatus = Literal["proposed", "validated", "approved", "deployed", "monitored", "reverted", "rejected"]

ALLOWED_TRANSITIONS: dict[QueueStatus, set[QueueStatus]] = {
    "proposed": {"validated", "rejected"},
    "validated": {"approved", "rejected"},
    "approved": {"deployed", "reverted"},
    "deployed": {"monitored", "reverted"},
    "monitored": {"reverted"},
    "reverted": set(),
    "rejected": set(),
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def queue_id() -> str:
    return f"improveq::{uuid4()}"


class QueueTransition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_status: QueueStatus | None = None
    to_status: QueueStatus
    actor: str
    reason: str
    timestamp: datetime = Field(default_factory=utc_now)


class ImprovementQueueItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queue_id: str = Field(default_factory=queue_id)
    event: ImprovementEvent
    decision: TriageDecision
    status: QueueStatus
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    history: list[QueueTransition] = Field(default_factory=list)


class ImprovementQueue:
    def __init__(self, storage_path: str | Path):
        self.storage_path = Path(storage_path)
        self._items: dict[str, ImprovementQueueItem] = {}
        self._load()

    def propose(
        self,
        event: ImprovementEvent,
        *,
        decision: TriageDecision | None = None,
        actor: str = "NexusBrain",
        reason: str = "self-improvement event triaged",
    ) -> ImprovementQueueItem:
        resolved_decision = decision or triage_improvement_event(event)
        status: QueueStatus = "proposed" if resolved_decision.queue_required else "rejected"
        item = ImprovementQueueItem(
            event=event,
            decision=resolved_decision,
            status=status,
            history=[
                QueueTransition(
                    from_status=None,
                    to_status=status,
                    actor=actor,
                    reason=reason,
                )
            ],
        )
        self._items[item.queue_id] = item
        self._save()
        return item

    def transition(
        self,
        queue_id: str,
        status: QueueStatus,
        *,
        actor: str,
        reason: str,
    ) -> ImprovementQueueItem:
        item = self.get(queue_id)
        allowed = ALLOWED_TRANSITIONS[item.status]
        if status not in allowed:
            raise ValueError(f"Invalid improvement queue transition: {item.status} -> {status}")
        updated = item.model_copy(
            update={
                "status": status,
                "updated_at": utc_now(),
                "history": [
                    *item.history,
                    QueueTransition(
                        from_status=item.status,
                        to_status=status,
                        actor=actor,
                        reason=reason,
                    ),
                ],
            }
        )
        self._items[queue_id] = updated
        self._save()
        return updated

    def get(self, queue_id: str) -> ImprovementQueueItem:
        try:
            return self._items[queue_id]
        except KeyError as exc:
            raise KeyError(f"Unknown improvement queue item: {queue_id}") from exc

    def list_items(self, *, status: QueueStatus | None = None) -> list[ImprovementQueueItem]:
        items = sorted(self._items.values(), key=lambda item: item.created_at)
        if status is None:
            return items
        return [item for item in items if item.status == status]

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
        self._items = {
            item.queue_id: item
            for item in (ImprovementQueueItem.model_validate(record) for record in payload.get("items", []))
        }

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "nexusnet-self-improvement-queue-v1",
            "items": [item.model_dump(mode="json") for item in self.list_items()],
        }
        self.storage_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
