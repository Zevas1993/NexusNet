from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.browser.context_memory import BrowserContextIngestRequest, BrowserContextMemory
from tests.test_nexus_phase1_foundation import make_project


def test_browser_context_memory_indexes_operator_provided_tabs_and_queries_locally():
    memory = BrowserContextMemory()

    record = memory.ingest(
        BrowserContextIngestRequest(
            context_id="tab::gemma-browser-assistant",
            context_type="tab",
            title="Gemma browser assistant",
            url="https://example.local/gemma-browser",
            text="A local browser assistant can search open tabs, explain the current page, and find browser history without sending private data to cloud services.",
            local_only=True,
            contains_private_data=False,
            source_permission="operator_provided",
            provenance_ref="youtube-transcript::jB3yKR6bOjQ",
            tags=["browser-agent", "edge-ai", "privacy"],
        )
    )

    assert record["status_label"] == "LOCKED CANON"
    assert record["authority"] == "NexusBrain"
    assert record["status"] == "indexed"
    assert record["privacy_boundary"] == "local-context-index"
    assert record["policy_scan"]["summary"]["allow_merge"] is True

    query = memory.query(
        {
            "query_id": "query::browser-history",
            "question": "Which page mentions searching open tabs and browser history locally?",
            "limit": 3,
        }
    )

    assert query["query_id"] == "query::browser-history"
    assert query["result_count"] == 1
    assert query["top_results"][0]["context_id"] == "tab::gemma-browser-assistant"
    assert "Gemma browser assistant" in query["answer_summary"]
    assert query["operator_actions"]["ingest"]["endpoint"] == "/ops/brain/browser-context/ingest"


def test_browser_context_memory_blocks_private_history_without_permission_or_local_only_boundary():
    memory = BrowserContextMemory()

    record = memory.ingest(
        {
            "context_id": "history::raw-private",
            "context_type": "history",
            "title": "Raw private history",
            "url": "",
            "text": "private browsing history with no explicit permission",
            "local_only": False,
            "contains_private_data": True,
            "source_permission": "unknown",
            "provenance_ref": "",
        }
    )

    assert record["status"] == "blocked"
    assert {
        "browser_context_requires_operator_permission",
        "private_browser_context_requires_local_only",
    }.issubset({finding["rule_id"] for finding in record["privacy_findings"]})
    assert record["policy_scan"]["summary"]["allow_merge"] is False

    summary = memory.scorecard()
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1
    assert summary["latest_context"]["status"] == "blocked"


def test_browser_context_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/browser-context/ingest",
        json={
            "context_id": "page::agentic-pipeline",
            "context_type": "page",
            "title": "Agentic pipeline notes",
            "url": "https://example.local/agentic-pipelines",
            "text": "Agentic pipelines use fresh subprocesses, manifests, block artifacts, events, and deterministic gate checks.",
            "local_only": True,
            "contains_private_data": False,
            "source_permission": "operator_provided",
            "provenance_ref": "youtube-transcript::9YYUzA5ZnDo",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "indexed"

    query = client.post(
        "/ops/brain/browser-context/query",
        json={
            "query_id": "query::pipelines",
            "question": "What page mentioned manifests and gate checks?",
            "limit": 5,
        },
    )
    assert query.status_code == 200
    assert query.json()["top_results"][0]["context_id"] == "page::agentic-pipeline"

    summary = client.get("/ops/brain/browser-context")
    assert summary.status_code == 200
    assert summary.json()["context_count"] == 1

    scorecard = client.get("/ops/brain/canon/browser-context")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert "local_only_browser_context" in scorecard_payload["required_controls"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "browser-context-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["browser_context_scorecard"]["context_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "browser-context-cockpit"}).json()
    assert blackbox["scorecard_refs"]["browser_context"] == "/ops/brain/canon/browser-context"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Browser Context Memory" in ui.text
    assert "browserContextScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderBrowserContextScorecard" in app_js
    assert "/ops/brain/canon/browser-context" in app_js
