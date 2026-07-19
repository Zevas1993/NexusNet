from __future__ import annotations

import math

import pytest

from nexus.runtimes.registry import LlamaCppRuntimeAdapter, TransformersRuntimeAdapter
from nexusnet.developmental.global_workspace import GlobalWorkspaceRouter
from nexusnet.developmental.kernel import DevelopmentalCortexKernel
from nexusnet.developmental.semantic_pointers import SemanticPointerMemory


def test_global_workspace_ignites_bounded_evidence_backed_broadcast() -> None:
    router = GlobalWorkspaceRouter(capacity=2, ignition_threshold=0.55)

    result = router.ignite(
        workspace_id="workspace:test",
        candidates=[
            {
                "candidate_id": "goal",
                "content_ref": "task:goal",
                "goal_relevance": 0.9,
                "salience": 0.8,
                "evidence_refs": ["trace:goal"],
            },
            {
                "candidate_id": "failure",
                "content_ref": "eval:failure",
                "eval_failure": 1.0,
                "anomaly": 0.8,
                "evidence_refs": ["eval:001"],
            },
            {
                "candidate_id": "noise",
                "content_ref": "trace:noise",
                "salience": 0.1,
                "evidence_refs": ["trace:noise"],
            },
        ],
    )

    assert result["status"] == "broadcast"
    assert result["broadcast_count"] == 2
    assert {item["candidate_id"] for item in result["broadcast"]} == {"goal", "failure"}
    assert result["production_mutation_allowed"] is False
    assert all(item["evidence_refs"] for item in result["broadcast"])


def test_semantic_pointer_binding_round_trip_and_contradiction_detection() -> None:
    memory = SemanticPointerMemory(dimensions=512)
    subject = memory.pointer("subject:nexusnet")
    relation = memory.pointer("relation:owns")
    value = memory.pointer("value:routing")

    bound = memory.bind_many(subject, relation, value)
    recovered = memory.unbind(memory.unbind(bound, subject), relation)

    assert memory.similarity(recovered, value) > 0.99
    contradiction = memory.compare_claims(
        claim_a={"subject": "nexusnet", "predicate": "route-live", "object": "yes"},
        claim_b={"subject": "nexusnet", "predicate": "route-live", "object": "no"},
        evidence_refs=["health:a", "health:b"],
    )
    assert contradiction["contradiction"] is True
    assert contradiction["evidence_refs"] == ["health:a", "health:b"]


def test_developmental_cortex_executes_workspace_and_semantic_memory_mechanisms(tmp_path) -> None:
    kernel = DevelopmentalCortexKernel(artifacts_dir=tmp_path)

    result = kernel.assess(
        request_id="dev:corpus:001",
        task_ref="task:implement-corpus",
        trace_refs=["trace:001"],
        evidence_refs=["evidence:001"],
        runtime_state={"available": 2},
        memory_state={"healthy": 1},
        authority_state={"allowed": 1},
        eval_state={"passed": 1},
    )

    assert result["global_workspace"]["status"] == "broadcast"
    assert result["semantic_memory"]["binding_id"].startswith("semantic:")
    assert result["semantic_memory"]["dimensions"] >= 256
    assert result["production_mutation_allowed"] is False


def test_local_runtime_adapters_fail_closed_without_stub_output(tmp_path) -> None:
    missing = tmp_path / "missing.gguf"
    llama = LlamaCppRuntimeAdapter({"model_path": str(missing)})
    health = llama.health()

    assert health["available"] is False
    assert health["mode"] == "missing-model"
    with pytest.raises(FileNotFoundError):
        llama.generate(prompt="hello", messages=[], model_id="local/missing")

    transformers = TransformersRuntimeAdapter({})
    health = transformers.health()
    assert health["available"] is False
    assert health["mode"] == "unconfigured"
    with pytest.raises(RuntimeError, match="model_id"):
        transformers.generate(prompt="hello", messages=[], model_id="")


def test_semantic_pointer_vectors_are_finite_and_normalized() -> None:
    memory = SemanticPointerMemory(dimensions=256)
    vector = memory.pointer("finite")
    norm = math.sqrt(sum(value * value for value in vector))
    assert all(math.isfinite(value) for value in vector)
    assert norm == pytest.approx(1.0)
