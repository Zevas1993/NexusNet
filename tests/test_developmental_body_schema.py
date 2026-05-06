from nexusnet.developmental.contracts import AssimilationSourceLedger


def test_assimilation_source_ledger_counts_full_chat_packet():
    ledger = AssimilationSourceLedger.full_2026_05_06_packet()

    assert ledger.online_spec_count == 134
    assert ledger.video_spec_count == 10
    assert ledger.total_spec_count == 144
    assert ledger.status == "refs_only_until_code_backed"
    assert "consciousness_upload_claims_blocked" in ledger.boundaries
    assert "production_self_mutation_blocked" in ledger.boundaries
