from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.adapters.dataset_forge import DatasetForge, DatasetForgeRequest
from nexusnet.curriculum.dataset_radar import DatasetRadar
from tests.test_nexus_phase1_foundation import make_project


def test_dataset_forge_builds_prompt_response_splits_eval_cases_and_policy_scan():
    forge = DatasetForge()

    manifest = forge.build(
        DatasetForgeRequest(
            dataset_manifest_id="dataset::control-panel-style",
            purpose="Control Panel summarization style adapter",
            sources=[
                {
                    "source_id": "doc::control-panel",
                    "source_type": "document",
                    "text": "NexusNet Control Panel monitors NexusBrain, AOs, experts, tools, memory, policy, runtime, and evolution loops.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
                },
                {
                    "source_id": "doc::policy-kernel",
                    "source_type": "document",
                    "text": "Policy Kernel scans training candidates, memory updates, tool execution, artifacts, and autonomous updates.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
                },
            ],
        )
    )

    assert manifest["status_label"] == "LOCKED CANON"
    assert manifest["authority"] == "NexusBrain"
    assert manifest["status"] == "ready"
    assert manifest["dataset"]["example_count"] == 2
    assert manifest["dataset"]["contains_private_data"] is False
    assert manifest["dataset"]["license_status"] == "approved"
    assert manifest["splits"]["train"]["example_count"] == 1
    assert manifest["splits"]["validation"]["example_count"] == 1
    assert manifest["splits"]["test"]["example_count"] == 0
    assert manifest["examples"][0]["prompt"].startswith("Summarize the NexusNet source")
    assert manifest["eval_cases"]
    assert manifest["policy_scan"]["summary"]["allow_merge"] is True


def test_dataset_forge_blocks_private_or_unlicensed_sources_before_training_use():
    forge = DatasetForge()

    manifest = forge.build(
        {
            "dataset_manifest_id": "dataset::blocked-private",
            "purpose": "Unsafe private log training",
            "sources": [
                {
                    "source_id": "raw::private-log",
                    "source_type": "trace",
                    "text": "private user trace with no license approval",
                    "license_status": "blocked",
                    "contains_private_data": True,
                    "provenance_ref": "",
                }
            ],
        }
    )

    assert manifest["status"] == "blocked"
    assert manifest["dataset"]["contains_private_data"] is True
    assert manifest["dataset"]["license_status"] == "blocked"
    assert manifest["policy_scan"]["summary"]["allow_merge"] is False
    assert {
        "training_candidate_requires_operator_approval",
        "artifact_requires_license_and_provenance",
    }.issubset({finding["rule_id"] for finding in manifest["policy_scan"]["findings"]})

    scorecard = forge.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_count"] == 1
    assert scorecard["latest_manifest"]["status"] == "blocked"


def test_dataset_forge_uses_dataset_radar_to_block_non_training_sources():
    forge = DatasetForge(dataset_radar=DatasetRadar())

    manifest = forge.build(
        {
            "dataset_manifest_id": "dataset::context7-teacher-context-only",
            "purpose": "Coder Expert child context training",
            "sources": [
                {
                    "source_id": "radar::context7",
                    "source_type": "web",
                    "text": "Context7 supplies current package documentation as teacher context, not direct train split material.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "https://context7.com/",
                    "dataset_radar_source_id": "context7",
                }
            ],
        }
    )

    assert manifest["status"] == "blocked"
    assert manifest["dataset_radar_gates"][0]["source_id"] == "context7"
    assert manifest["dataset_radar_gates"][0]["split"] == "train"
    assert manifest["dataset_radar_gates"][0]["allowed"] is False
    assert manifest["dataset_radar_gates"][0]["license_state"] == "approved_teacher_context"
    assert "dataset_radar_gate" in manifest["required_controls"]


