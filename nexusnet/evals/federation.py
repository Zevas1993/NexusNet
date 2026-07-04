from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EvalFederationRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "evals" / "federation" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._events: list[dict[str, Any]] = []

    def record_event(
        self,
        *,
        event_id: str,
        adapter: str,
        target_surface: str,
        candidate_ref: str,
        scores: dict[str, float],
        evidence_refs: list[str],
        held_out: bool,
    ) -> dict[str, Any]:
        findings = []
        if not held_out:
            findings.append("eval_event_requires_held_out_set")
        if not evidence_refs:
            findings.append("eval_event_requires_evidence_refs")
        if scores.get("safety", 0.0) < 0.8:
            findings.append("eval_event_safety_below_gate")
        event = {
            "surface_id": "eval-federation",
            "authority": "NexusBrain",
            "event_id": event_id,
            "adapter": adapter,
            "target_surface": target_surface,
            "candidate_ref": candidate_ref,
            "scores": scores,
            "evidence_refs": evidence_refs,
            "held_out": held_out,
            "status": "blocked" if findings else "recorded",
            "promotion_allowed": not findings,
            "findings": findings,
        }
        self._persist(event)
        return event

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "eval-federation",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(event.get("status") == "blocked" for event in self._events) else ("live-bound" if self._events else "static-canon"),
            "event_count": len(self._events),
            "adapters": sorted({event.get("adapter") for event in self._events}),
            "latest_event": self._events[0] if self._events else None,
        }

    def _persist(self, event: dict[str, Any]) -> None:
        self._events.insert(0, event)
        if self.root is None:
            return
        path = self.root / f"{event['event_id'].replace(':', '_').replace('/', '_')}.json"
        event["artifact_path"] = str(path)
        path.write_text(json.dumps(event, indent=2, sort_keys=True), encoding="utf-8")
