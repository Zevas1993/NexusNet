from __future__ import annotations

from nexusnet.operations.complete_assimilation import CompleteAssimilationRuntime
from nexusnet.operations.assimilation_catalog import AssimilationTargetCatalog


def test_complete_runtime_reconciles_corpus_ledger_and_native_clusters(tmp_path):
    report = CompleteAssimilationRuntime(artifacts_dir=tmp_path).completeness_report()

    assert report["consolidated_source_count"] == 195
    assert report["numbered_target_count"] == 144
    assert report["ledger_entry_count"] == 111
    assert report["native_cluster_count"] == 13
    assert report["code_appropriate_numbered_target_count"] == 140
    assert report["implemented_numbered_target_count"] == 140
    assert report["implemented_ledger_candidate_count"] == 16
    assert report["missing_source_paths"] == []
    assert report["unbound_numbered_source_ids"] == []
    assert report["unimplemented_numbered_target_ids"] == []
    assert report["unimplemented_ledger_entry_ids"] == []
    assert report["overall_runtime_state"] == "complete-assimilation-runtime-evidence"


def test_all_195_sources_have_a_runtime_or_governance_route(tmp_path):
    report = CompleteAssimilationRuntime(artifacts_dir=tmp_path).completeness_report()

    assert len(report["sources"]) == 195
    assert all(source["route"] in {"numbered-runtime-target", "governance-or-evidence-source"} for source in report["sources"])
    assert sum(source["route"] == "numbered-runtime-target" for source in report["sources"]) == 144
    assert sum(source["route"] == "governance-or-evidence-source" for source in report["sources"]) == 51


def test_live_catalog_surfaces_full_corpus_and_ledger_completion():
    summary = AssimilationTargetCatalog().summary(limit=1)

    assert summary["complete_assimilation"]["consolidated_source_count"] == 195
    assert summary["complete_assimilation"]["ledger_entry_count"] == 111
    assert summary["complete_assimilation"]["overall_runtime_state"] == "complete-assimilation-runtime-evidence"
    assert summary["complete_assimilation"]["unimplemented_target_ids"] == []
