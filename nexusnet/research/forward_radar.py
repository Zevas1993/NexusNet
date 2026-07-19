from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.hive.core_brain_control import RecursiveDreamerGate
from nexusnet.policy import PolicyKernel


SourceQuality = Literal["primary", "verified", "secondary", "unverified"]
LicenseStatus = Literal["approved", "blocked", "needs_review"]
SecurityReview = Literal["passed", "blocked", "needs_review"]


class ForwardRadarCandidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    radar_id: str
    title: str
    lane: str
    summary: str
    source_refs: list[str] = Field(default_factory=list)
    source_quality: SourceQuality = "unverified"
    license_status: LicenseStatus = "needs_review"
    security_review: SecurityReview = "needs_review"
    runtime_evidence_refs: list[str] = Field(default_factory=list)
    eval_refs: list[str] = Field(default_factory=list)
    observability_refs: list[str] = Field(default_factory=list)
    rollback_plan: str = ""
    operator_approved: bool = False
    open_first: bool = True
    local_first: bool = True
    upstream_harness_ledger_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelReleaseObservationRequest(BaseModel):
    """Sanitized metadata from a local/static model-release source adapter."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    model_id: str
    provider: str
    release_url: str
    release_date: str | None = None
    source_refs: list[str] = Field(default_factory=list)
    teacher_roles: list[str] = Field(default_factory=list)
    domain_scope: list[str] = Field(default_factory=list)
    risk_scope: list[str] = Field(default_factory=lambda: ["medium"])
    license_gate: LicenseStatus = "needs_review"
    privacy_gate: LicenseStatus = "needs_review"
    hardware_gate: LicenseStatus = "needs_review"
    cost_gate: LicenseStatus = "needs_review"
    security_review: SecurityReview = "needs_review"


class DowntimeBenchmarkRequest(BaseModel):
    """Capacity-gated request that can only produce a dry-run benchmark packet."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    serving: bool = False
    temp_c: float = 0.0
    free_vram_mb: float = 0.0
    budget_available: bool = False
    release_gate_open: bool = False


class BoundedSmokeEvalRequest(BaseModel):
    """A metadata-only smoke evaluation bound to a queued downtime packet."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    packet_id: str


class SyntheticCapabilityFixtureRequest(BaseModel):
    """Run a deterministic local fixture after a persisted metadata smoke evaluation."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    smoke_eval_id: str


