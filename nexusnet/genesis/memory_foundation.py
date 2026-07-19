from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .event_spine import GenesisEventSpineService


class GenesisMemoryFoundationService:
    """Governed Layer 7 canon memory, graph, retrieval, and replay store."""

    def __init__(
        self,
        *,
        artifacts_dir: Path | str,
        event_spine: GenesisEventSpineService,
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.event_spine = event_spine
        self.root = self.artifacts_dir / "genesis" / "memory-foundation"
        self.records_dir = self.root / "records"
        self.content_dir = self.root / "content"
        self.states_dir = self.root / "states"
        self.commits_dir = self.root / "commits"
        self.rollbacks_dir = self.root / "rollbacks"
        self.evolutions_dir = self.root / "evolutions"
        self.evolution_content_dir = self.root / "evolution-content"
        self.retrieval_dir = self.root / "retrieval"
        self.graph_dir = self.root / "graph"
        self.passports_dir = self.root / "passports"
        self.user_index_dir = self.root / "indexes" / "users"
        self.global_index_path = self.root / "indexes" / "global.json"

    def bind_runtime_services(
        self,
        *,
        retrieval_service: Any,
        memory_service: Any,
        graph_ingestion: Any,
        global_growth: Any,
        memory_admission: Any,
    ) -> dict[str, Any]:
        self.runtime_retrieval = retrieval_service
        self.runtime_memory = memory_service
        self.runtime_graph_ingestion = graph_ingestion
        self.global_growth = global_growth
        self.memory_admission = memory_admission
        growth_receipts = [
            receipt
            for commit in self._artifacts(self.commits_dir)
            for receipt in (
                ((commit.get("runtime_activation") or {}).get("global_growth") or {}).get("receipts")
                or []
            )
            if isinstance(receipt, dict)
        ]
        growth_replay = global_growth.restore_runtime_receipts(growth_receipts)
        passivation_records = [
            record
            for artifact in [
                *self._artifacts(self.rollbacks_dir),
                *self._artifacts(self.evolutions_dir),
            ]
            if isinstance(
                record := (
                    ((artifact.get("runtime_deactivation") or {}).get("global_growth") or {}).get(
                        "passivation_record"
                    )
                ),
                dict,
            )
        ]
        passivation_replay = global_growth.restore_passivation_records(passivation_records)
        return {
            "surface_id": "genesis-memory-foundation-runtime-binding",
            "status": "bound",
            "growth_replay": growth_replay,
            "passivation_replay": passivation_replay,
            "raw_content_included": False,
        }

    def commit(
        self,
        *,
        application: dict[str, Any],
        gate: dict[str, Any],
        decisions: list[dict[str, Any]],
        source_content_by_decision_id: dict[str, str],
        governance_commit_ref: str,
        admin_commit_ref: str,
        admin_actor_digest: str,
    ) -> dict[str, Any]:
        self._validate_commit_inputs(
            application=application,
            gate=gate,
            decisions=decisions,
            source_content_by_decision_id=source_content_by_decision_id,
            governance_commit_ref=governance_commit_ref,
            admin_commit_ref=admin_commit_ref,
        )
        application_id = str(application["application_id"])
        existing = self._commit_for_application(application_id)
        if existing and existing.get("status") == "canonical-memory-committed":
            return existing

        created_at = _utcnow()
        content_refs = sorted(str(decision.get("content_ref") or "") for decision in decisions)
        commit_id = f"genesis-memory-commit::{_digest('|'.join([application_id, *content_refs]))}"
        commit_ref = f"genesis/memory-foundation/commits/{_artifact_id(commit_id)}.json"
        records: list[dict[str, Any]] = []
        graph_node_count = 0
        graph_edge_count = 0

        for decision in decisions:
            decision_id = str(decision["decision_id"])
            content = source_content_by_decision_id[decision_id]
            content_ref = str(decision["content_ref"])
            memory_id = f"genesis-memory::{_digest('|'.join([application_id, decision_id, content_ref]))}"
            memory_ref = f"genesis/memory-foundation/records/{_artifact_id(memory_id)}.json"
            content_artifact_ref = f"genesis/memory-foundation/content/{_artifact_id(memory_id)}.txt"
            retrieval_packet_ref = f"genesis/memory-foundation/retrieval/{_artifact_id(memory_id)}.json"
            graph_ref = f"genesis/memory-foundation/graph/{_artifact_id(memory_id)}.json"
            source_ref = str(decision.get("source_ref") or f"decision-source::{_digest(decision_id)}")
            graph = _graph_projection(
                memory_id=memory_id,
                decision_id=decision_id,
                source_ref=source_ref,
                content_ref=content_ref,
                graph_ref=graph_ref,
            )
            graph_node_count += len(graph["nodes"])
            graph_edge_count += len(graph["edges"])
            retrieval_packet = {
                "schema_version": "nexusnet-genesis-source-grounded-retrieval-packet-v1",
                "surface_id": "genesis-source-grounded-retrieval-packet",
                "memory_id": memory_id,
                "memory_ref": memory_ref,
                "source_ref": source_ref,
                "source_kind": decision.get("source_kind"),
                "content_ref": content_ref,
                "content_artifact_ref": content_artifact_ref,
                "graph_refs": [graph_ref, *[node["node_id"] for node in graph["nodes"]]],
                "admission_decision_id": decision_id,
                "operation_receipt_id": decision.get("operation_receipt_id"),
                "evidence_checkpoint_id": decision.get("evidence_checkpoint_id"),
                "contradiction_state": "not-observed",
                "stale_state": "current",
                "temporal_metadata": {"valid_from": created_at, "valid_until": None},
                "raw_source_fallback": {
                    "allowed": True,
                    "content_artifact_ref": content_artifact_ref,
                    "source_ref": source_ref,
                },
                "raw_content_included": False,
            }
            record = {
                "schema_version": "nexusnet-genesis-canon-memory-record-v1",
                "surface_id": "genesis-canon-memory-record",
                "memory_id": memory_id,
                "memory_ref": memory_ref,
                "application_id": application_id,
                "commit_id": commit_id,
                "session_ref_digest": gate.get("session_ref_digest"),
                "admission_decision_id": decision_id,
                "source_ref": source_ref,
                "source_kind": decision.get("source_kind"),
                "content_ref": content_ref,
                "content_artifact_ref": content_artifact_ref,
                "retrieval_packet_ref": retrieval_packet_ref,
                "graph_refs": retrieval_packet["graph_refs"],
                "operation_receipt_id": decision.get("operation_receipt_id"),
                "operation_content_ref": decision.get("operation_content_ref"),
                "evidence_checkpoint_id": decision.get("evidence_checkpoint_id"),
                "privacy_class": decision.get("privacy_class"),
                "consent_status": decision.get("consent_status"),
                "rights_license_status": decision.get("rights_license_status"),
                "contradiction_state": "not-observed",
                "contradiction_refs": [],
                "stale_state": "current",
                "temporal_metadata": {"created_at": created_at, "last_verified_at": created_at},
                "created_at": created_at,
                "raw_content_included": False,
            }
            self._write_text(content, artifact_ref=content_artifact_ref)
            self._write_json(graph, artifact_ref=graph_ref)
            self._write_json(retrieval_packet, artifact_ref=retrieval_packet_ref)
            self._write_json(record, artifact_ref=memory_ref)
            self._write_state(memory_id=memory_id, application_id=application_id, state="active", at=created_at)
            records.append(record)

        try:
            runtime_activation = self._activate_runtime_records(records)
        except Exception as exc:
            failed_reason_ref = f"runtime-activation-failed::{_digest(type(exc).__name__)}"
            for record in records:
                self._write_state(
                    memory_id=str(record["memory_id"]),
                    application_id=application_id,
                    state="revoked",
                    at=_utcnow(),
                    reason_ref=failed_reason_ref,
                )
            self._rebuild_indexes()
            raise ValueError("canonical memory runtime activation failed and was compensated") from exc

        passport_ref = f"genesis/memory-foundation/passports/{_artifact_id(commit_id)}.json"
        passport = {
            "schema_version": "nexusnet-memory-evolution-passport-v1",
            "surface_id": "MemoryEvolutionPassport",
            "passport_id": f"memory-evolution-passport::{_digest(commit_id)}",
            "passport_ref": passport_ref,
            "application_id": application_id,
            "commit_id": commit_id,
            "memory_refs": [record["memory_ref"] for record in records],
            "source_refs": [record["source_ref"] for record in records],
            "admission_decision_refs": [record["admission_decision_id"] for record in records],
            "lifecycle": [{"state": "canonical-memory-committed", "at": created_at, "ref": commit_ref}],
            "current_state": "active",
            "raw_content_included": False,
        }
        self._write_json(passport, artifact_ref=passport_ref)
        self._rebuild_indexes()
        per_user_state = self._growth_state(session_ref_digest=str(gate.get("session_ref_digest") or ""))
        global_state = self._growth_state(session_ref_digest=None)
        shared_event = self.event_spine.publish_event(
            event_type="genesis.memory.foundation.committed",
            source_surface_id="genesis-memory-foundation",
            correlation_ref=commit_id,
            session_ref_digest=gate.get("session_ref_digest"),
            privacy_label="sanitized-genesis-memory-foundation-commit",
            artifact_refs=[
                commit_ref,
                passport_ref,
                application_id,
                *[record["memory_ref"] for record in records],
                *[record["retrieval_packet_ref"] for record in records],
            ],
            planes=["memory", "retrieval", "graph", "growth", "governance"],
            priority_trails=[{"topic": "genesis-memory-foundation", "strength": 1.0, "artifact_ref": commit_id}],
            created_at=created_at,
        )
        packet = {
            "schema_version": "nexusnet-genesis-memory-foundation-commit-v1",
            "surface_id": "genesis-memory-foundation-commit",
            "commit_id": commit_id,
            "commit_ref": commit_ref,
            "application_id": application_id,
            "gate_id": gate.get("gate_id"),
            "status": "canonical-memory-committed",
            "honest_status_label": "genesis-layer7-memory-foundation-commit-applied",
            "memory_record_count": len(records),
            "memory_refs": [record["memory_ref"] for record in records],
            "retrieval_packet_count": len(records),
            "retrieval_packet_refs": [record["retrieval_packet_ref"] for record in records],
            "graph_node_count": graph_node_count,
            "graph_edge_count": graph_edge_count,
            "graph_refs": _unique(ref for record in records for ref in record["graph_refs"]),
            "memory_evolution_passport_ref": passport_ref,
            "operation_receipt_refs": _unique(record.get("operation_receipt_id") for record in records),
            "evidence_checkpoint_refs": _unique(record.get("evidence_checkpoint_id") for record in records),
            "governance_commit_ref": governance_commit_ref,
            "admin_commit_ref": admin_commit_ref,
            "admin_actor_digest": admin_actor_digest,
            "per_user_growth_state": per_user_state,
            "global_growth_state": global_state,
            "runtime_activation": runtime_activation,
            "shared_event_spine": shared_event,
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": True,
            "active_production_mutated": True,
            "privacy_boundary": "public-rights-approved-source-content-separated-from-sanitized-control-evidence",
            "mutation_boundary": "governed-layer7-memory-retrieval-graph-index-write-only",
        }
        self._write_json(packet, artifact_ref=commit_ref)
        return packet

    def rollback_application(self, *, application_id: str, reason_ref: str) -> dict[str, Any] | None:
        commit = self._commit_for_application(application_id)
        if not commit or commit.get("status") != "canonical-memory-committed":
            return None
        active_records = [
            record
            for record in self._records()
            if record.get("application_id") == application_id and self._record_state(record) == "active"
        ]
        rolled_back_at = _utcnow()
        rollback_id = f"genesis-memory-foundation-rollback::{_digest('|'.join([application_id, rolled_back_at]))}"
        rollback_ref = f"genesis/memory-foundation/rollbacks/{_artifact_id(rollback_id)}.json"
        growth_receipts = (
            ((commit.get("runtime_activation") or {}).get("global_growth") or {}).get("receipts")
            or []
        )
        runtime_deactivation = self._deactivate_runtime_records(
            active_records,
            reason_ref=reason_ref,
            growth_receipts=[receipt for receipt in growth_receipts if isinstance(receipt, dict)],
        )
        for record in active_records:
            self._write_state(
                memory_id=str(record["memory_id"]),
                application_id=application_id,
                state="revoked",
                at=rolled_back_at,
                reason_ref=reason_ref,
            )
        self._rebuild_indexes()
        passport_ref = str(commit.get("memory_evolution_passport_ref") or "")
        passport = self._read_artifact(passport_ref)
        if passport:
            passport["current_state"] = "revoked"
            passport.setdefault("lifecycle", []).append(
                {"state": "canonical-memory-reverted", "at": rolled_back_at, "ref": rollback_ref}
            )
            self._write_json(passport, artifact_ref=passport_ref)
        packet = {
            "schema_version": "nexusnet-genesis-memory-foundation-rollback-v1",
            "surface_id": "genesis-memory-foundation-rollback",
            "rollback_id": rollback_id,
            "rollback_ref": rollback_ref,
            "application_id": application_id,
            "commit_id": commit.get("commit_id"),
            "status": "rollback-recorded",
            "rollback_state": "canonical-memory-reverted",
            "reverted_memory_count": len(active_records),
            "reverted_memory_refs": [record.get("memory_ref") for record in active_records],
            "memory_evolution_passport_ref": passport_ref or None,
            "reason_ref": reason_ref,
            "rolled_back_at": rolled_back_at,
            "global_growth_state": self._growth_state(session_ref_digest=None),
            "runtime_deactivation": runtime_deactivation,
            "raw_content_included": False,
            "active_production_mutation_allowed": True,
            "active_production_mutated": bool(active_records),
            "mutation_boundary": "governed-layer7-index-tombstone-no-audit-evidence-deletion",
        }
        self._write_json(packet, artifact_ref=rollback_ref)
        return packet

    def refresh_source(
        self,
        *,
        memory_id: str,
        session_id: str,
        refreshed_content: str,
        source_refresh_ref: str,
        classification: str = "stale",
        contradiction_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        memory_id = str(memory_id or "").strip()
        session_id = str(session_id or "").strip()
        refreshed_content = str(refreshed_content or "")
        source_refresh_ref = _safe_ref(source_refresh_ref)
        classification = str(classification or "stale").strip().lower()
        safe_contradiction_refs = _safe_refs(contradiction_refs or [])
        if not memory_id or not session_id or not refreshed_content.strip() or not source_refresh_ref:
            raise ValueError("memory_id, session_id, refreshed_content, and source_refresh_ref are required")
        if classification not in {"stale", "contradictory"}:
            raise ValueError("classification must be stale or contradictory")
        if classification == "contradictory" and not safe_contradiction_refs:
            raise ValueError("contradiction_refs are required for contradictory source refreshes")

        record = next((item for item in self._records() if item.get("memory_id") == memory_id), None)
        if record is None:
            raise KeyError(f"unknown canonical memory: {memory_id}")
        if record.get("session_ref_digest") != _privacy_digest(session_id):
            raise ValueError("session does not own the canonical memory record")
        refreshed_content_ref = f"sha256:{hashlib.sha256(refreshed_content.encode('utf-8')).hexdigest()}"
        content_changed = refreshed_content_ref != str(record.get("content_ref") or "")
        evolution_id = f"memory-evolution::{_digest('|'.join([memory_id, refreshed_content_ref, source_refresh_ref, classification]))}"
        evolution_ref = f"genesis/memory-foundation/evolutions/{_artifact_id(evolution_id)}.json"
        existing = self._read_artifact(evolution_ref)
        if existing:
            return existing
        if self._record_state(record) != "active":
            raise ValueError("only active canonical memory can be source-refreshed")

        observed_at = _utcnow()
        passport_ref = self._passport_ref_for_record(record)
        if not content_changed:
            packet = {
                "schema_version": "nexusnet-memory-evolution-event-v1",
                "surface_id": "MemoryEvolutionPassport",
                "evolution_id": evolution_id,
                "evolution_ref": evolution_ref,
                "memory_id": memory_id,
                "memory_ref": record.get("memory_ref"),
                "memory_evolution_passport_ref": passport_ref or None,
                "status": "verified-current",
                "honest_status_label": "genesis-layer7-memory-source-refresh-verified-current",
                "content_changed": False,
                "previous_content_ref": record.get("content_ref"),
                "refreshed_content_ref": refreshed_content_ref,
                "source_refresh_ref": source_refresh_ref,
                "stale_state": "current",
                "contradiction_state": "not-observed",
                "current_memory_state": "active",
                "recommit_required": False,
                "required_controls": [],
                "candidate_decision_ref": None,
                "observed_at": observed_at,
                "created_at": observed_at,
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
            self._append_passport_event(
                passport_ref=passport_ref,
                state="source-verified-current",
                at=observed_at,
                event_ref=evolution_ref,
                current_state="active",
            )
            self._write_json(packet, artifact_ref=evolution_ref)
            return packet

        state = "contradicted" if classification == "contradictory" else "stale"
        reason_ref = f"memory-evolution::{classification}::{_digest(source_refresh_ref)}"
        runtime_deactivation = self._deactivate_runtime_records(
            [record],
            reason_ref=reason_ref,
            growth_receipts=self._growth_receipts_for_record(record),
        )
        self._write_state(
            memory_id=memory_id,
            application_id=str(record.get("application_id") or ""),
            state=state,
            at=observed_at,
            reason_ref=reason_ref,
        )
        self._rebuild_indexes()
        refreshed_content_artifact_ref = (
            f"genesis/memory-foundation/evolution-content/{_artifact_id(evolution_id)}.txt"
        )
        self._write_text(refreshed_content, artifact_ref=refreshed_content_artifact_ref)
        admission = getattr(self, "memory_admission", None)
        if admission is None or not callable(getattr(admission, "record_manual_ingress", None)):
            raise RuntimeError("memory admission must be bound before source refresh")
        candidate = admission.record_manual_ingress(
            session_id=session_id,
            ingress_route="retrieval-document-ingest",
            content=refreshed_content,
            metadata={
                "source_ref": record.get("source_ref"),
                "source_kind": record.get("source_kind"),
                "privacy_class": record.get("privacy_class"),
                "consent_status": record.get("consent_status"),
                "rights_license_status": record.get("rights_license_status"),
            },
        )
        candidate_decision_ref = str(candidate.get("decision_id") or "")
        self._append_passport_event(
            passport_ref=passport_ref,
            state=f"source-{state}",
            at=observed_at,
            event_ref=evolution_ref,
            current_state=state,
        )
        shared_event = self.event_spine.publish_event(
            event_type="genesis.memory.foundation.evolved",
            source_surface_id="genesis-memory-foundation",
            correlation_ref=evolution_id,
            session_ref_digest=record.get("session_ref_digest"),
            privacy_label="sanitized-genesis-memory-foundation-evolution",
            artifact_refs=[
                evolution_ref,
                passport_ref,
                record.get("memory_ref"),
                candidate_decision_ref,
                source_refresh_ref,
                *safe_contradiction_refs,
            ],
            planes=["memory", "retrieval", "graph", "growth", "governance", "evolution"],
            priority_trails=[
                {"topic": "genesis-memory-evolution", "strength": 1.0, "artifact_ref": evolution_id}
            ],
            created_at=observed_at,
        )
        packet = {
            "schema_version": "nexusnet-memory-evolution-event-v1",
            "surface_id": "MemoryEvolutionPassport",
            "evolution_id": evolution_id,
            "evolution_ref": evolution_ref,
            "memory_id": memory_id,
            "memory_ref": record.get("memory_ref"),
            "memory_evolution_passport_ref": passport_ref or None,
            "status": "contradiction-passivated" if state == "contradicted" else "stale-memory-passivated",
            "honest_status_label": f"genesis-layer7-memory-source-refresh-{state}-passivated",
            "content_changed": True,
            "previous_content_ref": record.get("content_ref"),
            "refreshed_content_ref": refreshed_content_ref,
            "refreshed_content_artifact_ref": refreshed_content_artifact_ref,
            "source_refresh_ref": source_refresh_ref,
            "stale_state": "source-changed",
            "contradiction_state": "confirmed" if state == "contradicted" else "not-observed",
            "contradiction_refs": safe_contradiction_refs,
            "temporal_metadata": {
                "valid_from": (record.get("temporal_metadata") or {}).get("created_at"),
                "valid_until": observed_at,
                "last_verified_at": (record.get("temporal_metadata") or {}).get("last_verified_at"),
            },
            "current_memory_state": state,
            "recommit_required": True,
            "required_controls": [
                "held_out_eval",
                "closed_sandbox_eval",
                "artifact_trust",
                "rollback_proof",
                "governance_approval",
                "admin_approval",
            ],
            "candidate_decision_ref": candidate_decision_ref,
            "runtime_deactivation": runtime_deactivation,
            "shared_event_spine": shared_event,
            "observed_at": observed_at,
            "created_at": observed_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": True,
            "active_production_mutated": True,
            "mutation_boundary": "passivate-stale-memory-and-quarantine-refreshed-source-until-fresh-governed-commit",
        }
        self._write_json(packet, artifact_ref=evolution_ref)
        return packet

    def summary(self, *, session_ref_digest: str | None = None) -> dict[str, Any]:
        records = self._records()
        scoped = [record for record in records if not session_ref_digest or record.get("session_ref_digest") == session_ref_digest]
        active = [record for record in scoped if self._record_state(record) == "active"]
        revoked = [record for record in scoped if self._record_state(record) == "revoked"]
        stale = [record for record in scoped if self._record_state(record) == "stale"]
        contradicted = [record for record in scoped if self._record_state(record) == "contradicted"]
        commits = self._artifacts(self.commits_dir)
        rollbacks = self._artifacts(self.rollbacks_dir)
        evolutions = [
            item
            for item in self._artifacts(self.evolutions_dir)
            if not session_ref_digest
            or next(
                (
                    record.get("session_ref_digest") == session_ref_digest
                    for record in scoped
                    if record.get("memory_id") == item.get("memory_id")
                ),
                False,
            )
        ]
        latest_commit = _sanitized_commit(commits[0]) if commits else None
        latest_rollback = _sanitized_rollback(rollbacks[0]) if rollbacks else None
        latest_evolution = _sanitized_evolution(evolutions[0]) if evolutions else None
        if active and evolutions:
            status = "live-with-memory-evolution"
        elif active:
            status = "live"
        elif contradicted:
            status = "degraded-contradicted"
        elif stale:
            status = "degraded-stale"
        elif revoked:
            status = "degraded-revoked-only"
        else:
            status = "not-observed"
        return {
            "schema_version": "nexusnet-genesis-memory-foundation-status-v1",
            "surface_id": "genesis-memory-foundation",
            "status": status,
            "honest_status_label": (
                f"genesis-layer7-memory-foundation-{status}"
            ),
            "authority": "NexusBrain",
            "active_memory_count": len(active),
            "revoked_memory_count": len(revoked),
            "stale_memory_count": len(stale),
            "contradicted_memory_count": len(contradicted),
            "commit_count": len(commits),
            "rollback_count": len(rollbacks),
            "evolution_count": len(evolutions),
            "active_memory_refs": [record.get("memory_ref") for record in active],
            "latest_commit": latest_commit,
            "latest_rollback": latest_rollback,
            "latest_evolution": latest_evolution,
            "global_growth_state": self._growth_state(session_ref_digest=None),
            "per_user_growth_state": self._growth_state(session_ref_digest=session_ref_digest)
            if session_ref_digest
            else None,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def _growth_receipts_for_record(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        commit_id = str(record.get("commit_id") or "")
        commit = next(
            (item for item in self._artifacts(self.commits_dir) if item.get("commit_id") == commit_id),
            {},
        )
        receipts = [
            receipt
            for receipt in (
                ((commit.get("runtime_activation") or {}).get("global_growth") or {}).get("receipts")
                or []
            )
            if isinstance(receipt, dict)
        ]
        expected_packet_id = f"genesis-memory-growth::{_digest(str(record.get('memory_id') or ''))}"
        matched = [
            receipt
            for receipt in receipts
            if str((receipt.get("federated_packet") or {}).get("packet_id") or "") == expected_packet_id
        ]
        return matched or (receipts if len(receipts) == 1 else [])

    def _passport_ref_for_record(self, record: dict[str, Any]) -> str:
        commit_id = str(record.get("commit_id") or "")
        commit = next(
            (item for item in self._artifacts(self.commits_dir) if item.get("commit_id") == commit_id),
            {},
        )
        return str(commit.get("memory_evolution_passport_ref") or "")

    def _append_passport_event(
        self,
        *,
        passport_ref: str,
        state: str,
        at: str,
        event_ref: str,
        current_state: str,
    ) -> None:
        passport = self._read_artifact(passport_ref)
        if not passport:
            return
        passport["current_state"] = current_state
        passport.setdefault("lifecycle", []).append({"state": state, "at": at, "ref": event_ref})
        self._write_json(passport, artifact_ref=passport_ref)

    def query(self, *, query: str, session_ref_digest: str | None, limit: int = 10) -> dict[str, Any]:
        query_terms = _terms(query)
        hits: list[tuple[float, dict[str, Any]]] = []
        for record in self._records():
            if self._record_state(record) != "active":
                continue
            if session_ref_digest and record.get("session_ref_digest") != session_ref_digest:
                continue
            content = self._read_text(str(record.get("content_artifact_ref") or ""))
            if content is None:
                continue
            overlap = sum(_terms(content).count(term) for term in query_terms)
            if query_terms and overlap <= 0:
                continue
            score = float(overlap) / max(len(query_terms), 1) if query_terms else 1.0
            hits.append(
                (
                    score,
                    {
                        "memory_id": record.get("memory_id"),
                        "content": content,
                        "content_ref": record.get("content_ref"),
                        "source_ref": record.get("source_ref"),
                        "source_kind": record.get("source_kind"),
                        "score": round(score, 6),
                        "retrieval_packet_ref": record.get("retrieval_packet_ref"),
                        "graph_refs": record.get("graph_refs") or [],
                        "operation_receipt_id": record.get("operation_receipt_id"),
                        "evidence_checkpoint_id": record.get("evidence_checkpoint_id"),
                        "contradiction_state": record.get("contradiction_state"),
                        "stale_state": record.get("stale_state"),
                        "temporal_metadata": record.get("temporal_metadata") or {},
                        "raw_source_fallback": {
                            "allowed": True,
                            "source_ref": record.get("source_ref"),
                            "content_ref": record.get("content_ref"),
                        },
                    },
                )
            )
        hits.sort(key=lambda item: item[0], reverse=True)
        visible = [item[1] for item in hits[: max(1, min(limit, 100))]]
        return {
            "schema_version": "nexusnet-genesis-source-grounded-retrieval-result-v1",
            "surface_id": "genesis-memory-foundation-query",
            "status": "hits" if visible else "no-active-grounded-memory",
            "hit_count": len(visible),
            "hits": visible,
            "raw_content_included": bool(visible),
            "retrieval_boundary": "active-governed-public-memory-records-only",
        }

    def _validate_commit_inputs(
        self,
        *,
        application: dict[str, Any],
        gate: dict[str, Any],
        decisions: list[dict[str, Any]],
        source_content_by_decision_id: dict[str, str],
        governance_commit_ref: str,
        admin_commit_ref: str,
    ) -> None:
        if application.get("status") != "shadow-candidate-written" or application.get("apply_allowed") is not True:
            raise ValueError("governed shadow candidate is required before canonical memory commit")
        if gate.get("promotion_allowed") is not True:
            raise ValueError("promotion gate must allow canonical memory commit")
        if not governance_commit_ref or not admin_commit_ref:
            raise ValueError("governance_commit_ref and admin_commit_ref are required")
        if not decisions:
            raise ValueError("admitted source decisions are required")
        expected_ids = {str(item) for item in gate.get("decision_refs") or []}
        actual_ids = {str(decision.get("decision_id") or "") for decision in decisions}
        if actual_ids != expected_ids:
            raise ValueError("commit decisions must exactly match the promotion gate")
        if set(source_content_by_decision_id) != actual_ids:
            raise ValueError("source content is required for every admitted decision")
        for decision in decisions:
            decision_id = str(decision["decision_id"])
            if decision.get("memory_write_allowed") is not True or decision.get("retrieval_truth_allowed") is not True:
                raise ValueError("admission decision does not permit memory and retrieval truth")
            if str(decision.get("privacy_class") or "") not in {"public", "public-source", "licensed-public"}:
                raise ValueError("canonical memory commit requires an explicitly public source")
            if str(decision.get("consent_status") or "") not in {
                "memory-approved",
                "training-approved",
                "operator-approved",
            }:
                raise ValueError("canonical memory commit requires explicit memory consent")
            if str(decision.get("rights_license_status") or "") not in {
                "approved-for-memory",
                "approved-for-training",
            }:
                raise ValueError("canonical memory commit requires approved source rights")
            content = source_content_by_decision_id[decision_id]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("source content must be non-empty text")
            if f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}" != decision.get("content_ref"):
                raise ValueError("content digest does not match admitted source")

    def _activate_runtime_records(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        retrieval = getattr(self, "runtime_retrieval", None)
        memory = getattr(self, "runtime_memory", None)
        graph = getattr(self, "runtime_graph_ingestion", None)
        growth = getattr(self, "global_growth", None)
        if not all((retrieval, memory, graph, growth)):
            raise RuntimeError("all Layer 7 runtime services must be bound before commit")
        retrieval_receipts: list[dict[str, Any]] = []
        memory_receipts: list[dict[str, Any]] = []
        graph_receipts: list[dict[str, Any]] = []
        growth_receipts: list[dict[str, Any]] = []
        try:
            for record in records:
                content = self._read_text(str(record.get("content_artifact_ref") or ""))
                if content is None:
                    raise RuntimeError("canonical memory content artifact is unavailable")
                common = {
                    "memory_id": str(record["memory_id"]),
                    "memory_ref": str(record["memory_ref"]),
                    "session_ref_digest": str(record.get("session_ref_digest") or ""),
                    "source_ref": str(record.get("source_ref") or ""),
                    "content": content,
                    "content_ref": str(record.get("content_ref") or ""),
                }
                retrieval_receipts.append(
                    retrieval.activate_genesis_memory(
                        **common,
                        source_kind=str(record.get("source_kind") or "canon-memory"),
                    )
                )
                memory_receipts.append(memory.activate_genesis_memory(**common))
                graph_receipts.append(graph.activate_genesis_memory(**common))
                growth_receipts.append(
                    growth.record_runtime_interaction(
                        str(record.get("session_ref_digest") or "global"),
                        source_model="NexusBrain-canon-memory",
                        expert_node="expert.memory",
                        task_family="genesis-layer7-memory-activation",
                        route_geometry="canon-memory>retrieval>graph>growth",
                        selected_node_ids=["memory", "retrieval", "graph"],
                        confidence=1.0,
                        eval_scores={"quality": 1.0, "groundedness": 1.0},
                        runtime_class="genesis-memory-foundation",
                        sandbox_result="passed",
                        quality=1.0,
                        knowledge_ref=str(record.get("memory_ref") or ""),
                        packet_id=f"genesis-memory-growth::{_digest(str(record.get('memory_id') or ''))}",
                        metadata={
                            "memory_id_ref": str(record.get("memory_id") or ""),
                            "content_ref": str(record.get("content_ref") or ""),
                        },
                    )
                )
        except Exception:
            self._deactivate_runtime_records(
                records,
                reason_ref="runtime-activation-compensation",
                growth_receipts=growth_receipts,
            )
            raise
        return {
            "schema_version": "nexusnet-genesis-memory-runtime-activation-v1",
            "surface_id": "genesis-memory-foundation-runtime-activation",
            "status": "activated",
            "lexical_retrieval": {"status": "active", "receipts": retrieval_receipts},
            "semantic_memory": {"status": "active", "receipts": memory_receipts},
            "live_graphrag": {"status": "active", "receipts": graph_receipts},
            "global_growth": {"status": "active", "receipts": growth_receipts},
            "raw_content_included": False,
        }

    def _deactivate_runtime_records(
        self,
        records: list[dict[str, Any]],
        *,
        reason_ref: str,
        growth_receipts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        retrieval = getattr(self, "runtime_retrieval", None)
        memory = getattr(self, "runtime_memory", None)
        graph = getattr(self, "runtime_graph_ingestion", None)
        growth = getattr(self, "global_growth", None)
        if not all((retrieval, memory, graph, growth)):
            raise RuntimeError("all Layer 7 runtime services must be bound before rollback")
        retrieval_receipts = [
            retrieval.deactivate_genesis_memory(memory_id=str(record["memory_id"]), reason_ref=reason_ref)
            for record in records
        ]
        memory_receipts = [
            memory.deactivate_genesis_memory(
                memory_id=str(record["memory_id"]),
                session_ref_digest=str(record.get("session_ref_digest") or ""),
                reason_ref=reason_ref,
            )
            for record in records
        ]
        graph_receipts = [
            graph.deactivate_genesis_memory(memory_id=str(record["memory_id"]), reason_ref=reason_ref)
            for record in records
        ]
        passivation_refs = [
            {
                "capture_ref": receipt.get("capture_ref"),
                "runtime_growth_receipt_id": receipt.get("receipt_id"),
                "packet_id": (receipt.get("federated_packet") or {}).get("packet_id"),
            }
            for receipt in growth_receipts
        ]
        passivation = growth.passivate_runtime_captures(
            passivation_refs,
            reason_ref=reason_ref,
            session_ref_digest=str(records[0].get("session_ref_digest") or "") if records else "",
        )
        return {
            "schema_version": "nexusnet-genesis-memory-runtime-deactivation-v1",
            "surface_id": "genesis-memory-foundation-runtime-deactivation",
            "status": "passivated",
            "lexical_retrieval": {"status": "revoked", "receipts": retrieval_receipts},
            "semantic_memory": {"status": "revoked", "receipts": memory_receipts},
            "live_graphrag": {"status": "revoked", "receipts": graph_receipts},
            "global_growth": {
                "status": "passivated",
                "passivation_record": passivation,
            },
            "raw_content_included": False,
        }

    def _write_state(
        self,
        *,
        memory_id: str,
        application_id: str,
        state: str,
        at: str,
        reason_ref: str | None = None,
    ) -> None:
        artifact_ref = f"genesis/memory-foundation/states/{_artifact_id(memory_id)}.json"
        self._write_json(
            {
                "memory_id": memory_id,
                "application_id": application_id,
                "state": state,
                "at": at,
                "reason_ref": reason_ref,
                "raw_content_included": False,
            },
            artifact_ref=artifact_ref,
        )

    def _record_state(self, record: dict[str, Any]) -> str:
        state_ref = f"genesis/memory-foundation/states/{_artifact_id(str(record.get('memory_id') or ''))}.json"
        state = self._read_artifact(state_ref)
        return str(state.get("state") or "unknown") if state else "unknown"

    def _records(self) -> list[dict[str, Any]]:
        return self._artifacts(self.records_dir)

    def _artifacts(self, directory: Path) -> list[dict[str, Any]]:
        if not directory.is_dir():
            return []
        records: list[dict[str, Any]] = []
        for path in directory.glob("*.json"):
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(value, dict):
                records.append(value)
        records.sort(key=lambda item: str(item.get("created_at") or item.get("rolled_back_at") or ""), reverse=True)
        return records

    def _commit_for_application(self, application_id: str) -> dict[str, Any] | None:
        return next(
            (commit for commit in self._artifacts(self.commits_dir) if commit.get("application_id") == application_id),
            None,
        )

    def _growth_state(self, *, session_ref_digest: str | None) -> dict[str, Any]:
        active = [
            record
            for record in self._records()
            if self._record_state(record) == "active"
            and (session_ref_digest is None or record.get("session_ref_digest") == session_ref_digest)
        ]
        return {
            "scope": "global" if session_ref_digest is None else "per-user",
            "scope_ref_digest": session_ref_digest,
            "active_memory_count": len(active),
            "memory_refs": [record.get("memory_ref") for record in active],
            "source_refs": _unique(record.get("source_ref") for record in active),
            "raw_content_included": False,
        }

    def _rebuild_indexes(self) -> None:
        all_records = self._records()
        active = [record for record in all_records if self._record_state(record) == "active"]
        global_payload = {
            "schema_version": "nexusnet-genesis-canon-memory-index-v1",
            "scope": "global",
            "active_memory_count": len(active),
            "memory_refs": [record.get("memory_ref") for record in active],
            "raw_content_included": False,
        }
        self._write_absolute_json(global_payload, self.global_index_path)
        grouped: dict[str, list[dict[str, Any]]] = {}
        for record in all_records:
            digest = str(record.get("session_ref_digest") or "global-anonymous")
            grouped.setdefault(digest, [])
        for record in active:
            digest = str(record.get("session_ref_digest") or "global-anonymous")
            grouped[digest].append(record)
        for digest, records in grouped.items():
            self._write_absolute_json(
                {
                    "schema_version": "nexusnet-genesis-canon-memory-index-v1",
                    "scope": "per-user",
                    "scope_ref_digest": digest,
                    "active_memory_count": len(records),
                    "memory_refs": [record.get("memory_ref") for record in records],
                    "raw_content_included": False,
                },
                self.user_index_dir / f"{_artifact_id(digest)}.json",
            )

    def _write_json(self, payload: dict[str, Any], *, artifact_ref: str) -> None:
        self._write_absolute_json(payload, self.artifacts_dir / artifact_ref)

    @staticmethod
    def _write_absolute_json(payload: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(path)

    def _write_text(self, content: str, *, artifact_ref: str) -> None:
        path = self.artifacts_dir / artifact_ref
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)

    def _read_artifact(self, artifact_ref: str) -> dict[str, Any]:
        if not artifact_ref:
            return {}
        path = self.artifacts_dir / artifact_ref
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return value if isinstance(value, dict) else {}

    def _read_text(self, artifact_ref: str) -> str | None:
        if not artifact_ref:
            return None
        try:
            return (self.artifacts_dir / artifact_ref).read_text(encoding="utf-8")
        except OSError:
            return None


def _graph_projection(
    *,
    memory_id: str,
    decision_id: str,
    source_ref: str,
    content_ref: str,
    graph_ref: str,
) -> dict[str, Any]:
    source_node = f"source::{_digest(source_ref)}"
    decision_node = f"admission::{_digest(decision_id)}"
    return {
        "schema_version": "nexusnet-genesis-nexusgraph-intelligence-fabric-v0",
        "surface_id": "NexusGraph-Intelligence-Fabric-v0",
        "graph_ref": graph_ref,
        "nodes": [
            {"node_id": memory_id, "kind": "canon-memory", "content_ref": content_ref},
            {"node_id": source_node, "kind": "source", "source_ref": source_ref},
            {"node_id": decision_node, "kind": "admission-decision", "decision_ref": decision_id},
        ],
        "edges": [
            {"edge_id": f"edge::{_digest(memory_id + source_node)}", "from": memory_id, "to": source_node, "kind": "grounded-by"},
            {"edge_id": f"edge::{_digest(memory_id + decision_node)}", "from": memory_id, "to": decision_node, "kind": "admitted-by"},
        ],
        "event_refs": [decision_id],
        "raw_content_included": False,
    }


def _sanitized_commit(commit: dict[str, Any]) -> dict[str, Any]:
    return {
        key: commit.get(key)
        for key in (
            "commit_id",
            "commit_ref",
            "application_id",
            "gate_id",
            "status",
            "honest_status_label",
            "memory_record_count",
            "retrieval_packet_count",
            "graph_node_count",
            "graph_edge_count",
            "memory_evolution_passport_ref",
            "created_at",
            "raw_content_included",
            "active_production_mutation_allowed",
            "active_production_mutated",
        )
    }


def _sanitized_rollback(rollback: dict[str, Any]) -> dict[str, Any]:
    return {
        key: rollback.get(key)
        for key in (
            "rollback_id",
            "rollback_ref",
            "application_id",
            "commit_id",
            "status",
            "rollback_state",
            "reverted_memory_count",
            "rolled_back_at",
            "raw_content_included",
            "active_production_mutation_allowed",
            "active_production_mutated",
        )
    }


def _sanitized_evolution(evolution: dict[str, Any]) -> dict[str, Any]:
    return {
        key: evolution.get(key)
        for key in (
            "evolution_id",
            "evolution_ref",
            "memory_id",
            "memory_ref",
            "memory_evolution_passport_ref",
            "status",
            "honest_status_label",
            "content_changed",
            "previous_content_ref",
            "refreshed_content_ref",
            "source_refresh_ref",
            "stale_state",
            "contradiction_state",
            "contradiction_refs",
            "current_memory_state",
            "recommit_required",
            "required_controls",
            "candidate_decision_ref",
            "observed_at",
            "raw_content_included",
            "active_production_mutation_allowed",
            "active_production_mutated",
        )
    }


def _unique(values: Any) -> list[str]:
    output: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in output:
            output.append(text)
    return output


def _safe_refs(values: Any) -> list[str]:
    return _unique(_safe_ref(value) for value in values)


def _safe_ref(value: Any) -> str:
    text = str(value or "").strip()
    lowered = text.lower()
    if not text:
        return ""
    if len(text) > 240 or any(
        marker in lowered
        for marker in ("secret", "password", "token", "api-key", "apikey", ":\\", "runtime/test-fixtures")
    ):
        return f"ref-digest::{_digest(text)}"
    return text


def _artifact_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-")


def _terms(value: str) -> list[str]:
    return [term for term in re.findall(r"[a-zA-Z0-9_]+", value.lower()) if term]


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _privacy_digest(value: str | None) -> str:
    return "sha256:" + hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
