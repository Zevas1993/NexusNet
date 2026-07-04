from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel
from nexusnet.security.artifact_signing import file_sha256, verify_signed_artifact_record


ArtifactType = Literal["model", "adapter", "dataset", "tool", "plugin", "runtime", "document"]
ArtifactFormat = Literal["safetensors", "gguf", "onnx", "mlx", "mnn", "executorch", "pickle", "bin", "zip", "unknown"]
LicenseStatus = Literal["approved", "needs_review", "blocked"]


class ArtifactScanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    artifact_type: ArtifactType
    uri: str
    format: ArtifactFormat = "unknown"
    license_status: LicenseStatus = "needs_review"
    provenance_refs: list[str] = Field(default_factory=list)
    checksum: str = ""
    signature_ref: str = ""
    contains_pickle: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactTrustRegistry:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.scans_dir = self.artifacts_dir / "security" / "artifact-trust" if self.artifacts_dir else None
        if self.scans_dir is not None:
            self.scans_dir.mkdir(parents=True, exist_ok=True)
        self._memory_scans: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def scan(self, request: ArtifactScanRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, ArtifactScanRequest) else ArtifactScanRequest.model_validate(request)
        return self._scan(normalized, persist=True)

    def _scan(self, normalized: ArtifactScanRequest, *, persist: bool) -> dict[str, Any]:
        trust_findings = _trust_findings(normalized)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = bool(trust_findings) or policy_scan.summary.active_hard_fail_count > 0
        status = "quarantined" if blocked else "trusted"
        scan = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "artifact-trust-registry",
            "artifact_id": normalized.artifact_id,
            "artifact_type": normalized.artifact_type,
            "uri": normalized.uri,
            "format": normalized.format,
            "status": status,
            "trust_decision": "blocked-pending-review" if blocked else "allow-shadow-or-active-use",
            "created_at": utcnow().isoformat(),
            "license_status": normalized.license_status,
            "provenance_refs": normalized.provenance_refs,
            "checksum": normalized.checksum,
            "signature_ref": normalized.signature_ref,
            "contains_pickle": normalized.contains_pickle,
            "reason_codes": _reason_codes(normalized, blocked=blocked),
            "trust_findings": trust_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "metadata": normalized.metadata,
            "persisted": persist,
        }
        if persist:
            self._persist(scan)
        return scan

    def scan_knowledge_artifact(self, artifact: dict[str, Any]) -> dict[str, Any]:
        return self._scan(_knowledge_artifact_scan_request(artifact), persist=True)

    def preview_knowledge_artifact(self, artifact: dict[str, Any]) -> dict[str, Any]:
        return self._scan(_knowledge_artifact_scan_request(artifact), persist=False)

    def scan_deep_replay_bundle(self, replay: dict[str, Any]) -> dict[str, Any]:
        artifact_index_path = Path((replay.get("artifacts") or {}).get("artifact_index_path", ""))
        replay_id = str(replay.get("replay_id") or "replay")
        bundle_path = str((replay.get("artifacts") or {}).get("deep_replay_bundle_path") or "")
        scans = []
        records = []
        if artifact_index_path.is_file():
            for line in artifact_index_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                record = json.loads(line)
                records.append(record)
                signature_state = record.get("signature_state")
                signature_ref = ""
                signature_verified: bool | None = None
                if signature_state == "signed_ed25519":
                    signature_ref = f"ed25519:{record.get('public_key', '')}:{record.get('signature', '')[:16]}"
                    # Cryptographically verify the ed25519 signature rather than trusting the claim.
                    signature_verified = verify_signed_artifact_record(record)
                checksum_verified = _record_checksum_verified(record)
                artifact_type = "adapter" if record.get("artifact_type") == "sandbox_adapter_bundle" else "document"
                source = "sandbox_adapter_artifact_bundle" if artifact_type == "adapter" else "deep_replay_bundle"
                scans.append(
                    self.scan(
                        {
                            "artifact_id": f"deep-replay::{replay_id}::{record.get('relative_path') or record.get('artifact_path')}",
                            "artifact_type": artifact_type,
                            "uri": str(record.get("artifact_path") or ""),
                            "format": _format_from_uri(str(record.get("artifact_path") or "")),
                            "license_status": record.get("license_status") or "approved",
                            "provenance_refs": [bundle_path] if bundle_path else [],
                            "checksum": str(record.get("hash") or ""),
                            "signature_ref": signature_ref,
                            "contains_pickle": False,
                            "metadata": {
                                "source": source,
                                "replay_id": replay_id,
                                "relative_path": record.get("relative_path"),
                                "signature_state": signature_state,
                                "signature_algorithm": record.get("signature_algorithm"),
                                "signature_verified": signature_verified,
                                "checksum_verified": checksum_verified,
                                "deep_replay_source": "deep_replay_bundle",
                            },
                        }
                    )
                )
        lifecycle_promotion = _deep_replay_lifecycle_promotion(records)
        trusted_count = sum(1 for scan in scans if scan.get("status") == "trusted")
        quarantined_count = sum(1 for scan in scans if scan.get("status") == "quarantined")
        adapter_artifact_scan = next(
            (scan for scan in scans if (scan.get("metadata") or {}).get("source") == "sandbox_adapter_artifact_bundle"),
            None,
        )
        return {
            "source": "deep_replay_bundle",
            "replay_id": replay_id,
            "scan_count": len(scans),
            "trusted_count": trusted_count,
            "quarantined_count": quarantined_count,
            "adapter_artifact_scan": adapter_artifact_scan,
            "adapter_artifact_trust_status": adapter_artifact_scan.get("status") if adapter_artifact_scan else "not_recorded",
            "signature_summary": replay.get("signature_summary") or {},
            "promotion_allowed": quarantined_count == 0 and not lifecycle_promotion["promotion_blockers"],
            "promotion_blockers": lifecycle_promotion["promotion_blockers"],
            "blocked_lifecycle_count": lifecycle_promotion["blocked_lifecycle_count"],
            "scans": scans,
        }

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        scans = self._list_scans(limit=limit)
        quarantined_count = sum(1 for scan in scans if scan.get("status") == "quarantined")
        latest_scan = scans[0] if scans else None
        runtime_state = "static-canon"
        if scans:
            runtime_state = "degraded" if quarantined_count or latest_scan.get("status") == "quarantined" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "artifact-trust-registry",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "scan_count": len(scans),
            "trusted_count": sum(1 for scan in scans if scan.get("status") == "trusted"),
            "quarantined_count": quarantined_count,
            "latest_scan": latest_scan,
            "scans": scans,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
                "docs/NEXUSNET_RESEARCH_CANDIDATE_DOSSIER_2026-04-28.md",
            ],
            "supply_chain_boundary": "artifact-use-requires-provenance-license-checksum-and-unsafe-format-scan",
            "watch_items": ["Sigstore", "ML-BOM", "AI-BOM", "safetensors", "pickle scanning", "model signing"],
        }

    def _persist(self, scan: dict[str, Any]) -> None:
        self._memory_scans.insert(0, scan)
        self._memory_scans = self._memory_scans[:50]
        if self.scans_dir is not None:
            path = self.scans_dir / _artifact_scan_filename(str(scan["artifact_id"]))
            scan["artifact_path"] = str(path)
            path.write_text(json.dumps(scan, indent=2), encoding="utf-8")

    def _list_scans(self, *, limit: int) -> list[dict[str, Any]]:
        scans = list(self._memory_scans)
        seen = {scan.get("artifact_id") for scan in scans}
        if self.scans_dir is not None:
            for path in self.scans_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("artifact_id") not in seen:
                    scans.append(payload)
        scans.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return scans[:limit]


