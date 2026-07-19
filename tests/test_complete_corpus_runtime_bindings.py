from __future__ import annotations

from nexusnet.operations.assimilation_catalog import AssimilationTargetCatalog
from nexusnet.operations.corpus_runtime import CorpusAssimilationRuntime


def test_every_code_appropriate_corpus_target_has_a_live_native_binding(tmp_path):
    runtime = CorpusAssimilationRuntime(artifacts_dir=tmp_path)
    report = runtime.completeness_report()

    assert report["target_count"] == 144
    assert report["canon_excluded_target_ids"] == [
        "109-human-brain-atlas-connectome-ladder-spec",
        "110-synapse-connectome-simulation-ladder-spec",
        "111-whole-brain-emulation-boundary-spec",
        "112-organoid-intelligence-ethics-spec",
    ]
    assert report["code_appropriate_target_count"] == 140
    assert report["unbound_target_ids"] == []
    assert report["unimplemented_target_ids"] == []
    assert report["probe_failure_target_ids"] == []
    assert report["runtime_state"] == "complete-runtime-bindings"
    assert report["cluster_counts"] == {
        "1": 3,
        "2": 5,
        "3": 16,
        "4": 12,
        "5": 9,
        "6": 21,
        "7": 33,
        "8": 20,
        "9": 1,
        "10": 1,
        "11": 3,
        "12": 11,
        "13": 5,
    }


def test_catalog_exposes_runtime_binding_instead_of_research_candidate_fiction(tmp_path):
    runtime = CorpusAssimilationRuntime(artifacts_dir=tmp_path)
    catalog = AssimilationTargetCatalog(runtime=runtime)
    summary = catalog.summary()

    assert summary["implemented_count"] == 140
    assert summary["canon_excluded_count"] == 4
    assert summary["unimplemented_count"] == 0
    assert summary["runtime_state"] == "complete-runtime-bindings"
    for target in summary["targets"]:
        binding = target["runtime_binding"]
        if target["target_id"] in summary["canon_excluded_target_ids"]:
            assert binding["state"] == "canon-excluded"
            assert binding["exclusion_reason"]
        else:
            assert binding["state"] == "runtime-implemented"
            assert binding["cluster_id"] in range(1, 14)
            assert binding["implementation_refs"]
            assert binding["verified_capabilities"]
            assert binding["probe"]["passed"] is True


def test_runtime_executes_target_through_native_cluster_handler(tmp_path):
    runtime = CorpusAssimilationRuntime(artifacts_dir=tmp_path)

    workflow = runtime.execute(
        "55-workflow-engine-substrate-spec",
        payload={"nodes": ["collect", "evaluate", "publish"], "edges": [["collect", "evaluate"], ["evaluate", "publish"]]},
    )
    graph = runtime.execute(
        "05-gitnexus-codegraph-gate-spec",
        payload={"query": "runtime binding", "privacy_class": "internal"},
    )

    assert workflow["status"] == "executed"
    assert workflow["result"]["topological_order"] == ["collect", "evaluate", "publish"]
    assert graph["status"] == "executed"
    assert graph["result"]["query_passport"]["privacy_class"] == "internal"
    assert workflow["receipt_sha256"].startswith("sha256:")
    assert graph["receipt_sha256"].startswith("sha256:")
