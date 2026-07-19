from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any


class OperationalChangeRegistry:
    """Durable rollout and rollback gate for every governed operational change."""

    STAGES = ("draft", "shadow", "canary", "active", "rolled-back")

    def __init__(self, *, artifacts_dir: Path | str) -> None:
        self.path = Path(artifacts_dir) / "operations" / "change-passports.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save({"passports": {}, "events": []})

    def create(self, **fields: Any) -> dict[str, Any]:
        required_scalars = ("change_id", "owner", "goal", "base_state_ref", "worktree_ref", "feature_flag", "rollback_ref")
        missing = [name for name in required_scalars if not str(fields.get(name) or "").strip()]
        required_lists = ("source_refs", "affected_surfaces", "permissions", "evidence_refs", "telemetry_refs", "approval_refs")
        missing.extend(name for name in required_lists if not fields.get(name))
        if missing:
            raise ValueError(f"OperationalChangePassport missing: {', '.join(sorted(missing))}")
        change_id = str(fields["change_id"])
        approval_refs = sorted(set(fields["approval_refs"]))
        approval_granted = any(
            marker in str(ref).lower()
            for ref in approval_refs
            for marker in ("approved", "allow", "granted")
        )
        blockers = [] if approval_granted else ["operator-approval-required"]
        passport = {
            "passport_kind": "OperationalChangePassport",
            "change_id": change_id,
            "owner": str(fields["owner"]),
            "goal": str(fields["goal"]),
            "source_refs": sorted(set(fields["source_refs"])),
            "base_state_ref": str(fields["base_state_ref"]),
            "worktree_ref": str(fields["worktree_ref"]),
            "affected_surfaces": sorted(set(fields["affected_surfaces"])),
            "permissions": sorted(set(fields["permissions"])),
            "feature_flag": str(fields["feature_flag"]),
            "evidence_refs": sorted(set(fields["evidence_refs"])),
            "telemetry_refs": sorted(set(fields["telemetry_refs"])),
            "rollback_ref": str(fields["rollback_ref"]),
            "approval_refs": approval_refs,
            "rollout_stage": "draft",
            "status": "ready-for-shadow" if not blockers else "blocked",
            "blockers": blockers,
            "monitoring_refs": [],
            "rollback_rehearsed": False,
            "production_mutation_allowed": False,
        }
        payload = self._load()
        payload["passports"][change_id] = passport
        payload["events"].append({"event": "passport.created", "change_id": change_id})
        self._save(payload)
        return deepcopy(passport)

    def get(self, change_id: str) -> dict[str, Any] | None:
        passport = self._load()["passports"].get(change_id)
        return deepcopy(passport) if passport else None

    def transition(self, change_id: str, *, target_stage: str, monitoring_ref: str, rollback_rehearsed: bool) -> dict[str, Any]:
        payload = self._load()
        passport = payload["passports"].get(change_id)
        if passport is None:
            raise KeyError(change_id)
        if target_stage not in self.STAGES:
            raise ValueError(f"unsupported rollout stage: {target_stage}")
        current = passport["rollout_stage"]
        if passport.get("blockers"):
            raise PermissionError("operational change passport has unresolved blockers")
        allowed = {
            "draft": {"shadow", "rolled-back"},
            "shadow": {"canary", "rolled-back"},
            "canary": {"active", "rolled-back"},
            "active": {"rolled-back"},
            "rolled-back": set(),
        }
        if target_stage not in allowed[current]:
            raise PermissionError(f"invalid rollout transition: {current} -> {target_stage}")
        if not monitoring_ref or not rollback_rehearsed:
            raise PermissionError("monitoring evidence and rollback rehearsal are required")
        passport["rollout_stage"] = target_stage
        passport["monitoring_refs"] = sorted(set([*passport["monitoring_refs"], monitoring_ref]))
        passport["rollback_rehearsed"] = True
        passport["status"] = "rolled-back" if target_stage == "rolled-back" else f"{target_stage}-active"
        passport["production_mutation_allowed"] = target_stage == "active"
        payload["events"].append({"event": "passport.transitioned", "change_id": change_id, "stage": target_stage})
        self._save(payload)
        return deepcopy(passport)

    def summary(self) -> dict[str, Any]:
        payload = self._load()
        stages: dict[str, int] = {}
        for passport in payload["passports"].values():
            stage = passport["rollout_stage"]
            stages[stage] = stages.get(stage, 0) + 1
        return {
            "surface_id": "operational-change-passports",
            "runtime_state": "live-bound",
            "passport_count": len(payload["passports"]),
            "stage_counts": stages,
            "event_count": len(payload["events"]),
        }

    def _load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temporary, self.path)
