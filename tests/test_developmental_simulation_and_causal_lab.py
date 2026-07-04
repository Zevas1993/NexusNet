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