def test_dataset_forge_keeps_sealed_eval_out_of_train_and_teacher_visible_splits():
    forge = DatasetForge(dataset_radar=DatasetRadar())

    manifest = forge.build(
        {
            "dataset_manifest_id": "dataset::coder-lineage",
            "purpose": "Coder Expert child lineage",
            "sources": [
                {
                    "source_id": "radar::the-stack-v2",
                    "source_type": "web",
                    "text": "The Stack v2 is approved for code training only after Dataset Radar and license/provenance gates pass.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "https://hf.co/datasets/bigcode/the-stack-v2",
                    "dataset_radar_source_id": "the-stack-v2",
                },
                {
                    "source_id": "synthetic::teacher-coder",
                    "source_type": "tool_output",
                    "text": "Synthetic case generated by a license-cleared teacher for Coder Expert routing and test-repair behavior.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "teacher:qwen3-coder-next",
                    "dataset_radar_source_id": "stack-edu",
                    "generator_model": "teacher:qwen3-coder-next",
                    "source_license_ref": "license_review:qwen3_2026",
                    "allowed_distillation_state": "approved",
                    "contamination_risk": "low",
                },
            ],
            "metadata": {"sealed_eval_source_ids": ["swe-bench", "swe-gym"]},
        }
    )

    assert manifest["status"] == "needs_review"
    assert "heldout" in manifest["splits"]
    assert "adversarial" in manifest["splits"]
    sealed = manifest["splits"]["teacher_free_hidden"]
    assert sealed["sealed"] is True
    assert sealed["visible_to_training"] is False
    assert sealed["visible_to_teacher_council"] is False
    assert sealed["source_ids"] == ["swe-bench", "swe-gym"]
    assert {gate["source_id"] for gate in manifest["dataset_radar_gates"]} == {"the-stack-v2", "stack-edu"}
    assert all(gate["allowed"] for gate in manifest["dataset_radar_gates"])
    assert manifest["dataset_radar_training_review_gate"]["allowed"] is False
    assert set(manifest["dataset_radar_training_review_gate"]["blocked_source_ids"]) == {"the-stack-v2", "stack-edu"}
    assert manifest["dataset"]["synthetic_generator_models"] == ["teacher:qwen3-coder-next"]
    split_policy = manifest["dataset_radar_lineage_split_policy"]
    assert split_policy["train_source_ids"] == ["the-stack-v2", "stack-edu", "codesearchnet"]
    assert split_policy["teacher_context_only_source_ids"] == ["context7"]
    assert split_policy["sealed_eval_source_ids"] == ["swe-bench", "swe-gym"]
    assert split_policy["split_rule"] == "training sources cannot be reused as sealed teacher-free eval sources"
    assert manifest["splits"]["train"]["blocked_source_ids"] == ["swe-bench", "swe-gym"]
    assert manifest["splits"]["teacher_free_hidden"]["blocked_from_train"] is True


def test_dataset_forge_records_knowledge_artifact_refs_as_context_lineage():
    forge = DatasetForge(dataset_radar=DatasetRadar())

    manifest = forge.build(
        {
            "dataset_manifest_id": "dataset::kac-context-lineage",
            "purpose": "Coder Expert child curriculum from compiled NexusNet context",
            "knowledge_artifact_refs": ["kac://architecture_review/abc123"],
            "sources": [
                {
                    "source_id": "doc::compiled-context-seed",
                    "source_type": "document",
                    "text": "Compiled KAC context can seed curriculum but cannot mutate model weights or promotions directly.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "docs/compiled_knowledge_artifact_layer.md",
                    "metadata": {"context_role": "teacher_council_seed"},
                }
            ],
        }
    )

    assert manifest["status"] == "ready"
    assert manifest["knowledge_artifact_refs"] == ["kac://architecture_review/abc123"]
    assert manifest["dataset"]["knowledge_artifact_refs"] == ["kac://architecture_review/abc123"]
    assert manifest["examples"][0]["knowledge_artifact_refs"] == ["kac://architecture_review/abc123"]
    assert manifest["eval_cases"][0]["knowledge_artifact_refs"] == ["kac://architecture_review/abc123"]
    assert "knowledge_artifact_context_gate" in manifest["required_controls"]
    assert "knowledge_artifact_runtime_gate" in manifest["required_controls"]
    assert manifest["knowledge_artifact_context_gate"] == "refs_only_no_prompt_or_weight_mutation"
    assert manifest["knowledge_artifact_runtime_gate"] == {
        "requires_krc_runtime_context_allowed": True,
        "blocks_stale_or_quarantined_context": True,
        "blocks_raw_retrieval_fallback_context": True,
        "gate_source": "KnowledgeArtifactCompiler.query",
        "mutation_allowed": False,
    }