class ForwardRadarRegistry:
    def __init__(self, *, artifacts_dir: Path | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "research" / "forward-radar" if self.artifacts_dir else None
        self.benchmark_packets_dir = (
            self.artifacts_dir / "research" / "model-release-downtime-benchmarks"
            if self.artifacts_dir
            else None
        )
        self.smoke_evals_dir = (
            self.artifacts_dir / "research" / "model-release-smoke-evals"
            if self.artifacts_dir
            else None
        )
        self.synthetic_fixture_evals_dir = (
            self.artifacts_dir / "research" / "model-release-synthetic-fixture-evals"
            if self.artifacts_dir
            else None
        )
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        if self.benchmark_packets_dir is not None:
            self.benchmark_packets_dir.mkdir(parents=True, exist_ok=True)
        if self.smoke_evals_dir is not None:
            self.smoke_evals_dir.mkdir(parents=True, exist_ok=True)
        if self.synthetic_fixture_evals_dir is not None:
            self.synthetic_fixture_evals_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []
        self._memory_benchmark_packets: list[dict[str, Any]] = []
        self._memory_smoke_evals: list[dict[str, Any]] = []
        self._memory_synthetic_fixture_evals: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()
        self.teacher_candidate_registry: Any | None = None
        self.tool_action_harness: Any | None = None

    def review(self, radar_id: str, request: ForwardRadarCandidateRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, ForwardRadarCandidateRequest) else ForwardRadarCandidateRequest.model_validate(request)
        upstream_harness_ledger_gate = _upstream_harness_ledger_gate(normalized)
        review_findings = _review_findings(radar_id, normalized, upstream_harness_ledger_gate=upstream_harness_ledger_gate)
        gate_summary = _gate_summary(normalized)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        hard_blocked = _has_hard_fail(review_findings)
        promotion_allowed = gate_summary["failed_gate_count"] == 0 and policy_scan.summary.active_hard_fail_count == 0 and not hard_blocked
        status = _status(normalized, promotion_allowed=promotion_allowed, hard_blocked=hard_blocked)
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "forward-radar",
            "radar_id": normalized.radar_id,
            "title": normalized.title,
            "lane": normalized.lane,
            "summary": normalized.summary,
            "status": status,
            "runtime_state": "live-bound" if promotion_allowed else "research-candidate",
            "promotion_allowed": promotion_allowed,
            "created_at": utcnow().isoformat(),
            "source_refs": normalized.source_refs,
            "source_quality": normalized.source_quality,
            "license_status": normalized.license_status,
            "security_review": normalized.security_review,
            "runtime_evidence_refs": normalized.runtime_evidence_refs,
            "eval_refs": normalized.eval_refs,
            "observability_refs": normalized.observability_refs,
            "rollback_plan": normalized.rollback_plan,
            "operator_approved": normalized.operator_approved,
            "open_first": normalized.open_first,
            "local_first": normalized.local_first,
            "upstream_harness_ledger_gate": upstream_harness_ledger_gate,
            "gate_summary": gate_summary,
            "review_findings": review_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "promotion_boundary": "forward-radar-candidates-require-source-license-security-runtime-eval-observability-rollback-and-operator-gates",
            "operator_actions": _operator_actions(),
            "metadata": normalized.metadata,
        }
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_records(limit=limit)
        promotion_ready_count = sum(1 for record in records if record.get("status") == "promotion-ready")
        watchlist_count = sum(1 for record in records if record.get("status") == "watchlist")
        blocked_count = sum(1 for record in records if record.get("status") == "blocked")
        latest_candidate = records[0] if records else None
        runtime_state = "static-canon"
        if records:
            if blocked_count or latest_candidate.get("status") == "blocked":
                runtime_state = "degraded"
            elif promotion_ready_count == len(records):
                runtime_state = "live-bound"
            else:
                runtime_state = "research-candidate"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "forward-radar",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "candidate_count": len(records),
            "promotion_ready_count": promotion_ready_count,
            "watchlist_count": watchlist_count,
            "blocked_count": blocked_count,
            "latest_candidate": latest_candidate,
            "candidates": records,
            "required_gates": _required_gates(),
            "operator_actions": _operator_actions(),
        }

    def observe_model_release(
        self,
        request: ModelReleaseObservationRequest | dict[str, Any],
    ) -> dict[str, Any]:
        if self.teacher_candidate_registry is None:
            raise RuntimeError("model release observation blocked because the Genesis teacher candidate registry is unavailable")
        normalized = (
            request
            if isinstance(request, ModelReleaseObservationRequest)
            else ModelReleaseObservationRequest.model_validate(request)
        )
        candidate_id = _safe_identifier(normalized.candidate_id, prefix="model")
        existing = self._teacher_candidate(candidate_id)
        source_refs = _unique_refs(
            [*(existing.source_refs if existing is not None else []), *normalized.source_refs]
        )
        if not source_refs:
            source_refs = [
                f"model-release::{_safe_identifier(normalized.provider, prefix='provider')}::{candidate_id}"
            ]
        teacher_roles = _unique_roles(
            [*(existing.teacher_roles if existing is not None else []), *normalized.teacher_roles]
        )
        domain_scope = _unique_refs(
            [*(existing.domain_scope if existing is not None else []), *normalized.domain_scope]
        )
        risk_scope = _unique_refs(
            [*(existing.risk_scope if existing is not None else []), *normalized.risk_scope]
        )
        candidate_status = (
            existing.candidate_status
            if existing is not None
            else _model_release_candidate_status(normalized)
        )
        candidate_payload = {
            "candidate_id": candidate_id,
            "model_or_tool_id": _safe_identifier(normalized.model_id, prefix="model"),
            "provider": _safe_identifier(normalized.provider, prefix="provider"),
            "source_url": normalized.release_url,
            "candidate_status": candidate_status,
            "teacher_roles": teacher_roles,
            "license_gate": _restrictive_gate(
                existing.license_gate if existing is not None else None,
                normalized.license_gate,
            ),
            "privacy_gate": _restrictive_gate(
                existing.privacy_gate if existing is not None else None,
                normalized.privacy_gate,
            ),
            "hardware_gate": _restrictive_gate(
                existing.hardware_gate if existing is not None else None,
                normalized.hardware_gate,
            ),
            "cost_gate": _restrictive_gate(
                existing.cost_gate if existing is not None else None,
                normalized.cost_gate,
            ),
            "eval_family": _unique_refs(
                [*(existing.eval_family if existing is not None else []), "model-release-smoke"]
            ),
            "domain_scope": domain_scope or ["general"],
            "risk_scope": risk_scope or ["medium"],
            "source_refs": source_refs,
            "benchmark_refs": list(existing.benchmark_refs) if existing is not None else [],
            "replacement_candidates": list(existing.replacement_candidates) if existing is not None else [],
        }
        intake = self.teacher_candidate_registry.register_teacher_candidate(candidate_payload)
        radar_id = f"model-release::{candidate_id}"
        radar_record = self.review(
            radar_id,
            ForwardRadarCandidateRequest(
                radar_id=radar_id,
                title=f"Model release observation: {candidate_payload['model_or_tool_id']}",
                lane="model-release",
                summary="Sanitized local/static model-release observation awaiting governed benchmark evidence.",
                source_refs=source_refs,
                source_quality="primary",
                license_status=candidate_payload["license_gate"],
                security_review=normalized.security_review,
                runtime_evidence_refs=[],
                eval_refs=list(candidate_payload["benchmark_refs"]),
                observability_refs=["genesis::teacher-candidate-intake"],
                rollback_plan="remove-from-shadow-benchmark-queue",
                operator_approved=False,
                metadata={
                    "candidate_id": candidate_id,
                    "candidate_status": candidate_payload["candidate_status"],
                    "release_date": _safe_ref(normalized.release_date),
                },
            ),
        )
        return {
            "schema_version": "nexusnet-model-release-radar-observation-v1",
            "surface_id": "model-release-radar",
            "authority": "NexusBrain",
            "radar_id": radar_id,
            "candidate_id": candidate_id,
            "status": candidate_payload["candidate_status"],
            "candidate_intake": intake,
            "forward_radar_status": radar_record["status"],
            "promotion_allowed": False,
            "active_teacher_promotion_allowed": False,
            "raw_content_included": False,
        }

    def model_release_summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = [
            record
            for record in self._list_records(limit=limit)
            if record.get("lane") == "model-release"
        ]
        public_records = [_public_model_release_record(record) for record in records]
        watchlist_count = sum(1 for record in public_records if record.get("status") == "watchlist")
        quarantined_count = sum(1 for record in public_records if record.get("status") == "quarantined")
        return {
            "schema_version": "nexusnet-model-release-radar-summary-v1",
            "surface_id": "model-release-radar",
            "authority": "NexusBrain",
            "status": "live-observation-evidence" if public_records else "awaiting-model-release-observation",
            "honest_status_label": (
                "model-release-observation-live-no-active-promotion"
                if public_records
                else "model-release-observation-not-yet-observed"
            ),
            "model_release_observation_count": len(public_records),
            "watchlist_count": watchlist_count,
            "quarantined_count": quarantined_count,
            "promotion_ready_count": 0,
            "latest_observation": public_records[0] if public_records else None,
            "observations": public_records,
            "downtime_scheduler": self.downtime_benchmark_summary(limit=limit),
            "smoke_eval_summary": self.smoke_eval_summary(limit=limit),
            "synthetic_fixture_summary": self.synthetic_fixture_summary(limit=limit),
            "automatic_actions": ["local-static-observation", "teacher-candidate-intake", "isolated-synthetic-fixture"],
            "blocked_actions": ["model-download", "benchmark-execution", "teacher-promotion", "training", "distillation"],
            "raw_content_included": False,
        }

    def schedule_downtime_benchmark(
        self,
        request: DowntimeBenchmarkRequest | dict[str, Any],
    ) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, DowntimeBenchmarkRequest)
            else DowntimeBenchmarkRequest.model_validate(request)
        )
        candidate_id = _safe_identifier(normalized.candidate_id, prefix="model")
        capacity = RecursiveDreamerGate().may_dream(
            temp_c=normalized.temp_c,
            free_vram_mb=normalized.free_vram_mb,
            serving=normalized.serving,
        )
        blockers = list(capacity["blocked_reasons"])
        if not normalized.budget_available:
            blockers.append("budget_unavailable")
        if not normalized.release_gate_open:
            blockers.append("release_gate_closed")
        candidate = self._teacher_candidate(candidate_id)
        if candidate is None:
            blockers.append("candidate_missing")
        created_at = utcnow().isoformat()
        packet = {
            "schema_version": "nexusnet-model-release-downtime-benchmark-packet-v1",
            "surface_id": "model-release-downtime-benchmark-scheduler",
            "packet_id": f"model-release-benchmark::{candidate_id}::{_digest(created_at)[:16]}",
            "candidate_id": candidate_id,
            "status": "skipped" if blockers else "queued-dry-run",
            "blockers": sorted(set(_safe_ref(blocker) for blocker in blockers if _safe_ref(blocker))),
            "capacity_gate": {
                "serving": normalized.serving,
                "temp_c": normalized.temp_c,
                "free_vram_mb": normalized.free_vram_mb,
                "may_schedule": not capacity["blocked_reasons"],
            },
            "budget_available": normalized.budget_available,
            "release_gate_open": normalized.release_gate_open,
            "candidate_status": candidate.candidate_status if candidate is not None else "missing",
            "planned_stages": (
                ["metadata-validation", "safety-provenance-scan", "hardware-cost-estimate"]
                if not blockers
                else []
            ),
            "evidence_refs": [
                f"forward-radar::model-release::{candidate_id}",
                f"teacher-candidate::{candidate_id}",
            ],
            "benchmark_execution_allowed": False,
            "model_download_allowed": False,
            "model_attach_allowed": False,
            "active_teacher_promotion_allowed": False,
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }
        self._persist_benchmark_packet(packet)
        return packet

    def downtime_benchmark_summary(self, *, limit: int = 50) -> dict[str, Any]:
        packets = self._list_benchmark_packets(limit=limit)
        return {
            "surface_id": "model-release-downtime-benchmark-scheduler",
            "status": "live-dry-run-evidence" if packets else "awaiting-downtime-benchmark-request",
            "honest_status_label": (
                "downtime-benchmark-dry-run-packets-live-no-execution"
                if packets
                else "downtime-benchmark-not-yet-observed"
            ),
            "packet_count": len(packets),
            "skipped_count": sum(1 for packet in packets if packet.get("status") == "skipped"),
            "queued_dry_run_count": sum(1 for packet in packets if packet.get("status") == "queued-dry-run"),
            "latest_packet": _public_benchmark_packet(packets[0]) if packets else None,
            "benchmark_execution_allowed": False,
            "raw_content_included": False,
        }

    def run_bounded_smoke_eval(
        self,
        request: BoundedSmokeEvalRequest | dict[str, Any],
    ) -> dict[str, Any]:
        if self.tool_action_harness is None:
            raise RuntimeError("bounded smoke eval blocked because the tool action harness is unavailable")
        normalized = (
            request
            if isinstance(request, BoundedSmokeEvalRequest)
            else BoundedSmokeEvalRequest.model_validate(request)
        )
        candidate_id = _safe_identifier(normalized.candidate_id, prefix="model")
        packet_id = _safe_ref(normalized.packet_id)
        packet = next(
            (item for item in self._list_benchmark_packets(limit=500) if item.get("packet_id") == packet_id),
            None,
        )
        candidate = self._teacher_candidate(candidate_id)
        if packet is None:
            raise ValueError("bounded smoke eval requires a persisted downtime benchmark packet")
        if packet.get("candidate_id") != candidate_id or packet.get("status") != "queued-dry-run":
            raise ValueError("bounded smoke eval requires a queued dry-run packet for the requested candidate")
        if candidate is None:
            raise ValueError("bounded smoke eval requires a persisted teacher candidate")
        sandbox_action = self.tool_action_harness.plan_action(
            action_id=f"model-release-metadata-inspect::{candidate_id}::{_digest(packet_id)[:16]}",
            tool_ref="model-release-radar",
            action_type="inspect",
            requested_effect="model-release-metadata-sandbox-smoke-eval",
            contains_private_data=False,
            sandbox_state="release-wrapper-shadow-observation",
            operator_approved=False,
            evidence_refs=[packet_id, f"teacher-candidate::{candidate_id}"],
        )
        checks = {
            "queued_dry_run_packet_present": True,
            "candidate_present": True,
            "no_private_content": True,
            "inspect_only_action": sandbox_action.get("action_type") == "inspect",
            "sandbox_execution_denied": sandbox_action.get("execution_allowed") is False,
        }
        passed = all(checks.values()) and sandbox_action.get("status") == "planned-shadow"
        created_at = utcnow().isoformat()
        result = {
            "schema_version": "nexusnet-model-release-bounded-smoke-eval-v1",
            "surface_id": "model-release-bounded-smoke-eval",
            "eval_id": f"model-release-smoke-eval::{candidate_id}::{_digest(created_at)[:16]}",
            "candidate_id": candidate_id,
            "packet_id": packet_id,
            "status": "synthetic-metadata-smoke-eval-passed" if passed else "synthetic-metadata-smoke-eval-blocked",
            "evaluation_kind": "synthetic-metadata-only",
            "checks": checks,
            "sandbox_action": sandbox_action,
            "benchmark_execution_allowed": False,
            "model_download_allowed": False,
            "model_attach_allowed": False,
            "candidate_status_after": candidate.candidate_status,
            "recommendation": {
                "status": "keep-watchlist-awaiting-real-eval",
                "reason": "metadata-only smoke eval is not model capability evidence",
                "active_teacher_promotion_allowed": False,
                "training_or_distillation_allowed": False,
            },
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }
        self._persist_smoke_eval(result)
        return result

    def smoke_eval_summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_smoke_evals(limit=limit)
        return {
            "surface_id": "model-release-bounded-smoke-eval",
            "status": "live-synthetic-evidence" if records else "awaiting-bounded-smoke-eval",
            "smoke_eval_count": len(records),
            "synthetic_passed_count": sum(
                1 for record in records if record.get("status") == "synthetic-metadata-smoke-eval-passed"
            ),
            "latest_smoke_eval": _public_smoke_eval(records[0]) if records else None,
            "real_model_benchmark_count": 0,
            "active_teacher_promotion_allowed": False,
            "raw_content_included": False,
        }

    def run_synthetic_capability_fixture(
        self,
        request: SyntheticCapabilityFixtureRequest | dict[str, Any],
    ) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, SyntheticCapabilityFixtureRequest)
            else SyntheticCapabilityFixtureRequest.model_validate(request)
        )
        candidate_id = _safe_identifier(normalized.candidate_id, prefix="model")
        smoke_eval_id = _safe_ref(normalized.smoke_eval_id)
        candidate = self._teacher_candidate(candidate_id)
        smoke_eval = next(
            (item for item in self._list_smoke_evals(limit=500) if item.get("eval_id") == smoke_eval_id),
            None,
        )
        if candidate is None:
            raise ValueError("synthetic capability fixture requires a persisted teacher candidate")
        if smoke_eval is None:
            raise ValueError("synthetic capability fixture requires a persisted bounded smoke evaluation")
        if smoke_eval.get("candidate_id") != candidate_id:
            raise ValueError("synthetic capability fixture requires smoke evidence for the requested candidate")
        if smoke_eval.get("status") != "synthetic-metadata-smoke-eval-passed":
            raise ValueError("synthetic capability fixture requires a passed metadata smoke evaluation")

        fixture = _run_isolated_synthetic_fixture(
            {
                "candidate_id": candidate_id,
                "teacher_roles": _unique_roles(list(candidate.teacher_roles)),
                "domain_scope": _unique_refs(list(candidate.domain_scope)),
            }
        )
        fixture_checks = {
            "smoke_eval_present": True,
            "smoke_eval_passed": True,
            "candidate_present": True,
            "isolated_process_completed": fixture["isolated_process"].get("status") == "completed",
            "structured_output_contract": bool(fixture["fixture_checks"].get("structured_output_contract")),
            "declared_teacher_roles_present": bool(fixture["fixture_checks"].get("declared_teacher_roles_present")),
            "declared_domain_scope_present": bool(fixture["fixture_checks"].get("declared_domain_scope_present")),
            "no_private_content": True,
        }
        passed = all(fixture_checks.values()) and fixture.get("status") == "passed"
        created_at = utcnow().isoformat()
        result = {
            "schema_version": "nexusnet-model-release-synthetic-capability-fixture-v1",
            "surface_id": "model-release-synthetic-capability-fixture",
            "fixture_id": f"model-release-synthetic-fixture::{candidate_id}::{_digest(created_at)[:16]}",
            "candidate_id": candidate_id,
            "smoke_eval_id": smoke_eval_id,
            "status": "isolated-synthetic-capability-fixture-passed" if passed else "isolated-synthetic-capability-fixture-blocked",
            "evaluation_kind": "isolated-process-synthetic-fixture",
            "fixture_checks": fixture_checks,
            "fixture_protocol": fixture.get("fixture_protocol"),
            "isolated_process": fixture["isolated_process"],
            "real_model_execution": False,
            "benchmark_execution_allowed": False,
            "model_download_allowed": False,
            "model_attach_allowed": False,
            "candidate_status_after": candidate.candidate_status,
            "recommendation": {
                "status": "keep-watchlist-awaiting-real-model-eval",
                "reason": "isolated synthetic fixture verifies only the local benchmark contract, not model capability",
                "active_teacher_promotion_allowed": False,
                "training_or_distillation_allowed": False,
            },
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }
        self._persist_synthetic_fixture_eval(result)
        return result

    def synthetic_fixture_summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_synthetic_fixture_evals(limit=limit)
        return {
            "surface_id": "model-release-synthetic-capability-fixture",
            "status": "live-isolated-synthetic-fixture-evidence" if records else "awaiting-isolated-synthetic-fixture",
            "honest_status_label": (
                "isolated-synthetic-fixtures-live-no-real-model-execution"
                if records
                else "isolated-synthetic-fixture-not-yet-observed"
            ),
            "fixture_eval_count": len(records),
            "isolated_fixture_passed_count": sum(
                1 for record in records if record.get("status") == "isolated-synthetic-capability-fixture-passed"
            ),
            "latest_fixture_eval": _public_synthetic_fixture_eval(records[0]) if records else None,
            "real_model_benchmark_count": 0,
            "active_teacher_promotion_allowed": False,
            "raw_content_included": False,
        }

    def get(self, radar_id: str) -> dict[str, Any] | None:
        for record in self._list_records(limit=500):
            if record.get("radar_id") == radar_id:
                return record
        return None

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "model_release": self.model_release_summary(),
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
                "docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md",
            ],
            "watch_items": ["TurboQuant", "LMCache", "A2A", "AG-UI", "OSWorld", "GraphRAG", "Sigstore", "WebNN"],
            "autonomy_rule": "researchers-can-discover-and-propose-but-not-promote-without-all-gates-and-operator-approval",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._memory_records = [item for item in self._memory_records if item.get("radar_id") != record.get("radar_id")]
        self._memory_records.insert(0, record)
        self._memory_records = self._memory_records[:50]
        if self.records_dir is not None:
            safe_id = record["radar_id"].replace(":", "_").replace("/", "_")
            path = self.records_dir / f"{safe_id}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_records)
        seen = {record.get("radar_id") for record in records}
        if self.records_dir is not None:
            for path in self.records_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("radar_id") not in seen:
                    records.append(payload)
        records.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return records[:limit]

    def _teacher_candidate(self, candidate_id: str) -> Any | None:
        cluster9_registry = getattr(self.teacher_candidate_registry, "cluster9_registry", None)
        if cluster9_registry is None:
            return None
        return next(
            (
                candidate
                for candidate in cluster9_registry.teacher_candidates()
                if candidate.candidate_id == candidate_id
            ),
            None,
        )

    def _persist_benchmark_packet(self, packet: dict[str, Any]) -> None:
        self._memory_benchmark_packets = [
            item for item in self._memory_benchmark_packets if item.get("packet_id") != packet.get("packet_id")
        ]
        self._memory_benchmark_packets.insert(0, dict(packet))
        self._memory_benchmark_packets = self._memory_benchmark_packets[:100]
        if self.benchmark_packets_dir is not None:
            safe_id = str(packet["packet_id"]).replace(":", "_").replace("/", "_")
            (self.benchmark_packets_dir / f"{safe_id}.json").write_text(
                json.dumps(packet, indent=2, sort_keys=True),
                encoding="utf-8",
            )

    def _list_benchmark_packets(self, *, limit: int) -> list[dict[str, Any]]:
        packets = list(self._memory_benchmark_packets)
        seen = {packet.get("packet_id") for packet in packets}
        if self.benchmark_packets_dir is not None:
            for path in self.benchmark_packets_dir.glob("*.json"):
                try:
                    packet = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if packet.get("packet_id") not in seen:
                    packets.append(packet)
        packets.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        return packets[:limit]

    def _persist_smoke_eval(self, result: dict[str, Any]) -> None:
        self._memory_smoke_evals = [
            item for item in self._memory_smoke_evals if item.get("eval_id") != result.get("eval_id")
        ]
        self._memory_smoke_evals.insert(0, dict(result))
        self._memory_smoke_evals = self._memory_smoke_evals[:100]
        if self.smoke_evals_dir is not None:
            safe_id = str(result["eval_id"]).replace(":", "_").replace("/", "_")
            (self.smoke_evals_dir / f"{safe_id}.json").write_text(
                json.dumps(result, indent=2, sort_keys=True),
                encoding="utf-8",
            )

    def _list_smoke_evals(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_smoke_evals)
        seen = {record.get("eval_id") for record in records}
        if self.smoke_evals_dir is not None:
            for path in self.smoke_evals_dir.glob("*.json"):
                try:
                    record = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if record.get("eval_id") not in seen:
                    records.append(record)
        records.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        return records[:limit]

    def _persist_synthetic_fixture_eval(self, result: dict[str, Any]) -> None:
        self._memory_synthetic_fixture_evals = [
            item for item in self._memory_synthetic_fixture_evals if item.get("fixture_id") != result.get("fixture_id")
        ]
        self._memory_synthetic_fixture_evals.insert(0, dict(result))
        self._memory_synthetic_fixture_evals = self._memory_synthetic_fixture_evals[:100]
        if self.synthetic_fixture_evals_dir is not None:
            safe_id = str(result["fixture_id"]).replace(":", "_").replace("/", "_")
            (self.synthetic_fixture_evals_dir / f"{safe_id}.json").write_text(
                json.dumps(result, indent=2, sort_keys=True),
                encoding="utf-8",
            )

    def _list_synthetic_fixture_evals(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_synthetic_fixture_evals)
        seen = {record.get("fixture_id") for record in records}
        if self.synthetic_fixture_evals_dir is not None:
            for path in self.synthetic_fixture_evals_dir.glob("*.json"):
                try:
                    record = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if record.get("fixture_id") not in seen:
                    records.append(record)
        records.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        return records[:limit]


