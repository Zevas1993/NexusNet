"""The wrapper's multi-agent orchestration: multiplex agents across nodes, replace teachers ASAP."""
from __future__ import annotations

from nexusnet.hive.wrapper_orchestrator import WrapperAgentOrchestrator, WrapperAgent


def _orch():
    o = WrapperAgentOrchestrator()
    o.register_agent(WrapperAgent("coder-agent", capabilities=["coding", "review"], max_nodes=3))
    o.register_agent(WrapperAgent("science-agent", capabilities=["physics", "math"], max_nodes=3))
    o.register_agent(WrapperAgent("generalist", capabilities=["coding", "physics", "writing"], max_nodes=5))
    return o


# --- one agent multiplexed across multiple nodes ---

def test_one_agent_serves_multiple_nodes():
    o = _orch()
    a1 = o.assign("expert.coder.1", "coding")
    a2 = o.assign("expert.coder.2", "coding")
    # least-loaded balancing spreads across the two coding-capable agents, but an agent CAN take many
    o.assign("expert.coder.3", "coding")
    o.assign("expert.coder.4", "coding")
    mp = o.multiplex_map()
    assert any(len(nodes) >= 2 for nodes in mp.values())     # at least one agent serves multiple nodes
    assert all(a in ("coder-agent", "generalist") for a in (a1, a2))


def test_multiple_agents_active_concurrently():
    o = _orch()
    o.assign("expert.coder.1", "coding")
    o.assign("expert.physicist.1", "physics")
    o.assign("expert.math.1", "math")
    assert len(o.active_agents()) >= 2                       # multiple agents running at once


def test_assign_respects_capability():
    o = _orch()
    # no agent has 'medicine' -> cannot assign
    assert o.assign("expert.medic.1", "medicine") is None
    assert o.assign("expert.coder.1", "coding") is not None


def test_multiplex_respects_capacity():
    o = WrapperAgentOrchestrator()
    o.register_agent(WrapperAgent("solo", capabilities=["x"], max_nodes=2))
    assert o.assign("n1", "x") == "solo"
    assert o.assign("n2", "x") == "solo"
    assert o.assign("n3", "x") is None                       # capacity full -> no binding


# --- replace teachers ASAP (do not hold) ---

def test_native_competence_releases_teacher_immediately():
    o = _orch()
    o.assign("expert.coder.1", "coding")
    assert "expert.coder.1" in o.status()["depending_nodes"]
    res = o.record_competence("expert.coder.1", native_score=0.82, teacher_score=0.80)
    assert res["replaced"] is True and res["released_agent"] is not None
    assert "expert.coder.1" in o.status()["native_nodes"]
    assert "expert.coder.1" not in o.status()["depending_nodes"]   # teacher dropped, now native


def test_dependency_ratio_drops_to_zero_as_natives_replace():
    o = _orch()
    nodes = ["expert.coder.1", "expert.physicist.1", "expert.math.1"]
    caps = ["coding", "physics", "math"]
    for n, c in zip(nodes, caps):
        o.assign(n, c)
    assert o.dependency_ratio() == 1.0                       # all depend on teachers initially
    for n in nodes:
        o.record_competence(n, native_score=0.9, teacher_score=0.5)   # natives surpass
    assert o.dependency_ratio() == 0.0                       # fully native = birth-ready
    assert o.status()["fully_native"] is True


def test_idle_agents_released_when_no_longer_needed():
    o = _orch()
    o.assign("expert.coder.1", "coding")
    o.record_competence("expert.coder.1", native_score=1.0, teacher_score=0.0)
    released = o.release_idle_agents()
    assert "science-agent" in released                       # never used -> dropped from pool


# --- encompass many capabilities ---

# --- routing preference: native preferred after eviction, user choice overrides ---

def test_teacher_routes_until_native_then_native_is_preferred():
    o = _orch()
    r0 = o.route("expert.coder.1", "coding")
    assert r0["source"] == "teacher_agent" and r0["preferred"] is False   # teacher serves first
    o.record_competence("expert.coder.1", native_score=0.9, teacher_score=0.5)
    r1 = o.route("expert.coder.1", "coding")
    assert r1["source"] == "native_expert" and r1["preferred"] is True     # native now preferred
    assert r1["provider"] == "native::expert.coder.1"


def test_user_choice_overrides_native_preference():
    o = _orch()
    o.record_competence("expert.coder.1", native_score=0.9, teacher_score=0.5)   # native formed
    assert o.route("expert.coder.1")["source"] == "native_expert"
    o.set_user_preference("expert.coder.1", "gpt-5.2-codex")                 # end user picks another
    r = o.route("expert.coder.1")
    assert r["source"] == "user_override" and r["provider"] == "gpt-5.2-codex"
    assert r["overrides_native"] is True
    # clearing the override reverts to the preferred native expert
    o.clear_user_preference("expert.coder.1")
    assert o.route("expert.coder.1")["source"] == "native_expert"


def test_user_override_works_even_before_native():
    o = _orch()
    o.set_user_preference("expert.physicist.1", "custom-model")
    r = o.route("expert.physicist.1", "physics")
    assert r["source"] == "user_override" and r["overrides_native"] is False


def test_unrouted_when_no_capability_no_teacher_no_native():
    o = _orch()
    assert o.route("expert.unknown.1")["source"] == "unrouted"


def test_capability_coverage_reports_gaps():
    o = _orch()
    cov = o.capability_coverage(["coding", "physics", "math", "writing", "medicine"])
    assert "medicine" in cov["missing"]
    assert set(cov["covered"]) == {"coding", "physics", "math", "writing"}
    assert 0.0 < cov["coverage"] < 1.0
    assert "review" in cov["pool_capabilities"]              # union of all agent capabilities
