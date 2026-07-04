from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


ConceptKind = Literal["behavioral_proxy", "activation_feature"]


class ConceptTelemetryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    concept_id: str
    trace_refs: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    concept_kind: ConceptKind = "behavioral_proxy"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    safety_flags: list[str] = Field(default_factory=list)
    contains_private_data: bool = False
    sae_experiment_ref: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class SAEExperimentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    model_id: str
    layer: str
    token_count: int
    activation_capture_method: str
    sae_config: dict[str, Any] = Field(default_factory=dict)
    reconstruction_metrics: dict[str, float] = Field(default_factory=dict)
    feature_examples: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConceptTelemetryRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "telemetry" / "concept-plane" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._concepts: list[dict[str, Any]] = []
        self._experiments: list[dict[str, Any]] = []

    def record_concept(self, request: ConceptTelemetryRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, ConceptTelemetryRequest) else ConceptTelemetryRequest.model_validate(request)
        findings = _concept_findings(normalized)
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "concept-telemetry",
            "concept_id": normalized.concept_id,
            "status": "blocked" if findings else "recorded",
            "runtime_state": "degraded" if findings else "live-bound",
            "created_at": utcnow().isoformat(),
            "trace_refs": normalized.trace_refs,
            "labels": normalized.labels,
            "concept_kind": normalized.concept_kind,
            "confidence": normalized.confidence,
            "safety_flags": normalized.safety_flags,
            "contains_private_data": normalized.contains_private_data,
            "sae_experiment_ref": normalized.sae_experiment_ref,
            "activation_claim_allowed": normalized.concept_kind == "activation_feature" and not findings,
            "manifold_caution_label": "behavioral_proxy_not_internal_activation"
            if normalized.concept_kind == "behavioral_proxy"
            else "activation_experiment_required",
            "findings": findings,
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._concepts.insert(0, record)
        self._concepts = self._concepts[:50]
        self._persist("concept", record["concept_id"], record)
        return record

    def record_sae_experiment(self, request: SAEExperimentRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, SAEExperimentRequest) else SAEExperimentRequest.model_validate(request)
        experiment = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "concept-telemetry",
            "experiment_id": normalized.experiment_id,
            "status": "research-only",
            "runtime_state": "live-bound",
            "created_at": utcnow().isoformat(),
            "model_id": normalized.model_id,
            "layer": normalized.layer,
            "token_count": normalized.token_count,
            "activation_capture_method": normalized.activation_capture_method,
            "sae_config": normalized.sae_config,
            "reconstruction_metrics": normalized.reconstruction_metrics,
            "feature_examples": normalized.feature_examples,
            "evidence_refs": normalized.evidence_refs,
            "closed_model_boundary": "no-closed-model-internals-from-output-only-traces",
            "promotion_allowed": False,
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._experiments.insert(0, experiment)
        self._experiments = self._experiments[:50]
        self._persist("sae", experiment["experiment_id"], experiment)
        return experiment

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        concepts = self._concepts[:limit]
        experiments = self._experiments[:limit]
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "concept-telemetry",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(concept.get("status") == "blocked" for concept in concepts)
            else ("live-bound" if concepts or experiments else "static-canon"),
            "concept_count": len(concepts),
            "sae_experiment_count": len(experiments),
            "latest_concept": concepts[0] if concepts else None,
            "concepts": concepts,
            "sae_experiments": experiments,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, prefix: str, record_id: str, payload: dict[str, Any]) -> None:
        if self.records_dir is None:
            return
        path = self.records_dir / f"{prefix}_{record_id.replace(':', '_').replace('/', '_')}.json"
        payload["artifact_path"] = str(path)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _concept_findings(request: ConceptTelemetryRequest) -> list[dict[str, str]]:
    findings = []
    if request.concept_kind == "activation_feature" and not request.sae_experiment_ref:
        findings.append(
            {
                "rule_id": "activation_features_require_sae_experiment",
                "severity": "hard_fail",
                "message": "Activation-feature claims require an SAE experiment reference.",
            }
        )
    if request.contains_private_data:
        findings.append(
            {
                "rule_id": "concept_telemetry_blocks_private_content_capture",
                "severity": "hard_fail",
                "message": "Concept telemetry stores labels and trace refs only, not private content.",
            }
        )
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/concept-telemetry"},
        "record_concept": {"method": "POST", "endpoint": "/ops/brain/concept-telemetry/concepts"},
        "record_sae_experiment": {"method": "POST", "endpoint": "/ops/brain/concept-telemetry/sae-experiments"},
    }
