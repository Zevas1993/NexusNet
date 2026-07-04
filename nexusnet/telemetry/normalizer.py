from __future__ import annotations

import hashlib
from typing import Any


class NormalizedTelemetryService:
    """Maps NexusNet lifecycle records into stable GenAI-style operator spans."""

    EVENT_KIND_PREFIXES = {
        "workflow.": "workflow",
        "parallel_run.": "parallel_run",
        "package_candidate.": "package_candidate",
        "assimilation.": "assimilation",
        "plan.": "approval",
        "tool.": "tool",
        "provider.": "provider",
        "memory.": "memory",
        "retrieval.": "retrieval",
        "runtime.": "runtime",
        "adaptive.": "adaptive",
        "research_scout.": "research_scout",
        "self_improvement.": "self_improvement",
        "tier5.": "tier5",
        "context_graph.": "context_graph",
        "factory_orchestration.": "factory_orchestration",
        "execution_authority.": "execution_authority",
        "harness_engineering.": "harness_engineering",
        "autonomous_growth.": "autonomous_growth",
        "protocol.": "protocol",
        "product_sweep.": "product_sweep",
    }

    def __init__(self, *, events: Any | None = None, store: Any | None = None):
        self.events = events
        self.store = store

    def summary(self, *, limit: int = 200) -> dict[str, Any]:
        spans = self.spans(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "span_count": len(spans),
            "span_kind_counts": self._counts(spans, "span_kind"),
            "trace_health": self._trace_health(spans),
            "spans": spans,
        }

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "span_count": payload["span_count"],
            "span_kind_counts": payload["span_kind_counts"],
            "trace_health": payload["trace_health"],
            "latest_span": payload["spans"][0] if payload["spans"] else None,
        }

    def spans(self, *, limit: int = 200) -> list[dict[str, Any]]:
        event_items = self.events.list(limit=limit) if self.events else []
        spans = [self._event_span(event) for event in event_items]
        spans.extend(self._trace_spans(limit=max(0, limit - len(spans))))
        return spans[:limit]

    def _event_span(self, event: dict[str, Any]) -> dict[str, Any]:
        payload = event.get("payload") or {}
        event_id = str(event.get("event_id") or self._stable_id(event))
        trace_ids = [str(item) for item in event.get("trace_ids", []) if item]
        event_type = str(event.get("event_type") or "unknown")
        subject = str(event.get("subject") or "unknown")
        return {
            "trace_id": trace_ids[0] if trace_ids else f"trace_{event_id}",
            "span_id": f"span_{event_id}",
            "parent_span_id": None,
            "span_kind": self._span_kind(event_type),
            "subject": subject,
            "started_at": event.get("created_at"),
            "ended_at": event.get("created_at"),
            "status": self._status(event_type, payload),
            "model_or_tool": payload.get("model")
            or payload.get("tool")
            or payload.get("provider_id")
            or payload.get("extension_id")
            or payload.get("runtime_name"),
            "workflow_execution_id": payload.get("execution_id") or payload.get("workflow_execution_id"),
            "policy_decision": payload.get("policy_decision")
            or payload.get("decision")
            or ("deny" if payload.get("execution_allowed") is False else "metadata_only"),
            "approval_decision": payload.get("approval_decision")
            or payload.get("approval")
            or ("not_requested" if payload.get("execution_allowed") is False else None),
            "redaction_state": payload.get("redaction_state") or "metadata_only",
            "token_usage": payload.get("token_usage") or {"prompt": 0, "completion": 0, "total": 0},
            "cost_estimate": payload.get("cost_estimate") or {"amount": 0.0, "currency": "USD", "state": "not_metered"},
            "linked_artifact_ids": self._linked_artifacts(event, payload),
        }

    def _trace_spans(self, *, limit: int) -> list[dict[str, Any]]:
        if limit <= 0 or self.store is None:
            return []
        try:
            traces = self.store.list_traces(limit=limit)
        except Exception:
            return []
        spans = []
        for trace in traces:
            trace_id = str(trace.get("trace_id") or self._stable_id(trace))
            spans.append(
                {
                    "trace_id": trace_id,
                    "span_id": f"span_{trace_id}",
                    "parent_span_id": None,
                    "span_kind": "model_call",
                    "subject": str(trace.get("session_id") or trace.get("prompt") or "model-call"),
                    "started_at": trace.get("created_at"),
                    "ended_at": trace.get("created_at"),
                    "status": "recorded",
                    "model_or_tool": trace.get("model_id") or trace.get("runtime") or trace.get("model"),
                    "workflow_execution_id": None,
                    "policy_decision": "recorded",
                    "approval_decision": "not_required",
                    "redaction_state": "source_trace",
                    "token_usage": trace.get("token_usage") or {"prompt": 0, "completion": 0, "total": 0},
                    "cost_estimate": trace.get("cost_estimate") or {"amount": 0.0, "currency": "USD", "state": "not_metered"},
                    "linked_artifact_ids": [],
                }
            )
        return spans

    def _span_kind(self, event_type: str) -> str:
        for prefix, kind in self.EVENT_KIND_PREFIXES.items():
            if event_type.startswith(prefix):
                return kind
        return event_type.split(".", 1)[0] if "." in event_type else "event"

    def _status(self, event_type: str, payload: dict[str, Any]) -> str:
        if "denied" in event_type or payload.get("decision") == "deny":
            return "denied"
        if payload.get("execution_allowed") is False:
            return "metadata_only"
        return str(payload.get("status") or payload.get("state") or "recorded")

    def _linked_artifacts(self, event: dict[str, Any], payload: dict[str, Any]) -> list[str]:
        artifacts = []
        for key in ("artifact_path", "artifact_id", "report_id"):
            if event.get(key):
                artifacts.append(str(event[key]))
            if payload.get(key):
                artifacts.append(str(payload[key]))
        for key in ("artifacts", "linked_artifact_ids"):
            for item in payload.get(key, []) or []:
                artifacts.append(str(item))
        return sorted(set(artifacts))

    def _trace_health(self, spans: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "status": "ok" if spans else "no_spans",
            "normalizer": "nexusnet-metadata-v1",
            "otel_genai_shape": True,
            "openinference_shape": True,
        }

    def _counts(self, items: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = str(item.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _stable_id(self, payload: dict[str, Any]) -> str:
        digest = hashlib.sha256(repr(sorted(payload.items())).encode("utf-8")).hexdigest()[:12]
        return digest
