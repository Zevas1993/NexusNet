"""PB-2026-06-03-095..100 - post-book candidate lanes (governed, non-mutating, shadow-only)."""
from __future__ import annotations

from nexusnet.knowledge.memory_model import (
    CorpusDoc, corpus_eligibility, generate_reflection_qa, MemoryModelLane,
)
from nexusnet.adapters.passport import AdapterPassport, AdapterRegistry
from nexusnet.agents.harnesses.secure_runtime import (
    SecureRuntimeContract, NetworkAllowlist, CredentialBroker, redact_snapshot, restore_snapshot,
    propose_candidates_from_trace,
)
from nexusnet.agents.harnesses.contract import HarnessContractRequest, IdentityClaim
from nexusnet.audio.scene_alignment import (
    AudioScene, Speaker, Turn, consent_gate, forced_align, synthesize, STATUS,
)
from nexusnet.runtime.focal_coding_lane import CodingRouteEvaluator, CodingRouteRequest
from nexusnet.runtime.hardware_fit import HardwareSnapshot, ModelFitCandidate, ModelFitRecommender


# --- PB-095 MeMo memory-model lane ---

def _docs():
    return [
        CorpusDoc(doc_id="d1", text="...", source_ref="src://a", rights_cleared=True,
                  privacy_class="public", freshness_days=10, entities=["Euler"],
                  facts=["V - E + F = 2 for convex polyhedra"]),
        CorpusDoc(doc_id="d2", text="...", source_ref="src://b", rights_cleared=True,
                  privacy_class="public", freshness_days=20, entities=["Euler"],
                  facts=["e^{i pi} + 1 = 0", "Euler studied graph theory"]),
    ]


def test_corpus_eligibility_blocks_private_and_unrightsed():
    bad = CorpusDoc(doc_id="x", text="t", source_ref="", rights_cleared=False, privacy_class="private")
    v = corpus_eligibility(bad)
    assert v["eligible"] is False
    assert "rights_not_cleared" in v["reasons"] and "private_data" in v["reasons"]


def test_reflection_qa_covers_all_categories_with_provenance():
    qa = generate_reflection_qa(_docs())
    cats = {q.category for q in qa}
    assert {"direct_fact", "consolidated_multi_fact", "entity_surface", "cross_document_synthesis"} <= cats
    assert all(q.source_ref for q in qa)                        # provenance on every pair


def test_memory_answer_is_secondary_unless_kac_cited():
    lane = MemoryModelLane()
    lane.ingest(_docs())
    secondary = lane.query("what is euler's polyhedron formula")
    assert secondary["evidence_class"] == "secondary_recall" and secondary["grounded"] is False
    grounded = lane.query("what is euler's polyhedron formula", kac_citation="kac://123")
    assert grounded["evidence_class"] == "grounded_kac" and grounded["grounded"] is True


# --- PB-096 adapter passport fabric ---

def _passport(**kw):
    base = dict(adapter_id="ad1", revision="v1", allowed_base_models=["nexus-lm"],
                eval_suite_refs=["eval://x"], eval_delta=0.03, residency="local",
                privacy_class="internal", rights_cleared=True, rollback_target="base")
    base.update(kw)
    return AdapterPassport(**base)


def test_adapter_registry_enumerates_without_weights_and_gates():
    reg = AdapterRegistry()
    reg.register(_passport())
    assert reg.candidates(base_model="nexus-lm") == ["ad1"]
    ok = reg.gate("ad1", "nexus-lm")
    assert ok.decision == "shadow_route" and ok.shadow_only is True
    bad = reg.gate("ad1", "other-model")
    assert bad.decision == "block" and "base_model_incompatible" in bad.reasons


def test_adapter_gate_blocks_regression_and_missing_rollback():
    reg = AdapterRegistry()
    reg.register(_passport(adapter_id="bad", eval_delta=-0.1, rollback_target=""))
    d = reg.gate("bad", "nexus-lm")
    assert d.decision == "block"
    assert "eval_regression" in d.reasons and "no_rollback_target" in d.reasons


def test_adapter_shadow_attach_and_rollback_restorable():
    reg = AdapterRegistry()
    reg.register(_passport(adapter_id="a1"))
    reg.register(_passport(adapter_id="a2"))
    reg.shadow_attach("a1", "nexus-lm")
    reg.shadow_attach("a2", "nexus-lm")
    assert reg.active("nexus-lm") == "a2"
    assert reg.rollback("nexus-lm") == "a1"                     # restorable to previous
    assert reg.active("nexus-lm") == "a1"


# --- PB-097 secure self-evolving runtime ---

def test_secure_runtime_blocks_unallowlisted_egress_and_redacts_snapshot():
    rt = SecureRuntimeContract(allowlist=NetworkAllowlist(["api.internal"]))
    req = HarnessContractRequest(run_id="s1", harness_id="h", required_artifacts=["skill.a"],
                                 loaded_artifacts=["skill.a"], trajectory_followed=["skill.a"])
    res = rt.evaluate(req, egress_hosts=["evil.example"],
                      learned_state={"skill_weights": [1, 2], "api_token": "RAW"})
    assert res["egress_ok"] is False and res["policy_pass"] is False
    assert "api_token" in res["snapshot"]["redacted_fields"]    # secret-tagged field stripped
    assert res["restore_secret_free"] is True