def test_dataset_forge_blocks_kac_refs_when_runtime_context_evidence_is_disallowed():
    forge = DatasetForge(dataset_radar=DatasetRadar())

    manifest = forge.build(
        {
            "dataset_manifest_id": "dataset::kac-context-blocked",
            "purpose": "Blocked KAC context cannot seed training material",
            "knowledge_artifact_refs": ["kac://architecture_review/blocked"],
            "knowledge_artifact_runtime_contexts": [
                {
                    "artifact_id": "kac://architecture_review/blocked",
                    "runtime_context_allowed": False,
                    "fallback_state": "compiled_artifact_quarantined",
                    "quarantine_state": {"reason": "artifact_trust_preview_quarantined"},
                }
            ],
            "sources": [
                {
                    "source_id": "doc::compiled-context-seed",
                    "source_type": "document",
                    "text": "A quarantined compiled artifact must not become DatasetForge training context.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "docs/compiled_knowledge_artifact_layer.md",
                }
            ],
        }
    )

    assert manifest["status"] == "blocked"
    runtime_gate = manifest["knowledge_artifact_runtime_gate"]
    assert runtime_gate["allowed"] is False
    assert runtime_gate["runtime_context_evidence_count"] == 1
    assert runtime_gate["blocked_artifact_refs"] == ["kac://architecture_review/blocked"]
    assert "compiled_artifact_quarantined" in runtime_gate["blocked_reasons"]
    assert "knowledge_artifact_runtime_gate" in manifest["required_controls"]


def test_dataset_forge_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/dataset-forge/manifests",
        json={
            "dataset_manifest_id": "dataset::api-control-panel",
            "purpose": "Control Panel telemetry summarization",
            "sources": [
                {
                    "source_id": "doc::telemetry",
                    "source_type": "document",
                    "text": "Telemetry summaries should cite command ids, policy gates, runtime routes, and rollback state.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
                }
            ],
        },
    )
    assert response.status_code == 200
    manifest = response.json()
    assert manifest["status"] == "ready"

    summary = client.get("/ops/brain/dataset-forge")
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload["manifest_count"] == 1
    assert summary_payload["latest_manifest"]["dataset_manifest_id"] == "dataset::api-control-panel"

    scorecard = client.get("/ops/brain/canon/dataset-forge")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert "privacy_license_filters" in scorecard_payload["required_controls"]
    assert "dataset_radar_gate" in scorecard_payload["required_controls"]
    assert "sealed_teacher_free_eval_split" in scorecard_payload["required_controls"]
    assert scorecard_payload["operator_actions"]["build_manifest"]["endpoint"] == "/ops/brain/dataset-forge/manifests"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "dataset-forge-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["dataset_forge_scorecard"]["manifest_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "dataset-forge-cockpit"}).json()
    assert blackbox["scorecard_refs"]["dataset_forge"] == "/ops/brain/canon/dataset-forge"
    dataset_forge_frame = next(frame for frame in blackbox["frames"] if frame["frame_id"] == "dataset-forge")
    assert "/ops/brain/dataset-forge/manifests" in dataset_forge_frame["evidence_refs"]
    assert "dataset_radar_material_request_gate" in dataset_forge_frame["compliance_controls"]

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Dataset Forge" in ui.text
    assert "datasetForgeScorecard" in ui.text
    assert "datasetForgeManifestForm" in ui.text
    assert "datasetForgeApplyHandoffButton" in ui.text
    assert "datasetForgeManifestButton" in ui.text
    assert "operator-reviewed excerpt required" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderDatasetForgeScorecard" in app_js
    assert "applyDatasetForgeHandoffTemplate" in app_js
    assert "submitDatasetForgeManifest" in app_js
    assert "datasetForgeManifestRequestBody" in app_js
    assert "no_training_execution_authorized" in app_js
    assert "Manifest-time source review packets" in app_js
    assert "dataset_radar_review_packets" in app_js
    assert "Review-blocked Dataset Flow lineage" in app_js
    assert "review_blocked_lineage" in app_js
    assert "Training review gate" in app_js
    assert "dataset_radar_training_review_gate" in app_js
    assert "training promotion" in app_js
    assert "Lineage split policy" in app_js
    assert "dataset_radar_lineage_split_policy" in app_js
    assert "sealed eval blocked from train" in app_js
    assert "/ops/brain/canon/dataset-forge" in app_js
    assert "/ops/brain/dataset-forge/manifests" in app_js


