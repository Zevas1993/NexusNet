from nexusnet.runtime.decision_ledger import RuntimeDecisionLedger


def test_runtime_decision_ledger_combines_route_cache_quantization_and_eval(tmp_path):
    ledger = RuntimeDecisionLedger(artifacts_dir=tmp_path)

    record = ledger.record(
        decision_id="runtime:decision:001",
        route_decision={"status": "routed-shadow", "provider": {"provider_id": "local"}, "estimated_cost_usd": 0.0},
        cache_state={"status": "measured", "promotion_allowed": True},
        quantization_state={"status": "recommended", "promotion_blockers": []},
        eval_state={"promotion_allowed": True},
        evidence_refs=["route:001", "cache:001", "eval:001"],
    )

    assert record["status"] == "ready-shadow"
    assert record["promotion_allowed"] is True
    assert record["estimated_cost_usd"] == 0.0


def test_runtime_decision_ledger_blocks_missing_eval(tmp_path):
    ledger = RuntimeDecisionLedger(artifacts_dir=tmp_path)

    record = ledger.record(
        decision_id="runtime:decision:002",
        route_decision={"status": "routed-shadow"},
        cache_state={"status": "measured", "promotion_allowed": True},
        quantization_state={"status": "recommended", "promotion_blockers": []},
        eval_state={"promotion_allowed": False},
        evidence_refs=["route:002"],
    )

    assert record["status"] == "blocked"
    assert "runtime_decision_eval_gate_not_clear" in record["findings"]
