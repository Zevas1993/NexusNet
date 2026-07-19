from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


AnswerabilityStatus = Literal["source_backed", "explicit_unknown", "unsupported", "conflicting"]
SourceStatus = Literal[
    "primary_verified",
    "secondary_verified",
    "transcript_only",
    "operator_supplied",
    "inferred",
    "unverified",
    "contradicted",
    "rejected",
]
PromotionState = Literal["none", "refs_only", "review_required", "canon_candidate", "promoted", "blocked"]


class SourceClaimRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str
    answer_id: str
    claim_text: str
    answerability_status: AnswerabilityStatus
    source_status: SourceStatus = "unverified"
    evidence_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    uncertainty_label: str = ""
    reviewer: str = ""
    promotion_state: PromotionState = "none"
    source_refs: list[str] = Field(default_factory=list)
    memory_refs: list[str] = Field(default_factory=list)
    retrieval_refs: list[str] = Field(default_factory=list)
    graph_refs: list[str] = Field(default_factory=list)
    contains_private_data: bool = False
    consent_ref: str = ""
    contradiction_refs: list[str] = Field(default_factory=list)
    evaluator_refs: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryQualityLedger:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.claims_dir = self.artifacts_dir / "memory" / "quality-ledger" if self.artifacts_dir else None
        if self.claims_dir is not None:
            self.claims_dir.mkdir(parents=True, exist_ok=True)
        self._memory_claims: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def record_claim(self, request: SourceClaimRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, SourceClaimRequest) else SourceClaimRequest.model_validate(request)
        quality_findings = _quality_findings(normalized)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = bool(quality_findings) or policy_scan.summary.active_hard_fail_count > 0
        genesis_admission = _record_genesis_source_claim_admission(self, normalized)
        admission_allows_memory = (
            genesis_admission.get("memory_write_allowed") is True if genesis_admission else not blocked
        )
        admission_allows_retrieval = (
            genesis_admission.get("retrieval_truth_allowed") is True if genesis_admission else not blocked
        )
        admission_allows_training = (
            genesis_admission.get("training_allowed") is True if genesis_admission else False
        )
        memory_write_allowed = admission_allows_memory and not blocked
        retrieval_truth_allowed = admission_allows_retrieval and not blocked
        training_allowed = admission_allows_training and not blocked
        graph_truth_allowed = (
            memory_write_allowed
            and retrieval_truth_allowed
            and normalized.source_status in {"primary_verified", "secondary_verified"}
        )
        knowledge_artifact_allowed = graph_truth_allowed and bool(_provenance_refs(normalized))
        genesis_denied_raw_claim = bool(genesis_admission) and genesis_admission.get("memory_write_allowed") is not True
        raw_claim_allowed = not genesis_denied_raw_claim and (memory_write_allowed or not normalized.contains_private_data)
        claim_text = normalized.claim_text if raw_claim_allowed else _redacted_claim_ref(normalized.claim_text)
        claim = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "memory-quality",
            "claim_id": normalized.claim_id,
            "answer_id": normalized.answer_id,
            "claim_text": claim_text,
            "answerability_status": normalized.answerability_status,
            "answerability_gate": _answerability_gate(normalized),
            "source_status": normalized.source_status,
            "evidence_strength": normalized.evidence_strength,
            "uncertainty_label": normalized.uncertainty_label,
            "reviewer": normalized.reviewer,
            "promotion_state": normalized.promotion_state,
            "abstention_reward": _abstention_reward(normalized),
            "status": "blocked" if blocked else "verified",
            "quality_state": "blocked-by-memory-quality" if blocked else "claim-grounded",
            "created_at": utcnow().isoformat(),
            "source_refs": normalized.source_refs,
            "memory_refs": normalized.memory_refs,
            "retrieval_refs": normalized.retrieval_refs,
            "graph_refs": normalized.graph_refs,
            "contains_private_data": normalized.contains_private_data,
            "consent_ref": normalized.consent_ref,
            "contradiction_refs": normalized.contradiction_refs,
            "evaluator_refs": normalized.evaluator_refs,
            "confidence": normalized.confidence,
            "required_controls": _required_controls(),
            "quality_findings": quality_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "genesis_memory_admission": genesis_admission,
            "raw_content_included": raw_claim_allowed,
            "memory_write_allowed": memory_write_allowed,
            "retrieval_truth_allowed": retrieval_truth_allowed,
            "training_allowed": training_allowed,
            "graph_truth_allowed": graph_truth_allowed,
            "knowledge_artifact_allowed": knowledge_artifact_allowed,
            "metadata": _sanitized_claim_metadata(normalized, genesis_admission),
        }
        self._persist(claim)
        return claim

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        claims = self._list_claims(limit=limit)
        latest = claims[0] if claims else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if latest.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "memory-quality",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "claim_count": len(claims),
            "verified_count": sum(1 for claim in claims if claim.get("status") == "verified"),
            "blocked_count": sum(1 for claim in claims if claim.get("status") == "blocked"),
            "explicit_unknown_count": sum(1 for claim in claims if claim.get("answerability_status") == "explicit_unknown"),
            "latest_claim": latest,
            "claims": claims,
            "required_controls": _required_controls(),
            "research_lanes": _research_lanes(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
                "docs/SELF_IMPROVEMENT_LAYER.md",
            ],
            "quality_boundary": "every-promoted-answer-claim-is-source-backed-or-explicitly-unknown",
            "consolidation_boundary": "stale-conflicting-private-memory-enters-review-before-reuse",
        }

    def _persist(self, claim: dict[str, Any]) -> None:
        self._memory_claims.insert(0, claim)
        self._memory_claims = self._memory_claims[:50]
        if self.claims_dir is not None:
            safe_id = claim["claim_id"].replace(":", "_").replace("/", "_")
            path = self.claims_dir / f"{safe_id}.json"
            claim["artifact_path"] = str(path)
            path.write_text(json.dumps(claim, indent=2), encoding="utf-8")

    def _list_claims(self, *, limit: int) -> list[dict[str, Any]]:
        claims = list(self._memory_claims)
        seen = {claim.get("claim_id") for claim in claims}
        if self.claims_dir is not None:
            for path in self.claims_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("claim_id") not in seen:
                    claims.append(payload)
        claims.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return claims[:limit]


