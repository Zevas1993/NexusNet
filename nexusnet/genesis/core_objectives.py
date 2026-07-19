from __future__ import annotations

import hashlib
import hmac
import json
import math
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


class GenesisCoreObjectivesLedgerService:
    """Fail-closed core-objective evidence with an integrity-linked local history."""

    _REQUIRED_METRICS = ("quality_score", "robustness_score")
    _HARD_OBJECTIVES = ("safety_score", "privacy_score", "authority_score", "traceability_score")
    _PRIORITY_ORDER = ("safety", "privacy", "authority", "traceability", "robustness", "quality")

    def __init__(self, *, artifacts_dir: Path | str, event_spine: Any | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.event_spine = event_spine
        self.root = self.artifacts_dir / "genesis" / "core-objectives"
        self.assessments_dir = self.root / "assessments"
        self.baseline_path = self.root / "immutable-baseline.json"
        self.history_path = self.root / "integrity-history.jsonl"
        self.key_path = self.root / "local-integrity-key.json"
        self._ensure_baseline()

    def assess(
        self,
        *,
        candidate_ref: str,
        candidate_kind: str,
        objective_metrics: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        integrity = self._verify_history()
        if integrity != "valid-local-hmac-chain":
            raise RuntimeError("core objectives integrity history is invalid; candidate evaluation is blocked")

        assessment_id = "core-objectives-assessment::" + _digest(
            "|".join((str(candidate_ref), str(candidate_kind), _utcnow()))
        )
        assessment = {
            "schema_version": "nexusnet-genesis-core-objectives-assessment-v1",
            "surface_id": "genesis-core-objectives-ledger",
            "assessment_id": assessment_id,
            "candidate_ref": _safe_ref(candidate_ref),
            "candidate_kind": _safe_ref(candidate_kind),
            "artifact_ref": f"genesis/core-objectives/assessments/{_artifact_id(assessment_id)}.json",
            "immutable_baseline_ref": "genesis/core-objectives/immutable-baseline.json",
            "priority_order": list(self._PRIORITY_ORDER),
            **self._assess_metrics(objective_metrics),
            "created_at": _utcnow(),
            "raw_metric_values_included": False,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        entry = self._append_history(assessment)
        assessment["integrity_entry_ref"] = entry["entry_ref"]
        assessment["integrity_status"] = "valid-local-hmac-chain"
        assessment["shared_event_spine"] = self._publish_event(
            event_type=(
                "genesis.core_objectives.blocked"
                if assessment["shadow_governance_allowed"] is False
                else "genesis.core_objectives.assessed"
            ),
            correlation_ref=assessment_id,
            artifact_refs=[assessment["artifact_ref"], assessment_id, candidate_ref],
        )
        self._write(assessment, Path(assessment["artifact_ref"]))
        return assessment

    def summary(self) -> dict[str, Any]:
        records, integrity_status = self._history()
        assessments = [record.get("assessment") for record in records if isinstance(record.get("assessment"), dict)]
        assessments.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        baseline = self._load_json(self.baseline_path)
        robustness_regression_count = sum(
            1 for item in assessments if item.get("status") == "blocked-robustness-regression"
        )
        return {
            "schema_version": "nexusnet-genesis-core-objectives-ledger-v1",
            "surface_id": "genesis-core-objectives-ledger",
            "status": "live-with-core-objective-evidence" if assessments else "live-awaiting-core-objective-evidence",
            "honest_status_label": (
                "core-objectives-ledger-live-with-local-integrity-evidence"
                if assessments
                else "core-objectives-ledger-live-awaiting-candidate-evidence"
            ),
            "immutable_by_default": True,
            "baseline_mutation_endpoint_available": False,
            "priority_order": list(baseline.get("priority_order") or self._PRIORITY_ORDER),
            "integrity_status": integrity_status,
            "integrity_contract": {
                "history": "append-only-local-hmac-chain-v1",
                "external_signature_required_for_production": True,
                "local_hmac_is_not_an_external_production_signature": True,
            },
            "assessment_count": len(assessments),
            "robustness_regression_count": robustness_regression_count,
            "blocked_assessment_count": sum(
                1 for item in assessments if item.get("shadow_governance_allowed") is False
            ),
            "latest_assessment": assessments[0] if assessments else None,
            "raw_metric_values_included": False,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def _assess_metrics(self, objective_metrics: Mapping[str, Any] | None) -> dict[str, Any]:
        if objective_metrics is None:
            return {
                "status": "not-evaluated-objective-metrics-missing",
                "shadow_governance_allowed": True,
                "production_promotion_allowed": False,
                "blockers": ["objective_metrics_required_for_production_promotion"],
                "quality_improved": None,
                "robustness_regressed": None,
                "regressed_hard_objectives": [],
                "metric_contract": "objective-metrics-not-supplied-shadow-governance-only",
            }
        if not isinstance(objective_metrics, Mapping):
            return self._invalid_metrics("objective_metrics_must_be_an_object")

        baseline = objective_metrics.get("baseline")
        candidate = objective_metrics.get("candidate")
        if not isinstance(baseline, Mapping) or not isinstance(candidate, Mapping):
            return self._invalid_metrics("baseline_and_candidate_objective_metrics_required")
        if any(not _finite_number(baseline.get(name)) or not _finite_number(candidate.get(name)) for name in self._REQUIRED_METRICS):
            return self._invalid_metrics("quality_and_robustness_numeric_metrics_required")

        quality_improved = float(candidate["quality_score"]) > float(baseline["quality_score"])
        robustness_regressed = float(candidate["robustness_score"]) < float(baseline["robustness_score"])
        regressed_hard_objectives = [
            name
            for name in self._HARD_OBJECTIVES
            if _finite_number(baseline.get(name))
            and _finite_number(candidate.get(name))
            and float(candidate[name]) < float(baseline[name])
        ]
        if quality_improved and robustness_regressed:
            return {
                "status": "blocked-robustness-regression",
                "shadow_governance_allowed": False,
                "production_promotion_allowed": False,
                "blockers": ["robustness_regressed_despite_score_gain"],
                "quality_improved": True,
                "robustness_regressed": True,
                "regressed_hard_objectives": regressed_hard_objectives,
                "metric_contract": "declared-baseline-and-candidate-objective-metrics-v1",
            }
        if regressed_hard_objectives:
            return {
                "status": "blocked-core-objective-drift",
                "shadow_governance_allowed": False,
                "production_promotion_allowed": False,
                "blockers": ["hard_core_objective_regressed"],
                "quality_improved": quality_improved,
                "robustness_regressed": robustness_regressed,
                "regressed_hard_objectives": regressed_hard_objectives,
                "metric_contract": "declared-baseline-and-candidate-objective-metrics-v1",
            }
        return {
            "status": "aligned-with-declared-objective-metrics",
            "shadow_governance_allowed": True,
            "production_promotion_allowed": True,
            "blockers": [],
            "quality_improved": quality_improved,
            "robustness_regressed": robustness_regressed,
            "regressed_hard_objectives": [],
            "metric_contract": "declared-baseline-and-candidate-objective-metrics-v1",
        }

    def _invalid_metrics(self, blocker: str) -> dict[str, Any]:
        return {
            "status": "blocked-invalid-objective-metrics",
            "shadow_governance_allowed": False,
            "production_promotion_allowed": False,
            "blockers": [blocker],
            "quality_improved": None,
            "robustness_regressed": None,
            "regressed_hard_objectives": [],
            "metric_contract": "invalid-objective-metrics",
        }

    def _ensure_baseline(self) -> None:
        if self.baseline_path.exists():
            return
        self._write(
            {
                "schema_version": "nexusnet-genesis-core-objectives-baseline-v1",
                "surface_id": "genesis-core-objectives-baseline",
                "immutable_by_default": True,
                "priority_order": list(self._PRIORITY_ORDER),
                "production_mutation_requires_external_signature": True,
                "created_at": _utcnow(),
                "raw_content_included": False,
            },
            self.baseline_path.relative_to(self.artifacts_dir),
        )

    def _append_history(self, assessment: dict[str, Any]) -> dict[str, Any]:
        records, integrity_status = self._history()
        if integrity_status != "valid-local-hmac-chain":
            raise RuntimeError("core objectives integrity history is invalid; append is blocked")
        previous_signature = str(records[-1].get("entry_signature") or "genesis") if records else "genesis"
        entry = {
            "schema_version": "nexusnet-genesis-core-objectives-integrity-entry-v1",
            "entry_ref": "core-objectives-history::" + _digest(
                "|".join((assessment["assessment_id"], previous_signature))
            ),
            "sequence": len(records) + 1,
            "previous_signature": previous_signature,
            "assessment": assessment,
        }
        entry["entry_signature"] = self._sign(entry)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(_canonical_json(entry) + "\n")
        return entry

    def _history(self) -> tuple[list[dict[str, Any]], str]:
        if not self.history_path.exists():
            return [], "valid-local-hmac-chain"
        try:
            lines = [line for line in self.history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            records = [json.loads(line) for line in lines]
        except (OSError, json.JSONDecodeError):
            return [], "invalid-local-hmac-chain"
        if not all(isinstance(record, dict) for record in records):
            return [], "invalid-local-hmac-chain"
        previous_signature = "genesis"
        for sequence, record in enumerate(records, start=1):
            if record.get("sequence") != sequence or record.get("previous_signature") != previous_signature:
                return [], "invalid-local-hmac-chain"
            signature = str(record.get("entry_signature") or "")
            if not signature or not hmac.compare_digest(signature, self._sign(record)):
                return [], "invalid-local-hmac-chain"
            previous_signature = signature
        return records, "valid-local-hmac-chain"

    def _verify_history(self) -> str:
        return self._history()[1]

    def _sign(self, record: dict[str, Any]) -> str:
        unsigned = dict(record)
        unsigned.pop("entry_signature", None)
        return "hmac-sha256:" + hmac.new(
            self._integrity_key().encode("utf-8"),
            _canonical_json(unsigned).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _integrity_key(self) -> str:
        loaded = self._load_json(self.key_path)
        key = str(loaded.get("local_hmac_key") or "")
        if key:
            return key
        key = secrets.token_hex(32)
        self._write(
            {
                "schema_version": "nexusnet-genesis-core-objectives-local-integrity-key-v1",
                "key_scope": "local-artifact-store-only",
                "local_hmac_key": key,
            },
            self.key_path.relative_to(self.artifacts_dir),
        )
        return key

    def _load_json(self, path: Path) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _write(self, payload: dict[str, Any], relative_path: Path) -> None:
        path = self.artifacts_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(path)

    def _publish_event(self, *, event_type: str, correlation_ref: str, artifact_refs: list[Any]) -> dict[str, Any]:
        publish = getattr(self.event_spine, "publish_event", None)
        if not callable(publish):
            return {"status": "not-configured", "raw_content_included": False}
        return publish(
            event_type=event_type,
            source_surface_id="genesis-core-objectives-ledger",
            correlation_ref=correlation_ref,
            privacy_label="sanitized-genesis-core-objective-evidence",
            artifact_refs=[_safe_ref(ref) for ref in artifact_refs if ref],
            planes=["governance", "eval", "authority", "robustness", "privacy"],
        )


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _safe_ref(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    if not text:
        return ""
    lowered = text.lower()
    if len(text) > 240 or ":/" in text or any(marker in lowered for marker in ("secret", "password", "token", "api-key", "apikey")):
        return "ref-digest::" + _digest(text)
    return text


def _artifact_id(value: str) -> str:
    return "".join(character if character.isalnum() or character in "._-" else "-" for character in value).strip("-")


def _digest(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:24]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
