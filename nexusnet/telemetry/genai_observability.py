from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


GenAIOperationName = Literal[
    "chat",
    "create_agent",
    "embeddings",
    "execute_tool",
    "generate_content",
    "invoke_agent",
    "retrieval",
    "text_completion",
]


class GenAITraceEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    session_id: str
    operation_name: GenAIOperationName
    provider_name: str
    request_model: str = ""
    response_model: str = ""
    actor: str = "NexusBrain"
    target_surface: str = ""
    span_kind: Literal["CLIENT", "INTERNAL"] = "CLIENT"
    tool_name: str = ""
    data_source_id: str = ""
    input_contains_private_data: bool = False
    output_contains_private_data: bool = False
    token_usage: dict[str, int] = Field(default_factory=dict)
    latency_ms: int = 0
    error_type: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenAITraceRegistry:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.traces_dir = self.artifacts_dir / "telemetry" / "genai-observability" if self.artifacts_dir else None
        if self.traces_dir is not None:
            self.traces_dir.mkdir(parents=True, exist_ok=True)
        self._memory_traces: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def record(self, request: GenAITraceEventRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, GenAITraceEventRequest) else GenAITraceEventRequest.model_validate(request)
        trace_findings = _trace_findings(normalized)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = bool(trace_findings) or policy_scan.summary.active_hard_fail_count > 0
        trace = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "genai-observability",
            "trace_id": normalized.trace_id,
            "session_id": normalized.session_id,
            "actor": normalized.actor,
            "target_surface": normalized.target_surface,
            "status": "blocked" if blocked else "recorded",
            "created_at": utcnow().isoformat(),
            "span_name": _span_name(normalized),
            "span_kind": normalized.span_kind,
            "otel_attributes": _otel_attributes(normalized),
            "token_usage": normalized.token_usage,
            "latency_ms": normalized.latency_ms,
            "redaction_state": _redaction_state(normalized),
            "content_capture_policy": _content_capture_policy(normalized),
            "evidence_refs": normalized.evidence_refs,
            "trace_findings": trace_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "metadata": normalized.metadata,
        }
        self._persist(trace)
        return trace

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        traces = self._list_traces(limit=limit)
        latest = traces[0] if traces else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if latest.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "genai-observability",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "trace_count": len(traces),
            "redacted_count": sum(1 for trace in traces if trace.get("redaction_state") == "redacted"),
            "blocked_count": sum(1 for trace in traces if trace.get("status") == "blocked"),
            "latest_trace": latest,
            "traces": traces,
            "otel_semconv_status": "development",
            "stability_opt_in": "OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental",
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/",
                "https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
            ],
            "export_boundary": "redact-private-content-and-export-evidence-linked-span-metadata",
            "standard_mappings": ["OpenTelemetry-GenAI", "OpenInference", "NexusNet-command-timeline"],
        }

    def trace_schema(self) -> dict[str, Any]:
        return {
            "status_label": "LOCKED CANON",
            "schema_id": "nexusnet-genai-trace-schema",
            "authority": "NexusBrain",
            "source_documents": [
                "https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/",
                "https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
            ],
            "standard_mappings": ["OpenTelemetry-GenAI", "OpenInference", "NexusNet-command-timeline"],
            "required_otel_attributes": [
                "gen_ai.operation.name",
                "gen_ai.provider.name",
                "gen_ai.conversation.id",
            ],
            "conditional_otel_attributes": [
                "gen_ai.request.model",
                "gen_ai.response.model",
                "gen_ai.tool.name",
                "gen_ai.data_source.id",
                "error.type",
                "nexusnet.surface.id",
                "nexusnet.operation.latency_ms",
            ],
            "privacy_boundary": "raw-input-output-content-is-not-exported-when-private-redaction-is-required",
            "operator_actions": _operator_actions(),
        }

    def otel_projection(self, trace_id: str) -> dict[str, Any] | None:
        trace = self.get_trace(trace_id)
        if trace is None:
            return None
        attributes = trace.get("otel_attributes", {})
        return {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "trace_id": trace.get("trace_id"),
            "session_id": trace.get("session_id"),
            "export_format": "opentelemetry-genai-span",
            "standard_mapping": "OpenTelemetry-GenAI",
            "redaction_state": trace.get("redaction_state"),
            "content_capture_policy": trace.get("content_capture_policy"),
            "span": {
                "name": trace.get("span_name"),
                "kind": trace.get("span_kind"),
                "attributes": attributes,
                "status": {"code": "ERROR" if attributes.get("error.type") else "OK"},
            },
            "token_usage": trace.get("token_usage", {}),
            "evidence_refs": trace.get("evidence_refs", []),
            "source_trace": trace,
        }

    def get_trace(self, trace_id: str) -> dict[str, Any] | None:
        for trace in self._list_traces(limit=500):
            if trace.get("trace_id") == trace_id:
                return trace
        return None

    def _persist(self, trace: dict[str, Any]) -> None:
        self._memory_traces.insert(0, trace)
        self._memory_traces = self._memory_traces[:50]
        if self.traces_dir is not None:
            safe_id = trace["trace_id"].replace(":", "_").replace("/", "_")
            path = self.traces_dir / f"{safe_id}.json"
            trace["artifact_path"] = str(path)
            path.write_text(json.dumps(trace, indent=2), encoding="utf-8")

    def _list_traces(self, *, limit: int) -> list[dict[str, Any]]:
        traces = list(self._memory_traces)
        seen = {trace.get("trace_id") for trace in traces}
        if self.traces_dir is not None:
            for path in self.traces_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("trace_id") not in seen:
                    traces.append(payload)
        traces.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return traces[:limit]


