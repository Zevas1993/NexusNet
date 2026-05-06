import json

import pytest
from pydantic import ValidationError

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


def test_developmental_summaries_include_persisted_records_after_restart(tmp_path):
    simulator = DreamingSimulator(artifacts_dir=tmp_path)
    lab = CausalInterventionLab(artifacts_dir=tmp_path)
    simulation = simulator.record_simulation(
        simulation_id="sim:restart-visible",
        seed_trace_ref="trace:restart",
        scenario={"route": "planning"},
        expected_outcomes=["stable_shadow_replay"],
        evidence_refs=["trace:restart"],
    )
    intervention = lab.record_intervention(
        intervention_id="causal:restart-visible",
        variable="retrieval_source_set",
        control_value="all_sources",
        treatment_value="trusted_sources_only",
        observed_delta={"faithfulness": 0.12},
        evidence_refs=["trace:restart"],
    )

    restarted_simulator = DreamingSimulator(artifacts_dir=tmp_path)
    restarted_lab = CausalInterventionLab(artifacts_dir=tmp_path)

    simulation_summary = restarted_simulator.summary()
    intervention_summary = restarted_lab.summary()

    assert simulation_summary["simulation_count"] == 1
    assert simulation_summary["latest_simulation"]["simulation_id"] == simulation["simulation_id"]
    assert intervention_summary["intervention_count"] == 1
    assert intervention_summary["latest_intervention"]["intervention_id"] == intervention["intervention_id"]


def test_developmental_summaries_skip_invalid_disk_files_without_hiding_valid_records(tmp_path):
    simulator = DreamingSimulator(artifacts_dir=tmp_path)
    lab = CausalInterventionLab(artifacts_dir=tmp_path)
    simulation = simulator.record_simulation(
        simulation_id="sim:valid-disk",
        seed_trace_ref="trace:valid",
        scenario={},
        expected_outcomes=[],
        evidence_refs=["trace:valid"],
    )
    intervention = lab.record_intervention(
        intervention_id="causal:valid-disk",
        variable="retrieval_source_set",
        control_value="all_sources",
        treatment_value="trusted_sources_only",
        observed_delta={"faithfulness": 0.12},
        evidence_refs=["trace:valid"],
    )

    simulations_dir = tmp_path / "developmental" / "simulations"
    causal_dir = tmp_path / "developmental" / "causal-lab"
    (simulations_dir / "corrupt.json").write_text("{", encoding="utf-8")
    (simulations_dir / "non-object.json").write_text(json.dumps([]), encoding="utf-8")
    (simulations_dir / "invalid-model.json").write_text(json.dumps({"simulation_id": "missing-required"}), encoding="utf-8")
    (causal_dir / "corrupt.json").write_text("{", encoding="utf-8")
    (causal_dir / "non-object.json").write_text(json.dumps([]), encoding="utf-8")
    (causal_dir / "invalid-model.json").write_text(json.dumps({"intervention_id": "missing-required"}), encoding="utf-8")

    simulation_summary = DreamingSimulator(artifacts_dir=tmp_path).summary()
    intervention_summary = CausalInterventionLab(artifacts_dir=tmp_path).summary()

    assert simulation_summary["simulation_count"] == 1
    assert simulation_summary["latest_simulation"]["simulation_id"] == simulation["simulation_id"]
    assert intervention_summary["intervention_count"] == 1
    assert intervention_summary["latest_intervention"]["intervention_id"] == intervention["intervention_id"]


def test_causal_lab_confidence_uses_validated_numeric_string_delta(tmp_path):
    lab = CausalInterventionLab(artifacts_dir=tmp_path)

    intervention = lab.record_intervention(
        intervention_id="causal:numeric-string",
        variable="retrieval_source_set",
        control_value="all_sources",
        treatment_value="trusted_sources_only",
        observed_delta={"faithfulness": "0.12"},
        evidence_refs=["trace:numeric-string"],
    )

    assert intervention["observed_delta"] == {"faithfulness": 0.12}
    assert intervention["causal_confidence"] == "confirmed"


def test_causal_lab_rejects_non_finite_deltas_without_persisting(tmp_path):
    lab = CausalInterventionLab(artifacts_dir=tmp_path)

    with pytest.raises(ValidationError):
        lab.record_intervention(
            intervention_id="causal:non-finite",
            variable="retrieval_source_set",
            control_value="all_sources",
            treatment_value="trusted_sources_only",
            observed_delta={"faithfulness": float("nan")},
            evidence_refs=["trace:non-finite"],
        )

    assert lab.summary()["intervention_count"] == 0
    assert not any((tmp_path / "developmental" / "causal-lab").glob("*.json"))
