from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from nexus.schemas import MemoryQuery
from nexusnet.schemas import (
    BenchmarkCase,
    CurriculumAssessmentRequest,
    DistillationExportRequest,
    DreamCycleRequest,
    SessionContext,
)
from tests.test_nexus_phase1_foundation import make_project


def test_nexusnet_brain_generates_and_logs(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    result = services.brain.generate(
        session_context=SessionContext(session_id="brain-session", expert="researcher", use_retrieval=False),
        prompt="Explain NexusNet's role in one sentence.",
        model_hint="mock/default",
    )

    assert result.output
    assert result.inference_trace.log_path
    assert (project_root / "runtime" / "logs" / "startup.log").exists()
    assert (project_root / "runtime" / "logs" / "model_load.log").exists()
    assert (project_root / "runtime" / "logs" / "inference.log").exists()

    records = services.memory.query(MemoryQuery(session_id="brain-session", plane="optimization", limit=20))
    assert records


def test_nexusnet_brain_generate_feeds_native_hive_runtime_growth_without_raw_content(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    result = services.brain.generate(
        session_context=SessionContext(
            session_id="brain-heart-session",
            expert="researcher",
            task_type="runtime-heartbeat",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["runtime", "federated_learning"]},
        ),
        prompt="Private Project Caldera should not leak while the NexusBrain heart emits growth.",
        model_hint="mock/default",
    )

    summary = services.brain_hive_substrate.summary(session_id="brain-heart-session")
    receipt = summary["latest_runtime_growth_receipt"]
    packet = summary["latest_runtime_growth_packet"]
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]

    assert receipt["surface_id"] == "multi-user-runtime-growth-receipt"
    assert receipt["forward_pass_coverage"]["continuous_assimilation"] is True
    assert receipt["forward_pass_coverage"]["federated_packet"] is True
    assert receipt["raw_content_included"] is False
    assert receipt["contains_personal_data"] is False
    assert packet["surface_id"] == "multi-user-runtime-growth-federated-packet"
    assert packet["raw_content_included"] is False
    assert packet["contains_personal_data"] is False
    assert native_hive["runtime_growth_receipt_id"] == receipt["receipt_id"]
    assert native_hive["federated_packet_id"] == packet["packet_id"]
    assert native_hive["raw_content_included"] is False
    assert "Private Project Caldera" not in repr(receipt)
    assert "Private Project Caldera" not in repr(packet)


