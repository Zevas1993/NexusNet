from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EvolutionMemory:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load()

    def record(self, *, feature_key: str, plan_id: str, outcome: str, evidence_id: str = "") -> None:
        record = {
            "feature_key": feature_key,
            "plan_id": plan_id,
            "outcome": outcome,
            "evidence_id": evidence_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        record["digest"] = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        self._state["records"].append(record)
        self._write()

    def priors(self, feature_key: str) -> dict[str, float]:
        totals: dict[str, list[int]] = {}
        for record in self._state["records"]:
            if record["feature_key"] != feature_key:
                continue
            bucket = totals.setdefault(record["plan_id"], [0, 0])
            bucket[0] += 1 if record["outcome"] in {"promoted", "successful"} else 0
            bucket[1] += 1
        return {plan_id: (successes + 1) / (count + 2) for plan_id, (successes, count) in totals.items()}

    def summary(self) -> dict[str, Any]:
        outcomes: dict[str, int] = {}
        for record in self._state["records"]:
            outcomes[record["outcome"]] = outcomes.get(record["outcome"], 0) + 1
        return {"record_count": len(self._state["records"]), "outcomes": outcomes}

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"schema_version": "1.0", "records": []}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"schema_version": "1.0", "records": []}
        return payload if isinstance(payload.get("records"), list) else {"schema_version": "1.0", "records": []}

    def _write(self) -> None:
        descriptor, name = tempfile.mkstemp(prefix=self.path.name, suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(self._state, handle, sort_keys=True, separators=(",", ":"))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(name, self.path)
        finally:
            Path(name).unlink(missing_ok=True)
