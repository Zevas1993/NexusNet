from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow


class CheckpointRewindLedger:
    """In-memory exact snapshots for governed, subject-bound rewind operations."""

    def __init__(self, *, artifacts_dir: str | Path | None = None) -> None:
        self._checkpoints: dict[str, dict[str, Any]] = {}
        self._sequence = 0
        self._ledger_path = Path(artifacts_dir) / "checkpoint-rewind-ledger.json" if artifacts_dir else None
        self._load()

    def capture(self, *, subject_ref: str, state: dict[str, Any]) -> dict[str, Any]:
        if not subject_ref:
            raise ValueError("subject_ref is required")
        snapshot = deepcopy(state)
        snapshot_payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), default=str)
        self._sequence += 1
        checkpoint_id = f"checkpoint:{self._sequence:06d}"
        record = {
            "checkpoint_id": checkpoint_id,
            "subject_ref": subject_ref,
            "created_at": utcnow().isoformat(),
            "state": snapshot,
            "snapshot_sha256": "sha256:" + hashlib.sha256(snapshot_payload.encode("utf-8")).hexdigest(),
            "restore_policy": "exact-snapshot",
        }
        self._checkpoints[checkpoint_id] = record
        self._persist()
        return self._public(record)

    def rewind(self, checkpoint_id: str, *, subject_ref: str) -> dict[str, Any]:
        record = self._checkpoints.get(checkpoint_id)
        if record is None:
            raise KeyError(f"unknown checkpoint: {checkpoint_id}")
        if record["subject_ref"] != subject_ref:
            raise PermissionError("checkpoint subject mismatch")
        return self._public(record)

    def summary(self, *, limit: int = 20) -> dict[str, Any]:
        if limit < 1 or limit > 200:
            raise ValueError("limit must be between 1 and 200")
        records = sorted(
            self._checkpoints.values(),
            key=lambda record: record["created_at"],
            reverse=True,
        )[:limit]
        sanitized = [
            {
                "checkpoint_id": record["checkpoint_id"],
                "subject_ref_digest": "sha256:"
                + hashlib.sha256(record["subject_ref"].encode("utf-8")).hexdigest(),
                "created_at": record["created_at"],
                "snapshot_sha256": record["snapshot_sha256"],
                "restore_policy": record["restore_policy"],
            }
            for record in records
        ]
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "checkpoint-rewind-ledger",
            "runtime_state": "live-bound",
            "checkpoint_count": len(self._checkpoints),
            "recent_checkpoints": sanitized,
            "raw_state_exposed": False,
        }

    @staticmethod
    def _public(record: dict[str, Any]) -> dict[str, Any]:
        return {**record, "state": deepcopy(record["state"])}

    def _load(self) -> None:
        if self._ledger_path is None or not self._ledger_path.is_file():
            return
        payload = json.loads(self._ledger_path.read_text(encoding="utf-8"))
        for record in payload.get("checkpoints", []):
            checkpoint_id = str(record.get("checkpoint_id") or "")
            if checkpoint_id:
                self._checkpoints[checkpoint_id] = record
                self._sequence = max(self._sequence, int(checkpoint_id.rsplit(":", 1)[-1]))

    def _persist(self) -> None:
        if self._ledger_path is None:
            return
        self._ledger_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._ledger_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"checkpoints": list(self._checkpoints.values())}, sort_keys=True, separators=(",", ":"), default=str),
            encoding="utf-8",
        )
        temporary.replace(self._ledger_path)