def test_dataset_forge_records_dataset_radar_material_request_lineage(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    material_request = client.post(
        "/ops/brain/dataset-radar/material-request",
        json={
            "session_id": "dataset-forge-material-request",
            "operator_actor": "Teacher Council",
            "teacher_ref": "teacher:qwen3-coder-next",
            "target_node": "Coder Expert",
            "requested_split": "train",
            "allowed_use": "train",
        },
    ).json()
    assert "the-stack-v2" in material_request["approved_source_ids"]

    response = client.post(
        "/ops/brain/dataset-forge/manifests",
        json={
            "dataset_manifest_id": "dataset::material-request-lineage",
            "purpose": "Coder Expert child training material",
            "material_request_ref": material_request["material_request_id"],
            "sources": [
                {
                    "source_id": "radar::the-stack-v2",
                    "source_type": "web",
                    "text": "The Stack v2 material was selected through the Dataset Radar teacher material request gate.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "https://hf.co/datasets/bigcode/the-stack-v2",
                    "dataset_radar_source_id": "the-stack-v2",
                }
            ],
        },
    )
    assert response.status_code == 200
    manifest = response.json()
    assert manifest["status"] == "needs_review"
    assert manifest["material_request_ref"] == material_request["material_request_id"]
    assert manifest["dataset_radar_material_request"]["material_request_id"] == material_request["material_request_id"]
    assert manifest["dataset_radar_material_request"]["teacher_ref"] == "teacher:qwen3-coder-next"
    assert manifest["dataset_radar_gates"][0]["material_request_ref"] == material_request["material_request_id"]
    assert manifest["dataset_radar_gates"][0]["material_request_approved"] is True
    review_packet = manifest["dataset_radar_review_packets"][0]
    assert review_packet["dataset_radar_source_id"] == "the-stack-v2"
    assert review_packet["source_id"] == "radar::the-stack-v2"
    assert review_packet["source_kind"] == "canonical_source"
    assert review_packet["review_required_packet"]["dataset_id"] == "the-stack-v2"
    assert review_packet["review_required_packet"]["review_state"] == "review_required"
    assert review_packet["review_required_packet"]["training_promotion_allowed"] is False
    assert "privacy_evidence" in review_packet["review_required_packet"]["blocking_fields"]
    assert manifest["dataset_radar_training_review_gate"]["allowed"] is False
    assert manifest["dataset_radar_training_review_gate"]["blocked_source_ids"] == ["the-stack-v2"]
    assert "privacy_evidence" in manifest["dataset_radar_training_review_gate"]["blockers"][0]["blocking_fields"]
    assert "dataset_radar_material_request_gate" in manifest["required_controls"]
    assert "dataset_radar_source_review_packet" in manifest["required_controls"]
    assert "dataset_radar_training_review_gate" in manifest["required_controls"]

    summary = client.get("/ops/brain/dataset-forge").json()
    assert summary["latest_manifest"]["material_request_ref"] == material_request["material_request_id"]


def test_dataset_forge_accepts_dataset_radar_handoff_template_after_operator_excerpt(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    material_request = client.post(
        "/ops/brain/dataset-radar/material-request",
        json={
            "session_id": "dataset-forge-handoff-template",
            "operator_actor": "Teacher Council",
            "teacher_ref": "teacher:qwen3-coder-next",
            "target_node": "Coder Expert",
            "requested_split": "teacher_context",
            "allowed_use": "teacher_context",
        },
    ).json()
    handoff = material_request["dataset_forge_handoff"]
    request_body = handoff["request_body_template"]
    assert handoff["auto_execute_allowed"] is False
    assert handoff["build_allowed"] is False
    assert request_body["operator_approved"] is False

    request_body["operator_approved"] = True
    request_body["metadata"]["source"] = "test-dataset-forge-handoff-template"
    request_body["sources"][0]["text"] = (
        "Operator reviewed this teacher-context excerpt from the Dataset Radar source before building the manifest."
    )

    response = client.post("/ops/brain/dataset-forge/manifests", json=request_body)
    assert response.status_code == 200
    manifest = response.json()
    assert manifest["dataset_manifest_id"] == request_body["dataset_manifest_id"]
    assert manifest["material_request_ref"] == material_request["material_request_id"]
    assert manifest["dataset_radar_material_request"]["material_request_id"] == material_request["material_request_id"]
    assert manifest["dataset_radar_gates"][0]["requested_split"] == "teacher_context"
    assert manifest["dataset_radar_gates"][0]["allowed"] is True
    assert manifest["status"] == "ready"


def test_dataset_forge_accepts_reviewed_candidate_material_only_as_non_training_lineage(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/ops/brain/dataset-radar/refresh",
        json={
            "session_id": "dataset-forge-candidate-lineage",
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
    client.post(
        "/ops/brain/dataset-radar/candidate-review",
        json={
            "dataset_id": "example/apache-code-agent",
            "review_state": "approved_teacher_context",
            "reviewer": "operator",
            "reason": "Use as teacher context only until full provenance review completes.",
        },
    )
    material_request = client.post(
        "/ops/brain/dataset-radar/material-request",
        json={
            "session_id": "dataset-forge-candidate-lineage",
            "operator_actor": "Teacher Council",
            "teacher_ref": "teacher:qwen3-coder-next",
            "target_node": "Coder Expert",
            "requested_split": "teacher_context",
            "allowed_use": "teacher_context",
            "limit": 200,
        },
    ).json()
    assert "example/apache-code-agent" in material_request["approved_source_ids"]

    response = client.post(
        "/ops/brain/dataset-forge/manifests",
        json={
            "dataset_manifest_id": "dataset::candidate-teacher-context-lineage",
            "purpose": "Coder Expert teacher-context material",
            "material_request_ref": material_request["material_request_id"],
            "sources": [
                {
                    "source_id": "radar::example-apache-code-agent",
                    "source_type": "web",
                    "text": "Reviewed candidate material is teacher context lineage only, not direct canonical train material.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "https://hf.co/datasets/example/apache-code-agent",
                    "dataset_radar_source_id": "example/apache-code-agent",
                    "metadata": {"intended_split": "teacher_context"},
                }
            ],
        },
    )
    assert response.status_code == 200
    manifest = response.json()
    assert manifest["status"] == "ready"
    gate = manifest["dataset_radar_gates"][0]
    assert gate["source_id"] == "example/apache-code-agent"
    assert gate["requested_split"] == "teacher_context"
    assert gate["source_kind"] == "candidate"
    assert gate["candidate_material"] is True
    assert gate["training_eligible"] is False
    assert gate["material_request_approved"] is True
    assert gate["allowed"] is True
    review_packet = manifest["dataset_radar_review_packets"][0]
    assert review_packet["dataset_radar_source_id"] == "example/apache-code-agent"
    assert review_packet["source_kind"] == "candidate"
    assert review_packet["review_required_packet"]["review_state"] == "review_required"
    assert review_packet["review_required_packet"]["training_promotion_allowed"] is False
    assert "training_eligibility" in review_packet["review_required_packet"]["blocking_fields"]
    assert manifest["dataset_radar_material_request"]["requested_split"] == "teacher_context"
    assert "candidate_material_separation" in manifest["required_controls"]

    train_response = client.post(
        "/ops/brain/dataset-forge/manifests",
        json={
            "dataset_manifest_id": "dataset::candidate-train-blocked",
            "purpose": "Coder Expert candidate train material",
            "material_request_ref": material_request["material_request_id"],
            "sources": [
                {
                    "source_id": "radar::example-apache-code-agent-train",
                    "source_type": "web",
                    "text": "The same reviewed candidate cannot enter the canonical training split.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "https://hf.co/datasets/example/apache-code-agent",
                    "dataset_radar_source_id": "example/apache-code-agent",
                    "metadata": {"intended_split": "train"},
                }
            ],
        },
    )
    assert train_response.status_code == 200
    train_manifest = train_response.json()
    assert train_manifest["status"] == "blocked"
    train_gate = train_manifest["dataset_radar_gates"][0]
    assert train_gate["source_kind"] == "candidate"
    assert train_gate["requested_split"] == "train"
    assert train_gate["allowed"] is False
    assert train_gate["training_eligible"] is False
