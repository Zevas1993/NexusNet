from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.research.forward_radar import ForwardRadarRegistry
from nexusnet.research.monitor import ResearchMonitor
from tests.test_nexus_phase1_foundation import make_project


def test_research_monitor_polls_http_deduplicates_and_intakes_changed_content(tmp_path: Path):
    state = {"etag": '"v1"', "body": b"<html><title>KV Cache v1</title><body>first release</body></html>"}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.headers.get("If-None-Match") == state["etag"]:
                self.send_response(304)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("ETag", state["etag"])
            self.end_headers()
            self.wfile.write(state["body"])

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        radar = ForwardRadarRegistry(artifacts_dir=tmp_path)
        monitor = ResearchMonitor(
            artifacts_dir=tmp_path,
            radar=radar,
            allow_private_network=True,
        )
        source = monitor.add_source(
            source_id="kv-cache-releases",
            url=f"http://127.0.0.1:{server.server_port}/releases",
            interval_seconds=60,
        )

        first = monitor.poll(source["source_id"])
        second = monitor.poll(source["source_id"])
        state["etag"] = '"v2"'
        state["body"] = b"<html><title>KV Cache v2</title><body>second release</body></html>"
        third = monitor.poll(source["source_id"])
    finally:
        server.shutdown()
        thread.join(timeout=5)

    assert first["state"] == "changed"
    assert second["state"] == "not_modified"
    assert third["state"] == "changed"
    assert first["content_digest"] != third["content_digest"]
    assert radar.summary()["candidate_count"] == 2
    assert monitor.summary()["changed_count"] == 2


def test_research_monitor_rejects_private_network_sources_by_default(tmp_path: Path):
    monitor = ResearchMonitor(
        artifacts_dir=tmp_path,
        radar=ForwardRadarRegistry(artifacts_dir=tmp_path),
    )

    try:
        monitor.add_source(source_id="local", url="http://127.0.0.1/private", interval_seconds=60)
    except ValueError as exc:
        assert "private network" in str(exc)
    else:
        raise AssertionError("private network source was accepted")


def test_research_monitor_api_registers_public_source_and_reports_it(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    added = client.post(
        "/ops/brain/research-monitors/sources",
        json={"source_id": "public-source", "url": "https://8.8.8.8/research", "interval_seconds": 3600},
    )

    assert added.status_code == 200
    summary = client.get("/ops/brain/research-monitors")
    assert summary.status_code == 200
    assert summary.json()["source_count"] == 1


def test_research_monitor_polls_only_due_sources_and_detects_cross_source_trend(tmp_path: Path):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            body = f"<html><title>{self.path}</title><body>KV cache compression</body></html>".encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        monitor = ResearchMonitor(
            artifacts_dir=tmp_path,
            radar=ForwardRadarRegistry(artifacts_dir=tmp_path),
            allow_private_network=True,
        )
        base = f"http://127.0.0.1:{server.server_port}"
        monitor.add_source(source_id="source-a", url=f"{base}/a", interval_seconds=3600, topics=["kv-cache-compression"])
        monitor.add_source(source_id="source-b", url=f"{base}/b", interval_seconds=3600, topics=["kv-cache-compression"])
        monitor.poll("source-a")

        due = monitor.poll_due()
    finally:
        server.shutdown()
        thread.join(timeout=5)

    assert due["polled_count"] == 1
    assert due["skipped_not_due_count"] == 1
    assert due["results"][0]["source_id"] == "source-b"
    trends = monitor.summary()["strong_trends"]
    assert trends == [{"topic": "kv-cache-compression", "source_count": 2, "source_ids": ["source-a", "source-b"]}]
