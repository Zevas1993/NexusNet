from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .event_spine import GenesisEventSpineService


GENESIS_FEDERATED_OUTCOMES_SCHEMA = "nexusnet-genesis-federated-outcomes-v1"
GENESIS_FEDERATED_OUTCOME_PACKET_SCHEMA = "nexusnet-genesis-federated-outcome-packet-v1"
GENESIS_FEDERATED_OUTCOMES_SURFACE_ID = "genesis-federated-outcome-packets"
GENESIS_FEDERATED_OUTCOME_PACKET_SURFACE_ID = "genesis-federated-outcome-packet"
GENESIS_FEDERATED_OUTCOMES_REF = "genesis/federated-outcomes/packets.jsonl"


class GenesisFederatedOutcomeService:
    """Sanitized federated packets for Genesis dream and self-repair outcomes."""

    def __init__(
        self,
        *,
        artifacts_dir: Path | str,
        project_root: Path | str,
        event_spine: GenesisEventSpineService,
        global_growth: Any | None = None,
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.project_root = Path(project_root)
        self.event_spine = event_spine
        self.global_growth = global_growth
        self.outcome_dir = self.artifacts_dir / "genesis" / "federated-outcomes"
        self.packets_path = self.outcome_dir / "packets.jsonl"

    def record_outcome(
        self,
        *,
        outcome_type: str,
        source_surface_id: str,
        source_event_ref: str | None = None,
        source_event_type: str | None = None,
        session_id: str | None = None,
        session_ref_digest: str | None = None,
        linked_self_repair_proposal_id: str | None = None,
        dream_proposal_id: str | None = None,
        sandbox_eval_run_id: str | None = None,
        apply_id: str | None = None,
        rollback_id: str | None = None,
        evidence_refs: list[str | None] | None = None,
        status: str = "recorded",
    ) -> dict[str, Any]:
        scoped_digest = session_ref_digest or (_privacy_digest(session_id) if session_id else None)
        created_at = _utcnow()
        seed = json.dumps(
            {
                "outcome_type": outcome_type,
                "source_surface_id": source_surface_id,
                "source_event_ref": source_event_ref,
                "linked_self_repair_proposal_id": linked_self_repair_proposal_id,
                "dream_proposal_id": dream_proposal_id,
                "sandbox_eval_run_id": sandbox_eval_run_id,
                "apply_id": apply_id,
                "rollback_id": rollback_id,
                "session_ref_digest": scoped_digest,
                "created_at": created_at,
            },
            sort_keys=True,
        )
        packet_id = f"genesis-fed-outcome::{_digest(seed)}"
        safe_evidence_refs = _sanitize_refs(
            [
                source_event_ref,
                linked_self_repair_proposal_id,
                dream_proposal_id,
                sandbox_eval_run_id,
                apply_id,
                rollback_id,
                *(evidence_refs or []),
            ]
        )
        growth_receipt = self._record_growth(
            user_key=session_id or scoped_digest or packet_id,
            outcome_type=outcome_type,
            packet_id=packet_id,
            source_event_ref=source_event_ref,
            linked_self_repair_proposal_id=linked_self_repair_proposal_id,
            dream_proposal_id=dream_proposal_id,
            sandbox_eval_run_id=sandbox_eval_run_id,
            apply_id=apply_id,
            rollback_id=rollback_id,
        )
        federated_packet = (
            growth_receipt.get("federated_packet")
            if isinstance(growth_receipt.get("federated_packet"), dict)
            else {}
        )
        global_growth_impact = (
            growth_receipt.get("global_growth")
            if isinstance(growth_receipt.get("global_growth"), dict)
            else self._growth_status()
        )
        shared_event_spine = self.event_spine.publish_event(
            event_type="genesis.federated_outcome.packet",
            source_surface_id=GENESIS_FEDERATED_OUTCOMES_SURFACE_ID,
            correlation_ref=packet_id,
            session_ref_digest=scoped_digest,
            privacy_label="sanitized-genesis-federated-outcome-packet",
            artifact_refs=[
                packet_id,
                source_event_ref,
                linked_self_repair_proposal_id,
                dream_proposal_id,
                sandbox_eval_run_id,
                apply_id,
                rollback_id,
                federated_packet.get("packet_id") if isinstance(federated_packet, dict) else None,
                *safe_evidence_refs,
            ],
            planes=["federation", "growth", "dream", "self_repair", "governance"],
            priority_trails=[
                {
                    "topic": "genesis-federated-outcome",
                    "strength": 1.0,
                    "artifact_ref": packet_id,
                }
            ],
        )
        packet = {
            "schema_version": GENESIS_FEDERATED_OUTCOME_PACKET_SCHEMA,
            "surface_id": GENESIS_FEDERATED_OUTCOME_PACKET_SURFACE_ID,
            "packet_id": packet_id,
            "status": status,
            "outcome_type": str(outcome_type or "unknown"),
            "source_surface_id": _safe_ref(source_surface_id),
            "source_event_ref": _safe_ref(source_event_ref),
            "source_event_type": _safe_ref(source_event_type),
            "session_ref_digest": scoped_digest,
            "linked_self_repair_proposal_id": _safe_ref(linked_self_repair_proposal_id),
            "dream_proposal_id": _safe_ref(dream_proposal_id),
            "sandbox_eval_run_id": _safe_ref(sandbox_eval_run_id),
            "apply_id": _safe_ref(apply_id),
            "rollback_id": _safe_ref(rollback_id),
            "federated_packet": federated_packet,
            "global_growth_impact": global_growth_impact,
            "per_user_global_learning_state": {
                "schema_version": "nexusnet-genesis-federated-outcome-growth-state-v1",
                "surface_id": "genesis-federated-outcome-growth-state",
                "session_ref_digest": scoped_digest,
                "runtime_growth_captured": bool(growth_receipt),
                "global_federated_packet_captured": bool(federated_packet.get("packet_id")),
                "global_growth_receipt_id": growth_receipt.get("receipt_id"),
                "global_growth_user_ref": growth_receipt.get("user_ref"),
                "federated_packet_id": federated_packet.get("packet_id"),
                "raw_content_included": False,
                "contains_personal_data": False,
                "active_production_mutation_allowed": False,
            },
            "shared_event_spine": shared_event_spine,
            "created_at": created_at,
            "evidence_refs": _sanitize_refs(
                [
                    GENESIS_FEDERATED_OUTCOMES_REF,
                    packet_id,
                    source_event_ref,
                    linked_self_repair_proposal_id,
                    dream_proposal_id,
                    sandbox_eval_run_id,
                    apply_id,
                    rollback_id,
                    federated_packet.get("packet_id"),
                    shared_event_spine.get("event_ref"),
                    *safe_evidence_refs,
                ]
            ),
            "privacy_boundary": (
                "sanitized-genesis-federated-outcome-ids-digests-statuses-and-growth-packet-refs-only-"
                "no-prompts-outputs-session-ids-admin-identities-local-paths-or-raw-content"
            ),
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "mutates_production": False,
            "raw_content_included": False,
            "contains_personal_data": False,
        }
        self._append_jsonl(self.packets_path, packet)
        return packet

    def summary(self, session_id: str | None = None, *, limit: int = 100) -> dict[str, Any]:
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        packets = self._scoped(self._read_jsonl(self.packets_path), session_ref_digest)
        latest = packets[-1] if packets else {}
        shared_summary = self.event_spine.summary(session_ref_digest=session_ref_digest, limit=limit)
        event_count = int(
            (shared_summary.get("event_type_counts") or {}).get("genesis.federated_outcome.packet", 0) or 0
        )
        return {
            "schema_version": GENESIS_FEDERATED_OUTCOMES_SCHEMA,
            "surface_id": GENESIS_FEDERATED_OUTCOMES_SURFACE_ID,
            "status": "live-control-plane" if latest else "not-observed",
            "honest_status_label": (
                "genesis-federated-dream-self-repair-outcome-packets-live-control-plane"
                if latest
                else "genesis-federated-dream-self-repair-outcome-packets-not-observed"
            ),
            "authority": "NexusBrain",
            "source": "genesis-dream-research-and-self-repair-runtime-outcomes" if latest else None,
            "session_ref_digest": session_ref_digest,
            "packet_count": len(packets),
            "latest_packet_id": latest.get("packet_id"),
            "latest_packet": latest,
            "recent_packets": list(reversed(packets[-20:])),
            "global_growth_impact": latest.get("global_growth_impact") if latest else self._growth_status(),
            "per_user_global_learning_state": latest.get("per_user_global_learning_state") if latest else {},
            "shared_event_spine": {
                "schema_version": "nexusnet-genesis-federated-outcomes-shared-event-spine-v1",
                "surface_id": "genesis-federated-outcomes-shared-event-spine",
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
            "governance": {
                "records_real_runtime_outcomes": bool(latest),
                "links_to_multi_user_growth": True,
                "links_to_runtime_federated_learning_packets": True,
                "dream_outputs_shadow_only": True,
                "self_repair_requires_sandbox_admin_apply_rollback": True,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
                "raw_content_included": False,
            },
            "evidence_refs": _sanitize_refs(
                [
                    GENESIS_FEDERATED_OUTCOMES_REF,
                    latest.get("packet_id"),
                    latest.get("source_event_ref"),
                    latest.get("linked_self_repair_proposal_id"),
                    latest.get("dream_proposal_id"),
                    latest.get("sandbox_eval_run_id"),
                    latest.get("apply_id"),
                    latest.get("rollback_id"),
                    latest.get("federated_packet", {}).get("packet_id")
                    if isinstance(latest.get("federated_packet"), dict)
                    else None,
                    latest.get("shared_event_spine", {}).get("event_ref")
                    if isinstance(latest.get("shared_event_spine"), dict)
                    else None,
                ]
            ),
            "raw_content_included": False,
            "contains_personal_data": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-genesis-federated-outcome-counts-ids-digests-growth-status-and-packet-refs-only-"
                "no-prompts-outputs-session-ids-admin-identities-local-paths-or-raw-content"
            ),
            "mutation_boundary": "append-only-outcome-packets-plus-growth-receipts-no-production-mutation",
        }

    def _record_growth(
        self,
        *,
        user_key: str,
        outcome_type: str,
        packet_id: str,
        source_event_ref: str | None = None,
        linked_self_repair_proposal_id: str | None = None,
        dream_proposal_id: str | None = None,
        sandbox_eval_run_id: str | None = None,
        apply_id: str | None = None,
        rollback_id: str | None = None,
    ) -> dict[str, Any]:
        if not hasattr(self.global_growth, "record_runtime_interaction"):
            return {}
        sandbox_result = (
            "passed"
            if outcome_type in {"self_repair_sandbox_eval_passed", "self_repair_applied", "self_repair_rolled_back"}
            else "not-run"
        )
        return self.global_growth.record_runtime_interaction(
            user_id=user_key,
            source_model="genesis-dream-self-repair",
            expert_node="expert.genesis_self_repair",
            task_family="genesis-federated-outcome",
            route_geometry="|".join(
                _sanitize_refs(
                    [
                        source_event_ref,
                        linked_self_repair_proposal_id,
                        dream_proposal_id,
                        sandbox_eval_run_id,
                        apply_id,
                        rollback_id,
                        outcome_type,
                    ]
                )
            ),
            selected_node_ids=[
                "GenesisDreamResearchService",
                "GenesisSelfRepairService",
                "GenesisFederatedOutcomeService",
            ],
            confidence=1.0,
            eval_scores={"quality": 1.0, "safety": 1.0, "governance": 1.0},
            failure_class="none",
            policy_block_class="none",
            runtime_class="genesis-governed-shadow",
            hardware_class="local-runtime",
            sandbox_result=sandbox_result,
            dream_candidate_outcome=outcome_type,
            quality=1.0,
            knowledge_ref=(
                _safe_ref(linked_self_repair_proposal_id)
                or _safe_ref(dream_proposal_id)
                or _safe_ref(source_event_ref)
                or packet_id
            ),
            packet_id=f"genesis-fed::{_digest(packet_id)}",
            metadata={
                "source": GENESIS_FEDERATED_OUTCOMES_SURFACE_ID,
                "outcome_type": outcome_type,
                "source_event_ref": _safe_ref(source_event_ref),
                "linked_self_repair_proposal_id": _safe_ref(linked_self_repair_proposal_id),
                "dream_proposal_id": _safe_ref(dream_proposal_id),
                "sandbox_eval_run_id": _safe_ref(sandbox_eval_run_id),
                "apply_id": _safe_ref(apply_id),
                "rollback_id": _safe_ref(rollback_id),
                "raw_content_included": False,
            },
        )

    def _growth_status(self) -> dict[str, Any]:
        if hasattr(self.global_growth, "growth_status"):
            status = self.global_growth.growth_status(include_latest_receipt=False)
            if isinstance(status, dict):
                return status
        return {
            "schema_version": "nexusnet-genesis-federated-outcome-growth-impact-v1",
            "surface_id": "genesis-federated-outcome-growth-impact",
            "global_captures": 0,
            "runtime_interaction_count": 0,
            "runtime_receipt_count": 0,
            "federation_ready": False,
            "raw_content_included": False,
            "contains_personal_data": False,
            "active_production_mutation_allowed": False,
        }

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