def _trace_findings(request: GenAITraceEventRequest) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not request.provider_name.strip():
        findings.append(
            {
                "rule_id": "genai_trace_requires_provider_name",
                "severity": "hard_fail",
                "message": "OpenTelemetry GenAI traces require gen_ai.provider.name.",
            }
        )
    if request.operation_name not in {"execute_tool", "retrieval"} and not request.request_model.strip():
        findings.append(
            {
                "rule_id": "genai_trace_requires_request_model",
                "severity": "warning",
                "message": "Inference traces should carry gen_ai.request.model when available.",
            }
        )
    if request.operation_name == "execute_tool" and not request.tool_name.strip():
        findings.append(
            {
                "rule_id": "genai_execute_tool_requires_tool_name",
                "severity": "hard_fail",
                "message": "Execute-tool spans require a tool name.",
            }
        )
    if request.operation_name == "retrieval" and not request.data_source_id.strip():
        findings.append(
            {
                "rule_id": "genai_retrieval_requires_data_source",
                "severity": "hard_fail",
                "message": "Retrieval spans require a data source identifier.",
            }
        )
    return findings


def _otel_attributes(request: GenAITraceEventRequest) -> dict[str, Any]:
    attributes: dict[str, Any] = {
        "gen_ai.operation.name": request.operation_name,
        "gen_ai.provider.name": request.provider_name,
        "gen_ai.conversation.id": request.session_id,
    }
    if request.request_model:
        attributes["gen_ai.request.model"] = request.request_model
    if request.response_model:
        attributes["gen_ai.response.model"] = request.response_model
    if request.tool_name:
        attributes["gen_ai.tool.name"] = request.tool_name
    if request.data_source_id:
        attributes["gen_ai.data_source.id"] = request.data_source_id
    if request.error_type:
        attributes["error.type"] = request.error_type
    if request.latency_ms:
        attributes["nexusnet.operation.latency_ms"] = request.latency_ms
    if request.target_surface:
        attributes["nexusnet.surface.id"] = request.target_surface
    return attributes


def _span_name(request: GenAITraceEventRequest) -> str:
    if request.operation_name == "execute_tool":
        return f"execute_tool {request.tool_name or 'unknown-tool'}"
    if request.operation_name == "retrieval":
        return f"retrieval {request.data_source_id or 'unknown-source'}"
    return f"{request.operation_name} {request.request_model or request.provider_name}"


def _redaction_state(request: GenAITraceEventRequest) -> str:
    return "redacted" if request.input_contains_private_data or request.output_contains_private_data else "not-required"


def _content_capture_policy(request: GenAITraceEventRequest) -> str:
    if request.input_contains_private_data or request.output_contains_private_data:
        return "redacted-private-content"
    return "metadata-only-no-raw-content"


def _policy_targets(request: GenAITraceEventRequest) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"telemetry-export::{request.trace_id}",
            "target_type": "tool_execution",
            "metadata": {
                "write_enabled": False,
                "sandboxed": True,
                "tool_scope": "telemetry-export",
            },
        }
    ]


def _required_controls() -> list[str]:
    return [
        "gen_ai_operation_name",
        "gen_ai_provider_name",
        "gen_ai_conversation_id",
        "execute_tool_span",
        "retrieval_span",
        "redaction_export_boundary",
        "otel_semconv_stability_opt_in",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/genai-observability"},
        "record_trace": {"method": "POST", "endpoint": "/ops/brain/genai-observability/traces"},
        "trace_schema": {"method": "GET", "endpoint": "/ops/brain/trace-schema"},
        "otel_projection": {"method": "GET", "endpoint": "/ops/brain/trace-schema/otel-projection/{trace_id}"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/genai-observability"},
    }
