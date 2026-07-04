from types import SimpleNamespace

from nexus.schemas import utcnow
from nexusnet.hive.federated_prior_feedback import run_federated_prior_feedback_cycle


def test_federated_prior_feedback_cycle_builds_shadow_and_dream_context_without_private_content():
    selected_nodes = [
        SimpleNamespace(
            node_id="node:nexus-brain",
            node_type="NexusBrain",
            brain_scale="primary",
        ),
        SimpleNamespace(
            node_id="expert:runtime",
            node_type="Expert",
            brain_scale="expert",
        ),
    ]
    prior_updates = [
        {
            "prior_update_id": "prior-001",
            "created_at": utcnow(),
            "raw_content_included": False,
            "contains_personal_data": False,
            "route_geometry_signature": "flower-field-to-metatron-chord-sparse-selection",
            "packet_weight": 0.72,
            "mean_resonance_score": 0.8,
            "local_prior_delta": {
                "task_family": {"runtime": 0.72},
                "route_geometry": {"flower-field-to-metatron-chord-sparse-selection": 0.72},
                "node_selection": {"expert:runtime": 0.72},
                "confidence_bucket": {"medium": 0.72},
            },
        }
    ]
    request = SimpleNamespace(
        source_refs=["research::operator-note::runtime-safety"],
        memory_refs=["private-memory::Project-Caldera"],
    )

    cycle = run_federated_prior_feedback_cycle(
        prior_updates=prior_updates,
        selected_nodes=selected_nodes,
        selected_node_resonance=[
            {"node_id": "node:nexus-brain", "resonance_score": 0.5},
            {"node_id": "expert:runtime", "resonance_score": 0.7},
        ],
        dream_request=request,
        health_events=[
            {
                "health_event_id": "health-001",
                "event_state": "degraded_observed",
                "raw_content_included": False,
            }
        ],
        candidates=[
            {
                "candidate_run_id": "candidate-001",
                "lifecycle_state": "blocked",
                "blocked_reasons": ["closed_sandbox_eval_failed"],
            }
        ],
    )

    assert cycle.surface_id == "hive-federated-prior-feedback-cycle"
    assert cycle.status == "live-bound"
    assert cycle.raw_content_included is False
    assert cycle.active_production_mutated is False
    assert cycle.prior_ledger["prior_update_count"] == 1
    assert cycle.shadow_routing["prior_source"] == "FederatedPriorLedger"
    assert cycle.shadow_routing["active_route_mutated"] is False
    assert cycle.dream_context["context_contract"] == "failure-prior-research-conditioned-dreaming-v0"
    assert cycle.dream_context["consumed_prior_ledger"]["prior_update_count"] == 1
    assert cycle.dream_context["federated_prior_feedback"]["status"] == "live-bound"
    assert cycle.control_panel_status["honest_status_label"] == "prior-feedback-live-shadow-only"

    serialized = repr(cycle)
    assert "Project-Caldera" not in serialized
    assert "Private Project Caldera" not in serialized
    assert "C:\\Users\\ChrisBoyd" not in serialized
