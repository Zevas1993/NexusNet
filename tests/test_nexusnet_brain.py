from __future__ import annotations

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
        request=DreamCycleRequest(trace_id=seed_result.trace_id, model_hint="mock/default", variant_count=3),
    )
    assert dream.variants
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
