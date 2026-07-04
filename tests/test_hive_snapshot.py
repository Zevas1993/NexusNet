from __future__ import annotations

from nexusnet.hive.hive_snapshot import hive_evidence_snapshot


def test_snapshot_composes_all_layers():
    snap = hive_evidence_snapshot()
    assert set(snap["layers"].keys()) == {
        "neural_core", "collective", "memory", "regulation", "dreaming", "fabric"
    }
    # the fabric layer is the connected organism: every node reachable, signal reaches the experts
    fab = snap["layers"]["fabric"]
    assert fab["connectivity"]["fully_connected"] is True
    assert fab["reached_experts"] is True
    assert fab["sparse_activation"] is True


def test_snapshot_is_fully_shadow_gated():
    snap = hive_evidence_snapshot()
    assert snap["all_layers_shadow_gated"] is True
    assert snap["production_mutation_allowed"] is False
    assert snap["native_weight_training"] is False


def test_snapshot_is_deterministic():
    a = hive_evidence_snapshot(token_values=[0.2, 0.4, -0.1, 0.3, 0.5, -0.2, 0.1, 0.0], position=3)
    b = hive_evidence_snapshot(token_values=[0.2, 0.4, -0.1, 0.3, 0.5, -0.2, 0.1, 0.0], position=3)
    assert a["layers"]["neural_core"]["forward"]["output"] == b["layers"]["neural_core"]["forward"]["output"]


def test_snapshot_neural_core_finite_and_dreaming_observe_only():
    snap = hive_evidence_snapshot()
    assert snap["layers"]["neural_core"]["forward"]["output_finite"] is True
    assert snap["layers"]["dreaming"]["observe_only"] is True
    assert snap["layers"]["dreaming"]["promotable_candidate"] is False