def _quality_findings(request: SourceClaimRequest) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    source_to_claim_refs = _provenance_refs(request)
    claim_grounding_refs = [*request.source_refs, *request.retrieval_refs, *request.graph_refs]
    if request.answerability_status == "source_backed" and not source_to_claim_refs:
        findings.append(
            {
                "rule_id": "memory_claim_requires_source_to_claim_refs",
                "severity": "hard_fail",
                "message": "Source-backed claims require source, memory, retrieval, or graph references.",
            }
        )
    if request.answerability_status in {"unsupported", "conflicting"} and not claim_grounding_refs:
        findings.append(
            {
                "rule_id": "memory_claim_requires_source_to_claim_refs",
                "severity": "hard_fail",
                "message": "Source-backed claims require source, memory, retrieval, or graph references.",
            }
        )
    if request.answerability_status == "unsupported":
        findings.append(
            {
                "rule_id": "memory_claim_unsupported_answerability",
                "severity": "hard_fail",
                "message": "Unsupported claims must be revised or marked explicitly unknown before promotion.",
            }
        )
    if request.answerability_status == "conflicting" or request.contradiction_refs:
        findings.append(
            {
                "rule_id": "memory_claim_conflict_requires_resolution",
                "severity": "hard_fail",
                "message": "Conflicting memory evidence requires resolution before reuse.",
            }
        )
    promotion_requested = request.promotion_state in {"canon_candidate", "promoted"}
    unverified_source_statuses = {
        "transcript_only",
        "operator_supplied",
        "inferred",
        "unverified",
        "contradicted",
        "rejected",
    }
    if promotion_requested and request.source_status in unverified_source_statuses:
        findings.append(
            {
                "rule_id": "claim_source_status_blocks_promotion",
                "severity": "hard_fail",
                "message": "Claims need primary or secondary verification before canon promotion.",
            }
        )
    if request.source_status == "contradicted" and not request.contradiction_refs:
        findings.append(
            {
                "rule_id": "contradicted_claim_requires_contradiction_refs",
                "severity": "hard_fail",
                "message": "Contradicted claims must preserve contradiction references.",
            }
        )
    if request.contains_private_data and not request.consent_ref.strip():
        findings.append(
            {
                "rule_id": "memory_claim_private_data_requires_consent",
                "severity": "hard_fail",
                "message": "Private memory claims require consent or redaction proof.",
            }
        )
    if request.answerability_status != "explicit_unknown" and request.confidence < 0.65:
        findings.append(
            {
                "rule_id": "memory_claim_low_confidence",
                "severity": "warning",
                "message": "Low-confidence claims require more evidence or explicit uncertainty.",
            }
        )
    return findings


def _policy_targets(request: SourceClaimRequest) -> list[dict[str, Any]]:
    provenance_refs = _provenance_refs(request) if request.answerability_status == "source_backed" else []
    if request.answerability_status == "explicit_unknown":
        provenance_refs = provenance_refs or [f"explicit-unknown::{request.claim_id}"]
    return [
        {
            "target_id": f"memory-claim::{request.claim_id}",
            "target_type": "memory_update",
            "metadata": {
                "provenance_refs": provenance_refs,
                "retention_policy": request.metadata.get("retention_policy", "project"),
                "requires_review": bool(request.contains_private_data or request.contradiction_refs),
            },
        },
        {
            "target_id": f"claim::{request.claim_id}",
            "target_type": "claim",
            "metadata": {
                "promotion_requested": request.promotion_state in {"canon_candidate", "promoted"},
                "source_status": request.source_status,
                "source_refs": request.source_refs,
            },
        },
    ]


