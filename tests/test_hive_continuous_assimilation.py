"""Continuous Ivy-League assimilation: learn from wrapped models during usage -> train at threshold."""
from __future__ import annotations

from nexusnet.hive.continuous_assimilation import ContinuousAssimilationLoop, AssimilationRecord
from nexusnet.hive.multi_user_growth import MultiUserGrowthCoordinator


def test_assimilate_tags_provenance_by_source_model():
    loop = ContinuousAssimilationLoop(train_threshold=3)
    rec = loop.assimilate(source_model="gpt-5.2", expert_node="expert.coder",
                          task="patch", quality=0.9, knowledge_ref="ref://1")
    assert isinstance(rec, AssimilationRecord)
    assert rec.source_model == "gpt-5.2" and rec.expert_node == "expert.coder"
    assert loop.source_models("expert.coder") == ["gpt-5.2"]    # provenance tagged


def test_distinct_source_models_drive_the_count_not_raw_captures():
    loop = ContinuousAssimilationLoop(train_threshold=3)
    # many captures from the SAME model count as one assimilated source
    for _ in range(5):
        loop.assimilate(source_model="claude-opus", expert_node="expert.writer")
    assert loop.captures("expert.writer") == 5
    assert loop.assimilation_count("expert.writer") == 1
    assert loop.ready_to_train("expert.writer") is False


def test_node_becomes_training_ready_at_threshold():
    loop = ContinuousAssimilationLoop(train_threshold=3)
    for m in ("gpt-5.2", "claude-opus", "qwen3"):
        loop.assimilate(source_model=m, expert_node="expert.coder", quality=0.8)
    assert loop.assimilation_count("expert.coder") == 3
    assert loop.ready_to_train("expert.coder") is True
    assert "expert.coder" in loop.training_ready_nodes()


def test_training_is_continuous_not_one_time():
    loop = ContinuousAssimilationLoop(train_threshold=2)
    for m in ("a", "b"):
        loop.assimilate(source_model=m, expert_node="expert.x")
    assert loop.ready_to_train("expert.x") is True
    consumed = loop.mark_trained("expert.x")                    # trainer consumes the bank
    assert consumed["round"] == 1 and set(consumed["assimilated_sources"]) == {"a", "b"}
    assert loop.ready_to_train("expert.x") is False             # bank reset after training
    # ... and assimilation keeps going -> can train AGAIN (continuous Ivy-League)
    for m in ("c", "d"):
        loop.assimilate(source_model=m, expert_node="expert.x")
    assert loop.ready_to_train("expert.x") is True
    assert loop.mark_trained("expert.x")["round"] == 2


def test_replace_target_is_top_model_for_domain():
    loop = ContinuousAssimilationLoop()
    loop.assimilate(source_model="qwen3-coder", expert_node="expert.coder")
    leaderboard = {"expert.coder": "gpt-5.2-codex"}
    tgt = loop.replace_target("expert.coder", leaderboard)
    assert tgt["replace_target_model"] == "gpt-5.2-codex"
    assert tgt["already_assimilated"] is False                  # haven't assimilated the top model yet


def test_provenance_and_status_report():
    loop = ContinuousAssimilationLoop(train_threshold=2)
    loop.assimilate(source_model="gpt-5.2", expert_node="expert.coder", quality=1.0)
    loop.assimilate(source_model="gpt-5.2", expert_node="expert.coder", quality=0.5)
    loop.assimilate(source_model="claude", expert_node="expert.coder", quality=0.8)
    prov = {p["source_model"]: p for p in loop.provenance("expert.coder")}
    assert prov["gpt-5.2"]["captures"] == 2 and prov["gpt-5.2"]["mean_quality"] == 0.75
    st = loop.status()
    assert st["continuous"] is True
    assert st["nodes"]["expert.coder"]["distinct_sources"] == 2
    assert st["nodes"]["expert.coder"]["ready_to_train"] is True


