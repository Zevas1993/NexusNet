from __future__ import annotations

import json
from pathlib import Path

from nexus.storage import NexusStore

from ..schemas import RetirementShadowRecord


class RetirementShadowLog:
    def __init__(self, *, store: NexusStore, artifacts_dir: Path):
        self.store = store
        self.artifacts_dir = artifacts_dir

    def persist(self, record: RetirementShadowRecord) -> RetirementShadowRecord:
        relative = f"teachers/retirement/{record.teacher_id}/{record.record_id}.json"
        payload = record.model_dump(mode="json")
        path = self.store.write_artifact(relative, json.dumps(payload, indent=2))
        updated = record.model_copy(update={"artifact_path": path})
        self.store.save_retirement_shadow_record(updated.model_dump(mode="json"))
        return updated

    def list(self, *, teacher_id: str | None = None, limit: int = 100) -> list[dict]:
        return self.store.list_retirement_shadow_records(teacher_id=teacher_id, limit=limit)
