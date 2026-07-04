from nexusnet.evals.federation import EvalFederationRegistry


def test_eval_federation_records_external_adapter_shape(tmp_path):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)

    event = registry.record_event(
        event_id="eval:browsergym:001",
        adapter="browsergym",
        target_surface="computer-use",
        candidate_ref="plan:browser-readonly",
        scores={"success": 0.8, "safety": 1.0},
        evidence_refs=["trace:browsergym-fixture"],
        held_out=True,
    )

    assert event["status"] == "recorded"
    assert event["promotion_allowed"] is True
    assert event["adapter"] == "browsergym"


def test_eval_federation_blocks_non_held_out_eval(tmp_path):
    registry = EvalFederationRegistry(artifacts_dir=tmp_path)

    event = registry.record_event(
        event_id="eval:swebench:001",
        adapter="swebench",
        target_surface="coding",
        candidate_ref="patch:demo",
        scores={"success": 1.0, "safety": 1.0},
        evidence_refs=["trace:swebench-fixture"],
        held_out=False,
    )

    assert event["status"] == "blocked"
    assert event["promotion_allowed"] is False
    assert "eval_event_requires_held_out_set" in event["findings"]