def test_multi_user_growth_records_sanitized_runtime_interaction_receipts():
    growth = MultiUserGrowthCoordinator(global_train_threshold=2, federate_min_users=2, dream_every=2)

    first = growth.record_runtime_interaction(
        "raw-user-alpha",
        source_model="local-llama",
        expert_node="expert.coder",
        task_family="coding",
        route_geometry="sparse-coder-route",
        selected_node_ids=["CodingAO", "CritiqueAO"],
        confidence=0.83,
        eval_scores={"quality": 0.91, "safety": 0.96},
        failure_class="",
        policy_block_class="",
        runtime_class="desktop-gpu",
        hardware_class="consumer-gpu",
        sandbox_result="shadow-pass",
        dream_candidate_outcome="not-requested",
        quality=0.91,
        knowledge_ref="trace::safe-code-ref",
        metadata={
            "prompt": "private prompt must not persist",
            "raw_output": "private output must not persist",
            "local_path": "F:\\private\\secret.txt",
            "trace_ref": "trace::safe-code-ref",
        },
    )
    second = growth.record_runtime_interaction(
        "raw-user-beta",
        source_model="api-gpt",
        expert_node="expert.coder",
        task_family="coding",
        route_geometry="sparse-coder-route",
        selected_node_ids=["CodingAO", "CritiqueAO"],
        confidence=0.87,
        eval_scores={"quality": 0.93, "safety": 0.95},
        runtime_class="api",
        hardware_class="remote",
        sandbox_result="shadow-pass",
        dream_candidate_outcome="candidate-proposed",
        quality=0.93,
        knowledge_ref="trace::safe-code-ref-2",
    )

    assert first["surface_id"] == "multi-user-runtime-growth-receipt"
    assert first["raw_content_included"] is False
    assert first["contains_personal_data"] is False
    assert first["active_production_mutation_allowed"] is False
    assert first["privacy_boundary"].startswith("sanitized")
    assert first["user_ref"] != "raw-user-alpha"
    assert first["forward_pass_coverage"] == {
        "continuous_assimilation": True,
        "per_user_growth": True,
        "global_growth": True,
        "federated_packet": True,
        "dream_signal": True,
    }
    assert first["federated_packet"]["raw_content_included"] is False
    assert first["federated_packet"]["contains_personal_data"] is False
    assert first["federated_packet"]["selected_node_roles"] == ["CodingAO", "CritiqueAO"]
    assert first["federated_packet"]["confidence_bucket"] == "high"

    serialized = repr(first)
    assert "private prompt must not persist" not in serialized
    assert "private output must not persist" not in serialized
    assert "F:\\private\\secret.txt" not in serialized
    assert "raw-user-alpha" not in serialized

    assert second["global_growth"]["federation_ready"] is True
    assert second["global_growth"]["training_ready_nodes"] == ["expert.coder"]
    assert second["global_growth"]["dream_due"] is True
    status = growth.growth_status()
    assert status["runtime_interaction_count"] == 2
    assert status["latest_runtime_receipt"]["receipt_id"] == second["receipt_id"]
    assert status["latest_runtime_receipt"]["federated_packet"]["packet_id"] == second["federated_packet"]["packet_id"]
    assert status["latest_runtime_receipt"]["raw_content_included"] is False


def test_multi_user_growth_rehydrates_sanitized_runtime_receipts_idempotently():
    growth = MultiUserGrowthCoordinator(global_train_threshold=2, federate_min_users=2, dream_every=2)
    first = growth.record_runtime_interaction(
        "raw-user-alpha",
        source_model="local-llama",
        expert_node="expert.coder",
        task_family="coding",
        route_geometry="CodingAO|CritiqueAO",
        selected_node_ids=["CodingAO", "CritiqueAO"],
        confidence=0.83,
        knowledge_ref="trace::safe-code-ref",
    )
    second = growth.record_runtime_interaction(
        "raw-user-beta",
        source_model="api-gpt",
        expert_node="expert.coder",
        task_family="coding",
        route_geometry="CodingAO|CritiqueAO",
        selected_node_ids=["CodingAO", "CritiqueAO"],
        confidence=0.87,
        knowledge_ref="trace::safe-code-ref-2",
    )

    restored = MultiUserGrowthCoordinator(global_train_threshold=2, federate_min_users=2, dream_every=2)
    rehydration = restored.restore_runtime_receipts([second, first])

    assert rehydration["surface_id"] == "multi-user-runtime-growth-rehydration"
    assert rehydration["restored_receipts"] == 2
    assert rehydration["raw_content_included"] is False
    status = restored.growth_status()
    assert status["runtime_interaction_count"] == 2
    assert status["runtime_receipt_count"] == 2
    assert status["global_captures"] == 2
    assert status["users"] == 2
    assert status["latest_runtime_receipt"]["receipt_id"] == second["receipt_id"]
    assert status["latest_runtime_receipt"]["raw_content_included"] is False
    assert restored.global_ready_to_train("expert.coder") is True
    assert restored.federation_ready() is True

    duplicate = restored.restore_runtime_receipts([second, first])
    assert duplicate["restored_receipts"] == 0
    assert restored.growth_status()["runtime_interaction_count"] == 2

    unsafe = dict(second)
    unsafe["receipt_id"] = "runtime-growth::unsafe"
    unsafe["raw_content_included"] = True
    rejected = restored.restore_runtime_receipts([unsafe])
    assert rejected["restored_receipts"] == 0
    assert rejected["skipped_receipts"] == 1
    assert "raw-user-alpha" not in repr(restored.growth_status())


