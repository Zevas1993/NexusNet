from __future__ import annotations

from nexusnet.hive.regulation import (
    ConsequenceMemory,
    decay_step,
    anomaly_score,
    screen,
    reflect,
)


# --- consequence memory ---

def test_unseen_signature_has_zero_penalty():
    cm = ConsequenceMemory()
    assert cm.penalty_for("route-x") == 0.0
    assert cm.avoidance_signal("route-x")["avoid"] is False


def test_recording_raises_penalty_and_decay_lowers_it():
    cm = ConsequenceMemory(decay_rate=0.5)
    cm.record(signature="route-x", penalty=1.0)
    cm.record(signature="route-x", penalty=0.5)
    assert cm.penalty_for("route-x") == 1.5
    assert cm.avoidance_signal("route-x")["avoid"] is True
    cm.decay()
    assert abs(cm.penalty_for("route-x") - 0.75) < 1e-9


# --- selective memory decay ---

def test_unaccessed_memory_decays_and_prunes():
    res = decay_step(strengths={"a": 0.5, "b": 0.06}, decay_rate=0.2, prune_floor=0.05)
    assert res["strengths"]["a"] < 0.5
    assert "b" in res["pruned"]                 # 0.06 * 0.8 = 0.048 < floor


def test_accessed_memory_is_refreshed():
    res = decay_step(strengths={"a": 0.5}, accessed={"a": 0.9}, decay_rate=0.2)
    assert res["strengths"]["a"] == 0.9         # reinforcement wins over decay


# --- neural immune system ---

def test_in_distribution_not_quarantined():
    res = screen(
        candidate=[1.0, 2.0, 3.0],
        baseline_mean=[1.0, 2.0, 3.0],
        baseline_std=[1.0, 1.0, 1.0],
        z_threshold=3.0,
    )
    assert res["quarantine"] is False
    assert res["stop_signal"] is False


def test_out_of_distribution_quarantined_raises_stop_signal():
    res = screen(
        candidate=[50.0, 60.0, 70.0],
        baseline_mean=[1.0, 2.0, 3.0],
        baseline_std=[1.0, 1.0, 1.0],
        z_threshold=3.0,
    )
    assert res["quarantine"] is True
    assert res["stop_signal"] is True
    assert res["anomaly_score"] > 3.0


# --- meta reflection ---

def test_higher_error_suggests_more_deliberation():
    low = reflect(confidences=[0.8, 0.9], errors=[0.05, 0.05], max_extra_steps=8)
    high = reflect(confidences=[0.8, 0.9], errors=[0.9, 0.8], max_extra_steps=8)
    assert high["suggested_extra_deliberation"] >= low["suggested_extra_deliberation"]


def test_overconfidence_detected():
    res = reflect(confidences=[0.95, 0.97], errors=[0.6, 0.7])
    assert res["overconfident"] is True
    assert res["calibration_gap"] > 0.1
