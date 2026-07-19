from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .event_spine import GenesisEventSpineService
from .self_repair import GenesisSelfRepairService


GENESIS_DREAM_RESEARCH_SCHEMA = "nexusnet-genesis-dream-research-v1"
GENESIS_DREAM_RESEARCH_SURFACE_ID = "genesis-dream-research-proposal-loop"


class GenesisDreamResearchService:
    """Layer 12 dream/research proposal loop fed by Genesis runtime events."""

    def __init__(
        self,
        *,
        artifacts_dir: Path | str,
        project_root: Path | str,
        event_spine: GenesisEventSpineService,
        self_repair: GenesisSelfRepairService,
        federated_outcomes: Any | None = None,
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.project_root = Path(project_root)
        self.event_spine = event_spine
        self.self_repair = self_repair
        self.federated_outcomes = federated_outcomes
        self.dream_dir = self.artifacts_dir / "genesis" / "dream-research"
        self.proposals_path = self.dream_dir / "proposals.jsonl"

    def summary(self, session_id: str | None = None, *, limit: int = 100) -> dict[str, Any]:
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        proposals = self._scoped(self._read_jsonl(self.proposals_path), session_ref_digest)
        automatic_degraded_heartbeat_proposals = [
            proposal
            for proposal in proposals
            if proposal.get("proposal_origin") == "automatic-degraded-heartbeat"
        ]
        latest = proposals[-1] if proposals else {}
        shared_summary = self.event_spine.summary(session_ref_digest=session_ref_digest, limit=limit)
        event_count = int((shared_summary.get("event_type_counts") or {}).get("genesis.dream_research.proposal", 0) or 0)
        status = "live-control-plane" if latest else "not-observed"
        return {
            "schema_version": GENESIS_DREAM_RESEARCH_SCHEMA,
            "surface_id": GENESIS_DREAM_RESEARCH_SURFACE_ID,
            "status": status,
            "honest_status_label": (
                "genesis-layer12-dream-research-proposal-loop-live-control-plane"
                if latest
                else "genesis-layer12-dream-research-proposal-loop-not-observed"
            ),
            "authority": "NexusBrain",
            "source": "genesis-shared-event-spine" if latest else None,
            "session_ref_digest": session_ref_digest,
            "proposal_count": len(proposals),
            "latest_dream_proposal_id": latest.get("dream_proposal_id"),
            "latest_proposal": latest,
            "recent_proposals": list(reversed(proposals[-20:])),
            "shared_event_spine": {
                "schema_version": "nexusnet-genesis-dream-research-shared-event-spine-v1",
                "surface_id": "genesis-dream-research-shared-event-spine",
                "status": shared_summary.get("status"),
                "event_count": event_count,
                "latest_event_ref": (
                    latest.get("shared_event_spine", {}).get("event_ref")
                    if isinstance(latest.get("shared_event_spine"), dict)
                    else None
                ),
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            },
            "automatic_observation": {
                "surface_id": "genesis-dream-research-automatic-observation",
                "status": (
                    "degraded-heartbeat-dream-proposal-observed"
                    if automatic_degraded_heartbeat_proposals
                    else "no-degraded-heartbeat-dream-proposal-observed"
                ),
                "degraded_heartbeat_proposal_count": len(automatic_degraded_heartbeat_proposals),
                "latest_degraded_heartbeat_dream_proposal_id": (
                    automatic_degraded_heartbeat_proposals[-1].get("dream_proposal_id")
                    if automatic_degraded_heartbeat_proposals
                    else None
                ),
                "promotion_started": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
                "raw_content_included": False,
            },
            "governance": {
                "dream_outputs_shadow_only": True,
                "low_temperature_critique_required": True,
                "linked_self_repair_required": True,
                "sandbox_eval_required_before_apply": True,
                "admin_approval_required_before_apply": True,
                "rollback_required": True,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
                "raw_content_included": False,
            },
            "evidence_refs": _sanitize_refs(
                [
                    latest.get("dream_proposal_id"),
                    latest.get("source_event_ref"),
                    latest.get("linked_self_repair_proposal_id"),
                    latest.get("shared_event_spine", {}).get("event_ref")
                    if isinstance(latest.get("shared_event_spine"), dict)
                    else None,
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-genesis-dream-research-ids-digests-research-refs-event-refs-and-linked-proposal-refs-only-"
                "no-prompts-outputs-session-ids-local-paths-admin-identities-or-raw-content"
            ),
            "mutation_boundary": "dream-research-proposals-only-linked-self-repair-remains-sandbox-admin-rollback-gated",
        }

    def propose_from_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        session_id = str(payload.get("session_id") or "")
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        event_ref = _safe_ref(payload.get("event_ref"))
        if not event_ref:
            raise ValueError("event_ref is required")
        event = self._find_event(event_ref=event_ref, session_id=session_id or None)
        research_refs = _sanitize_refs(payload.get("research_refs") or [])
        dream_objective = str(payload.get("dream_objective") or "dream governed repair proposal")
        proposal_origin = _proposal_origin(payload.get("proposal_origin"))
        requested_dream_proposal_id = _safe_ref(payload.get("dream_proposal_id"))
        if requested_dream_proposal_id:
            existing = next(
                (
                    proposal
                    for proposal in self._read_jsonl(self.proposals_path)
                    if str(proposal.get("dream_proposal_id") or "") == requested_dream_proposal_id
                ),
                None,
            )
            if existing is not None:
                replayed = dict(existing)
                replayed["status"] = "dream-proposal-replayed"
                replayed["proposal_status"] = str(existing.get("status") or "dream-proposal")
                return replayed
        target_ref = str(
            payload.get("target_ref")
            or f"genesis/safe-files/self-repair/dream-research-{_digest(event_ref)}.json"
        )
        created_at = _utcnow()
        dream_proposal_id = requested_dream_proposal_id or f"genesis-dream-research::{_digest('|'.join([event_ref, target_ref, created_at]))}"
        linked_self_repair_proposal_id = _safe_ref(payload.get("linked_self_repair_proposal_id"))
        if linked_self_repair_proposal_id:
            self_repair_candidate = self.self_repair.proposal_by_id(linked_self_repair_proposal_id)
        else:
            self_repair_candidate = self.self_repair.propose_from_event(
                {
                    "session_id": session_id,
                    "event_ref": event_ref,
                    "target_ref": target_ref,
                    "repair_objective": f"dream-research::{_digest(dream_objective)}",
                }
            )
        shared_event_spine = self.event_spine.publish_event(
            event_type="genesis.dream_research.proposal",
            source_surface_id=GENESIS_DREAM_RESEARCH_SURFACE_ID,
            correlation_ref=dream_proposal_id,
            session_ref_digest=event.get("session_ref_digest") or session_ref_digest,
            source_hive_run_ref=event.get("source_hive_run_ref"),
            heartbeat_record_id=event.get("heartbeat_record_id"),
            privacy_label="sanitized-genesis-dream-research-proposal",
            artifact_refs=[
                event_ref,
                dream_proposal_id,
                self_repair_candidate.get("proposal_id"),
                target_ref,
                *research_refs,
            ],
            planes=["dream", "research", "self_repair", "critique", "governance"],
            priority_trails=[
                {
                    "topic": "genesis-dream-research",
                    "strength": 1.0,
                    "artifact_ref": event_ref,
                }
            ],
        )
        record = {
            "schema_version": "nexusnet-genesis-dream-research-proposal-v1",
            "surface_id": "genesis-dream-research-proposal",
            "dream_proposal_id": dream_proposal_id,
            "status": "dream-proposal",
            "proposal_origin": proposal_origin,
            "session_ref_digest": event.get("session_ref_digest") or session_ref_digest,
            "source_event_ref": event_ref,
            "source_event_type": str(event.get("event_type") or "unknown"),
            "source_event_correlation_ref": event.get("correlation_ref"),
            "dream_packet": {
                "schema_version": "nexusnet-genesis-dream-packet-v1",
                "surface_id": "genesis-dream-packet",
                "dream_temperature": 0.95,
                "dream_mode": "failure-prior-conditioned-self-repair",
                "dream_objective_ref": f"dream-objective::{_digest(dream_objective)}",
                "source_event_ref": event_ref,
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            },
            "critique_packet": {
                "schema_version": "nexusnet-genesis-dream-critique-packet-v1",
                "surface_id": "genesis-dream-critique-packet",
                "critic_temperature": 0.2,
                "review_state": "required-before-any-promotion",
                "review_axes": ["canon-fit", "safety", "testability", "rollback"],
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            },
            "research_packet": {
                "schema_version": "nexusnet-genesis-dream-research-packet-v1",
                "surface_id": "genesis-dream-research-packet",
                "research_refs": research_refs,
                "research_ref_count": len(research_refs),
                "source_event_ref": event_ref,
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            },
            "linked_self_repair_proposal_id": self_repair_candidate.get("proposal_id"),
            "self_repair_candidate": self_repair_candidate,
            "shared_event_spine": shared_event_spine,
            "created_at": created_at,
            "promotion_allowed": False,
            "sandbox_eval_required": True,
            "admin_approval_required": True,
            "rollback_required": True,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "evidence_refs": _sanitize_refs(
                [
                    dream_proposal_id,
                    event_ref,
                    self_repair_candidate.get("proposal_id"),
                    shared_event_spine.get("event_ref"),
                    *research_refs,
                ]
            ),
        }
        record["federated_outcome_packet"] = self._record_federated_outcome(
            outcome_type="dream_research_proposed",
            session_id=session_id,
            session_ref_digest=record.get("session_ref_digest"),
            source_event_ref=record.get("source_event_ref"),
            source_event_type=record.get("source_event_type"),
            linked_self_repair_proposal_id=record.get("linked_self_repair_proposal_id"),
            dream_proposal_id=dream_proposal_id,
            evidence_refs=record.get("evidence_refs"),
        )
        self._append_jsonl(self.proposals_path, record)
        return record

    def propose_from_degraded_heartbeat(
        self,
        *,
        session_id: str | None,
        heartbeat_record: dict[str, Any],
    ) -> dict[str, Any]:
        """Create one replay-safe dream/research proposal from a degraded heartbeat only."""
        if not isinstance(heartbeat_record, dict):
            return _automatic_observation("not-eligible", reason="missing-heartbeat-record")
        if heartbeat_record.get("status") != "degraded":
            return _automatic_observation("not-eligible", reason="heartbeat-not-degraded")
        if heartbeat_record.get("raw_content_included") is not False:
            return _automatic_observation("not-eligible", reason="heartbeat-not-sanitized")
        if heartbeat_record.get("active_production_mutation_allowed") is not False:
            return _automatic_observation("not-eligible", reason="heartbeat-allows-production-mutation")
        if heartbeat_record.get("active_production_mutated") is not False:
            return _automatic_observation("not-eligible", reason="heartbeat-mutated-production")

        shared_event = heartbeat_record.get("shared_event_spine")
        event_ref = _safe_ref(shared_event.get("event_ref") if isinstance(shared_event, dict) else None)
        if not event_ref:
            return _automatic_observation("not-eligible", reason="missing-heartbeat-event-ref")
        event = self._find_event(event_ref=event_ref, session_id=session_id)
        if event.get("event_type") != "genesis.heartbeat.recorded":
            return _automatic_observation("not-eligible", reason="unexpected-heartbeat-event-type")
        if str(event.get("heartbeat_record_id") or "") != str(heartbeat_record.get("record_id") or ""):
            return _automatic_observation("not-eligible", reason="heartbeat-event-mismatch")

        self_repair_candidate = self.self_repair.propose_from_degraded_heartbeat(
            session_id=session_id,
            heartbeat_record=heartbeat_record,
        )
        if self_repair_candidate.get("status") not in {"proposal", "proposal-replayed"}:
            return _automatic_observation("not-eligible", reason="self-repair-proposal-not-available")
        event_digest = _digest(event_ref)
        return self.propose_from_event(
            {
                "session_id": session_id or "",
                "event_ref": event_ref,
                "target_ref": f"genesis/safe-files/self-repair/automatic-dream-research-{event_digest}.json",
                "dream_objective": "research a governed response to the sanitized degraded runtime heartbeat",
                "research_refs": [
                    "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
                    "docs/superpowers/specs/2026-07-05-nexusnet-genesis-build-order-design.md",
                ],
                "dream_proposal_id": f"genesis-dream-research::automatic-degraded-heartbeat::{event_digest}",
                "proposal_origin": "automatic-degraded-heartbeat",
                "linked_self_repair_proposal_id": self_repair_candidate.get("proposal_id"),
            }
        )

    def _record_federated_outcome(self, **payload: Any) -> dict[str, Any]:
        if not hasattr(self.federated_outcomes, "record_outcome"):
            return {
                "schema_version": "nexusnet-genesis-federated-outcome-packet-v1",
                "surface_id": "genesis-federated-outcome-packet",
                "status": "not-configured",
                "raw_content_included": False,
                "contains_personal_data": False,
                "active_production_mutation_allowed": False,
            }
        return self.federated_outcomes.record_outcome(
            source_surface_id=GENESIS_DREAM_RESEARCH_SURFACE_ID,
            status="dream-research-outcome-recorded",
            **payload,
        )

    def _find_event(self, *, event_ref: str, session_id: str | None = None) -> dict[str, Any]:
        summary = self.event_spine.summary(session_id=session_id, limit=500)
        for event in summary.get("events") or []:
            if str(event.get("event_ref") or "") == event_ref:
                if event.get("raw_content_included") is not False:
                    raise ValueError("source event must be sanitized")
                if event.get("active_production_mutation_allowed") is not False:
                    raise ValueError("source event must not allow production mutation")
                return event
        raise KeyError(event_ref)

    def _scoped(self, records: list[dict[str, Any]], session_ref_digest: str | None) -> list[dict[str, Any]]:
        if not session_ref_digest:
            return records
        return [
            record
            for record in records
            if str(record.get("session_ref_digest") or "") == session_ref_digest
        ]

    def _append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        records: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                records.append(item)
        return records


def _sanitize_refs(value: Any) -> list[str]:
    if isinstance(value, str):
        candidates = [value]
    elif isinstance(value, list):
        candidates = value
    else:
        candidates = []
    seen: set[str] = set()
    result: list[str] = []
    for item in candidates:
        ref = _safe_ref(item)
        if ref and ref not in seen:
            seen.add(ref)
            result.append(ref)
    return result


def _proposal_origin(value: Any) -> str:
    origin = str(value or "manual-event").strip().lower()
    if origin not in {"automatic-degraded-heartbeat", "manual-event"}:
        return "manual-event"
    return origin


def _automatic_observation(status: str, *, reason: str) -> dict[str, Any]:
    return {
        "surface_id": "genesis-dream-research-automatic-observation",
        "status": status,
        "reason": reason,
        "dream_proposal_id": None,
        "promotion_allowed": False,
        "sandbox_eval_required": True,
        "admin_approval_required": True,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def _safe_ref(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    normalized = text.lower()
    if (
        not text
        or ".." in text
        or ":\\" in text
        or "secret" in normalized
        or "token" in normalized
        or "password" in normalized
        or "api-key" in normalized
        or "apikey" in normalized
        or "runtime/test-fixtures" in normalized
    ):
        return ""
    return text[:220]


def _privacy_digest(value: str | None) -> str:
    return "sha256:" + hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
