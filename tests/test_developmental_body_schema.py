from nexusnet.developmental.contracts import AssimilationSourceLedger
from nexusnet.developmental.body_schema import NexusBodySchemaBuilder


def test_assimilation_source_ledger_counts_full_chat_packet():
    ledger = AssimilationSourceLedger.full_2026_05_06_packet()

    assert ledger.online_spec_count == 134
    assert ledger.video_spec_count == 10
    assert ledger.total_spec_count == 144
    assert ledger.status == "refs_only_until_code_backed"
    assert "consciousness_upload_claims_blocked" in ledger.boundaries
    assert "production_self_mutation_blocked" in ledger.boundaries


def test_body_schema_snapshot_marks_degraded_and_blocked_surfaces():
    builder = NexusBodySchemaBuilder()

    snapshot = builder.snapshot(
        runtime_state={"runtime_state": "live-bound", "provider_count": 3},
        memory_state={"runtime_state": "degraded", "blocked_count": 1},
        authority_state={"runtime_state": "degraded", "blocked_count": 2},
        eval_state={"runtime_state": "static-canon", "suite_count": 0},
    )

    assert snapshot["surface_id"] == "nexus-body-schema"
    assert snapshot["authority"] == "NexusBrain"
    assert snapshot["runtime_state"] == "degraded"
    assert snapshot["capability_counts"]["runtime"] == 3
    assert "memory" in snapshot["degraded_surfaces"]
    assert "authority" in snapshot["degraded_surfaces"]
    assert snapshot["production_mutation_allowed"] is False


def test_body_schema_snapshot_tolerates_malformed_counts():
    builder = NexusBodySchemaBuilder()

    snapshot = builder.snapshot(
        runtime_state={"runtime_state": "live-bound", "provider_count": "unknown"},
        memory_state={"blocked_count": "unknown", "claim_count": ""},
        authority_state={"grant_count": object()},
        eval_state={"suite_count": None},
        tool_state={"plan_count": "not-a-number"},
    )

    assert snapshot["runtime_state"] == "static-canon"
    assert snapshot["capability_counts"] == {
        "runtime": 0,
        "memory": 0,
        "authority": 0,
        "eval": 0,
        "tool": 0,
    }
    assert snapshot["degraded_surfaces"] == []
    assert snapshot["blocked_surfaces"] == []
