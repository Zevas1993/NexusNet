from nexusnet.developmental.causal_lab import CausalInterventionLab
from nexusnet.developmental.simulator import DreamingSimulator


def test_dreaming_simulator_records_deterministic_shadow_request(tmp_path):
    simulator = DreamingSimulator(artifacts_dir=tmp_path)

    result = simulator.record_simulation(
        simulation_id="sim:route-cache-off",
        seed_trace_ref="trace:abc",
        scenario={"route": "reasoning", "cache": "off"},
        expected_outcomes=["lower_cache_hit_rate", "higher_latency"],
        evidence_refs=["trace:abc", "cache-ledger:baseline"],
    )

    assert result["status"] == "shadow-recorded"
    assert result["learned_world_model_claim"] is False
    assert result["production_action_allowed"] is False


def test_causal_lab_blocks_interventions_without_evidence(tmp_path):
    lab = CausalInterventionLab(artifacts_dir=tmp_path)

    result = lab.record_intervention(
        intervention_id="causal:missing-evidence",
        variable="retrieval_source_set",
        control_value="all_sources",
        treatment_value="trusted_sources_only",
        observed_delta={"faithfulness": 0.12},
        evidence_refs=[],
    )

    assert result["status"] == "blocked"
    assert result["causal_confidence"] == "unknown"
    assert "causal_intervention_requires_evidence_refs" in result["findings"]


def test_developmental_labs_safely_persist_unsafe_ids_inside_roots(tmp_path):
    simulator = DreamingSimulator(artifacts_dir=tmp_path)
    lab = CausalInterventionLab(artifacts_dir=tmp_path)

    simulation = simulator.record_simulation(
        simulation_id="..\\escaped/sim",
        seed_trace_ref="trace:unsafe",
        scenario={},
        expected_outcomes=[],
        evidence_refs=["trace:unsafe"],
    )
    intervention = lab.record_intervention(
        intervention_id="../escaped\\causal",
        variable="retrieval_source_set",
        control_value="all_sources",
        treatment_value="trusted_sources_only",
        observed_delta={"faithfulness": 0.01},
        evidence_refs=["trace:unsafe"],
    )

    simulation_path = type(tmp_path)(simulation["artifact_path"]).resolve()
    intervention_path = type(tmp_path)(intervention["artifact_path"]).resolve()

    assert simulation_path.parent == (tmp_path / "developmental" / "simulations").resolve()
    assert intervention_path.parent == (tmp_path / "developmental" / "causal-lab").resolve()
    assert simulation_path.exists()
    assert intervention_path.exists()


def test_developmental_labs_do_not_record_phantoms_after_write_failure(tmp_path, monkeypatch):
    simulator = DreamingSimulator(artifacts_dir=tmp_path)
    lab = CausalInterventionLab(artifacts_dir=tmp_path)

    def fail_write(*args, **kwargs):
        raise OSError("simulated write failure")

    monkeypatch.setattr(type(tmp_path), "write_text", fail_write)

    try:
        simulator.record_simulation(
            simulation_id="sim:write-failure",
            seed_trace_ref="trace:failure",
            scenario={},
            expected_outcomes=[],
            evidence_refs=["trace:failure"],
        )
    except OSError:
        pass

    try:
        lab.record_intervention(
            intervention_id="causal:write-failure",
            variable="retrieval_source_set",
            control_value="all_sources",
            treatment_value="trusted_sources_only",
            observed_delta={"faithfulness": 0.12},
            evidence_refs=["trace:failure"],
        )
    except OSError:
        pass

    assert simulator.summary()["simulation_count"] == 0
    assert lab.summary()["intervention_count"] == 0
