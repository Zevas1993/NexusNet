from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .calibration import BoundedHostCalibrator
from .feasibility import CandidateFeasibilityEvaluator
from .fingerprints import synthetic_model_fingerprint
from .hardware import HardwareCapabilityDiscoverer
from .primitives import InferencePrimitiveRegistry
from .schemas import EvolutionaryInferenceEvidence, ModelExecutionFingerprint


_ARTIFACT_REF = "runtime/evolutionary-inference/foundation-v1.json"


class EvolutionaryInferenceFoundation:
    def __init__(
        self,
        *,
        artifacts_dir: Path | None = None,
        discoverer: HardwareCapabilityDiscoverer | None = None,
        calibrator: BoundedHostCalibrator | None = None,
        registry: InferencePrimitiveRegistry | None = None,
        evaluator: CandidateFeasibilityEvaluator | None = None,
    ) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.artifact_path = self.artifacts_dir / _ARTIFACT_REF if self.artifacts_dir is not None else None
        self.discoverer = discoverer or HardwareCapabilityDiscoverer(
            storage_root=str(self.artifacts_dir or Path.cwd())
        )
        self.calibrator = calibrator or BoundedHostCalibrator()
        self.registry = registry or InferencePrimitiveRegistry.default()
        self.evaluator = evaluator or CandidateFeasibilityEvaluator()
        self._evidence: EvolutionaryInferenceEvidence | None = None
        self._load_error: str | None = None

    def establish_baseline(
        self,
        *,
        model_fingerprint: ModelExecutionFingerprint | None = None,
    ) -> EvolutionaryInferenceEvidence:
        graph = self.discoverer.discover()
        graph = graph.model_copy(update={"calibration": self.calibrator.calibrate()})
        fingerprint = model_fingerprint or synthetic_model_fingerprint()
        feasibility = self.evaluator.evaluate(graph=graph, fingerprint=fingerprint, registry=self.registry)
        created_at = datetime.now(timezone.utc)
        evidence_id = _evidence_id(graph.host_fingerprint, fingerprint.fingerprint_id, created_at)
        evidence = EvolutionaryInferenceEvidence(
            evidence_id=evidence_id,
            created_at=created_at,
            hardware=graph,
            model_fingerprint=fingerprint,
            primitives=self.registry.list(),
            feasibility=feasibility,
            artifact_ref=_ARTIFACT_REF if self.artifact_path is not None else None,
        )
        self._evidence = evidence
        self._load_error = None
        self._persist(evidence)
        return evidence

    def status(self, *, ensure_baseline: bool = False) -> dict[str, Any]:
        if self._evidence is None and self._load_error is None:
            self._load()
        if self._load_error is not None:
            return {
                "status_label": "MEASURED SHADOW",
                "surface_id": "evolutionary-inference-foundation",
                "authority": "NexusBrain",
                "runtime_state": "degraded-evidence",
                "reason_codes": [self._load_error],
                "artifact_ref": _ARTIFACT_REF if self.artifact_path is not None else None,
                "policy_mutation_allowed": False,
            }
        if self._evidence is None and ensure_baseline:
            try:
                self.establish_baseline()
            except Exception:
                self._load_error = "baseline-establishment-failed"
                return self.status()
        if self._evidence is None:
            return {
                "status_label": "MEASURED SHADOW",
                "surface_id": "evolutionary-inference-foundation",
                "authority": "NexusBrain",
                "runtime_state": "uninitialized",
                "reason_codes": ["baseline-not-established"],
                "artifact_ref": _ARTIFACT_REF if self.artifact_path is not None else None,
                "policy_mutation_allowed": False,
            }
        evidence = self._evidence
        return {
            "status_label": "MEASURED SHADOW",
            "surface_id": "evolutionary-inference-foundation",
            "authority": "NexusBrain",
            "runtime_state": "live-evidence",
            "evidence_id": evidence.evidence_id,
            "created_at": evidence.created_at.isoformat(),
            "artifact_ref": evidence.artifact_ref,
            "host_fingerprint": evidence.hardware.host_fingerprint,
            "hardware": evidence.hardware.model_dump(mode="json"),
            "model_fingerprint": evidence.model_fingerprint.model_dump(mode="json"),
            "primitive_ids": [primitive.primitive_id for primitive in evidence.primitives],
            "feasibility": evidence.feasibility.model_dump(mode="json"),
            "reason_codes": evidence.feasibility.reason_codes,
            "policy_mutation_allowed": False,
        }

    def _persist(self, evidence: EvolutionaryInferenceEvidence) -> None:
        if self.artifact_path is None:
            return
        self.artifact_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.artifact_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(evidence.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary.replace(self.artifact_path)

    def _load(self) -> None:
        if self.artifact_path is None or not self.artifact_path.exists():
            return
        try:
            payload = json.loads(self.artifact_path.read_text(encoding="utf-8"))
            self._evidence = EvolutionaryInferenceEvidence.model_validate(payload)
        except (OSError, json.JSONDecodeError, ValueError):
            self._load_error = "persisted-evidence-invalid"


def _evidence_id(host_fingerprint: str, model_fingerprint: str, created_at: datetime) -> str:
    canonical = f"{host_fingerprint}|{model_fingerprint}|{created_at.isoformat()}"
    return f"evolutionary-inference::{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:24]}"
