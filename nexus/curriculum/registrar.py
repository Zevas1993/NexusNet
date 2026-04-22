from __future__ import annotations

from ..schemas import new_id, utcnow
from ..storage import NexusStore


class CurriculumRegistrar:
    def __init__(self, store: NexusStore):
        self.store = store

    def record_grade(self, *, subject: str, course: str, status: str, score: float | None, detail: dict) -> dict:
        record = {
            "record_id": new_id("course"),
            "subject": subject,
            "course": course,
            "status": status,
            "score": score,
            "detail": detail,
            "created_at": utcnow().isoformat(),
        }
        self.store.save_curriculum_record(
            record["record_id"],
            subject,
            course,
            status,
            score,
            detail,
            record["created_at"],
        )
        return record

    def transcript(self, subject: str | None = None, limit: int = 200) -> list[dict]:
        return self.store.list_curriculum_records(subject=subject, limit=limit)
