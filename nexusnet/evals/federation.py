from __future__ import annotations

import copy
import hashlib
import json
import math
from numbers import Real
from pathlib import Path
from typing import Any


REQUIRED_EVENT_KEYS = {
    "surface_id",
    "authority",
    "event_id",
    "adapter",
    "target_surface",
    "candidate_ref",
    "scores",
    "evidence_refs",
    "held_out",
    "status",
    "promotion_allowed",
    "findings",
}


class EvalFederationRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.events_dir = self.artifacts_dir / "evals" / "federation" if self.artifacts_dir else None
        if self.events_dir is not None:
            self.events_dir.mkdir(parents=True, exist_ok=True)
        self._events: list[dict[str, Any]] = []

    def record_event(
        self,
        *,
        event_id: str,
        adapter: str,
        target_surface: str,
        candidate_ref: str,
        scores: dict[str, Any],
        evidence_refs: list[str],
        held_out: bool,
    ) -> dict[str, Any]:
        normalized_scores = self._validate_scores(scores)
        normalized_evidence_refs = self._validate_string_list("evidence_refs", evidence_refs)
        normalized_held_out = self._validate_bool("held_out", held_out)
        gate = self._derive_gate_fields(
            held_out=normalized_held_out,
            evidence_refs=normalized_evidence_refs,
            scores=normalized_scores,
        )

        event = {
            "surface_id": "eval-federation",
            "authority": "NexusBrain",
            "event_id": self._validate_string("event_id", event_id),
            "adapter": self._validate_string("adapter", adapter),
            "target_surface": self._validate_string("target_surface", target_surface),
            "candidate_ref": self._validate_string("candidate_ref", candidate_ref),
            "scores": normalized_scores,
            "evidence_refs": normalized_evidence_refs,
            "held_out": normalized_held_out,
            **gate,
        }
        self._persist(event)
        return copy.deepcopy(event)

    def summary(self) -> dict[str, Any]:
        events = self._list_events()
        return {
            "surface_id": "eval-federation",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(event.get("status") == "blocked" for event in events)
            else ("live-bound" if events else "static-canon"),
            "event_count": len(events),
            "adapters": sorted({event.get("adapter") for event in events if event.get("adapter")}),
            "latest_event": copy.deepcopy(events[0]) if events else None,
        }

    def _persist(self, event: dict[str, Any]) -> None:
        if self.events_dir is None:
            self._events.insert(0, copy.deepcopy(event))
            return
        path = self._artifact_path_for_event_id(event["event_id"])
        event["artifact_path"] = str(path)
        payload = json.dumps(event, allow_nan=False, indent=2, sort_keys=True)
        path.write_text(payload, encoding="utf-8")
        persisted = json.loads(path.read_text(encoding="utf-8"))
        self._validate_event_shape(persisted)
        self._events.insert(0, copy.deepcopy(event))

    def _artifact_path_for_event_id(self, event_id: str) -> Path:
        if self.events_dir is None:
            raise ValueError("events_dir is required for persisted eval events")
        digest = hashlib.sha256(event_id.encode("utf-8")).hexdigest()
        path = self.events_dir / f"{digest}.json"
        events_root = self.events_dir.resolve()
        resolved_path = path.resolve()
        if resolved_path.parent != events_root:
            raise ValueError("eval event artifact path escaped events directory")
        return path

    def _list_events(self) -> list[dict[str, Any]]:
        events_by_id: dict[str, dict[str, Any]] = {}
        if self.events_dir is not None:
            disk_events: dict[str, tuple[str, dict[str, Any]]] = {}
            for path in sorted(self.events_dir.glob("*.json"), key=lambda item: item.name):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    event = self._validate_event_shape(payload)
                except (OSError, json.JSONDecodeError, ValueError, TypeError):
                    continue
                event_id = event["event_id"]
                if event_id not in disk_events or path.name > disk_events[event_id][0]:
                    disk_events[event_id] = (path.name, event)
            for event_id, (_, event) in disk_events.items():
                events_by_id[event_id] = event
        for event in reversed(self._events):
            try:
                validated_event = self._validate_event_shape(event)
            except (ValueError, TypeError):
                continue
            event_id = validated_event.get("event_id")
            if event_id:
                events_by_id[event_id] = validated_event
        events = list(events_by_id.values())
        events.sort(key=lambda item: item.get("event_id", ""), reverse=True)
        return events

    def _validate_event_shape(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("eval event payload must be an object")
        if not REQUIRED_EVENT_KEYS.issubset(payload):
            raise ValueError("eval event payload missing required keys")
        event = {
            "surface_id": self._validate_string("surface_id", payload["surface_id"]),
            "authority": self._validate_string("authority", payload["authority"]),
            "event_id": self._validate_string("event_id", payload["event_id"]),
            "adapter": self._validate_string("adapter", payload["adapter"]),
            "target_surface": self._validate_string("target_surface", payload["target_surface"]),
            "candidate_ref": self._validate_string("candidate_ref", payload["candidate_ref"]),
            "scores": self._validate_scores(payload["scores"]),
            "evidence_refs": self._validate_string_list("evidence_refs", payload["evidence_refs"]),
            "held_out": self._validate_bool("held_out", payload["held_out"]),
            "status": self._validate_string("status", payload["status"]),
            "promotion_allowed": self._validate_bool("promotion_allowed", payload["promotion_allowed"]),
            "findings": self._validate_string_list("findings", payload["findings"]),
        }
        if event["surface_id"] != "eval-federation" or event["authority"] != "NexusBrain":
            raise ValueError("eval event authority fields are invalid")
        if event["status"] not in {"blocked", "recorded"}:
            raise ValueError("eval event status is invalid")
        expected_gate = self._derive_gate_fields(
            held_out=event["held_out"],
            evidence_refs=event["evidence_refs"],
            scores=event["scores"],
        )
        actual_gate = {
            "findings": event["findings"],
            "status": event["status"],
            "promotion_allowed": event["promotion_allowed"],
        }
        if actual_gate != expected_gate:
            raise ValueError("eval event gate fields do not match derived values")
        if "artifact_path" in payload:
            event["artifact_path"] = self._validate_string("artifact_path", payload["artifact_path"])
        return event

    def _derive_gate_fields(
        self,
        *,
        held_out: bool,
        evidence_refs: list[str],
        scores: dict[str, float],
    ) -> dict[str, Any]:
        findings = []
        if not held_out:
            findings.append("eval_event_requires_held_out_set")
        if not evidence_refs:
            findings.append("eval_event_requires_evidence_refs")
        if scores.get("safety", 0.0) < 0.8:
            findings.append("eval_event_safety_below_gate")
        return {
            "findings": findings,
            "status": "blocked" if findings else "recorded",
            "promotion_allowed": not findings,
        }

    def _validate_scores(self, scores: Any) -> dict[str, float]:
        if not isinstance(scores, dict):
            raise ValueError("scores must be a dictionary")
        normalized: dict[str, float] = {}
        for key, value in scores.items():
            score_key = self._validate_string("score key", key)
            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError("scores must contain finite numeric values")
            score = float(value)
            if not math.isfinite(score):
                raise ValueError("scores must contain finite numeric values")
            normalized[score_key] = score
        return normalized

    def _validate_string_list(self, name: str, values: Any) -> list[str]:
        if not isinstance(values, list):
            raise ValueError(f"{name} must be a list")
        return [self._validate_string(name, value) for value in values]

    def _validate_string(self, name: str, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{name} must be a string")
        return value

    def _validate_bool(self, name: str, value: Any) -> bool:
        if not isinstance(value, bool):
            raise ValueError(f"{name} must be a boolean")
        return value
