from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow


class RuntimeDecisionLedger:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "runtime" / "decision-ledger" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def record(
        self,
        *,
        decision_id: str,
        route_decision: dict[str, Any],
        cache_state: dict[str, Any],
        quantization_state: dict[str, Any],
        eval_state: dict[str, Any],
        evidence_refs: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        findings = []
        if not evidence_refs:
            findings.append("runtime_decision_requires_evidence_refs")
        if str(route_decision.get("status") or "").startswith("blocked"):
            findings.append("runtime_decision_route_blocked")
        if cache_state.get("promotion_allowed") is not True:
            findings.append("runtime_decision_cache_gate_not_clear")
        if quantization_state.get("promotion_blockers"):
            findings.append("runtime_decision_quantization_blocked")
        if eval_state.get("promotion_allowed") is not True:
            findings.append("runtime_decision_eval_gate_not_clear")
        record = {
            "surface_id": "runtime-decision-ledger",
            "authority": "NexusBrain",
            "decision_id": decision_id,
            "route_decision": route_decision,
            "cache_state": cache_state,
            "quantization_state": quantization_state,
            "eval_state": eval_state,
            "evidence_refs": evidence_refs,
            "created_at": utcnow().isoformat(),
            "estimated_cost_usd": float(route_decision.get("estimated_cost_usd") or 0.0),
            "status": "blocked" if findings else "ready-shadow",
            "promotion_allowed": not findings,
            "findings": findings,
            "metadata": metadata or {},
        }
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        all_records = self._list_records(limit=max(limit, 50))
        records = all_records[:limit]
        return {
            "surface_id": "runtime-decision-ledger",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(record.get("status") == "blocked" for record in all_records) else ("live-bound" if all_records else "static-canon"),
            "decision_count": len(all_records),
            "latest_decision": all_records[0] if all_records else None,
            "decisions": records,
            "recent_decisions": records,
            "control_panel_label": "Runtime Decision Ledger",
            "promotion_boundary": "runtime decisions remain shadow-only until route, cache, quantization, eval, and fallback evidence clear",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._records.insert(0, record)
        if self.root is None:
            return
        path = self.root / f"{record['decision_id'].replace(':', '_').replace('/', '_')}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._records)
        seen = {record.get("decision_id") for record in records}
        if self.root is not None:
            for path in self.root.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("decision_id") in seen:
                    continue
                records.append(payload)
                seen.add(payload.get("decision_id"))
        records.sort(key=lambda item: item.get("created_at") or item.get("decision_id") or "", reverse=True)
        return records[:limit]