def test_credential_broker_issues_handles_without_raw_secrets():
    broker = CredentialBroker()
    rec = broker.issue("acct1", ["api:call"])
    assert rec["carries_raw_secret"] is False and rec["handle"].startswith("cred::")
    assert broker.resolve_scopes(rec["handle"]) == ["api:call"]


def test_trace_proposes_shadow_only_candidates():
    trace = [{"type": "tool_call", "tool": "grep"}] * 3 + [{"type": "error", "error": "timeout"}]
    cands = propose_candidates_from_trace(trace)
    assert any(c.kind == "skill" for c in cands) and any(c.kind == "policy" for c in cands)
    assert all(c.review_required and c.shadow_only for c in cands)


# --- PB-098 audio scene alignment (research_only, no synthesis) ---

def test_consent_gate_requires_consent_rights_provenance():
    scene = AudioScene(scene_id="sc1", speakers=[Speaker(speaker_id="s1", consent_ref="")],
                       provenance="", rights_cleared=False)
    g = consent_gate(scene)
    assert g["approved"] is False
    assert "rights_not_cleared" in g["reasons"] and "missing_provenance" in g["reasons"]


def test_forced_alignment_is_monotonic_and_covers_timeline():
    scene = AudioScene(scene_id="sc1",
                       speakers=[Speaker(speaker_id="a", consent_ref="c"),
                                 Speaker(speaker_id="b", consent_ref="c")],
                       turns=[Turn(turn_id="t1", speaker_id="a", text="hello there friend"),
                              Turn(turn_id="t2", speaker_id="b", text="hi", pause_before_s=0.5)],
                       provenance="vid://1", rights_cleared=True)
    res = forced_align(scene, total_duration_s=10.0)
    assert res["monotonic"] is True and len(res["aligned"]) == 2
    assert res["aligned"][0]["start_s"] < res["aligned"][1]["start_s"]


def test_synthesis_is_blocked_and_excluded_from_evidence():
    out = synthesize()
    assert out["implemented"] is False and out["synthetic_output_excluded_from_evidence"] is True
    assert STATUS == "research_only"


# --- PB-099 focal coding model lane ---

def _crq(**kw):
    base = dict(model_id="mellum2", task="code_completion", candidate_score=0.8,
                incumbent_id="gpt-x", incumbent_score=0.7, license_reviewed=True,
                eval_suite_refs=["eval://code"], rollback_provider="gpt-x")
    base.update(kw)
    return CodingRouteRequest(**base)


def test_coding_route_promotes_only_on_owned_fixture_win():
    ev = CodingRouteEvaluator(win_margin=0.02)
    win = ev.evaluate(_crq(candidate_score=0.8, incumbent_score=0.7))
    assert win["decision"] == "promote_candidate" and win["writes_via_tool_action_harness"] is True
    tie = ev.evaluate(_crq(candidate_score=0.70, incumbent_score=0.70))
    assert tie["decision"] == "shadow_route" and tie["shadow_only"] is True


def test_coding_route_blocks_unreviewed_and_unrightsed_distillation():
    ev = CodingRouteEvaluator()
    d = ev.evaluate(_crq(license_reviewed=False, distillation_requested=True, distillation_rights=False))
    assert d["decision"] == "block"
    assert "license_card_not_reviewed" in d["reasons"]
    assert "distillation_without_rights_blocked" in d["reasons"]


# --- PB-100 hardware-fit recommender ---

def _recommender():
    return ModelFitRecommender([
        ModelFitCandidate(model_id="big", task_categories=["coding"], min_ram_gb=64, min_vram_gb=48,
                          eval_score=0.9, license_status="approved"),
        ModelFitCandidate(model_id="mid", task_categories=["coding"], min_ram_gb=16, min_vram_gb=12,
                          eval_score=0.75, expected_latency_ms=200, license_status="approved"),
        ModelFitCandidate(model_id="small", task_categories=["coding"], min_ram_gb=8, min_vram_gb=0,
                          eval_score=0.6, expected_latency_ms=400, license_status="approved"),
    ])


def test_recommender_fits_to_hardware_and_blocks_too_large():
    hw = HardwareSnapshot(cpu="Ryzen", ram_gb=32, gpu="RTX 5070 Ti", vram_gb=16, backend="cuda")
    rec = _recommender().recommend(hw, "coding")
    ids = [r["model_id"] for r in rec["recommendations"]]
    assert "big" not in ids                                     # 48GB VRAM doesn't fit 16GB
    assert "mid" in ids and "small" in ids
    assert any(b["model_id"] == "big" for b in rec["blocked"])
    assert rec["performs_install_or_download"] is False


def test_recommender_redacts_hardware_identifiers():
    hw = HardwareSnapshot(cpu="Ryzen", ram_gb=8, vram_gb=0, backend="cpu",
                          serial="SN-12345", user_path="C:\\Users\\Chris\\models")
    rec = _recommender().recommend(hw, "coding")
    assert "serial" not in rec["hardware"]                      # raw identifier never shared
    assert set(rec["hardware"]["redacted_fields"]) == {"serial", "user_path"}
    assert [r["model_id"] for r in rec["recommendations"]] == ["small"]   # only CPU model fits 8GB