def _artifact_scan_filename(artifact_id: str, *, max_filename_length: int = 120) -> str:
    safe_id = artifact_id.replace(":", "_").replace("/", "_").replace("\\", "_")
    digest = hashlib.sha256(artifact_id.encode("utf-8")).hexdigest()[:16]
    suffix = f"__{digest}.json"
    budget = max(1, max_filename_length - len(suffix))
    if len(safe_id) > budget:
        safe_id = safe_id[:budget].rstrip("._-") or "artifact"
    return f"{safe_id}{suffix}"


def _knowledge_artifact_scan_request(artifact: dict[str, Any]) -> ArtifactScanRequest:
        source_digests = artifact.get("source_digests") or []
        source_ref_security_gate = artifact.get("source_ref_security_gate") or {}
        blocked_source_refs = artifact.get("blocked_source_refs") or source_ref_security_gate.get("blocked_source_refs") or []
        artifact_hash = str(artifact.get("artifact_hash") or "")
        signature_ref = f"kac:compiled-artifact:{artifact_hash.removeprefix('sha256:')[:16]}" if artifact_hash else ""
        return ArtifactScanRequest(
            artifact_id=str(artifact.get("artifact_id") or "kac://unknown"),
            artifact_type="document",
            uri=str(artifact.get("artifact_id") or ""),
            format="unknown",
            license_status="approved",
            provenance_refs=[str(digest.get("source_ref")) for digest in source_digests if digest.get("source_ref")],
            checksum=artifact_hash,
            signature_ref=signature_ref,
            contains_pickle=False,
            metadata={
                "source": "knowledge_artifact_compiler",
                "task_family": artifact.get("task_family"),
                "source_ref_security_gate": source_ref_security_gate,
                "blocked_source_refs": blocked_source_refs,
                "control_panel_replay": artifact.get("control_panel_replay") or {},
                "mutation_allowed": False,
            },
        )


def _policy_targets(request: ArtifactScanRequest) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"artifact::{request.artifact_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": True,
                "license_state": "approved" if request.license_status == "approved" else None,
                "provenance_refs": request.provenance_refs,
            },
        }
    ]


def _record_checksum_verified(record: dict[str, Any]) -> bool | None:
    """Recompute the on-disk sha256 and compare to the claimed hash.

    Returns None when the file is not locally present or the record carries no hash (nothing to
    check), True on a match, and False on a mismatch (tampering or corruption).
    """
    claimed = str(record.get("hash") or "")
    artifact_path = Path(str(record.get("artifact_path") or ""))
    if not claimed or not artifact_path.is_file():
        return None
    try:
        return file_sha256(artifact_path) == claimed
    except OSError:
        return None


