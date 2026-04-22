from __future__ import annotations

from ..schemas import ExperimentRecord
from ..storage import NexusStore


class ExperimentService:
    def __init__(self, store: NexusStore):
        self.store = store

    def record(self, record: ExperimentRecord) -> ExperimentRecord:
        self.store.save_experiment(record.model_dump(mode="json"))
        return record

    def list(self) -> list[ExperimentRecord]:
        return [ExperimentRecord.model_validate(payload) for payload in self.store.list_experiments()]