def _review_findings(
    path_radar_id: str,
    request: ForwardRadarCandidateRequest,
    *,
    upstream_harness_ledger_gate: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    upstream_harness_ledger_gate = upstream_harness_ledger_gate or {}
    if path_radar_id != request.radar_id:
        findings.append(_finding("forward_radar_path_id_mismatch", "Path radar_id must match request radar_id."))
    if not request.source_refs or request.source_quality not in {"primary", "verified"}:
        findings.append(_finding("forward_radar_requires_primary_or_verified_source", "Forward Radar candidates require primary or verified source evidence."))
    if request.license_status != "approved":
        findings.append(_finding("forward_radar_requires_approved_license", "Forward Radar candidates require approved license posture before promotion."))
    if request.security_review != "passed":
        findings.append(_finding("forward_radar_requires_security_review", "Forward Radar candidates require a passed security review."))
    if not request.runtime_evidence_refs:
        findings.append(_finding("forward_radar_requires_runtime_evidence", "Forward Radar candidates require runtime or hardware evidence."))
    if not request.eval_refs:
        findings.append(_finding("forward_radar_requires_eval_refs", "Forward Radar candidates require eval or regression evidence."))
    if not request.observability_refs:
        findings.append(_finding("forward_radar_requires_observability_refs", "Forward Radar candidates require trace or observability evidence."))
    if not request.rollback_plan.strip():
        findings.append(_finding("forward_radar_requires_rollback_plan", "Forward Radar candidates require a rollback or demotion plan."))
    if not request.operator_approved:
        findings.append(_finding("forward_radar_requires_operator_approval", "Forward Radar candidates require operator approval before promotion."))
    if upstream_harness_ledger_gate.get("promotion_allowed") is False or upstream_harness_ledger_gate.get("status") == "blocked":
        findings.append(_finding("forward_radar_blocks_harness_ledger_gate", "Forward Radar candidates cannot become promotion-ready while upstream harness-ledger evidence is blocked.", severity="hard_fail"))
    upstream_self_review_gate = upstream_harness_ledger_gate.get("upstream_self_review_gate") or {}
    if upstream_self_review_gate.get("status") == "blocked" or upstream_self_review_gate.get("review_state") == "blocked-by-review":
        findings.append(_finding("forward_radar_blocks_upstream_self_review_gate", "Forward Radar candidates cannot become promotion-ready while upstream self-review is blocked.", severity="hard_fail"))
    upstream_eval_gate = upstream_self_review_gate.get("upstream_eval_gate") or {}
    if upstream_eval_gate.get("promotion_allowed") is False:
        findings.append(_finding("forward_radar_blocks_upstream_eval_gate", "Forward Radar candidates cannot become promotion-ready while upstream eval evidence is blocked.", severity="hard_fail"))
    upstream_lifecycle_gate = upstream_eval_gate.get("upstream_lifecycle_gate") or {}
    if upstream_lifecycle_gate.get("lifecycle_status") == "closed_loop_blocked":
        findings.append(_finding("forward_radar_blocks_upstream_lifecycle_gate", "Forward Radar candidates cannot become promotion-ready while upstream lifecycle evidence is blocked.", severity="hard_fail"))
    return findings


def _upstream_harness_ledger_gate(request: ForwardRadarCandidateRequest) -> dict[str, Any]:
    gate = request.upstream_harness_ledger_gate or {}
    self_review_gate = gate.get("upstream_self_review_gate") or {}
    eval_gate = self_review_gate.get("upstream_eval_gate") or {}
    lifecycle_gate = eval_gate.get("upstream_lifecycle_gate") or {}
    blockers = [str(item) for item in gate.get("blockers") or []]
    blockers.extend(str(item) for item in self_review_gate.get("blockers") or [])
    blockers.extend(str(item) for item in eval_gate.get("blockers") or [])
    blockers.extend(str(item) for item in lifecycle_gate.get("blockers") or [])
    return {
        "promotion_allowed": gate.get("promotion_allowed"),
        "status": gate.get("status") or "not_provided",
        "entry_id": gate.get("entry_id") or "",
        "blockers": sorted(set(blockers)),
        "upstream_self_review_gate": {
            **self_review_gate,
            "blockers": sorted(
                set(
                    [str(item) for item in self_review_gate.get("blockers") or []]
                    + [str(item) for item in eval_gate.get("blockers") or []]
                    + [str(item) for item in lifecycle_gate.get("blockers") or []]
                )
            ),
            "upstream_eval_gate": {
                **eval_gate,
                "blockers": sorted(set([str(item) for item in eval_gate.get("blockers") or []] + [str(item) for item in lifecycle_gate.get("blockers") or []])),
                "upstream_lifecycle_gate": lifecycle_gate,
            },
        },
        "source": gate.get("source") or "harness_improvement_ledger",
    }


def _gate_summary(request: ForwardRadarCandidateRequest) -> dict[str, Any]:
    gates = {
        "source": bool(request.source_refs and request.source_quality in {"primary", "verified"}),
        "license": request.license_status == "approved",
        "security": request.security_review == "passed",
        "runtime": bool(request.runtime_evidence_refs),
        "eval": bool(request.eval_refs),
        "observability": bool(request.observability_refs),
        "rollback": bool(request.rollback_plan.strip()),
        "operator": request.operator_approved,
    }
    return {
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": sum(1 for passed in gates.values() if not passed),
    }


def _policy_targets(request: ForwardRadarCandidateRequest) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"forward-radar::{request.radar_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": request.operator_approved,
                "license_state": "approved" if request.license_status == "approved" else None,
                "provenance_refs": request.source_refs,
            },
        },
        {
            "target_id": f"forward-radar-update::{request.radar_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": request.operator_approved,
                "rollback_plan": request.rollback_plan,
                "monitoring_plan": "forward-radar-shadow-review-and-eval-monitoring",
            },
        },
    ]


