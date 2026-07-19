from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.curriculum.dataset_radar import DATASET_SOURCE_STATES, DatasetRadar
from tests.test_nexus_phase1_foundation import make_project


def test_dataset_radar_seed_registry_is_broad_freshness_and_license_gated():
    radar = DatasetRadar()

    scorecard = radar.scorecard()
    sources = radar.list_sources()
    by_id = {source["dataset_id"]: source for source in sources}

    assert scorecard["surface_id"] == "living-dataset-radar"
    assert scorecard["source_count"] >= 80
    assert scorecard["freshness_summary"]["source_count"] == scorecard["source_count"]
    assert "refresh_due_count" in scorecard["freshness_summary"]
    assert "refresh_due_sources" in scorecard
    assert "refresh_run_freshness" in scorecard
    assert "refresh_warning_count" in scorecard
    assert set(DATASET_SOURCE_STATES).issubset(set(scorecard["state_catalog"]))
    assert {
        "fineweb",
        "fineweb-edu",
        "fineweb-2",
        "dclm",
        "the-stack-v2",
        "stack-edu",
        "codesearchnet",
        "context7",
        "swe-bench",
        "swe-gym",
        "openmathreasoning",
        "agenttrove",
        "common-voice",
        "books1",
        "books2",
    }.issubset(by_id)

    for source in sources:
        assert source["source_url"]
        assert source["license_state"] in DATASET_SOURCE_STATES
        assert source["provenance_state"]
        assert source["freshness"]["last_checked"]
        assert source["freshness"]["tracking"] in {"last_modified", "release_page", "bulk_snapshot", "manual_review"}
        assert source["allowed_uses"] is not None
        assert source["target_nodes"]
        assert source["student_targets"]
        assert source["quality_signals"] is not None


def test_dataset_radar_summary_surfaces_stale_source_refresh_due_counts(tmp_path):
    today = datetime.now(timezone.utc).date()
    fresh_last_checked = today.isoformat()
    stale_last_checked = (today - timedelta(days=30)).isoformat()
    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text(
        """
schema_version: dataset_radar_registry.v0.1
sources:
  - dataset_id: fresh-code
    label: Fresh Code
    source_family: code_agent
    source_url: https://example.test/fresh-code
    license_state: approved_train
    provenance_state: source_card_available
    allowed_uses: [teacher_context, train, validation]
    student_targets: [coder]
    target_nodes: [Coder Expert]
    quality_signals: [test]
    freshness: {tracking: last_modified, last_checked: "__FRESH_LAST_CHECKED__", cadence: monthly}
    blocked_reason: ""
    privacy_risk: low
  - dataset_id: stale-code
    label: Stale Code
    source_family: code_agent
    source_url: https://example.test/stale-code
    license_state: approved_teacher_context
    provenance_state: source_card_available
    allowed_uses: [teacher_context]
    student_targets: [coder]
    target_nodes: [Coder Expert]
    quality_signals: [test]
    freshness: {tracking: release_page, last_checked: "__STALE_LAST_CHECKED__", cadence: weekly}
    blocked_reason: ""
    privacy_risk: low
""".strip()
        .replace("__FRESH_LAST_CHECKED__", fresh_last_checked)
        .replace("__STALE_LAST_CHECKED__", stale_last_checked),
        encoding="utf-8",
    )
    radar = DatasetRadar(artifacts_dir=tmp_path, registry_path=registry_path)

    summary = radar.summary()

    assert summary["freshness_summary"]["source_count"] == 2
    assert summary["freshness_summary"]["refresh_due_count"] == 1
    assert summary["freshness_summary"]["stale_count"] == 1
    assert summary["freshness_summary"]["current_count"] == 1
    assert summary["refresh_due_sources"][0]["dataset_id"] == "stale-code"
    assert summary["refresh_due_sources"][0]["freshness_status"] == "stale"
    assert summary["refresh_due_sources"][0]["days_overdue"] > 0
    assert summary["refresh_run_freshness"]["refresh_due"] is True
    assert summary["refresh_recommendations"][0]["source_family"] == "code_agent"
    assert summary["refresh_recommendations"][0]["due_source_ids"] == ["stale-code"]
    assert summary["refresh_recommendations"][0]["endpoint"] == "/ops/brain/dataset-radar/refresh-batch"
    assert summary["refresh_recommendations"][0]["refresh_payload"]["preset_ids"] == ["coder-expert"]
    assert summary["refresh_recommendations"][0]["refresh_payload"]["source_families"] == ["code_agent"]
    assert summary["refresh_warning_count"] >= 2


def test_dataset_radar_hf_discovery_never_auto_approves_live_candidates(tmp_path):
    radar = DatasetRadar(artifacts_dir=tmp_path)

    refresh = radar.refresh(
        {
            "query": "agent traces",
            "sort": "trendingScore",
            "hf_results": [
                {
                    "id": "lambda/hermes-agent-reasoning-traces",
                    "downloads": 4921,
                    "lastModified": "2026-05-04T12:00:00Z",
                    "trendingScore": 37.5,
                    "tags": ["license:apache-2.0", "agent", "tool-use"],
                    "author": "lambda",
                },
                {
                    "id": "unknown/private-chat-dump",
                    "downloads": 10,
                    "lastModified": "2026-05-04T12:00:00Z",
                    "tags": ["chat", "personal"],
                    "author": "unknown",
                },
            ],
        }
    )

    assert refresh["discovery_source"] == "huggingface"
    assert refresh["candidate_count"] == 2
    candidates = {candidate["dataset_id"]: candidate for candidate in refresh["candidates"]}
    hermes = candidates["lambda/hermes-agent-reasoning-traces"]
    assert hermes["license_state"] == "pending_provenance_review"
    assert hermes["auto_approved"] is False
    assert hermes["quality_signals"]["trendingScore"] == 37.5
    assert candidates["unknown/private-chat-dump"]["license_state"] == "blocked_private_or_personal"