def _record_genesis_source_claim_admission(
    ledger: MemoryQualityLedger,
    request: SourceClaimRequest,
) -> dict[str, Any]:
    admission = getattr(ledger, "genesis_memory_admission", None)
    record_manual_ingress = getattr(admission, "record_manual_ingress", None)
    if not callable(record_manual_ingress):
        return {}
    return record_manual_ingress(
        session_id=_source_claim_session_id(request),
        ingress_route="source-claim-record",
        content=request.claim_text,
        metadata=_source_claim_ingress_metadata(request),
    )


def _source_claim_session_id(request: SourceClaimRequest) -> str | None:
    session_id = request.metadata.get("session_id") or request.metadata.get("session_ref")
    return str(session_id) if session_id else None


def _source_claim_ingress_metadata(request: SourceClaimRequest) -> dict[str, Any]:
    metadata = dict(request.metadata)
    return {
        "source_kind": metadata.get("source_kind") or "source-claim-record",
        "privacy_class": metadata.get("privacy_class")
        or ("operator-private" if request.contains_private_data else "unspecified"),
        "consent_status": metadata.get("consent_status") or ("memory-approved" if request.consent_ref else "not-declared"),
        "rights_license_status": metadata.get("rights_license_status")
        or metadata.get("license_status")
        or "not-declared",
        "claim_status": request.answerability_status,
        "source_status": request.source_status,
        "promotion_state": request.promotion_state,
    }


def _redacted_claim_ref(value: str) -> str:
    return f"redacted::sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _sanitized_claim_metadata(
    request: SourceClaimRequest,
    genesis_admission: dict[str, Any],
) -> dict[str, Any]:
    safe_keys = {
        "source_kind",
        "privacy_class",
        "consent_status",
        "rights_license_status",
        "license_status",
        "retention_policy",
    }
    metadata = {
        key: value
        for key, value in request.metadata.items()
        if key in safe_keys and _is_safe_metadata_value(value)
    }
    session_ref_digest = genesis_admission.get("session_ref_digest") if genesis_admission else None
    if session_ref_digest:
        metadata["session_ref_digest"] = session_ref_digest
    decision_id = genesis_admission.get("decision_id") if genesis_admission else None
    if decision_id:
        metadata["genesis_memory_admission_decision_id"] = decision_id
    return metadata


def _is_safe_metadata_value(value: Any) -> bool:
    if isinstance(value, (str, int, float, bool)) or value is None:
        text = str(value).lower()
        return not any(marker in text for marker in ("secret", "token", "password", "api-key", "apikey", ":\\"))
    return False


def _provenance_refs(request: SourceClaimRequest) -> list[str]:
    return [*request.source_refs, *request.memory_refs, *request.retrieval_refs, *request.graph_refs]


def _answerability_gate(request: SourceClaimRequest) -> str:
    return request.answerability_status.replace("_", "-")


def _abstention_reward(request: SourceClaimRequest) -> float:
    if request.answerability_status == "explicit_unknown" and request.source_status in {"unverified", "rejected", "contradicted"}:
        return 1.0
    if request.uncertainty_label and request.promotion_state in {"none", "refs_only", "blocked"}:
        return 0.5
    return 0.0


def _required_controls() -> list[str]:
    return [
        "source_to_claim_maps",
        "retrieval_quality",
        "answerability_gate",
        "staleness_check",
        "privacy_consent",
        "contradiction_check",
        "ragchecker_metrics",
    ]


def _research_lanes() -> list[dict[str, str]]:
    return [
        {"lane_id": "GraphRAG", "label": "Graph-grounded retrieval and relationship traversal.", "state": "mapped"},
        {"lane_id": "LightRAG", "label": "Low-overhead graph/RAG indexing for local contexts.", "state": "research-candidate"},
        {"lane_id": "HippoRAG", "label": "Long-memory retrieval and consolidation watch lane.", "state": "research-candidate"},
        {"lane_id": "RAGChecker", "label": "Answerability, grounding, and retrieval-quality evaluation.", "state": "mapped"},
        {"lane_id": "source-to-claim", "label": "Claim-level source map for promoted answers.", "state": "live-bound"},
        {"lane_id": "memory-consolidation", "label": "Stale, duplicate, private, and conflicting memory review.", "state": "mapped"},
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/memory-quality"},
        "record_claim": {"method": "POST", "endpoint": "/ops/brain/memory-quality/claims"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/memory-quality"},
    }