def _status(request: ForwardRadarCandidateRequest, *, promotion_allowed: bool, hard_blocked: bool = False) -> str:
    if hard_blocked:
        return "blocked"
    if request.license_status == "blocked" or request.security_review == "blocked":
        return "blocked"
    if promotion_allowed:
        return "promotion-ready"
    return "watchlist"


def _finding(rule_id: str, message: str, severity: str = "gate_missing") -> dict[str, str]:
    return {"rule_id": rule_id, "severity": severity, "message": message}


def _has_hard_fail(findings: list[dict[str, str]]) -> bool:
    return any(finding.get("severity") == "hard_fail" for finding in findings)


def _required_gates() -> list[str]:
    return ["source", "license", "security", "runtime", "eval", "observability", "rollback", "operator"]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/forward-radar"},
        "candidate": {"method": "GET", "endpoint": "/ops/brain/forward-radar/{radar_id}"},
        "review": {"method": "POST", "endpoint": "/ops/brain/forward-radar/{radar_id}/review"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/forward-radar"},
    }


def _model_release_candidate_status(request: ModelReleaseObservationRequest) -> str:
    if request.license_gate != "approved" or request.privacy_gate != "approved":
        return "quarantined"
    if request.security_review != "passed":
        return "quarantined"
    return "watchlist"