def test_dataset_radar_refresh_can_use_live_hf_fetcher_without_training_approval(tmp_path, monkeypatch):
    radar = DatasetRadar(artifacts_dir=tmp_path)
    captured = {}

    def fake_fetch(*, query: str, sort: str, limit: int):
        captured.update({"query": query, "sort": sort, "limit": limit})
        return [
            {
                "id": "example/live-hf-code-agent",
                "downloads": 777,
                "lastModified": "2026-05-05T18:00:00Z",
                "trendingScore": 22.0,
                "tags": ["license:apache-2.0", "code", "agent"],
                "author": "example",
            }
        ]

    monkeypatch.setattr(radar, "_fetch_huggingface_results", fake_fetch)
    refresh = radar.refresh(
        {
            "query": "open code agent dataset",
            "sort": "trendingScore",
            "limit": 7,
        }
    )

    assert captured == {"query": "open code agent dataset", "sort": "trendingScore", "limit": 7}
    assert refresh["discovery_fetch_mode"] == "live_huggingface_api"
    assert refresh["candidate_count"] == 1
    candidate = refresh["candidates"][0]
    assert candidate["dataset_id"] == "example/live-hf-code-agent"
    assert candidate["auto_approved"] is False
    assert candidate["license_state"] == "pending_provenance_review"


def test_dataset_radar_refresh_filters_candidates_by_tags_author_and_source_family_without_approval(tmp_path):
    radar = DatasetRadar(artifacts_dir=tmp_path)

    refresh = radar.refresh(
        {
            "query": "open code agent dataset",
            "required_tags": ["code"],
            "blocked_tags": ["private"],
            "authors": ["example"],
            "source_families": ["code_agent"],
            "hf_results": [
                {
                    "id": "example/code-agent-set",
                    "downloads": 800,
                    "lastModified": "2026-05-05T18:00:00Z",
                    "trendingScore": 33.0,
                    "tags": ["license:apache-2.0", "code", "agent"],
                    "author": "example",
                },
                {
                    "id": "other/code-agent-set",
                    "downloads": 900,
                    "lastModified": "2026-05-05T18:00:00Z",
                    "trendingScore": 34.0,
                    "tags": ["license:apache-2.0", "code", "agent"],
                    "author": "other",
                },
                {
                    "id": "example/private-code-dump",
                    "downloads": 1000,
                    "lastModified": "2026-05-05T18:00:00Z",
                    "trendingScore": 99.0,
                    "tags": ["license:apache-2.0", "code", "private"],
                    "author": "example",
                },
            ],
        }
    )

    assert refresh["raw_candidate_count"] == 3
    assert refresh["candidate_count"] == 1
    assert refresh["filtered_out_count"] == 2
    assert refresh["discovery_filters"]["required_tags"] == ["code"]
    assert refresh["discovery_filters"]["authors"] == ["example"]
    assert refresh["discovery_filters"]["source_families"] == ["code_agent"]
    assert refresh["candidates"][0]["dataset_id"] == "example/code-agent-set"
    assert refresh["candidates"][0]["auto_approved"] is False


def test_dataset_radar_infers_specialized_source_families_for_operator_filters(tmp_path):
    radar = DatasetRadar(artifacts_dir=tmp_path)

    cases = [
        ("science_research", "example/arxiv-openalex-papers", ["papers", "citation", "science"]),
        ("open_legal_text", "example/wikimedia-public-domain-books", ["wikimedia", "public-domain"]),
        ("cybersecurity_defensive", "example/defensive-cyber-vuln", ["cybersecurity", "vulnerability"]),
        ("patents_legal", "example/uspto-patent-corpus", ["patent", "legal"]),
        ("biomedical_genomics", "example/pubmed-genbank-biomed", ["pubmed", "genomics"]),
        ("engineering_cad", "example/cad-geometry-bench", ["engineering", "cad", "geometry"]),
    ]

    for index, (family, dataset_id, tags) in enumerate(cases):
        refresh = radar.refresh(
            {
                "query": f"open {family} dataset",
                "source_families": [family],
                "hf_results": [
                    {
                        "id": dataset_id,
                        "downloads": 1000,
                        "lastModified": "2026-05-05T12:00:00Z",
                        "trendingScore": 10.0,
                        "tags": tags,
                        "author": "example",
                    },
                    {
                        "id": f"example/generic-code-baseline-{index}",
                        "downloads": 1000,
                        "lastModified": "2026-05-05T12:00:00Z",
                        "trendingScore": 10.0,
                        "tags": ["code"],
                        "author": "example",
                    },
                ],
            }
        )
        assert refresh["candidate_count"] == 1
        assert refresh["filtered_out_count"] == 1
        assert refresh["candidates"][0]["dataset_id"] == dataset_id
        assert refresh["candidates"][0]["source_family"] == family


def test_dataset_radar_discovery_scoring_ranks_review_candidates_without_approval(tmp_path):
    radar = DatasetRadar(artifacts_dir=tmp_path)

    refresh = radar.refresh(
        {
            "query": "open code agent dataset swe-bench stack tool use",
            "target_nodes": ["Coder Expert", "Toolsmith Expert"],
            "hf_results": [
                {
                    "id": "unknown/private-chat-dump",
                    "downloads": 500000,
                    "lastModified": "2026-05-05T10:00:00Z",
                    "trendingScore": 99.0,
                    "tags": ["chat", "private", "conversation"],
                    "author": "unknown",
                },
                {
                    "id": "example/apache-code-agent",
                    "downloads": 125000,
                    "lastModified": "2026-05-05T12:00:00Z",
                    "trendingScore": 56.0,
                    "tags": ["license:apache-2.0", "code", "agent", "swe-bench"],
                    "author": "example",
                },
                {
                    "id": "example/old-math-set",
                    "downloads": 200,
                    "lastModified": "2024-01-01T00:00:00Z",
                    "trendingScore": 1.0,
                    "tags": ["license:apache-2.0", "math"],
                    "author": "example",
                },
            ],
        }
    )

    ranked_ids = [candidate["dataset_id"] for candidate in refresh["candidates"]]
    assert ranked_ids[0] == "example/apache-code-agent"
    assert ranked_ids[-1] == "unknown/private-chat-dump"
    top = refresh["candidates"][0]
    assert top["auto_approved"] is False
    assert top["review_score"] > refresh["candidates"][1]["review_score"]
    assert top["quality_signals"]["review_priority"] == "high"
    assert top["quality_signals"]["target_fit_signal"] > 0
    assert top["ranking_reason"] == "candidate-ranked-for-review-only"


