"""Multi-user growth: many users + federated learning + dreaming grow the substrate toward birth.

Canon: the born model emerges over a LONG time as MANY end users use the wrapper; their assimilation is
aggregated (federated) and dreamed on. This coordinator keeps a per-user ContinuousAssimilationLoop,
aggregates assimilation GLOBALLY across users, and signals when the global threshold for an expert is
reached (train), when enough users are active (federate), and overall birth progress. Privacy: only
source-model provenance + counts cross the user boundary, never raw content.
"""
from __future__ import annotations

import hashlib
from typing import Any

from .continuous_assimilation import ContinuousAssimilationLoop


def _privacy_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _safe_ref(value: str) -> str:
    if value.startswith(("trace::", "evidence::", "artifact::", "federated-packet::", "runtime-growth::")):
        return value[:160]
    return f"ref-digest::{_privacy_digest(value)}" if value else ""


def _confidence_bucket(confidence: float) -> str:
    if confidence >= 0.8:
        return "high"
    if confidence >= 0.5:
        return "medium"
    if confidence > 0:
        return "low"
    return "unknown"


def _safe_score(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    return round(max(0.0, min(1.0, score)), 4)


def _safe_metadata(metadata: dict[str, Any] | None) -> dict[str, str]:
    allowed = {"trace_ref", "evidence_ref", "artifact_ref", "packet_ref"}
    safe: dict[str, str] = {}
    for key, value in (metadata or {}).items():
        if key not in allowed:
            continue
        safe[key] = _safe_ref(str(value))
    return safe


def _capture_ref_for_receipt(receipt_id: str) -> str:
    return f"runtime-growth-capture::{_privacy_digest(receipt_id)}"


class MultiUserGrowthCoordinator:
    """Aggregate continuous assimilation across users; schedule federated training + dreaming toward birth."""

    mutates_production = False

    def __init__(self, *, global_train_threshold: int = 5, federate_min_users: int = 2,
                 dream_every: int = 10) -> None:
        self.global_train_threshold = global_train_threshold
        self.federate_min_users = federate_min_users
        self.dream_every = dream_every
        self._users: dict[str, ContinuousAssimilationLoop] = {}
        self._global_captures = 0
        self._runtime_receipts: list[dict[str, Any]] = []
        self._runtime_interactions = 0
        self._inactive_capture_refs: dict[str, dict[str, Any]] = {}
        self._inactive_receipt_ids: set[str] = set()
        self._inactive_packet_ids: set[str] = set()
        self._passivation_records: list[dict[str, Any]] = []

    def _loop(self, user_id: str) -> ContinuousAssimilationLoop:
        return self._users.setdefault(user_id, ContinuousAssimilationLoop(train_threshold=3))

    def assimilate_for_user(self, user_id: str, *, source_model: str, expert_node: str,
                            quality: float = 1.0, knowledge_ref: str = "") -> None:
        self._loop(user_id).assimilate(source_model=source_model, expert_node=expert_node,
                                       quality=quality, knowledge_ref=knowledge_ref)
        self._global_captures += 1

    def record_runtime_interaction(
        self,
        user_id: str,
        *,
        source_model: str,
        expert_node: str,
        task_family: str = "",
        route_geometry: str = "",
        selected_node_ids: list[str] | None = None,
        confidence: float = 0.0,
        eval_scores: dict[str, Any] | None = None,
        failure_class: str = "",
        policy_block_class: str = "",
        runtime_class: str = "",
        hardware_class: str = "",
        sandbox_result: str = "",
        dream_candidate_outcome: str = "",
        quality: float = 1.0,
        knowledge_ref: str = "",
        packet_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Record a sanitized whole-system interaction as growth evidence.

        This is the non-wrapper bridge: any runtime/hive surface can feed per-user
        assimilation, global growth, and federated learning without exporting raw
        prompts, outputs, paths, session IDs, or private memory refs.
        """
        self._runtime_interactions += 1
        user_ref = f"user::{_privacy_digest(user_id)}"
        safe_knowledge_ref = _safe_ref(knowledge_ref) or f"runtime-growth::{self._runtime_interactions}"
        safe_selected_nodes = [str(node)[:80] for node in (selected_node_ids or [])]
        safe_scores = {str(key)[:48]: _safe_score(value) for key, value in (eval_scores or {}).items()}
        packet_seed = "|".join(
            [
                str(self._runtime_interactions),
                user_ref,
                source_model,
                expert_node,
                task_family,
                route_geometry,
            ]
        )
        packet_ref = packet_id or f"runtime-fed::{_privacy_digest(packet_seed)}"
        receipt_id = f"runtime-growth::{_privacy_digest(packet_ref)}"
        capture_ref = _capture_ref_for_receipt(receipt_id)
        user_loop = self._loop(user_id)
        user_loop.assimilate(
            source_model=source_model,
            expert_node=expert_node,
            task=task_family,
            quality=_safe_score(quality),
            knowledge_ref=safe_knowledge_ref,
            metadata={
                "capture_ref": capture_ref,
                "runtime_growth_receipt_id": receipt_id,
                "runtime_growth_packet_id": packet_ref,
                "raw_content_included": False,
            },
        )
        self._global_captures += 1
        federated_packet = {
            "schema_version": "nexusnet-runtime-federated-learning-packet-v1",
            "surface_id": "multi-user-runtime-growth-federated-packet",
            "packet_id": packet_ref,
            "task_family": task_family or "general",
            "source_model": source_model,
            "expert_node": expert_node,
            "route_geometry_signature": _privacy_digest(route_geometry or "unspecified-route"),
            "selected_node_roles": safe_selected_nodes,
            "confidence_bucket": _confidence_bucket(confidence),
            "eval_scores": safe_scores,
            "failure_class": failure_class or "none",
            "policy_block_class": policy_block_class or "none",
            "runtime_class": runtime_class or "unspecified",
            "hardware_class": hardware_class or "unspecified",
            "sandbox_result": sandbox_result or "not-run",
            "dream_candidate_outcome": dream_candidate_outcome or "not-requested",
            "safe_metadata": _safe_metadata(metadata),
            "raw_content_included": False,
            "contains_personal_data": False,
            "active_production_mutation_allowed": False,
        }
        receipt = {
            "schema_version": "nexusnet-multi-user-runtime-growth-receipt-v1",
            "surface_id": "multi-user-runtime-growth-receipt",
            "receipt_id": receipt_id,
            "capture_ref": capture_ref,
            "user_ref": user_ref,
            "source_model": source_model,
            "expert_node": expert_node,
            "knowledge_ref": safe_knowledge_ref,
            "per_user_growth": {
                "captures": user_loop.captures(expert_node),
                "distinct_sources": user_loop.assimilation_count(expert_node),
                "ready_to_train": user_loop.ready_to_train(expert_node),
            },
            "global_growth": self.growth_status(include_latest_receipt=False),
            "federated_packet": federated_packet,
            "forward_pass_coverage": {
                "continuous_assimilation": True,
                "per_user_growth": True,
                "global_growth": True,
                "federated_packet": True,
                "dream_signal": True,
            },
            "privacy_boundary": "sanitized-runtime-growth-metadata-only-no-raw-prompts-outputs-session-ids-paths-or-private-memory",
            "raw_content_included": False,
            "contains_personal_data": False,
            "active_production_mutation_allowed": False,
            "mutates_production": False,
        }
        self._runtime_receipts.insert(0, receipt)
        self._runtime_receipts = self._runtime_receipts[:50]
        return receipt

    def restore_runtime_receipts(self, receipts: list[dict[str, Any]]) -> dict[str, Any]:
        """Rehydrate sanitized runtime growth receipts from durable artifacts.

        Rehydration intentionally accepts only already-sanitized receipts. It rebuilds the
        same per-user/global counters used by live runtime interactions without restoring
        raw prompts, outputs, local paths, session IDs, or private memory refs.
        """
        existing_receipt_ids = {
            str(receipt.get("receipt_id"))
            for receipt in self._runtime_receipts
            if isinstance(receipt, dict) and receipt.get("receipt_id")
        }
        restored = 0
        skipped = 0
        safe_receipts = [receipt for receipt in receipts if isinstance(receipt, dict)]
        for receipt in reversed(safe_receipts):
            packet = receipt.get("federated_packet") if isinstance(receipt.get("federated_packet"), dict) else {}
            receipt_id = str(receipt.get("receipt_id") or "")
            if not receipt_id or receipt_id in existing_receipt_ids:
                skipped += 1
                continue
            if not self._can_restore_runtime_receipt(receipt, packet):
                skipped += 1
                continue

            user_ref = str(receipt.get("user_ref") or f"user::{_privacy_digest(receipt_id)}")
            if not user_ref.startswith("user::"):
                user_ref = f"user::{_privacy_digest(user_ref)}"
            source_model = str(receipt.get("source_model") or packet.get("source_model") or "unknown-runtime")
            expert_node = str(receipt.get("expert_node") or packet.get("expert_node") or "expert.runtime")
            eval_scores = packet.get("eval_scores") if isinstance(packet.get("eval_scores"), dict) else {}
            quality = _safe_score(eval_scores.get("quality", eval_scores.get("confidence", 1.0)))
            knowledge_ref = _safe_ref(
                str(receipt.get("knowledge_ref") or packet.get("packet_id") or receipt_id)
            )

            self._loop(user_ref).assimilate(
                source_model=source_model,
                expert_node=expert_node,
                task=str(packet.get("task_family") or ""),
                quality=quality,
                knowledge_ref=knowledge_ref,
                metadata={
                    "capture_ref": _capture_ref_for_receipt(receipt_id),
                    "runtime_growth_receipt_id": receipt_id,
                    "runtime_growth_packet_id": str(packet.get("packet_id") or ""),
                    "restored_runtime_receipt_ref": _safe_ref(receipt_id),
                    "raw_content_included": False,
                },
            )
            self._global_captures += 1
            self._runtime_interactions += 1
            restored_receipt = dict(receipt)
            restored_receipt["federated_packet"] = dict(packet)
            self._runtime_receipts.insert(0, restored_receipt)
            existing_receipt_ids.add(receipt_id)
            restored += 1

        self._runtime_receipts = self._runtime_receipts[:50]
        return {
            "surface_id": "multi-user-runtime-growth-rehydration",
            "schema_version": "nexusnet-multi-user-runtime-growth-rehydration-v1",
            "restored_receipts": restored,
            "skipped_receipts": skipped,
            "runtime_interaction_count": self._runtime_interactions,
            "runtime_receipt_count": len(self._runtime_receipts),
            "raw_content_included": False,
            "contains_personal_data": False,
            "mutates_production": False,
        }

    @staticmethod
    def _can_restore_runtime_receipt(receipt: dict[str, Any], packet: dict[str, Any]) -> bool:
        return (
            receipt.get("surface_id") == "multi-user-runtime-growth-receipt"
            and receipt.get("raw_content_included") is False
            and receipt.get("contains_personal_data") is False
            and receipt.get("active_production_mutation_allowed") is False
            and packet.get("surface_id") == "multi-user-runtime-growth-federated-packet"
            and packet.get("raw_content_included") is False
            and packet.get("contains_personal_data") is False
            and packet.get("active_production_mutation_allowed") is False
        )

    def _capture_records(self) -> list[tuple[str, str, Any]]:
        records: list[tuple[str, str, Any]] = []
        for user_id, loop in self._users.items():
            banks = getattr(loop, "_banks", {})
            for expert_node, captures in banks.items():
                for record in captures:
                    records.append((user_id, expert_node, record))
        return records

    def _capture_match_keys(self, record: Any) -> set[str]:
        metadata = record.metadata if isinstance(getattr(record, "metadata", None), dict) else {}
        receipt_id = str(metadata.get("runtime_growth_receipt_id") or "")
        packet_id = str(metadata.get("runtime_growth_packet_id") or "")
        capture_ref = str(metadata.get("capture_ref") or "")
        keys = {value for value in (capture_ref, receipt_id, packet_id, record.knowledge_ref) if value}
        if receipt_id:
            keys.add(f"runtime-growth-receipt::{receipt_id}")
        if packet_id:
            keys.add(f"federated-packet::{packet_id}")
        return keys

    def _passivation_target_keys(self, ref: dict[str, Any]) -> set[str]:
        values = {
            str(ref.get("capture_ref") or ""),
            str(ref.get("runtime_growth_receipt_id") or ""),
            str(ref.get("receipt_id") or ""),
            str(ref.get("packet_id") or ""),
            str(ref.get("source_ref") or ""),
        }
        values = {value for value in values if value}
        expanded = set(values)
        for value in values:
            if value.startswith("federated-packet::") or value.startswith("runtime-growth-receipt::"):
                expanded.add(value.split("::", 1)[1])
            else:
                expanded.add(f"federated-packet::{value}")
                expanded.add(f"runtime-growth-receipt::{value}")
        return expanded

    def _is_capture_inactive(self, record: Any) -> bool:
        metadata = record.metadata if isinstance(getattr(record, "metadata", None), dict) else {}
        capture_ref = str(metadata.get("capture_ref") or "")
        receipt_id = str(metadata.get("runtime_growth_receipt_id") or "")
        packet_id = str(metadata.get("runtime_growth_packet_id") or "")
        return (
            (capture_ref and capture_ref in self._inactive_capture_refs)
            or (receipt_id and receipt_id in self._inactive_receipt_ids)
            or (packet_id and packet_id in self._inactive_packet_ids)
        )

    def _active_capture_records(self, expert_node: str | None = None) -> list[tuple[str, str, Any]]:
        records = [
            item
            for item in self._capture_records()
            if not self._is_capture_inactive(item[2])
        ]
        if expert_node is None:
            return records
        return [item for item in records if item[1] == expert_node]

    def _safe_passivation_ref(self, ref: dict[str, Any]) -> dict[str, Any]:
        return {
            "source_ref": _safe_ref(str(ref.get("source_ref") or "")),
            "capture_ref": _safe_ref(str(ref.get("capture_ref") or "")),
            "runtime_growth_receipt_id": _safe_ref(str(ref.get("runtime_growth_receipt_id") or ref.get("receipt_id") or "")),
            "packet_id": _safe_ref(str(ref.get("packet_id") or "")),
            "status": str(ref.get("status") or "inactive-retention-passivated")[:80],
            "raw_content_included": False,
            "contains_personal_data": False,
        }

    def passivate_runtime_captures(
        self,
        passivation_refs: list[dict[str, Any]],
        *,
        reason_ref: str,
        session_ref_digest: str = "",
        record_id: str | None = None,
    ) -> dict[str, Any]:
        safe_refs = [
            self._safe_passivation_ref(ref)
            for ref in passivation_refs
            if isinstance(ref, dict)
        ]
        seed = "|".join(
            [
                _safe_ref(reason_ref),
                _safe_ref(session_ref_digest),
                *[repr(ref) for ref in safe_refs],
            ]
        )
        resolved_record_id = record_id or f"multi-user-runtime-growth-passivation::{_privacy_digest(seed)}"
        matched: dict[str, dict[str, Any]] = {}
        for ref in passivation_refs:
            if not isinstance(ref, dict):
                continue
            target_keys = self._passivation_target_keys(ref)
            for user_id, expert_node, record in self._capture_records():
                metadata = record.metadata if isinstance(getattr(record, "metadata", None), dict) else {}
                capture_ref = str(metadata.get("capture_ref") or "")
                if not capture_ref or capture_ref in self._inactive_capture_refs:
                    continue
                if not (self._capture_match_keys(record) & target_keys):
                    continue
                receipt_id = str(metadata.get("runtime_growth_receipt_id") or "")
                packet_id = str(metadata.get("runtime_growth_packet_id") or "")
                inactive_record = {
                    "capture_ref": capture_ref,
                    "user_ref": f"user::{_privacy_digest(user_id)}" if not user_id.startswith("user::") else user_id,
                    "expert_node": expert_node,
                    "source_model": str(record.source_model),
                    "runtime_growth_receipt_id": receipt_id,
                    "packet_id": packet_id,
                    "reason_ref": _safe_ref(reason_ref),
                    "session_ref_digest": session_ref_digest,
                    "status": "inactive-retention-passivated",
                    "active_personal_data_training_allowed": False,
                    "active_production_mutation_allowed": False,
                    "raw_content_included": False,
                    "contains_personal_data": False,
                }
                self._inactive_capture_refs[capture_ref] = inactive_record
                if receipt_id:
                    self._inactive_receipt_ids.add(receipt_id)
                if packet_id:
                    self._inactive_packet_ids.add(packet_id)
                matched[capture_ref] = inactive_record
        record = {
            "schema_version": "nexusnet-multi-user-runtime-growth-passivation-v1",
            "surface_id": "multi-user-runtime-growth-passivation",
            "record_id": resolved_record_id,
            "status": "passivated" if matched else "no-active-captures-matched",
            "session_ref_digest": session_ref_digest,
            "reason_ref": _safe_ref(reason_ref),
            "requested_passivation_refs": safe_refs,
            "passivated_capture_count": len(matched),
            "passivated_capture_refs": list(matched.values()),
            "active_global_captures": len(self._active_capture_records()),
            "passivated_global_captures": len(self._inactive_capture_refs),
            "raw_content_included": False,
            "contains_personal_data": False,
            "active_production_mutation_allowed": False,
            "mutates_production": False,
            "privacy_boundary": "sanitized-runtime-growth-passivation-refs-only-no-raw-prompts-outputs-session-ids-or-local-paths",
        }
        if not any(existing.get("record_id") == resolved_record_id for existing in self._passivation_records):
            self._passivation_records.insert(0, record)
            self._passivation_records = self._passivation_records[:50]
        return record

    def restore_passivation_records(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        restored = 0
        skipped = 0
        passivated = 0
        existing_ids = {
            str(record.get("record_id") or "")
            for record in self._passivation_records
            if isinstance(record, dict)
        }
        for record in records:
            if not isinstance(record, dict):
                skipped += 1
                continue
            source_record_id = str(record.get("record_id") or "")
            if not source_record_id or source_record_id in existing_ids:
                skipped += 1
                continue
            if record.get("surface_id") == "multi-user-runtime-growth-passivation":
                passivation_refs = (
                    record.get("requested_passivation_refs")
                    if isinstance(record.get("requested_passivation_refs"), list)
                    else record.get("passivated_capture_refs")
                    if isinstance(record.get("passivated_capture_refs"), list)
                    else []
                )
                reason_ref = str(record.get("reason_ref") or source_record_id)
                session_ref_digest = str(record.get("session_ref_digest") or "")
                target_record_id = source_record_id
            elif record.get("surface_id") == "release-wrapper-privacy-retention-enforcement-record":
                passivation_refs = (
                    record.get("passivated_global_growth_refs")
                    if isinstance(record.get("passivated_global_growth_refs"), list)
                    else []
                )
                reason_ref = source_record_id
                session_ref_digest = str(record.get("session_ref_digest") or "")
                target_record_id = f"multi-user-runtime-growth-passivation-replay::{_privacy_digest(source_record_id)}"
            else:
                skipped += 1
                continue
            if not passivation_refs:
                skipped += 1
                continue
            applied = self.passivate_runtime_captures(
                [ref for ref in passivation_refs if isinstance(ref, dict)],
                reason_ref=reason_ref,
                session_ref_digest=session_ref_digest,
                record_id=target_record_id,
            )
            governance = (
                record.get("authority_evidence_tool_governance")
                if isinstance(record.get("authority_evidence_tool_governance"), dict)
                else {}
            )
            native_passivation = (
                record.get("native_global_growth_passivation")
                if isinstance(record.get("native_global_growth_passivation"), dict)
                else {}
            )
            if not governance and isinstance(
                native_passivation.get("authority_evidence_tool_governance"), dict
            ):
                governance = native_passivation["authority_evidence_tool_governance"]
            if governance:
                applied["authority_evidence_tool_governance"] = governance
            existing_ids.add(target_record_id)
            restored += 1
            passivated += int(applied.get("passivated_capture_count") or 0)
        return {
            "schema_version": "nexusnet-multi-user-runtime-growth-passivation-replay-v1",
            "surface_id": "multi-user-runtime-growth-passivation-replay",
            "status": "replayed" if restored else "no-new-passivation-records",
            "restored_passivation_records": restored,
            "skipped_passivation_records": skipped,
            "passivated_capture_count": passivated,
            "active_global_captures": len(self._active_capture_records()),
            "passivated_global_captures": len(self._inactive_capture_refs),
            "raw_content_included": False,
            "contains_personal_data": False,
            "active_production_mutation_allowed": False,
        }

    def global_sources(self, expert_node: str) -> list[str]:
        """Distinct source models assimilated into a node ACROSS all users (federated provenance)."""
        sources = {record.source_model for _, _, record in self._active_capture_records(expert_node)}
        return sorted(sources)

    def global_ready_to_train(self, expert_node: str) -> bool:
        return len(self.global_sources(expert_node)) >= self.global_train_threshold

    def federation_ready(self) -> bool:
        """Enough distinct users contributing to run a federated aggregation round."""
        active_users = {user_id for user_id, _, _ in self._active_capture_records()}
        return len(active_users) >= self.federate_min_users

    def dream_due(self) -> bool:
        active_captures = len(self._active_capture_records())
        return active_captures > 0 and active_captures % self.dream_every == 0

    def all_expert_nodes(self) -> list[str]:
        nodes: set[str] = set()
        for loop in self._users.values():
            nodes.update(loop.status()["nodes"].keys())
        return sorted(nodes)

    def growth_status(self, *, include_latest_receipt: bool = True) -> dict[str, Any]:
        nodes = self.all_expert_nodes()
        train_ready = [n for n in nodes if self.global_ready_to_train(n)]
        active_records = self._active_capture_records()
        active_users = {user_id for user_id, _, _ in active_records}
        status = {
            "users": len(active_users),
            "historical_users": len(self._users),
            "global_captures": self._global_captures,
            "active_global_captures": len(active_records),
            "passivated_global_captures": len(self._inactive_capture_refs),
            "expert_nodes": len(nodes),
            "global_sources_per_node": {n: len(self.global_sources(n)) for n in nodes},
            "training_ready_nodes": train_ready,
            "federation_ready": self.federation_ready(),
            "dream_due": self.dream_due(),
            "runtime_interaction_count": self._runtime_interactions,
            "runtime_receipt_count": len(self._runtime_receipts),
            "native_privacy_passivation": {
                "surface_id": "multi-user-runtime-growth-passivation-status",
                "status": "passivated" if self._inactive_capture_refs else "no-passivated-captures",
                "record_count": len(self._passivation_records),
                "latest_record_id": (
                    self._passivation_records[0].get("record_id")
                    if self._passivation_records
                    else None
                ),
                "inactive_capture_count": len(self._inactive_capture_refs),
                "inactive_receipt_count": len(self._inactive_receipt_ids),
                "inactive_packet_count": len(self._inactive_packet_ids),
                "latest_record": self._passivation_records[0] if self._passivation_records else None,
                "raw_content_included": False,
                "contains_personal_data": False,
                "active_production_mutation_allowed": False,
            },
            # birth progresses as more nodes cross the global training threshold across users over time
            "birth_progress": round(len(train_ready) / len(nodes), 4) if nodes else 0.0,
            "fully_grown": bool(nodes) and len(train_ready) == len(nodes) and self.federation_ready(),
            "mutates_production": False,
        }
        if include_latest_receipt:
            status["latest_runtime_receipt"] = self._runtime_receipts[0] if self._runtime_receipts else None
        return status