def _restrictive_gate(existing: str | None, observed: str) -> str:
    order = {"blocked": 3, "needs_review": 2, "approved": 1, "not_required": 1}
    if existing is None:
        return observed
    return existing if order.get(existing, 2) >= order.get(observed, 2) else observed


def _unique_roles(values: list[str]) -> list[str]:
    allowed = {"generator", "critic", "verifier", "retriever", "simulator", "judge"}
    roles = [str(value).strip().lower() for value in values if str(value).strip().lower() in allowed]
    return list(dict.fromkeys(roles)) or ["generator"]


def _unique_refs(values: list[Any]) -> list[str]:
    return list(dict.fromkeys(ref for value in values if (ref := _safe_ref(value))))


def _safe_identifier(value: Any, *, prefix: str) -> str:
    raw = str(value or "").strip()
    safe = "".join(character.lower() if character.isalnum() else "-" for character in raw)
    safe = "-".join(part for part in safe.split("-") if part)
    return safe[:120] or f"{prefix}-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _safe_ref(value: Any) -> str:
    raw = str(value or "").strip()
    lowered = raw.lower()
    if not raw:
        return ""
    if len(raw) > 240 or any(marker in lowered for marker in ("secret", "password", "token", "api-key", "apikey", ":\\")):
        return "ref-digest::" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return raw