def test_multi_user_growth_passivates_runtime_captures_for_readiness_and_replay():
    growth = MultiUserGrowthCoordinator(global_train_threshold=2, federate_min_users=2, dream_every=2)
    first = growth.record_runtime_interaction(
        "raw-user-alpha",
        source_model="local-llama",
        expert_node="expert.coder",
        task_family="coding",
        route_geometry="CodingAO|CritiqueAO",
        selected_node_ids=["CodingAO", "CritiqueAO"],
        confidence=0.83,
        knowledge_ref="trace::safe-code-ref",
    )
    second = growth.record_runtime_interaction(
        "raw-user-beta",
        source_model="api-gpt",
        expert_node="expert.coder",
        task_family="coding",
        route_geometry="CodingAO|CritiqueAO",
        selected_node_ids=["CodingAO", "CritiqueAO"],
        confidence=0.87,
        knowledge_ref="trace::safe-code-ref-2",
    )
    assert growth.global_ready_to_train("expert.coder") is True
    assert growth.federation_ready() is True

    passivation = growth.passivate_runtime_captures(
        [
            {
                "source_ref": f"federated-packet::{first['federated_packet']['packet_id']}",
                "packet_id": first["federated_packet"]["packet_id"],
                "status": "inactive-retention-passivated",
            }
        ],
        reason_ref="privacy-retention-enforcement::revoked-personal-data",
        session_ref_digest="session-ref-digest",
    )

    assert passivation["surface_id"] == "multi-user-runtime-growth-passivation"
    assert passivation["status"] == "passivated"
    assert passivation["passivated_capture_count"] == 1
    assert passivation["raw_content_included"] is False
    assert passivation["contains_personal_data"] is False
    assert passivation["active_production_mutation_allowed"] is False

    status = growth.growth_status()
    assert status["global_captures"] == 2
    assert status["active_global_captures"] == 1
    assert status["passivated_global_captures"] == 1
    assert status["global_sources_per_node"]["expert.coder"] == 1
    assert status["training_ready_nodes"] == []
    assert status["federation_ready"] is False
    assert status["native_privacy_passivation"]["latest_record_id"] == passivation["record_id"]
    assert status["native_privacy_passivation"]["inactive_capture_count"] == 1

    restored = MultiUserGrowthCoordinator(global_train_threshold=2, federate_min_users=2, dream_every=2)
    restored.restore_runtime_receipts([second, first])
    replay = restored.restore_passivation_records([passivation])
    replayed_status = restored.growth_status()

    assert replay["surface_id"] == "multi-user-runtime-growth-passivation-replay"
    assert replay["restored_passivation_records"] == 1
    assert replayed_status["active_global_captures"] == 1
    assert replayed_status["passivated_global_captures"] == 1
    assert replayed_status["training_ready_nodes"] == []
    assert replayed_status["federation_ready"] is False

    duplicate = restored.restore_passivation_records([passivation])
    assert duplicate["restored_passivation_records"] == 0
    assert restored.growth_status()["passivated_global_captures"] == 1

    serialized = repr({"passivation": passivation, "status": status, "replay": replay})
    assert "raw-user-alpha" not in serialized
    assert "raw-user-beta" not in serialized
    assert "session-ref-digest" in serialized