def test_dataset_radar_candidate_review_is_replayable_and_cannot_train_approve_by_default(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/ops/brain/dataset-radar/refresh",
        json={
            "session_id": "dataset-radar-candidate-review",
            "operator_actor": "Control Panel",
            "query": "open code agent dataset",
            "hf_results": [
                {
                    "id": "example/apache-code-agent",
                    "downloads": 125000,
                    "lastModified": "2026-05-05T12:00:00Z",
                    "trendingScore": 56.0,
                    "tags": ["license:apache-2.0", "code", "agent"],
                    "author": "example",
                }
            ],
        },
    )

    blocked_train = client.post(
        "/ops/brain/dataset-radar/candidate-review",
        json={
            "dataset_id": "example/apache-code-agent",
            "review_state": "approved_train",
            "reviewer": "operator",
            "reason": "should not train-approve from candidate review",
        },
    ).json()
    assert blocked_train["decision"] == "blocked_training_approval"
    assert blocked_train["applied_state"] == "pending_license_review"
    assert blocked_train["training_approval_allowed"] is False

    review = client.post(
        "/ops/brain/dataset-radar/candidate-review",
        json={
            "dataset_id": "example/apache-code-agent",
            "review_state": "approved_teacher_context",
            "reviewer": "operator",
            "reason": "license tag present; teacher context only until provenance review completes",
        },
    )
    assert review.status_code == 200
    payload = review.json()
    assert payload["candidate_review_id"].startswith("dataset-radar-review-")
    assert payload["applied_state"] == "approved_teacher_context"
    assert payload["training_approval_allowed"] is False
    assert "teacher_context" in payload["allowed_uses"]
    assert payload["replay"]["event_log_ref"].endswith("candidate_reviews.jsonl")

    preview = client.post(
        "/ops/brain/dataset-radar/gate-preview",
        json={"dataset_id": "example/apache-code-agent"},
    ).json()
    gates = {gate["split"]: gate for gate in preview["gates"]}
    assert gates["train"]["allowed"] is False
    assert gates["teacher_context"]["allowed"] is True
    assert preview["latest_candidate_review"]["candidate_review_id"] == payload["candidate_review_id"]

    summary = client.get("/ops/brain/dataset-radar").json()
    assert summary["latest_candidate_review"]["candidate_review_id"] == payload["candidate_review_id"]
    assert summary["candidate_review_history"][0]["applied_state"] == "approved_teacher_context"
    assert summary["operator_actions"]["candidate_review"]["endpoint"] == "/ops/brain/dataset-radar/candidate-review"

    reviews = client.get("/ops/brain/dataset-radar/candidate-reviews")
    assert reviews.status_code == 200
    assert reviews.json()["reviews"][0]["candidate_review_id"] == payload["candidate_review_id"]

    replay = client.get(f"/ops/brain/dataset-radar/candidate-reviews/{payload['candidate_review_id']}")
    assert replay.status_code == 200
    assert replay.json()["dataset_id"] == "example/apache-code-agent"

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "dataset-radar-candidate-review"}).json()
    dataset_frame = next(frame for frame in blackbox["frames"] if frame["frame_id"] == "dataset-radar")
    assert "/ops/brain/dataset-radar/candidate-reviews" in dataset_frame["evidence_refs"]
    assert "/ops/brain/dataset-radar/candidate-reviews/{candidate_review_id}" in dataset_frame["replay_refs"]


