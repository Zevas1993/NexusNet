from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.runtime.model_passport import CertificationRunRequest, EdgeModelCertificationRegistry, ModelPassportRequest
from tests.test_nexus_phase1_foundation import make_project


def test_model_passport_records_bounded_task_strengths_and_refusals():
    registry = EdgeModelCertificationRegistry()

    passport = registry.register_passport(
        ModelPassportRequest(
            model_id="LiquidAI/LFM2.5-350M",
            parameter_count=350_000_000,
            context_tokens=32768,
            runtime_formats=["onnx", "gguf"],
            memory_budget_mb=768,
            latency_envelope_ms={"p50_decode": 35.0},
            task_strengths=["structured_output", "tool_call_formatting"],
            task_refusals=["knowledge_intensive_programming", "high_stakes_factual_recall"],
            license_status="needs_review",
            provenance_refs=["https://huggingface.co/LiquidAI/LFM2.5-350M"],
        )
    )

    assert passport["status"] == "registered"
    assert passport["deployment_boundary"] == "task-certified-edge-model-not-default-brain"
    assert "knowledge_intensive_programming" in passport["task_refusals"]


def test_certification_blocks_knowledge_task_without_retrieval_support():
    registry = EdgeModelCertificationRegistry()
    registry.register_passport(
        {
            "model_id": "edge-small",
            "parameter_count": 350_000_000,
            "context_tokens": 8192,
            "runtime_formats": ["onnx"],
            "memory_budget_mb": 512,
            "latency_envelope_ms": {"p50_decode": 40.0},
            "task_strengths": ["structured_output"],
            "task_refusals": ["knowledge_intensive_programming"],
            "license_status": "approved",
            "provenance_refs": ["source::model-card"],
        }
    )

    run = registry.certify(
        CertificationRunRequest(
            run_id="cert::edge-small",
            model_id="edge-small",
            scenarios=["extraction", "tool_call_formatting", "knowledge_intensive_programming"],
            device_matrix={"desktop_cpu": {"latency_ms": 42, "memory_mb": 410}},
            benchmark_refs=["eval::edge-small"],
            retrieval_support_enabled=False,
            evidence_refs=["artifact::benchmark"],
        )
    )

    assert run["status"] == "blocked"
    assert "certification_blocks_refused_task_without_support" in {finding["rule_id"] for finding in run["findings"]}


def test_model_certification_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    passport = client.post(
        "/ops/brain/model-passports",
        json={
            "model_id": "edge-api",
            "parameter_count": 350000000,
            "context_tokens": 8192,
            "runtime_formats": ["onnx"],
            "memory_budget_mb": 512,
            "latency_envelope_ms": {"p50_decode": 45},
            "task_strengths": ["extraction"],
            "task_refusals": ["high_stakes_factual_recall"],
            "license_status": "approved",
            "provenance_refs": ["source::api"],
        },
    )
    assert passport.status_code == 200
    assert passport.json()["status"] == "registered"

    summary = client.get("/ops/brain/model-passports")
    assert summary.status_code == 200
    assert summary.json()["passport_count"] == 1
