from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.schemas import ApprovalRequest, ChatRequest, RetrievalDocumentInput, RetrievalIngestRequest, RetrievalRequest
from nexus.services import build_services


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def make_project(tmp_path: Path) -> Path:
    project_root = tmp_path / "workspace"
    (project_root / "ui").mkdir(parents=True, exist_ok=True)
    (project_root / "ui" / "index.html").write_text("<html><body>Nexus UI</body></html>", encoding="utf-8")

    _write_yaml(
        project_root / "runtime" / "config" / "inference.yaml",
        {
            "transformers": {"model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"},
            "llama_cpp": {"model_path": str(project_root / "models" / "missing.gguf")},
            "vllm": {"endpoint": None},
            "policy": {"prefer_local": True, "allow_cloud": False},
        },
    )
    _write_yaml(
        project_root / "runtime" / "config" / "engines.yaml",
        {"weights": {"latency": 0.4, "cost": 0.3, "capability": 0.25, "gpu": 0.05}},
    )
    _write_yaml(
        project_root / "runtime" / "config" / "experts.yaml",
        {
            "capsules": {
                "coder": {"enabled": True, "teachers": ["codellama/CodeLlama-7b-Python-hf"]},
                "researcher": {"enabled": True, "teachers": ["qwen/Qwen2.5-7B-Instruct"]},
                "conversationalist": {"enabled": True, "teachers": ["TinyLlama/TinyLlama-1.1B-Chat-v1.0"]},
            }
        },
    )
    _write_yaml(
        project_root / "runtime" / "config" / "router.yaml",
        {
            "default_expert": "conversationalist",
            "keyword_map": {
                "coder": ["code", "python", "traceback", "function"],
                "researcher": ["paper", "source", "citation"],
            },
        },
    )
    _write_yaml(
        project_root / "runtime" / "config" / "rag.yaml",
        {"top_k": 5, "temporal": {"enabled": False}},
    )
    _write_yaml(project_root / "runtime" / "config" / "providers.yaml", {})
    _write_yaml(project_root / "runtime" / "config" / "quant_profile.yaml", {"default": "int8"})
    _write_yaml(project_root / "runtime" / "config" / "qes_policy.yaml", {"enabled": True})
    _write_yaml(project_root / "runtime" / "config" / "settings.yaml", {"features": {"dreamer": False}})
    _write_yaml(project_root / "runtime" / "config" / "terms_of_use.yaml", {"accepted": True})
    (project_root / ".nexus.json").write_text('{"aliases":{"fast":"openai/gpt-4.1-mini"},"permissions":{"mode":"workspace-write"}}', encoding="utf-8")
    return project_root


def test_build_services_bootstraps_foundation(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    doctor = services.doctor_report()
    assert doctor["ok"] is True
    assert doctor["checks"]["database_exists"] is True
    assert len(services.model_registry.list_models()) >= 4
    assert len(services.runtime_registry.list_profiles()) >= 3


def test_retrieval_and_operator_flow_persist_trace_and_memory(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="local-doc",
                    title="RAG notes",
                    text="Nexus retrieval stores source-traceable chunks and supports optional pgvector augmentation.",
                )
            ]
        )
    )

    result = services.operator.execute_chat(
        ChatRequest(
            session_id="session-a",
            prompt="What does Nexus retrieval support?",
            use_retrieval=True,
        )
    )
    assert result.trace_id
    assert result.output
    assert result.trace.selected_expert == "researcher"
    memory = services.memory.session_view("session-a")
    assert memory["analytics"]["total_records"] >= 2
    stored_trace = services.store.get_trace(result.trace_id)
    assert stored_trace is not None


def test_governance_and_alias_routing(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    model = services.model_registry.resolve_model("fast")
    assert model.runtime_name == "openai-compatible"

    decision = services.governance.record_approval(
        ApprovalRequest(subject="runtime-promotion/mock", decision="approved", approver="architect", rationale="shadow benchmark passed")
    )
    assert decision.decision == "approved"
    events = services.governance.list_audit()
    assert any(event["action"] == "approval.recorded" for event in events)


def test_canonical_api_and_compat_routes(tmp_path: Path):
    project_root = make_project(tmp_path)
    app = create_app(str(project_root))
    client = TestClient(app)

    assert client.get("/health").status_code == 200
    assert client.get("/admin/config").status_code == 200
    ingest = client.post("/rag/ingest", json=["Nexus has a canonical operator kernel and memory system."])
    assert ingest.status_code == 200

    chat = client.post("/chat", json={"session_id": "session-b", "message": "Explain the operator kernel", "rag": True})
    assert chat.status_code == 200
    payload = chat.json()
    assert payload["ok"] is True
    assert "response" in payload
    assert payload["capsule"] in {"conversationalist", "researcher", "coder"}

    memory = client.get("/ops/memory/session-b")
    assert memory.status_code == 200
    assert memory.json()["analytics"]["total_records"] >= 2


def test_retrieval_query_endpoint_and_manifest(tmp_path: Path):
    project_root = make_project(tmp_path)
    app = create_app(str(project_root))
    client = TestClient(app)
    client.post(
        "/retrieval/ingest",
        json={
            "documents": [
                {
                    "source": "spec",
                    "title": "Phase1",
                    "text": "Nexus ships with doctor checks, permission modes, and workspace manifests.",
                }
            ]
        },
    )
    response = client.post("/retrieval/query", json=RetrievalRequest(query="doctor checks", top_k=3).model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json()["hits"]
    manifest = client.get("/ops/manifest")
    assert manifest.status_code == 200
    assert "Nexus Workspace Manifest" in manifest.text
