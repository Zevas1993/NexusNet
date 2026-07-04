from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.telemetry.genai_observability import GenAITraceEventRequest, GenAITraceRegistry
from tests.test_nexus_phase1_foundation import make_project


def test_genai_trace_registry_maps_chat_trace_to_opentelemetry_attributes_with_redaction():
    registry = GenAITraceRegistry()

    trace = registry.record(
        GenAITraceEventRequest(
            trace_id="trace::chat-redacted",
            session_id="observability-session",
            operation_name="chat",
            provider_name="openai",
            request_model="gpt-5.5",
            response_model="gpt-5.5",
            actor="NexusBrain",
            target_surface="neural-core",
            input_contains_private_data=True,
            output_contains_private_data=True,
            token_usage={"input": 2048, "output": 512},
            latency_ms=820,
            evidence_refs=["/ops/brain/operations"],
        )
    )

    assert trace["status_label"] == "LOCKED CANON"
    assert trace["authority"] == "NexusBrain"
    assert trace["status"] == "recorded"
    assert trace["redaction_state"] == "redacted"
    assert trace["span_name"] == "chat gpt-5.5"
    assert trace["span_kind"] == "CLIENT"
    assert trace["otel_attributes"]["gen_ai.operation.name"] == "chat"
    assert trace["otel_attributes"]["gen_ai.provider.name"] == "openai"
    assert trace["otel_attributes"]["gen_ai.conversation.id"] == "observability-session"
    assert trace["otel_attributes"]["gen_ai.request.model"] == "gpt-5.5"
    assert trace["otel_attributes"]["gen_ai.response.model"] == "gpt-5.5"
    assert trace["content_capture_policy"] == "redacted-private-content"
    assert trace["policy_scan"]["summary"]["allow_merge"] is True


def test_genai_trace_registry_maps_tool_and_retrieval_spans_without_private_content():
    registry = GenAITraceRegistry()

    tool_trace = registry.record(
        {
            "trace_id": "trace::tool",
            "session_id": "tool-session",
            "operation_name": "execute_tool",
            "provider_name": "nexusnet.local",
            "request_model": "",
            "tool_name": "artifact_trust_scan",
            "target_surface": "artifact-trust-registry",
            "evidence_refs": ["/ops/brain/artifact-trust"],
        }
    )
    retrieval_trace = registry.record(
        {
            "trace_id": "trace::retrieval",
            "session_id": "tool-session",
            "operation_name": "retrieval",
            "provider_name": "nexusnet.local",
            "data_source_id": "memory-plane::project",
            "target_surface": "context-memory",
            "evidence_refs": ["/ops/brain/canon/memory-provenance"],
        }
    )

    assert tool_trace["span_name"] == "execute_tool artifact_trust_scan"
    assert tool_trace["otel_attributes"]["gen_ai.tool.name"] == "artifact_trust_scan"
    assert retrieval_trace["span_name"] == "retrieval memory-plane::project"
    assert retrieval_trace["otel_attributes"]["gen_ai.data_source.id"] == "memory-plane::project"
    assert registry.summary()["trace_count"] == 2


def test_genai_trace_registry_blocks_invalid_tool_trace_and_degrades_summary():
    registry = GenAITraceRegistry()

    trace = registry.record(
        {
            "trace_id": "trace::blocked-tool",
            "session_id": "blocked-tool-session",
            "operation_name": "execute_tool",
            "provider_name": "nexusnet.local",
            "tool_name": "",
            "target_surface": "artifact-trust-registry",
        }
    )

    assert trace["status"] == "blocked"
    assert "genai_execute_tool_requires_tool_name" in {finding["rule_id"] for finding in trace["trace_findings"]}

    summary = registry.scorecard()
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1
    assert summary["latest_trace"]["status"] == "blocked"


def test_genai_observability_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/genai-observability/traces",
        json={
            "trace_id": "trace::api-agent",
            "session_id": "genai-observability-cockpit",
            "operation_name": "invoke_agent",
            "provider_name": "nexusnet.local",
            "request_model": "NexusBrain",
            "response_model": "NexusBrain",
            "actor": "AO Hive",
            "target_surface": "agentic-pipelines",
            "input_contains_private_data": False,
            "output_contains_private_data": False,
            "token_usage": {"input": 640, "output": 220},
            "latency_ms": 410,
            "evidence_refs": ["/ops/brain/agentic-pipelines"],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "recorded"

    summary = client.get("/ops/brain/genai-observability")
    assert summary.status_code == 200
    assert summary.json()["trace_count"] == 1

    scorecard = client.get("/ops/brain/canon/genai-observability")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["record_trace"]["endpoint"] == "/ops/brain/genai-observability/traces"
    assert scorecard_payload["operator_actions"]["trace_schema"]["endpoint"] == "/ops/brain/trace-schema"
    assert (
        scorecard_payload["operator_actions"]["otel_projection"]["endpoint"]
        == "/ops/brain/trace-schema/otel-projection/{trace_id}"
    )
    assert "otel_semconv_stability_opt_in" in scorecard_payload["required_controls"]

    schema = client.get("/ops/brain/trace-schema")
    assert schema.status_code == 200
    schema_payload = schema.json()
    assert schema_payload["schema_id"] == "nexusnet-genai-trace-schema"
    assert "gen_ai.operation.name" in schema_payload["required_otel_attributes"]
    assert "OpenTelemetry-GenAI" in schema_payload["standard_mappings"]

    projection = client.get("/ops/brain/trace-schema/otel-projection/trace::api-agent")
    assert projection.status_code == 200
    projection_payload = projection.json()
    assert projection_payload["trace_id"] == "trace::api-agent"
    assert projection_payload["export_format"] == "opentelemetry-genai-span"
    assert projection_payload["span"]["name"] == "invoke_agent NexusBrain"
    assert projection_payload["span"]["attributes"]["gen_ai.operation.name"] == "invoke_agent"
    assert projection_payload["content_capture_policy"] == "metadata-only-no-raw-content"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "genai-observability-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["genai_observability_scorecard"]["trace_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "genai-observability-cockpit"}).json()
    assert blackbox["scorecard_refs"]["genai_observability"] == "/ops/brain/canon/genai-observability"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "GenAI Observability" in ui.text
    assert "genAIObservabilityScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderGenAIObservabilityScorecard" in app_js
    assert "/ops/brain/canon/genai-observability" in app_js