def test_dataset_radar_source_detail_replays_reviews_gates_and_material_usage(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/ops/brain/dataset-radar/refresh",
        json={
            "session_id": "dataset-radar-source-detail",
            "operator_actor": "Control Panel",
            "query": "open code agent dataset",
            "hf_results": [
                {
                    "id": "example/apache-code-agent",
                    "downloads": 125000,
                    "lastModified": "2026-05-05T12:00:00Z",
                    "trendingScore": 56.0,
                    "tags": ["license:apache-2.0", "code", "agent"],
                    "author": "example",
                }
            ],
        },
    )
    review = client.post(
        "/ops/brain/dataset-radar/candidate-review",
        json={
            "dataset_id": "example/apache-code-agent",
            "review_state": "approved_teacher_context",
            "reviewer": "operator",
            "reason": "source detail fixture review",
        },
    ).json()
    material_request = client.post(
        "/ops/brain/dataset-radar/material-request",
        json={
            "teacher_ref": "teacher:qwen3-coder-next",
            "target_node": "Coder Expert",
            "requested_split": "teacher_context",
            "allowed_use": "teacher_context",
            "limit": 200,
        },
    ).json()
    assert "example/apache-code-agent" in material_request["approved_source_ids"]

    detail_response = client.get("/ops/brain/dataset-radar/sources/example/apache-code-agent")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["source_kind"] == "candidate"
    assert detail["dataset_id"] == "example/apache-code-agent"
    assert detail["latest_candidate_review"]["candidate_review_id"] == review["candidate_review_id"]
    assert detail["candidate_review_history"][0]["candidate_review_id"] == review["candidate_review_id"]
    assert detail["gate_preview"]["gates"][0]["split"] == "train"
    assert detail["gate_preview"]["gates"][0]["allowed"] is False
    assert any(gate["split"] == "teacher_context" and gate["allowed"] for gate in detail["gate_preview"]["gates"])
    review_packet = detail["review_required_packet"]
    review_fields = {field["field"]: field for field in review_packet["fields"]}
    assert review_packet["review_state"] == "review_required"
    assert review_packet["training_promotion_allowed"] is False
    assert review_packet["teacher_context_allowed"] is True
    assert "training_eligibility" in review_packet["blocking_fields"]
    assert review_fields["license_evidence"]["status"] == "required"
    assert review_fields["provenance_evidence"]["status"] == "required"
    assert review_fields["privacy_evidence"]["status"] == "required"
    assert detail["material_request_usage"][0]["material_request_id"] == material_request["material_request_id"]
    assert detail["material_request_usage"][0]["usage_state"] == "approved"
    assert detail["material_request_usage"][0]["dataset_forge_handoff"]["endpoint"] == "/ops/brain/dataset-forge/manifests"
    assert (
        detail["material_request_usage"][0]["dataset_forge_handoff"]["request_body_template"]["material_request_ref"]
        == material_request["material_request_id"]
    )
    assert detail["operator_actions"]["candidate_review"]["endpoint"] == "/ops/brain/dataset-radar/candidate-review"

    canonical = client.get("/ops/brain/dataset-radar/sources/the-stack-v2").json()
    assert canonical["source_kind"] == "canonical_source"
    assert canonical["canonical_source"]["dataset_id"] == "the-stack-v2"
    assert canonical["gate_preview"]["gates"][0]["allowed"] is True
    assert canonical["review_required_packet"]["training_promotion_allowed"] is False
    assert "privacy_evidence" in canonical["review_required_packet"]["blocking_fields"]

    open_training = client.get("/ops/brain/dataset-radar/sources/common-corpus").json()
    assert open_training["source_kind"] == "canonical_source"
    assert open_training["review_required_packet"]["review_state"] == "complete"
    assert open_training["review_required_packet"]["training_promotion_allowed"] is True

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "dataset-radar-source-detail"}).json()
    dataset_frame = next(frame for frame in blackbox["frames"] if frame["frame_id"] == "dataset-radar")
    assert "/ops/brain/dataset-radar/sources/{dataset_id}" in dataset_frame["replay_refs"]
    assert "source_detail_replay" in dataset_frame["compliance_controls"]

    missing = client.get("/ops/brain/dataset-radar/sources/missing/dataset")
    assert missing.status_code == 404


def test_dataset_radar_material_request_can_use_reviewed_candidates_for_teacher_context_only(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/ops/brain/dataset-radar/refresh",
        json={
            "query": "open code agent dataset",
            "hf_results": [
                {
                    "id": "example/apache-code-agent",
                    "downloads": 125000,
                    "lastModified": "2026-05-05T12:00:00Z",
                    "trendingScore": 56.0,
                    "tags": ["license:apache-2.0", "code", "agent"],
                    "author": "example",
                }
            ],
        },
    )
    client.post(
        "/ops/brain/dataset-radar/candidate-review",
        json={
            "dataset_id": "example/apache-code-agent",
            "review_state": "approved_teacher_context",
            "reviewer": "operator",
            "reason": "teacher-context only review",
        },
    )

    teacher_context = client.post(
        "/ops/brain/dataset-radar/material-request",
        json={
            "teacher_ref": "teacher:qwen3-coder-next",
            "requested_split": "teacher_context",
            "allowed_use": "teacher_context",
            "limit": 200,
        },
    ).json()
    assert "example/apache-code-agent" in teacher_context["approved_source_ids"]
    handoff = teacher_context["dataset_forge_handoff"]
    assert handoff["endpoint"] == "/ops/brain/dataset-forge/manifests"
    assert handoff["method"] == "POST"
    assert handoff["auto_execute_allowed"] is False
    assert handoff["request_body_template"]["material_request_ref"] == teacher_context["material_request_id"]
    assert handoff["request_body_template"]["metadata"]["requested_split"] == "teacher_context"
    candidate_source = next(
        source for source in handoff["request_body_template"]["sources"] if source["dataset_radar_source_id"] == "example/apache-code-agent"
    )
    assert candidate_source["metadata"]["source_kind"] == "candidate"
    assert candidate_source["metadata"]["training_eligible"] is False
    reviewed_preview = next(
        preview for preview in teacher_context["source_gate_previews"] if preview["dataset_id"] == "example/apache-code-agent"
    )
    assert reviewed_preview["source_kind"] == "candidate"
    assert reviewed_preview["gates"][0]["allowed"] is True

    train = client.post(
        "/ops/brain/dataset-radar/material-request",
        json={
            "teacher_ref": "teacher:qwen3-coder-next",
            "requested_split": "train",
            "allowed_use": "train",
            "limit": 200,
        },
    ).json()
    assert "example/apache-code-agent" not in train["approved_source_ids"]
    assert all(preview["source_kind"] == "canonical_source" for preview in train["source_gate_previews"])


def test_dataset_radar_split_gate_enforces_training_and_sealed_eval_boundaries():
    radar = DatasetRadar()

    assert radar.validate_source_for_split("the-stack-v2", "train")["allowed"] is True
    assert radar.validate_source_for_split("context7", "teacher_context")["allowed"] is True
    assert radar.validate_source_for_split("context7", "train")["allowed"] is False
    assert radar.validate_source_for_split("swe-bench", "teacher_free_hidden")["allowed"] is True
    assert radar.validate_source_for_split("swe-bench", "train")["allowed"] is False
    assert radar.validate_source_for_split("books3", "train")["allowed"] is False
    assert radar.validate_source_for_split("wildchat", "train")["allowed"] is False