def _public_model_release_record(record: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(record.get("metadata") or {})
    return {
        "radar_id": _safe_ref(record.get("radar_id")),
        "candidate_id": _safe_ref(metadata.get("candidate_id")),
        "status": _safe_ref(metadata.get("candidate_status")) or "watchlist",
        "forward_radar_status": _safe_ref(record.get("status")),
        "source_refs": _unique_refs(list(record.get("source_refs") or [])),
        "release_date": _safe_ref(metadata.get("release_date")),
        "raw_content_included": False,
    }


def _public_benchmark_packet(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "packet_id": _safe_ref(packet.get("packet_id")),
        "candidate_id": _safe_ref(packet.get("candidate_id")),
        "status": _safe_ref(packet.get("status")),
        "blockers": _unique_refs(list(packet.get("blockers") or [])),
        "planned_stages": _unique_refs(list(packet.get("planned_stages") or [])),
        "benchmark_execution_allowed": False,
        "raw_content_included": False,
    }


def _public_smoke_eval(record: dict[str, Any]) -> dict[str, Any]:
    recommendation = dict(record.get("recommendation") or {})
    return {
        "eval_id": _safe_ref(record.get("eval_id")),
        "candidate_id": _safe_ref(record.get("candidate_id")),
        "packet_id": _safe_ref(record.get("packet_id")),
        "status": _safe_ref(record.get("status")),
        "evaluation_kind": _safe_ref(record.get("evaluation_kind")),
        "recommendation_status": _safe_ref(recommendation.get("status")),
        "active_teacher_promotion_allowed": False,
        "raw_content_included": False,
    }


def _public_synthetic_fixture_eval(record: dict[str, Any]) -> dict[str, Any]:
    recommendation = dict(record.get("recommendation") or {})
    isolated_process = dict(record.get("isolated_process") or {})
    return {
        "fixture_id": _safe_ref(record.get("fixture_id")),
        "candidate_id": _safe_ref(record.get("candidate_id")),
        "smoke_eval_id": _safe_ref(record.get("smoke_eval_id")),
        "status": _safe_ref(record.get("status")),
        "evaluation_kind": _safe_ref(record.get("evaluation_kind")),
        "isolated_process_status": _safe_ref(isolated_process.get("status")),
        "recommendation_status": _safe_ref(recommendation.get("status")),
        "real_model_execution": False,
        "active_teacher_promotion_allowed": False,
        "raw_content_included": False,
    }


def _run_isolated_synthetic_fixture(payload: dict[str, Any]) -> dict[str, Any]:
    """Execute a fixed, no-network fixture in a temporary child process.

    The child receives only sanitized candidate metadata. It is execution evidence for
    the benchmark protocol, not a claim that a candidate model has run or is sandboxed.
    """

    with tempfile.TemporaryDirectory(prefix="nexusnet-model-release-fixture-") as temporary_dir:
        workdir = Path(temporary_dir)
        input_path = workdir / "fixture-input.json"
        output_path = workdir / "fixture-output.json"
        input_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-c", _ISOLATED_SYNTHETIC_FIXTURE_SCRIPT, str(input_path), str(output_path)],
                cwd=workdir,
                env=_isolated_fixture_environment(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=5,
            )
            output = json.loads(output_path.read_text(encoding="utf-8")) if output_path.exists() else {}
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
            return {
                "status": "blocked",
                "fixture_checks": {},
                "fixture_protocol": "nexusnet-synthetic-capability-fixture-v1",
                "isolated_process": {
                    "status": "blocked",
                    "execution_boundary": "isolated-python-process-temporary-workdir",
                    "timeout_seconds": 5,
                    "ambient_credentials_forwarded": False,
                    "os_capability_sandbox_proven": False,
                },
            }

    fixture_checks = output.get("fixture_checks") if isinstance(output, dict) else {}
    valid_output = (
        isinstance(fixture_checks, dict)
        and output.get("schema_version") == "nexusnet-synthetic-capability-fixture-v1"
        and output.get("status") == "passed"
        and all(
            fixture_checks.get(name) is True
            for name in (
                "structured_output_contract",
                "declared_teacher_roles_present",
                "declared_domain_scope_present",
                "sanitized_input_only",
            )
        )
    )
    return {
        "status": "passed" if completed.returncode == 0 and valid_output else "blocked",
        "fixture_checks": fixture_checks if valid_output else {},
        "fixture_protocol": _safe_ref(output.get("fixture_protocol")) if isinstance(output, dict) else "",
        "isolated_process": {
            "status": "completed" if completed.returncode == 0 and valid_output else "blocked",
            "execution_boundary": "isolated-python-process-temporary-workdir",
            "timeout_seconds": 5,
            "ambient_credentials_forwarded": False,
            "os_capability_sandbox_proven": False,
        },
    }


def _isolated_fixture_environment() -> dict[str, str]:
    return {
        key: value
        for key in ("SYSTEMROOT", "WINDIR", "COMSPEC")
        if (value := os.environ.get(key))
    }


_ISOLATED_SYNTHETIC_FIXTURE_SCRIPT = """
import json
import re
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
candidate_id = payload.get("candidate_id")
teacher_roles = payload.get("teacher_roles")
domain_scope = payload.get("domain_scope")
checks = {
    "structured_output_contract": True,
    "declared_teacher_roles_present": isinstance(teacher_roles, list) and bool(teacher_roles),
    "declared_domain_scope_present": isinstance(domain_scope, list) and bool(domain_scope),
    "sanitized_input_only": isinstance(candidate_id, str) and bool(re.fullmatch(r"[a-z0-9-]{1,120}", candidate_id)),
}
result = {
    "schema_version": "nexusnet-synthetic-capability-fixture-v1",
    "fixture_protocol": "structured-output-contract-v1",
    "status": "passed" if all(checks.values()) else "blocked",
    "fixture_checks": checks,
}
Path(sys.argv[2]).write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
"""
