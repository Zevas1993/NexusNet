from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from nexusnet.experts.reconciliation import Cluster9TeacherReconciliationRegistry

from .event_spine import GenesisEventSpineService


class GenesisNodeContractRegistry:
    """Persistent Layer 9 contracts and lifecycle enforcement for hive nodes."""

    def __init__(
        self,
        *,
        artifacts_dir: Path | str,
        canon_registry: Any,
        ao_registry: Any,
        cluster9_registry: Cluster9TeacherReconciliationRegistry,
        event_spine: GenesisEventSpineService,
    ) -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.canon_registry = canon_registry
        self.ao_registry = ao_registry
        self.cluster9_registry = cluster9_registry
        self.event_spine = event_spine
        self.root = self.artifacts_dir / "genesis" / "node-contracts"
        self.route_receipts_dir = self.root / "route-receipts"
        self.children_dir = self.root / "temporary-children"
        self.retention_reviews_dir = self.root / "retention-reviews"
        self.retirements_dir = self.root / "retirements"
        self.restorations_dir = self.root / "restorations"
        self.archives_dir = self.root / "archives"
        self.teacher_candidates_dir = self.root / "teacher-candidate-intakes"
        self.birth_verifications_dir = self.root / "teacher-birth-verifications"
        self.teacher_use_authorizations_dir = self.root / "teacher-use-authorizations"
        self.teacher_replacement_recommendations_dir = self.root / "teacher-replacement-recommendations"
        self._replay_teacher_candidates()
        self._base_contracts = self._build_base_contracts()

    def summary(self, *, session_ref_digest: str | None = None) -> dict[str, Any]:
        contracts = self.contracts()
        route_receipts = [
            receipt
            for receipt in self._artifacts(self.route_receipts_dir)
            if not session_ref_digest or receipt.get("session_ref_digest") == session_ref_digest
        ]
        children = self._artifacts(self.children_dir)
        reviews = self._artifacts(self.retention_reviews_dir)
        retirements = self._artifacts(self.retirements_dir)
        restorations = self._artifacts(self.restorations_dir)
        teacher_governance = self.teacher_governance_summary()
        node_kind_counts: dict[str, int] = {}
        for contract in contracts:
            kind = str(contract.get("node_kind") or "unknown")
            node_kind_counts[kind] = node_kind_counts.get(kind, 0) + 1
        complete_count = sum(1 for contract in contracts if _contract_complete(contract))
        lifecycle_observed = bool(children or reviews or retirements or restorations or route_receipts)
        return {
            "schema_version": "nexusnet-genesis-o-ao-expert-contract-registry-v1",
            "surface_id": "genesis-o-ao-expert-contract-registry",
            "status": (
                "live-contract-registry-with-lifecycle-evidence"
                if lifecycle_observed
                else "live-contract-registry"
            ),
            "honest_status_label": (
                "genesis-layer9-node-contract-registry-live-with-lifecycle-evidence"
                if lifecycle_observed
                else "genesis-layer9-node-contract-registry-live"
            ),
            "mother_brain_authority": "NexusBrain",
            "contract_count": len(contracts),
            "complete_contract_count": complete_count,
            "incomplete_contract_count": len(contracts) - complete_count,
            "node_kind_counts": node_kind_counts,
            "active_contract_count": sum(
                1 for contract in contracts if contract.get("lifecycle_state") == "active"
            ),
            "archived_contract_count": sum(
                1 for contract in contracts if contract.get("lifecycle_state") == "archived-retired"
            ),
            "shadow_contract_count": sum(
                1 for contract in contracts if contract.get("lifecycle_state") in {"shadow", "retention-reviewed-shadow"}
            ),
            "route_receipt_count": len(route_receipts),
            "latest_route_receipt": route_receipts[0] if route_receipts else None,
            "temporary_child_count": len(children),
            "retention_review_count": len(reviews),
            "retirement_event_count": len(retirements),
            "restoration_event_count": len(restorations),
            "latest_temporary_child": children[0] if children else None,
            "latest_retention_review": reviews[0] if reviews else None,
            "latest_retirement": retirements[0] if retirements else None,
            "latest_restoration": restorations[0] if restorations else None,
            "teacher_governance": teacher_governance,
            "roster_policy": "open-ended-canon-and-cluster9-reconciled",
            "route_policy": "deny-by-default-unless-active-complete-ao-and-expert-contracts-exist",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }

    def register_teacher_candidate(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(payload or {})
        normalized["metadata"] = {}
        normalized["source_url"] = _safe_public_source_url(normalized.get("source_url"))
        candidate = self.cluster9_registry.register_teacher_candidate(normalized, replace=True)
        created_at = _utcnow()
        artifact_ref = (
            f"genesis/node-contracts/teacher-candidate-intakes/{_artifact_id(candidate.candidate_id)}.json"
        )
        passport = self.cluster9_registry.teacher_capability_passport(candidate.candidate_id)
        record = {
            "schema_version": "nexusnet-genesis-teacher-candidate-intake-v1",
            "surface_id": "genesis-layer13-teacher-candidate-intake",
            "candidate_id": candidate.candidate_id,
            "artifact_ref": artifact_ref,
            "status": "candidate-intake-recorded",
            "candidate": candidate.model_dump(mode="json"),
            "teacher_capability_passport": passport.model_dump(mode="json"),
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }
        self._write_json(record, artifact_ref=artifact_ref)
        self._publish_event(
            event_type="genesis.teacher_candidate.intake_recorded",
            correlation_ref=f"teacher-candidate::{candidate.candidate_id}",
            session_ref_digest=None,
            artifact_refs=[artifact_ref, *passport.source_refs, *candidate.benchmark_refs],
            created_at=created_at,
        )
        return record

    def teacher_governance_summary(self) -> dict[str, Any]:
        intakes = self._artifacts(self.teacher_candidates_dir)
        verifications = self._artifacts(self.birth_verifications_dir)
        authorizations = self._artifacts(self.teacher_use_authorizations_dir)
        replacement_recommendations = self._artifacts(self.teacher_replacement_recommendations_dir)
        candidates = self.cluster9_registry.teacher_candidates()
        return {
            "schema_version": "nexusnet-genesis-layer13-teacher-governance-v1",
            "surface_id": "genesis-layer13-teacher-governance",
            "status": "live-evidence" if intakes or verifications or authorizations else "awaiting-live-birth-evidence",
            "honest_status_label": (
                "teacher-candidate-intake-and-birth-verification-live"
                if intakes or verifications
                else "teacher-execution-rights-live"
                if authorizations
                else "teacher-replacement-recommendation-live"
                if replacement_recommendations
                else "teacher-passports-present-live-birth-verification-not-yet-observed"
            ),
            "mother_brain_authority": "NexusBrain",
            "candidate_count": len(candidates),
            "promotion_ready_candidate_count": sum(
                1
                for candidate in candidates
                if self.cluster9_registry.teacher_capability_passport(candidate.candidate_id).promotion_allowed
            ),
            "persisted_candidate_intake_count": len(intakes),
            "persisted_candidate_ids": [
                str(record.get("candidate_id")) for record in intakes if record.get("candidate_id")
            ],
            "birth_verification_count": len(verifications),
            "verified_birth_count": sum(1 for record in verifications if record.get("passed") is True),
            "blocked_birth_count": sum(1 for record in verifications if record.get("passed") is not True),
            "latest_birth_verification": verifications[0] if verifications else None,
            "teacher_use_authorization_count": len(authorizations),
            "authorized_teacher_use_count": sum(
                1 for record in authorizations if record.get("teacher_or_distillation_use_authorized") is True
            ),
            "denied_teacher_use_count": sum(
                1 for record in authorizations if record.get("teacher_or_distillation_use_authorized") is not True
            ),
            "latest_teacher_use_authorization": authorizations[0] if authorizations else None,
            "teacher_replacement_recommendation_count": len(replacement_recommendations),
            "latest_teacher_replacement_recommendation": (
                replacement_recommendations[0] if replacement_recommendations else None
            ),
            "teacher_pairing_policy": "two-plus-rights-cleared-domain-fit-teachers-required-before-node-birth",
            "high_risk_domain_policy": "high-risk-birth-requires-cleared-reviewer-teacher-and-risk-scope",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }

    def authorize_teacher_use(self, *, teacher_id: str, usage_intent: str) -> dict[str, Any]:
        if usage_intent != "teacher-or-distillation":
            raise ValueError("teacher use authorization only supports teacher-or-distillation")
        normalized_teacher_id = _required_ref({"teacher_id": teacher_id}, "teacher_id")
        passport = self.cluster9_registry.teacher_capability_passport(normalized_teacher_id)
        created_at = _utcnow()
        authorization_id = (
            f"teacher-use::{_artifact_id(normalized_teacher_id)}::{_digest(f'{normalized_teacher_id}:{created_at}')[:16]}"
        )
        artifact_ref = f"genesis/node-contracts/teacher-use-authorizations/{_artifact_id(authorization_id)}.json"
        allowed = passport.promotion_allowed
        record = {
            "schema_version": "nexusnet-genesis-layer13-teacher-use-authorization-v1",
            "surface_id": "genesis-layer13-teacher-use-authorization",
            "authorization_id": authorization_id,
            "artifact_ref": artifact_ref,
            "teacher_id": passport.teacher_id,
            "usage_intent": usage_intent,
            "status": (
                "authorized-teacher-or-distillation-use"
                if allowed
                else "blocked-teacher-or-distillation-use"
            ),
            "teacher_or_distillation_use_authorized": allowed,
            "license_status": "approved" if allowed else "needs-review",
            "rights_refs": _safe_refs(passport.source_refs),
            "teacher_capability_passport": passport.model_dump(mode="json"),
            "blockers": _safe_refs(passport.promotion_blockers),
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }
        self._write_json(record, artifact_ref=artifact_ref)
        self._publish_event(
            event_type=(
                "genesis.teacher_use.authorized"
                if allowed
                else "genesis.teacher_use.blocked"
            ),
            correlation_ref=authorization_id,
            session_ref_digest=None,
            artifact_refs=[artifact_ref, *passport.source_refs, *passport.promotion_blockers],
            created_at=created_at,
        )
        return record

    def record_teacher_replacement_recommendation(
        self,
        *,
        teacher_id: str,
        replacement_target: str,
        takeover: Any,
    ) -> dict[str, Any]:
        normalized_teacher_id = _required_ref({"teacher_id": teacher_id}, "teacher_id")
        normalized_replacement_target = _required_ref(
            {"replacement_target": replacement_target},
            "replacement_target",
        )
        takeover_payload = (
            takeover.model_dump(mode="json") if hasattr(takeover, "model_dump") else dict(takeover or {})
        )
        takeover_evidence = dict(takeover_payload.get("evidence") or {})
        replacement = dict(takeover_evidence.get("teacher_replacement_decision") or {})
        shadow_record = dict(takeover_evidence.get("retirement_shadow_record") or {})
        created_at = _utcnow()
        recommendation_id = (
            "teacher-replacement::"
            f"{_artifact_id(normalized_teacher_id)}::{_digest(f'{normalized_replacement_target}:{created_at}')[:16]}"
        )
        artifact_ref = (
            "genesis/node-contracts/teacher-replacement-recommendations/"
            f"{_artifact_id(recommendation_id)}.json"
        )
        takeover_decision = _safe_ref(takeover_payload.get("decision")) or "shadow"
        record = {
            "schema_version": "nexusnet-genesis-layer13-teacher-replacement-recommendation-v1",
            "surface_id": "genesis-layer13-teacher-replacement-recommendation",
            "recommendation_id": recommendation_id,
            "artifact_ref": artifact_ref,
            "teacher_id": normalized_teacher_id,
            "replacement_target": normalized_replacement_target,
            "status": (
                "replacement-recommended-awaiting-admin-approval"
                if takeover_decision == "takeover"
                else "replacement-recommended-shadow"
            ),
            "takeover_decision": takeover_decision,
            "replacement_decision": _safe_ref(replacement.get("decision")) or "shadow",
            "retirement_shadow_decision": _safe_ref(shadow_record.get("decision")) or "hold",
            "evidence_refs": _safe_refs(
                [
                    takeover_payload.get("teacher_evidence_bundle_id"),
                    takeover_payload.get("takeover_scorecard_id"),
                    takeover_payload.get("takeover_trend_report_id"),
                    takeover_payload.get("replacement_readiness_report_id"),
                    shadow_record.get("record_id"),
                    shadow_record.get("artifact_path"),
                ]
            ),
            "archive_not_delete": True,
            "rollback_required": True,
            "admin_approval_required": True,
            "active_teacher_retired": False,
            "replacement_activation_allowed": False,
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }
        self._write_json(record, artifact_ref=artifact_ref)
        self._publish_event(
            event_type="genesis.teacher_replacement.recommended",
            correlation_ref=recommendation_id,
            session_ref_digest=None,
            artifact_refs=[artifact_ref, *record["evidence_refs"]],
            created_at=created_at,
        )
        return record

    def contracts(self) -> list[dict[str, Any]]:
        contracts = [dict(contract) for contract in self._base_contracts.values()]
        contracts.extend(self._artifacts(self.children_dir))
        return [
            self._with_lifecycle(contract)
            for contract in sorted(contracts, key=lambda item: str(item.get("contract_ref") or ""))
        ]

    def contract(self, contract_ref: str) -> dict[str, Any] | None:
        normalized = str(contract_ref or "").strip()
        contract = next(
            (item for item in self.contracts() if item.get("contract_ref") == normalized),
            None,
        )
        return dict(contract) if contract else None

    def authorize_route(
        self,
        *,
        selected_ao: str,
        selected_expert: str,
        trace_ref: str,
        session_ref_digest: str,
    ) -> dict[str, Any]:
        selected_ao = str(selected_ao or "").strip()
        selected_expert = str(selected_expert or "conversationalist").strip()
        session_ref_digest = _normalize_session_ref_digest(session_ref_digest)
        ao_contract = self._resolve_contract("assistant_orchestrator", selected_ao)
        expert_contract = self._resolve_contract("expert", selected_expert)
        blockers: list[str] = []
        if ao_contract is None:
            blockers.append("ao_contract_missing")
        elif ao_contract.get("lifecycle_state") != "active" or not _contract_complete(ao_contract):
            blockers.append("ao_contract_not_active")
        if expert_contract is None:
            blockers.append("expert_contract_missing")
        elif expert_contract.get("lifecycle_state") != "active" or not _contract_complete(expert_contract):
            blockers.append("expert_contract_not_active")
        created_at = _utcnow()
        receipt_id = f"node-contract-route::{_digest('|'.join([trace_ref, selected_ao, selected_expert, created_at]))}"
        artifact_ref = f"genesis/node-contracts/route-receipts/{_artifact_id(receipt_id)}.json"
        packet = {
            "schema_version": "nexusnet-genesis-node-contract-route-receipt-v1",
            "surface_id": "genesis-node-contract-route-receipt",
            "receipt_id": receipt_id,
            "artifact_ref": artifact_ref,
            "status": "route-authorized" if not blockers else "blocked-uncontracted-node",
            "route_allowed": not blockers,
            "trace_ref": _safe_ref(trace_ref),
            "session_ref_digest": session_ref_digest,
            "selected_ao": selected_ao,
            "selected_expert": selected_expert,
            "ao_contract_ref": ao_contract.get("contract_ref") if ao_contract else None,
            "expert_contract_ref": expert_contract.get("contract_ref") if expert_contract else None,
            "blockers": blockers,
            "enforced_boundaries": {
                "ao_capability_boundaries": ao_contract.get("capability_boundaries", []) if ao_contract else [],
                "expert_capability_boundaries": expert_contract.get("capability_boundaries", []) if expert_contract else [],
                "tool_permission_refs": _unique(
                    [
                        *(ao_contract.get("tool_permission_refs", []) if ao_contract else []),
                        *(expert_contract.get("tool_permission_refs", []) if expert_contract else []),
                    ]
                ),
                "memory_scope_refs": _unique(
                    [
                        *(ao_contract.get("memory_scope_refs", []) if ao_contract else []),
                        *(expert_contract.get("memory_scope_refs", []) if expert_contract else []),
                    ]
                ),
            },
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        packet["shared_event_spine"] = self._publish_event(
            event_type="genesis.node_contract.route_authorized" if not blockers else "genesis.node_contract.route_blocked",
            correlation_ref=receipt_id,
            session_ref_digest=session_ref_digest,
            artifact_refs=[artifact_ref, packet.get("ao_contract_ref"), packet.get("expert_contract_ref")],
            created_at=created_at,
        )
        self._write_json(packet, artifact_ref=artifact_ref)
        return packet

    def register_temporary_child(self, payload: dict[str, Any]) -> dict[str, Any]:
        child_id = _required_ref(payload, "child_id")
        parent_contract_ref = _required_ref(payload, "parent_contract_ref")
        parent = self.contract(parent_contract_ref)
        if parent is None or parent.get("lifecycle_state") != "active":
            raise ValueError("an active parent_contract_ref is required")
        contract_ref = f"temporary-expert-contract::{_artifact_id(child_id)}"
        artifact_ref = f"genesis/node-contracts/temporary-children/{_artifact_id(child_id)}.json"
        existing = self._read_artifact(artifact_ref)
        if existing:
            return self._with_lifecycle(existing)
        created_at = _utcnow()
        domain = _required_ref(payload, "domain")
        risk_tier = str(payload.get("risk_tier") or "medium").strip().lower()
        if risk_tier not in {"low", "medium", "high", "critical"}:
            raise ValueError("risk_tier must be low, medium, high, or critical")
        teacher_birth_verification = self.cluster9_registry.verify_birth_pairing(
            node_id=f"temporary.{_artifact_id(child_id)}",
            node_type="temporary_expert",
            domain=domain,
            risk_tier=risk_tier,
            teacher_ids=[str(item) for item in payload.get("teacher_ids") or []],
            source_refs=[str(item) for item in payload.get("source_refs") or []],
            required_teacher_count=2,
        )
        verification_id = (
            f"teacher-birth-verification::{_digest('|'.join([child_id, domain, risk_tier, created_at]))}"
        )
        verification_artifact_ref = (
            f"genesis/node-contracts/teacher-birth-verifications/{_artifact_id(verification_id)}.json"
        )
        teacher_birth_verification.update(
            {
                "schema_version": "nexusnet-genesis-layer13-teacher-birth-verification-v1",
                "verification_id": verification_id,
                "artifact_ref": verification_artifact_ref,
                "child_id": child_id,
                "parent_contract_ref": parent_contract_ref,
                "created_at": created_at,
            }
        )
        self._write_json(teacher_birth_verification, artifact_ref=verification_artifact_ref)
        self._publish_event(
            event_type=(
                "genesis.teacher_birth.verified"
                if teacher_birth_verification.get("passed") is True
                else "genesis.teacher_birth.blocked"
            ),
            correlation_ref=verification_id,
            session_ref_digest=None,
            artifact_refs=[
                verification_artifact_ref,
                parent_contract_ref,
                *teacher_birth_verification.get("teacher_ids", []),
            ],
            created_at=created_at,
        )
        if teacher_birth_verification.get("passed") is not True:
            raise ValueError(
                "teacher birth verification blocked: "
                + ", ".join(teacher_birth_verification.get("findings") or ["unknown_teacher_gate"])
            )
        contract = _node_contract(
            contract_ref=contract_ref,
            node_id=f"temporary.{_artifact_id(child_id)}",
            node_name=child_id,
            node_kind="temporary_expert",
            hierarchy="temporary-expert-mini-nexusnet",
            capabilities=_safe_refs(payload.get("capability_refs") or []),
            source_refs=_safe_refs(payload.get("source_refs") or []),
            lifecycle_state="shadow",
        )
        contract.update(
            {
                "artifact_ref": artifact_ref,
                "parent_contract_ref": parent_contract_ref,
                "status": "shadow-awaiting-retention-review",
                "production_route_allowed": False,
                "retention_review_required": True,
                "permanent_birth_allowed": False,
                "domain": domain,
                "risk_tier": risk_tier,
                "teacher_ids": teacher_birth_verification.get("teacher_ids", []),
                "teacher_birth_verification_ref": verification_artifact_ref,
                "teacher_birth_verification": teacher_birth_verification,
                "expert_domain_passport": teacher_birth_verification.get("expert_domain_passport"),
                "created_at": created_at,
            }
        )
        self._write_json(contract, artifact_ref=artifact_ref)
        self._publish_event(
            event_type="genesis.node_contract.temporary_child_registered",
            correlation_ref=contract_ref,
            session_ref_digest=None,
            artifact_refs=[artifact_ref, contract_ref, parent_contract_ref],
            created_at=created_at,
        )
        return contract

    def _replay_teacher_candidates(self) -> None:
        for record in reversed(self._artifacts(self.teacher_candidates_dir)):
            candidate = record.get("candidate") if isinstance(record.get("candidate"), dict) else None
            if candidate is None:
                continue
            try:
                self.cluster9_registry.register_teacher_candidate(candidate, replace=True)
            except ValueError:
                continue

    def review_temporary_child(self, child_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        child_ref = f"genesis/node-contracts/temporary-children/{_artifact_id(child_id)}.json"
        child = self._read_artifact(child_ref)
        if not child:
            raise KeyError(f"unknown temporary child: {child_id}")
        decision = str(payload.get("decision") or "").strip()
        if decision not in {"retain-shadow", "retire"}:
            raise ValueError("decision must be retain-shadow or retire")
        controls = _required_controls(
            payload,
            [
                "sandbox_eval_ref",
                "eval_refs",
                "rollback_plan_ref",
                "governance_approval_ref",
                "admin_approval_ref",
            ],
        )
        immune_governance = getattr(self, "immune_governance", None)
        immune_decision = (
            immune_governance.require_decision(
                decision_id=payload.get("immune_governance_decision_id"),
                candidate_ref=str(child.get("contract_ref") or ""),
                candidate_kind="temporary-expert-retention",
            )
            if immune_governance is not None
            else None
        )
        created_at = _utcnow()
        review_id = f"node-contract-retention-review::{_digest('|'.join([str(child.get('contract_ref')), decision, created_at]))}"
        artifact_ref = f"genesis/node-contracts/retention-reviews/{_artifact_id(review_id)}.json"
        status = "retention-reviewed-shadow" if decision == "retain-shadow" else "retention-reviewed-retired"
        packet = {
            "schema_version": "nexusnet-genesis-node-retention-review-v1",
            "surface_id": "genesis-node-retention-review",
            "review_id": review_id,
            "artifact_ref": artifact_ref,
            "child_id": child_id,
            "child_contract_ref": child.get("contract_ref"),
            "parent_contract_ref": child.get("parent_contract_ref"),
            "decision": decision,
            "status": status,
            "lifecycle_state": "shadow" if decision == "retain-shadow" else "archived-retired",
            "production_route_allowed": False,
            "permanent_birth_allowed": False,
            "controls": controls,
            "immune_governance_decision": immune_decision,
            "admin_actor_digest": _privacy_digest(str(payload.get("approved_by") or "admin")),
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        child.update(
            {
                "status": status,
                "lifecycle_state": packet["lifecycle_state"],
                "latest_retention_review_ref": artifact_ref,
                "retention_reviewed_at": created_at,
            }
        )
        self._write_json(child, artifact_ref=child_ref)
        self._write_json(packet, artifact_ref=artifact_ref)
        self._publish_event(
            event_type="genesis.node_contract.retention_reviewed",
            correlation_ref=review_id,
            session_ref_digest=None,
            artifact_refs=[artifact_ref, child.get("contract_ref"), (immune_decision or {}).get("decision_id"), *controls.values()],
            created_at=created_at,
        )
        return packet

    def retire_parent(self, payload: dict[str, Any]) -> dict[str, Any]:
        parent_contract_ref = _required_ref(payload, "parent_contract_ref")
        replacement_contract_ref = _required_ref(payload, "replacement_contract_ref")
        parent = self.contract(parent_contract_ref)
        replacement = self.contract(replacement_contract_ref)
        if parent is None or parent.get("lifecycle_state") != "active":
            raise ValueError("an active parent contract is required")
        if parent.get("node_kind") == "core":
            raise ValueError("the NexusBrain core contract cannot be retired through this route")
        if replacement is None or replacement.get("status") != "retention-reviewed-shadow":
            raise ValueError("replacement must be a retention-reviewed shadow child")
        controls = _required_controls(
            payload,
            [
                "sandbox_eval_ref",
                "eval_refs",
                "rollback_plan_ref",
                "archive_ref",
                "governance_approval_ref",
                "admin_approval_ref",
            ],
        )
        immune_governance = getattr(self, "immune_governance", None)
        retirement_candidate_ref = f"node-retirement::{parent_contract_ref}::{replacement_contract_ref}"
        immune_decision = (
            immune_governance.require_decision(
                decision_id=payload.get("immune_governance_decision_id"),
                candidate_ref=retirement_candidate_ref,
                candidate_kind="parent-expert-retirement",
            )
            if immune_governance is not None
            else None
        )
        created_at = _utcnow()
        retirement_id = f"node-contract-retirement::{_digest('|'.join([parent_contract_ref, replacement_contract_ref, created_at]))}"
        artifact_ref = f"genesis/node-contracts/retirements/{_artifact_id(retirement_id)}.json"
        archive_artifact_ref = f"genesis/node-contracts/archives/{_artifact_id(retirement_id)}.json"
        archive = {
            "schema_version": "nexusnet-genesis-node-contract-archive-v1",
            "surface_id": "genesis-node-contract-archive",
            "archive_ref": controls["archive_ref"],
            "archive_artifact_ref": archive_artifact_ref,
            "parent_contract": parent,
            "archived_at": created_at,
            "archive_not_delete": True,
            "raw_content_included": False,
        }
        packet = {
            "schema_version": "nexusnet-genesis-parent-retirement-v1",
            "surface_id": "genesis-parent-retirement",
            "retirement_id": retirement_id,
            "artifact_ref": artifact_ref,
            "parent_contract_ref": parent_contract_ref,
            "replacement_contract_ref": replacement_contract_ref,
            "status": "parent-archived-retired",
            "lifecycle_state": "archived-retired",
            "archive_ref": controls["archive_ref"],
            "archive_artifact_ref": archive_artifact_ref,
            "archive_not_delete": True,
            "parent_contract_preserved": True,
            "controls": controls,
            "immune_governance_decision": immune_decision,
            "admin_actor_digest": _privacy_digest(str(payload.get("approved_by") or "admin")),
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": True,
            "active_production_mutated": True,
            "mutation_boundary": "contract-route-passivation-and-lineage-archive-no-node-or-evidence-deletion",
        }
        self._write_json(archive, artifact_ref=archive_artifact_ref)
        self._write_json(packet, artifact_ref=artifact_ref)
        self._publish_event(
            event_type="genesis.node_contract.parent_retired",
            correlation_ref=retirement_id,
            session_ref_digest=None,
            artifact_refs=[
                artifact_ref,
                archive_artifact_ref,
                parent_contract_ref,
                replacement_contract_ref,
                (immune_decision or {}).get("decision_id"),
            ],
            created_at=created_at,
        )
        return packet

    def restore_parent(self, payload: dict[str, Any]) -> dict[str, Any]:
        parent_contract_ref = _required_ref(payload, "parent_contract_ref")
        retirement_id = _required_ref(payload, "retirement_id")
        retirement = next(
            (item for item in self._artifacts(self.retirements_dir) if item.get("retirement_id") == retirement_id),
            None,
        )
        if retirement is None or retirement.get("parent_contract_ref") != parent_contract_ref:
            raise ValueError("retirement_id does not match parent_contract_ref")
        _required_controls(payload, ["governance_approval_ref", "admin_approval_ref"])
        if self.contract(parent_contract_ref) is None:
            raise ValueError("archived parent contract is unavailable")
        created_at = _utcnow()
        restoration_id = f"node-contract-restoration::{_digest('|'.join([retirement_id, created_at]))}"
        artifact_ref = f"genesis/node-contracts/restorations/{_artifact_id(restoration_id)}.json"
        packet = {
            "schema_version": "nexusnet-genesis-parent-restoration-v1",
            "surface_id": "genesis-parent-restoration",
            "restoration_id": restoration_id,
            "artifact_ref": artifact_ref,
            "retirement_id": retirement_id,
            "parent_contract_ref": parent_contract_ref,
            "status": "parent-active-restored",
            "lifecycle_state": "active",
            "admin_actor_digest": _privacy_digest(str(payload.get("approved_by") or "admin")),
            "governance_approval_ref": _safe_ref(payload.get("governance_approval_ref")),
            "admin_approval_ref": _safe_ref(payload.get("admin_approval_ref")),
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": True,
            "active_production_mutated": True,
            "mutation_boundary": "restore-archived-contract-route-eligibility-with-lineage-preserved",
        }
        self._write_json(packet, artifact_ref=artifact_ref)
        self._publish_event(
            event_type="genesis.node_contract.parent_restored",
            correlation_ref=restoration_id,
            session_ref_digest=None,
            artifact_refs=[artifact_ref, retirement.get("archive_artifact_ref"), parent_contract_ref],
            created_at=created_at,
        )
        return packet

    def _build_base_contracts(self) -> dict[str, dict[str, Any]]:
        contracts: dict[str, dict[str, Any]] = {}
        for orchestrator in self.ao_registry.list():
            contract = dict(orchestrator.contract())
            contract["node_kind"] = "assistant_orchestrator"
            contract["node_id"] = f"ao.{_slug(orchestrator.name)}"
            contract["node_name"] = orchestrator.name
            contract["lifecycle_state"] = "active"
            contract["source_refs"] = ["ao-registry::canonical-open-ended-roster"]
            contract["archive_not_delete"] = True
            contracts[str(contract["contract_ref"])] = contract
        for expert in self.canon_registry.expert_roster():
            contract = _node_contract(
                contract_ref=f"expert-contract::{expert.capsule_id}",
                node_id=f"expert.{expert.capsule_id}",
                node_name=expert.name,
                node_kind="expert",
                hierarchy="expert-mini-nexusnet",
                capabilities=list(expert.capabilities),
                source_refs=list(expert.evidence),
                lifecycle_state="active",
                tool_permission_refs=list(expert.permissions) or ["tool-policy::expert-deny-by-default"],
                memory_scope_refs=list(expert.memory_access) or ["memory-scope::expert-scoped"],
            )
            contracts[str(contract["contract_ref"])] = contract
        for expert_id, capabilities in {
            "general": ["general-runtime-fallback", "brain-mediated-routing"],
            "release-health": ["release-health-analysis", "repair-proposal-review"],
            "release-wrapper-self-repair": ["self-repair-guard", "governed-update-review"],
        }.items():
            contract = _node_contract(
                contract_ref=f"internal-expert-contract::{expert_id}",
                node_id=f"expert.{expert_id}",
                node_name=expert_id,
                node_kind="expert",
                hierarchy="internal-runtime-expert-mini-nexusnet",
                capabilities=capabilities,
                source_refs=["genesis-build-order::layer9-internal-runtime-contract"],
                lifecycle_state="active",
            )
            contracts[str(contract["contract_ref"])] = contract
        for node in self.cluster9_registry.list_nodes():
            if node.node_type == "assistant_orchestrator":
                kind = "assistant_orchestrator"
                hierarchy = "assistant-orchestrator-mini-nexusnet"
            elif node.node_type in {"expert", "temporary_expert"}:
                kind = node.node_type
                hierarchy = "expert-mini-nexusnet" if kind == "expert" else "temporary-expert-mini-nexusnet"
            elif node.node_type == "orchestrator":
                kind = "orchestrator"
                hierarchy = "orchestrator-department-brain"
            else:
                kind = "core"
                hierarchy = "nexusbrain-mother-brain"
            contract = _node_contract(
                contract_ref=f"cluster9-contract::{node.node_id}",
                node_id=node.node_id,
                node_name=node.display_name,
                node_kind=kind,
                hierarchy=hierarchy,
                capabilities=[node.domain, *node.birth_gates],
                source_refs=list(node.source_refs),
                lifecycle_state="shadow" if kind == "temporary_expert" else "active",
            )
            contract["cluster9_reconciliation_ref"] = f"cluster9-node::{node.node_id}"
            contract["expert_ref"] = node.expert_ref
            contract["ao_ref"] = node.ao_ref
            contract["orchestrator_ref"] = node.orchestrator_ref
            contracts[str(contract["contract_ref"])] = contract
        return contracts

    def _resolve_contract(self, node_kind: str, node_ref: str) -> dict[str, Any] | None:
        normalized = str(node_ref or "").strip()
        expected_kinds = {node_kind}
        if node_kind == "expert":
            expected_kinds.add("temporary_expert")
        candidates = [
            contract
            for contract in self.contracts()
            if contract.get("node_kind") in expected_kinds
        ]
        direct_refs = {
            normalized,
            f"ao-contract::{normalized}" if node_kind == "assistant_orchestrator" else f"expert-contract::{normalized}",
        }
        for contract in candidates:
            aliases = {
                str(contract.get("contract_ref") or ""),
                str(contract.get("node_id") or ""),
                str(contract.get("node_name") or ""),
                str(contract.get("expert_ref") or ""),
                str(contract.get("ao_ref") or ""),
            }
            if direct_refs & aliases:
                return contract
        return None

    def _with_lifecycle(self, contract: dict[str, Any]) -> dict[str, Any]:
        copy = dict(contract)
        contract_ref = str(copy.get("contract_ref") or "")
        lifecycle_events = [
            item
            for item in [
                *self._artifacts(self.retirements_dir),
                *self._artifacts(self.restorations_dir),
            ]
            if item.get("parent_contract_ref") == contract_ref
        ]
        lifecycle_events.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        if lifecycle_events:
            copy["lifecycle_state"] = lifecycle_events[0].get("lifecycle_state")
            copy["latest_lifecycle_event_ref"] = lifecycle_events[0].get("artifact_ref")
        copy["archive_not_delete"] = True
        return copy

    def _publish_event(
        self,
        *,
        event_type: str,
        correlation_ref: str,
        session_ref_digest: str | None,
        artifact_refs: list[Any],
        created_at: str,
    ) -> dict[str, Any]:
        return self.event_spine.publish_event(
            event_type=event_type,
            source_surface_id="genesis-o-ao-expert-contract-registry",
            correlation_ref=correlation_ref,
            session_ref_digest=session_ref_digest,
            privacy_label="sanitized-genesis-node-contract-evidence",
            artifact_refs=_safe_refs(artifact_refs),
            planes=["authority", "hive", "contracts", "governance", "replay"],
            priority_trails=[
                {"topic": "genesis-node-contracts", "strength": 1.0, "artifact_ref": correlation_ref}
            ],
            created_at=created_at,
        )

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
        records.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        return records

    def _write_json(self, payload: dict[str, Any], *, artifact_ref: str) -> None:
        path = self.artifacts_dir / artifact_ref
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(path)

    def _read_artifact(self, artifact_ref: str) -> dict[str, Any]:
        try:
            value = json.loads((self.artifacts_dir / artifact_ref).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return value if isinstance(value, dict) else {}


def _node_contract(
    *,
    contract_ref: str,
    node_id: str,
    node_name: str,
    node_kind: str,
    hierarchy: str,
    capabilities: list[str],
    source_refs: list[str],
    lifecycle_state: str,
    tool_permission_refs: list[str] | None = None,
    memory_scope_refs: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "nexusnet-genesis-node-contract-v1",
        "surface_id": "genesis-o-ao-expert-contract-registry",
        "contract_ref": contract_ref,
        "node_id": node_id,
        "node_name": node_name,
        "node_kind": node_kind,
        "brain_scale_hierarchy": hierarchy,
        "declared_capabilities": _unique(capabilities),
        "capability_boundaries": [
            "declared-capabilities-only",
            "no-direct-governance-bypass",
            "no-unscoped-local-state-access",
            "no-direct-active-production-mutation",
        ],
        "tool_permission_refs": tool_permission_refs or [f"tool-policy::{node_kind}-deny-by-default"],
        "memory_scope_refs": memory_scope_refs or [f"memory-scope::{node_kind}-scoped-by-reference"],
        "failure_visibility_refs": [
            "failure-visibility::genesis-event-spine",
            "failure-visibility::operator-control-panel",
        ],
        "self_improvement_participation": {
            "mode": "proposal-evidence-and-review-only",
            "direct_self_mutation_allowed": False,
            "governed_promotion_required": True,
        },
        "temporary_child_contract": {
            "mode": "sandbox-shadow-only",
            "retention_review_required": True,
            "permanent_birth_allowed": False,
        },
        "parent_retirement_contract": {
            "archive_not_delete": True,
            "admin_approval_required": True,
            "rollback_required": True,
        },
        "source_refs": _safe_refs(source_refs),
        "lifecycle_state": lifecycle_state,
        "archive_not_delete": True,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
    }


def _contract_complete(contract: dict[str, Any]) -> bool:
    return all(
        contract.get(key)
        for key in (
            "contract_ref",
            "node_id",
            "node_kind",
            "brain_scale_hierarchy",
            "capability_boundaries",
            "tool_permission_refs",
            "memory_scope_refs",
            "failure_visibility_refs",
            "self_improvement_participation",
            "temporary_child_contract",
            "parent_retirement_contract",
        )
    )


def _required_ref(payload: dict[str, Any], name: str) -> str:
    value = _safe_ref(payload.get(name))
    if not value:
        raise ValueError(f"{name} is required")
    return value


def _safe_public_source_url(value: Any) -> str:
    raw = str(value or "").strip()
    parsed = urlsplit(raw)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("source_url must be a public HTTPS URL without credentials, query, or fragment")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def _required_controls(payload: dict[str, Any], names: list[str]) -> dict[str, Any]:
    controls: dict[str, Any] = {}
    missing: list[str] = []
    for name in names:
        value = payload.get(name)
        if name == "eval_refs":
            refs = _safe_refs(value or [])
            controls[name] = refs
            if not refs:
                missing.append(name)
        else:
            ref = _safe_ref(value)
            controls[name] = ref
            if not ref:
                missing.append(name)
    if missing:
        raise ValueError(f"required controls missing: {', '.join(missing)}")
    return controls


def _safe_refs(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple, set)):
        values = [values]
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


def _unique(values: Any) -> list[str]:
    output: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in output:
            output.append(text)
    return output


def _artifact_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", str(value or "artifact")).strip("-")


def _slug(value: str) -> str:
    return _artifact_id(value).lower()


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _privacy_digest(value: str | None) -> str:
    return "sha256:" + hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _normalize_session_ref_digest(value: str | None) -> str:
    text = str(value or "").strip()
    if text.startswith("sha256:"):
        return text
    if re.fullmatch(r"[a-f0-9]{16}", text):
        return f"sha256:{text}"
    return _privacy_digest(text)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
