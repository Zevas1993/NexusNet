"""Capstone completion: full_birth composes every lane; MCP/computer-use connective helpers."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import full_birth
from nexusnet.protocols import (
    MCPClient, InProcessMCPServer, ProtocolTrustRegistry, ProtocolAdapterRequest,
    consent_gate_from_trust,
)
from nexusnet.vision.screen_parse import perceive_screen


# --- capstone: the whole womb process composed ---

def test_full_birth_composes_evolution_birth_dream_promotion(tmp_path):
    report = full_birth(
        ["philosopher", "physicist"],
        evolve=True, dream_self_improve=True, export=True, out_dir=str(tmp_path / "born"),
        epochs=18, seq_len=16, n_sentences=120, dream_cycles=1,
        evo_population=3, evo_generations=2,
        teacher_baselines={"philosopher": 0.2, "physicist": 0.2}, seed=0,
    )
    # 1) meta-evolution actually ran and chose a config
    assert report["evolution"] is not None and report["config_used"] is not None
    assert report["evolution"]["improved"] is True
    # 2) every expert was born and learned
    assert set(report["experts"]) == {"philosopher", "physicist"}
    for k in report["experts"]:
        m = report["experts"][k]["metrics"]
        assert m["final_loss"] < m["initial_loss"]
        # 3) recursive dream self-improvement ran (cycles accounted)
        d = report["experts"][k]["recursive_dream"]
        assert d is not None and d["applied"] + d["vetoed"] + d["rolled_back"] == 1
    # 4) hive TRP promotion decided over all expert nodes
    assert set(report["promotions"]["nodes"]) == {"expert.philosopher", "expert.physicist"}
    # 5) the best born expert was exported as a real artifact
    assert report["best_expert"] in ("philosopher", "physicist")
    assert "safetensors" in report["export"]["written"]


def test_full_birth_actually_invokes_assimilation_and_attach():
    # proves the previously-island mechanisms (Aspect 2 assimilation, Aspect 1 LoRA attach) are
    # really called inside the live pipeline - not standalone modules sitting beside it.
    report = full_birth(["coder"], evolve=False, dream_self_improve=False, export=False,
                        assimilate_extra_expert=True, attach_adapters=True,
                        epochs=12, seq_len=14, n_sentences=90, seed=0)
    ex = report["experts"]["coder"]
    # expert assimilation grew the MoE by a real grafted capsule
    assert ex["assimilation"] is not None
    assert ex["assimilation"]["num_experts"] == ex["assimilation"]["grew_from"] + 1
    assert ex["assimilation"]["existing_experts_preserved"] is True
    # brain-first attach injected real LoRA adapters and froze the base
    assert ex["adapters"] is not None
    assert ex["adapters"]["injected_count"] >= 1 and ex["adapters"]["base_frozen"] is True
    assert report["lanes"]["assimilate_extra_expert"] is True
    assert report["lanes"]["attach_adapters"] is True


def test_full_birth_runs_autonomous_efficiency_improvement():
    # the efficiency autopilot (bit-model/quant search) is part of the live birth self-improvement
    report = full_birth(["coder"], evolve=False, dream_self_improve=False, export=False,
                        improve_efficiency=True, epochs=10, seq_len=14, n_sentences=80, seed=0)
    assert report["lanes"]["improve_efficiency"] is True
    eff = report["experts"]["coder"]["efficiency"]
    assert eff is not None
    assert eff["final_compression_vs_fp16"] > 1.0        # found a real efficiency gain
    assert eff["efficiency_monotonic"] is True
    assert eff["best_bit_model"]["max_error"] <= 0.08    # quality-gated
    # the report also attests the best model's wrapper absorption
    assert report["wrapper_absorption"]["wrapper_fully_absorbed"] is True


def test_full_birth_lanes_can_be_disabled():
    report = full_birth(["coder"], evolve=False, dream_self_improve=False, export=False,
                        improve_efficiency=False, epochs=15, seq_len=14, n_sentences=100, seed=0)
    assert report["evolution"] is None
    assert report["experts"]["coder"]["recursive_dream"] is None
    assert report["export"] is None and report["efficiency"] is None
    assert report["experts"]["coder"]["metrics"]["final_loss"] < \
        report["experts"]["coder"]["metrics"]["initial_loss"]


# --- connective helper: MCP consent gate driven by the trust registry ---

def test_mcp_consent_gate_from_trust_registry():
    reg = ProtocolTrustRegistry()
    rec = reg.register(ProtocolAdapterRequest(
        adapter_id="mcp1", protocol="MCP", endpoint="inproc://x", enabled=True,
        identity_ref="id://1", consent_ref="c://1", permissions=["tools:echo"],
        revocation_ref="rev://1", sandboxed=True))
    gate = consent_gate_from_trust(rec)
    server = InProcessMCPServer()
    server.register_tool("echo", lambda a: a.get("text", ""))
    server.register_tool("delete", lambda a: "deleted")
    client = MCPClient(server, consent_gate=gate)
    client.initialize()
    assert client.call_tool("echo", {"text": "hi"})["content"][0]["text"] == "hi"  # permitted
    with pytest.raises(PermissionError):
        client.call_tool("delete")                                                # not in permissions


def test_blocked_adapter_denies_all_tools():
    reg = ProtocolTrustRegistry()
    # enabled but missing sandbox/identity -> blocked -> gate denies everything
    rec = reg.register(ProtocolAdapterRequest(adapter_id="bad", protocol="MCP", endpoint="x",
                                              enabled=True, permissions=["tools:echo"]))
    gate = consent_gate_from_trust(rec)
    assert gate("echo") is False


# --- connective helper: computer-use perception bundle ---

def test_perceive_screen_bundles_parse_and_grounding():
    elements = [
        {"role": "button", "text": "Submit", "bbox": [0, 0, 80, 30]},
        {"role": "link", "text": "Help", "bbox": [90, 0, 40, 30]},
    ]
    bundle = perceive_screen(elements, "click submit")
    assert bundle["perception_only"] is True and bundle["action_allowed"] is False
    assert bundle["parse"]["clickable_count"] == 2
    assert bundle["grounding"]["target_text"] == "Submit"