def test_dataset_radar_api_and_visualizer_flow_are_available(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    scorecard = client.get("/ops/brain/dataset-radar")
    assert scorecard.status_code == 200
    payload = scorecard.json()
    assert payload["surface_id"] == "living-dataset-radar"
    assert payload["source_count"] >= 80
    assert "approved_train" in payload["state_counts"]

    refresh = client.post(
        "/ops/brain/dataset-radar/refresh",
        json={
            "query": "fresh code evals",
            "sort": "lastModified",
            "hf_results": [
                {
                    "id": "example/fresh-code-agent-evals",
                    "downloads": 101,
                    "lastModified": "2026-05-05T01:00:00Z",
                    "trendingScore": 9.75,
                    "tags": ["license:mit", "code", "agent"],
                    "author": "example",
                }
            ],
        },
    )
    assert refresh.status_code == 200
    assert refresh.json()["candidates"][0]["license_state"] == "pending_provenance_review"
    assert refresh.json()["candidates"][0]["auto_approved"] is False

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "dataset-radar"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["dataset_radar_scorecard"]["surface_id"] == "living-dataset-radar"
    assert control_panel["dataset_flow_view"]["view_id"] == "dataset-flow-view"
    assert [
        "Macro Hive",
        "Neural Substrate",
        "Transformer/MoE Path",
        "Growth Flow",
        "Dataset Curriculum",
        "Replay Mode",
    ] == control_panel["dataset_flow_view"]["stage_views"]
    assert "dataset -> license/privacy gate -> teacher council -> curriculum stage -> student -> eval -> promotion" in (
        control_panel["dataset_flow_view"]["flow_label"]
    )

    ui = client.get("/ui/visualizer/")
    assert ui.status_code == 200
    assert "Dataset Flow View" in ui.text
    assert "Dataset Curriculum" in ui.text


def test_control_panel_exposes_dataset_radar_operator_refresh_card(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Dataset Radar" in ui.text
    assert "datasetRadarScorecard" in ui.text
    assert "datasetRadarRefreshForm" in ui.text
    assert "datasetRadarRefreshButton" in ui.text
    assert "datasetRadarRequiredTags" in ui.text
    assert "datasetRadarBlockedTags" in ui.text
    assert "datasetRadarAuthors" in ui.text
    assert "datasetRadarSourceFamilyFilter" in ui.text
    assert "datasetRadarCandidateReviewForm" in ui.text
    assert "datasetRadarCandidateReviewButton" in ui.text
    assert "datasetRadarMaterialRequestForm" in ui.text
    assert "datasetRadarMaterialRequestButton" in ui.text
    assert "datasetRadarSourceDetailForm" in ui.text
    assert "datasetRadarSourceDetailButton" in ui.text
    assert "Refresh Dataset Radar" in ui.text
    assert "Record Candidate Review" in ui.text
    assert "Request Material" in ui.text
    assert "Inspect Source Detail" in ui.text
    assert "science_research" in ui.text
    assert "open_legal_text" in ui.text
    assert "cybersecurity_defensive" in ui.text
    assert "patents_legal" in ui.text
    assert "biomedical_genomics" in ui.text
    assert "engineering_cad" in ui.text
    assert "teacher councils request material through Dataset Radar" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderDatasetRadarScorecard" in app_js
    assert "submitDatasetRadarRefresh" in app_js
    assert "datasetRadarDiscoveryFilters" in app_js
    assert "required_tags" in app_js
    assert "blocked_tags" in app_js
    assert "source_families" in app_js
    assert "submitDatasetRadarCandidateReview" in app_js
    assert "submitDatasetRadarMaterialRequest" in app_js
    assert "inspectDatasetRadarSourceDetail" in app_js
    assert "/ops/brain/dataset-radar/refresh" in app_js
    assert "/ops/brain/dataset-radar/candidate-review" in app_js
    assert "/ops/brain/dataset-radar/material-request" in app_js
    assert "/ops/brain/dataset-radar/sources" in app_js
    assert "/ops/brain/canon/dataset-radar" in app_js
    assert "refresh_history" in app_js
    assert "Replay Artifacts" in app_js
    assert "Latest review action" in app_js
    assert "Latest material request" in app_js
    assert "DatasetForge handoff" in app_js
    assert "dataset_forge_handoff" in app_js
    assert "Latest source detail" in app_js
    assert "Source review packet" in app_js
    assert "review_required_packet" in app_js
    assert "blocking_fields" in app_js
    assert "Freshness Radar" in app_js
    assert "refresh_due_sources" in app_js
    assert "source_freshness_warnings" in app_js
    assert "refresh_run_freshness" in app_js
    assert "Refresh Recommendations" in app_js
    assert "refresh_recommendations" in app_js
    assert "Inspect Source" in app_js
    assert "Inspect Due Source" in app_js
    assert "Inspect Recommended Source" in app_js
    assert "data-dataset-radar-detail" in app_js
    assert "inspectDatasetRadarSourceFromButton" in app_js
    assert "event_log_ref" in app_js
    assert "endpoint_template" in app_js
    assert "session_id" in app_js
    assert "operator_actor" in app_js


def test_dataset_radar_target_node_presets_drive_refresh_queries_and_operator_ui(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    presets = client.get("/ops/brain/dataset-radar/refresh-presets")
    assert presets.status_code == 200
    preset_payload = presets.json()
    preset_ids = {preset["preset_id"] for preset in preset_payload["presets"]}
    assert {
        "coder-expert",
        "math-reasoning",
        "research-open",
        "multimodal-perception",
        "cybersecurity-defensive",
        "patent-legal",
        "biomedical-genomics",
        "engineering-cad",
    }.issubset(preset_ids)
    coder = next(preset for preset in preset_payload["presets"] if preset["preset_id"] == "coder-expert")
    assert "Coder Expert" in coder["target_nodes"]
    assert coder["seed_lineage_source_ids"] == [
        "the-stack-v2",
        "stack-edu",
        "codesearchnet",
        "context7",
        "swe-bench",
        "swe-gym",
    ]
    assert {
        "The Stack v2",
        "Stack-Edu",
        "CodeSearchNet",
        "Context7",
        "SWE-bench",
        "SWE-Gym",
    }.issubset(set(coder["seed_lineage_labels"]))
    assert coder["seed_lineage_train_source_ids"] == ["the-stack-v2", "stack-edu", "codesearchnet"]
    assert coder["seed_lineage_teacher_context_only_source_ids"] == ["context7"]
    assert coder["seed_lineage_sealed_eval_source_ids"] == ["swe-bench", "swe-gym"]
    assert coder["default_sort"] == "trendingScore"
    patent = next(preset for preset in preset_payload["presets"] if preset["preset_id"] == "patent-legal")
    assert patent["source_family"] == "patents_legal"
    assert "Patent Expert" in patent["target_nodes"]

    refresh = client.post(
        "/ops/brain/dataset-radar/refresh",
        json={
            "session_id": "dataset-radar-preset",
            "operator_actor": "Control Panel",
            "preset_id": "coder-expert",
            "hf_results": [
                {
                    "id": "example/coder-preset-evals",
                    "downloads": 333,
                    "lastModified": "2026-05-05T17:00:00Z",
                    "trendingScore": 11.5,
                    "tags": ["license:mit", "code", "swe-bench"],
                    "author": "example",
                }
            ],
        },
    )
    assert refresh.status_code == 200
    refresh_payload = refresh.json()
    assert refresh_payload["preset"]["preset_id"] == "coder-expert"
    assert refresh_payload["query"] == coder["query"]
    assert refresh_payload["sort"] == coder["default_sort"]
    assert refresh_payload["target_nodes"] == coder["target_nodes"]
    assert refresh_payload["seed_lineage_source_ids"] == coder["seed_lineage_source_ids"]

    summary = client.get("/ops/brain/dataset-radar").json()
    assert summary["refresh_presets"][0]["preset_id"]
    assert summary["coder_expert_lineage_split_policy"]["train_source_ids"] == [
        "the-stack-v2",
        "stack-edu",
        "codesearchnet",
    ]
    assert summary["coder_expert_lineage_split_policy"]["sealed_eval_source_ids"] == ["swe-bench", "swe-gym"]
    assert summary["latest_refresh_run"]["preset_id"] == "coder-expert"
    assert summary["operator_actions"]["list_refresh_presets"]["endpoint"] == "/ops/brain/dataset-radar/refresh-presets"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "datasetRadarPreset" in ui.text
    assert "Coder Expert" in ui.text
    assert "Math Reasoning" in ui.text
    assert "Multimodal Perception" in ui.text
    assert "Cybersecurity Defensive" in ui.text
    assert "Patent Legal" in ui.text
    assert "Biomedical Genomics" in ui.text
    assert "Engineering CAD" in ui.text
    assert "optional custom query; preset default used when blank" in ui.text
    assert 'value="fresh open training datasets"' not in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "datasetRadarPreset" in app_js
    assert "preset_id" in app_js
    assert "Review Priority Ranking" in app_js
    assert "review_score" in app_js
    assert 'const query = (dom.datasetRadarQuery?.value || "").trim();' in app_js
    assert "if (query)" in app_js
    assert "/ops/brain/dataset-radar/refresh-presets" in app_js


def test_dataset_radar_refresh_runs_are_replayable_and_blackbox_visible(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    refresh = client.post(
        "/ops/brain/dataset-radar/refresh",
        json={
            "session_id": "dataset-radar-history",
            "operator_actor": "Control Panel",
            "query": "fresh open code datasets",
            "sort": "trendingScore",
            "hf_results": [
                {
                    "id": "example/fresh-code-dataset",
                    "downloads": 2048,
                    "lastModified": "2026-05-05T16:00:00Z",
                    "trendingScore": 42.0,
                    "tags": ["license:apache-2.0", "code", "agent"],
                    "author": "example",
                }
            ],
        },
    )
    assert refresh.status_code == 200
    refresh_payload = refresh.json()
    assert refresh_payload["refresh_run_id"].startswith("dataset-radar-refresh-")
    assert refresh_payload["operator_context"]["session_id"] == "dataset-radar-history"
    assert refresh_payload["operator_context"]["operator_actor"] == "Control Panel"
    assert refresh_payload["replay"]["event_log_ref"].endswith("refresh_runs.jsonl")
    assert refresh_payload["replay"]["artifact_ref"].endswith(".json")
    assert refresh_payload["candidates"][0]["refresh_run_id"] == refresh_payload["refresh_run_id"]

    radar_dir = project_root / "runtime" / "artifacts" / "curriculum" / "dataset-radar"
    events_path = radar_dir / "refresh_runs.jsonl"
    assert events_path.is_file()
    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
    assert events[-1]["refresh_run_id"] == refresh_payload["refresh_run_id"]
    assert events[-1]["candidate_count"] == 1

    replay_path = project_root / refresh_payload["replay"]["artifact_ref"]
    assert replay_path.is_file()
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    assert replay["refresh_run_id"] == refresh_payload["refresh_run_id"]
    assert replay["blocked_rule"] == "HF discoveries are candidates only; license/provenance/privacy gates decide use."

    summary = client.get("/ops/brain/dataset-radar").json()
    assert summary["latest_refresh_run"]["refresh_run_id"] == refresh_payload["refresh_run_id"]
    assert summary["refresh_history"][0]["refresh_run_id"] == refresh_payload["refresh_run_id"]
    assert summary["refresh_history"][0]["replay"]["artifact_ref"] == refresh_payload["replay"]["artifact_ref"]
    assert summary["operator_actions"]["list_refresh_runs"]["endpoint"] == "/ops/brain/dataset-radar/refresh-runs"
    assert (
        summary["operator_actions"]["replay_refresh_run"]["endpoint_template"]
        == "/ops/brain/dataset-radar/refresh-runs/{refresh_run_id}"
    )

    runs = client.get("/ops/brain/dataset-radar/refresh-runs")
    assert runs.status_code == 200
    assert runs.json()["runs"][0]["refresh_run_id"] == refresh_payload["refresh_run_id"]

    replay_response = client.get(f"/ops/brain/dataset-radar/refresh-runs/{refresh_payload['refresh_run_id']}")
    assert replay_response.status_code == 200
    assert replay_response.json()["refresh_run_id"] == refresh_payload["refresh_run_id"]
    assert replay_response.json()["candidates"][0]["dataset_id"] == "example/fresh-code-dataset"

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "dataset-radar-history"}).json()
    assert blackbox["scorecard_refs"]["dataset_radar"] == "/ops/brain/canon/dataset-radar"
    assert "dataset-radar" in {frame["frame_id"] for frame in blackbox["frames"]}


def test_dataset_radar_batch_refresh_runs_multiple_presets_with_replay(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    batch = client.post(
        "/ops/brain/dataset-radar/refresh-batch",
        json={
            "session_id": "dataset-radar-batch",
            "operator_actor": "Control Panel",
            "preset_ids": ["coder-expert", "math-reasoning"],
            "hf_results_by_preset": {
                "coder-expert": [
                    {
                        "id": "example/coder-batch-dataset",
                        "downloads": 1200,
                        "lastModified": "2026-05-05T18:00:00Z",
                        "trendingScore": 23.5,
                        "tags": ["license:apache-2.0", "code", "agent"],
                        "author": "example",
                    }
                ],
                "math-reasoning": [
                    {
                        "id": "example/math-batch-dataset",
                        "downloads": 900,
                        "lastModified": "2026-05-05T18:05:00Z",
                        "trendingScore": 19.0,
                        "tags": ["license:mit", "math", "proof"],
                        "author": "example",
                    }
                ],
            },
        },
    )
    assert batch.status_code == 200
    payload = batch.json()
    assert payload["batch_id"].startswith("dataset-radar-batch-")
    assert payload["surface_id"] == "living-dataset-radar"
    assert payload["preset_count"] == 2
    assert payload["operator_context"]["session_id"] == "dataset-radar-batch"
    assert payload["replay"]["event_log_ref"].endswith("refresh_batches.jsonl")
    assert payload["replay"]["artifact_ref"].endswith(".json")
    assert [run["preset_id"] for run in payload["runs"]] == ["coder-expert", "math-reasoning"]
    assert len(payload["refresh_run_ids"]) == 2
    assert payload["runs"][0]["batch_id"] == payload["batch_id"]
    assert payload["runs"][1]["batch_id"] == payload["batch_id"]
    assert payload["runs"][0]["candidates"][0]["dataset_id"] == "example/coder-batch-dataset"

    radar_dir = project_root / "runtime" / "artifacts" / "curriculum" / "dataset-radar"
    batch_events_path = radar_dir / "refresh_batches.jsonl"
    assert batch_events_path.is_file()
    batch_events = [json.loads(line) for line in batch_events_path.read_text(encoding="utf-8").splitlines()]
    assert batch_events[-1]["batch_id"] == payload["batch_id"]
    assert batch_events[-1]["refresh_run_ids"] == payload["refresh_run_ids"]

    replay_path = project_root / payload["replay"]["artifact_ref"]
    assert replay_path.is_file()
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    assert replay["batch_id"] == payload["batch_id"]
    assert replay["runs"][1]["candidates"][0]["source_family"] == "math_reasoning"

    summary = client.get("/ops/brain/dataset-radar").json()
    assert summary["latest_refresh_batch"]["batch_id"] == payload["batch_id"]
    assert summary["refresh_batch_history"][0]["batch_id"] == payload["batch_id"]
    assert summary["operator_actions"]["refresh_batch"]["endpoint"] == "/ops/brain/dataset-radar/refresh-batch"
    assert summary["operator_actions"]["list_refresh_batches"]["endpoint"] == "/ops/brain/dataset-radar/refresh-batches"
    assert (
        summary["operator_actions"]["replay_refresh_batch"]["endpoint_template"]
        == "/ops/brain/dataset-radar/refresh-batches/{batch_id}"
    )

    batches = client.get("/ops/brain/dataset-radar/refresh-batches")
    assert batches.status_code == 200
    assert batches.json()["batches"][0]["batch_id"] == payload["batch_id"]

    batch_replay = client.get(f"/ops/brain/dataset-radar/refresh-batches/{payload['batch_id']}")
    assert batch_replay.status_code == 200
    assert batch_replay.json()["refresh_run_ids"] == payload["refresh_run_ids"]

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "/ops/brain/dataset-radar/refresh-batch" in app_js
    assert "refresh_batch_history" in app_js
    assert "datasetRadarBatchButton" in app_js


def test_dataset_radar_batch_refresh_applies_operator_discovery_filters(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    batch = client.post(
        "/ops/brain/dataset-radar/refresh-batch",
        json={
            "session_id": "dataset-radar-batch-filter",
            "operator_actor": "Control Panel",
            "preset_ids": ["coder-expert", "math-reasoning"],
            "required_tags": ["code"],
            "source_families": ["code_agent"],
            "hf_results_by_preset": {
                "coder-expert": [
                    {
                        "id": "example/coder-filtered-dataset",
                        "downloads": 1200,
                        "lastModified": "2026-05-05T18:00:00Z",
                        "trendingScore": 23.5,
                        "tags": ["license:apache-2.0", "code", "agent"],
                        "author": "example",
                    }
                ],
                "math-reasoning": [
                    {
                        "id": "example/math-filtered-dataset",
                        "downloads": 900,
                        "lastModified": "2026-05-05T18:05:00Z",
                        "trendingScore": 19.0,
                        "tags": ["license:mit", "math", "proof"],
                        "author": "example",
                    }
                ],
            },
        },
    )

    assert batch.status_code == 200
    runs = batch.json()["runs"]
    assert runs[0]["raw_candidate_count"] == 1
    assert runs[0]["candidate_count"] == 1
    assert runs[0]["discovery_filters"]["required_tags"] == ["code"]
    assert runs[0]["discovery_filters"]["source_families"] == ["code_agent"]
    assert runs[1]["raw_candidate_count"] == 1
    assert runs[1]["candidate_count"] == 0
    assert runs[1]["filtered_out_count"] == 1


def test_dataset_radar_candidate_gate_preview_surfaces_blocked_splits_in_api_and_ui(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    refresh = client.post(
        "/ops/brain/dataset-radar/refresh",
        json={
            "session_id": "dataset-radar-gate-preview",
            "operator_actor": "Control Panel",
            "preset_id": "instruction-preference",
            "hf_results": [
                {
                    "id": "example/user-chat-dump",
                    "downloads": 7,
                    "lastModified": "2026-05-05T19:00:00Z",
                    "trendingScore": 1.0,
                    "tags": ["chat-dump", "instruction"],
                    "author": "example",
                }
            ],
        },
    )
    assert refresh.status_code == 200
    assert refresh.json()["candidates"][0]["license_state"] == "blocked_private_or_personal"

    preview = client.post(
        "/ops/brain/dataset-radar/gate-preview",
        json={
            "dataset_id": "example/user-chat-dump",
            "splits": ["train", "teacher_context", "validation", "teacher_free_hidden"],
        },
    )
    assert preview.status_code == 200
    preview_payload = preview.json()
    assert preview_payload["dataset_id"] == "example/user-chat-dump"
    assert preview_payload["source_kind"] == "candidate"
    assert preview_payload["license_state"] == "blocked_private_or_personal"
    assert preview_payload["auto_approval_allowed"] is False
    assert {gate["split"]: gate["allowed"] for gate in preview_payload["gates"]} == {
        "train": False,
        "teacher_context": False,
        "validation": False,
        "teacher_free_hidden": False,
    }
    assert "candidate remains blocked" in preview_payload["gates"][0]["reason"]

    summary = client.get("/ops/brain/dataset-radar").json()
    assert summary["runtime_state"] == "degraded"
    assert summary["candidate_gate_blocked_count"] == 1
    assert summary["candidate_gate_previews"][0]["dataset_id"] == "example/user-chat-dump"
    assert summary["candidate_gate_previews"][0]["gates"][0]["allowed"] is False
    assert summary["operator_actions"]["gate_preview"]["endpoint"] == "/ops/brain/dataset-radar/gate-preview"

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "candidate_gate_previews" in app_js
    assert "candidate_gate_blocked_count" in app_js
    assert "candidate gate blocks" in app_js
    assert "Candidate Gate Preview" in app_js


def test_dataset_radar_teacher_material_requests_are_gated_and_replayable(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    request = client.post(
        "/ops/brain/dataset-radar/material-request",
        json={
            "session_id": "dataset-radar-material-request",
            "operator_actor": "Teacher Council",
            "teacher_ref": "teacher:qwen3-coder-next",
            "target_node": "Coder Expert",
            "requested_split": "train",
            "allowed_use": "train",
            "limit": 8,
        },
    )
    assert request.status_code == 200
    payload = request.json()
    assert payload["material_request_id"].startswith("dataset-radar-material-")
    assert payload["teacher_ref"] == "teacher:qwen3-coder-next"
    assert payload["target_node"] == "Coder Expert"
    assert payload["requested_split"] == "train"
    assert payload["auto_download_allowed"] is False
    assert payload["replay"]["event_log_ref"].endswith("material_requests.jsonl")
    assert payload["approved_source_ids"]
    assert "the-stack-v2" in payload["approved_source_ids"]
    assert all(gate["gates"][0]["split"] == "train" for gate in payload["source_gate_previews"])

    radar_dir = project_root / "runtime" / "artifacts" / "curriculum" / "dataset-radar"
    events_path = radar_dir / "material_requests.jsonl"
    assert events_path.is_file()
    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
    assert events[-1]["material_request_id"] == payload["material_request_id"]
    assert events[-1]["approved_source_ids"] == payload["approved_source_ids"]

    replay_path = project_root / payload["replay"]["artifact_ref"]
    assert replay_path.is_file()
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    assert replay["material_request_id"] == payload["material_request_id"]
    assert replay["teacher_access_rule"] == "teacher councils request material through Dataset Radar only"

    summary = client.get("/ops/brain/dataset-radar").json()
    assert summary["latest_material_request"]["material_request_id"] == payload["material_request_id"]
    assert summary["material_request_history"][0]["material_request_id"] == payload["material_request_id"]
    assert summary["operator_actions"]["material_request"]["endpoint"] == "/ops/brain/dataset-radar/material-request"
    assert summary["operator_actions"]["list_material_requests"]["endpoint"] == "/ops/brain/dataset-radar/material-requests"

    requests = client.get("/ops/brain/dataset-radar/material-requests")
    assert requests.status_code == 200
    assert requests.json()["requests"][0]["material_request_id"] == payload["material_request_id"]

    replay_response = client.get(f"/ops/brain/dataset-radar/material-requests/{payload['material_request_id']}")
    assert replay_response.status_code == 200
    assert replay_response.json()["approved_source_ids"] == payload["approved_source_ids"]

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "dataset-radar-material-request"}).json()
    dataset_frame = next(frame for frame in blackbox["frames"] if frame["frame_id"] == "dataset-radar")
    assert "/ops/brain/dataset-radar/material-requests" in dataset_frame["evidence_refs"]
    assert "/ops/brain/dataset-radar/material-requests/{material_request_id}" in dataset_frame["replay_refs"]
    assert "material_request_replay" in dataset_frame["compliance_controls"]

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "material_request_history" in app_js
    assert "candidate_review_history" in app_js
    assert "Candidate Reviews" in app_js
    assert "Teacher Material Requests" in app_js