def _trust_findings(request: ArtifactScanRequest) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    source_ref_security_gate = request.metadata.get("source_ref_security_gate") or {}
    if request.metadata.get("signature_state") == "signed_ed25519" and request.metadata.get("signature_verified") is False:
        findings.append(
            {
                "rule_id": "artifact_signature_verification_failed",
                "severity": "hard_fail",
                "message": "Artifact claims an ed25519 signature that does not cryptographically verify; quarantine until re-signed.",
            }
        )
    if request.metadata.get("checksum_verified") is False:
        findings.append(
            {
                "rule_id": "artifact_checksum_mismatch",
                "severity": "hard_fail",
                "message": "Artifact on-disk content hash does not match the signed/claimed checksum; quarantine until re-verified.",
            }
        )
    if int(source_ref_security_gate.get("blocked_count") or 0) > 0:
        findings.append(
            {
                "rule_id": "kac_source_ref_security_gate_blocked",
                "severity": "hard_fail",
                "message": "KAC artifacts with blocked source refs must remain quarantined until the source-ref gate is cleared.",
                "blocked_source_refs": request.metadata.get("blocked_source_refs") or [],
            }
        )
    if request.contains_pickle or request.format in {"pickle", "bin"}:
        findings.append(
            {
                "rule_id": "artifact_pickle_serialization_risk",
                "severity": "hard_fail",
                "message": "Pickle or raw PyTorch binary artifacts require quarantine and explicit review.",
            }
        )
    if not request.checksum:
        findings.append(
            {
                "rule_id": "artifact_requires_checksum",
                "severity": "hard_fail",
                "message": "Artifact scans require a checksum before use.",
            }
        )
    if not request.signature_ref:
        findings.append(
            {
                "rule_id": "artifact_requires_signature_or_signed_manifest",
                "severity": "hard_fail",
                "message": "Artifact scans require a signature reference or signed manifest.",
            }
        )
    return findings


def _reason_codes(request: ArtifactScanRequest, *, blocked: bool) -> list[str]:
    reasons: list[str] = []
    source_ref_security_gate = request.metadata.get("source_ref_security_gate") or {}
    if int(source_ref_security_gate.get("blocked_count") or 0) > 0:
        reasons.append("kac_source_ref_security_gate_blocked")
    if request.format == "safetensors":
        reasons.append("safetensors_preferred")
    if request.checksum:
        reasons.append("checksum_present")
    if request.signature_ref:
        reasons.append("signature_present")
    if request.provenance_refs:
        reasons.append("provenance_present")
    if blocked:
        reasons.append("quarantine_required")
    return reasons


def _deep_replay_lifecycle_promotion(records: list[dict[str, Any]]) -> dict[str, Any]:
    blockers: list[str] = []
    blocked_lifecycle_count = 0
    for record in records:
        artifact_path = Path(str(record.get("artifact_path") or ""))
        if artifact_path.name != "lifecycle_report.json" or not artifact_path.is_file():
            continue
        try:
            lifecycle = json.loads(artifact_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            blockers.append("lifecycle_report_unreadable")
            blocked_lifecycle_count += 1
            continue
        lifecycle_blockers = [str(item) for item in lifecycle.get("blocked_reasons") or []]
        growth_engine_gate = lifecycle.get("growth_engine_gate") or {}
        if growth_engine_gate.get("allowed") is False:
            lifecycle_blockers.extend(str(item) for item in growth_engine_gate.get("blockers") or [])
        if str(lifecycle.get("status") or "") == "closed_loop_blocked":
            lifecycle_blockers.append("production_lifecycle_blocked")
        if lifecycle_blockers:
            blocked_lifecycle_count += 1
            blockers.extend(lifecycle_blockers)
    return {
        "promotion_blockers": sorted(set(blockers)),
        "blocked_lifecycle_count": blocked_lifecycle_count,
    }


def _format_from_uri(uri: str) -> ArtifactFormat:
    suffix = Path(uri).suffix.lower().lstrip(".")
    if suffix in {"safetensors", "gguf", "onnx", "mlx", "mnn", "executorch", "pickle", "bin", "zip"}:
        return suffix  # type: ignore[return-value]
    return "unknown"


def _required_controls() -> list[str]:
    return [
        "license_review",
        "provenance_refs",
        "checksum_verification",
        "signature_or_signed_manifest",
        "pickle_scanning",
        "unsafe_format_quarantine",
        "ai_bom_or_ml_bom",
        "runtime_plugin_trust",
        "kac_source_ref_security_gate",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/artifact-trust"},
        "scan": {"method": "POST", "endpoint": "/ops/brain/artifact-trust/scans"},
        "scan_knowledge_artifact": {"method": "POST", "endpoint": "/ops/brain/artifact-trust/knowledge-artifacts/scan"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/artifact-trust-registry"},
    }
