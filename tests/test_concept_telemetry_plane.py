from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.telemetry import ConceptTelemetryRegistry, ConceptTelemetryRequest, SAEExperimentRequest
from tests.test_nexus_phase1_foundation import make_project


def test_concept_telemetry_records_behavioral_proxy_without_activation_claim():
    registry = ConceptTelemetryRegistry()

    record = registry.record_concept(
        ConceptTelemetryRequest(
            concept_id="concept::source-confidence",
            trace_refs=["trace::1"],
            labels=["source_confidence", "uncertainty"],
            concept_kind="behavioral_proxy",
            confidence=0.82,
            safety_flags=["hallucination-risk"],
            contains_private_data=False,
        )
    )

    assert record["status"] == "recorded"
    assert record["concept_kind"] == "behavioral_proxy"
    assert record["activation_claim_allowed"] is False


def test_concept_telemetry_blocks_activation_claim_without_open_model_record():
    registry = ConceptTelemetryRegistry()

    record = registry.record_concept(
        {
            "concept_id": "concept::closed-model-activation",
            "trace_refs": ["trace::closed"],
            "labels": ["deception"],
            "concept_kind": "activation_feature",
            "confidence": 0.9,
            "safety_flags": [],
            "contains_private_data": False,
        }
    )

    assert record["status"] == "blocked"
    assert "activation_features_require_sae_experiment" in {finding["rule_id"] for finding in record["findings"]}


def test_sae_experiment_records_research_only_open_model_metadata():
    registry = ConceptTelemetryRegistry()

    experiment = registry.record_sae_experiment(
        SAEExperimentRequest(
            experiment_id="sae::mistral-layer-12",
            model_id="mistral-open",
            layer="12",
            token_count=4096,
            activation_capture_method="local_forward_hooks",
            sae_config={"hidden_dim": 8192, "sparsity": 0.05},
            reconstruction_metrics={"loss": 0.12},
            feature_examples=["source confidence feature"],
            evidence_refs=["artifact::sae-run"],
        )
    )

    assert experiment["status"] == "research-only"
    assert experiment["closed_model_boundary"] == "no-closed-model-internals-from-output-only-traces"


def test_concept_telemetry_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/concept-telemetry/concepts",
        json={
            "concept_id": "concept::api",
            "trace_refs": ["trace::api"],
            "labels": ["uncertainty"],
            "concept_kind": "behavioral_proxy",
            "confidence": 0.7,
            "safety_flags": [],
            "contains_private_data": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "recorded"
    summary = client.get("/ops/brain/concept-telemetry")
    assert summary.status_code == 200
    assert summary.json()["concept_count"] == 1
