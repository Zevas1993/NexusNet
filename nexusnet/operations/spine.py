from __future__ import annotations

import hashlib
import json
import os
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class OperationalSpineService:
    """Durable worktree, release, monitor, scheduler, and disaster-recovery runtime."""

    CHANNELS = {"shadow", "canary", "stable"}

    def __init__(self, *, artifacts_dir: Path | str) -> None:
        self.root = Path(artifacts_dir) / "operational-spine"
        self.root.mkdir(parents=True, exist_ok=True)
        self.recovery_dir = self.root / "recovery"
        self.state_path = self.root / "state.json"
        if not self.state_path.exists():
            self._save(self._empty_state())

    def register_worktree(
        self,
        *,
        worktree_id: str,
        path: str,
        canonical_branch: str,
        current_branch: str,
        preserved_ref: str,
        dirty: bool,
        owner: str,
    ) -> dict[str, Any]:
        blockers = []
        if current_branch != canonical_branch:
            blockers.append("branch-not-canonical")
        if dirty:
            blockers.append("dirty-worktree")
        record = {
            "worktree_id": self._required(worktree_id, "worktree_id"),
            "path_digest": self._digest(self._required(path, "path")),
            "canonical_branch": self._required(canonical_branch, "canonical_branch"),
            "current_branch": self._required(current_branch, "current_branch"),
            "preserved_ref": self._required(preserved_ref, "preserved_ref"),
            "owner": self._required(owner, "owner"),
            "dirty": bool(dirty),
            "status": "aligned" if not blockers else "blocked",
            "blockers": blockers,
            "updated_at": self._now(),
        }
        state = self._load()
        state["worktrees"][worktree_id] = record
        self._audit(state, "worktree.registered", worktree_id, record["status"])
        self._save(state)
        return deepcopy(record)

    def worktree(self, worktree_id: str) -> dict[str, Any] | None:
        item = self._load()["worktrees"].get(worktree_id)
        return deepcopy(item) if item else None

    def register_release(
        self,
        *,
        release_id: str,
        channel: str,
        artifact_ref: str,
        owner: str,
        feature_flag: str,
        monitoring_ref: str,
        rollback_ref: str,
        evidence_refs: list[str],
        approval_refs: list[str],
    ) -> dict[str, Any]:
        channel = str(channel).strip().lower()
        blockers = []
        if channel not in self.CHANNELS:
            blockers.append("release-channel-invalid")
        for value, blocker in (
            (feature_flag, "feature-flag-required"),
            (monitoring_ref, "monitoring-ref-required"),
            (rollback_ref, "rollback-ref-required"),
        ):
            if not str(value or "").strip():
                blockers.append(blocker)
        if not evidence_refs:
            blockers.append("evidence-required")
        if not approval_refs:
            blockers.append("approval-required")
        record = {
            "release_id": self._required(release_id, "release_id"),
            "channel": channel,
            "artifact_ref": self._required(artifact_ref, "artifact_ref"),
            "owner": self._required(owner, "owner"),
            "feature_flag": str(feature_flag),
            "monitoring_ref": str(monitoring_ref),
            "rollback_ref": str(rollback_ref),
            "evidence_refs": sorted(set(map(str, evidence_refs))),
            "approval_refs": sorted(set(map(str, approval_refs))),
            "status": "ready" if not blockers else "blocked",
            "blockers": blockers,
            "created_at": self._now(),
        }
        state = self._load()
        state["releases"][release_id] = record
        self._audit(state, "release.registered", release_id, record["status"])
        self._save(state)
        return deepcopy(record)

    def release(self, release_id: str) -> dict[str, Any] | None:
        item = self._load()["releases"].get(release_id)
        return deepcopy(item) if item else None

    def record_monitor_observation(
        self,
        *,
        monitor_id: str,
        release_id: str,
        metrics: dict[str, float],
        thresholds: dict[str, float],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        state = self._load()
        release = state["releases"].get(release_id)
        if release is None:
            raise KeyError(f"unknown release: {release_id}")
        safe_metrics = {str(key): float(value) for key, value in metrics.items()}
        safe_thresholds = {str(key): float(value) for key, value in thresholds.items()}
        violations = sorted(
            key for key, threshold in safe_thresholds.items()
            if key not in safe_metrics or safe_metrics[key] > threshold
        )
        observation = {
            "monitor_id": self._required(monitor_id, "monitor_id"),
            "release_id": release_id,
            "metrics": safe_metrics,
            "thresholds": safe_thresholds,
            "violations": violations,
            "evidence_refs": sorted(set(map(str, evidence_refs))),
            "status": "slo-violated" if violations else "healthy",
            "rollback_required": bool(violations),
            "observed_at": self._now(),
        }
        state["monitors"].setdefault(monitor_id, []).append(observation)
        if violations:
            release["status"] = "rollback-required"
            release["blockers"] = sorted(set(release.get("blockers", [])) | {f"slo:{item}" for item in violations})
        self._audit(state, "monitor.observed", monitor_id, observation["status"])
        self._save(state)
        return deepcopy(observation)

    def schedule(
        self,
        *,
        job_id: str,
        action_ref: str,
        interval_seconds: int,
        authority_ref: str | None,
        enabled: bool,
        next_run_at: str | None = None,
    ) -> dict[str, Any]:
        if int(interval_seconds) < 60:
            raise ValueError("scheduler interval must be at least 60 seconds")
        if enabled and not str(authority_ref or "").strip():
            raise PermissionError("enabled scheduled jobs require an authority_ref")
        next_run = next_run_at or self._now()
        self._parse_time(next_run)
        job = {
            "job_id": self._required(job_id, "job_id"),
            "action_ref": self._required(action_ref, "action_ref"),
            "interval_seconds": int(interval_seconds),
            "authority_ref": str(authority_ref) if authority_ref else None,
            "enabled": bool(enabled),
            "next_run_at": next_run,
            "created_at": self._now(),
        }
        state = self._load()
        state["jobs"][job_id] = job
        self._audit(state, "job.scheduled", job_id, "enabled" if enabled else "disabled")
        self._save(state)
        return deepcopy(job)

    def due_jobs(self, *, at: str | None = None) -> list[dict[str, Any]]:
        instant = self._parse_time(at or self._now())
        jobs = [
            deepcopy(job)
            for job in self._load()["jobs"].values()
            if job["enabled"] and self._parse_time(job["next_run_at"]) <= instant
        ]
        return sorted(jobs, key=lambda item: (item["next_run_at"], item["job_id"]))

    def create_recovery_snapshot(self, *, snapshot_id: str, evidence_refs: list[str]) -> dict[str, Any]:
        if not evidence_refs:
            raise ValueError("recovery snapshot requires evidence_refs")
        snapshot_id = self._required(snapshot_id, "snapshot_id")
        state = self._load()
        payload = {
            "snapshot_id": snapshot_id,
            "created_at": self._now(),
            "evidence_refs": sorted(set(map(str, evidence_refs))),
            "state": deepcopy(state),
        }
        path = self.recovery_dir / f"{self._safe_name(snapshot_id)}.json"
        self._write_json(path, payload)
        metadata = {key: payload[key] for key in ("snapshot_id", "created_at", "evidence_refs")}
        metadata["snapshot_ref"] = str(path)
        state["recovery_snapshots"][snapshot_id] = metadata
        self._audit(state, "recovery.snapshot-created", snapshot_id, "verified")
        self._save(state)
        return deepcopy(metadata)

    def restore_recovery_snapshot(self, snapshot_id: str, *, approval_ref: str, reason_ref: str) -> dict[str, Any]:
        approval_ref = self._required(approval_ref, "approval_ref")
        reason_ref = self._required(reason_ref, "reason_ref")
        path = self.recovery_dir / f"{self._safe_name(snapshot_id)}.json"
        if not path.exists():
            raise KeyError(f"unknown recovery snapshot: {snapshot_id}")
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        restored = deepcopy(snapshot["state"])
        self._audit(restored, "recovery.snapshot-restored", snapshot_id, "restored")
        restored["audit"][-1].update({"approval_ref": approval_ref, "reason_ref": reason_ref})
        self._save(restored)
        return {
            "snapshot_id": snapshot_id,
            "status": "restored",
            "approval_ref": approval_ref,
            "reason_ref": reason_ref,
            "restored_at": self._now(),
        }

    def summary(self) -> dict[str, Any]:
        state = self._load()
        return {
            "surface_id": "operational-spine-runtime",
            "runtime_state": "live-bound",
            "worktree_count": len(state["worktrees"]),
            "release_count": len(state["releases"]),
            "monitor_count": len(state["monitors"]),
            "job_count": len(state["jobs"]),
            "recovery_snapshot_count": len(state["recovery_snapshots"]),
            "rollback_required_release_ids": sorted(
                key for key, item in state["releases"].items() if item["status"] == "rollback-required"
            ),
            "audit_event_count": len(state["audit"]),
        }

    @staticmethod
    def _empty_state() -> dict[str, Any]:
        return {"worktrees": {}, "releases": {}, "monitors": {}, "jobs": {}, "recovery_snapshots": {}, "audit": []}

    def _load(self) -> dict[str, Any]:
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        self._write_json(self.state_path, payload)

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temporary, path)

    def _audit(self, state: dict[str, Any], event: str, subject_ref: str, status: str) -> None:
        state["audit"].append({"event": event, "subject_ref": subject_ref, "status": status, "at": self._now()})

    @staticmethod
    def _digest(value: str) -> str:
        return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _safe_name(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "snapshot"

    @staticmethod
    def _required(value: Any, field: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError(f"{field} is required")
        return text

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _parse_time(value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timestamps must include a timezone")
        return parsed
