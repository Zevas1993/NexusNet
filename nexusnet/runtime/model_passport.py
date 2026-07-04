from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


LicenseStatus = Literal["approved", "needs_review", "blocked"]


class ModelPassportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str
    parameter_count: int
    active_parameter_count: int | None = None
    context_tokens: int
    runtime_formats: list[str] = Field(default_factory=list)
    memory_budget_mb: int
    latency_envelope_ms: dict[str, float] = Field(default_factory=dict)
    task_strengths: list[str] = Field(default_factory=list)
    task_refusals: list[str] = Field(default_factory=list)
    license_status: LicenseStatus = "needs_review"
    provenance_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CertificationRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    model_id: str
    scenarios: list[str] = Field(default_factory=list)
    device_matrix: dict[str, Any] = Field(default_factory=dict)
    benchmark_refs: list[str] = Field(default_factory=list)
    retrieval_support_enabled: bool = False
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EdgeModelCertificationRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "runtime" / "model-passports" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._passports: dict[str, dict[str, Any]] = {}
        self._runs: list[dict[str, Any]] = []

    def register_passport(self, request: ModelPassportRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, ModelPassportRequest) else ModelPassportRequest.model_validate(request)
        passport = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "edge-model-certification",
            "model_id": normalized.model_id,
            "status": "registered" if normalized.license_status != "blocked" else "blocked",
            "created_at": utcnow().isoformat(),
            "parameter_count": normalized.parameter_count,
            "active_parameter_count": normalized.active_parameter_count,
            "context_tokens": normalized.context_tokens,
            "runtime_formats": normalized.runtime_formats,
            "memory_budget_mb": normalized.memory_budget_mb,
            "latency_envelope_ms": normalized.latency_envelope_ms,
            "task_strengths": normalized.task_strengths,
            "task_refusals": normalized.task_refusals,
            "license_status": normalized.license_status,
            "provenance_refs": normalized.provenance_refs,
            "deployment_boundary": "task-certified-edge-model-not-default-brain",
            "metadata": normalized.metadata,
        }
        self._passports[passport["model_id"]] = passport
        self._persist("passport", passport["model_id"], passport)
        return passport

    def certify(self, request: CertificationRunRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, CertificationRunRequest) else CertificationRunRequest.model_validate(request)
        passport = self._passports.get(normalized.model_id)
        findings = _certification_findings(normalized, passport)
        run = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "edge-model-certification",
            "run_id": normalized.run_id,
            "model_id": normalized.model_id,
            "status": "blocked" if findings else "certified-shadow",
            "runtime_state": "degraded" if findings else "live-bound",
            "created_at": utcnow().isoformat(),
            "scenarios": normalized.scenarios,
            "device_matrix": normalized.device_matrix,
            "benchmark_refs": normalized.benchmark_refs,
            "retrieval_support_enabled": normalized.retrieval_support_enabled,
            "evidence_refs": normalized.evidence_refs,
            "passport_snapshot": passport,
            "findings": findings,
            "certification_boundary": "certified-by-task-and-device-not-global-model-reputation",
            "metadata": normalized.metadata,
        }
        self._runs.insert(0, run)
        self._runs = self._runs[:50]
        self._persist("certification", run["run_id"], run)
        return run

    def summary(self) -> dict[str, Any]:
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "edge-model-certification",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(run.get("status") == "blocked" for run in self._runs)
            else ("live-bound" if self._passports or self._runs else "static-canon"),
            "passport_count": len(self._passports),
            "certification_count": len(self._runs),
            "passports": list(self._passports.values()),
            "latest_certification": self._runs[0] if self._runs else None,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, prefix: str, record_id: str, payload: dict[str, Any]) -> None:
        if self.records_dir is None:
            return
        path = self.records_dir / f"{prefix}_{record_id.replace(':', '_').replace('/', '_')}.json"
        payload["artifact_path"] = str(path)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _certification_findings(request: CertificationRunRequest, passport: dict[str, Any] | None) -> list[dict[str, str]]:
    findings = []
    if passport is None:
        findings.append(
            {
                "rule_id": "certification_requires_model_passport",
                "severity": "hard_fail",
                "message": "Certification requires a registered model passport.",
            }
        )
        return findings
    refused = set(passport.get("task_refusals") or [])
    requested_refused = refused & set(request.scenarios)
    if requested_refused and not request.retrieval_support_enabled:
        findings.append(
            {
                "rule_id": "certification_blocks_refused_task_without_support",
                "severity": "hard_fail",
                "message": "Refused task scenarios require retrieval or teacher support.",
            }
        )
    if not request.benchmark_refs:
        findings.append(
            {
                "rule_id": "certification_requires_benchmark_refs",
                "severity": "hard_fail",
                "message": "Certification requires benchmark references.",
            }
        )
    if not request.device_matrix:
        findings.append(
            {
                "rule_id": "certification_requires_device_matrix",
                "severity": "hard_fail",
                "message": "Certification requires device matrix evidence.",
            }
        )
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/model-passports"},
        "register_passport": {"method": "POST", "endpoint": "/ops/brain/model-passports"},
        "certify": {"method": "POST", "endpoint": "/ops/brain/model-certifications"},
    }
