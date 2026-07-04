from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.memory import EngramLookupRequest, EngramRecordRequest, NexusEngramIndex
from tests.test_nexus_phase1_foundation import make_project


def test_engram_index_uses_multi_head_ngram_hashes_and_context_gate(tmp_path):
    index = NexusEngramIndex(artifacts_dir=tmp_path, table_size=101, head_count=4, ngram_orders=(1, 2, 3))

    record = index.store(
        EngramRecordRequest(
            record_id="entity::diana-princess-of-wales",
            text="Diana Princess of Wales",
            fact="Diana, Princess of Wales, was a British royal and humanitarian figure.",
            source_ref="docs/test-engram.md#diana",
            tags=["royal", "humanitarian", "person"],
            sensitivity="public",
        )
    )

    assert record["record_id"] == "entity::diana-princess-of-wales"
    assert record["hashes"]
    assert all(item["head"] in {0, 1, 2, 3} for item in record["hashes"])

    lookup = index.lookup(
        EngramLookupRequest(
            text="Who was Diana Princess of Wales?",
            context_terms=["royal", "humanitarian"],
            top_k=3,
        )
    )

    assert lookup["query"]["text"] == "Who was Diana Princess of Wales?"
    assert lookup["results"][0]["record_id"] == "entity::diana-princess-of-wales"
    assert lookup["results"][0]["gate_score"] > 0.5
    assert lookup["results"][0]["ngram_hit_count"] >= 2
    assert lookup["results"][0]["collision_count"] == 0
    assert lookup["memory_boundary"] == "explicit-memory-sidecar-not-hidden-weight-authority"


def test_engram_index_surfaces_collision_pressure_and_sensitive_lookup_gate(tmp_path):
    index = NexusEngramIndex(artifacts_dir=tmp_path, table_size=2, head_count=2, ngram_orders=(1, 2))
    index.store({"record_id": "entity::harry-potter", "text": "Harry Potter", "fact": "Young wizard", "tags": ["wizard"], "source_ref": "test"})
    index.store(
        {
            "record_id": "entity::private-project",
            "text": "Project Caldera",
            "fact": "Confidential project detail",
            "tags": ["project"],
            "source_ref": "test",
            "sensitivity": "confidential",
        }
    )

    summary = index.summary()
    assert summary["collision_slot_count"] >= 1
    assert "multi_head_hash_collision_budget" in summary["required_controls"]

    redacted = index.lookup({"text": "Project Caldera", "context_terms": ["project"], "include_sensitive": False})
    assert redacted["runtime_state"] == "degraded"
    assert redacted["results"] == []
    assert "sensitive_records_excluded" in redacted["findings"]

    included = index.lookup({"text": "Project Caldera", "context_terms": ["project"], "include_sensitive": True})
    assert included["runtime_state"] == "live-bound"
    assert included["results"][0]["record_id"] == "entity::private-project"


def test_engram_memory_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    record = client.post(
        "/ops/brain/memory/engram/records",
        json={
            "record_id": "phrase::by-the-way",
            "text": "By the way",
            "fact": "Fixed discourse phrase that often signals a side note.",
            "source_ref": "docs/test-engram.md#phrase",
            "tags": ["fixed_phrase", "discourse"],
            "sensitivity": "public",
        },
    )
    assert record.status_code == 200

    lookup = client.post(
        "/ops/brain/memory/engram/lookup",
        json={"text": "By the way, what changed?", "context_terms": ["fixed_phrase"], "top_k": 2},
    )
    assert lookup.status_code == 200
    assert lookup.json()["results"][0]["record_id"] == "phrase::by-the-way"

    scorecard = client.get("/ops/brain/canon/engram-memory")
    assert scorecard.status_code == 200
    assert scorecard.json()["operator_actions"]["lookup"]["endpoint"] == "/ops/brain/memory/engram/lookup"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "engram-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["engram_memory_scorecard"]["surface_id"] == "engram-memory-index"

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "engram-cockpit"}).json()
    assert blackbox["scorecard_refs"]["engram_memory"] == "/ops/brain/canon/engram-memory"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Engram Memory Index" in ui.text
    assert "engramMemoryScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderEngramMemoryScorecard" in app_js
    assert "/ops/brain/canon/engram-memory" in app_js
