from types import SimpleNamespace

from nexus.schemas import utcnow
from nexusnet.hive.multi_user_growth import MultiUserGrowthCoordinator
from nexusnet.hive.runtime_growth_federation import run_runtime_growth_federation_cycle


def test_runtime_growth_federation_cycle_emits_sanitized_packet_prior_and_growth_receipt():
    growth = MultiUserGrowthCoordinator(global_train_threshold=2, federate_min_users=1, dream_every=1)
    request = SimpleNamespace(
        session_id="private-growth-session",
        task_id="private-growth-task",
        intent="Private Project Caldera local cache route on C:\\Users\\ChrisBoyd\\secret.txt",
        requested_capabilities=["planning", "runtime", "federated learning"],
        requested_actions=[
            {
                "action_id": "inspect-private-path",
                "action_type": "read",
                "target_ref": "C:\\Users\\ChrisBoyd\\secret.txt",
            }
        ],
        memory_refs=["private-memory::Project-Caldera"],
        privacy_class="confidential",
    )
    selected_nodes = [
        SimpleNamespace(
            node_id="node:nexus-brain",
            node_type="NexusBrain",
            brain_scale="primary",
            capabilities=["planning", "runtime"],
            brain_instance_ref="brain:nexus",
        ),
        SimpleNamespace(
            node_id="expert:runtime",
            node_type="Expert",
            brain_scale="expert",
            capabilities=["runtime", "federated learning"],
            brain_instance_ref="brain:expert-runtime",
        ),
    ]
    loops = [{"confidence": 0.82, "exit_reason": "completed"}]

    cycle = run_runtime_growth_federation_cycle(
        run_id="private-run-001",
        session_id=request.session_id,
        task_id=request.task_id,
        created_at=utcnow(),
        request=request,
        selected_nodes=selected_nodes,
        selected_node_resonance=[{"node_id": "expert:runtime", "resonance_score": 0.9}],
        loops=loops,
        blocked=False,
        requested_caps=["runtime", "planning"],
        previous_prior_updates=[],
        global_growth=growth,
    )

    packet = cycle.federated_learning_packet
    prior_update = cycle.federated_prior_update
    receipt = cycle.runtime_growth_receipt
    runtime_packet = cycle.runtime_growth_packet

    assert cycle.surface_id == "hive-runtime-growth-federation-cycle"
    assert cycle.raw_content_included is False
    assert cycle.active_production_mutated is False
    assert cycle.selected_node_ids == ["node:nexus-brain", "expert:runtime"]
    assert cycle.expert_node == "expert:runtime"

    assert packet["contract_ref"] == "mandatory-sanitized-federated-learning-v0"
    assert packet["raw_content_included"] is False
    assert packet["contains_personal_data"] is False
    assert packet["security_envelope"]["signed_packet"]["signature"].startswith("hive_sig_")

    assert prior_update["source_packet_id"] == packet["packet_id"]
    assert prior_update["sequence_index"] == 1
    assert prior_update["raw_content_included"] is False
    assert prior_update["contains_personal_data"] is False

    assert receipt["surface_id"] == "multi-user-runtime-growth-receipt"
    assert receipt["forward_pass_coverage"]["continuous_assimilation"] is True
    assert receipt["forward_pass_coverage"]["global_growth"] is True
    assert receipt["raw_content_included"] is False
    assert receipt["contains_personal_data"] is False
    assert runtime_packet["surface_id"] == "multi-user-runtime-growth-federated-packet"
    assert cycle.runtime_growth_status["runtime_interaction_count"] == 1

    serialized = repr({"packet": packet, "prior": prior_update, "receipt": receipt})
    assert "Private Project Caldera" not in serialized
    assert "Project-Caldera" not in serialized
    assert "secret.txt" not in serialized
    assert "C:\\Users\\ChrisBoyd" not in serialized
