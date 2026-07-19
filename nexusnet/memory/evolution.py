from __future__ import annotations

import hashlib
import json
import math
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .operating_system import MemoryOperatingSystem


class MemoryEvolutionRegistry:
    """Durable MemoryEvolutionPassport gate with reversible Memory OS mutations."""

    OPERATIONS = {"store", "update", "archive", "forget"}
    PRIVACY_CLASSES = {"public", "internal", "private", "federated"}
    CONSENT_STATES = {"granted", "public-source", "not-required"}
    PROMOTION_STATES = {"shadow", "canary", "active"}

    def __init__(self, *, artifacts_dir: Path | str) -> None:
        self.root = Path(artifacts_dir) / "memory"
        self.root.mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.root / "evolution-passports.json"
        self.state_path = self.root / "state.json"
        self.snapshots_dir = self.root / "rollback-snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.memory = MemoryOperatingSystem(self.state_path)
        if not self.ledger_path.exists():
            self._save({"passports": {}, "audit": []})

    def propose(
        self,
        *,
        passport_id: str,
        operation: str,
        fact_id: str,
        content: str | None,
        source_refs: list[str],
        privacy_class: str,
        consent_status: str,
        confidence: float,
        contradiction_refs: list[str],
        eval_refs: list[str],
        eval_passed: bool,
        reviewer_refs: list[str],
        rollback_plan: dict[str, Any],
        promotion_state: str,
        effective_at: str | None = None,
    ) -> dict[str, Any]:
        passport_id = self._required(passport_id, "passport_id")
        fact_id = self._required(fact_id, "fact_id")
        operation = str(operation).strip().lower()
        confidence = float(confidence)
        blockers: list[str] = []
        if operation not in self.OPERATIONS:
            blockers.append("unsupported-operation")
        if operation in {"store", "update"} and not str(content or "").strip():
            blockers.append("content-required")
        if not source_refs:
            blockers.append("source-refs-required")
        if privacy_class not in self.PRIVACY_CLASSES:
            blockers.append("privacy-class-invalid")
        if consent_status not in self.CONSENT_STATES:
            blockers.append("consent-required")
        if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
            blockers.append("confidence-invalid")
        if contradiction_refs and promotion_state == "active":
            blockers.append("unresolved-contradiction")
        if not eval_passed or not eval_refs:
            blockers.append("eval-pass-required")
        if len(set(filter(None, reviewer_refs))) < 2:
            blockers.append("reviewer-pair-required")
        if not rollback_plan:
            blockers.append("rollback-plan-required")
        if promotion_state not in self.PROMOTION_STATES:
            blockers.append("promotion-state-invalid")
        now = self._now()
        passport = {
            "schema_version": "nexusnet-memory-evolution-passport-v2",
            "surface_id": "MemoryEvolutionPassport",
            "passport_id": passport_id,
            "operation": operation,
            "fact_id": fact_id,
            "content_ref": self._content_ref(content),
            "source_refs": sorted(set(map(str, source_refs))),
            "privacy_class": privacy_class,
            "consent_status": consent_status,
            "effective_at": effective_at or now,
            "confidence": confidence,
            "contradiction_refs": sorted(set(map(str, contradiction_refs))),
            "eval_refs": sorted(set(map(str, eval_refs))),
            "eval_passed": bool(eval_passed),
            "reviewer_refs": sorted(set(map(str, reviewer_refs))),
            "rollback_plan": deepcopy(rollback_plan),
            "promotion_state": promotion_state,
            "status": "ready" if not blockers else "blocked",
            "blockers": blockers,
            "snapshot_ref": None,
            "snapshot_sha256": None,
            "applied_memory_id": None,
            "lifecycle": [{"state": "proposed", "at": now}],
            "raw_content_included": False,
        }
        ledger = self._load()
        if passport_id in ledger["passports"]:
            raise ValueError(f"passport already exists: {passport_id}")
        ledger["passports"][passport_id] = passport
        ledger["audit"].append({"event": "memory-evolution.proposed", "passport_id": passport_id, "status": passport["status"], "at": now})
        self._save(ledger)
        return deepcopy(passport)

    def get(self, passport_id: str) -> dict[str, Any] | None:
        passport = self._load()["passports"].get(passport_id)
        return deepcopy(passport) if passport else None

    def apply(self, passport_id: str, *, content: str | None = None) -> dict[str, Any]:
        ledger = self._load()
        passport = ledger["passports"].get(passport_id)
        if not passport or passport["status"] != "ready":
            raise PermissionError("memory evolution passport is not ready")
        if passport["operation"] in {"store", "update"}:
            if self._content_ref(content) != passport["content_ref"]:
                raise ValueError("content does not match the passport content_ref")
        snapshot = self.memory.export_state()
        snapshot_path = self.snapshots_dir / f"{hashlib.sha256(passport_id.encode()).hexdigest()}.json"
        snapshot_bytes = json.dumps(snapshot, indent=2, sort_keys=True).encode("utf-8")
        temporary_snapshot = snapshot_path.with_suffix(".tmp")
        temporary_snapshot.write_bytes(snapshot_bytes)
        os.replace(temporary_snapshot, snapshot_path)
        operation = passport["operation"]
        fact_id = passport["fact_id"]
        memory_id = None
        if operation == "store":
            record = self.memory.store(
                fact_id=fact_id,
                content=str(content),
                source=passport["source_refs"][0],
                evidence=self._evidence(passport),
            )
            memory_id = record.memory_id
        elif operation == "update":
            record = self.memory.update(
                fact_id=fact_id,
                content=str(content),
                source=passport["source_refs"][0],
                evidence=self._evidence(passport),
            )
            memory_id = record.memory_id
        elif operation == "archive":
            if self.memory.archive(fact_id) is None:
                raise KeyError(f"unknown memory fact: {fact_id}")
        elif operation == "forget":
            if self.memory.forget(fact_id) is None:
                raise KeyError(f"unknown memory fact: {fact_id}")
        passport["snapshot_ref"] = str(snapshot_path)
        passport["snapshot_sha256"] = "sha256:" + hashlib.sha256(snapshot_bytes).hexdigest()
        passport["applied_memory_id"] = memory_id
        passport["status"] = "applied"
        passport["lifecycle"].append({"state": "applied", "at": self._now()})
        ledger["audit"].append({"event": "memory-evolution.applied", "passport_id": passport_id, "at": self._now()})
        self._save(ledger)
        return deepcopy(passport)

    def rollback(self, passport_id: str, *, reason_ref: str) -> dict[str, Any]:
        ledger = self._load()
        passport = ledger["passports"].get(passport_id)
        if not passport or passport["status"] != "applied" or not passport.get("snapshot_ref"):
            raise PermissionError("memory evolution passport is not applied")
        reason_ref = self._required(reason_ref, "reason_ref")
        snapshot_path = Path(passport["snapshot_ref"])
        snapshot_bytes = snapshot_path.read_bytes()
        if "sha256:" + hashlib.sha256(snapshot_bytes).hexdigest() != passport.get("snapshot_sha256"):
            raise ValueError("memory rollback snapshot integrity check failed")
        self.memory.restore_state(json.loads(snapshot_bytes.decode("utf-8")))
        passport["status"] = "rolled-back"
        passport["lifecycle"].append({"state": "rolled-back", "at": self._now(), "reason_ref": reason_ref})
        ledger["audit"].append({"event": "memory-evolution.rolled-back", "passport_id": passport_id, "reason_ref": reason_ref, "at": self._now()})
        self._save(ledger)
        return deepcopy(passport)

    def summary(self) -> dict[str, Any]:
        ledger = self._load()
        passports = list(ledger["passports"].values())
        return {
            "surface_id": "memory-evolution-registry",
            "runtime_state": "live-bound",
            "passport_count": len(passports),
            "status_counts": {
                status: sum(1 for item in passports if item["status"] == status)
                for status in ("blocked", "ready", "applied", "rolled-back")
            },
            "audit_event_count": len(ledger["audit"]),
            "raw_content_included": False,
        }

    @staticmethod
    def _evidence(passport: dict[str, Any]) -> dict[str, Any]:
        return {
            "memory_evolution_passport_id": passport["passport_id"],
            "source_refs": passport["source_refs"],
            "eval_refs": passport["eval_refs"],
            "reviewer_refs": passport["reviewer_refs"],
            "confidence": passport["confidence"],
            "privacy_class": passport["privacy_class"],
        }

    def _load(self) -> dict[str, Any]:
        return json.loads(self.ledger_path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        temporary = self.ledger_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temporary, self.ledger_path)

    @staticmethod
    def _content_ref(content: str | None) -> str | None:
        if content is None:
            return None
        return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _required(value: Any, field: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError(f"{field} is required")
        return text

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
