from __future__ import annotations

from nexusnet.operations.ledger_runtime import AssimilationLedgerRuntime


def test_complete_ledger_is_parsed_and_all_code_entries_are_verified():
    report = AssimilationLedgerRuntime().completeness_report()

    assert report["entry_count"] == 111
    assert report["status_counts"] == {
        "candidate": 15,
        "code_backed_candidate": 1,
        "live_control_plane": 12,
        "live_substrate_implementation": 68,
        "locked_clarification": 14,
        "research_only": 1,
    }
    assert report["code_appropriate_entry_count"] == 96
    assert report["implemented_candidate_count"] == 16
    assert report["unimplemented_candidate_entry_ids"] == []
    assert report["live_entry_missing_code_refs"] == []
    assert report["missing_evidence_paths"] == []
    assert report["runtime_state"] == "complete-ledger-runtime-evidence"


def test_ledger_candidates_resolve_to_real_callable_implementations():
    runtime = AssimilationLedgerRuntime()
    report = runtime.completeness_report()

    candidate_ids = {
        entry_id
        for entry_id, entry in report["entries"].items()
        if entry["ledger_status"] in {"candidate", "code_backed_candidate"}
    }
    assert len(candidate_ids) == 16
    for entry_id in candidate_ids:
        binding = report["entries"][entry_id]["runtime_binding"]
        assert binding["state"] == "runtime-implemented"
        assert binding["implementation_refs"]
        assert binding["probe"]["passed"] is True