def test_nexusnet_brain_direct_forward_pass_replays_into_release_runtime_and_control_panel(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "direct-brain-forward-user"
    prompt = "Private Direct Brain Packet SECRET-DIRECT-BRAIN should stay out of release replay."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="runtime-heartbeat",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["runtime", "federated_learning"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )

    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    assert native_hive["status"] == "completed"
    assert native_hive["runtime_growth_receipt_id"]
    assert native_hive["federated_packet_id"]

    restarted_client = TestClient(create_app(str(project_root)))
    runtime = restarted_client.get(
        "/ops/wrapper/release-runtime",
        params={"session_id": session_id},
    ).json()
    visualizer = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    direct_forward = runtime["direct_nexusbrain_forward_pass"]
    assert direct_forward["surface_id"] == "direct-nexusbrain-forward-pass"
    assert direct_forward["status"] == "covered"
    assert direct_forward["runtime_state"] == "replayed-history"
    assert direct_forward["runtime_growth_receipt_id"] == native_hive["runtime_growth_receipt_id"]
    assert direct_forward["runtime_growth_federated_packet_id"] == native_hive["federated_packet_id"]
    assert direct_forward["global_growth_captured"] is True
    assert direct_forward["federated_packet_emitted"] is True
    assert direct_forward["dream_signal_emitted"] is True
    assert direct_forward["raw_content_included"] is False
    assert direct_forward["active_production_mutated"] is False

    assert runtime["federated_packet_count"] >= 1
    assert runtime["latest_federated_packet"]["raw_content_included"] is False
    assert runtime["global_growth"]["global_captures"] >= 1
    assert runtime["global_growth"]["latest_runtime_receipt"]["receipt_id"] == native_hive["runtime_growth_receipt_id"]

    control_direct = control_panel["direct_nexusbrain_forward_pass"]
    assert control_direct["status"] == "covered"
    assert control_direct["runtime_growth_receipt_id"] == native_hive["runtime_growth_receipt_id"]
    assert control_direct["runtime_growth_federated_packet_id"] == native_hive["federated_packet_id"]
    assert (
        control_panel["live_refs"]["direct_nexusbrain_forward_pass"]
        == "overlay.control_panel.direct_nexusbrain_forward_pass"
    )

    serialized = json.dumps(
        {
            "direct_forward": direct_forward,
            "control_direct": control_direct,
            "latest_federated_packet": runtime["latest_federated_packet"],
            "global_growth": runtime["global_growth"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-DIRECT-BRAIN" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_nexusnet_brain_generate_routes_blocked_native_growth_into_dream_research_bridge(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services
    prompt = "Private Project Caldera SECRET-BRAIN-NATIVE-DREAM must not leak into native growth repair."

    result = services.brain.generate(
        session_context=SessionContext(
            session_id="brain-native-dream-user",
            expert="researcher",
            task_type="runtime-heartbeat",
            use_retrieval=False,
            metadata={
                "graph_plane_tags": ["runtime", "federated_learning"],
                "native_hive_requested_actions": [
                    {
                        "action_id": "blocked-brain-native-write",
                        "action_type": "write",
                        "target_ref": "nexusnet/hive/substrate.py",
                    }
                ],
            },
        ),
        prompt=prompt,
        model_hint="mock/default",
    )

    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    bridge = native_hive["runtime_growth_dream_research"]
    assert native_hive["status"] == "blocked"
    assert bridge["surface_id"] == "native-hive-runtime-growth-dream-research-bridge"
    assert bridge["status"] == "queued"
    assert bridge["runtime_growth_receipt_id"] == native_hive["runtime_growth_receipt_id"]
    assert bridge["governance_lifecycle_status"] == "completed"
    assert bridge["governance_lifecycle_run_id"]
    assert bridge["governance_lifecycle_update_id"]
    assert bridge["governance_lifecycle_action_statuses"] == {
        "proposal": "rolled-back",
        "admin_approval": "admin-approved",
        "shadow_eval_replay": "passed-shadow",
        "sandbox_tests": "passed",
        "apply": "applied-shadow-safe-file",
        "rollback": "rolled-back",
        "readiness_runner": "completed",
    }
    assert bridge["raw_content_included"] is False

    queue = client.get("/ops/brain/self-improvement/queue").json()
    native_items = [
        item
        for item in queue["items"]
        if item["event"]["metadata"].get("native_hive_runtime_growth") is True
        and item["event"]["metadata"].get("runtime_growth_receipt_id") == native_hive["runtime_growth_receipt_id"]
    ]
    assert len(native_items) == 1
    item = native_items[0]
    assert item["status"] == "reverted"
    assert item["event"]["metadata"]["source"] == "native-hive-runtime-growth"
    assert item["event"]["metadata"]["hive_run_id"] == native_hive["hive_run_id"]
    assert item["event"]["metadata"]["raw_content_included"] is False
    assert item["event"]["safety"]["contains_private_data"] is False
    assert item["event"]["safety"]["contains_secrets"] is False

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "brain-native-dream-user"}).json()
    dream_queue = runtime["dream_research_queue"]
    assert dream_queue["latest_item"]["queue_id"] == item["queue_id"]
    assert dream_queue["latest_item"]["metadata"]["native_hive_runtime_growth"] is True
    assert dream_queue["latest_item"]["metadata"]["runtime_growth_receipt_id"] == native_hive["runtime_growth_receipt_id"]
    assert dream_queue["latest_episode"]["status"] == "researched"

    proposal = next(
        candidate
        for candidate in runtime["autonomous_updates"]["proposals"]
        if (candidate["metadata"].get("safe_payload") or {}).get("runtime_growth_receipt_id")
        == native_hive["runtime_growth_receipt_id"]
    )
    assert proposal["requested_state"] == "proposal"
    assert proposal["metadata"]["source"] == "native-hive-runtime-growth"
    assert proposal["metadata"]["active_production_mutation_allowed"] is False
    assert proposal["metadata"]["safe_payload"]["native_hive_runtime_growth"] is True
    assert proposal["metadata"]["direct_nexusbrain_generate"] is True

    runner = runtime["release_readiness_evidence_runner"]
    assert runner["latest_autonomous_update_lifecycle_status"] == "completed"
    assert runner["latest_autonomous_update_lifecycle_run_id"] == bridge["governance_lifecycle_run_id"]
    assert runner["latest_autonomous_update_lifecycle_update_id"] == bridge["governance_lifecycle_update_id"]

    native_governance = runtime["native_runtime_growth_governance"]
    assert native_governance["status"] == "rolled-back"
    assert native_governance["runtime_growth_receipt_id"] == native_hive["runtime_growth_receipt_id"]
    assert native_governance["direct_nexusbrain_generate"] is True
    assert native_governance["latest_action_statuses"] == bridge["governance_lifecycle_action_statuses"]

    serialized = json.dumps({"bridge": bridge, "queue": queue, "runtime": runtime, "proposal": proposal}, sort_keys=True)
    assert prompt not in serialized
    assert "SECRET-BRAIN-NATIVE-DREAM" not in serialized
    assert "brain-native-dream-user" not in serialized


def test_nexusnet_brain_direct_native_growth_replays_into_visualizer_after_restart(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "brain-native-replay-user"
    prompt = "Private Project Caldera SECRET-BRAIN-NATIVE-REPLAY should stay out of replay evidence."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="runtime-heartbeat",
            use_retrieval=False,
            metadata={
                "graph_plane_tags": ["runtime", "federated_learning"],
                "native_hive_requested_actions": [
                    {
                        "action_id": "blocked-direct-replay-write",
                        "action_type": "write",
                        "target_ref": "nexusnet/hive/substrate.py",
                    }
                ],
            },
        ),
        prompt=prompt,
        model_hint="mock/default",
    )

    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    bridge = native_hive["runtime_growth_dream_research"]
    assert bridge["governance_lifecycle_status"] == "completed"

    restarted_client = TestClient(create_app(str(project_root)))
    restarted_runtime = restarted_client.get(
        "/ops/wrapper/release-runtime",
        params={"session_id": session_id},
    ).json()
    restarted_governance = restarted_runtime["native_runtime_growth_governance"]
    assert restarted_governance["status"] == "rolled-back"
    assert restarted_governance["direct_nexusbrain_generate"] is True
    assert restarted_governance["latest_runner_run_id"] == bridge["governance_lifecycle_run_id"]
    assert restarted_governance["runtime_growth_receipt_id"] == native_hive["runtime_growth_receipt_id"]
    assert restarted_governance["latest_action_statuses"] == bridge["governance_lifecycle_action_statuses"]
    assert restarted_governance["raw_content_included"] is False

    visualizer = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    control_runtime = control_panel["release_wrapper_runtime"]
    visual_governance = control_runtime["native_runtime_growth_governance"]
    direct_status = control_panel["direct_nexusbrain_native_growth_governance"]
    assert visual_governance["direct_nexusbrain_generate"] is True
    assert direct_status["surface_id"] == "direct-nexusbrain-native-growth-governance"
    assert direct_status["status"] == "rolled-back"
    assert direct_status["honest_status_label"] == "direct-nexusbrain-native-growth-governance-replayed"
    assert direct_status["latest_runner_run_id"] == bridge["governance_lifecycle_run_id"]
    assert direct_status["runtime_growth_receipt_id"] == native_hive["runtime_growth_receipt_id"]
    assert direct_status["active_production_mutated"] is False
    assert direct_status["raw_content_included"] is False
    assert (
        control_panel["live_refs"]["direct_nexusbrain_native_growth_governance"]
        == "overlay.control_panel.direct_nexusbrain_native_growth_governance"
    )

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "direct NexusBrain native growth" in control_panel_js
    assert "direct_nexusbrain_generate" in control_panel_js

    serialized = json.dumps(
        {
            "restarted_governance": restarted_governance,
            "visual_governance": visual_governance,
            "direct_status": direct_status,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-BRAIN-NATIVE-REPLAY" not in serialized
    assert session_id not in serialized


def test_ops_brain_endpoint_reports_attached_models(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    response = client.get("/ops/brain")
    assert response.status_code == 200
    payload = response.json()
    assert "attached_models" in payload
    assert "mock/default" in payload["attached_models"]
    assert "inference" in payload["logs"]


def test_nexusnet_phase2_loops_produce_artifacts_and_records(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    seed_result = services.brain.generate(
        session_context=SessionContext(session_id="phase2-seed", expert="researcher", use_retrieval=False),
        prompt="Explain why NexusNet uses benchmarks and critique loops.",
        model_hint="mock/default",
    )

    reflection = services.brain_reflection.summarize(limit=10)
    assert reflection.metrics["trace_count"] >= 1

    dream = services.brain_dreaming.run_cycle(
        brain=services.brain,
        request=DreamCycleRequest(
            trace_id=seed_result.trace_id,
            model_hint="mock/default",
            variant_count=3,
            knowledge_artifact_refs=["kac://architecture_review/abc123"],
        ),
    )
    assert dream.variants
    assert dream.knowledge_artifact_refs == ["kac://architecture_review/abc123"]
    assert dream.compiled_knowledge_context["mutation_allowed"] is False
    assert dream.compiled_knowledge_context["requires_krc_runtime_context_allowed"] is True
    assert dream.compiled_knowledge_context["blocks_stale_or_quarantined_context"] is True
    assert dream.artifact_path
    assert Path(dream.artifact_path).exists()

    assessment = services.brain_curriculum.assess(
        brain=services.brain,
        request=CurriculumAssessmentRequest(phase="foundation", subject="general", model_hint="mock/default"),
    )
    assert assessment.total_courses >= 1
    transcript = services.brain_curriculum.transcript(subject="foundation:general")
    assert transcript

    export = services.brain_distillation.export(
        DistillationExportRequest(name="phase2-smoke", trace_limit=20, include_dreams=True, include_curriculum=True)
    )
    assert export.sample_count >= 1
    assert Path(export.artifact_path).exists()

    dream_records = services.memory.query(MemoryQuery(session_id=f"dream::{seed_result.trace_id}", plane="dream", limit=20))
    assert dream_records


def test_recursive_dream_engine_rejects_disallowed_kac_runtime_context(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    dream = services.brain_dreaming.run_cycle(
        brain=services.brain,
        request=DreamCycleRequest(
            seed="Try to seed a dream from blocked compiled context.",
            model_hint="mock/default",
            variant_count=3,
            knowledge_artifact_refs=["kac://architecture_review/blocked"],
            knowledge_artifact_runtime_contexts=[
                {
                    "artifact_id": "kac://architecture_review/blocked",
                    "runtime_context_allowed": False,
                    "fallback_state": "compiled_artifact_quarantined",
                }
            ],
        ),
    )

    assert dream.status == "rejected"
    assert dream.variants == []
    assert "kac_runtime_context_not_allowed" in dream.findings
    assert dream.compiled_knowledge_context["allowed"] is False
    assert dream.compiled_knowledge_context["blocked_artifact_refs"] == ["kac://architecture_review/blocked"]


def test_ops_brain_phase2_endpoints(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post("/chat", json={"session_id": "api-phase2", "message": "Explain NexusNet benchmarking.", "rag": False})

    reflection = client.get("/ops/brain/reflection")
    assert reflection.status_code == 200
    assert "metrics" in reflection.json()

    dream = client.post("/ops/brain/dream", json={"seed": "Design a stronger benchmark defense.", "model_hint": "mock/default", "variant_count": 2})
    assert dream.status_code == 200
    assert dream.json()["variants"]

    assessment = client.post("/ops/brain/curriculum/assess", json={"phase": "foundation", "subject": "general", "model_hint": "mock/default"})
    assert assessment.status_code == 200
    assert assessment.json()["total_courses"] >= 1

    transcript = client.get("/ops/brain/curriculum", params={"subject": "foundation:general"})
    assert transcript.status_code == 200
    assert transcript.json()["transcript"]

    export = client.post("/ops/brain/distill-dataset", json={"name": "api-phase2", "trace_limit": 20, "include_dreams": True, "include_curriculum": True})
    assert export.status_code == 200
    assert export.json()["sample_count"] >= 1


def test_nexusnet_benchmark_harness_records_artifacts(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    run = services.brain.run_benchmark(
        suite_name="core-smoke",
        model_hint="mock/default",
        cases=[
            BenchmarkCase(
                prompt="State that NexusNet is a wrapper brain.",
                expected_substrings=["wrapper", "runtime"],
                model_hint="mock/default",
            )
        ],
    )

    assert run.case_count == 1
    assert run.artifact_path
    assert Path(run.artifact_path).exists()
    benchmark_records = services.memory.query(MemoryQuery(session_id="benchmark::core-smoke", plane="benchmark", limit=20))
    assert benchmark_records
