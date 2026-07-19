from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable


Reducer = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


class IncrementalProjectionEngine:
    """Durable event log with reducer checkpoints that apply only unseen events."""

    def __init__(self, *, artifacts_dir: Path | str) -> None:
        self.root = Path(artifacts_dir) / "incremental-projections"
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "state.json"
        if not self.path.exists():
            self._save({"events": [], "projections": {}})
        self._reducers: dict[str, tuple[dict[str, Any], Reducer]] = {}

    def register_reducer(self, projection_id: str, *, initial: dict[str, Any], reducer: Reducer) -> None:
        if not projection_id or not callable(reducer):
            raise ValueError("projection requires id and reducer")
        self._reducers[projection_id] = (deepcopy(initial), reducer)

    def append(self, *, event_id: str, event_type: str, payload: dict[str, Any], source_refs: list[str]) -> dict[str, Any]:
        if not event_id or not event_type or not source_refs:
            raise ValueError("event requires id, type, and source_refs")
        state = self._load()
        if any(event["event_id"] == event_id for event in state["events"]):
            raise ValueError(f"duplicate event_id: {event_id}")
        event = {
            "sequence": len(state["events"]) + 1,
            "event_id": event_id,
            "event_type": event_type,
            "payload": deepcopy(payload),
            "source_refs": sorted(set(source_refs)),
        }
        state["events"].append(event)
        self._save(state)
        return deepcopy(event)

    def project(self, projection_id: str) -> dict[str, Any]:
        if projection_id not in self._reducers:
            raise KeyError(f"unregistered projection: {projection_id}")
        initial, reducer = self._reducers[projection_id]
        persisted = self._load()
        checkpoint = persisted["projections"].get(projection_id, {"state": deepcopy(initial), "last_sequence": 0})
        projection_state = deepcopy(checkpoint["state"])
        pending = [event for event in persisted["events"] if event["sequence"] > checkpoint["last_sequence"]]
        for event in pending:
            projection_state = reducer(projection_state, deepcopy(event["payload"]))
            if not isinstance(projection_state, dict):
                raise TypeError("projection reducer must return a dict")
        last_sequence = pending[-1]["sequence"] if pending else checkpoint["last_sequence"]
        persisted["projections"][projection_id] = {"state": projection_state, "last_sequence": last_sequence}
        self._save(persisted)
        return {
            "projection_id": projection_id,
            "state": deepcopy(projection_state),
            "last_sequence": last_sequence,
            "applied_event_count": len(pending),
        }

    def _load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temporary, self.path)
