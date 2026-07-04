from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class Tier5FallbackService:
    def __init__(self, *, artifacts_dir: Path | str, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "tier5-fallback"
        self.events = events

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        items = self._records(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "cloud_fallback_allowed_as_governed_tier": True,
            "fallback_count": len(items),
            "status_counts": self._counts(items, "status"),
            "provider_counts": self._source_provider_counts(items),
            "execution_allowed": False,
            "mutation_allowed": False,
            "latest_fallback": items[0] if items else None,
            "items": items,
        }

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "cloud_fallback_allowed_as_governed_tier": True,
            "fallback_count": payload["fallback_count"],
            "status_counts": payload["status_counts"],
            "execution_allowed": False,
            "mutation_allowed": False,
            "latest_fallback": payload["latest_fallback"],
        }

    def evaluate(
        self,
        *,
        provider_id: str,
        fallback_reason: str,
        privacy_posture: str | None,
        cost_posture: dict[str, Any] | None,
        approval_decision: str = "not_requested",
        gateway_decision: str = "hold",
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        if not privacy_posture:
            raise ValueError("privacy_posture is required for Tier 5 fallback")
        if not cost_posture:
            raise ValueError("cost_posture is required for Tier 5 fallback")
        record_id = new_id("tier5fallback")
        trace_ids = list(linked_trace_ids or []) or [f"trace_{record_id}"]
        status = "denied" if gateway_decision == "deny" else "approval_required"
        path = self.output_dir / f"{record_id}.json"
        record = {
            "record_id": record_id,
            "status": status,
            "tier": "tier_5_governed_cloud",
            "capability_family": "provider_fallback",
            "source": {
                "source_type": "tier5_fallback",
                "provider_id": provider_id,
                "fallback_reason": fallback_reason,
                "observed_at": utcnow().isoformat(),
            },
            "target_subsystem": "runtime",
            "hardware_profile": {"local_satisfied_policy": False, "cloud_fallback_requested": True},
            "runtime_candidates": [{"runtime_id": "tier5-cloud-router", "execution_allowed": False}],
            "provider_candidates": [{"provider_id": provider_id, "registration_allowed": False, "execution_allowed": False}],
            "model_artifact_formats": ["provider-native", "openai-compatible"],
            "quantization_posture": {"state": "provider_declared"},
            "offline_posture": "cloud_required_after_governance",
            "privacy_posture": privacy_posture,
            "cost_posture": cost_posture,
            "policy_path": [{"stage": "tier5-fallback", "decision": gateway_decision, "reason": "gateway-and-product-sweep-required"}],
            "approval_path": {
                "decision": approval_decision if approval_decision != "approved" else "approved_for_validation_only",
                "human_approval_is_not_execution_authority": True,
            },
            "product_sweep_gate_ids": ["tier5-cloud-fallback-gate", "privacy-redaction-gate", "cost-budget-gate", "gateway-policy"],
            "eval_suite_ids": ["runtime_quality", "prompt_security_red_team"],
            "telemetry_trace_ids": trace_ids,
            "provenance": {"metadata_only": True, "created_at": utcnow().isoformat()},
            "artifacts": [str(path).replace("\\", "/")],
            "execution_allowed": False,
            "mutation_allowed": False,
        }
        self._write(record)
        self._event("tier5.fallback_requested", record)
        self._event("tier5.fallback_denied" if status == "denied" else "tier5.fallback_approval_required", record)
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def _records(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        items = []
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(items) >= limit:
                break
        return items

    def _write(self, record: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{record['record_id']}.json"
        record["artifacts"] = [str(path).replace("\\", "/")]
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _event(self, event_type: str, record: dict[str, Any]) -> None:
        if not self.events:
            return
        self.events.record(
            event_type=event_type,
            subject=f"tier5:{record['record_id']}",
            trace_ids=record.get("telemetry_trace_ids", []),
            payload={
                "record_id": record["record_id"],
                "provider_id": record["source"]["provider_id"],
                "status": record["status"],
                "decision": record["policy_path"][0]["decision"],
                "execution_allowed": False,
                "mutation_allowed": False,
            },
        )

    def _counts(self, items: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = str(item.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _source_provider_counts(self, items: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            provider_id = str((item.get("source") or {}).get("provider_id") or "unknown")
            counts[provider_id] = counts.get(provider_id, 0) + 1
        return counts
